# Ghat-Guard v5.0

Production-grade, **offline-first municipal safety terminal** for **Kotilingala Ghat (Godavari Pushkaralu 2027)**.

## Core Architecture

- **Edge Nodes (STM32/ESP32):** Multi-modal edge-computing firmware logic parses and emits **51-byte LoRa mesh packets** for resilient local telemetry.
- **Offline First:** Zero cloud dependency for critical operation. Local processing with **append-only cryptographic SHA-256 chained SQLite** audit logging.
- **Vision & Sensor Fusion:** LWIR thermal fusion pipeline bypasses heavy ritual smoke (**Harati Puja haze**) that can blind standard RGB cameras.
- **Emergency Control:** Adrenaline-proof **Palm-Smash** override and **break-before-make actuator interlocks** to prevent unsafe simultaneous actuation.

## Project Structure

```text
ghat-guard-v5/
├── index.html                         # Root redirect to command console
├── README.md
├── audit_logs/
│   └── compliance_register.py         # SHA-256 chained append-only SQLite audit log
├── communications/
│   └── lora_mesh.py                   # 51-byte LoRa packet codec (encode/decode)
├── core_firmware/
│   └── edge_hardware_node.py          # Edge node state machine + LoRa handling
├── emergency_subsystem/
│   └── palm_smash_override.py         # Palm-Smash + break-before-make interlocks
├── physics_engine/
│   ├── granular_flow.py               # Crowd granular flow / phase modeling
│   └── shockwave_propagation.py       # Upstream shockwave propagation
├── ui_frontend/
│   ├── yali_telugu_console.html       # UTF-8 Telugu command console (Tailwind CDN)
│   └── telemetry_worker.js            # Off-main-thread 51-byte telemetry parsing
└── vision_fusion/
    └── puja_haze_fusion.py            # Optical + LWIR fusion (Harati Puja haze)
```

## 51-Byte LoRa Packet Format

Little-endian `<IffBHH34s>` (total **51 bytes**):

| Field | Type | Size |
|---|---:|---:|
| Node ID | `uint32` | 4 |
| Density | `float32` | 4 |
| Velocity | `float32` | 4 |
| Phase | `uint8` | 1 |
| Bad-MAC count | `uint16` | 2 |
| Supercap voltage (scaled ×100) | `uint16` | 2 |
| Security padding | bytes | 34 |

## Run Locally (Chrome)

The UI uses the Tailwind CDN and an ES5-compatible Web Worker. Serve the repository root over HTTP for worker loading:

```bash
# From repository root
python -m http.server 8080
```

Then open:

- `http://localhost:8080/` (redirects automatically), or
- `http://localhost:8080/ui_frontend/yali_telugu_console.html`

## Python Module Verification

```bash
python communications/lora_mesh.py
python core_firmware/edge_hardware_node.py
python vision_fusion/puja_haze_fusion.py
python emergency_subsystem/palm_smash_override.py
python audit_logs/compliance_register.py
```

## Safety Notes

- **Stambhana (స్తంభన)** is treated as a critical crowd-solidification risk condition.
- **Break-before-make** logic must isolate actuator outputs before applying a new state.
- Audit records are **append-only** and hash-chained; verification should be performed during maintenance/offline review.
- This repository provides production-oriented control logic and UI scaffolding; field deployment requires hardware validation, calibration, and municipal safety certification.
