import re
import uuid
import base64
from typing import Optional, Dict, Any, List

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# =========================================================
# PROJECT IMPORTS
# =========================================================

from backend.ml_services.model_manager import LocalScamDetector
from backend.url_detection.url_classifier import (
    calculate_risk_score,
    detect_typosquatting,
)
from backend.ml_services.fusion_engine import (
    FusionEngine,
    ModalityScore,
)
from backend.ml_services.indicator_mapping import normalize_indicator
from backend.ml_services.translation_fallback import get_fallback_translation

from backend.schemas import (
    ScanResponse,
    RiskLevel,
    SeverityLevel,
    SupportedLanguage,
    TextAnalysisResult,
    URLAnalysisResult,
    VisualAnalysisResult,
    AudioAnalysisResult,
    RedFlag,
    ModalityBreakdown,
    LocalizedGuidance,
)

# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="DhokaDetect Orchestration Engine",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# SERVICE URLS
# =========================================================

VISION_SERVICE_URL = "http://127.0.0.1:8001/detect-media"
AUDIO_SERVICE_URL = "http://127.0.0.1:8001/analyze-audio"

# =========================================================
# URL / TEXT PATTERNS
# =========================================================

URL_REGEX = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|"
    r"\b[a-zA-Z0-9-]+\.(?:com|in|co\.in|org|net)\b[^\s]*)",
    re.IGNORECASE,
)

URGENCY_PATTERNS = [
    r"within\s+\d+\s*mins?",
    r"immediate(?:ly)?",
    r"\btoday\b",
    r"avoid\s+disconnection",
    r"account\s+will\s+be\s+blocked",
    r"\burgent\b",
    r"\bimmediately\b",
    r"expires?\s+(?:today|soon)",
]

IMPERSONATION_PATTERNS = [
    r"\bmseb\b",
    r"electricity\s+board",
    r"\bsbi\b",
    r"\bhdfc\b",
    r"\bkyc\b",
    r"update\s+pan",
    r"\bupi\b",
    r"\bicici\b",
    r"\baxis\b",
    r"\brbi\b",
    r"\bnpci\b",
]

FINANCIAL_COERCION_PATTERNS = [
    r"₹\s?\d+",
    r"\brs\.?\s?\d+",
    r"\bpay\b",
    r"transfer\s+money",
    r"send\s+money",
    r"\botp\b",
    r"\brefund\b",
    r"\bpayment\b",
    r"\bupi\b",
]

ENTITY_EXTRACTION_PATTERNS = {
    "amount": r"(?:₹\s?\d+(?:,\d+)*|\brs\.?\s?\d+(?:,\d+)*)",
    "phone": r"\b\d{10}\b",
    "vpa": r"\b[\w.\-+]+@[\w]+\b",
}

# =========================================================
# LOAD LOCAL TEXT MODEL
# =========================================================

try:
    print("[INIT] Loading LocalScamDetector...")
    text_detector = LocalScamDetector()
    print("[INIT] LocalScamDetector loaded successfully.")
except Exception as exc:
    print(f"[ERROR] Failed to load LocalScamDetector: {exc}")
    text_detector = None

# =========================================================
# FUSION ENGINE
# =========================================================

fusion_engine = FusionEngine()

# =========================================================
# REQUEST MODEL
# =========================================================

class AnalyzeRequest(BaseModel):
    text_input: Optional[str] = Field(
        None,
        description="Raw SMS/WhatsApp message text",
    )

    url_input: Optional[str] = Field(
        None,
        description="URL supplied directly for analysis",
    )

    image_base64: Optional[str] = Field(
        None,
        description="Base64 encoded image or frame buffer",
    )

    audio_base64: Optional[str] = Field(
        None,
        description="Base64 encoded audio file (.wav expected)",
    )

    language: SupportedLanguage = Field(
        SupportedLanguage.EN,
        description="Preferred response language",
    )

    force_high_risk: Optional[bool] = Field(
        False,
        description="Manual override for demo purposes",
    )


# =========================================================
# FLAG CLEANING / NORMALIZATION
# =========================================================

