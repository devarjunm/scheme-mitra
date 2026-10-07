"""Environment-backed configuration with fail-closed production checks."""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent.parent
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'backend' / 'data' / 'scheme_mitra_app.sqlite3'}")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-before-deployment-32-char-minimum")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true" if IS_PRODUCTION else "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "strict").lower()
DEMO_MODE = os.getenv("DEMO_MODE", "false" if IS_PRODUCTION else "true").lower() == "true"
SEED_SCHEMES = os.getenv("SEED_SCHEMES", "true" if not IS_PRODUCTION else "false").lower() == "true"
CORS_ORIGINS = [value.strip() for value in os.getenv("CORS_ORIGINS", "").split(",") if value.strip()]
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
TRUSTED_HOSTS = [value.strip() for value in os.getenv("TRUSTED_HOSTS", "*").split(",") if value.strip()]
RATE_LIMIT_REDIS_URL = os.getenv("RATE_LIMIT_REDIS_URL", "")
FORWARDED_ALLOW_IPS = os.getenv("FORWARDED_ALLOW_IPS", "127.0.0.1,::1")


def validate_runtime_config() -> None:
    if COOKIE_SAMESITE not in {"strict", "lax", "none"}:
        raise RuntimeError("COOKIE_SAMESITE must be strict, lax, or none.")
    if COOKIE_SAMESITE == "none" and not COOKIE_SECURE:
        raise RuntimeError("SameSite=None cookies require COOKIE_SECURE=true.")
    if ACCESS_TOKEN_MINUTES < 5 or ACCESS_TOKEN_MINUTES > 1440:
        raise RuntimeError("ACCESS_TOKEN_MINUTES must be between 5 and 1440.")
    if IS_PRODUCTION:
        if len(JWT_SECRET) < 32 or JWT_SECRET.startswith("dev-only"):
            raise RuntimeError("Production requires a unique JWT_SECRET with at least 32 characters.")
        if not DATABASE_URL.startswith("postgresql+psycopg://"):
            raise RuntimeError("Production requires a PostgreSQL DATABASE_URL using the psycopg driver.")
        try:
            sslmode = make_url(DATABASE_URL).query.get("sslmode", "")
        except Exception as exc:
            raise RuntimeError("DATABASE_URL is invalid.") from exc
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise RuntimeError("Production DATABASE_URL must specify sslmode=require, verify-ca, or verify-full.")
        if DEMO_MODE or SEED_SCHEMES:
            raise RuntimeError("DEMO_MODE and SEED_SCHEMES must be disabled in production.")
        if not COOKIE_SECURE:
            raise RuntimeError("Production requires COOKIE_SECURE=true behind HTTPS.")
        if not RATE_LIMIT_REDIS_URL:
            raise RuntimeError("Production requires RATE_LIMIT_REDIS_URL for distributed rate limiting.")
        if not RATE_LIMIT_REDIS_URL.startswith("rediss://"):
            raise RuntimeError("Production RATE_LIMIT_REDIS_URL must use TLS (rediss://).")
        if not TRUSTED_HOSTS or "*" in TRUSTED_HOSTS:
            raise RuntimeError("Production requires an explicit TRUSTED_HOSTS allowlist; wildcard hosts are forbidden.")
        if not FORWARDED_ALLOW_IPS.strip() or FORWARDED_ALLOW_IPS.strip() == "*":
            raise RuntimeError("Production requires FORWARDED_ALLOW_IPS to name only trusted reverse proxies.")
        if any(not origin.startswith("https://") for origin in CORS_ORIGINS):
            raise RuntimeError("Production CORS_ORIGINS entries must use HTTPS; leave empty for same-origin deployment.")
        if bool(ADMIN_EMAIL) != bool(ADMIN_PASSWORD):
            raise RuntimeError("Set both ADMIN_EMAIL and ADMIN_PASSWORD to bootstrap an administrator, or leave both unset.")
        if ADMIN_PASSWORD and len(ADMIN_PASSWORD) < 16:
            raise RuntimeError("ADMIN_PASSWORD must contain at least 16 characters.")
