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
        print(f"Booting Dual-Modal Vision Engine on {self.device}...")

        # 1. PAYMENT FRAUD MODEL (Swin Transformer)
        self.payment_model = AutoModelForImageClassification.from_pretrained(
            "microsoft/swin-base-patch4-window7-224"
        )
        self.payment_model.classifier = nn.Linear(self.payment_model.classifier.in_features, 1)
        
        # Auto-detect trained weight file location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_weight_paths = [
            "swin_fraud_head.pt",
            os.path.join(script_dir, "swin_fraud_head.pt"),
            os.path.join(script_dir, "..", "swin_fraud_head.pt")
        ]
        
        loaded_weights = False
        for wpath in possible_weight_paths:
            if os.path.exists(wpath):
                self.payment_model.classifier.load_state_dict(
                    torch.load(wpath, map_location=self.device)
                )
                print(f"✅ Loaded trained payment weights from: {wpath}")
                loaded_weights = True
                break
                
        if not loaded_weights:
            print("⚠️ Warning: 'swin_fraud_head.pt' not found. Using baseline classifier.")

        self.payment_model = self.payment_model.to(self.device).half()
        self.payment_model.eval()
        self.payment_target = [self.payment_model.swin.layernorm]

        # 2. DEEPFAKE FACE MODEL (ViT)
        self.deepfake_model = AutoModelForImageClassification.from_pretrained(
            "prithivMLmods/Deepfake-Detection-Exp-02-22"
        )
        self.deepfake_model = self.deepfake_model.to(self.device).half()
        self.deepfake_model.eval()
        self.deepfake_target = [self.deepfake_model.vit.layers[-1].layernorm_before]

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

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

    def detect_and_explain(self, file_input, task="payment"):
        """Primary Entry Point: Accepts image/video and routing task ('payment' or 'deepfake')"""
        if isinstance(file_input, str) and file_input.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return self._analyze_video(file_input, task)
        else:
            return self._analyze_image(file_input, task)

    def _analyze_image(self, image_input, task):
        image = self._parse_input(image_input)
        return self._process_frame(image, task)

    def _analyze_video(self, video_path, task):
        print(f"Extracting frames from video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file.")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        num_samples = min(8, frame_count) if frame_count > 0 else 8
        frames_to_process = []

        if frame_count > 0:
            step = max(1, frame_count // num_samples)
            for i in range(0, frame_count, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames_to_process.append(Image.fromarray(frame))
                if len(frames_to_process) >= num_samples:
                    break
        cap.release()

        if not frames_to_process:
            raise ValueError("Failed to extract frames from video.")

        highest_score = -1
        worst_frame_result = None

        for idx, frame in enumerate(frames_to_process):
            result = self._process_frame(frame, task)
            if result["fraud_probability"] > highest_score:
                highest_score = result["fraud_probability"]
                worst_frame_result = result

        worst_frame_result["mode_used"] = f"{task} (Video Analysis)"
        return worst_frame_result

    def _process_frame(self, image, task):
        tensor = self.transform(image).unsqueeze(0).to(self.device).half()
        
        if task == "deepfake":
            model = self.deepfake_model
            target_layers = self.deepfake_target
        else:
            model = self.payment_model
            target_layers = self.payment_target
            
        with torch.no_grad():
            outputs = model(tensor)
            if task == "deepfake":
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                score = round(probs[0][0].item(), 4)
            else:
                score = round(torch.sigmoid(outputs.logits).item(), 4)

        model.zero_grad()
        tensor.requires_grad = True
        
        try:
            cam = GradCAM(model=model, target_layers=target_layers)
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
            "heatmap_base64": heatmap_base64,
            "mode_used": task
        }