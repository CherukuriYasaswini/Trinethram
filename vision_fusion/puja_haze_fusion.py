"""
Ghat-Guard v5.0 - Chunk 5: Multi-Modal Thermal & Optical Vision Fusion
Feature: Harati Puja Haze Filter (హారతి పొగ ఫిల్టర్)
Target: Kotilingala Ghat Terminal (Rajahmundry Municipal Corporation)
"""

class HaratiVisionFusionEngine:
    def __init__(self, smoke_threshold: float = 0.35):
        self.smoke_threshold = smoke_threshold

    def fuse_sensors(self, optical_density: float, thermal_density: float, smoke_opacity: float) -> dict:
        """
        Fuses visible-light optical feed with LWIR thermal sensor data.
        Applies the Harati Puja Haze Filter to dynamically reweight sensor confidence
        when camphor/incense smoke occludes visible cameras.
        """
        # Clamp opacity between 0.0 (clear air) and 1.0 (dense ritual smoke)
        opacity = max(0.0, min(1.0, smoke_opacity))
        
        # Determine fusion weights based on smoke occlusion
        if opacity >= self.smoke_threshold:
            # Heavy smoke condition: Attenuate optical confidence, rely heavily on LWIR thermal
            optical_weight = max(0.1, 1.0 - (opacity * 1.2))
            thermal_weight = 1.0 - optical_weight
            haze_filter_active = True
            status_msg = "హారతి పొగ ఫిల్టర్ యాక్టివ్ (Puja Haze Filter Active) - LWIR Thermal Shift"
        else:
            # Clear condition: Standard optical-primary weighting
            optical_weight = 0.75
            thermal_weight = 0.25
            haze_filter_active = False
            status_msg = "నామినల్ ఆప్టికల్-థర్మల్ ఫ్యూజన్ (Nominal Optical-Thermal Fusion)"

        # Compute fused crowd density
        fused_density = (optical_density * optical_weight) + (thermal_density * thermal_weight)

        return {
            "optical_density": round(optical_density, 2),
            "thermal_density": round(thermal_density, 2),
            "smoke_opacity": round(opacity, 2),
            "fused_density": round(fused_density, 2),
            "optical_weight": round(optical_weight, 2),
            "thermal_weight": round(thermal_weight, 2),
            "puja_haze_filter_active": haze_filter_active,
            "status": status_msg
        }


# --- Test Execution Verification ---
if __name__ == "__main__":
    engine = HaratiVisionFusionEngine()
    
    print("=== Ghat-Guard v5.0: Harati Puja Haze Vision Fusion Simulations ===")
    scenarios = [
        ("Nominal Afternoon Clear Air", 1.2, 1.1, 0.05),
        ("Evening Harati Ritual Smoke Surge", 3.8, 3.5, 0.78),
        ("Post-Ritual Clearing Phase", 2.1, 2.0, 0.20)
    ]
    
    for title, opt, therm, smoke in scenarios:
        result = engine.fuse_sensors(opt, therm, smoke)
        print(f"Scenario: {title}")
        print(f"  -> Optical: {result['optical_density']} | Thermal: {result['thermal_density']} | Smoke Opacity: {result['smoke_opacity']}")
        print(f"  -> Weights [Opt/Therm]: [{result['optical_weight']} / {result['thermal_weight']}]")
        print(f"  -> Fused Density: {result['fused_density']} p/m²")
        print(f"  -> State: {result['status']}\n")