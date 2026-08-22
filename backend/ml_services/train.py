import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForImageClassification

class FraudDataset(Dataset):
    def __init__(self, real_dir, fake_dir, transform=None):
        self.samples = []
        self.transform = transform
        
        # Load real images (label 0)
        if os.path.exists(real_dir):
            for fname in os.listdir(real_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    self.samples.append((os.path.join(real_dir, fname), 0.0))
                    
        # Load fake images (label 1)
        if os.path.exists(fake_dir):
            for fname in os.listdir(fake_dir):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    self.samples.append((os.path.join(fake_dir, fname), 1.0))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor([label], dtype=torch.float32)

def find_dataset_dir():
    """Locates the dataset directory automatically regardless of execution path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.getcwd()
    
    candidates = [
        os.path.join(current_dir, "dataset"),
        os.path.join(script_dir, "dataset"),
        os.path.join(script_dir, "..", "dataset"),
        os.path.join(script_dir, "..", "..", "dataset")
    ]
    
    for cand in candidates:
        cand_norm = os.path.normpath(cand)
        real_p = os.path.join(cand_norm, "real")
        fake_p = os.path.join(cand_norm, "fake")
        if os.path.exists(real_p) or os.path.exists(fake_p):
            return cand_norm
            
    return os.path.join(current_dir, "dataset")

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    dataset_base = find_dataset_dir()
    real_dir = os.path.join(dataset_base, "real")
    fake_dir = os.path.join(dataset_base, "fake")
    print(f"Looking for dataset in: {dataset_base}")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dataset = FraudDataset(real_dir, fake_dir, transform=transform)
    if len(dataset) == 0:
        print(f"❌ Error: No images found in '{real_dir}' or '{fake_dir}'!")
        print("Please check that your images (.jpg, .png) are placed inside those folders.")
        return
        
    real_count = sum(1 for _, l in dataset.samples if l == 0.0)
    fake_count = sum(1 for _, l in dataset.samples if l == 1.0)
    print(f"Loaded {len(dataset)} images ({real_count} Real, {fake_count} Fake).")
    
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    print("Loading Swin Transformer...")
    model = AutoModelForImageClassification.from_pretrained("microsoft/swin-base-patch4-window7-224")
    
    for param in model.parameters():
        param.requires_grad = False
        
    model.classifier = nn.Linear(model.classifier.in_features, 1)
    for param in model.classifier.parameters():
        param.requires_grad = True
        
    model = model.to(device)
    
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.classifier.parameters(), lr=1e-3)
    
    model.train()
    epochs = 15
    print(f"Starting training for {epochs} epochs...")
    
    for epoch in range(epochs):
        total_loss = 0.0
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images).logits
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {total_loss/len(loader):.4f}")
        
    output_weights_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swin_fraud_head.pt")
    torch.save(model.classifier.state_dict(), output_weights_path)
    print(f"\n✅ Training complete! Saved model head to '{output_weights_path}'.")

if __name__ == "__main__":
    main()