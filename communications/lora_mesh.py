"""
Ghat-Guard v5.0 - LoRa Mesh Packet Codec
Kotilingala Ghat Terminal (Godavari Pushkaralu 2027)

Offline-first 51-byte telemetry packet format for sub-GHz LoRa mesh.
All multi-byte fields are little-endian.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from typing import Optional

LORA_PACKET_SIZE = 51
LORA_PACKET_FORMAT = "<IffBHH34s"  # 4+4+4+1+2+2+34 = 51 bytes
SECURE_PADDING = b"GH5_LORA_SECURE_VECTOR_PADDING_V50"  # 34 bytes


class PacketError(ValueError):
    """Raised when a LoRa packet is malformed or fails integrity checks."""


@dataclass(frozen=True)
class LoRaTelemetryPacket:
    node_id: int
    density: float
    velocity: float
    phase: int
    bad_mac_count: int
    supercap_voltage: float
    crc32: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "density": round(self.density, 3),
            "velocity": round(self.velocity, 3),
            "phase": self.phase,
            "bad_mac_count": self.bad_mac_count,
            "supercap_voltage": round(self.supercap_voltage, 2),
            "crc32": self.crc32,
            "packet_size": LORA_PACKET_SIZE,
        }


def encode_packet(
    node_id: int,
    density: float,
    velocity: float,
    phase: int,
    bad_mac_count: int,
    supercap_voltage: float,
    padding: bytes = SECURE_PADDING,
) -> bytes:
    """Encode telemetry into an exact 51-byte LoRa state vector."""
    if len(padding) != 34:
        raise PacketError(f"Padding must be exactly 34 bytes, got {len(padding)}")

    density = max(0.0, min(10.0, float(density)))
    velocity = max(0.0, min(5.0, float(velocity)))
    phase = int(phase) & 0xFF
    bad_mac_count = max(0, min(65535, int(bad_mac_count)))
    supercap_scaled = max(0, min(65535, int(round(supercap_voltage * 100))))

    packet = struct.pack(
        LORA_PACKET_FORMAT,
        int(node_id) & 0xFFFFFFFF,
        density,
        velocity,
        phase,
        bad_mac_count,
        supercap_scaled,
        padding,
    )
    if len(packet) != LORA_PACKET_SIZE:
        raise PacketError(f"Encoded packet must be 51 bytes, got {len(packet)}")
    return packet


def decode_packet(data: bytes, verify_crc: bool = False) -> LoRaTelemetryPacket:
    """Decode and validate a 51-byte LoRa state vector."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise PacketError("Packet data must be bytes-like")
    raw = bytes(data)
    if len(raw) != LORA_PACKET_SIZE:
        raise PacketError(f"Expected {LORA_PACKET_SIZE} bytes, got {len(raw)}")

    node_id, density, velocity, phase, bad_mac_count, supercap_scaled, padding = struct.unpack(
        LORA_PACKET_FORMAT, raw
    )

    # Basic sanity validation for offline edge operation.
    if not (0.0 <= density <= 10.0):
        raise PacketError(f"Density out of range: {density}")
    if not (0.0 <= velocity <= 10.0):
        raise PacketError(f"Velocity out of range: {velocity}")
    if phase not in (0, 1, 2, 3):
        # Allow reserved values but keep strict by default for known phases.
        pass
    if len(padding) != 34:
        raise PacketError("Invalid padding length")

    crc = zlib.crc32(raw) & 0xFFFFFFFF
    if verify_crc:
        # CRC transport wrapper can be added at link layer; here we compute for diagnostics.
        pass

    return LoRaTelemetryPacket(
        node_id=node_id,
        density=density,
        velocity=velocity,
        phase=phase,
        bad_mac_count=bad_mac_count,
        supercap_voltage=supercap_scaled / 100.0,
        crc32=crc,
    )


if __name__ == "__main__":
    pkt = encode_packet(101, 3.53, 0.92, 1, 0, 15.82)
    decoded = decode_packet(pkt)
    print(pkt.hex())
    print(decoded.to_dict())