def clean_flag_text(flag: str) -> str:
    """
    Remove detector evidence text before normalization.

    Example:
        No HTTPS (Evidence: 'http://example.com')

    becomes:
        No HTTPS
    """

    if not flag:
        return ""

    cleaned = str(flag).strip()

    cleaned = re.sub(
        r"\s*\(Evidence:.*?\)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip()


def resolve_indicator(flag: str) -> str:
    """
    Convert detector output into a standard DhokaDetect
    indicator name.
    """

    cleaned = clean_flag_text(flag)

    # -----------------------------------------------------
    # Existing project indicator mapping
    # -----------------------------------------------------

    try:
        indicator = normalize_indicator(cleaned)

        if indicator and indicator != "UNKNOWN_INDICATOR":
            return indicator

    except Exception:
        pass

    # -----------------------------------------------------
    # Defensive mappings
    # -----------------------------------------------------

    lower = cleaned.lower()

    if "no https" in lower or "insecure connection" in lower:
        return "NO_HTTPS"

    if "suspicious keyword" in lower:
        return "SUSPICIOUS_KEYWORD"

    if "typosquatting" in lower:
        return "TYPOSQUATTING"

    if "punycode" in lower:
        return "PUNYCODE_DOMAIN"

    if "ip address" in lower:
        return "IP_ADDRESS_URL"

    if "urgent action" in lower:
        return "URGENCY_PRESSURE"

    if "urgency" in lower:
        return "URGENCY_PRESSURE"

    if "impersonation" in lower:
        return "ENTITY_IMPERSONATION"

    if "human voice" in lower:
        return "HUMAN_VOICE_SIGNAL"

    if "synthetic voice" in lower or "ai synthetic" in lower:
        return "SYNTHETIC_VOICE_SIGNAL"

    if "visual manipulation" in lower:
        return "VISUAL_MANIPULATION"

    if "font inconsistency" in lower:
        return "VISUAL_FONT_INCONSISTENCY"

    if "qr" in lower:
        return "SUSPICIOUS_QR_CODE"

    if "model initialization" in lower:
        return "MODEL_UNAVAILABLE"

    if "vision service error" in lower:
        return "VISION_SERVICE_ERROR"

    if "audio service error" in lower:
        return "AUDIO_SERVICE_ERROR"

    if "text evaluation exception" in lower:
        return "TEXT_EVALUATION_ERROR"

    if "manual evaluation override" in lower:
        return "MANUAL_OVERRIDE"

    # -----------------------------------------------------
    # Final attempt through mapping module
    # -----------------------------------------------------

    try:
        normalized = normalize_indicator(flag)

        if normalized:
            return normalized

    except Exception:
        pass

    return "UNKNOWN_INDICATOR"


# =========================================================
# FALLBACK TRANSLATION
# =========================================================

def build_localized_flag(
    flag: str,
    lang: str = "en",
) -> dict:

    indicator = resolve_indicator(flag)

    try:
        translation = get_fallback_translation(
            indicator,
            lang,
        )
    except Exception:
        translation = None

    if not translation:
        translation = {
            "title": clean_flag_text(flag),
            "explanation": clean_flag_text(flag),
            "action": (
                "Verify the information independently "
                "before taking any action."
            ),
        }

    return {
        "indicator": indicator,
        "title": translation.get(
            "title",
            clean_flag_text(flag),
        ),
        "explanation": translation.get(
            "explanation",
            clean_flag_text(flag),
        ),
        "action": translation.get(
            "action",
            "Verify the information independently.",
        ),
    }


# =========================================================
# URL ANALYSIS
# =========================================================

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs/domains from text safely.
    """

    if not text:
        return []

    matches = URL_REGEX.findall(text)

    cleaned_urls = []

    for url in matches:
        url = url.strip()

        url = url.rstrip(
            ".,;:!?)]}\"'"
        )

        if url and url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def run_url_analysis(
    text: Optional[str],
) -> Optional[Dict[str, Any]]:

    if not text:
        return None

    urls = extract_urls(text)

    if not urls:
        return None

    analyzed = []

    for url in urls:

        try:
            risk_result = calculate_risk_score(url)

        except Exception as exc:
            risk_result = {
                "risk_score": 0.0,
                "reasons": [
                    f"URL analysis error: {str(exc)}"
                ],
            }

        try:
            typo_result = detect_typosquatting(url)

        except Exception:
            typo_result = {
                "typosquatting": False,
            }

        analyzed.append(
            {
                "url": url,
                **risk_result,
                "typosquatting": typo_result,
            }
        )

    if not analyzed:
        return None

    top = max(
        analyzed,
        key=lambda result: float(
            result.get("risk_score", 0.0)
        ),
    )

    typo_data = top.get(
        "typosquatting",
        {},
    )

    if isinstance(typo_data, dict):
        typo_detected = bool(
            typo_data.get(
                "typosquatting",
                False,
            )
        )
    else:
        typo_detected = bool(typo_data)

    return {
        "urls_found": len(analyzed),

        "all_urls": [
            item["url"]
            for item in analyzed
        ],

        "top_risk_score": float(
            top.get("risk_score", 0.0)
        ),

        "top_url": top["url"],

        "top_reasons": list(
            top.get("reasons", [])
        ),

        "top_typosquatting": typo_detected,

        "all_results": analyzed,
    }


def run_direct_url_analysis(
    url: Optional[str],
) -> Optional[Dict[str, Any]]:

    if not url:
        return None

    return run_url_analysis(url)


# =========================================================
# VISION ANALYSIS
# =========================================================

async def run_vision_analysis(
    image_b64: str,
) -> Dict[str, Any]:

    try:

        image_bytes = base64.b64decode(
            image_b64,
            validate=True,
        )

        files = {
            "file": (
                "upload_media.jpg",
                image_bytes,
                "image/jpeg",
            )
        }

        async with httpx.AsyncClient(
            timeout=25.0
        ) as client:

            response = await client.post(
                VISION_SERVICE_URL,
                files=files,
                data={"task": "payment"},
            )

            response.raise_for_status()

            return response.json()

    except Exception as exc:

        return {
            "risk_score": 0.0,
            "status": "vision_fallback",
            "red_flags": [
                f"Vision Service Error: {str(exc)}"
            ],
        }


# =========================================================
# AUDIO ANALYSIS
# =========================================================

async def run_audio_analysis(
    audio_b64: str,
) -> Dict[str, Any]:

    try:

        audio_bytes = base64.b64decode(
            audio_b64,
            validate=True,
        )

        files = {
            "file": (
                "upload_audio.wav",
                audio_bytes,
                "audio/wav",
            )
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                AUDIO_SERVICE_URL,
                files=files,
            )

            response.raise_for_status()

            return response.json()

    except Exception as exc:

        return {
            "risk_score": 0.0,
            "verdict": "audio_fallback",
            "status": "audio_fallback",
            "red_flags": [
                f"Audio Service Error: {str(exc)}"
            ],
        }


# =========================================================
# TEXT → MODALITY SCORE
# =========================================================

def to_text_score(
    res: Optional[Dict[str, Any]],
) -> Optional[ModalityScore]:

    if not res:
        return None

    conf = float(
        res.get(
            "scam_confidence",
            0.0,
        )
    )

    evidence = (
        f"(Evidence: DistilBERT NLP confidence "
        f"{conf * 100:.1f}%)"
    )

    flags = [
        f"{flag} {evidence}"
        for flag in res.get(
            "red_flags",
            [],
        )
    ]

    return ModalityScore(
        confidence=max(
            0.0,
            min(1.0, conf),
        ),
        weight=0.25,
        red_flags=flags,
    )


# =========================================================
# URL → MODALITY SCORE
# =========================================================

def to_url_score(
    res: Optional[Dict[str, Any]],
) -> Optional[ModalityScore]:

    if not res:
        return None

    confidence = float(
        res.get(
            "top_risk_score",
            0.0,
        )
    )

    url = res.get(
        "top_url",
        "",
    )

    flags = []

    for reason in res.get(
        "top_reasons",
        [],
    ):

        flags.append(
            f"{reason} (Evidence: '{url}')"
        )

    if res.get(
        "top_typosquatting",
        False,
    ):

        typo_already_present = any(
            "typosquat" in str(flag).lower()
            for flag in flags
        )

        if not typo_already_present:
            flags.append(
                "Possible typosquatting "
                f"(Evidence: '{url}')"
            )

    return ModalityScore(
        confidence=max(
            0.0,
            min(1.0, confidence),
        ),
        weight=0.35,
        red_flags=flags,
    )


# =========================================================
# VISION → MODALITY SCORE
# =========================================================

def to_vision_score(
    res: Optional[Dict[str, Any]],
) -> Optional[ModalityScore]:

    if not res:
        return None

    conf = float(
        res.get(
            "risk_score",
            0.0,
        )
    )

    flags = list(
        res.get(
            "red_flags",
            [],
        )
    )

    if conf >= 0.5:

        evidence = (
            f"(Evidence: Swin Transformer confidence "
            f"{conf * 100:.1f}%)"
        )

        flags = [
            f"{flag} {evidence}"
            for flag in flags
        ]

        if not flags:
            flags.append(
                "Visual Manipulation Detected "
                f"{evidence}"
            )

    return ModalityScore(
        confidence=max(
            0.0,
            min(1.0, conf),
        ),
        weight=0.20,
        red_flags=flags,
    )


# =========================================================
# AUDIO → MODALITY SCORE
# =========================================================

def to_audio_score(
    res: Optional[Dict[str, Any]],
) -> Optional[ModalityScore]:

    if not res:
        return None

    conf = float(
        res.get(
            "risk_score",
            0.0,
        )
    )

    flags = list(
        res.get(
            "red_flags",
            [],
        )
    )

    if conf >= 0.4:

        verdict = res.get(
            "verdict",
            "Suspicious",
        )

        flags.append(
            "AI Synthetic Voice Flagged "
            "(Evidence: Wav2Vec2 detected "
            "Mel-spectrogram anomalies with "
            f"{conf * 100:.1f}% confidence. "
            f"Verdict: {verdict})"
        )

    elif (
        res.get("status") != "audio_fallback"
        and res.get("verdict") != "audio_fallback"
    ):

        flags.append(
            "HUMAN_VOICE_SIGNAL "
            "(Evidence: Audio recording analyzed; "
            "no synthetic-voice anomaly detected.)"
        )

    return ModalityScore(
        confidence=max(
            0.0,
            min(1.0, conf),
        ),
        weight=0.20,
        red_flags=flags,
    )


# =========================================================
# BUILD SCAN RESPONSE
# =========================================================

def build_scan_response(
    fusion: Dict[str, Any],
    text: Optional[str],
    requested_language: SupportedLanguage,
    text_res: Optional[Dict[str, Any]],
    url_res: Optional[Dict[str, Any]],
    vis_res: Optional[Dict[str, Any]],
    aud_res: Optional[Dict[str, Any]],
) -> ScanResponse:

    score = float(
        fusion.get(
            "final_risk_score",
            0.0,
        )
    )

    score = max(
        0.0,
        min(1.0, score),
    )

    # =====================================================
    # RISK LEVEL
    # =====================================================

    if score >= 0.85:
        level = RiskLevel.CRITICAL

    elif score >= 0.60:
        level = RiskLevel.HIGH

    elif score >= 0.40:
        level = RiskLevel.MEDIUM

    elif score >= 0.20:
        level = RiskLevel.LOW

    else:
        level = RiskLevel.SAFE

    # =====================================================
    # TEXT BREAKDOWN
    # =====================================================

    t_lower = (text or "").lower()

    bert = float(
        text_res.get(
            "ml_bert_score",
            0.0,
        )
        if text_res
        else 0.0
    )

    text_breakdown = None

    if text:

        text_breakdown = TextAnalysisResult(

            urgency_score=(
                1.0
                if any(
                    re.search(
                        pattern,
                        t_lower,
                    )
                    for pattern in URGENCY_PATTERNS
                )
                else round(
                    bert * 0.3,
                    4,
                )
            ),

            impersonation_score=(
                1.0
                if any(
                    re.search(
                        pattern,
                        t_lower,
                    )
                    for pattern in IMPERSONATION_PATTERNS
                )
                else round(
                    bert * 0.3,
                    4,
                )
            ),

            financial_coercion_score=(
                1.0
                if any(
                    re.search(
                        pattern,
                        t_lower,
                    )
                    for pattern in FINANCIAL_COERCION_PATTERNS
                )
                else round(
                    bert * 0.3,
                    4,
                )
            ),

            extracted_entities=[
                match
                for pattern in ENTITY_EXTRACTION_PATTERNS.values()
                for match in re.findall(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )
            ],

            risk_score=float(
                text_res.get(
                    "scam_confidence",
                    0.0,
                )
                if text_res
                else 0.0
            ),
        )

    # =====================================================
    # URL BREAKDOWN
    # =====================================================

    url_breakdown = None

    if url_res:

        url_breakdown = URLAnalysisResult(

            extracted_urls=url_res.get(
                "all_urls",
                [],
            ),

            typosquatting_detected=bool(
                url_res.get(
                    "top_typosquatting",
                    False,
                )
            ),

            punycode_detected=False,

            domain_reputation_score=float(
                url_res.get(
                    "top_risk_score",
                    0.0,
                )
            ),

            risk_score=float(
                url_res.get(
                    "top_risk_score",
                    0.0,
                )
            ),
        )

    # =====================================================
    # VISUAL BREAKDOWN
    # =====================================================

    visual_breakdown = None

    if (
        vis_res
        and "risk_score" in vis_res
        and vis_res.get("status") != "vision_fallback"
    ):

        visual_breakdown = VisualAnalysisResult(

            manipulation_detected=(
                float(
                    vis_res.get(
                        "risk_score",
                        0.0,
                    )
                ) >= 0.5
            ),

            qr_code_detected=False,

            risk_score=float(
                vis_res.get(
                    "risk_score",
                    0.0,
                )
            ),
        )

    # =====================================================
    # AUDIO BREAKDOWN
    # =====================================================

    audio_breakdown = None

    if (
        aud_res
        and "risk_score" in aud_res
        and aud_res.get("status") != "audio_fallback"
    ):

        audio_breakdown = AudioAnalysisResult(

            synthetic_voice_detected=(
                float(
                    aud_res.get(
                        "risk_score",
                        0.0,
                    )
                ) >= 0.5
            ),

            risk_score=float(
                aud_res.get(
                    "risk_score",
                    0.0,
                )
            ),
        )

    # =====================================================
    # RAW RED FLAGS
    # =====================================================

    raw_flags = fusion.get(
        "aggregated_red_flags",
        [],
    )

    flags = []

    for raw_flag in raw_flags:

        flag_text = str(raw_flag)

        indicator = resolve_indicator(
            flag_text
        )

        if score >= 0.60:
            severity = SeverityLevel.HIGH

        elif score >= 0.40:
            severity = SeverityLevel.MEDIUM

        else:
            severity = SeverityLevel.LOW

        flags.append(
            RedFlag(
                indicator=indicator,
                severity=severity,
                description=clean_flag_text(
                    flag_text
                ),
            )
        )

    # =====================================================
    # OFFLINE TRANSLATION
    # =====================================================

    localized_flags = {
        "en": [
            build_localized_flag(
                flag.description,
                "en",
            )
            for flag in flags
        ],

        "hi": [
            build_localized_flag(
                flag.description,
                "hi",
            )
            for flag in flags
        ],

        "mr": [
            build_localized_flag(
                flag.description,
                "mr",
            )
            for flag in flags
        ],
    }

    # =====================================================
    # DEFAULT ACTION
    # =====================================================

    if level in (
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    ):

        action_text = (
            "Do not click any links or transfer funds. "
            "Verify through the organization's official website."
        )

    elif level == RiskLevel.MEDIUM:

        action_text = (
            "Exercise caution. "
            "Independently confirm sender identity."
        )

    else:

        action_text = (
            "No immediate threat detected. "
            "Remain vigilant regarding unsolicited "
            "payment requests."
        )

    # =====================================================
    # BUILD GUIDANCE FOR ALL LANGUAGES
    # =====================================================

    english_summary = (
        f"Threat level evaluated as "
        f"{level.value} "
        f"({round(score * 100)}/100)."
    )

    english_details = (
        "; ".join(
            item["explanation"]
            for item in localized_flags["en"]
        )
        or "No critical anomalies detected."
    )

    english_action = (
        localized_flags["en"][0]["action"]
        if localized_flags["en"]
        else action_text
    )

    hindi_summary = (
        f"खतरे का स्तर {level.value} "
        f"आंका गया है ({round(score * 100)}/100)।"
    )

    hindi_details = (
        "; ".join(
            item["explanation"]
            for item in localized_flags["hi"]
        )
        or "कोई गंभीर असामान्यता नहीं मिली।"
    )

    hindi_action = (
        localized_flags["hi"][0]["action"]
        if localized_flags["hi"]
        else
        "सावधानी बरतें और अनुरोध की स्वतंत्र रूप से पुष्टि करें।"
    )

    marathi_summary = (
        f"धोक्याची पातळी {level.value} "
        f"अशी निश्चित करण्यात आली आहे "
        f"({round(score * 100)}/100)."
    )

    marathi_details = (
        "; ".join(
            item["explanation"]
            for item in localized_flags["mr"]
        )
        or "कोणतीही गंभीर विसंगती आढळली नाही."
    )

    marathi_action = (
        localized_flags["mr"][0]["action"]
        if localized_flags["mr"]
        else
        "सावध राहा आणि विनंतीची स्वतंत्रपणे खात्री करा."
    )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    response = ScanResponse(

        task_id=str(uuid.uuid4()),

        overall_risk_score=round(
            score * 100
        ),

        risk_level=level,

        confidence=round(
            score,
            4,
        ),

        modalities_processed=(
            fusion.get(
                "active_channels",
                [],
            )
        ),

        red_flags=flags,

        breakdown=ModalityBreakdown(
            text=text_breakdown,
            url=url_breakdown,
            visual=visual_breakdown,
            audio=audio_breakdown,
        ),

        explanations={

            SupportedLanguage.EN:
                LocalizedGuidance(
                    language=SupportedLanguage.EN,
                    summary=english_summary,
                    detailed_explanation=english_details,
                    recommended_action=english_action,
                ),

            SupportedLanguage.HI:
                LocalizedGuidance(
                    language=SupportedLanguage.HI,
                    summary=hindi_summary,
                    detailed_explanation=hindi_details,
                    recommended_action=hindi_action,
                ),

            SupportedLanguage.MR:
                LocalizedGuidance(
                    language=SupportedLanguage.MR,
                    summary=marathi_summary,
                    detailed_explanation=marathi_details,
                    recommended_action=marathi_action,
                ),
        },
    )

    return response


# =========================================================
# MAIN ANALYSIS PIPELINE
# =========================================================

async def perform_analysis(
    request: AnalyzeRequest,
) -> ScanResponse:

    text_result = None
    url_result = None
    vision_result = None
    audio_result = None

    # =====================================================
    # TEXT ANALYSIS
    # =====================================================

    if request.text_input:

        if text_detector is None:

            text_result = {
                "scam_confidence": 0.0,
                "ml_bert_score": 0.0,
                "red_flags": [
                    "Model initialization unavailable"
                ],
            }

        else:

            try:

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
                    "red_flags": [
                        f"Text evaluation exception: {str(exc)}"
                    ],
                }

    # =====================================================
    # URL ANALYSIS
    # =====================================================

    try:

        if request.url_input:

            url_result = run_direct_url_analysis(
                request.url_input
            )

        elif request.text_input:

            url_result = run_url_analysis(
                request.text_input
            )

    except Exception as exc:

        print(
            f"[WARNING] URL analysis failed: {exc}"
        )

        url_result = None

    # =====================================================
    # IMAGE ANALYSIS
    # =====================================================

    if request.image_base64:

        vision_result = await run_vision_analysis(
            request.image_base64
        )

    # =====================================================
    # AUDIO ANALYSIS
    # =====================================================

    if request.audio_base64:

        audio_result = await run_audio_analysis(
            request.audio_base64
        )

    # =====================================================
    # MULTIMODAL FUSION
    # =====================================================

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

            audio_score=to_audio_score(
                audio_result
            ),
        )
    )

    # =====================================================
    # DEMO OVERRIDE
    # =====================================================

    if request.force_high_risk:

        fusion_result[
            "final_risk_score"
        ] = 1.0

        fusion_result.setdefault(
            "aggregated_red_flags",
            [],
        ).append(
            "Manual evaluation override"
        )

    # =====================================================
    # BUILD RESPONSE
    # =====================================================

    return build_scan_response(
        fusion_result,
        request.text_input,
        request.language,
        text_result,
        url_result,
        vision_result,
        audio_result,
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "service": "DhokaDetect Orchestration Engine",
        "version": "2.0",
        "text_detector_loaded": (
            text_detector is not None
        ),
    }


# =========================================================
# API V1
# =========================================================

@app.post(
    "/api/v1/analyze",
    response_model=ScanResponse,
)
async def analyze_payload_v1(
    request: AnalyzeRequest,
):

    return await perform_analysis(
        request
    )


# =========================================================
# API V2 MULTIMODAL
# =========================================================

@app.post(
    "/api/v2/analyze/multimodal",
    response_model=ScanResponse,
)
async def analyze_payload_v2(
    request: AnalyzeRequest,
):

    return await perform_analysis(
        request
    )