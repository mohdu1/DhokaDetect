import base64
import io
import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageClassification
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

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
        
        self.target_layers = [self.model.swin.layernorm]
        
    def _parse_input(self, image_input):
        if isinstance(image_input, str):
            try:
                return Image.open(image_input).convert("RGB")
            except (FileNotFoundError, OSError):
                pass
            
            try:
                if "," in image_input:
                    image_input = image_input.split(",")[1]
                image_input += "=" * ((4 - len(image_input) % 4) % 4)
                image_bytes = base64.b64decode(image_input)
                return Image.open(io.BytesIO(image_bytes)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Detection failed: {e}")
        
        return Image.open(image_input).convert("RGB")

    def detect_and_explain(self, image_input):
        image = self._parse_input(image_input)
        tensor = self.transform(image).unsqueeze(0).to(self.device).half()
        
        with torch.no_grad():
            outputs = self.model(tensor)
            confidence_score = torch.sigmoid(outputs.logits).item()
            score = round(confidence_score, 4)

        self.model.zero_grad()
        tensor.requires_grad = True
        
        try:
            cam = GradCAM(model=self.model, target_layers=self.target_layers)
            grayscale_cam = cam(input_tensor=tensor, targets=None)[0, :]
            
            rgb_img = np.float32(image.resize((224, 224))) / 255
            visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
            
            pil_heatmap = Image.fromarray(visualization)
            buffered = io.BytesIO()
            pil_heatmap.save(buffered, format="JPEG")
            heatmap_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception:
            heatmap_base64 = None

        return {
            "fraud_probability": score,
            "heatmap_base64": heatmap_base64
        }