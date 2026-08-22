from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ModalityScore(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(0.25, ge=0.0, le=1.0)
    red_flags: List[str] = Field(default_factory=list)

class FusionEngine:
    """
    Multimodal Late-Fusion Risk Engine for DhokaDetect.
    Resolves conflicts when Text, URL, Image/OCR, or Audio detectors yield different results.
    """
    def __init__(self):
        self.default_weights = {
            "url": 0.35,
            "text": 0.25,
            "image": 0.20,
            "audio": 0.20
        }

    def compute_final_risk(
        self,
        text_score: Optional[ModalityScore] = None,
        url_score: Optional[ModalityScore] = None,
        image_score: Optional[ModalityScore] = None,
        audio_score: Optional[ModalityScore] = None
    ) -> Dict:
        
        modalities = {
            "text": text_score,
            "url": url_score,
            "image": image_score,
            "audio": audio_score
        }

        active_modalities = {k: v for k, v in modalities.items() if v is not None}
        
        if not active_modalities:
            return {
                "final_risk_score": 0.0, 
                "risk_level": "LOW RISK", 
                "active_channels": [],
                "aggregated_red_flags": [],
                "explanation": "No valid input channels provided."
            }

        weighted_score_sum = 0.0
        total_weight = 0.0
        all_red_flags = []
        max_single_score = 0.0

        for name, data in active_modalities.items():
            score = data.confidence
            weight = data.weight if data.weight > 0 else self.default_weights.get(name, 0.25)
            
            weighted_score_sum += score * weight
            total_weight += weight
            all_red_flags.extend(data.red_flags)
            
            if score > max_single_score:
                max_single_score = score

        fused_score = weighted_score_sum / total_weight if total_weight > 0 else 0.0

        # Safety Override for High-Confidence Signals
        if max_single_score >= 0.90 and fused_score < 0.70:
            fused_score = max_single_score * 0.85

        if fused_score >= 0.75:
            risk_level = "HIGH RISK"
        elif fused_score >= 0.40:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"

        return {
            "final_risk_score": round(fused_score, 4),
            "risk_level": risk_level,
            "active_channels": list(active_modalities.keys()),
            "aggregated_red_flags": list(set(all_red_flags))
        }