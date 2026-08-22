from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SupportedLanguage(str, Enum):
    EN = "en"
    HI = "hi"
    MR = "mr"


# ==========================================
# 1. Microservice Ingestion & Response Models
# ==========================================

class TextAnalysisResult(BaseModel):
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Confidence of fabricated urgency/panic")
    impersonation_score: float = Field(..., ge=0.0, le=1.0, description="Detection of authority/brand impersonation")
    financial_coercion_score: float = Field(..., ge=0.0, le=1.0, description="Presence of payment redirection demands")
    extracted_entities: List[str] = Field(default_factory=list, description="Extracted VPAs, phone numbers, account tags")
    risk_score: float = Field(..., ge=0.0, le=1.0)


class DeepfakeAnalysisResult(BaseModel):
    media_type: str = Field(..., pattern="^(image|video)$", description="Type of visual media analyzed")
    face_manipulation_score: float = Field(..., ge=0.0, le=1.0, description="Spatial artifact score (e.g., EfficientNet/ViT)")
    temporal_inconsistency_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Frame-to-frame jitter/flicker score for video inputs"
    )
    metadata_tampering_score: float = Field(..., ge=0.0, le=1.0, description="EXIF/Container anomaly score")
    frames_analyzed: Optional[int] = Field(None, ge=1, description="Total sampled frames if video")
    risk_score: float = Field(..., ge=0.0, le=1.0)


class AudioAnalysisResult(BaseModel):
    voice_cloning_score: float = Field(..., ge=0.0, le=1.0, description="Synthetic voice/TTS likelihood")
    spectral_artifact_score: float = Field(..., ge=0.0, le=1.0, description="Bispectral/Mel-spectrogram anomalies")
    risk_score: float = Field(..., ge=0.0, le=1.0)


class URLAnalysisResult(BaseModel):
    extracted_urls: List[str] = Field(default_factory=list)
    typosquatting_detected: bool = False
    punycode_detected: bool = False
    domain_reputation_score: float = Field(..., ge=0.0, le=1.0, description="0 is trusted, 1 is known malicious")
    risk_score: float = Field(..., ge=0.0, le=1.0)


# ==========================================
# 2. Explainability & Regional Output Models
# ==========================================

class RedFlag(BaseModel):
    indicator: str = Field(..., description="Short tag, e.g., 'TEMPORAL_FLICKER' or 'FAKE_URGENCY'")
    severity: SeverityLevel
    description: str = Field(..., description="Technical rationale behind the flag")


class LocalizedGuidance(BaseModel):
    language: SupportedLanguage
    summary: str
    detailed_explanation: str
    recommended_action: str


# ==========================================
# 3. Final Aggregated Orchestration Contract
# ==========================================

class ModalityBreakdown(BaseModel):
    text: Optional[TextAnalysisResult] = None
    visual: Optional[DeepfakeAnalysisResult] = None
    audio: Optional[AudioAnalysisResult] = None
    url: Optional[URLAnalysisResult] = None


class ScanResponse(BaseModel):
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_risk_score: int = Field(..., ge=0, le=100, description="Aggregated Late-Fusion Risk Score (0-100)")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Ensemble confidence metric")
    modalities_processed: List[str]
    red_flags: List[RedFlag]
    breakdown: ModalityBreakdown
    explanations: Dict[SupportedLanguage, LocalizedGuidance]