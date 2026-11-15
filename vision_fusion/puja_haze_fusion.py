"""
Ghat-Guard v5.0 - Multi-Modal Thermal & Optical Vision Fusion
Kotilingala Ghat Terminal (Godavari Pushkaralu 2027)

LWIR thermal fusion pipeline designed to bypass heavy ritual smoke
(Harati Puja haze) that blinds standard RGB cameras.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FusionResult:
    optical_density: float
    thermal_density: float
    smoke_opacity: float
    fused_density: float
    optical_weight: float
    thermal_weight: float
    puja_haze_filter_active: bool
    confidence: float
    status: str

    def to_dict(self) -> dict:
        return {
            "optical_density": round(self.optical_density, 3),
            "thermal_density": round(self.thermal_density, 3),
            "smoke_opacity": round(self.smoke_opacity, 3),
            "fused_density": round(self.fused_density, 3),
            "optical_weight": round(self.optical_weight, 3),
            "thermal_weight": round(self.thermal_weight, 3),
            "puja_haze_filter_active": self.puja_haze_filter_active,
            "confidence": round(self.confidence, 3),
            "status": self.status,
        }


class HaratiVisionFusionEngine:
    def __init__(self, smoke_threshold: float = 0.35):
        self.smoke_threshold = smoke_threshold

    def fuse_sensors(
        self,
        optical_density: float,
        thermal_density: float,
        smoke_opacity: float,
        optical_confidence: float = 1.0,
        thermal_confidence: float = 1.0,
    ) -> dict:
        optical_density = max(0.0, min(10.0, float(optical_density)))
        thermal_density = max(0.0, min(10.0, float(thermal_density)))
        opacity = max(0.0, min(1.0, float(smoke_opacity)))
        optical_confidence = max(0.0, min(1.0, float(optical_confidence)))
        thermal_confidence = max(0.0, min(1.0, float(thermal_confidence)))

        if opacity >= self.smoke_threshold:
            # Harati Puja haze: RGB degrades rapidly; shift to LWIR thermal.
            haze_factor = min(1.0, (opacity - self.smoke_threshold) / (1.0 - self.smoke_threshold + 1e-6))
            optical_weight = max(0.05, (1.0 - 0.95 * haze_factor) * optical_confidence)
            thermal_weight = max(0.05, (0.35 + 0.65 * haze_factor) * thermal_confidence)
            haze_active = True
            status = "హారతి పొగ ఫిల్టర్ యాక్టివ్ (Puja Haze Filter Active) - LWIR Thermal Shift"
        else:
            optical_weight = 0.75 * max(0.2, optical_confidence)
            thermal_weight = 0.25 * max(0.2, thermal_confidence)
            haze_active = False
            status = "నామినల్ ఆప్టికల్-థర్మల్ ఫ్యూజన్ (Nominal Optical-Thermal Fusion)"

        norm = optical_weight + thermal_weight
        optical_weight /= norm
        thermal_weight /= norm

        fused_density = (optical_density * optical_weight) + (thermal_density * thermal_weight)

        # Confidence reflects agreement between sensors and haze severity.
        agreement = 1.0 - min(1.0, abs(optical_density - thermal_density) / 6.0)
        confidence = (agreement * (0.6 + 0.4 * thermal_confidence)) * (0.85 if haze_active else 1.0)

        result = FusionResult(
            optical_density=optical_density,
            thermal_density=thermal_density,
            smoke_opacity=opacity,
            fused_density=fused_density,
            optical_weight=optical_weight,
            thermal_weight=thermal_weight,
            puja_haze_filter_active=haze_active,
            confidence=confidence,
            status=status,
        )
        return result.to_dict()


if __name__ == "__main__":
    engine = HaratiVisionFusionEngine()
    print(engine.fuse_sensors(3.8, 3.5, 0.78))
