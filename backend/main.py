from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import traceback

from ml_services.model_manager import LocalScamDetector
from ml_services.fusion_engine import FusionEngine, ModalityScore

app = FastAPI(title="DhokaDetect Multi-Modal Late-Fusion API", version="2.0")

# --- CORS MIDDLEWARE: Critical for Yug's Frontend Connection ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows localhost connections from React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing Local ML Engine...")
text_detector = LocalScamDetector()
fusion_engine = FusionEngine()

class MultimodalAnalysisRequest(BaseModel):
    text_input: Optional[str] = Field(None, json_schema_extra={"example": "Dear Customer, Your MSEB electricity bill is pending. Pay within 10 mins to avoid disconnection."})
    url_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, json_schema_extra={"example": 0.85})
    image_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, json_schema_extra={"example": 0.0})
    audio_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, json_schema_extra={"example": 0.0})

@app.get("/")
def root():
    return {"status": "online", "service": "DhokaDetect Multi-Modal API"}

# Changed to v1 so Yug's current React code hits the correct endpoint
@app.post("/api/v1/analyze")
async def analyze_payload(request: MultimodalAnalysisRequest):
    try:
        text_modality = None
        
        # 1. Process Text locally if provided
        if request.text_input:
            text_res, _ = text_detector.predict([request.text_input])
            res = text_res[0] if text_res else {}
            
            # Safe key access with fallbacks
            text_modality = ModalityScore(
                confidence=res.get("scam_confidence", 0.0),
                weight=0.35,
                red_flags=res.get("red_flags", [])
            )

        # 2. Map optional scores from other modules
        url_modality = ModalityScore(
            confidence=request.url_confidence, 
            weight=0.35, 
            red_flags=["Suspicious Domain Pattern"]
        ) if request.url_confidence is not None else None

        image_modality = ModalityScore(
            confidence=request.image_confidence, 
            weight=0.15,
            red_flags=[]
        ) if request.image_confidence is not None else None

        audio_modality = ModalityScore(
            confidence=request.audio_confidence, 
            weight=0.15,
            red_flags=[]
        ) if request.audio_confidence is not None else None

        # 3. Perform Late Fusion
        fusion_result = fusion_engine.compute_final_risk(
            text_score=text_modality,
            url_score=url_modality,
            image_score=image_modality,
            audio_score=audio_modality
        )

        return fusion_result

    except Exception as e:
        print("ERROR LOGGED IN ENDPOINT:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Processing Error: {str(e)}")