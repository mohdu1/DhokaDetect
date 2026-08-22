import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Local ML & Logic Imports
from ml_services import model_manager      # Aditi's NLP Engine
from url_detection import url_classifier   # Arnav's URL Extraction & Analysis
from ml_services import fusion_engine      # Late-Fusion Math
from schemas import ScanResponse

# ==========================================
# 1. App Initialization & CORS
# ==========================================
app = FastAPI(title="DhokaDetect Orchestration Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manas's Remote GPU Vision Service
VISION_SERVICE_URL = "https://20b78333ede132.lhr.life/api/v1/analyze-image"

# ==========================================
# 2. Incoming Request Schema
# ==========================================
class AnalyzeRequest(BaseModel):
    text_input: Optional[str] = Field(None, description="Raw SMS/WhatsApp message text")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image or frame buffer")
    force_high_risk: Optional[bool] = Field(False, description="Manual override for demo/evaluator purposes")

# ==========================================
# 3. Main Orchestration Endpoint
# ==========================================
@app.post("/api/v1/analyze", response_model=ScanResponse)
async def analyze_payload(request: AnalyzeRequest):
    """
    Core routing endpoint. Dispatches text/URL locally and async requests to the remote Vision API.
    Fuses all returned metrics into a single explainable risk score.
    """
    
    # Initialize empty modality results
    text_result: Optional[Dict[str, Any]] = None
    url_result: Optional[Dict[str, Any]] = None
    vision_result: Optional[Dict[str, Any]] = None

    # Step A: Local NLP and URL Processing (Aditi & Arnav)
    if request.text_input:
        text_result = model_manager.analyze_text(request.text_input)
        url_result = url_classifier.extract_and_analyze(request.text_input)

    # Step B: Remote Vision Processing (Manas) - Non-blocking HTTPX Call
    if request.image_base64:
        async with httpx.AsyncClient() as client:
            try:
                # 5-second timeout requirement to prevent bottlenecking the orchestrator
                response = await client.post(
                    VISION_SERVICE_URL,
                    json={"image_base64": request.image_base64},
                    timeout=5.0 
                )
                response.raise_for_status()
                vision_result = response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                # Graceful degradation: If Manas's node drops, we don't crash the SIH demo.
                print(f"[WARN] Vision microservice fallback triggered: {exc}")
                vision_result = {
                    "risk_score": 0.0, 
                    "status": "unreachable_fallback",
                    "error_log": str(exc)
                }

    # Step C: Late-Fusion Risk Scoring
    # Push all gathered metrics to the fusion engine to calculate the 0-100 score
    final_response = fusion_engine.compute_final_risk(
        text_result=text_result,
        url_result=url_result,
        vision_result=vision_result,
        audio_result=None, # Audio routing reserved for future step
        manual_override=request.force_high_risk
    )

    return final_response