import re
import uuid
import asyncio

import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# Local ML & Logic Imports
from ml_services.model_manager import LocalScamDetector            # Aditi's NLP Engine
from url_detection import url_classifier                           # Arnav's URL Extraction & Analysis
from ml_services.fusion_engine import FusionEngine, ModalityScore   # Late-Fusion Math
from schemas import (
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

# Simple URL matcher for pulling links out of raw SMS/WhatsApp text
URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9-]+\.(?:com|in|co\.in|org|net)\b\S*)")

# Stopgap regex sets used to fill in TextAnalysisResult's three sub-scores,
# since LocalScamDetector currently only returns one combined heuristic score
# plus a flat red_flags list. Ideally Aditi's module returns these natively.
URGENCY_PATTERNS = [
    r"within \d+ mins?", r"immediate(ly)?", r"\btoday\b", r"avoid disconnection", r"account will be blocked"
]
IMPERSONATION_PATTERNS = [
    r"\bmseb\b", r"electricity board", r"\bsbi\b", r"\bhdfc\b", r"\bkyc\b", r"update pan", r"\bupi\b"
]
FINANCIAL_COERCION_PATTERNS = [
    r"₹\s?\d+", r"\brs\.?\s?\d+", r"\bpay\b", r"transfer money", r"send money", r"\botp\b", r"\brefund\b"
]
ENTITY_EXTRACTION_PATTERNS = {
    "amount": r"₹\s?\d+(?:,\d+)*|\brs\.?\s?\d+(?:,\d+)*",
    "phone": r"\b\d{10}\b",
    "vpa": r"\b[\w.\-]+@[\w]+\b",
}


# ==========================================
# 2. Load models ONCE at startup, not per-request
# ==========================================
text_detector: Optional[LocalScamDetector] = None
fusion_engine = FusionEngine()  # cheap to construct, no model weights, fine at import time


@app.on_event("startup")
async def load_models():
    global text_detector
    text_detector = LocalScamDetector()


# ==========================================
# 3. Incoming Request Schema
# ==========================================
class AnalyzeRequest(BaseModel):
    text_input: Optional[str] = Field(None, description="Raw SMS/WhatsApp message text")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image or frame buffer")
    force_high_risk: Optional[bool] = Field(False, description="Manual override for demo/evaluator purposes")


# ==========================================
# 4. Helpers - raw modality calls
# ==========================================
def extract_urls(text: str) -> List[str]:
    return URL_REGEX.findall(text)


def run_url_analysis(text: str) -> Optional[Dict[str, Any]]:
    """Extracts URLs from raw text and runs Arnav's risk scorer on each one found."""
    urls = extract_urls(text)
    if not urls:
        return None

    analyzed = []
    for url in urls:
        result = url_classifier.calculate_risk_score(url)
        typo = url_classifier.detect_typosquatting(url)
        analyzed.append({"url": url, **result, "typosquatting": typo})

    top = max(analyzed, key=lambda r: r["risk_score"])
    return {
        "urls_found": len(analyzed),
        "all_urls": [a["url"] for a in analyzed],
        "top_risk_score": top["risk_score"],
        "top_url": top["url"],
        "top_reasons": top["reasons"],
        "top_typosquatting": top["typosquatting"]["typosquatting"],
        "all_results": analyzed,
    }


