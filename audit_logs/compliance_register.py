"""
Ghat-Guard v5.0 - Append-Only Cryptographic Compliance & Audit Register
Kotilingala Ghat Terminal (Godavari Pushkaralu 2027)

Offline-first SQLite audit logging with SHA-256 hash chaining.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from typing import Any, Optional


class GhatComplianceRegister:
    def __init__(self, db_path: str = "audit_logs/ghat_compliance.db"):
        base_dir = os.path.dirname(db_path)
        if base_dir:
            os.makedirs(base_dir, exist_ok=True)
        self.db_path = db_path
        self._init_database()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_database(self) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    details TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL UNIQUE
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_trail_ts ON audit_trail(timestamp)"
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _canonical_details(details: Any) -> str:
        if isinstance(details, str):
            return details
        return json.dumps(details, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _get_last_hash(self, cursor: sqlite3.Cursor) -> str:
        cursor.execute("SELECT current_hash FROM audit_trail ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else "GENESIS_BLOCK_KOTILINGALA_2027"

    def log_event(self, event_type: str, zone: str, details: Any) -> str:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            prev_hash = self._get_last_hash(cursor)
            timestamp = time.time()
            details_text = self._canonical_details(details)
            raw_data = f"{timestamp:.6f}|{event_type}|{zone}|{details_text}|{prev_hash}"
            curr_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()
            cursor.execute(
                """
                INSERT INTO audit_trail (timestamp, event_type, zone, details, previous_hash, current_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, event_type, zone, details_text, prev_hash, curr_hash),
            )
            conn.commit()
            return curr_hash
        finally:
            conn.close()

    def verify_chain(self) -> dict:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, event_type, zone, details, previous_hash, current_hash FROM audit_trail ORDER BY id ASC"
            )
            rows = cursor.fetchall()
            prev = "GENESIS_BLOCK_KOTILINGALA_2027"
            for (row_id, ts, event_type, zone, details, previous_hash, current_hash) in rows:
                expected_prev = prev
                raw_data = f"{float(ts):.6f}|{event_type}|{zone}|{details}|{previous_hash}"
                expected_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()
                if previous_hash != expected_prev or current_hash != expected_hash:
                    return {"ok": False, "failed_id": row_id, "count": len(rows)}
                prev = current_hash
            return {"ok": True, "count": len(rows)}
        finally:
            conn.close()


if __name__ == "__main__":
    register = GhatComplianceRegister()
    h1 = register.log_event("SYSTEM_INIT", "Kotilingala_Main", {"status": "online", "mode": "offline-first"})
    h2 = register.log_event("PALM_SMASH_LOCKDOWN", "Pen_Step_3", {"operator": "OP_RAJU_402"})
    print(h1)
    print(h2)
    print(register.verify_chain())
