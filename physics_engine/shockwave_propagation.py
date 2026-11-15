"""
Ghat-Guard v5.0 - Chunk 4: Upstream Shockwave & Chevron Vector Tracing Pipeline
Target: Kotilingala Ghat Terminal (Rajahmundry Municipal Corporation)
"""

class ShockwavePropagationEngine:
    def __init__(self):
        # Ghat topology mapping (Downstream step -> Upstream approach zone)
        self.topology_graph = {
            "Pen_Step_3": ["Approach_Gate_B", "Queue_Corridor_North"],
            "Queue_Corridor_North": ["Main_Entry_Plaza"]
        }

    def calculate_kinematic_wave_speed(self, density_downstream: float, velocity_downstream: float) -> float:
        """
        Calculates kinematic shockwave propagation velocity upstream (v_wave)
        using flux-gradient approximations for dense crowds.
        """
        if density_downstream <= 0.1:
            return 0.0
        
        # Shockwave travels upstream opposite to crowd flow direction when congested
        d_flux_d_dens = velocity_downstream * (1.0 - (2.0 * density_downstream / 5.5))
        return round(d_flux_d_dens, 3)

    def propagate_shockwave(self, node_id: str, current_density: float, current_velocity: float) -> dict:
        """
        Evaluates if downstream congestion triggers an upstream shockwave,
        generating terracotta-red chevron vector indicators (⬇⬇⬇) for the command console.
        """
        wave_speed = self.calculate_kinematic_wave_speed(current_density, current_velocity)
        is_shockwave_active = current_density >= 3.8 or wave_speed <= -0.15

        chevron_intensity = 0
        if is_shockwave_active:
            if current_density >= 4.5:
                chevron_intensity = 3  # Maximum alert: ⬇⬇⬇ Terracotta Red
            elif current_density >= 4.0:
                chevron_intensity = 2  # Moderate alert: ⬇⬇
            else:
                chevron_intensity = 1  # Warning: ⬇

        chevron_string = "⬇ " * chevron_intensity if chevron_intensity > 0 else "---"

        return {
            "node_id": node_id,
            "downstream_density": current_density,
            "shockwave_speed_ms": wave_speed,
            "shockwave_active": is_shockwave_active,
            "chevron_vector": chevron_string.strip(),
            "status_message": "UPSTREAM SHOCKWAVE DETECTED - STAMBHANA PROPAGATING" if is_shockwave_active else "LAMINAR FLOW - NO BACKPRESSURE"
        }


# --- Test Execution Verification ---
if __name__ == "__main__":
    engine = ShockwavePropagationEngine()
    
    print("=== Ghat-Guard v5.0: Upstream Shockwave & Chevron Vector Simulations ===")
    scenarios = [
        ("Pen_Step_3", 1.2, 1.2),  # Nominal free flow
        ("Pen_Step_3", 3.2, 0.5),  # Building pressure
        ("Pen_Step_3", 4.3, 0.08)  # Critical Stambhana shockwave collapse
    ]
    
    for node, dens, vel in scenarios:
        result = engine.propagate_shockwave(node, dens, vel)
        print(f"Node: {result['node_id']} | Density: {result['downstream_density']} p/m²")
        print(f"  -> Shockwave Speed: {result['shockwave_speed_ms']} m/s")
        print(f"  -> Vector Tracing: [{result['chevron_vector']}]")
        print(f"  -> State: {result['status_message']}\n")