import os
import shutil
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from preprocessing import MultimodalPreprocessor
from model_engine import FraudDetector

app = FastAPI(title="DhokaDetect Vision Microservice")

preprocessor = MultimodalPreprocessor()
detector = FraudDetector()

os.makedirs("temp_uploads", exist_ok=True)

@app.post("/detect-media")
async def detect_media(file: UploadFile = File(...)):
    temp_path = f"temp_uploads/{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ext = file.filename.split(".")[-1].lower()
        
        if ext in ["jpg", "jpeg", "png"]:
            modality = "image"
            tensor = preprocessor.process_image(temp_path)
            score = detector.predict_image(tensor)
        elif ext in ["mp4", "avi", "mov", "webm"]:
            modality = "video"
            tensor = preprocessor.process_video(temp_path)
            score = detector.predict_video(tensor)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        torch.cuda.empty_cache()

        return JSONResponse(content={
            "filename": file.filename,
            "modality": modality,
            "fraud_probability": score
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)