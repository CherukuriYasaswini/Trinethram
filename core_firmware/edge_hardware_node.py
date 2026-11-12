"""
Ghat-Guard v5.0 - Edge Hardware Node
Kotilingala Ghat Terminal (Godavari Pushkaralu 2027)

STM32/ESP32-oriented edge-computing firmware model:
- Parses/produces 51-byte LoRa mesh packets
- Runs local state machine (offline-first, zero cloud dependency)
- Enforces gate/interlock decisions and telemetry health checks
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

try:
    from communications.lora_mesh import decode_packet, encode_packet
except Exception:  # pragma: no cover - supports direct execution from repo root
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from communications.lora_mesh import decode_packet, encode_packet


class SystemMode(IntEnum):
    NORMAL = 0
    DEGRADED = 1
    EMERGENCY = 2
    MAINTENANCE = 3


class CrowdPhase(IntEnum):
    GAS = 0      # < 1.5 p/m²
    LIQUID = 1   # 1.5 - < 4.0 p/m²
    SOLID = 2    # >= 4.0 p/m² or collapse velocity (Stambhana)


@dataclass
class SensorFrame:
    density: float
    velocity: float
    supercap_voltage: float
    timestamp: float


class EdgeHardwareNode:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.mode = SystemMode.NORMAL
        self.bad_mac_counter = 0
        self.break_before_make_counter = 0
        self.supercap_voltage = 15.8
        self.last_valid_heartbeat = time.time()
        self.gate_locked = False
        self.interlock_state = "READY"  # READY | BREAK | MAKE | FAULT

    @staticmethod
    def classify_phase(density: float, velocity: float) -> CrowdPhase:
        if density >= 4.0 or velocity < 0.25:
            return CrowdPhase.SOLID
        if density >= 1.5:
            return CrowdPhase.LIQUID
        return CrowdPhase.GAS

    def poll_sensors(self, raw_density: float, raw_velocity: float, current_voltage: float) -> dict:
        frame = SensorFrame(
            density=max(0.0, min(10.0, float(raw_density))),
            velocity=max(0.0, min(5.0, float(raw_velocity))),
            supercap_voltage=max(0.0, min(20.0, float(current_voltage))),
            timestamp=time.time(),
        )
        self.supercap_voltage = frame.supercap_voltage
        self.last_valid_heartbeat = frame.timestamp
        phase = self.classify_phase(frame.density, frame.velocity)
        self._evaluate_state_machine(phase, frame.density)

        return {
            "node_id": self.node_id,
            "density": round(frame.density, 3),
            "velocity": round(frame.velocity, 3),
            "phase": phase.name,
            "phase_code": int(phase),
            "mode": self.mode.name,
            "supercap_v": round(self.supercap_voltage, 2),
            "bad_mac_count": self.bad_mac_counter,
            "break_before_make_counter": self.break_before_make_counter,
            "gate_locked": self.gate_locked,
            "interlock_state": self.interlock_state,
        }

    def _evaluate_state_machine(self, phase: CrowdPhase, density: float) -> None:
        packet_age = time.time() - self.last_valid_heartbeat
        if self.supercap_voltage < 14.5 or packet_age > 1.5:
            if self.mode != SystemMode.EMERGENCY:
                self.mode = SystemMode.DEGRADED

        if phase == CrowdPhase.SOLID or density >= 4.0:
            self._set_gate_lock(True, reason="STAMBHANA")
            self.mode = SystemMode.EMERGENCY
        elif self.mode == SystemMode.EMERGENCY and density < 2.5:
            self._set_gate_lock(False, reason="RECOVERY")
            self.mode = SystemMode.NORMAL
        elif self.mode != SystemMode.EMERGENCY and self.supercap_voltage >= 14.5:
            self.mode = SystemMode.NORMAL

    def _set_gate_lock(self, locked: bool, reason: str = "") -> None:
        """Apply break-before-make transition before changing actuator state."""
        desired = bool(locked)
        if desired == self.gate_locked and self.interlock_state in ("READY", "MAKE"):
            return
        # BREAK: isolate current actuator drive
        self.interlock_state = "BREAK"
        self.break_before_make_counter += 1
        # MAKE: apply new state only after break
        self.gate_locked = desired
        self.interlock_state = "MAKE" if desired else "READY"

    def record_rf_anomaly(self) -> None:
        self.bad_mac_counter = min(65535, self.bad_mac_counter + 1)

    def parse_lora_packet(self, packet: bytes) -> Optional[dict]:
        """Parse a 51-byte LoRa packet from the mesh and update RF health counters."""
        try:
            decoded = decode_packet(packet)
            self.last_valid_heartbeat = time.time()
            return decoded.to_dict()
        except Exception:
            self.record_rf_anomaly()
            return None

    def pack_lora_vector(self, density: float, velocity: float, phase: CrowdPhase) -> bytes:
        return encode_packet(
            node_id=self.node_id,
            density=density,
            velocity=velocity,
            phase=int(phase),
            bad_mac_count=self.bad_mac_counter,
            supercap_voltage=self.supercap_voltage,
        )


if __name__ == "__main__":
    node = EdgeHardwareNode(node_id=101)
    print(node.poll_sensors(raw_density=3.53, raw_velocity=0.92, current_voltage=15.8))
    packet = node.pack_lora_vector(3.53, 0.92, CrowdPhase.LIQUID)
    print(len(packet), packet.hex())
    print(node.parse_lora_packet(packet))
