import os
import shutil
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from vision_service import VisionService

app = FastAPI(title="DhokaDetect Vision Microservice")
service = VisionService()

os.makedirs("temp_uploads", exist_ok=True)

@app.post("/detect-media")
async def detect_media(file: UploadFile = File(...)):
    temp_path = f"temp_uploads/{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = service.detect_and_explain(temp_path)
        torch.cuda.empty_cache()

        return JSONResponse(content={
            "filename": file.filename,
            "fraud_probability": result["fraud_probability"],
            "heatmap_base64": result["heatmap_base64"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)