# ✅ Definition of Done (DoD) — Story → Sprint → Quarter → Half‑Year → Year

This DoD is written for **Product Owner + Engineering** and checked by **Product Manager** for release readiness.

---

## Definition of Ready (DoR) (Recommended)

A backlog item is “ready” when:
- **Problem and user value are clear**
- **Acceptance criteria are testable**
- **Dependencies identified** (services, teams, external libs)
- **Non-functional needs declared** (performance, security, accessibility) if relevant
- **Demo script exists** (what will be shown at sprint review)

---

## DoD: Backlog Item / PBI / User Story

A story is “done” when:
- **Acceptance criteria met** (as written by PO; verified in review/demo)
- **Tests added/updated** (unit/integration where appropriate)
- **Docs updated** (user flow or service doc if impacted; at least notes in PR)
- **No known critical bugs** introduced
- **Observability hooks** added when relevant (logs/metrics/traces)
- **Security basics applied**
  - input validation, no secrets in code, least-privilege where applicable

---

## DoD: Sprint

A sprint is “done” when:
- **Sprint goal achieved** (or explicitly renegotiated and documented)
- **Increment is usable** (not just code merged; feature works end-to-end in the target environment)
- **Regression risk is managed**
  - key flows tested (manual or automated)
- **Docs and changelog updated**
  - at minimum: what changed + known limitations
- **Operational readiness**
  - error handling reviewed, key logs exist, dashboards updated if available

Sprint artifacts (minimum):
- Sprint goal statement
- Demo recording or demo notes
- Completed/rolled-over items list + rationale

---

## DoD: Quarterly (Quarter)

A quarter is “done” when:
- **Quarterly outcome delivered**
  - users can perceive the change (not purely internal refactors)
- **Success metrics reviewed**
  - baseline → current comparison and interpretation
- **Quality baseline improved**
  - fewer defects, faster cycle time, improved reliability signals
- **Roadmap updated**
  - learnings incorporated; next quarter re-planned
- **Risk register reviewed**
  - top risks mitigated or re-scoped

Evidence (minimum):
- Quarterly release notes
- Metric snapshot (even if approximate)
- “What we learned” summary and plan adjustment

---

## DoD: Half-Year (H1 / H2)

A half-year is “done” when:
- **Major product capability set is complete**
  - H1: decisioning + trust foundation
  - H2: scale/quality/growth + hardening (per roadmap)
- **Platform maturity step-change**
  - meaningful improvements in testing, delivery automation, and observability
- **Architecture health check**
  - service boundaries still make sense; technical debt assessed and prioritized
- **Security posture reviewed**
  - top threats addressed; secrets/headers/validation posture improved

Evidence:
- Capability checklist completion (mapped to epics)
- Reliability/quality trend review
- Security checklist status

---

## DoD: Year

A year is “done” when:
- **Product is production-grade**
  - stable releases, known-operable platform, security baseline, documented runbooks
- **Roadmap outcomes achieved**
  - major epics completed or explicitly descoped with rationale
- **Business/product narrative is clear**
  - what the product is, who it serves, why it wins, and what’s next
- **Maintainability is demonstrated**
  - new contributors can onboard using docs; key systems are observable and testable

Evidence:
- Annual product review (vision → outcomes → metrics)
- System readiness checklist (security/observability/testing/CI/CD)
- Updated documentation map and roadmap

