import os
import shutil
import io
import subprocess
import librosa
import numpy as np
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vision_service import VisionService

app = FastAPI(
    title="DhokaDetect - ML Microservice",
    description="Multi-Modal API for UPI Payment Forgery, Vision Deepfakes, and Audio Voice Clones",
    version="2.4.0"
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

print("Initializing Vision Service...")
vision_service = VisionService()

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

# ----------------- UNIVERSAL AUDIO ENDPOINT -----------------
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

        # Robustly load audio signal from file/video
        y, sr = load_audio_signal(file_path)
        
        # 1. Spectral Centroid
        centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        centroid_mean = float(np.mean(centroids))
        centroid_std = float(np.std(centroids))
        
        # 2. Pitch Jitter
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7')
        )
        
        f0_voiced = f0[~np.isnan(f0)]
        
        if len(f0_voiced) > 1:
            jitter = float(np.mean(np.abs(np.diff(f0_voiced))) / np.mean(f0_voiced))
        else:
            jitter = 0.0

        # Risk Scoring
        risk_score = 0.0
        if jitter < 0.015: 
            risk_score += 0.4
        if centroid_std < 400: 
            risk_score += 0.4
            
        return {
            "filename": file.filename,
            "features": {
                "spectral_centroid_mean": centroid_mean,
                "spectral_centroid_std": centroid_std,
                "pitch_jitter": jitter
            },
            "risk_score": round(risk_score, 2),
            "verdict": "Likely AI" if risk_score >= 0.7 else "Suspicious" if risk_score >= 0.4 else "Human"
        }
        
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