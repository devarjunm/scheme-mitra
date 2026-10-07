from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import DEMO_MODE
from .db import get_db
from .models import AuthSession, User
from .security import ACCESS_COOKIE, decode_token


def optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        if DEMO_MODE:
            return db.scalar(select(User).where(User.email == "demo@schememitra.app", User.is_demo.is_(True), User.is_active.is_(True)))
        return None
    claims = decode_token(token)
    jti = claims.get("jti")
    session = db.get(AuthSession, jti) if isinstance(jti, str) else None
    if session is None or session.revoked_at is not None or session.user_id != claims.get("sub"):
        return None
    expiry = session.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        return None
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        return None
    request.state.user_id = user.id
    return user


def current_user(user: User | None = Depends(optional_user)) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.")
    return user


def roles_required(*roles: str) -> Callable:
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this area.")
        return user
    return dependency
