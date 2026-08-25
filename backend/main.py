import re
import uuid
import base64

import httpx

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from backend.ml_services.model_manager import LocalScamDetector
from backend.ml_services.fusion_engine import FusionEngine, ModalityScore

from url_detection import url_classifier

from backend.schemas import (
    ScanResponse,
    RiskLevel,
    SeverityLevel,
    SupportedLanguage,
    TextAnalysisResult,
    URLAnalysisResult,
    RedFlag,
    ModalityBreakdown,
    LocalizedGuidance,
)


app = FastAPI(title="DhokaDetect Orchestration Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

VISION_SERVICE_URL = "http://127.0.0.1:8001/detect-media"

URL_REGEX = re.compile(
    r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9-]+\.(?:com|in|co\.in|org|net)\b\S*)"
)

URGENCY_PATTERNS = [
    r"within \d+ mins?",
    r"within \d+ hours?",
    r"immediate(ly)?",
    r"\btoday\b",
    r"urgent",
    r"urgently",
    r"as soon as possible",
    r"avoid disconnection",
    r"account will be blocked",
    r"account will be suspended",
    r"avoid suspension",
    r"within \d+ minutes?",
]

IMPERSONATION_PATTERNS = [
    r"\bmseb\b",
    r"electricity board",
    r"\bsbi\b",
    r"\bhdfc\b",
    r"\bicici\b",
    r"\bhdfc\b",
    r"\baxis\b",
    r"\brbi\b",
    r"\bupi\b",
    r"\bkyc\b",
    r"bank official",
    r"bank support",
    r"customer care",
]

FINANCIAL_COERCION_PATTERNS = [
    r"₹\s?\d+",
    r"\brs\.?\s?\d+",
    r"\binr\s?\d+",
    r"\bpay\b",
    r"payment",
    r"transfer money",
    r"send money",
    r"send .* money",
    r"\botp\b",
    r"\brefund\b",
    r"collect request",
    r"upi request",
]

ENTITY_EXTRACTION_PATTERNS = {
    "amount": r"₹\s?\d+(?:,\d+)*|\brs\.?\s?\d+(?:,\d+)*|\binr\s?\d+(?:,\d+)*",
    "phone": r"\b\d{10}\b",
    "vpa": r"\b[\w.\-]+@[\w]+\b",
}


VISION_UPLOAD_FILENAME = "frame.jpg"
VISION_UPLOAD_CONTENT_TYPE = "image/jpeg"
VISION_TASK = "payment"


# ============================================================
# GLOBAL SERVICES
# ============================================================

text_detector: Optional[LocalScamDetector] = None
fusion_engine = FusionEngine()


@app.on_event("startup")
async def load_models():
    global text_detector
    text_detector = LocalScamDetector()


# ============================================================
# REQUEST MODEL
# ============================================================

class AnalyzeRequest(BaseModel):
    text_input: Optional[str] = Field(
        None,
        description="Raw SMS/WhatsApp message text",
    )

    image_base64: Optional[str] = Field(
        None,
        description="Base64 encoded image or frame buffer",
    )

    force_high_risk: Optional[bool] = Field(
        False,
        description="Manual override for demo/evaluator purposes",
    )


# ============================================================
# URL ANALYSIS
# ============================================================

def extract_urls(text: str) -> List[str]:
    return URL_REGEX.findall(text)


