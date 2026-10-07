# Architecture

## Runtime

```text
Browser (same origin)
   ├─ frontend/index.html + app.js + styles.css (farmer workspace)
   └─ frontend/admin.html + admin.js + admin.css (role-gated console)
                │ JSON + HttpOnly session cookie + CSRF header
                ▼
FastAPI (backend/api/main.py)
   ├─ Authentication, validation, CSRF, request IDs, headers, rate limits
   ├─ Farmer profile and scheme/action API routers
   ├─ Role-protected administration router
   └─ Grounded local assistant and deterministic recommendation services
                │ SQLAlchemy
                ▼
PostgreSQL in production / SQLite in local development
                │
                └─ Redis rate-limit counters in production
```

The app is same-origin by default. The browser does not call `localhost` to reach an API. The local Compose stack includes PostgreSQL and Redis; Python development defaults to SQLite.

## Trust boundaries and core decisions

- **Eligibility:** deterministic Python rules consume profile values and the versioned source-capture fields. No LLM participates in eligibility or approval prediction. Missing facts remain unknown.
- **Assistant:** answer templates are grounded in captured local source summaries or the user's own profile and return official source links. It degrades without an AI provider or network access.
- **Data governance:** scheme records have workflow status, verification status, versioned snapshots, source URL/name, check date, verifier, and audit history. New/edited records return to review; verifying and publishing are separate actions, and the API blocks the recorded verifier from publishing that same version. Demo seed data is not implicitly human-verified.
- **Identity:** Argon2 hashes passwords. Signed cookies are HttpOnly; a CSRF double-submit token protects unsafe cookie-authenticated requests. The JWT `jti` is stored server-side and revoked on logout. Roles are read from the database, not trusted from a client-provided role field.
- **Privacy:** there are no structured Aadhaar/bank fields or document blobs. Account email and farmer profile data are personal data; free-text notes/comments could still contain sensitive details, so the UI warning is not a data-loss-prevention control. Appropriate access, retention, deletion, consent, and operational safeguards are still required.
- **Observability:** request IDs, structured logs, health/readiness, audit logs, and minimized allow-listed product events. Product analytics are not evidence of farmer impact.

## Main modules

- `backend/api/main.py`: FastAPI app lifecycle, error envelopes, CSRF/rate/security middleware, static frontend, health/readiness.
- `backend/api/auth.py`, `backend/security.py`, `backend/dependencies.py`: account/session/role controls.
- `backend/api/farmer.py`: farmer-owned profile, land/crop, checklist, notifications.
- `backend/api/schemes.py`: scheme discovery, matching, saved records, manual tracker, assistant, feedback, survey metrics.
- `backend/api/admin.py`: source catalog, review/publish/archive, audit, usage counts, proposed pilots.
- `backend/eligibility.py`, `backend/services/recommendations.py`: deterministic rule engine and profile-fit results.
- `backend/models.py`, `backend/db.py`, `migrations/`: relational persistence and schema upgrades.
- `frontend/`: browser client. `admin.html` is not a security boundary; API role checks are authoritative.

## Production design still to validate

The system is not yet production-certified. PostgreSQL/Redis deployment behavior, reverse-proxy header trust, cookie deployment, concurrency, backup/restore, retention cleanup, account deletion/export, email verification/password reset, privileged MFA, accessibility, privacy/legal obligations, and independent security testing remain deployment work. See [deployment runbook](DEPLOYMENT.md) and [security review](SECURITY_REVIEW.md).
