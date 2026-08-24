import os
import re
import torch
import torch.nn as nn
from transformers import DistilBertModel, DistilBertTokenizer

# 1. Matching Heuristic Engine
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

# 2. Hybrid Model Architecture Definition
class DistilBertWithHeuristics(nn.Module):
    def __init__(self):
        super(DistilBertWithHeuristics, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.classifier = nn.Sequential(
            nn.Linear(768 + 1, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 2)
        )

    def forward(self, input_ids, attention_mask, heuristic_score):
        bert_output = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        cls_vector = bert_output.last_hidden_state[:, 0, :]
        score_unsq = heuristic_score.unsqueeze(1)
        combined_features = torch.cat((cls_vector, score_unsq), dim=1)
        return self.classifier(combined_features)

# 3. Predictor Pipeline Class
class ScamDetector:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = os.path.join(os.path.dirname(__file__), "saved_models", "distilbert_scam_model")
        
        self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_dir)
        self.model = DistilBertWithHeuristics().to(self.device)
        
        weights_path = os.path.join(self.model_dir, "distilbert_scam.pt")
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.model.eval()

    def calculate_heuristic_score(self, text: str) -> float:
        flags = [1 if bool(pattern.search(text)) else 0 for pattern in REGIONAL_RULES.values()]
        return round(sum(flags) / len(flags), 3)

    def analyze_message(self, text: str):
        heuristic_score = self.calculate_heuristic_score(text)
        
        inputs = self.tokenizer(
            text,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        score_tensor = torch.tensor([heuristic_score], dtype=torch.float).to(self.device)

        with torch.no_grad():
            logits = self.model(inputs["input_ids"], inputs["attention_mask"], score_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            predicted_class = torch.argmax(logits, dim=1).item()

        return {
            "is_scam": bool(predicted_class == 1),
            "confidence": float(probs[predicted_class]),
            "scam_probability": float(probs[1]),
            "heuristic_risk_score": heuristic_score,
            "risk_level": "HIGH" if probs[1] > 0.7 else ("MEDIUM" if probs[1] > 0.3 else "LOW")
        }

if __name__ == "__main__":
    detector = ScamDetector()
    
    test_messages = [
        "Your Mahavitaran electricity bill is unpaid. Power supply will be disconnected tonight. Pay immediately at http://mseb-update.top",
        "CBI Digital Arrest Warning: You are involved in a money laundering case. Connect via video call to clear your name.",
        "Dear customer, your SBI savings account ending in 4021 was credited with Rs 15,000 via NEFT."
    ]

    for msg in test_messages:
        result = detector.analyze_message(msg)
        print(f"\nMessage: {msg}")
        print(f"Result: {result}")