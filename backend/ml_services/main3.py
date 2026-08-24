import os
import shutil
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vision_service import VisionService

app = FastAPI(
    title="DhokaDetect - Vision ML Microservice",
    description="Dual-Engine Vision API for UPI Payment Forgery and Deepfake Detection",
    version="2.0.0"
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

vision_service = VisionService()

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "DhokaDetect Vision Microservice",
        "supported_tasks": ["payment", "deepfake"]
    }

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
            os.remove(file_path)

if __name__ == "__main__":
    # Passing 'app' object directly fixes the "Could not import module" error
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)