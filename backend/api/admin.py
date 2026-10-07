from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import roles_required
from ..models import AnalyticsEvent, AuditLog, Feedback, FarmerProfile, Pilot, PilotSurvey, RecommendationSnapshot, Scheme, SchemeVersion, User
from ..schemas import SchemeInput
from ..services.recommendations import scheme_payload
from .common import validate_official_url, write_audit

router = APIRouter(prefix="/api/v1/admin", tags=["administration"])
admin_user = roles_required("ADMIN", "DATA_VERIFIER", "SUPER_ADMIN")
verifier_user = roles_required("DATA_VERIFIER", "ADMIN", "SUPER_ADMIN")
publisher_user = roles_required("ADMIN", "SUPER_ADMIN")


class ActionNote(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reason: str = Field(min_length=4, max_length=500)


class PilotInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=3, max_length=160)
    location: str = Field(min_length=2, max_length=160)
    target_users: int = Field(default=0, ge=0, le=100000)
    start_date: date | None = None
    end_date: date | None = None


def _scheme_json(payload: SchemeInput) -> dict:
    return payload.model_dump(mode="json", exclude={"status"})


def _assert_source_urls(data: dict) -> None:
    if not validate_official_url(data.get("source_url", ""), required=True):
        raise HTTPException(status_code=422, detail="Scheme source must be an HTTPS URL on an allowed official domain.")
    app_url = data.get("application_url", "")
    if app_url and not validate_official_url(app_url, required=False):
        raise HTTPException(status_code=422, detail="Application URL must use an allowed official HTTPS domain.")


def _create_scheme(db: Session, payload: SchemeInput, actor: User) -> Scheme:
    if payload.status in {"VERIFIED", "PUBLISHED"}:
        raise HTTPException(status_code=422, detail="New records must go through the review and publish workflow.")
    data = _scheme_json(payload)
    _assert_source_urls(data)
    existing = db.scalar(select(Scheme).where(Scheme.slug == payload.slug))
    if existing:
        raise HTTPException(status_code=409, detail=f"Scheme slug already exists: {payload.slug}")
    data["data_status"] = "NEEDS_HUMAN_REVIEW"
    row = Scheme(
        slug=payload.slug, name=payload.name, department=payload.department, level=payload.level,
        category=payload.category, status="UNDER_REVIEW", verification_status="NEEDS_REVIEW",
        source_url=payload.source_url, source_name=payload.source_name, application_url=payload.application_url,
        data_json=data, version=1,
    )
    db.add(row)
    db.flush()
    snapshot = dict(data)
    db.add(SchemeVersion(scheme_id=row.id, version=1, snapshot=snapshot, source_url=payload.source_url, change_reason="Initial admin import"))
    write_audit(db, actor, "SCHEME_CREATED", "scheme", row.slug, None, {"name": row.name, "status": row.status}, "Imported into review queue")
    return row


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(admin_user)):
    return {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "schemes": db.scalar(select(func.count(Scheme.id))) or 0,
        "published_schemes": db.scalar(select(func.count(Scheme.id)).where(Scheme.status == "PUBLISHED")) or 0,
        "needs_review": db.scalar(select(func.count(Scheme.id)).where(Scheme.verification_status == "NEEDS_REVIEW")) or 0,
        "recommendations": db.scalar(select(func.count(RecommendationSnapshot.id))) or 0,
        "feedback": db.scalar(select(func.count(Feedback.id))) or 0,
        "surveys": db.scalar(select(func.count(PilotSurvey.id))) or 0,
        "proposed_pilots": db.scalar(select(func.count(Pilot.id)).where(Pilot.status == "PROPOSED")) or 0,
        "note": "Counts are system usage only; do not present them as impact or benefit outcomes."
    }


@router.get("/schemes")
def admin_schemes(db: Session = Depends(get_db), user: User = Depends(admin_user)):
    rows = db.scalars(select(Scheme).order_by(Scheme.updated_at.desc())).all()
    return {"schemes": [{**scheme_payload(row), "verified_by": row.verified_by} for row in rows]}


