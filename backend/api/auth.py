from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import DEMO_MODE
from ..db import get_db
from ..dependencies import optional_user
from ..models import AuthSession, FarmerProfile, User
from ..schemas import LoginRequest, RegisterRequest
from ..security import ACCESS_COOKIE, clear_session_cookies, decode_token, hash_password, set_session_cookies, verify_password
from .common import record_event

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role, "is_demo": user.is_demo}


@router.get("/me")
def me(user: User | None = Depends(optional_user)):
    if not user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": public_user(user)}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(email=email, full_name=payload.full_name, password_hash=hash_password(payload.password), role="FARMER", is_active=True)
    db.add(user)
    db.flush()
    db.add(FarmerProfile(user_id=user.id, state=payload.state, district=payload.district, taluka=payload.taluka, support_needs=[]))
    set_session_cookies(response, user.id, user.role, db)
    db.commit()
    db.refresh(user)
    return {"authenticated": True, "user": public_user(user)}


@router.post("/login")
def login(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    # Keep the response identical for unknown users and wrong passwords.
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    user.last_login_at = datetime.now(timezone.utc)
    record_event(db, user.id, "login_succeeded", {})
    set_session_cookies(response, user.id, user.role, db)
    db.commit()
    return {"authenticated": True, "user": public_user(user)}


@router.post("/demo")
def open_demo(response: Response, db: Session = Depends(get_db)):
    if not DEMO_MODE:
        raise HTTPException(status_code=404, detail="Demo access is disabled.")
    user = db.scalar(select(User).where(User.email == "demo@schememitra.app", User.is_demo.is_(True), User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=503, detail="Demo account is not seeded. Run the development seed command.")
    user.last_login_at = datetime.now(timezone.utc)
    set_session_cookies(response, user.id, user.role, db)
    db.commit()
    return {"authenticated": True, "user": public_user(user)}


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(ACCESS_COOKIE)
    if token:
        try:
            claims = decode_token(token)
            session = db.get(AuthSession, claims.get("jti")) if claims.get("jti") else None
            if session and session.revoked_at is None:
                session.revoked_at = datetime.now(timezone.utc)
                db.commit()
        except HTTPException:
            # An expired or malformed token still gets its browser cookies cleared.
            db.rollback()
    clear_session_cookies(response)
    return {"authenticated": False}
