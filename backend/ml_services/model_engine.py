import torch
import torch.nn as nn
from transformers import AutoModelForImageClassification
class FraudDetector:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Swin Transformer onto {self.device}...")
        self.model = AutoModelForImageClassification.from_pretrained(
            "microsoft/swin-base-patch4-window7-224"
        )
        in_features = self.model.classifier.in_features
        self.model.classifier = nn.Linear(in_features, 1)
        self.model = self.model.to(self.device).half()
        self.model.eval() 
    @torch.no_grad() 
    def predict_image(self, image_tensor: torch.Tensor) -> float:
        """Runs a single screenshot through the model."""
        image_tensor = image_tensor.to(self.device).half()
        outputs = self.model(image_tensor)
        logits = outputs.logits
        probability = torch.sigmoid(logits).item()
        return round(probability, 4)
    @torch.no_grad()
    def predict_video(self, video_tensor: torch.Tensor) -> float:
        """
        Runs 16 video frames through the model simultaneously,
        then averages the results to get a single video confidence score.
        """
        video_tensor = video_tensor.to(self.device).half()
        outputs = self.model(video_tensor)
        logits = outputs.logits 
        mean_logit = torch.mean(logits)
        probability = torch.sigmoid(mean_logit).item()
        return round(probability, 4)
if __name__ == "__main__":
    detector = FraudDetector()
    print("Model loaded successfully into RTX 4060 VRAM!")
    print("Ready for Late-Fusion scoring.")