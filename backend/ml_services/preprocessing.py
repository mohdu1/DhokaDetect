import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms

class MultimodalPreprocessor:
    def __init__(self):
        # Swin Transformer expects 224x224 inputs and standard ImageNet normalization
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                 std=[0.229, 0.224, 0.225])
        ])

    def process_image(self, image_path: str) -> torch.Tensor:
        """
        Loads a payment screenshot and prepares it for the Vision Transformer.
        Returns tensor of shape [1, 3, 224, 224]
        """
        try:
            image = Image.open(image_path).convert("RGB")
            tensor = self.transform(image)
            # Add a batch dimension so it becomes [1, C, H, W]
            return tensor.unsqueeze(0)
        except Exception as e:
            raise ValueError(f"Failed to process image {image_path}: {str(e)}")

    def process_video(self, video_path: str, num_frames: int = 16) -> torch.Tensor:
        """
        Extracts evenly spaced frames from a video to prevent GPU memory overflow.
        Returns tensor of shape [num_frames, 3, 224, 224]
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise ValueError("Video file is empty or corrupted.")

        # Calculate evenly spaced indices (e.g., grab a frame every 10 frames)
        indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # OpenCV uses BGR, we need RGB for PyTorch
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(self.transform(pil_image))
            else:
                break
                
        cap.release()
        if not frames:
            raise ValueError("Could not extract any valid frames from the video.")
        return torch.stack(frames)
if __name__ == "__main__":
    print("Preprocessor initialized successfully!")