@router.post("/schemes", status_code=status.HTTP_201_CREATED)
def create_scheme(payload: SchemeInput, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    row = _create_scheme(db, payload, user)
    db.commit()
    return {"scheme": scheme_payload(row)}


@router.put("/schemes/{slug}")
def update_scheme(slug: str, payload: SchemeInput, note: ActionNote, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    if payload.slug != slug:
        raise HTTPException(status_code=422, detail="The scheme slug is immutable; create a new record to change it.")
    row = db.scalar(select(Scheme).where(Scheme.slug == slug))
    if row is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    data = _scheme_json(payload)
    _assert_source_urls(data)
    old = scheme_payload(row)
    next_version = row.version + 1
    row.name = payload.name
    row.department = payload.department
    row.level = payload.level
    row.category = payload.category
    row.source_url = payload.source_url
    row.source_name = payload.source_name
    row.application_url = payload.application_url
    data["data_status"] = "NEEDS_HUMAN_REVIEW"
    row.data_json = data
    row.version = next_version
    row.status = "UNDER_REVIEW"
    row.verification_status = "NEEDS_REVIEW"
    row.last_verified_at = None
    row.verified_by = None
    row.versions[-1].effective_to = datetime.now(timezone.utc) if row.versions else None
    db.add(SchemeVersion(scheme_id=row.id, version=next_version, snapshot=dict(data), source_url=payload.source_url, change_reason=note.reason))
    write_audit(db, user, "SCHEME_UPDATED", "scheme", row.slug, old, {"name": row.name, "status": row.status, "version": row.version}, note.reason)
    db.commit()
    db.refresh(row)
    return {"scheme": scheme_payload(row)}


@router.post("/schemes/import", status_code=status.HTTP_201_CREATED)
def import_schemes(payload: list[SchemeInput], db: Session = Depends(get_db), user: User = Depends(admin_user)):
    if len(payload) > 100:
        raise HTTPException(status_code=413, detail="Import is limited to 100 records per batch.")
    created = []
    for item in payload:
        created.append(_create_scheme(db, item, user))
    db.commit()
    return {"imported": len(created), "schemes": [scheme_payload(item) for item in created], "status": "UNDER_REVIEW"}


@router.post("/schemes/{slug}/verify")
def verify_scheme(slug: str, note: ActionNote, db: Session = Depends(get_db), user: User = Depends(verifier_user)):
    row = db.scalar(select(Scheme).where(Scheme.slug == slug))
    if row is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    data = row.data_json or {}
    _assert_source_urls(data)
    if not data.get("summary") or not data.get("source_facts") or not data.get("checks"):
        raise HTTPException(status_code=422, detail="A summary, source facts, and eligibility checks are required before verification.")
    old = {"verification_status": row.verification_status, "status": row.status, "version": row.version}
    row.verification_status = "VERIFIED"
    row.status = "VERIFIED"
    row.last_verified_at = datetime.now(timezone.utc)
    row.verified_by = user.id
    data["data_status"] = "VERIFIED_HUMAN"
    data["source_checked_at"] = row.last_verified_at.date().isoformat()
    row.data_json = data
    if row.versions:
        row.versions[-1].verified_at = row.last_verified_at
        row.versions[-1].verified_by = user.id
        row.versions[-1].snapshot = dict(data)
    write_audit(db, user, "SCHEME_VERIFIED", "scheme", row.slug, old, {"verification_status": row.verification_status, "version": row.version}, note.reason)
    db.commit()
    db.refresh(row)
    return {"scheme": scheme_payload(row), "message": "Human verification recorded. Publishing remains a separate admin action."}


@router.post("/schemes/{slug}/publish")
def publish_scheme(slug: str, note: ActionNote, db: Session = Depends(get_db), user: User = Depends(publisher_user)):
    row = db.scalar(select(Scheme).where(Scheme.slug == slug))
    if row is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    if row.verification_status != "VERIFIED" or not row.last_verified_at or not row.verified_by:
        raise HTTPException(status_code=409, detail="A data verifier must sign off before publishing.")
    if row.verified_by == user.id:
        raise HTTPException(status_code=409, detail="A different administrator must publish a version from its verifier.")
    old = {"status": row.status}
    row.status = "PUBLISHED"
    write_audit(db, user, "SCHEME_PUBLISHED", "scheme", row.slug, old, {"status": row.status, "version": row.version}, note.reason)
    db.commit()
    db.refresh(row)
    return {"scheme": scheme_payload(row)}


@router.post("/schemes/{slug}/archive")
def archive_scheme(slug: str, note: ActionNote, db: Session = Depends(get_db), user: User = Depends(publisher_user)):
    row = db.scalar(select(Scheme).where(Scheme.slug == slug))
    if row is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    old = {"status": row.status}
    row.status = "ARCHIVED"
    write_audit(db, user, "SCHEME_ARCHIVED", "scheme", row.slug, old, {"status": row.status}, note.reason)
    db.commit()
    return {"scheme": scheme_payload(row)}


@router.get("/audit-logs")
def audit_logs(limit: int = 100, db: Session = Depends(get_db), user: User = Depends(admin_user)):
    limit = max(1, min(limit, 500))
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return {"audit_logs": [{"id": row.id, "actor_user_id": row.actor_user_id, "action": row.action,
        "entity_type": row.entity_type, "entity_id": row.entity_id, "old_value": row.old_value,
        "new_value": row.new_value, "reason": row.reason, "created_at": row.created_at.isoformat()} for row in rows]}


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user: User = Depends(admin_user)):
    events = db.execute(select(AnalyticsEvent.event_name, func.count(AnalyticsEvent.id)).group_by(AnalyticsEvent.event_name)).all()
    by_event = {name: count for name, count in events}
    return {"events": by_event,
            "recommendations_generated": by_event.get("recommendations_generated", 0),
            "official_portal_clicks": by_event.get("official_application_click", 0),
            "scheme_views": by_event.get("scheme_viewed", 0),
            "feedback_count": db.scalar(select(func.count(Feedback.id))) or 0,
            "note": "Usage events are not impact measures; approvals and benefit delivery are not integrated."}


@router.get("/pilots")
def list_pilots(db: Session = Depends(get_db), user: User = Depends(admin_user)):
    rows = db.scalars(select(Pilot).order_by(Pilot.created_at.desc())).all()
    return {"pilots": [{"id": x.id, "name": x.name, "location": x.location, "target_users": x.target_users,
                        "status": x.status, "partner_claim": x.partner_claim,
                        "start_date": x.start_date.isoformat() if x.start_date else None,
                        "end_date": x.end_date.isoformat() if x.end_date else None} for x in rows]}


@router.post("/pilots", status_code=status.HTTP_201_CREATED)
def create_pilot(payload: PilotInput, db: Session = Depends(get_db), user: User = Depends(publisher_user)):
    item = Pilot(name=payload.name, location=payload.location, target_users=payload.target_users,
                 start_date=payload.start_date, end_date=payload.end_date, status="PROPOSED",
                 partner_claim="PROPOSED_ONLY", created_by=user.id)
    db.add(item)
    db.flush()
    write_audit(db, user, "PILOT_PROPOSED", "pilot", item.id, None, {"name": item.name, "partner_claim": item.partner_claim}, "Pilot partner not confirmed")
    db.commit()
    return {"id": item.id, "name": item.name, "location": item.location, "target_users": item.target_users,
            "status": item.status, "partner_claim": item.partner_claim}
