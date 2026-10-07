"""Password hashing, signed session cookies, and CSRF primitives."""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import HTTPException, Request, status

from .config import ACCESS_TOKEN_MINUTES, COOKIE_SAMESITE, COOKIE_SECURE, JWT_ALGORITHM, JWT_SECRET
from .models import AuthSession

_password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32, salt_len=16)
ACCESS_COOKIE = "scheme_mitra_access"
CSRF_COOKIE = "scheme_mitra_csrf"


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return _password_hasher.verify(encoded, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def issue_token(user_id: str, role: str) -> tuple[str, int, str, datetime]:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    jti = secrets.token_urlsafe(24)
    claims = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": expires,
        "iss": "scheme-mitra",
        "aud": "scheme-mitra-web",
        "jti": jti,
    }
    return jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGORITHM), int((expires - now).total_seconds()), jti, expires


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], issuer="scheme-mitra", audience="scheme-mitra-web")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session has expired. Please sign in again.") from exc


def set_session_cookies(response, user_id: str, role: str, db: Session) -> None:
    token, max_age, jti, expires_at = issue_token(user_id, role)
    csrf = secrets.token_urlsafe(32)
    db.add(AuthSession(jti=jti, user_id=user_id, expires_at=expires_at))
    response.set_cookie(ACCESS_COOKIE, token, max_age=max_age, httponly=True, secure=COOKIE_SECURE,
                        samesite=COOKIE_SAMESITE, path="/")
    response.set_cookie(CSRF_COOKIE, csrf, max_age=max_age, httponly=False, secure=COOKIE_SECURE,
                        samesite=COOKIE_SAMESITE, path="/")


def clear_session_cookies(response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/", httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)
    response.delete_cookie(CSRF_COOKIE, path="/", httponly=False, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE)


def csrf_from_request(request: Request) -> None:
    """Double-submit check for cookie-authenticated unsafe requests."""
    if request.method.upper() in {"GET", "HEAD", "OPTIONS"}:
        return
    if not request.cookies.get(ACCESS_COOKIE):
        return  # registration/login/demo bootstrap have no authenticated session yet
    cookie_value = request.cookies.get(CSRF_COOKIE, "")
    header_value = request.headers.get("X-CSRF-Token", "")
    if not cookie_value or not header_value or not secrets.compare_digest(cookie_value, header_value):
        raise HTTPException(status_code=403, detail="CSRF validation failed. Refresh the page and retry.")
