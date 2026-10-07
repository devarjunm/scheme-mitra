"""Normalized persistence models. No raw identity numbers or document blobs are stored."""
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_role_active", "role", "is_active"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False, default="FARMER")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    profile: Mapped["FarmerProfile | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    lands: Mapped[list["FarmerLand"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    crops: Mapped[list["FarmerCrop"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["FarmerDocument"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (Index("ix_auth_sessions_user_expires", "user_id", "expires_at"),)

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(60), nullable=False, default="Maharashtra")
    district: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    taluka: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    village: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    farmer_category: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    social_category: Mapped[str] = mapped_column(String(32), nullable=False, default="not_provided")
    support_needs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    aadhaar_present: Mapped[bool | None] = mapped_column(Boolean)
    irrigation: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    electric_water_pump: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    permanent_electric_connection: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    prior_micro_benefit_year: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    selected_component: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    selected_machinery: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    previous_same_machinery_year: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="profile")


class FarmerLand(Base):
    __tablename__ = "farmer_land"
    __table_args__ = (CheckConstraint("area_acres >= 0", name="ck_farmer_land_area_nonnegative"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(80), nullable=False, default="Farm plot")
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    ownership_type: Mapped[str] = mapped_column(String(24), nullable=False, default="unknown")
    irrigation_available: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    irrigation_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    water_source: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    survey_reference: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="lands")


class FarmerCrop(Base):
    __tablename__ = "farmer_crops"
    __table_args__ = (CheckConstraint("area_acres IS NULL OR area_acres >= 0", name="ck_farmer_crop_area_nonnegative"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    crop_category: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    season: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    area_acres: Mapped[float | None] = mapped_column(Float)
    year: Mapped[int | None] = mapped_column(Integer)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    user: Mapped[User] = relationship(back_populates="crops")


class FarmerDocument(Base):
    __tablename__ = "farmer_documents"
    __table_args__ = (UniqueConstraint("user_id", "document_id", name="uq_farmer_document_item"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="not_provided")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="documents")


class Scheme(Base):
    __tablename__ = "schemes"
    __table_args__ = (Index("ix_schemes_status_category", "status", "category"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    department: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="General")
    level: Mapped[str] = mapped_column(String(80), nullable=False, default="State")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="DRAFT")
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default="NEEDS_REVIEW")
    source_url: Mapped[str] = mapped_column(String(1200), nullable=False)
    application_url: Mapped[str] = mapped_column(String(1200), nullable=False, default="")
    source_name: Mapped[str] = mapped_column(String(160), nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    data_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    versions: Mapped[list["SchemeVersion"]] = relationship(back_populates="scheme", cascade="all, delete-orphan", order_by="SchemeVersion.version")


class SchemeVersion(Base):
    __tablename__ = "scheme_versions"
    __table_args__ = (UniqueConstraint("scheme_id", "version", name="uq_scheme_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_url: Mapped[str] = mapped_column(String(1200), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    change_reason: Mapped[str] = mapped_column(String(500), nullable=False, default="Initial import")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    scheme: Mapped[Scheme] = relationship(back_populates="versions")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"
    __table_args__ = (UniqueConstraint("user_id", "scheme_id", name="uq_saved_scheme_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    scheme: Mapped[Scheme] = relationship()


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (Index("ix_applications_user_status", "user_id", "status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("schemes.id", ondelete="RESTRICT"), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    applied_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    notes: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    status_source: Mapped[str] = mapped_column(String(24), nullable=False, default="USER_ENTERED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    scheme: Mapped[Scheme] = relationship()
    history: Mapped[list["ApplicationStatusHistory"]] = relationship(back_populates="application", cascade="all, delete-orphan", order_by="ApplicationStatusHistory.created_at")


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status: Mapped[str] = mapped_column(String(32), nullable=False)
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    status_source: Mapped[str] = mapped_column(String(24), nullable=False, default="USER_ENTERED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    application: Mapped[Application] = relationship(back_populates="history")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(String(800), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1200))
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False, default="INFO")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    scheme_id: Mapped[str | None] = mapped_column(ForeignKey("schemes.id", ondelete="SET NULL"), index=True)
    useful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = (Index("ix_analytics_event_name_created", "event_name", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    event_name: Mapped[str] = mapped_column(String(80), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class PilotSurvey(Base):
    __tablename__ = "pilot_surveys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    phase: Mapped[str] = mapped_column(String(16), nullable=False)
    time_minutes: Mapped[float | None] = mapped_column(Float)
    knows_relevant_schemes: Mapped[bool | None] = mapped_column(Boolean)
    understands_documents: Mapped[bool | None] = mapped_column(Boolean)
    knows_next_step: Mapped[bool | None] = mapped_column(Boolean)
    comment: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class Pilot(Base):
    __tablename__ = "pilots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    location: Mapped[str] = mapped_column(String(160), nullable=False)
    target_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="PROPOSED")
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    partner_claim: Mapped[str] = mapped_column(String(24), nullable=False, default="PROPOSED_ONLY")
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_created", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    old_value: Mapped[dict | None] = mapped_column(JSON)
    new_value: Mapped[dict | None] = mapped_column(JSON)
    reason: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class RecommendationSnapshot(Base):
    __tablename__ = "recommendation_snapshots"
    __table_args__ = (Index("ix_recommendations_user_created", "user_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_match: Mapped[int] = mapped_column(Integer, nullable=False)
    eligibility_status: Mapped[str] = mapped_column(String(32), nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
