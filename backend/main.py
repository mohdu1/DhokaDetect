import re
import uuid
import base64
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from ml_services.model_manager import LocalScamDetector
from url_detection import url_classifier
from ml_services.fusion_engine import FusionEngine, ModalityScore
from schemas import (
    ScanResponse, RiskLevel, SeverityLevel, SupportedLanguage,
    TextAnalysisResult, URLAnalysisResult, VisualAnalysisResult, AudioAnalysisResult,
    RedFlag, ModalityBreakdown, LocalizedGuidance,
)

app = FastAPI(title="DhokaDetect Orchestration Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

VISION_SERVICE_URL = "http://127.0.0.1:8001/detect-media"
AUDIO_SERVICE_URL = "http://127.0.0.1:8001/analyze-audio"
URL_REGEX = re.compile(r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9-]+\.(?:com|in|co\.in|org|net)\b\S*)")

URGENCY_PATTERNS = [r"within \d+ mins?", r"immediate(ly)?", r"\btoday\b", r"avoid disconnection", r"account will be blocked"]
IMPERSONATION_PATTERNS = [r"\bmseb\b", r"electricity board", r"\bsbi\b", r"\bhdfc\b", r"\bkyc\b", r"update pan", r"\bupi\b"]
FINANCIAL_COERCION_PATTERNS = [r"₹\s?\d+", r"\brs\.?\s?\d+", r"\bpay\b", r"transfer money", r"send money", r"\botp\b", r"\brefund\b"]
ENTITY_EXTRACTION_PATTERNS = {
    "amount": r"₹\s?\d+(?:,\d+)*|\brs\.?\s?\d+(?:,\d+)*",
    "phone": r"\b\d{10}\b",
    "vpa": r"\b[\w.\-]+@[\w]+\b"
}

# Top-level model loading
try:
    print("[INIT] Loading LocalScamDetector...")
    text_detector = LocalScamDetector()
    print("[INIT] LocalScamDetector loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load LocalScamDetector: {e}")
    text_detector = None

fusion_engine = FusionEngine()

class AnalyzeRequest(BaseModel):
    text_input: Optional[str] = Field(None, description="Raw SMS/WhatsApp message text")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image or frame buffer")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio file (.wav format expected)")
    force_high_risk: Optional[bool] = Field(False, description="Manual override for demo purposes")

def run_url_analysis(text: str) -> Optional[Dict[str, Any]]:
    urls = URL_REGEX.findall(text)
    if not urls:
        return None
    analyzed = [{"url": u, **url_classifier.calculate_risk_score(u), "typosquatting": url_classifier.detect_typosquatting(u)} for u in urls]
    top = max(analyzed, key=lambda r: r["risk_score"])
    return {
        "urls_found": len(analyzed),
        "all_urls": [a["url"] for a in analyzed],
        "top_risk_score": top["risk_score"],
        "top_url": top["url"],
        "top_reasons": top["reasons"],
        "top_typosquatting": top["typosquatting"]["typosquatting"],
        "all_results": analyzed
    }

async def run_vision_analysis(image_b64: str) -> Dict[str, Any]:
    try:
        files = {"file": ("upload_media.jpg", base64.b64decode(image_b64, validate=True), "image/jpeg")}
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(VISION_SERVICE_URL, files=files, data={"task": "payment"})
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        return {"risk_score": 0.0, "status": "vision_fallback", "red_flags": [f"Vision Service Error: {str(exc)}"]}

