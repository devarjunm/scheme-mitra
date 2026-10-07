# Source capture and data-verification controls

## Source policy

The demo only seeds summaries from official Maharashtra MahaDBT farmer scheme pages. The linked official page, not this application, is authoritative. Each record carries a source name, source URL, source-check date (`2026-10-07`), and a conspicuous status:

`DEMO_SOURCE_CAPTURED_NEEDS_HUMAN_SIGNOFF`

This status means the relevant public page was read and structured for a demo; it does **not** claim government endorsement, department verification, or production-ready rule validation. Before a pilot, a named agriculture-domain verifier should review the original page and benefit PDF, rule translations, document timing, applicability to the pilot region, and any current-year changes. Store verifier, timestamp, page/version snapshot, and reason for every correction.

## Seeded official pages

1. **PMKSY — Per Drop More Crop (Micro-irrigation Component)** — MahaDBT page, including its stated 55% assistance share for small/marginal farmers and 45% for other farmers, eligibility summary, listed area limit, repeat-benefit condition, pump-connection condition, and document list. [Official MahaDBT page](https://mahadbt.maharashtra.gov.in/Farmer/SchemeData/SchemeData?str=E9DDFA703C38E51AC7B56240D6D84F28)
2. **Mission for Integrated Development of Horticulture (MIDH)** — MahaDBT page listing horticulture components, horticulture-crop condition, document list, and onion-storage infrastructure among the post-harvest items. No component-specific amount is shown in the demo. [Official MahaDBT page](https://mahadbt.maharashtra.gov.in/Farmer/SchemeData/SchemeData?str=E9DDFA703C38E51AF823840F3424F82E)
3. **State Agriculture Mechanization Scheme** — MahaDBT page listing machinery/implements and eligibility/document notes. Item-specific benefit values are not copied into the demo. [Official MahaDBT page](https://mahadbt.maharashtra.gov.in/Farmer/SchemeData/SchemeData?str=E9DDFA703C38E51A147B39AD4D6A9082)

Official application portal link: [MahaDBT Farmer Portal](https://mahadbt.maharashtra.gov.in/Farmer/Login/Login).

## Safety rules in the MVP

- No scheme, benefit amount, deadline, department owner, or application link is fabricated.
- Unknown eligibility facts remain `unknown`; the engine does not infer them from crop, land size, or AI text.
- The system never labels a person `eligible` or `approved`. Its statuses are `Potential fit — confirm conditions` and `More information needed`.
- The 0–100 value is called **Profile match** and measures overlap with available profile signals; it is not an approval probability.
- For the PMKSY area condition, an entered area above the page's stated area limit becomes `review`, not an automatic rejection, because the captured text describes a benefit limit and may be applied to a component/plot.
- Scheme-specific history, selected activity, power-pump conditions, and component eligibility can remain unknown.
- Document checklist states are self-reported; no scans or files are accepted/validated. The app does not ask for identity numbers as structured fields, but free-text notes could still contain sensitive data; use only synthetic/test details.
- The application tracker uses `User-entered status`, never `Official status`.
- The assistant only uses local record text and official source links. It does not decide rules or answer beyond the captured summary.
- The demo works without third-party AI or government APIs.

## Human review queue before pilot

For every scheme, a reviewer must confirm:

- current scheme name/status and component availability;
- exact eligibility language, exceptions, and geographic conditions;
- current benefit schedule/percentages and annual limits;
- prior-benefit and application-window rules;
- required documents and when each is needed;
- language quality in Marathi and Hindi;
- official portal URL and operational instructions.

Until that review is signed off, keep the record out of a real farmer-facing deployment.
