"""
Ghat-Guard v5.0 - Chunk 8: Adrenaline-Proof Emergency Gesture Mechanics
Module: Palm-Smash Overdrive & Pink Lotus Inward-Pull Interlock
Target: Kotilingala Ghat Terminal (Rajahmundry Municipal Corporation)
"""

import time
import hashlib

class PalmSmashOverrideSystem:
    def __init__(self, ghat_zone: str = "Kotilingala_Pen_3"):
        self.ghat_zone = ghat_zone
        self.is_locked_down = False
        self.override_history = []

    def evaluate_palm_smash_hold(self, hold_duration_seconds: float, operator_id: str) -> dict:
        """
        Evaluates the Palm-Smash panic button press.
        Requires a strict hold duration (>= 2.0s) to prevent accidental adrenaline taps,
        while remaining instantaneous enough for critical crowd surges.
        """
        timestamp = time.time()
        
        if hold_duration_seconds >= 2.0:
            self.is_locked_down = True
            action_status = "EMERGENCY_LOCKDOWN_ENGAGED"
            message = "🚨 పామ్-స్మాష్ ఆమోదించబడింది: గేట్లు లాక్ చేయబడ్డాయి (Palm-Smash Confirmed: Gates Locked)"
        elif hold_duration_seconds >= 1.0:
            action_status = "WARNING_THRESHOLD_REACHED"
            message = "⚠️ హెచ్చరిక: మరింత గట్టిగా నొక్కండి (Warning: Hold Firm for Lockdown)"
        else:
            action_status = "IGNORED_SHORT_TAP"
            message = "ℹ️ ట్యాప్ చాలా చిన్నది - యాదృచ్ఛిక స్పర్శ విస్మరించబడింది (Ignored Accidental Tap)"

        # Generate cryptographic audit hash for compliance logs
        record_string = f"{operator_id}_{timestamp}_{action_status}_{self.ghat_zone}"
        audit_hash = hashlib.sha256(record_string.encode('utf-8')).hexdigest()[:16]

        event_log = {
            "timestamp": timestamp,
            "operator_id": operator_id,
            "zone": self.ghat_zone,
            "hold_duration": hold_duration_seconds,
            "status": action_status,
            "audit_hash": audit_hash,
            "message": message
        }

        self.override_history.append(event_log)
        return event_log


# --- Test Execution Verification ---
if __name__ == "__main__":
    system = PalmSmashOverrideSystem(ghat_zone="Kotilingala_Ghat_Pen_3")
    
    print("=== Ghat-Guard v5.0: Adrenaline-Proof Gesture Simulations ===")
    
    # Test 1: Accidental quick tap under adrenaline stress
    res1 = system.evaluate_palm_smash_hold(0.4, operator_id="OP_RAJU_402")
    print(f"Test 1 (Quick Tap): {res1['message']} | Status: {res1['status']}")
    
    # Test 2: Firm 2-second Palm-Smash panic hold
    res2 = system.evaluate_palm_smash_hold(2.1, operator_id="OP_RAJU_402")
    print(f"Test 2 (Palm-Smash): {res2['message']} | Status: {res2['status']}")
    print(f"  -> Cryptographic Audit Hash: {res2['audit_hash']}")
    print(f"  -> Ghat Gate Locked State: {system.is_locked_down}\n")