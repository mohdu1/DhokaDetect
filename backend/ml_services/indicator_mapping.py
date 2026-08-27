"""
DhokaDetect - Standard Indicator Mapping

Converts raw detector evidence into stable indicator keys
used by the multilingual fallback translation dictionary.
"""


# =========================================================
# URL DETECTOR INDICATORS
# =========================================================

URL_INDICATORS = {
    "No HTTPS": "NO_HTTPS",
    "Very long URL": "LONG_URL",
    "Many special characters": "EXCESSIVE_SPECIAL_CHARACTERS",
    "IP address used as domain": "IP_ADDRESS_URL",
}


# =========================================================
# TEXT / SCAM INDICATORS
# =========================================================

TEXT_INDICATORS = {
    "urgency": "URGENCY_PRESSURE",
    "impersonation": "ENTITY_IMPERSONATION",
    "financial": "FINANCIAL_COERCION",
    "otp": "OTP_REQUEST",
    "payment": "PAYMENT_REQUEST",
    "refund": "REFUND_SCAM",
    "kyc": "KYC_REQUEST",
}


# =========================================================
# VISION INDICATORS
# =========================================================

VISION_INDICATORS = {
    "Visual Manipulation Detected": "VISUAL_MANIPULATION",
    "QR": "SUSPICIOUS_QR_CODE",
    "font": "VISUAL_FONT_INCONSISTENCY",
}


# =========================================================
# AUDIO INDICATORS
# =========================================================

AUDIO_INDICATORS = {
    "AI Synthetic Voice Flagged": "SYNTHETIC_VOICE_SIGNAL",
    "HUMAN_VOICE_SIGNAL": "HUMAN_VOICE_SIGNAL",
}


# =========================================================
# ML / MODEL INDICATORS
# =========================================================

ML_INDICATORS = {
    "Legitimate Transactional Context Detected": "ML_LEGITIMATE_CONTEXT",
    "High Scam Confidence": "ML_HIGH_SCAM_CONFIDENCE",
    "Suspicious Pattern Detected": "ML_SUSPICIOUS_PATTERN",
}


# =========================================================
# SYSTEM / MODEL INDICATORS
# =========================================================

SYSTEM_INDICATORS = {
    "Model initialization unavailable": "MODEL_UNAVAILABLE",
    "Manual evaluation override": "MANUAL_OVERRIDE",
}


# =========================================================
# NORMALIZATION FUNCTION
# =========================================================

def normalize_indicator(reason: str) -> str:
    """
    Convert a raw detector reason into a stable indicator key.

    Supports:
        - Exact detector messages
        - Dynamic detector messages
        - ML evidence
        - URL evidence
        - Vision evidence
        - Audio evidence
        - System errors
    """

    if not reason:
        return "UNKNOWN_INDICATOR"

    reason_clean = str(reason).strip()

    if not reason_clean:
        return "UNKNOWN_INDICATOR"

    # =====================================================
    # EXACT URL INDICATORS
    # =====================================================

    if reason_clean in URL_INDICATORS:
        return URL_INDICATORS[reason_clean]

    # =====================================================
    # DYNAMIC URL INDICATORS
    # =====================================================

    if reason_clean.startswith("Suspicious keywords:"):
        return "SUSPICIOUS_KEYWORD"

    if reason_clean.startswith("Possible typosquatting of"):
        return "TYPOSQUATTING"

    if reason_clean.startswith("Suspicious domain"):
        return "SUSPICIOUS_DOMAIN"

    if reason_clean.startswith("IP address used as domain"):
        return "IP_ADDRESS_URL"

    # =====================================================
    # TEXT / SOCIAL ENGINEERING INDICATORS
    # =====================================================

    if reason_clean.startswith("Urgency"):
        return "URGENCY_PRESSURE"

    if reason_clean.startswith("Impersonation"):
        return "ENTITY_IMPERSONATION"

    if reason_clean.startswith("Financial"):
        return "FINANCIAL_COERCION"

    if reason_clean.startswith("OTP"):
        return "OTP_REQUEST"

    if reason_clean.startswith("Payment"):
        return "PAYMENT_REQUEST"

    if reason_clean.startswith("Refund"):
        return "REFUND_SCAM"

    if reason_clean.startswith("KYC"):
        return "KYC_REQUEST"

    # =====================================================
    # VISION INDICATORS
    # =====================================================

    if reason_clean.startswith("Visual Manipulation Detected"):
        return "VISUAL_MANIPULATION"

    if reason_clean.startswith("Vision Service Error"):
        return "VISION_SERVICE_ERROR"

    if reason_clean.startswith("QR"):
        return "SUSPICIOUS_QR_CODE"

    if reason_clean.lower().startswith("font"):
        return "VISUAL_FONT_INCONSISTENCY"

    # =====================================================
    # AUDIO INDICATORS
    # =====================================================

    if reason_clean.startswith("AI Synthetic Voice Flagged"):
        return "SYNTHETIC_VOICE_SIGNAL"

    if reason_clean.startswith("Audio Service Error"):
        return "AUDIO_SERVICE_ERROR"

    if reason_clean.startswith("HUMAN_VOICE_SIGNAL"):
        return "HUMAN_VOICE_SIGNAL"

    # =====================================================
    # ML / MODEL EVIDENCE
    # =====================================================

    # Important:
    # This handles messages such as:
    #
    # "Legitimate Transactional Context Detected
    #  (Evidence: DistilBERT NLP confidence 19.8%)"
    #
    # and prevents them from becoming UNKNOWN_INDICATOR.

    if reason_clean.startswith("Legitimate Transactional Context Detected"):
        return "ML_LEGITIMATE_CONTEXT"

    if reason_clean.startswith("High Scam Confidence"):
        return "ML_HIGH_SCAM_CONFIDENCE"

    if reason_clean.startswith("Suspicious Pattern Detected"):
        return "ML_SUSPICIOUS_PATTERN"

    # =====================================================
    # MODEL / SYSTEM ERRORS
    # =====================================================

    if reason_clean.startswith("Model initialization unavailable"):
        return "MODEL_UNAVAILABLE"

    if reason_clean.startswith("Text evaluation exception"):
        return "TEXT_EVALUATION_ERROR"

    # =====================================================
    # MANUAL / DEMO INDICATOR
    # =====================================================

    if reason_clean.startswith("Manual evaluation override"):
        return "MANUAL_OVERRIDE"

    # =====================================================
    # GENERIC FALLBACK
    # =====================================================

    return "UNKNOWN_INDICATOR"