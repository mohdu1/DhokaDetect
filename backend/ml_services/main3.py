import os
import shutil
import subprocess
import torch
import librosa
import numpy as np
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
from vision_service import VisionService

app = FastAPI(
    title="DhokaDetect - ML Microservice",
    description="Multi-Modal API for UPI Payment Forgery, Vision Deepfakes, and Wav2Vec2 Audio Deepfake Detection",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Loading ML Microservices on {device}...")

# 1. Initialize Vision Engine
vision_service = VisionService()

# 2. Initialize Hugging Face Audio Deepfake Transformer
AUDIO_MODEL_NAME = "mo-thecreator/Deepfake-audio-detection"
print(f"Loading Audio Transformer ({AUDIO_MODEL_NAME})...")
try:
    audio_feature_extractor = AutoFeatureExtractor.from_pretrained(AUDIO_MODEL_NAME)
    audio_model = AutoModelForAudioClassification.from_pretrained(AUDIO_MODEL_NAME).to(device)
    audio_model.eval()
    print("✅ Audio Deepfake Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Warning: Failed to load Audio Deepfake model ({e}). Will fallback to basic processing.")
    audio_model = None

def load_audio_signal(file_path: str):
    """
    Loads audio signal at 16kHz from any audio or video container (.wav, .mp3, .mp4, .m4a, .mov, etc.).
    Uses imageio_ffmpeg if librosa cannot natively open the format.
    """
    try:
        return librosa.load(file_path, sr=16000)
    except Exception:
        temp_wav = file_path + "_converted.wav"
        try:
            ffmpeg_exe = "ffmpeg"
            try:
                import imageio_ffmpeg
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                pass

            cmd = [
                ffmpeg_exe, "-y",
                "-i", file_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                temp_wav
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            y, sr = librosa.load(temp_wav, sr=16000)
            return y, sr
        except Exception as conv_err:
            raise RuntimeError(
                f"Conversion failed. Ensure 'imageio-ffmpeg' is installed (`pip install imageio-ffmpeg`). Error: {str(conv_err)}"
            )
        finally:
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "DhokaDetect ML Microservice",
        "supported_tasks": ["payment", "deepfake", "audio"]
    }

# ----------------- VISION ENDPOINT -----------------
@app.post("/detect-media")
async def detect_media(
    file: UploadFile = File(...), 
    task: str = Form("payment")
):
    if task not in ["payment", "deepfake"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid task specified. Must be 'payment' or 'deepfake'."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = vision_service.detect_and_explain(file_path, task=task)
        result["filename"] = file.filename
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

# ----------------- AI AUDIO TRANSFORMER ENDPOINT -----------------
@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    allowed_extensions = (
        '.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac', '.wma', 
        '.mp4', '.m4v', '.mov', '.avi', '.mkv', '.webm', '.opus'
    )
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}"
        )
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Load raw audio waveform at 16kHz
        y, sr = load_audio_signal(file_path)

        if audio_model is not None:
            # 2. Extract Wav2Vec2 features and run Inference
            inputs = audio_feature_extractor(
                y, 
                sampling_rate=16000, 
                return_tensors="pt", 
                padding=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = audio_model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]

            # Probabilities mapping: Class 0 vs Class 1 depending on model head output
            # For this Wav2Vec2 model head: index 1 is AI/Fake, index 0 is Real/Human
            ai_probability = round(float(probs[1].item()), 4)
            human_probability = round(float(probs[0].item()), 4)

            return {
                "filename": file.filename,
                "ai_voice_probability": ai_probability,
                "human_voice_probability": human_probability,
                "risk_score": ai_probability,
                "verdict": "Likely AI / Voice Clone" if ai_probability >= 0.50 else "Human Speech"
            }
        else:
            raise HTTPException(status_code=500, detail="Audio Deepfake model is not loaded.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
        
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)