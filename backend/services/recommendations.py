from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import DEMO_MODE
from ..eligibility import evaluate_scheme, generate_recommendations
from ..models import Scheme, User
from .farmers import profile_dict


def scheme_payload(row: Scheme) -> dict[str, Any]:
    payload = dict(row.data_json or {})
    payload.update({
        "slug": row.slug, "name": row.name, "department": row.department,
        "category": row.category, "level": row.level, "status": row.status,
        "verification_status": row.verification_status,
        "source_url": row.source_url, "source_name": row.source_name,
        "application_url": row.application_url,
        "last_verified_at": row.last_verified_at.isoformat() if row.last_verified_at else None,
        "version": row.version,
    })
    return payload


def visible_schemes(db: Session, user: User | None = None, include_archived: bool = False) -> list[dict[str, Any]]:
    query = select(Scheme).order_by(Scheme.name)
    rows = db.scalars(query).all()
    allow_review = DEMO_MODE and bool(user and user.is_demo)
    output = []
    for row in rows:
        if not include_archived and row.status == "ARCHIVED":
            continue
        if row.status != "PUBLISHED" and not allow_review:
            continue
        output.append(scheme_payload(row))
    return output


def recommendations_for(db: Session, user: User) -> list[dict[str, Any]]:
    profile = profile_dict(db, user)
    schemes = visible_schemes(db, user)
    return generate_recommendations(schemes, profile)


def evaluation_for(db: Session, user: User, scheme: Scheme) -> dict[str, Any]:
    return evaluate_scheme(scheme_payload(scheme), profile_dict(db, user))