# ==========================================
# 5. Helpers - fusion input conversion
# ==========================================
def to_text_score(text_result: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    if text_result is None:
        return None
    return ModalityScore(
        confidence=text_result["scam_confidence"],
        weight=0.25,
        red_flags=text_result.get("red_flags", []),
    )


def to_url_score(url_result: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    if url_result is None:
        return None
    return ModalityScore(
        confidence=url_result["top_risk_score"],
        weight=0.35,
        red_flags=url_result.get("top_reasons", []),
    )


def to_vision_score(vision_result: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    if vision_result is None:
        return None
    return ModalityScore(
        confidence=vision_result.get("risk_score", 0.0),
        weight=0.20,
        red_flags=vision_result.get("red_flags", []),
    )


# ==========================================
# 6. Helpers - building the ScanResponse contract
# ==========================================
def score_to_risk_level(score: float) -> RiskLevel:
    if score >= 0.85:
        return RiskLevel.CRITICAL
    elif score >= 0.6:
        return RiskLevel.HIGH
    elif score >= 0.4:
        return RiskLevel.MEDIUM
    elif score >= 0.2:
        return RiskLevel.LOW
    else:
        return RiskLevel.SAFE


def score_to_severity(score: float) -> SeverityLevel:
    if score >= 0.85:
        return SeverityLevel.CRITICAL
    elif score >= 0.6:
        return SeverityLevel.HIGH
    elif score >= 0.4:
        return SeverityLevel.MEDIUM
    else:
        return SeverityLevel.LOW


def build_text_breakdown(text: str, text_result: Dict[str, Any]) -> TextAnalysisResult:
    """STOPGAP: LocalScamDetector only returns one combined heuristic score,
    not the three separate sub-scores this schema wants. Approximated here
    via binary presence of each regex pattern group. Aditi's module should
    ideally expose these natively instead of main.py re-deriving them."""
    text_lower = text.lower()

    urgency_score = 1.0 if any(re.search(p, text_lower) for p in URGENCY_PATTERNS) else round(text_result["ml_bert_score"] * 0.3, 4)
    impersonation_score = 1.0 if any(re.search(p, text_lower) for p in IMPERSONATION_PATTERNS) else round(text_result["ml_bert_score"] * 0.3, 4)
    financial_coercion_score = 1.0 if any(re.search(p, text_lower) for p in FINANCIAL_COERCION_PATTERNS) else round(text_result["ml_bert_score"] * 0.3, 4)

    entities = []
    for pattern in ENTITY_EXTRACTION_PATTERNS.values():
        entities.extend(re.findall(pattern, text))

    return TextAnalysisResult(
        urgency_score=urgency_score,
        impersonation_score=impersonation_score,
        financial_coercion_score=financial_coercion_score,
        extracted_entities=entities,
        risk_score=text_result["scam_confidence"],
    )


def build_url_breakdown(url_result: Dict[str, Any]) -> URLAnalysisResult:
    return URLAnalysisResult(
        extracted_urls=url_result["all_urls"],
        typosquatting_detected=url_result["top_typosquatting"],
        punycode_detected=False,  # NOT IMPLEMENTED: url_classifier has no punycode check yet
        domain_reputation_score=url_result["top_risk_score"],
        risk_score=url_result["top_risk_score"],
    )


def build_red_flags(fusion_result: Dict[str, Any], overall_score: float) -> List[RedFlag]:
    """Severity is approximated from the overall fused score, since FusionEngine
    doesn't track per-flag severity individually."""
    severity = score_to_severity(overall_score)
    flags = []
    for flag_text in fusion_result["aggregated_red_flags"]:
        indicator = re.sub(r"[^A-Z0-9]+", "_", flag_text.upper()).strip("_")[:40]
        flags.append(RedFlag(indicator=indicator, severity=severity, description=flag_text))
    return flags


def build_explanations(overall_score: float, risk_level: RiskLevel, flags: List[RedFlag]) -> Dict[SupportedLanguage, LocalizedGuidance]:
    """STOPGAP: only English is populated. Hindi/Marathi localization is not
    wired up yet - add real translations here once that pipeline exists."""
    flag_summary = "; ".join(f.description for f in flags) if flags else "No specific red flags detected."

    if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        action = "Do not click any links or make any payment. Verify directly with the official organization using a number from their real website."
    elif risk_level == RiskLevel.MEDIUM:
        action = "Be cautious. Independently verify the sender before taking any action."
    else:
        action = "No immediate action needed, but stay alert to unexpected requests for money or personal info."

    return {
        SupportedLanguage.EN: LocalizedGuidance(
            language=SupportedLanguage.EN,
            summary=f"This message was classified as {risk_level.value} risk ({round(overall_score * 100)}/100).",
            detailed_explanation=flag_summary,
            recommended_action=action,
        )
    }


def build_scan_response(
    fusion_result: Dict[str, Any],
    text: Optional[str],
    text_result: Optional[Dict[str, Any]],
    url_result: Optional[Dict[str, Any]],
    vision_result: Optional[Dict[str, Any]],
) -> ScanResponse:
    score = fusion_result["final_risk_score"]
    risk_level = score_to_risk_level(score)

    breakdown = ModalityBreakdown(
        text=build_text_breakdown(text, text_result) if (text and text_result) else None,
        url=build_url_breakdown(url_result) if url_result else None,
        visual=None,  # STOPGAP: DeepfakeAnalysisResult needs fields Manas's vision service
                      # response shape hasn't been confirmed to provide yet.
        audio=None,   # Audio pipeline not implemented yet.
    )

    red_flags = build_red_flags(fusion_result, score)

    return ScanResponse(
        task_id=str(uuid.uuid4()),
        overall_risk_score=round(score * 100),
        risk_level=risk_level,
        confidence=round(score, 4),
        modalities_processed=fusion_result["active_channels"],
        red_flags=red_flags,
        breakdown=breakdown,
        explanations=build_explanations(score, risk_level, red_flags),
    )


# ==========================================
# 7. Main Orchestration Endpoint
# ==========================================
@app.post("/api/v1/analyze", response_model=ScanResponse)
async def analyze_payload(request: AnalyzeRequest):
    """
    Core routing endpoint. Dispatches text/URL locally and async requests to the remote Vision API.
    Fuses all returned metrics into a single explainable risk score.
    """

    text_result: Optional[Dict[str, Any]] = None
    url_result: Optional[Dict[str, Any]] = None
    vision_result: Optional[Dict[str, Any]] = None

    # Step A: Local NLP and URL Processing (Aditi & Arnav)
    if request.text_input:
        if text_detector is None:
            raise HTTPException(status_code=503, detail="Text model not loaded yet, try again shortly")

        predictions, inference_time = text_detector.predict([request.text_input])
        text_result = predictions[0]
        text_result["inference_time_sec"] = round(inference_time, 4)

        url_result = run_url_analysis(request.text_input)

    # Step B: Remote Vision Processing (Manas) - Non-blocking HTTPX Call
    if request.image_base64:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    VISION_SERVICE_URL,
                    json={"image_base64": request.image_base64},
                    timeout=5.0
                )
                response.raise_for_status()
                vision_result = response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                print(f"[WARN] Vision microservice fallback triggered: {exc}")
                vision_result = {
                    "risk_score": 0.0,
                    "status": "unreachable_fallback",
                    "error_log": str(exc)
                }

    # Step C: Late-Fusion Risk Scoring
    fusion_result = fusion_engine.compute_final_risk(
        text_score=to_text_score(text_result),
        url_score=to_url_score(url_result),
        image_score=to_vision_score(vision_result),
        audio_score=None,
    )

    if request.force_high_risk:
        fusion_result["final_risk_score"] = 1.0
        fusion_result.setdefault("aggregated_red_flags", [])
        fusion_result["aggregated_red_flags"].append("Manual override (force_high_risk)")

    return build_scan_response(fusion_result, request.text_input, text_result, url_result, vision_result)