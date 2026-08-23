from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModalityScore(BaseModel):
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )

    weight: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0
    )

    red_flags: List[str] = Field(
        default_factory=list
    )


class FusionEngine:
    """
    Multimodal Late-Fusion Risk Engine for DhokaDetect.

    Fusion strategy:
        1. Weighted normalized fusion
        2. Strongest-channel protection
        3. Multi-channel evidence boost
        4. Final score clamped between 0 and 1

    Default weights:
        URL   = 0.35
        Text  = 0.25
        Image = 0.20
        Audio = 0.20
    """

    def __init__(self):

        self.default_weights = {
            "url": 0.35,
            "text": 0.25,
            "image": 0.20,
            "audio": 0.20
        }

        # Minimum percentage of strongest detector
        # that the final score should preserve.
        self.strong_signal_floor = 0.75

        # Small boost when multiple independent
        # modalities detect risk.
        self.multi_channel_boost = 0.05


    def compute_final_risk(
        self,
        text_score: Optional[ModalityScore] = None,
        url_score: Optional[ModalityScore] = None,
        image_score: Optional[ModalityScore] = None,
        audio_score: Optional[ModalityScore] = None
    ) -> Dict:

        # -------------------------------------------------
        # Collect modalities
        # -------------------------------------------------

        modalities = {
            "text": text_score,
            "url": url_score,
            "image": image_score,
            "audio": audio_score
        }


        # -------------------------------------------------
        # Keep only active modalities
        # -------------------------------------------------

        active_modalities = {
            name: data
            for name, data in modalities.items()
            if data is not None
        }


        # -------------------------------------------------
        # No valid input
        # -------------------------------------------------

        if not active_modalities:

            return {
                "final_risk_score": 0.0,
                "risk_level": "LOW RISK",
                "active_channels": [],
                "aggregated_red_flags": [],
                "explanation": (
                    "No valid input channels provided."
                )
            }


        # -------------------------------------------------
        # Fusion variables
        # -------------------------------------------------

        weighted_score_sum = 0.0
        total_weight = 0.0

        all_red_flags = []

        max_single_score = 0.0


        # -------------------------------------------------
        # Process active modalities
        # -------------------------------------------------

        for name, data in active_modalities.items():

            score = data.confidence

            # Use explicitly supplied weight if available.
            # Otherwise use default modality weight.
            if data.weight is not None:

                weight = data.weight

            else:

                weight = self.default_weights.get(
                    name,
                    0.25
                )


            # Weighted contribution
            weighted_score_sum += (
                score * weight
            )

            total_weight += weight


            # Collect red flags
            all_red_flags.extend(
                data.red_flags
            )


            # Track strongest detector
            if score > max_single_score:

                max_single_score = score


        # -------------------------------------------------
        # Normalized weighted fusion
        # -------------------------------------------------

        if total_weight > 0:

            fused_score = (
                weighted_score_sum /
                total_weight
            )

        else:

            fused_score = 0.0


        # -------------------------------------------------
        # Strongest-channel protection
        # -------------------------------------------------
        #
        # Prevent a strong detector from being diluted
        # excessively by weaker modalities.
        #
        # Example:
        #
        # Text = 0.8763
        # URL  = 0.35
        #
        # Normal fusion = ~0.57
        #
        # Strongest signal floor:
        #
        # 0.8763 × 0.75 = ~0.657
        #
        # Final score becomes at least ~0.657.
        # -------------------------------------------------

        if max_single_score >= 0.75:

            strongest_floor = (
                max_single_score *
                self.strong_signal_floor
            )

            fused_score = max(
                fused_score,
                strongest_floor
            )


        # -------------------------------------------------
        # Multi-channel evidence boost
        # -------------------------------------------------
        #
        # If two or more independent detection channels
        # are active, increase the score slightly.
        #
        # This represents corroborating evidence.
        # -------------------------------------------------

        active_channel_count = len(
            active_modalities
        )

        if active_channel_count >= 2:

            fused_score += (
                self.multi_channel_boost
            )


        # -------------------------------------------------
        # Additional red-flag corroboration
        # -------------------------------------------------
        #
        # If multiple modalities contributed red flags,
        # the evidence is stronger than a single-channel
        # detection.
        # -------------------------------------------------

        modality_flag_count = sum(
            1
            for data in active_modalities.values()
            if len(data.red_flags) > 0
        )

        if (
            modality_flag_count >= 2
            and active_channel_count >= 2
        ):

            fused_score += 0.025


        # -------------------------------------------------
        # Clamp score
        # -------------------------------------------------

        fused_score = max(
            0.0,
            min(
                fused_score,
                1.0
            )
        )


        # -------------------------------------------------
        # Determine risk level
        # -------------------------------------------------

        if fused_score >= 0.75:

            risk_level = "HIGH RISK"

        elif fused_score >= 0.40:

            risk_level = "MEDIUM RISK"

        else:

            risk_level = "LOW RISK"


        # -------------------------------------------------
        # Remove duplicate red flags
        # -------------------------------------------------

        unique_red_flags = list(
            dict.fromkeys(
                all_red_flags
            )
        )


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return {

            "final_risk_score": round(
                fused_score,
                4
            ),

            "risk_level": risk_level,

            "active_channels": list(
                active_modalities.keys()
            ),

            "aggregated_red_flags": (
                unique_red_flags
            ),

            "explanation": (
                "Risk score calculated using "
                "weighted late fusion with "
                "strong-signal protection and "
                "multi-channel evidence boosting."
            )
        }