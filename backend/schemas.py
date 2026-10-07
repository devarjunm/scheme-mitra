"""Validated API payloads. Extra fields are rejected to avoid accidental mass assignment."""
from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegisterRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=100)
    state: str = Field(default="Maharashtra", max_length=60)
    district: str = Field(default="", max_length=100)
    taluka: str = Field(default="", max_length=100)

    @field_validator("password")
    @classmethod
    def password_not_common(cls, value: str) -> str:
        if value.lower() in {"password123!", "qwerty123456", "schememitra123"}:
            raise ValueError("Choose a stronger password.")
        if not any(ch.isalpha() for ch in value) or not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain letters and numbers.")
        return value


class LoginRequest(StrictModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ProfileUpdate(StrictModel):
    name: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=60)
    district: str | None = Field(default=None, max_length=100)
    taluka: str | None = Field(default=None, max_length=100)
    village: str | None = Field(default=None, max_length=120)
    land_area_acres: float | None = Field(default=None, ge=0, le=100000)
    farmer_category: Literal["marginal", "small", "other", "unknown"] | None = None
    social_category: Literal["not_provided", "open", "obc", "sc", "st", "not_applicable"] | None = None
    crop: str | None = Field(default=None, max_length=100)
    season: str | None = Field(default=None, max_length=32)
    irrigation: Literal["yes", "no", "unknown"] | None = None
    support_needs: list[Literal["irrigation", "horticulture", "machinery", "income_support", "crop_protection"]] | None = None
    aadhaar_present: bool | None = None
    electric_water_pump: Literal["yes", "no", "unknown"] | None = None
    permanent_electric_connection: Literal["yes", "no", "unknown"] | None = None
    prior_micro_benefit_year: Literal["none", "unknown", "before_2016_17", "from_2017_18", "other"] | None = None
    selected_component: str | None = Field(default=None, max_length=120)
    selected_machinery: str | None = Field(default=None, max_length=120)
    previous_same_machinery_year: Literal["none", "unknown", "within_10_years", "over_10_years"] | None = None
    documents: dict[str, Literal["available", "not_provided", "needs_verification", "not_yet_required", "not_yet_issued"]] | None = None


class LandCreate(StrictModel):
    label: str = Field(default="Farm plot", min_length=1, max_length=80)
    area_acres: float = Field(ge=0, le=100000)
    ownership_type: Literal["owned", "leased", "shared", "unknown"] = "unknown"
    irrigation_available: Literal["yes", "no", "unknown"] = "unknown"
    irrigation_type: str = Field(default="", max_length=64)
    water_source: str = Field(default="", max_length=64)
    survey_reference: str = Field(default="", max_length=80)
    is_primary: bool = False


class CropCreate(StrictModel):
    crop_name: str = Field(min_length=1, max_length=100)
    crop_category: str = Field(default="", max_length=64)
    season: str = Field(default="", max_length=32)
    area_acres: float | None = Field(default=None, ge=0, le=100000)
    year: int | None = Field(default=None, ge=2000, le=2100)
    is_current: bool = True


class DocumentStateUpdate(StrictModel):
    state: Literal["available", "not_provided", "needs_verification", "not_yet_required", "not_yet_issued"]


class ApplicationCreate(StrictModel):
    scheme_slug: str = Field(min_length=1, max_length=140)
    reference: str = Field(default="", max_length=100)
    applied_on: date | None = None
    status: Literal["DRAFT", "SUBMITTED", "UNDER_REVIEW", "DOCUMENTS_REQUIRED", "APPROVED", "REJECTED", "UNKNOWN"] = "DRAFT"
    notes: str = Field(default="", max_length=1000)


class ApplicationUpdate(StrictModel):
    reference: str | None = Field(default=None, max_length=100)
    applied_on: date | None = None
    status: Literal["DRAFT", "SUBMITTED", "UNDER_REVIEW", "DOCUMENTS_REQUIRED", "APPROVED", "REJECTED", "UNKNOWN"] | None = None
    notes: str | None = Field(default=None, max_length=1000)


class AssistantQuestion(StrictModel):
    question: str = Field(min_length=1, max_length=1000)
    scheme_slug: str | None = Field(default=None, max_length=140)
    language: Literal["en", "mr", "hi"] = "en"


class FeedbackCreate(StrictModel):
    scheme_slug: str | None = Field(default=None, max_length=140)
    useful: bool
    reason: str = Field(default="", max_length=160)


class PilotSurveyCreate(StrictModel):
    phase: Literal["baseline", "post_use"]
    time_minutes: float | None = Field(default=None, ge=0, le=10000)
    knows_relevant_schemes: bool | None = None
    understands_documents: bool | None = None
    knows_next_step: bool | None = None
    comment: str = Field(default="", max_length=500)


class SchemeInput(StrictModel):
    slug: str = Field(min_length=3, max_length=140, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=3, max_length=240)
    department: str = Field(min_length=2, max_length=180)
    level: str = Field(default="State", max_length=80)
    category: str = Field(default="General", max_length=80)
    source_name: str = Field(min_length=2, max_length=160)
    source_url: str = Field(min_length=12, max_length=1200)
    application_url: str = Field(default="", max_length=1200)
    summary: str = Field(min_length=10, max_length=4000)
    benefit_summary: str = Field(default="", max_length=2000)
    need: str = Field(default="", max_length=64)
    crop_tags: list[str] = Field(default_factory=list, max_length=100)
    source_facts: list[str] = Field(default_factory=list, max_length=100)
    document_items: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    checks: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    name_mr: str = Field(default="", max_length=240)
    icon: str = Field(default="leaf", max_length=24)
    source_checked_at: date | None = None
    status: Literal["DRAFT", "UNDER_REVIEW", "VERIFIED", "PUBLISHED", "ARCHIVED"] = "UNDER_REVIEW"

    @field_validator("source_url", "application_url")
    @classmethod
    def safe_official_url(cls, value: str) -> str:
        if value and not value.startswith("https://"):
            raise ValueError("Official links must use HTTPS.")
        return value
