from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import db as db_module
from backend.api import main
from backend.db import Base
from backend.models import Scheme, User
from backend.security import hash_password


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    testing_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(db_module, "engine", engine)
    monkeypatch.setattr(db_module, "SessionLocal", testing_sessions)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", testing_sessions)
    with TestClient(main.app) as test_client:
        yield test_client, testing_sessions
    engine.dispose()


def csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("scheme_mitra_csrf")
    assert token
    return {"X-CSRF-Token": token}


def test_cookie_session_csrf_and_server_side_logout_revocation(client):
    http, _ = client
    response = http.post("/api/v1/auth/demo", json={})
    assert response.status_code == 200
    access_token = http.cookies.get("scheme_mitra_access")
    assert access_token
    assert http.get("/api/v1/profile").status_code == 200
    generated = http.post("/api/v1/recommendations/generate", json={}, headers=csrf_headers(http))
    assert generated.status_code == 200
    assert len(generated.json()["recommendations"]) == 3

    # Authenticated unsafe requests fail closed without the double-submit token.
    assert http.patch("/api/v1/documents/land_7_12", json={"state": "available"}).status_code == 403
    update = http.patch("/api/v1/documents/land_7_12", json={"state": "available"}, headers=csrf_headers(http))
    assert update.status_code == 200
    assert update.json()["validated"] is False

    assert http.post("/api/v1/auth/logout", json={}, headers=csrf_headers(http)).status_code == 200
    # A copied signed token cannot be reused after the server-side session is revoked.
    http.cookies.set("scheme_mitra_access", access_token)
    assert http.get("/api/v1/profile").status_code == 401


def test_saved_schemes_include_their_scheme_record(client):
    http, session_factory = client
    assert http.post("/api/v1/auth/demo", json={}).status_code == 200

    with session_factory() as db:
        db.add(Scheme(
            slug="saved-test-scheme",
            name="Saved Test Scheme",
            department="Agriculture Department",
            status="PUBLISHED",
            verification_status="VERIFIED",
            source_url="https://mahadbt.maharashtra.gov.in/",
            source_name="MahaDBT",
            data_json={"summary": "Test scheme"},
        ))
        db.commit()

    saved_response = http.post(
        "/api/v1/saved/saved-test-scheme",
        json={},
        headers=csrf_headers(http),
    )
    assert saved_response.status_code == 201

    response = http.get("/api/v1/saved")
    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["saved"]] == ["saved-test-scheme"]


def test_farmer_role_cannot_access_admin_and_super_admin_can_publish(client):
    http, session_factory = client
    farmer = http.post("/api/v1/auth/register", json={
        "email": "farmer@example.com", "password": "FarmPassword2026!", "full_name": "Test Farmer",
        "state": "Maharashtra", "district": "Nashik", "taluka": "Niphad",
    })
    assert farmer.status_code == 201
    assert http.get("/api/v1/admin/overview").status_code == 403
    assert http.post("/api/v1/auth/logout", json={}, headers=csrf_headers(http)).status_code == 200

    with session_factory() as db:
        db.add(User(email="admin@example.com", full_name="Test Admin", password_hash=hash_password("AdminPassword2026!"), role="SUPER_ADMIN", is_active=True))
        db.add(User(email="verifier@example.com", full_name="Test Verifier", password_hash=hash_password("VerifierPassword2026!"), role="DATA_VERIFIER", is_active=True))
        db.commit()

    login = http.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "AdminPassword2026!"})
    assert login.status_code == 200
    headers = csrf_headers(http)
    assert http.get("/api/v1/admin/overview").status_code == 200

    scheme = {
        "slug": "test-admin-scheme", "name": "Test Admin Scheme", "department": "Agriculture Department, Government of Maharashtra",
        "level": "State", "category": "Irrigation", "source_name": "MahaDBT Farmer Portal",
        "source_url": "https://mahadbt.maharashtra.gov.in/Farmer/SchemeData/SchemeData?str=E9DDFA703C38E51AC7B56240D6D84F28",
        "application_url": "https://mahadbt.maharashtra.gov.in/Farmer/Login/Login",
        "summary": "A source-backed test record for workflow coverage.", "benefit_summary": "Not specified in this test record.",
        "need": "irrigation", "crop_tags": ["onion"], "source_facts": ["A test source fact."],
        "document_items": [{"id": "land_record", "label": "Land record", "stage": "Before applying", "required": True}],
        "checks": [{"id": "aadhaar", "label": "Aadhaar availability", "field": "aadhaar_present", "kind": "boolean"}],
        "name_mr": "", "icon": "water", "source_checked_at": "2026-10-07",
    }
    created = http.post("/api/v1/admin/schemes", json=scheme, headers=headers)
    assert created.status_code == 201
    assert created.json()["scheme"]["status"] == "UNDER_REVIEW"
    self_verified = http.post("/api/v1/admin/schemes/test-admin-scheme/verify", json={"reason": "Self-review must not be enough"}, headers=headers)
    assert self_verified.status_code == 200
    self_publish = http.post("/api/v1/admin/schemes/test-admin-scheme/publish", json={"reason": "Same actor"}, headers=headers)
    assert self_publish.status_code == 409

    assert http.post("/api/v1/auth/logout", json={}, headers=headers).status_code == 200
    verifier_login = http.post("/api/v1/auth/login", json={"email": "verifier@example.com", "password": "VerifierPassword2026!"})
    assert verifier_login.status_code == 200
    verifier_headers = csrf_headers(http)
    verified = http.post("/api/v1/admin/schemes/test-admin-scheme/verify", json={"reason": "Independent verifier review"}, headers=verifier_headers)
    assert verified.status_code == 200
    assert verified.json()["scheme"]["verification_status"] == "VERIFIED"
    # Same-person verification and publication are rejected by the API.
    assert http.post("/api/v1/admin/schemes/test-admin-scheme/publish", json={"reason": "Must be separate actor"}, headers=verifier_headers).status_code == 403

    assert http.post("/api/v1/auth/logout", json={}, headers=verifier_headers).status_code == 200
    publisher_login = http.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "AdminPassword2026!"})
    assert publisher_login.status_code == 200
    publisher_headers = csrf_headers(http)
    published = http.post("/api/v1/admin/schemes/test-admin-scheme/publish", json={"reason": "Independent verifier sign-off"}, headers=publisher_headers)
    assert published.status_code == 200
    assert published.json()["scheme"]["status"] == "PUBLISHED"


def test_health_and_admin_static_page_are_served(client):
    http, _ = client
    assert http.get("/health").status_code == 200
    assert http.get("/ready").status_code == 200
    page = http.get("/admin.html")
    assert page.status_code == 200
    assert "Scheme administration" in page.text