def run_url_analysis(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract URLs from message text and run the local URL phishing
    classifier against every discovered URL.
    """

    urls = extract_urls(text)

    if not urls:
        return None

    analyzed = []

    for url in urls:
        result = url_classifier.calculate_risk_score(url)
        typo = url_classifier.detect_typosquatting(url)

        analyzed.append(
            {
                "url": url,
                **result,
                "typosquatting": typo,
            }
        )

    top = max(
        analyzed,
        key=lambda result: result["risk_score"],
    )

    return {
        "urls_found": len(analyzed),
        "all_urls": [item["url"] for item in analyzed],
        "top_risk_score": top["risk_score"],
        "top_url": top["url"],
        "top_reasons": top["reasons"],
        "top_typosquatting": top["typosquatting"]["typosquatting"],
        "all_results": analyzed,
    }


# ============================================================
# VISION ANALYSIS
# ============================================================

async def run_vision_analysis(image_b64: str) -> Dict[str, Any]:
    """
    Send base64 encoded image to the local vision service.
    """

    try:
        image_bytes = base64.b64decode(
            image_b64,
            validate=True,
        )

        files = {
            "file": (
                VISION_UPLOAD_FILENAME,
                image_bytes,
                VISION_UPLOAD_CONTENT_TYPE,
            )
        }

        data = {
            "task": VISION_TASK,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                VISION_SERVICE_URL,
                files=files,
                data=data,
            )

            response.raise_for_status()

            return response.json()

    except Exception as exc:
        return {
            "risk_score": 0.0,
            "status": "vision_fallback",
            "error_log": str(exc),
        }


# ============================================================
# FUSION CONVERSION
# ============================================================

def to_text_score(
    text_result: Optional[Dict[str, Any]]
) -> Optional[ModalityScore]:

    if text_result is None:
        return None

    return ModalityScore(
        confidence=text_result["scam_confidence"],
        weight=0.25,
        red_flags=text_result.get("red_flags", []),
    )


def to_url_score(
    url_result: Optional[Dict[str, Any]]
) -> Optional[ModalityScore]:

    if url_result is None:
        return None

    return ModalityScore(
        confidence=url_result["top_risk_score"],
        weight=0.35,
        red_flags=url_result.get("top_reasons", []),
    )


def to_vision_score(
    vision_result: Optional[Dict[str, Any]]
) -> Optional[ModalityScore]:

    if vision_result is None:
        return None

    return ModalityScore(
        confidence=vision_result.get("risk_score", 0.0),
        weight=0.20,
        red_flags=vision_result.get("red_flags", []),
    )


# ============================================================
# RISK HELPERS
# ============================================================

def score_to_risk_level(score: float) -> RiskLevel:

    if score >= 0.85:
        return RiskLevel.CRITICAL

    if score >= 0.60:
        return RiskLevel.HIGH

    if score >= 0.40:
        return RiskLevel.MEDIUM

    if score >= 0.20:
        return RiskLevel.LOW

    return RiskLevel.SAFE


def score_to_severity(score: float) -> SeverityLevel:

    if score >= 0.85:
        return SeverityLevel.CRITICAL

    if score >= 0.60:
        return SeverityLevel.HIGH

    if score >= 0.40:
        return SeverityLevel.MEDIUM

    return SeverityLevel.LOW


# ============================================================
# TEXT BREAKDOWN
# ============================================================

def build_text_breakdown(
    text: str,
    text_result: Dict[str, Any],
) -> TextAnalysisResult:

    text_lower = text.lower()

    ml_score = text_result.get(
        "ml_bert_score",
        0.0,
    )

    urgency_score = (
        1.0
        if any(
            re.search(pattern, text_lower)
            for pattern in URGENCY_PATTERNS
        )
        else round(ml_score * 0.3, 4)
    )

    impersonation_score = (
        1.0
        if any(
            re.search(pattern, text_lower)
            for pattern in IMPERSONATION_PATTERNS
        )
        else round(ml_score * 0.3, 4)
    )

    financial_coercion_score = (
        1.0
        if any(
            re.search(pattern, text_lower)
            for pattern in FINANCIAL_COERCION_PATTERNS
        )
        else round(ml_score * 0.3, 4)
    )

    entities = []

    for pattern in ENTITY_EXTRACTION_PATTERNS.values():
        entities.extend(
            re.findall(pattern, text)
        )

    return TextAnalysisResult(
        urgency_score=urgency_score,
        impersonation_score=impersonation_score,
        financial_coercion_score=financial_coercion_score,
        extracted_entities=entities,
        risk_score=text_result["scam_confidence"],
    )


# ============================================================
# URL BREAKDOWN
# ============================================================

def build_url_breakdown(
    url_result: Dict[str, Any]
) -> URLAnalysisResult:

    return URLAnalysisResult(
        extracted_urls=url_result["all_urls"],
        typosquatting_detected=url_result["top_typosquatting"],
        punycode_detected=False,
        domain_reputation_score=url_result["top_risk_score"],
        risk_score=url_result["top_risk_score"],
    )


# ============================================================
# RED FLAGS
# ============================================================

def build_red_flags(
    fusion_result: Dict[str, Any],
    overall_score: float,
) -> List[RedFlag]:

    severity = score_to_severity(
        overall_score
    )

    flags = []

    for flag_text in fusion_result.get(
        "aggregated_red_flags",
        [],
    ):

        indicator = (
            re.sub(
                r"[^A-Z0-9]+",
                "_",
                flag_text.upper(),
            )
            .strip("_")[:40]
        )

        flags.append(
            RedFlag(
                indicator=indicator,
                severity=severity,
                description=flag_text,
            )
        )

    return flags


# ============================================================
# LOCALIZED EXPLANATIONS
# ============================================================

def build_explanations(
    overall_score: float,
    risk_level: RiskLevel,
    flags: List[RedFlag],
) -> Dict[SupportedLanguage, LocalizedGuidance]:

    flag_summary = (
        "; ".join(
            flag.description
            for flag in flags
        )
        if flags
        else "No specific red flags detected."
    )

    if risk_level in (
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    ):

        action = (
            "Do not click any links or make any payment. "
            "Verify directly with the official organization "
            "using a number from their real website."
        )

    elif risk_level == RiskLevel.MEDIUM:

        action = (
            "Be cautious. Independently verify the sender "
            "before taking any action."
        )

    else:

        action = (
            "No immediate action needed, but stay alert "
            "to unexpected requests for money or personal information."
        )

    return {
        SupportedLanguage.EN: LocalizedGuidance(
            language=SupportedLanguage.EN,
            summary=(
                f"This message was classified as "
                f"{risk_level.value} risk "
                f"({round(overall_score * 100)}/100)."
            ),
            detailed_explanation=flag_summary,
            recommended_action=action,
        )
    }


# ============================================================
# RESPONSE BUILDER
# ============================================================

def build_scan_response(
    fusion_result: Dict[str, Any],
    text: Optional[str],
    text_result: Optional[Dict[str, Any]],
    url_result: Optional[Dict[str, Any]],
    vision_result: Optional[Dict[str, Any]],
) -> ScanResponse:

    score = fusion_result["final_risk_score"]

    risk_level = score_to_risk_level(
        score
    )

    breakdown = ModalityBreakdown(
        text=(
            build_text_breakdown(
                text,
                text_result,
            )
            if text and text_result
            else None
        ),

        url=(
            build_url_breakdown(
                url_result
            )
            if url_result
            else None
        ),

        visual=None,
        audio=None,
    )

    red_flags = build_red_flags(
        fusion_result,
        score,
    )

    return ScanResponse(
        task_id=str(uuid.uuid4()),
        overall_risk_score=round(score * 100),
        risk_level=risk_level,
        confidence=round(score, 4),
        modalities_processed=fusion_result[
            "active_channels"
        ],
        red_flags=red_flags,
        breakdown=breakdown,
        explanations=build_explanations(
            score,
            risk_level,
            red_flags,
        ),
    )


# ============================================================
# CORE ANALYSIS ENGINE
# ============================================================

async def perform_analysis(
    request: AnalyzeRequest,
) -> ScanResponse:

    text_result: Optional[Dict[str, Any]] = None
    url_result: Optional[Dict[str, Any]] = None
    vision_result: Optional[Dict[str, Any]] = None

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    if request.text_input:

        try:

            if text_detector is not None:

                predictions, inference_time = (
                    text_detector.predict(
                        [request.text_input]
                    )
                )

                text_result = predictions[0]

                text_result[
                    "inference_time_sec"
                ] = round(
                    inference_time,
                    4,
                )

        except Exception as exc:

            text_result = {
                "scam_confidence": 0.0,
                "ml_bert_score": 0.0,
                "red_flags": [],
                "error_log": str(exc),
            }

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        try:

            url_result = run_url_analysis(
                request.text_input
            )

        except Exception:

            url_result = None

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    if request.image_base64:

        vision_result = (
            await run_vision_analysis(
                request.image_base64
            )
        )

    # --------------------------------------------------------
    # LATE FUSION
    # --------------------------------------------------------

    fusion_result = (
        fusion_engine.compute_final_risk(
            text_score=to_text_score(
                text_result
            ),
            url_score=to_url_score(
                url_result
            ),
            image_score=to_vision_score(
                vision_result
            ),
            audio_score=None,
        )
    )

    # --------------------------------------------------------
    # DEMO OVERRIDE
    # --------------------------------------------------------

    if request.force_high_risk:

        fusion_result[
            "final_risk_score"
        ] = 1.0

        fusion_result.setdefault(
            "aggregated_red_flags",
            [],
        )

        fusion_result[
            "aggregated_red_flags"
        ].append(
            "Manual override (force_high_risk)"
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return build_scan_response(
        fusion_result,
        request.text_input,
        text_result,
        url_result,
        vision_result,
    )


# ============================================================
# API V1
# ============================================================

@app.post(
    "/api/v1/analyze",
    response_model=ScanResponse,
)
async def analyze_payload(
    request: AnalyzeRequest,
):

    return await perform_analysis(
        request
    )


# ============================================================
# API V2 MULTIMODAL
# ============================================================

@app.post(
    "/api/v2/analyze/multimodal",
    response_model=ScanResponse,
)
async def analyze_multimodal(
    request: AnalyzeRequest,
):

    return await perform_analysis(
        request
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "service": "DhokaDetect Orchestration Engine",
        "version": "2.0",
        "text_detector_loaded": text_detector is not None,
    }