# Scheme Mitra

**Your schemes. Your eligibility. Your next step.**

Scheme Mitra is an independent, farmer-first application for discovering government scheme pathways, seeing deterministic profile-to-rule matches, preparing a self-reported document checklist, and continuing at the official application portal. It is **not** a government portal, does not submit applications, and cannot make an official eligibility or approval decision.

## Current status — read before deployment

This repository is an **in-progress, production-oriented application**, not a verified production service. The application code, API, admin workflow, migrations, tests, and local Docker stack are present, but production readiness is still gated on the environment and checks listed in [Production deployment](#production-deployment-checklist). The production container has not been built here; PostgreSQL/Redis deployment, load testing, independent security/privacy review, and real operations are not verified.

The included three-scheme catalog contains **demo source captures** from official MahaDBT pages checked on **7 October 2026**. Its records are intentionally marked for human review. They must not be treated as a complete catalog, current application-window information, or approved eligibility rules. A profile-fit score is not an eligibility or approval probability.

## What is implemented

- Responsive farmer workspace with English, Marathi, and Hindi UI labels, a clearly marked synthetic demo profile, account registration/sign-in, and sign-out.
- FastAPI JSON API, SQLAlchemy relational models, Alembic migrations, SQLite development mode, and PostgreSQL configuration.
- Argon2 password hashing; signed, HttpOnly session cookies; server-side session revocation; double-submit CSRF checks; role-based administration; request IDs; security headers; and Redis-backed rate limiting in production configuration.
- Deterministic, explainable eligibility checks and profile-fit ranking. Unknown inputs remain unknown; no LLM decides eligibility.
- A grounded, local assistant that uses captured records and can say it cannot verify a fact. It does not require an AI provider or external API.
- Farmer profile, land/crop, saved schemes, checklist states, user-entered application tracker, feedback, and pilot-survey endpoints. No document files or government status are ingested.
- Admin console for source-record maintenance/versioning, human verification, publication by a different account from the verifier, audit logs, usage counts, and explicitly proposed-only pilots.
- A local Postgres + Redis Docker Compose stack; API docs at `/api-docs`; readiness at `/ready`.

## Run locally with Python

Python 3.10+ is recommended (the container uses Python 3.12). From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python run.py
```

Open `http://localhost:8080`. The default development configuration uses a local SQLite database at `backend/data/scheme_mitra_app.sqlite3`, synthetic demo access, and demo scheme records. No `.env` auto-loader is installed; export any environment variables in your shell before launch. To reset local SQLite state, stop the app and run `python scripts/reset_demo.py`.

The demo sign-in is available from the login screen. It uses the synthetic Nashik farmer profile. Do not enter real identity, bank, or sensitive information.

### Create a local administrator

There is no default administrator password. For local testing, start the app with a one-time bootstrap account configured:

```bash
ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='Use-a-long-local-passphrase-2026' python run.py
```

The bootstrap account receives the `SUPER_ADMIN` role. Keep this local-only; do not use shell history or a checked-in `.env` file for real deployment secrets. Open `/admin.html` after signing in with that account. The bootstrap variables are applied at startup, so restart the app with them set if the user does not yet exist. To provision a separate human verifier, have that person register first, then use the audited operator command `python scripts/set_user_role.py --target-email verifier@example.com --actor-email admin@example.com --role DATA_VERIFIER --reason 'Scheme-data reviewer onboarding'`.

## Run the local Docker stack

Docker Compose starts PostgreSQL, Redis, and the app; it applies Alembic migrations before starting the app. Defaults are for a local development stack only:

```bash
docker compose up --build
```

Open `http://localhost:8080`. Compose persists PostgreSQL data in the `postgres_data` volume. Set `ADMIN_EMAIL` and a long `ADMIN_PASSWORD` in an untracked local `.env` file if you need to test administration. Do **not** expose the default Compose passwords/settings to the public internet.

## Production deployment checklist

A production operator must provide and verify all of the following; repository files do not provision these services:

1. A managed PostgreSQL database (`sslmode=require` or certificate-verified) and TLS Redis (`rediss://`) deployment with authentication, network restrictions, automated backups, restore testing, and monitoring.
2. Secret-manager values for a unique `JWT_SECRET` (32+ random characters), database and Redis URLs, and a one-time `ADMIN_EMAIL` / `ADMIN_PASSWORD` bootstrap. Do not use the development defaults.
3. `APP_ENV=production`, `DEMO_MODE=false`, `SEED_SCHEMES=false`, `COOKIE_SECURE=true`, an explicit non-wildcard `TRUSTED_HOSTS`, and `FORWARDED_ALLOW_IPS` containing only the trusted reverse proxy addresses. Set `CORS_ORIGINS` only when a separately hosted trusted UI is needed; same-origin is preferable.
4. HTTPS at the public reverse proxy, correct forwarded-protocol handling, a restrictive firewall, and a review of proxy/IP behavior. Never trust arbitrary client-supplied forwarded headers.
5. Run the database migration as a **single deployment step** before starting application workers:

   ```bash
   python -m alembic upgrade head
   ```

   Then launch `python run.py` or Uvicorn with the environment's trusted-proxy settings. Do not let multiple replicas run migrations concurrently.
6. Bootstrap the first administrator through the protected deployment secret, then remove the bootstrap password from the runtime environment. Review and publish scheme records only after a named human verifier has checked the official source and rules.
7. Recheck `/health` and `/ready`, logs, backups, restore procedures, retention/deletion needs, rate-limit behavior, cookie settings, and incident response. Configure routine cleanup for expired session rows.
8. Complete an independent security/privacy review, penetration test, accessibility review, and Maharashtra scheme-domain/translation review. Do not collect Aadhaar numbers, bank details, or document files until a lawful basis, consent process, encryption/storage design, access controls, and deletion schedule have been approved.

There is no claim of government integration, official approval, a confirmed pilot partnership, or measured farmer impact. Usage counts are product activity only.

## Useful routes

- `GET /health` — liveness response
- `GET /ready` — database readiness response (Redis availability is checked at startup in production)
- `/api-docs` — interactive OpenAPI documentation
- `/api/v1/auth/*` — register, login, demo entry, current session, and logout
- `/api/v1/profile`, `/api/v1/land`, `/api/v1/crops`, `/api/v1/documents` — farmer profile data
- `/api/v1/schemes`, `/api/v1/recommendations`, `/api/v1/eligibility/*` — deterministic discovery and matching
- `/api/v1/saved`, `/api/v1/applications`, `/api/v1/assistant/question`, `/api/v1/pilot-*` — farmer workflows
- `/api/v1/admin/*` — role-protected source governance and admin operations

See [API reference](docs/API.md), [architecture](docs/ARCHITECTURE.md), [data verification rules](docs/DATA_VERIFICATION.md), and [deployment guide](docs/DEPLOYMENT.md).

## Tests and known gaps

Run the checks with:

```bash
pytest -q
python -m alembic current
node --check frontend/app.js
node --check frontend/admin.js
```

Tests exercise the deterministic engine, authentication/CSRF/session revocation, role boundaries, and the scheme review-to-publish workflow using isolated SQLite databases. The migration has been applied to local SQLite, but a live PostgreSQL migration, Docker build/Compose run, browser end-to-end session, load test, and external security audit have not been verified in this workspace. See [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md) for the exact scope and limitations.
