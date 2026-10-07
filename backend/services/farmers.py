from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..eligibility import profile_completeness
from ..models import FarmerCrop, FarmerDocument, FarmerLand, FarmerProfile, User


def ensure_farmer_profile(db: Session, user: User) -> FarmerProfile:
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if profile is None:
        profile = FarmerProfile(user_id=user.id, state="Maharashtra")
        db.add(profile)
        db.flush()
    return profile


def profile_dict(db: Session, user: User) -> dict[str, Any]:
    profile = ensure_farmer_profile(db, user)
    lands = db.scalars(select(FarmerLand).where(FarmerLand.user_id == user.id).order_by(FarmerLand.is_primary.desc(), FarmerLand.created_at)).all()
    crops = db.scalars(select(FarmerCrop).where(FarmerCrop.user_id == user.id).order_by(FarmerCrop.is_current.desc(), FarmerCrop.created_at.desc())).all()
    docs = db.scalars(select(FarmerDocument).where(FarmerDocument.user_id == user.id)).all()
    document_map = {item.document_id: item.state for item in docs}
    for document_id in ("land_7_12", "land_8a", "electricity_bill", "purchase_invoice", "prior_consent", "caste_certificate", "equipment_quote", "self_declaration"):
        document_map.setdefault(document_id, "not_provided")
    primary_land = lands[0] if lands else None
    primary_crop = crops[0] if crops else None
    values = {
        "demo": bool(user.is_demo), "name": user.full_name,
        "state": profile.state, "district": profile.district, "taluka": profile.taluka, "village": profile.village,
        "land_area_acres": primary_land.area_acres if primary_land else None,
        "farmer_category": profile.farmer_category, "social_category": profile.social_category,
        "crop": primary_crop.crop_name if primary_crop else "", "season": primary_crop.season if primary_crop else "",
        "irrigation": profile.irrigation, "support_needs": profile.support_needs or [],
        "aadhaar_present": profile.aadhaar_present,
        "electric_water_pump": profile.electric_water_pump,
        "permanent_electric_connection": profile.permanent_electric_connection,
        "prior_micro_benefit_year": profile.prior_micro_benefit_year,
        "selected_component": profile.selected_component,
        "selected_machinery": profile.selected_machinery,
        "previous_same_machinery_year": profile.previous_same_machinery_year,
        "documents": document_map,
        "land_records": [{"id": item.id, "label": item.label, "area_acres": item.area_acres, "ownership_type": item.ownership_type, "irrigation_available": item.irrigation_available, "is_primary": item.is_primary} for item in lands],
        "crop_records": [{"id": item.id, "crop_name": item.crop_name, "crop_category": item.crop_category, "season": item.season, "area_acres": item.area_acres, "year": item.year, "is_current": item.is_current} for item in crops],
    }
    return values


def serialize_profile(db: Session, user: User) -> dict[str, Any]:
    profile = profile_dict(db, user)
    return {"profile": profile, "completeness": profile_completeness(profile)}


def update_profile(db: Session, user: User, data: dict[str, Any]) -> dict[str, Any]:
    profile = ensure_farmer_profile(db, user)
    if "name" in data and data["name"] is not None:
        user.full_name = data["name"]
    profile_fields = {
        "state", "district", "taluka", "village", "farmer_category", "social_category", "support_needs",
        "aadhaar_present", "irrigation", "electric_water_pump", "permanent_electric_connection",
        "prior_micro_benefit_year", "selected_component", "selected_machinery", "previous_same_machinery_year"
    }
    for key in profile_fields:
        if key in data and data[key] is not None:
            setattr(profile, key, data[key])
    if "land_area_acres" in data:
        primary = db.scalar(select(FarmerLand).where(FarmerLand.user_id == user.id, FarmerLand.is_primary.is_(True)))
        if primary is None:
            primary = db.scalar(select(FarmerLand).where(FarmerLand.user_id == user.id).order_by(FarmerLand.created_at))
        if data["land_area_acres"] is None:
            if primary is not None:
                primary.area_acres = 0
        elif primary is None:
            primary = FarmerLand(user_id=user.id, label="Primary farm", area_acres=data["land_area_acres"], is_primary=True)
            db.add(primary)
        else:
            primary.area_acres = data["land_area_acres"]
            primary.is_primary = True
    if "crop" in data and data["crop"] is not None:
        crop = db.scalar(select(FarmerCrop).where(FarmerCrop.user_id == user.id, FarmerCrop.is_current.is_(True)).order_by(FarmerCrop.created_at.desc()))
        if not data["crop"]:
            if crop is not None:
                crop.is_current = False
        elif crop is None:
            db.add(FarmerCrop(user_id=user.id, crop_name=data["crop"], season=data.get("season") or "", is_current=True))
        else:
            crop.crop_name = data["crop"]
            if "season" in data and data["season"] is not None:
                crop.season = data["season"]
    elif "season" in data and data["season"] is not None:
        crop = db.scalar(select(FarmerCrop).where(FarmerCrop.user_id == user.id, FarmerCrop.is_current.is_(True)).order_by(FarmerCrop.created_at.desc()))
        if crop:
            crop.season = data["season"]
    if "documents" in data and data["documents"] is not None:
        for document_id, state in data["documents"].items():
            item = db.scalar(select(FarmerDocument).where(FarmerDocument.user_id == user.id, FarmerDocument.document_id == document_id))
            if item is None:
                db.add(FarmerDocument(user_id=user.id, document_id=document_id, state=state))
            else:
                item.state = state
    db.commit()
    return serialize_profile(db, user)
