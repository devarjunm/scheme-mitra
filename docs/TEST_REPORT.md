# Test report

**Run date:** 2026-10-07 (workspace local time)  
**Status:** local development checks only; not a production sign-off.

## Checks performed

- `pytest -q` — **17 passed** across API security/auth, production-config validation, deterministic eligibility, and grounded-assistant (including localized Marathi explanation) tests. One Starlette/httpx TestClient deprecation warning was emitted by the installed dependency combination.
- `python -m unittest discover -s backend -p 'test_*.py' -v` — **11 passed** for the original deterministic-engine/assistant unittest set (run before the API-security pytest was added).
- `python -m alembic upgrade head` — successful against the local SQLite development database. `python -m alembic current` and `heads` both report `50b8aeed071b`.
- Fresh SQLite migration chain — both revisions applied successfully to a new temporary database.
- PostgreSQL offline Alembic SQL generation — produced DDL for both revisions under the PostgreSQL dialect; this did not connect to or execute against a live PostgreSQL server.
- `python -m py_compile backend/*.py backend/api/*.py backend/services/*.py backend/test_*.py scripts/*.py` — passed after the current backend changes.
- `node --check frontend/app.js` and `node --check frontend/admin.js` — passed after the current frontend changes.
- FastAPI `TestClient` smoke — `/health`, `/ready`, auth/demo, profile, scheme list, admin static assets, admin overview/analytics/audit/pilot routes, and create→verify→publish workflow returned expected local responses. CSRF-free authenticated writes returned 403 in the smoke test as intended.

## Not tested / limitations

- No real PostgreSQL server was available. PostgreSQL SQL generation was checked offline, but actual migration execution, database constraints, connection TLS, and runtime queries remain unverified; migrations were applied on SQLite only.
- No Docker executable was available, so the Docker image build and Compose stack were not run.
- No actual browser/device E2E, UI accessibility audit, performance/load/soak test, chaos/failover test, backup restore, TLS/proxy integration, or multi-worker test.
- No external security/privacy assessment, penetration test, dependency scan, or real farmer pilot.
- Test cases use synthetic data; they do not validate the correctness or currency of any government scheme rule.

A successful local check does not prove production safety, eligibility correctness, service availability, or farmer impact. See [security review](SECURITY_REVIEW.md) and [deployment runbook](DEPLOYMENT.md).
