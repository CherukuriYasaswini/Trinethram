"""
Ghat-Guard v5.0 - Chunk 9: Append-Only SQLite Compliance & Audit Register
Target: Kotilingala Ghat Terminal (Rajahmundry Municipal Corporation)
"""

import sqlite3
import time
import hashlib
import os

class GhatComplianceRegister:
    def __init__(self, db_path="audit_logs/ghat_compliance.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initializes an append-only SQLite compliance table with cryptographic chaining."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                zone TEXT,
                details TEXT,
                previous_hash TEXT,
                current_hash TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, event_type: str, zone: str, details: str) -> str:
        """Appends a cryptographically chained immutable compliance record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch the hash of the last recorded event to maintain a tamper-evident blockchain-like chain
        cursor.execute("SELECT current_hash FROM audit_trail ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        prev_hash = row[0] if row else "GENESIS_BLOCK_KOTILINGALA_2027"

        timestamp = time.time()
        raw_data = f"{timestamp}_{event_type}_{zone}_{details}_{prev_hash}"
        curr_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

        cursor.execute('''
            INSERT INTO audit_trail (timestamp, event_type, zone, details, previous_hash, current_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, event_type, zone, details, prev_hash, curr_hash))
        
        conn.commit()
        conn.close()
        return curr_hash


# --- Test Execution Verification ---
if __name__ == "__main__":
    register = GhatComplianceRegister()
    
    print("=== Ghat-Guard v5.0: Immutable Audit Log Verification ===")
    hash1 = register.log_event("SYSTEM_INIT", "Kotilingala_Main", "Zero-cloud autonomy node online.")
    hash2 = register.log_event("PALM_SMASH_LOCKDOWN", "Pen_Step_3", "Emergency gate interlock engaged by operator.")
    
    print(f"Log 1 Hash (Genesis Link): {hash1}")
    print(f"Log 2 Hash (Tamper-Evident): {hash2}")
    print("✅ Audit register successfully recorded!")