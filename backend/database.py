"""Deprecated MVP database helper retained only for regression-test fixtures.

The application now uses SQLAlchemy models in ``backend.db``; do not use this
legacy SQLite store for runtime data.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "scheme_mitra_demo.sqlite3"
SCHEMES_PATH = Path(__file__).resolve().parent / "data" / "schemes.json"

DEFAULT_PROFILE: dict[str, Any] = {
    "demo": True,
    "name": "Demo Farmer",
    "state": "Maharashtra",
    "district": "Nashik",
    "taluka": "Niphad",
    "village": "",
    "land_area_acres": 2.5,
    "farmer_category": "small",
    "social_category": "not_provided",
    "crop": "onion",
    "season": "Rabi",
    "irrigation": "yes",
    "support_needs": ["irrigation"],
    "aadhaar_present": True,
    "permanent_electric_connection": "unknown",
    "electric_water_pump": "unknown",
    "prior_micro_benefit_year": "unknown",
    "selected_component": "",
    "selected_machinery": "",
    "previous_same_machinery_year": "unknown",
    "documents": {
        "land_7_12": "available",
        "land_8a": "available",
        "electricity_bill": "not_provided",
        "purchase_invoice": "not_yet_required",
        "prior_consent": "not_yet_issued",
        "caste_certificate": "not_provided",
        "equipment_quote": "not_provided",
        "self_declaration": "not_provided"
    }
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db


def initialize(reset: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(DB_PATH) + suffix)
            if sidecar.exists():
                sidecar.unlink()
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS schemes (
                slug TEXT PRIMARY KEY,
                data_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS saved_schemes (
                scheme_slug TEXT PRIMARY KEY,
                saved_at TEXT NOT NULL,
                FOREIGN KEY (scheme_slug) REFERENCES schemes(slug)
            );
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_slug TEXT NOT NULL,
                reference TEXT NOT NULL DEFAULT '',
                applied_on TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                entered_by TEXT NOT NULL DEFAULT 'DEMO_USER',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (scheme_slug) REFERENCES schemes(slug)
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_slug TEXT NOT NULL,
                useful INTEGER NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (scheme_slug) REFERENCES schemes(slug)
            );
            CREATE TABLE IF NOT EXISTS recommendation_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                useful INTEGER NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pilot_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase TEXT NOT NULL CHECK (phase IN ('baseline','post_use')),
                time_minutes REAL,
                knows_relevant_schemes INTEGER,
                understands_documents INTEGER,
                knows_next_step INTEGER,
                comment TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)
        state = db.execute("SELECT value_json FROM app_state WHERE key='farmer_profile'").fetchone()
        if state is None:
            db.execute(
                "INSERT INTO app_state(key, value_json, updated_at) VALUES(?,?,?)",
                ("farmer_profile", json.dumps(DEFAULT_PROFILE), now_iso()),
            )
        records = json.loads(SCHEMES_PATH.read_text(encoding="utf-8"))
        for record in records:
            db.execute(
                "INSERT INTO schemes(slug, data_json, updated_at) VALUES(?,?,?) "
                "ON CONFLICT(slug) DO UPDATE SET data_json=excluded.data_json, updated_at=excluded.updated_at",
                (record["slug"], json.dumps(record, ensure_ascii=False), now_iso()),
            )
        db.commit()


def get_profile(db: sqlite3.Connection | None = None) -> dict[str, Any]:
    own = db is None
    db = db or connect()
    try:
        row = db.execute("SELECT value_json FROM app_state WHERE key='farmer_profile'").fetchone()
        if not row:
            return dict(DEFAULT_PROFILE)
        return json.loads(row["value_json"])
    finally:
        if own:
            db.close()


def save_profile(profile: dict[str, Any], db: sqlite3.Connection | None = None) -> dict[str, Any]:
    own = db is None
    db = db or connect()
    try:
        db.execute(
            "INSERT INTO app_state(key, value_json, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at",
            ("farmer_profile", json.dumps(profile, ensure_ascii=False), now_iso()),
        )
        db.commit()
        return profile
    finally:
        if own:
            db.close()


def list_schemes(db: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    own = db is None
    db = db or connect()
    try:
        rows = db.execute("SELECT data_json FROM schemes ORDER BY slug").fetchall()
        return [json.loads(row["data_json"]) for row in rows]
    finally:
        if own:
            db.close()


def get_scheme(slug: str, db: sqlite3.Connection | None = None) -> dict[str, Any] | None:
    own = db is None
    db = db or connect()
    try:
        row = db.execute("SELECT data_json FROM schemes WHERE slug=?", (slug,)).fetchone()
        return json.loads(row["data_json"]) if row else None
    finally:
        if own:
            db.close()


def record_event(name: str, metadata: dict[str, Any] | None = None, db: sqlite3.Connection | None = None) -> None:
    own = db is None
    db = db or connect()
    try:
        db.execute(
            "INSERT INTO analytics_events(event_name, metadata_json, created_at) VALUES(?,?,?)",
            (name, json.dumps(metadata or {}, ensure_ascii=False), now_iso()),
        )
        db.commit()
    finally:
        if own:
            db.close()


def list_saved(db: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    own = db is None
    db = db or connect()
    try:
        rows = db.execute(
            "SELECT s.data_json, v.saved_at FROM saved_schemes v "
            "JOIN schemes s ON s.slug=v.scheme_slug ORDER BY v.saved_at DESC"
        ).fetchall()
        return [{**json.loads(row["data_json"]), "saved_at": row["saved_at"]} for row in rows]
    finally:
        if own:
            db.close()


def set_saved(slug: str, saved: bool, db: sqlite3.Connection | None = None) -> bool:
    own = db is None
    db = db or connect()
    try:
        if saved:
            db.execute(
                "INSERT OR IGNORE INTO saved_schemes(scheme_slug, saved_at) VALUES(?,?)",
                (slug, now_iso()),
            )
        else:
            db.execute("DELETE FROM saved_schemes WHERE scheme_slug=?", (slug,))
        db.commit()
        return saved
    finally:
        if own:
            db.close()


def list_applications(db: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    own = db is None
    db = db or connect()
    try:
        rows = db.execute(
            "SELECT a.*, s.data_json FROM applications a JOIN schemes s ON s.slug=a.scheme_slug "
            "ORDER BY a.updated_at DESC, a.id DESC"
        ).fetchall()
        result = []
        for row in rows:
            scheme = json.loads(row["data_json"])
            result.append({
                "id": row["id"], "scheme_slug": row["scheme_slug"], "scheme_name": scheme["name"],
                "reference": row["reference"], "applied_on": row["applied_on"], "status": row["status"],
                "notes": row["notes"], "entered_by": row["entered_by"],
                "created_at": row["created_at"], "updated_at": row["updated_at"]
            })
        return result
    finally:
        if own:
            db.close()


def create_application(data: dict[str, Any], db: sqlite3.Connection | None = None) -> dict[str, Any]:
    own = db is None
    db = db or connect()
    try:
        timestamp = now_iso()
        cursor = db.execute(
            "INSERT INTO applications(scheme_slug, reference, applied_on, status, notes, created_at, updated_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (data["scheme_slug"], data.get("reference", ""), data.get("applied_on", ""),
             data["status"], data.get("notes", ""), timestamp, timestamp),
        )
        db.commit()
        app_id = cursor.lastrowid
        row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        scheme = get_scheme(data["scheme_slug"], db)
        return {
            "id": row["id"], "scheme_slug": row["scheme_slug"], "scheme_name": scheme["name"],
            "reference": row["reference"], "applied_on": row["applied_on"], "status": row["status"],
            "notes": row["notes"], "entered_by": row["entered_by"],
            "created_at": row["created_at"], "updated_at": row["updated_at"]
        }
    finally:
        if own:
            db.close()


def update_application(app_id: int, data: dict[str, Any], db: sqlite3.Connection | None = None) -> dict[str, Any] | None:
    own = db is None
    db = db or connect()
    try:
        allowed = {k: data[k] for k in ("status", "reference", "applied_on", "notes") if k in data}
        if not allowed:
            return None
        allowed["updated_at"] = now_iso()
        fields = ", ".join(f"{key}=?" for key in allowed)
        values = list(allowed.values()) + [app_id]
        db.execute(f"UPDATE applications SET {fields} WHERE id=?", values)
        db.commit()
        row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        if not row:
            return None
        scheme = get_scheme(row["scheme_slug"], db)
        return {
            "id": row["id"], "scheme_slug": row["scheme_slug"], "scheme_name": scheme["name"],
            "reference": row["reference"], "applied_on": row["applied_on"], "status": row["status"],
            "notes": row["notes"], "entered_by": row["entered_by"],
            "created_at": row["created_at"], "updated_at": row["updated_at"]
        }
    finally:
        if own:
            db.close()


def save_feedback(slug: str, useful: bool, reason: str = "", db: sqlite3.Connection | None = None) -> None:
    own = db is None
    db = db or connect()
    try:
        db.execute(
            "INSERT INTO feedback(scheme_slug,useful,reason,created_at) VALUES(?,?,?,?)",
            (slug, 1 if useful else 0, reason, now_iso()),
        )
        db.commit()
    finally:
        if own:
            db.close()


def save_recommendation_feedback(useful: bool, reason: str = "", db: sqlite3.Connection | None = None) -> None:
    own = db is None
    db = db or connect()
    try:
        db.execute(
            "INSERT INTO recommendation_feedback(useful,reason,created_at) VALUES(?,?,?)",
            (1 if useful else 0, reason, now_iso()),
        )
        db.commit()
    finally:
        if own:
            db.close()


def save_survey(data: dict[str, Any], db: sqlite3.Connection | None = None) -> None:
    own = db is None
    db = db or connect()
    try:
        def tri(v: Any) -> int | None:
            if v is True:
                return 1
            if v is False:
                return 0
            return None
        db.execute(
            "INSERT INTO pilot_surveys(phase,time_minutes,knows_relevant_schemes,understands_documents,knows_next_step,comment,created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (data["phase"], data.get("time_minutes"), tri(data.get("knows_relevant_schemes")),
             tri(data.get("understands_documents")), tri(data.get("knows_next_step")),
             data.get("comment", ""), now_iso()),
        )
        db.commit()
    finally:
        if own:
            db.close()


def pilot_metrics(db: sqlite3.Connection | None = None) -> dict[str, Any]:
    own = db is None
    db = db or connect()
    try:
        event_rows = db.execute(
            "SELECT event_name, COUNT(*) AS n FROM analytics_events GROUP BY event_name"
        ).fetchall()
        events = {row["event_name"]: row["n"] for row in event_rows}
        survey_rows = db.execute("SELECT phase, COUNT(*) AS n, AVG(time_minutes) AS avg_time FROM pilot_surveys GROUP BY phase").fetchall()
        surveys = {row["phase"]: {"count": row["n"], "average_time_minutes": round(row["avg_time"], 1) if row["avg_time"] is not None else None} for row in survey_rows}
        feedback = db.execute(
            "SELECT COALESCE(SUM(total),0) AS total, COALESCE(SUM(useful),0) AS useful FROM ("
            "SELECT COUNT(*) AS total, SUM(useful) AS useful FROM feedback UNION ALL "
            "SELECT COUNT(*) AS total, SUM(useful) AS useful FROM recommendation_feedback)"
        ).fetchone()
        return {
            "events": events,
            "baseline_surveys": surveys.get("baseline", {"count": 0, "average_time_minutes": None}),
            "post_use_surveys": surveys.get("post_use", {"count": 0, "average_time_minutes": None}),
            "feedback": {"total": feedback["total"] or 0, "useful": feedback["useful"] or 0},
            "disclaimer": "Local demo event counts only. This is not pilot evidence or an impact claim."
        }
    finally:
        if own:
            db.close()


def reset_demo() -> None:
    initialize(reset=True)