async def run_audio_analysis(audio_b64: str) -> Dict[str, Any]:
    try:
        files = {"file": ("upload_audio.wav", base64.b64decode(audio_b64, validate=True), "audio/wav")}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(AUDIO_SERVICE_URL, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        return {"risk_score": 0.0, "verdict": "audio_fallback", "red_flags": [f"Audio Service Error: {str(exc)}"]}

def to_text_score(res: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    return ModalityScore(confidence=res.get("scam_confidence", 0.0), weight=0.25, red_flags=res.get("red_flags", [])) if res else None

def to_url_score(res: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    return ModalityScore(confidence=res["top_risk_score"], weight=0.35, red_flags=res.get("top_reasons", [])) if res else None

def to_vision_score(res: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    return ModalityScore(confidence=res.get("risk_score", 0.0), weight=0.20, red_flags=res.get("red_flags", [])) if res else None

def to_audio_score(res: Optional[Dict[str, Any]]) -> Optional[ModalityScore]:
    if not res:
        return None
    conf = res.get("risk_score", 0.0)
    flags = res.get("red_flags", [])
    if conf >= 0.4:
        flags.append(f"AI Synthetic Voice Flagged ({res.get('verdict', 'Suspicious')})")
    return ModalityScore(confidence=conf, weight=0.20, red_flags=flags)

def build_scan_response(fusion: Dict[str, Any], text: Optional[str], text_res: Optional[Dict[str, Any]], url_res: Optional[Dict[str, Any]], vis_res: Optional[Dict[str, Any]], aud_res: Optional[Dict[str, Any]]) -> ScanResponse:
    score = fusion["final_risk_score"]
    level = (
        RiskLevel.CRITICAL if score >= 0.85 else
        RiskLevel.HIGH if score >= 0.60 else
        RiskLevel.MEDIUM if score >= 0.40 else
        RiskLevel.LOW if score >= 0.20 else
        RiskLevel.SAFE
    )

    t_lower = (text or "").lower()
    bert = text_res.get("ml_bert_score", 0.0) if text_res else 0.0
    text_breakdown = TextAnalysisResult(
        urgency_score=1.0 if any(re.search(p, t_lower) for p in URGENCY_PATTERNS) else round(bert * 0.3, 4),
        impersonation_score=1.0 if any(re.search(p, t_lower) for p in IMPERSONATION_PATTERNS) else round(bert * 0.3, 4),
        financial_coercion_score=1.0 if any(re.search(p, t_lower) for p in FINANCIAL_COERCION_PATTERNS) else round(bert * 0.3, 4),
        extracted_entities=[m for p in ENTITY_EXTRACTION_PATTERNS.values() for m in re.findall(p, text or "")],
        risk_score=text_res.get("scam_confidence", 0.0) if text_res else 0.0
    ) if text else None

    url_breakdown = URLAnalysisResult(
        extracted_urls=url_res["all_urls"],
        typosquatting_detected=url_res["top_typosquatting"],
        punycode_detected=False,
        domain_reputation_score=url_res["top_risk_score"],
        risk_score=url_res["top_risk_score"]
    ) if url_res else None

    visual_breakdown = VisualAnalysisResult(
        manipulation_detected=vis_res.get("risk_score", 0.0) >= 0.5,
        qr_code_detected=False,
        risk_score=vis_res.get("risk_score", 0.0)
    ) if vis_res and "risk_score" in vis_res else None

    audio_breakdown = AudioAnalysisResult(
        synthetic_voice_detected=aud_res.get("risk_score", 0.0) >= 0.5,
        risk_score=aud_res.get("risk_score", 0.0)
    ) if aud_res and "risk_score" in aud_res else None

    flags = [
        RedFlag(
            indicator=re.sub(r"[^A-Z0-9]+", "_", f.upper()).strip("_")[:40],
            severity=SeverityLevel.HIGH if score >= 0.6 else SeverityLevel.MEDIUM if score >= 0.4 else SeverityLevel.LOW,
            description=f
        )
        for f in fusion.get("aggregated_red_flags", [])
    ]

    action_text = (
        "Do not click any links or transfer funds. Verify through the organization's official website."
        if level in (RiskLevel.HIGH, RiskLevel.CRITICAL) else
        "Exercise caution. Independently confirm sender identity."
        if level == RiskLevel.MEDIUM else
        "No immediate threat detected. Remain vigilant regarding unsolicited payment requests."
    )

    return ScanResponse(
        task_id=str(uuid.uuid4()),
        overall_risk_score=round(score * 100),
        risk_level=level,
        confidence=round(score, 4),
        modalities_processed=fusion["active_channels"],
        red_flags=flags,
        breakdown=ModalityBreakdown(
            text=text_breakdown,
            url=url_breakdown,
            visual=visual_breakdown,
            audio=audio_breakdown
        ),
        explanations={
            SupportedLanguage.EN: LocalizedGuidance(
                language=SupportedLanguage.EN,
                summary=f"Threat level evaluated as {level.value} ({round(score * 100)}/100).",
                detailed_explanation="; ".join(f.description for f in flags) or "No critical anomalies detected.",
                recommended_action=action_text
            )
        }
    )

async def perform_analysis(request: AnalyzeRequest) -> ScanResponse:
    text_result, url_result, vision_result, audio_result = None, None, None, None

    if request.text_input:
        if text_detector is None:
            text_result = {"scam_confidence": 0.0, "ml_bert_score": 0.0, "red_flags": ["Model initialization unavailable"]}
        else:
            try:
                predictions, inference_time = text_detector.predict([request.text_input])
                text_result = predictions[0]
                text_result["inference_time_sec"] = round(inference_time, 4)
            except Exception as exc:
                text_result = {"scam_confidence": 0.0, "ml_bert_score": 0.0, "red_flags": [f"Text evaluation exception: {str(exc)}"]}

        try:
            url_result = run_url_analysis(request.text_input)
        except Exception:
            url_result = None

    if request.image_base64:
        vision_result = await run_vision_analysis(request.image_base64)

    if request.audio_base64:
        audio_result = await run_audio_analysis(request.audio_base64)

    fusion_result = fusion_engine.compute_final_risk(
        text_score=to_text_score(text_result),
        url_score=to_url_score(url_result),
        image_score=to_vision_score(vision_result),
        audio_score=to_audio_score(audio_result)
    )

    if request.force_high_risk:
        fusion_result["final_risk_score"] = 1.0
        fusion_result.setdefault("aggregated_red_flags", []).append("Manual evaluation override")

    return build_scan_response(fusion_result, request.text_input, text_result, url_result, vision_result, audio_result)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "DhokaDetect Orchestration Engine",
        "version": "2.0",
        "text_detector_loaded": text_detector is not None
    }

@app.post("/api/v1/analyze", response_model=ScanResponse)
async def analyze_payload_v1(request: AnalyzeRequest):
    return await perform_analysis(request)

@app.post("/api/v2/analyze/multimodal", response_model=ScanResponse)
async def analyze_payload_v2(request: AnalyzeRequest):
    return await perform_analysis(request)