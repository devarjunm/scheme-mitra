from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .. import models  # noqa: F401 — register metadata tables
from ..config import APP_ENV, CORS_ORIGINS, COOKIE_SECURE, DEMO_MODE, RATE_LIMIT_REDIS_URL, ROOT, TRUSTED_HOSTS, validate_runtime_config
from ..db import Base, SessionLocal, engine
from ..seed import seed_initial_data
from ..security import csrf_from_request
from . import admin, auth, farmer, schemes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("scheme_mitra.api")
FRONTEND = ROOT / "frontend"
DOCS_ROOT = (ROOT / "docs").resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_config()
    if APP_ENV != "production":
        Base.metadata.create_all(bind=engine)
    # In production the container entrypoint runs Alembic first; this seeds only
    # explicitly configured bootstrap accounts or approved demo data.
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
        seed_initial_data(db)
    app.state.redis = None
    if RATE_LIMIT_REDIS_URL:
        client = Redis.from_url(RATE_LIMIT_REDIS_URL, encoding="utf-8", decode_responses=True, socket_connect_timeout=2)
        try:
            await client.ping()
            app.state.redis = client
        except Exception:
            await client.aclose()
            if APP_ENV == "production":
                raise RuntimeError("Rate-limit Redis is unavailable; refusing to start in production.")
            logger.warning("Redis unavailable; development uses an in-process rate limiter.")
    elif APP_ENV == "production":
        raise RuntimeError("Production requires Redis-backed rate limiting.")
    app.state.local_rate = defaultdict(list)
    yield
    if app.state.redis is not None:
        await app.state.redis.aclose()


app = FastAPI(
    title="Scheme Mitra API",
    summary="Farmer-first government scheme discovery and action guidance.",
    description="Eligibility results are deterministic guidance, never a government approval or approval-probability estimate.",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.include_router(auth.router)
app.include_router(farmer.router)
app.include_router(schemes.router)
app.include_router(admin.router)

if TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)
if CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
                       allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                       allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID"])


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
    code = {401:"UNAUTHENTICATED",403:"FORBIDDEN",404:"NOT_FOUND",409:"CONFLICT",413:"PAYLOAD_TOO_LARGE",422:"VALIDATION_ERROR",429:"RATE_LIMITED",503:"SERVICE_UNAVAILABLE"}.get(exc.status_code, "REQUEST_ERROR")
    return JSONResponse({"error": {"code": code, "message": detail}}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    issues = []
    for item in exc.errors()[:8]:
        location = ".".join(str(part) for part in item.get("loc", []) if part != "body")
        issues.append({"field": location, "message": item.get("msg", "Invalid value.")})
    return JSONResponse({"error": {"code": "VALIDATION_ERROR", "message": "Please check the submitted fields.", "fields": issues}}, status_code=422)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("Database constraint conflict request_id=%s", getattr(request.state, "request_id", ""))
    return JSONResponse({"error": {"code": "DATA_CONFLICT", "message": "This record conflicts with existing data."}}, status_code=409)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database failure request_id=%s", getattr(request.state, "request_id", ""))
    return JSONResponse({"error": {"code": "DATABASE_ERROR", "message": "The service could not save or retrieve data. Please retry."}}, status_code=503)


@app.middleware("http")
async def request_security_and_observability(request: Request, call_next):
    supplied_id = re.sub(r"[^A-Za-z0-9._:-]", "", request.headers.get("X-Request-ID", ""))[:80]
    request_id = supplied_id or str(uuid4())
    request.state.request_id = request_id
    path = request.url.path
    method = request.method.upper()
    if path.startswith("/api/v1/"):
        try:
            csrf_from_request(request)
        except HTTPException as exc:
            return JSONResponse({"error": {"code": "CSRF_FAILED", "message": str(exc.detail)}}, status_code=exc.status_code)
        # Distributed per-IP limit in production; in-process fallback is development-only.
        now = time.time()
        window = 60
        limit = 300 if method in {"GET", "HEAD"} else 120
        bucket = "read" if method in {"GET", "HEAD"} else "write"
        if path in {"/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/demo"}:
            limit, bucket = 8, "auth"
        elif path == "/api/v1/assistant/question":
            limit, bucket = 30, "assistant"
        client_ip = request.client.host if request.client else "unknown"
        limiter = getattr(request.app.state, "redis", None)
        try:
            if limiter is not None:
                key = f"scheme-mitra:rl:{client_ip}:{bucket}:{int(now // window)}"
                count = await limiter.incr(key)
                if count == 1:
                    await limiter.expire(key, window + 2)
            else:
                local = request.app.state.local_rate
                key = f"{client_ip}:{bucket}:{int(now // window)}"
                entries = [stamp for stamp in local[key] if now - stamp < window]
                entries.append(now)
                local[key] = entries
                count = len(entries)
            if count > limit:
                return JSONResponse({"error": {"code": "RATE_LIMITED", "message": "Too many requests. Please wait and try again."}}, status_code=429, headers={"Retry-After":"60"})
        except Exception:
            if APP_ENV == "production":
                logger.exception("Rate limit store unavailable request_id=%s", request_id)
                return JSONResponse({"error": {"code": "RATE_LIMIT_UNAVAILABLE", "message": "The service is temporarily unavailable."}}, status_code=503)
            logger.exception("Development rate limiter error request_id=%s", request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request failure request_id=%s method=%s path=%s", request_id, method, path)
        return JSONResponse({"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred. Please retry."}}, status_code=500)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if path.startswith("/api/") else "no-cache"
    if path.startswith("/api/") or path.startswith("/"):
        frame = "'none'" if APP_ENV == "production" else "*"
        response.headers["Content-Security-Policy"] = f"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors {frame}"
    if APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%s", request_id, method, path, response.status_code, elapsed_ms)
    return response


@app.get("/health", tags=["operations"])
def health():
    return {"status":"ok", "service":"scheme-mitra", "mode":"demo" if DEMO_MODE else APP_ENV}


@app.get("/ready", tags=["operations"])
def ready():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status":"ready", "database":"ok", "rate_limiter":"configured" if (RATE_LIMIT_REDIS_URL or APP_ENV != "production") else "not_configured"}


@app.get("/docs/{path:path}", include_in_schema=False)
def project_docs(path: str):
    candidate = (DOCS_ROOT / path).resolve()
    if DOCS_ROOT not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Documentation file not found.")
    return FileResponse(candidate, media_type="text/markdown; charset=utf-8")


# Static browser app is same-origin, avoiding browser calls to localhost or cross-origin APIs.
app.mount("/", StaticFiles(directory=str(FRONTEND), html=True, check_dir=True), name="frontend")
