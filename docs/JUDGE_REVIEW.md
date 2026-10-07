# Honest product and readiness review

## Product case

- Focused farmer problem: turning a farm profile into a few explainable scheme pathways, a checklist of what to confirm, and an official next step.
- Intended journey: sign in/demo → complete farm profile → see deterministic profile-fit results → open source-backed conditions → prepare a self-reported checklist → continue to MahaDBT → optionally record personal progress.
- Guardrails: no fabricated submission, approval, department partnership, live application status, or impact claim. Unknown eligibility information stays unknown.
- The local demo does not require external APIs, scraping, or an AI provider.

## Readiness today

The earlier MVP has been expanded with FastAPI/SQLAlchemy, cookie authentication, role checks, a revocable server-side session, CSRF controls, Redis rate limiting configuration, Alembic migrations, an admin source-review/publish workflow, audit logs, and a local Postgres/Redis Compose stack. Local checks cover the deterministic engine, core auth/security behavior, role boundaries, and scheme review→publish workflow.

**This is still not a production-ready or field-validated service.** PostgreSQL/Redis/Docker were not executed in this workspace; there is no browser E2E or independent security/privacy review; operational hosting, account recovery/MFA, deletion/export, retention cleanup, verified scheme content, field evidence, and accessibility/load testing remain open.

## Product risks and questions

- **Problem validation:** no real farmer interview, baseline, or task-time evidence has been supplied. The synthetic Niphad profile is not research evidence.
- **Catalog scope:** only three captured summaries are present, not a complete or continuously updated catalog. Their status is `DEMO_SOURCE_CAPTURED_NEEDS_HUMAN_SIGNOFF`.
- **Government authority:** MahaDBT is authoritative. There is no live API, official approval, or department partnership.
- **Rules and language:** match weights are relevance heuristics; rule explanations and Marathi/Hindi scheme text need subject-matter and professional language review.
- **Accessibility/digital inclusion:** test with farmers with different literacy, disability, device, network, and assisted-service needs.
- **Privacy/security:** never collect Aadhaar numbers, bank details, or actual document files until lawful basis, consent, storage, access, deletion, and breach processes are approved.
- **Sustainability:** unit cost, support model, update staffing, and a pilot owner are unknown.

## Questions to answer with evidence

1. What field evidence proves the problem is frequent and costly in the target taluka?
2. Why is this clearer or more useful than MahaDBT/myScheme's existing search journey?
3. Which part improves user outcomes: understanding, document readiness, assisted onboarding, or task completion?
4. Who has agreed to review scheme data or test the tool? No such partnership is currently claimed.
5. Who checks source changes, and what is the correction/withdrawal SLA?
6. How does someone without a smartphone, data plan, or written Marathi use the service?
7. How will the team measure completion/comprehension without confusing clicks with benefits?
8. What is the cost per assisted user and who funds ongoing scheme-data maintenance?

## Evidence not to fabricate

- `[INSERT ACTUAL SURVEY RESULT]` problem frequency and current farmer journey.
- `[INSERT ACTUAL BASELINE]` task time, relevant schemes known, documents identified, next-step confidence.
- `[INSERT ACTUAL USABILITY RESULT]` completion, comprehension, relevance, and accessibility findings.
- `[INSERT ACTUAL PILOT RESULT]` outcomes collected with consent and an explicit denominator/method.
- `[INSERT VERIFIED SOURCE AND REVIEWER]` current rules, component windows, and human sign-off.
- `[INSERT ACTUAL COST]` support, translation, hosting, outreach, and maintenance costs.

## Next recommended work

1. Interview farmers and local agriculture facilitators; document consent, recruitment, current search path, confusion, and task time.
2. Have a Maharashtra scheme-domain reviewer validate each captured official page, translation, condition, benefit summary, and next step.
3. Observe usability in Marathi and test comprehension of “profile match ≠ eligibility/approval”.
4. Define a small proposed pilot with named owner, sampling plan, accessible alternatives, baseline/post-use method, support, cost, and success criteria.
5. Complete browser E2E, PostgreSQL/Redis, Docker, accessibility, security, privacy, deployment/restore, and load tests before real onboarding.
