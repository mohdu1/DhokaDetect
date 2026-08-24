import os
import re
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import DistilBertModel, DistilBertTokenizer, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# -------------------------------------------------------------------------
# 1. REGIONAL REGEX & HEURISTIC ENGINE
# -------------------------------------------------------------------------
REGIONAL_RULES = {
    "utility_scam": re.compile(
        r"\b(mseb|mahavitaran|bescom|tpddl|msedcl|smart meter|light bill|bijli|power cut|"
        r"power will be disconnected|meter update|disconnection|power supply|bill pending)\b", 
        re.IGNORECASE
    ),
    "kyc_telecom": re.compile(
        r"\b(trai|aadhaar|aadhar|pan card|pan block|sim block|kyc failure|kyc pending|"
        r"account is suspended|account will be deactivated|e-kyc|document update)\b", 
        re.IGNORECASE
    ),
    "digital_arrest": re.compile(
        r"\b(cbi|police|supreme court|arrest warrant|digital arrest|crime|security deposit|"
        r"confiscation|clear your name|hacked|digilocker)\b", 
        re.IGNORECASE
    ),
    "urgency_phishing": re.compile(
        r"\b(immediate action|urgent|pay now|won|lucky draw|grand prize|lottery|invest|"
        r"cashback|expedite|refund|thagi|khaata|paise|pathav|bhejo|in'am|ignore at your own risk|"
        r"over-speeding|echallan|challan)\b", 
        re.IGNORECASE
    ),
    "suspicious_link": re.compile(
        r"(https?://\S+|www\.\S+|\.vip|\.top|\[Malicious Link\]|\[Link\])", 
        re.IGNORECASE
    )
}

def process_fraud_dataset(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["message_text"] = df["message_text"].fillna("").astype(str)
    
    for rule_name, pattern in REGIONAL_RULES.items():
        df[f"flag_{rule_name}"] = df["message_text"].apply(
            lambda x: 1 if bool(pattern.search(x)) else 0
        )
        
    flag_cols = [f"flag_{r}" for r in REGIONAL_RULES.keys()]
    df["heuristic_risk_score"] = df[flag_cols].mean(axis=1).round(3)
    df["label"] = df["label"].astype(int)
    return df

# -------------------------------------------------------------------------
# 2. PYTORCH DATASET CLASS
# -------------------------------------------------------------------------
class FraudDetectionDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length=128):
        self.texts = dataframe["message_text"].values
        self.heuristic_scores = dataframe["heuristic_risk_score"].values
        self.labels = dataframe["label"].values
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        score = float(self.heuristic_scores[idx])
        label = int(self.labels[idx])

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "heuristic_score": torch.tensor(score, dtype=torch.float),
            "label": torch.tensor(label, dtype=torch.long)
        }

# -------------------------------------------------------------------------
# 3. HYBRID DISTILBERT NEURAL NETWORK ARCHITECTURE
# -------------------------------------------------------------------------
class DistilBertWithHeuristics(nn.Module):
    def __init__(self, freeze_bert_layers=False):
        super(DistilBertWithHeuristics, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        
        if freeze_bert_layers:
            for param in self.distilbert.parameters():
                param.requires_grad = False
                
        # 768 (DistilBERT [CLS] vector) + 1 (heuristic_score scalar) = 769 features
        self.classifier = nn.Sequential(
            nn.Linear(768 + 1, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 2)
        )

    def forward(self, input_ids, attention_mask, heuristic_score):
        bert_output = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        # Extract [CLS] token representation (batch_size, 768)
        cls_vector = bert_output.last_hidden_state[:, 0, :]
        
        # Reshape score to (batch_size, 1) and concatenate
        score_unsq = heuristic_score.unsqueeze(1)
        combined_features = torch.cat((cls_vector, score_unsq), dim=1)
        
        logits = self.classifier(combined_features)
        return logits

# -------------------------------------------------------------------------
# 4. TRAINING & EVALUATION LOOP
# -------------------------------------------------------------------------
def train_model():
    # Setup Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"⚡ Training on device: {device}")

    dataset_path = os.path.join(os.path.dirname(__file__), "dataset", "india_fraud_detection_FINAL.csv")
    df = process_fraud_dataset(dataset_path)

    # Train/Validation Split (80/20)
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
    print(f"Train samples: {len(train_df)} | Validation samples: {len(val_df)}")

    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    train_dataset = FraudDetectionDataset(train_df, tokenizer)
    val_dataset = FraudDetectionDataset(val_df, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

    model = DistilBertWithHeuristics().to(device)
    
    epochs = 3
    total_steps = len(train_loader) * epochs
    optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        print(f"\n--- Epoch {epoch + 1}/{epochs} ---")
        model.train()
        total_train_loss = 0

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            heuristic_score = batch["heuristic_score"].to(device)
            labels = batch["label"].to(device)

            model.zero_grad()
            logits = model(input_ids, attention_mask, heuristic_score)
            loss = criterion(logits, labels)
            total_train_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            if (step + 1) % 50 == 0 or (step + 1) == len(train_loader):
                print(f"Batch {step + 1}/{len(train_loader)} - Loss: {loss.item():.4f}")

        avg_train_loss = total_train_loss / len(train_loader)
        print(f"Average Training Loss: {avg_train_loss:.4f}")

        # Validation Phase
        model.eval()
        val_preds, val_labels = [], []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                heuristic_score = batch["heuristic_score"].to(device)
                labels = batch["label"].to(device)

                logits = model(input_ids, attention_mask, heuristic_score)
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_labels.extend(labels.cpu().numpy())

        acc = accuracy_score(val_labels, val_preds)
        precision, recall, f1, _ = precision_recall_fscore_support(val_labels, val_preds, average="binary")
        print(f"Validation Metrics -> Accuracy: {acc:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")

    # Save Model Weights & Tokenizer
    output_dir = os.path.join(os.path.dirname(__file__), "saved_models", "distilbert_scam_model")
    os.makedirs(output_dir, exist_ok=True)
    
    torch.save(model.state_dict(), os.path.join(output_dir, "distilbert_scam.pt"))
    tokenizer.save_pretrained(output_dir)
    print(f"\n✅ Fine-tuning complete! Model saved to '{output_dir}'.")

if __name__ == "__main__":
    train_model()