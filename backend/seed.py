"""Idempotent source-catalog seed and explicitly configured admin bootstrap."""
from __future__ import annotations

import json
import secrets
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import ADMIN_EMAIL, ADMIN_PASSWORD, DEMO_MODE, SEED_SCHEMES
from .db import Base, engine
from .models import FarmerCrop, FarmerDocument, FarmerLand, FarmerProfile, Scheme, User
from .security import hash_password

DATA_FILE = Path(__file__).resolve().parent / "data" / "schemes.json"


def seed_initial_data(db: Session) -> None:
    if SEED_SCHEMES:
        records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        for raw in records:
            existing = db.scalar(select(Scheme).where(Scheme.slug == raw["slug"]))
            if existing:
                continue
            scheme = Scheme(
                slug=raw["slug"], name=raw["name"], department=raw["department"],
                category=raw.get("category", "General"), level=raw.get("level", "State"),
                status="UNDER_REVIEW", verification_status="NEEDS_REVIEW",
                source_url=raw["source_url"], application_url=raw.get("application_url", ""),
                source_name=raw["source_name"], data_json=raw,
            )
            db.add(scheme)

    if DEMO_MODE:
        demo = db.scalar(select(User).where(User.email == "demo@schememitra.app"))
        if demo is None:
            demo = User(
                email="demo@schememitra.app", full_name="Demo Farmer",
                password_hash=hash_password(secrets.token_urlsafe(48)), role="FARMER",
                is_active=True, is_demo=True,
            )
            db.add(demo)
            db.flush()
            db.add(FarmerProfile(
                user_id=demo.id, state="Maharashtra", district="Nashik", taluka="Niphad", village="",
                farmer_category="small", social_category="not_provided", support_needs=["irrigation"],
                aadhaar_present=True, irrigation="yes", electric_water_pump="unknown",
                permanent_electric_connection="unknown", prior_micro_benefit_year="unknown",
            ))
            db.add(FarmerLand(user_id=demo.id, label="Demo farm", area_acres=2.5, ownership_type="owned", irrigation_available="yes", is_primary=True))
            db.add(FarmerCrop(user_id=demo.id, crop_name="onion", crop_category="vegetable", season="Rabi", area_acres=2.5, is_current=True))
            demo_docs = {
                "land_7_12":"available", "land_8a":"available", "electricity_bill":"not_provided",
                "purchase_invoice":"not_yet_required", "prior_consent":"not_yet_issued",
                "caste_certificate":"not_provided", "equipment_quote":"not_provided", "self_declaration":"not_provided"
            }
            for document_id, state in demo_docs.items():
                db.add(FarmerDocument(user_id=demo.id, document_id=document_id, state=state))

    if ADMIN_EMAIL and ADMIN_PASSWORD:
        if len(ADMIN_PASSWORD) < 16:
            raise RuntimeError("ADMIN_PASSWORD must be at least 16 characters for bootstrap.")
        admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if admin is None:
            db.add(User(email=ADMIN_EMAIL, full_name="Scheme Mitra Admin", password_hash=hash_password(ADMIN_PASSWORD), role="SUPER_ADMIN", is_active=True))
        else:
            admin.role = "SUPER_ADMIN"
            admin.is_active = True

    db.commit()


def initialize_development_database() -> None:
    Base.metadata.create_all(bind=engine)
    from .db import SessionLocal
    with SessionLocal() as db:
        seed_initial_data(db)
