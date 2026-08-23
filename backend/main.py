from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import traceback

from backend.ml_services.model_manager import LocalScamDetector
from backend.ml_services.fusion_engine import FusionEngine, ModalityScore
from url_detection.url_classifier import extract_and_analyze


app = FastAPI(
    title="DhokaDetect Multi-Modal Late-Fusion API",
    version="2.0"
)


# ---------------------------------------------------------
# Initialize ML components
# ---------------------------------------------------------

print("Initializing Local ML Engine...")

text_detector = LocalScamDetector()
fusion_engine = FusionEngine()


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------

class MultimodalAnalysisRequest(BaseModel):

    text_input: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": (
                "Dear Customer, Your MSEB electricity bill is pending. "
                "Pay within 10 mins to avoid disconnection."
            )
        }
    )

    url_input: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": (
                "http://secure-login-example.com/verify-account"
            )
        }
    )

    image_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        json_schema_extra={
            "example": 0.0
        }
    )

    audio_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        json_schema_extra={
            "example": 0.0
        }
    )


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "DhokaDetect Multi-Modal API"
    }


# ---------------------------------------------------------
# Multimodal Analysis Endpoint
# ---------------------------------------------------------

@app.post("/api/v2/analyze/multimodal")
async def analyze_multimodal(
    request: MultimodalAnalysisRequest
):
    try:

        # -------------------------------------------------
        # Initialize modality results
        # -------------------------------------------------

        text_modality = None
        url_modality = None
        image_modality = None
        audio_modality = None


        # -------------------------------------------------
        # 1. TEXT ANALYSIS
        # -------------------------------------------------

        if request.text_input:

            text_res, _ = text_detector.predict(
                [request.text_input]
            )

            res = text_res[0] if text_res else {}

            text_modality = ModalityScore(
                confidence=res.get(
                    "scam_confidence",
                    0.0
                ),

                # IMPORTANT:
                # None means FusionEngine uses its
                # default text weight = 0.25
                weight=None,

                red_flags=res.get(
                    "red_flags",
                    []
                )
            )


        # -------------------------------------------------
        # 2. URL ANALYSIS
        # -------------------------------------------------

        # Case A:
        # Explicit URL provided through url_input

        if request.url_input:

            url_result = extract_and_analyze(
                request.url_input
            )

            if url_result["url"]:

                url_modality = ModalityScore(
                    confidence=url_result[
                        "risk_score"
                    ],

                    # FusionEngine default:
                    # URL weight = 0.35
                    weight=None,

                    red_flags=url_result[
                        "reasons"
                    ]
                )


        # Case B:
        # No explicit URL.
        # Try extracting a URL from the text.

        elif request.text_input:

            url_result = extract_and_analyze(
                request.text_input
            )

            if url_result["url"]:

                url_modality = ModalityScore(
                    confidence=url_result[
                        "risk_score"
                    ],

                    # FusionEngine default:
                    # URL weight = 0.35
                    weight=None,

                    red_flags=url_result[
                        "reasons"
                    ]
                )


        # -------------------------------------------------
        # 3. IMAGE ANALYSIS
        # -------------------------------------------------

        if request.image_confidence is not None:

            image_modality = ModalityScore(
                confidence=request.image_confidence,

                # FusionEngine default:
                # Image weight = 0.20
                weight=None,

                red_flags=[]
            )


        # -------------------------------------------------
        # 4. AUDIO ANALYSIS
        # -------------------------------------------------

        if request.audio_confidence is not None:

            audio_modality = ModalityScore(
                confidence=request.audio_confidence,

                # FusionEngine default:
                # Audio weight = 0.20
                weight=None,

                red_flags=[]
            )


        # -------------------------------------------------
        # 5. LATE FUSION
        # -------------------------------------------------

        fusion_result = fusion_engine.compute_final_risk(

            text_score=text_modality,

            url_score=url_modality,

            image_score=image_modality,

            audio_score=audio_modality
        )


        # -------------------------------------------------
        # 6. RETURN FINAL RESULT
        # -------------------------------------------------

        return fusion_result


    except Exception as e:

        print(
            "ERROR LOGGED IN ENDPOINT:"
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Internal Processing Error: {str(e)}"
            )
        )