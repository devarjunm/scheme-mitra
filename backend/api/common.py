from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AnalyticsEvent, Application, AuditLog, Scheme, User

OFFICIAL_HOSTS = {
    "mahadbt.maharashtra.gov.in", "myscheme.gov.in", "www.myscheme.gov.in",
    "api.setu.gov.in", "www.data.gov.in", "data.gov.in", "maharashtra.gov.in", "www.maharashtra.gov.in"
}
SENSITIVE_EVENT_KEYS = {"phone", "mobile", "aadhaar", "aadhar", "email", "password", "bank", "account", "token", "reference"}
EVENT_METADATA_KEYS = {
    "recommendations_generated": {"count"},
    "scheme_viewed": {"scheme_slug"},
    "scheme_saved": {"scheme_slug"},
    "scheme_unsaved": {"scheme_slug"},
    "official_application_click": {"scheme_slug"},
    "assistant_question": {"scheme_slug", "grounding"},
    "profile_updated": set(),
    "document_state_changed": {"document_id", "state"},
    "application_created": {"scheme_slug", "status"},
    "application_updated": {"status"},
    "feedback_submitted": {"scope", "useful", "scheme_slug"},
    "pilot_survey_submitted": {"phase"},
    "scheme_search": {"category"},
    "notification_read": set(),
    "login_succeeded": set(),
}
EVENT_ALLOWLIST = set(EVENT_METADATA_KEYS)


def validate_official_url(value: str, required: bool = True) -> bool:
    if not value:
        return not required
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme == "https" and parsed.username is None and parsed.password is None and host in OFFICIAL_HOSTS


def require_scheme(db: Session, slug: str, user: User | None = None) -> Scheme:
    scheme = db.scalar(select(Scheme).where(Scheme.slug == slug))
    if scheme is None or scheme.status == "ARCHIVED":
        raise HTTPException(status_code=404, detail="Scheme not found.")
    if scheme.status != "PUBLISHED" and not (user and user.is_demo):
        raise HTTPException(status_code=404, detail="Scheme not found.")
    return scheme


def record_event(db: Session, user_id: str | None, event_name: str, metadata: dict[str, Any] | None = None) -> None:
    allowed_keys = EVENT_METADATA_KEYS.get(event_name)
    if allowed_keys is None:
        return
    safe = {}
    for key, value in (metadata or {}).items():
        if key not in allowed_keys or value is None or isinstance(value, (dict, list)):
            continue
        key_text = str(key)[:64]
        if key_text.lower() in SENSITIVE_EVENT_KEYS:
            continue
        safe[key_text] = str(value)[:200]
    db.add(AnalyticsEvent(user_id=user_id, event_name=event_name, metadata_json=safe))


def write_audit(db: Session, actor: User | None, action: str, entity_type: str, entity_id: str,
                old_value: dict | None = None, new_value: dict | None = None, reason: str = "") -> None:
    db.add(AuditLog(
        actor_user_id=actor.id if actor else None, action=action, entity_type=entity_type,
        entity_id=str(entity_id), old_value=old_value, new_value=new_value, reason=reason[:500]
    ))


def application_payload(application: Application) -> dict[str, Any]:
    return {
        "id": application.id,
        "scheme_slug": application.scheme.slug,
        "scheme_name": application.scheme.name,
        "reference": application.reference,
        "applied_on": application.applied_on.isoformat() if application.applied_on else "",
        "status": application.status,
        "notes": application.notes,
        "entered_by": "USER_ENTERED",
        "status_source": "USER_ENTERED",
        "created_at": application.created_at.isoformat(),
        "updated_at": application.updated_at.isoformat(),
    }


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
