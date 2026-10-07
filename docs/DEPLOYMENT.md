# Deployment runbook (draft)

This runbook describes a production-oriented deployment sequence. It is not a certification that the code or a chosen provider is production-ready. The local `docker-compose.yml` intentionally sets development mode, permits a demo farmer, seeds demo data, and uses local credentials. **Never expose that Compose stack as a production deployment.**

## Required services

- Python application container built from the repository `Dockerfile`.
- Managed PostgreSQL reachable only from the application and migration runner.
- Authenticated Redis reachable only from the application for shared rate limiting.
- HTTPS reverse proxy/load balancer with a restricted, documented forwarded-header trust boundary.
- Secret manager, centralized redacted logs, alerting, encrypted backups, and a verified restore procedure.

No document object store is used: the app deliberately does not accept document files.

## Configuration

Use the environment variables in `backend/config.py`. Production startup fails closed unless the secret, PostgreSQL URL, secure cookie, Redis, and deployment allowlists are configured.

Minimum production choices:

```text
APP_ENV=production
DATABASE_URL=postgresql+psycopg://<user>:<password>@<private-host>:5432/<database>?sslmode=verify-full
JWT_SECRET=<unique random secret, at least 32 characters>
COOKIE_SECURE=true
COOKIE_SAMESITE=strict
DEMO_MODE=false
SEED_SCHEMES=false
RATE_LIMIT_REDIS_URL=rediss://:<secret>@<private-redis-host>:<port>/<db>
TRUSTED_HOSTS=app.example.gov.in
FORWARDED_ALLOW_IPS=<exact trusted proxy IPs>
CORS_ORIGINS=
ADMIN_EMAIL=<first named administrator email>
ADMIN_PASSWORD=<one-time password, at least 16 characters>
```

Use provider-specific TLS and certificate options for PostgreSQL/Redis URLs. URL-encode special characters in credentials. `CORS_ORIGINS` can remain empty for a same-origin frontend; if set, each origin must be an explicit HTTPS origin. `TRUSTED_HOSTS` must be an explicit host list, not `*`. `FORWARDED_ALLOW_IPS` must identify only the proxy hops Uvicorn should trust. Do not copy development defaults from `.env.example` or `docker-compose.yml`.

At startup, `ADMIN_EMAIL`/`ADMIN_PASSWORD` create or promote a `SUPER_ADMIN`; remove the password from runtime configuration once the initial account is bootstrapped. Keep the database record and use normal account password reset/rotation procedures (a self-service password reset flow is not currently implemented). Do not use a shared admin account. A second reviewer must register a normal account and be identity-verified through the organization's approved out-of-band process (the app does not verify email), then a super-admin operator can assign `DATA_VERIFIER` through `python scripts/set_user_role.py --target-email <reviewer-email> --actor-email <super-admin-email> --role DATA_VERIFIER --reason '<auditable reason>'`; the CLI checks the actor role and writes an audit entry.

## Release sequence

1. Build and scan an immutable container image from a reviewed commit. Run the test suite and dependency/security scans in CI.
2. Provision and validate database, Redis, secret-manager access, backup retention, network ACLs, HTTPS, and proxy header behavior.
3. Run `python -m alembic upgrade head` once as a release/migration job, using the same image and database secret. Review migration SQL and take a recoverable backup before destructive changes. Do not run migrations from every app replica.
4. Start the app with `python run.py` for a single worker, or run Uvicorn directly with the provider-specific trusted proxy list and an intentionally sized worker count. Ensure the reverse proxy only accepts public traffic and strips/replaces incoming `X-Forwarded-*` headers.
5. Verify `/health`, `/ready`, HTTPS redirects/cookies, CSRF rejection, the authenticated farmer journey, role boundaries, rate limits, and audit writes from the deployed origin.
6. Sign in as the named super-admin; create/import official scheme records. A human verifier account must review each source/rule version; the API enforces that a different account publishes that version. A published record becomes farmer-visible; it is still guidance, not an official government decision.
7. Remove bootstrap credentials, confirm admin MFA/identity policy at the infrastructure layer, and set an operations owner for incident response, security patching, data access, backups, and retention.

## Operations and unresolved work

- Monitor application errors, database pool saturation, Redis availability, authentication failures, rate-limit rejections, and backup/restore results. Logs should not capture passwords, cookies, raw documents, Aadhaar/bank data, or full submitted profile bodies.
- Expired session rows are not automatically purged by the web process. Schedule and monitor `python scripts/cleanup_expired_sessions.py --retention-days 30` (or a reviewed retention value); choose the retention period with security/privacy owners and test it against audit/incident needs.
- Implement a reviewed account deletion/export workflow, email verification/password reset, MFA or an approved identity provider for privileged roles, security event alerting, and formal data-retention controls before onboarding real farmers.
- Keep the official-scheme allow-list, source capture, translation, and deterministic rule version under named human review. Check current official application status/window manually; there is no live feed.
- Complete threat modeling, privacy assessment under applicable law, accessibility testing, penetration testing, load/soak testing, disaster recovery, and pilot evaluation before calling a release production-ready.

## Rollback

Use an expand/contract migration strategy. Back up before upgrade; test restoring that backup to an isolated environment. Prefer rolling back the app image while keeping backward-compatible schema changes. Do not run an Alembic downgrade against production as an emergency action unless the rollback is explicitly reviewed and data-loss implications are understood.
