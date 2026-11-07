"""
Ghat-Guard v5.0 - Chunk 1 & 2: Edge Hardware Node & 51-Byte LoRa Telemetry
Target: STM32 + ESP32 Dual-Core Subsystem (Kotilingala Ghat Terminal)
"""

import time
import struct
from enum import IntEnum

class SystemMode(IntEnum):
    NORMAL = 0
    DEGRADED = 1
    EMERGENCY = 2
    MAINTENANCE = 3

class CrowdPhase(IntEnum):
    GAS = 0        # Free flow (< 1.5 p/m²)
    LIQUID = 1     # Laminar movement (1.5 - 3.5 p/m²)
    SOLID = 2      # Stambhana / Critical collapse (≥ 4.0 p/m²)

class EdgeHardwareNode:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.mode = SystemMode.NORMAL
        self.bad_mac_counter = 0
        self.supercap_voltage = 15.8  # Target 15.8V supercap holdover
        self.last_valid_heartbeat = time.time()
        self.gate_locked = False

    def poll_sensors(self, raw_density: float, raw_velocity: float, current_voltage: float) -> dict:
        """Validates optical sensors, tracks supercap voltage, and drives the state machine."""
        # 1. Update Power & Voltage State
        self.supercap_voltage = max(0.0, min(20.0, current_voltage))
        
        # 2. Input Validation (Clipping values to realistic bounds)
        density = max(0.0, min(10.0, raw_density))
        velocity = max(0.0, min(5.0, raw_velocity))

        # 3. Granular Phase Classification
        if density >= 4.0 or velocity < 0.25:
            phase = CrowdPhase.SOLID
        elif density >= 1.5:
            phase = CrowdPhase.LIQUID
        else:
            phase = CrowdPhase.GAS

        # 4. State Machine & Safety Rail Evaluation
        self._evaluate_state_machine(phase, density)

        return {
            "node_id": self.node_id,
            "density": density,
            "velocity": velocity,
            "phase": phase.name,
            "mode": self.mode.name,
            "supercap_v": self.supercap_voltage,
            "bad_mac_count": self.bad_mac_counter,
            "gate_locked": self.gate_locked
        }

    def _evaluate_state_machine(self, phase: CrowdPhase, density: float):
        """Applies power fallback rules and autonomous gate interlocks."""
        packet_age = time.time() - self.last_valid_heartbeat

        # Fallback to DEGRADED if supercap voltage drops below 14.5V or network lags
        if self.supercap_voltage < 14.5 or packet_age > 1.5:
            if self.mode != SystemMode.EMERGENCY:
                self.mode = SystemMode.DEGRADED

        # Trigger EMERGENCY (Stambhana collapse) & Lock Pneumatic Gate
        if phase == CrowdPhase.SOLID or density >= 4.0:
            self.mode = SystemMode.EMERGENCY
            self.gate_locked = True
        elif self.mode == SystemMode.EMERGENCY and density < 2.5:
            # Hysteresis recovery condition
            self.mode = SystemMode.NORMAL
            self.gate_locked = False

    def record_rf_anomaly(self):
        """Increments Bad-MAC counter upon detecting corrupt or spoofed radio packets."""
        self.bad_mac_counter += 1

    def pack_51byte_lora_vector(self, density: float, velocity: float, phase: CrowdPhase) -> bytes:
        """
        Packs telemetry into an exact 51-byte binary state vector for LoRa sub-GHz fallback.
        Structure:
          - Node ID: 4 bytes (uint32)
          - Density: 4 bytes (float32)
          - Velocity: 4 bytes (float32)
          - Phase State: 1 byte (uint8)
          - Bad-MAC Counter: 2 bytes (uint16)
          - Supercap Voltage: 2 bytes (uint16, scaled x100)
          - Security Padding: 34 bytes
        Total: 4 + 4 + 4 + 1 + 2 + 2 + 34 = 51 Bytes.
        """
        fmt = "<IffBHH34s"
        scaled_supercap = int(self.supercap_voltage * 100)
        padding = b"GH_5_LORA_SECURE_VECTOR_PADDING\x00\x00"  # Exactly 34 bytes

        packet = struct.pack(
            fmt,
            self.node_id,
            density,
            velocity,
            int(phase),
            self.bad_mac_counter,
            scaled_supercap,
            padding
        )
        assert len(packet) == 51, f"Packet size error: {len(packet)} bytes instead of 51."
        return packet


# --- Test Execution Verification ---
if __name__ == "__main__":
    node = EdgeHardwareNode(node_id=101)
    
    print("=== Test 1: Normal Flow State ===")
    res1 = node.poll_sensors(raw_density=1.1, raw_velocity=1.4, current_voltage=15.8)
    print(res1)
    
    print("\n=== Test 2: Crowd Surge & Low Voltage Degraded Mode ===")
    res2 = node.poll_sensors(raw_density=4.2, raw_velocity=0.1, current_voltage=14.1)
    print(res2)
    
    # Generate 51-Byte LoRa Packet
    packet_bytes = node.pack_51byte_lora_vector(4.2, 0.1, CrowdPhase.SOLID)
    print(f"\nGenerated 51-Byte LoRa Packet (Hex): {packet_bytes.hex()}")
    print(f"Verified Packet Length: {len(packet_bytes)} Bytes")