# Security review — implementation notes and open work

**Status: internal implementation review only. Not a penetration test, legal opinion, or production approval.** The code has basic controls, but the absence of an independent review and deployment evidence means Scheme Mitra must not be described as production-certified.

## Implemented in this repository

- Password hashes use Argon2id through `argon2-cffi`; plaintext passwords are not stored.
- Access tokens use a signed JWT in an HttpOnly cookie; no access token is stored in browser local storage. Session `jti` values are stored in `auth_sessions`; logout revokes the database session, which is checked on authenticated requests.
- Authenticated unsafe API requests require a double-submit CSRF token; login, registration, and demo bootstrap are unauthenticated bootstrap actions.
- Registration enforces a 12-character minimum plus alphabetic/numeric characters. Login responses do not disclose whether an email exists.
- Role checks are enforced in API dependencies. Farmer accounts cannot access admin endpoints; verifier sign-off and publication are separate actions.
- Production configuration fails closed without a non-development JWT secret, PostgreSQL URL, secure cookies, Redis rate-limit URL, explicit trusted hosts, and non-wildcard trusted proxy settings.
- Production rate limiting uses Redis counters. Local in-process limiting is development-only.
- Request IDs are sanitized; errors are returned in generic envelopes; API responses do not expose exception traces. Common security headers and a restrictive CSP are set.
- Source URLs are HTTPS and checked against an allow-list; admin audit/version data stores workflow actions.
- Analytics is allow-listed and metadata is minimized. No Aadhaar number, bank data, uploaded files, or official application status is requested or stored by design.

## Important limitations and required controls

1. **No external test.** No penetration test, threat-model workshop, load/soak test, dependency audit, or independent code review has been completed.
2. **Account assurance.** There is no email verification, account recovery/password reset, MFA, or privileged identity provider. Admin credentials are bootstrapped from environment variables; use a secrets manager and remove the bootstrap secret after first use. Enforce MFA at an approved identity layer before privileged use.
3. **Privacy operations.** Email and farmer profile data are personal data. No in-product consent ledger, export/deletion workflow, retention policy enforcement, or automated expired-session cleanup exists yet. Do not onboard real farmers until these controls and applicable-law review are complete.
4. **Transport/deployment.** HTTPS termination, trusted proxy addresses, forwarded-header replacement, TLS to managed PostgreSQL/Redis, network ACLs, WAF, backups, restore drills, and secret rotation depend on infrastructure not supplied here. `docker-compose.yml` is development only.
5. **Sessions.** Signed JWT expiry is bounded; logout revokes the session. Stolen active cookies remain usable until logout/expiry. Add incident-driven global session revocation and periodic expiry cleanup before long-lived production use. User deactivation is checked on each request.
6. **Rate limiting.** Limits are simple per-IP/path minute counters, not adaptive abuse detection. Verify client-IP behavior behind the actual reverse proxy and add monitoring/alerts. Do not set `FORWARDED_ALLOW_IPS=*`.
7. **Data governance.** Source captures require human verification and rechecking. The UI's status is not proof that government rules are current. Prevent publication until the independent source/reviewer process is defined and audited.
8. **Frontend.** API authorization is authoritative; the admin page's hidden/visible controls are not security controls. Continue escaping dynamic content and reviewing any new HTML sinks.
9. **Data sensitivity.** Structured Aadhaar/bank fields and file uploads are not implemented, but free-text notes/comments could still contain sensitive details; the UI warning is not a DLP control. Never submit real Aadhaar/bank information or upload real documents. If those data are ever needed, redesign storage, encryption, access, consent, retention, breach response, and deletion first.

## Deployment gates

Before production use, attach evidence for: configured secret manager, isolated production network, HTTPS and proxy validation, PostgreSQL/Redis TLS/auth, migration and restore tests, CSRF/session and role tests against the deployed origin, rate-limit tests, scan results, external penetration test, privacy assessment, accessibility review, alerting/incident runbook, and named ownership for the official scheme catalog.
