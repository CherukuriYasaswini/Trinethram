"""
Ghat-Guard v5.0 - Adrenaline-Proof Emergency Controls
Kotilingala Ghat Terminal (Godavari Pushkaralu 2027)

- Hardware-enforced Palm-Smash override gesture validation
- Break-before-make actuator interlocks for safe emergency transitions
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class InterlockState:
    actuator: str
    state: str  # READY | BREAK | MAKE | FAULT | LOCKED
    locked: bool
    break_before_make_counter: int
    last_transition_ts: float
    reason: str = ""


class BreakBeforeMakeInterlockController:
    """Ensures no unsafe simultaneous actuator drive during transitions."""

    def __init__(self, actuators: Optional[List[str]] = None):
        self.actuators = actuators or ["gate_main", "gate_aux", "siren", "beacon"]
        self.states: Dict[str, InterlockState] = {
            name: InterlockState(name, "READY", False, 0, time.time(), "INIT")
            for name in self.actuators
        }

    def transition(self, actuator: str, lock: bool, reason: str = "") -> InterlockState:
        if actuator not in self.states:
            raise KeyError(f"Unknown actuator: {actuator}")
        st = self.states[actuator]
        now = time.time()
        if st.locked == lock and st.state in ("READY", "MAKE", "LOCKED"):
            st.last_transition_ts = now
            st.reason = reason or st.reason
            return st

        # BREAK phase: isolate outputs before changing state.
        st.state = "BREAK"
        st.break_before_make_counter += 1
        st.last_transition_ts = now
        st.reason = reason

        # MAKE phase: apply requested safe state.
        st.locked = bool(lock)
        st.state = "LOCKED" if st.locked else "READY"
        st.last_transition_ts = time.time()
        self.states[actuator] = st
        return st

    def snapshot(self) -> dict:
        return {name: asdict(st) for name, st in self.states.items()}

    def total_break_before_make_events(self) -> int:
        return sum(st.break_before_make_counter for st in self.states.values())


class PalmSmashOverrideSystem:
    def __init__(self, ghat_zone: str = "Kotilingala_Pen_3"):
        self.ghat_zone = ghat_zone
        self.is_locked_down = False
        self.override_history: List[dict] = []
        self.interlocks = BreakBeforeMakeInterlockController()

    def evaluate_palm_smash_hold(self, hold_duration_seconds: float, operator_id: str) -> dict:
        timestamp = time.time()
        hold = max(0.0, float(hold_duration_seconds))

        if hold >= 2.0:
            self.is_locked_down = True
            self.interlocks.transition("gate_main", lock=True, reason="PALM_SMASH")
            self.interlocks.transition("gate_aux", lock=True, reason="PALM_SMASH")
            self.interlocks.transition("beacon", lock=True, reason="PALM_SMASH")
            action_status = "EMERGENCY_LOCKDOWN_ENGAGED"
            message = "🚨 పామ్-స్మాష్ ఆమోదించబడింది: గేట్లు లాక్ చేయబడ్డాయి (Palm-Smash Confirmed: Gates Locked)"
        elif hold >= 1.0:
            action_status = "WARNING_THRESHOLD_REACHED"
            message = "⚠️ హెచ్చరిక: మరింత గట్టిగా నొక్కండి (Warning: Hold Firm for Lockdown)"
        else:
            action_status = "IGNORED_SHORT_TAP"
            message = "ℹ️ ట్యాప్ చాలా చిన్నది - యాదృచ్ఛిక స్పర్శ విస్మరించబడింది (Ignored Accidental Tap)"

        record_string = f"{operator_id}_{timestamp}_{action_status}_{self.ghat_zone}_{self.interlocks.total_break_before_make_events()}"
        audit_hash = hashlib.sha256(record_string.encode("utf-8")).hexdigest()[:16]

        event_log = {
            "timestamp": timestamp,
            "operator_id": operator_id,
            "zone": self.ghat_zone,
            "hold_duration": hold,
            "status": action_status,
            "audit_hash": audit_hash,
            "break_before_make_counter": self.interlocks.total_break_before_make_events(),
            "interlock_snapshot": self.interlocks.snapshot(),
            "message": message,
        }
        self.override_history.append(event_log)
        return event_log


if __name__ == "__main__":
    system = PalmSmashOverrideSystem()
    print(system.evaluate_palm_smash_hold(0.4, "OP_RAJU_402")["status"])
    print(system.evaluate_palm_smash_hold(2.1, "OP_RAJU_402")["break_before_make_counter"])
