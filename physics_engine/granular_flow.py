"""
Ghat-Guard v5.0 - Chunk 3: Compressible Non-Newtonian Granular Flow Physics Engine
Target: Kotilingala Ghat Terminal (Rajahmundry Municipal Corporation)
"""

import math

class GranularFlowEngine:
    def __init__(self, max_packing_density: float = 5.5):
        """
        Initializes the granular flow engine.
        max_packing_density: Absolute physical jamming limit (p/m²) where movement halts entirely.
        """
        self.max_packing_density = max_packing_density

    def compute_granular_viscosity(self, density: float, shear_rate: float) -> float:
        """
        Computes apparent granular viscosity (in Pa·s equivalent) using a 
        Krieger-Dougherty style dilatant (shear-thickening) model for dense crowds.
        """
        if shear_rate <= 0.001:
            shear_rate = 0.001  # Prevent division by zero
            
        # Clamp density safely below maximum packing limit
        phi = min(density, self.max_packing_density - 0.05)
        phi_max = self.max_packing_density
        
        # Dilatant viscosity scaling: viscosity spikes exponentially as density nears packing limit
        viscosity_base = 1.0  
        scaling_factor = (phi / (phi_max - phi)) ** 1.8
        
        # Apparent viscosity calculation
        apparent_viscosity = viscosity_base * (1.0 + scaling_factor) / (shear_rate ** 0.3)
        return round(apparent_viscosity, 4)

    def classify_flow_phase(self, density: float, velocity: float, viscosity: float) -> str:
        """
        Classifies crowd movement into 3 physical phases:
          - GAS Phase: Low density, high velocity (free movement)
          - LIQUID Phase: Moderate density, laminar flow
          - SOLID Phase (స్తంభన / Stambhana): Critical density collapse, near-zero velocity, infinite viscosity
        """
        if density >= 4.0 or velocity < 0.25 or viscosity > 150.0:
            return "SOLID"    # Stambhana / Critical Jam
        elif density >= 1.5:
            return "LIQUID"   # Laminar Flow
        else:
            return "GAS"      # Free Flow


# --- Test Execution Verification ---
if __name__ == "__main__":
    engine = GranularFlowEngine()
    
    print("=== Ghat-Guard v5.0: Granular Flow Physics Simulations ===")
    test_cases = [
        (1.1, 1.4),  # Nominal free flow (Gas)
        (2.6, 0.9),  # Moderate laminar flow (Liquid)
        (4.2, 0.1)   # Critical crowd surge / Stambhana (Solid)
    ]
    
    for dens, vel in test_cases:
        # Estimate shear rate proportional to velocity gradient
        shear = max(0.05, vel * 0.8)
        visc = engine.compute_granular_viscosity(dens, shear)
        phase = engine.classify_flow_phase(dens, vel, visc)
        
        print(f"Density: {dens} p/m² | Velocity: {vel} m/s | Shear: {shear:.2f} s⁻¹")
        print(f"  -> Granular Viscosity: {visc} Pa·s | Computed Phase: {phase}\n")