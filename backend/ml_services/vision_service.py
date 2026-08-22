import base64
import io
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageClassification

class VisionService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = AutoModelForImageClassification.from_pretrained(
            "microsoft/swin-base-patch4-window7-224"
        )
        
        self.model.classifier = nn.Linear(self.model.classifier.in_features, 1)
        self.model = self.model.to(self.device).half()
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                 std=[0.229, 0.224, 0.225])
        ])

    def _parse_input(self, image_input):
        if isinstance(image_input, str):
            if "," in image_input:
                image_input = image_input.split(",")[1]
            image_bytes = base64.b64decode(image_input)
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        return Image.open(image_input).convert("RGB")

    @torch.no_grad()
    def detect_anomaly(self, image_input) -> float:
        try:
            image = self._parse_input(image_input)
            tensor = self.transform(image).unsqueeze(0).to(self.device).half()
            
            outputs = self.model(tensor)
            confidence_score = torch.sigmoid(outputs.logits).item()
            
            return round(confidence_score, 4)
            
        except Exception as e:
            raise ValueError(f"Detection failed: {str(e)}")