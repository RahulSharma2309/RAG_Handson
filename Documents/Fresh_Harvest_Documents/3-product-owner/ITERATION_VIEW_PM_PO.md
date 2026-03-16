# 🔁 Iteration View (PM/PO) — “How the Product Looks” Each Sprint

This document describes **what changes for users** each sprint, and what PM/PO should validate in demos.

It’s aligned to `docs/ITERATION_CHECKLIST.md` (sprints 1–35) and `docs/PROJECT_ROADMAP.md` (epics/PBIs).

---

## Sprint 0 (Completed): MVP Baseline ✅

**What users can do**
- Register/login, browse products, add to cart, checkout with wallet, view orders.

**PM validation**
- Core funnel exists end-to-end.

**PO validation**
- Basic acceptance criteria met; flows documented in `docs/Functionality/`.

---

## Sprint-by-Sprint Summary (Sprints 1–35)

> Each row is intentionally short. Use this as a *planning + demo checklist*, not a PRD.

| Sprint | Theme | Product “looks like” (user-visible) | PM focus | PO focus |
|---|---|---|---|---|
| 1 | Categories | Products organized into electronics categories; basic filtering starts | Discovery clarity | Type system + endpoints |
| 2 | Variants | Variant selection (color/storage/etc.), SKU behavior, variant stock/pricing | Decision confidence | Variant rules + AC |
| 3 | Pricing + Specs | Visible discounts + consistent price calc; specs displayed | Trust in pricing | Pricing strategies |
| 4 | Media + Search | Product gallery; search/filter/sort/pagination usable | Findability | Search perf + UX |
| 5 | Inventory + Reviews | Inventory signals; reviews/ratings start building trust | Trust signals | Review rules |
| 6 | Wishlist + Compare | Wishlist; comparison for similar items | Retention | Constraints + UX |
| 7 | Order lifecycle | Clear order states and transitions | Post‑purchase trust | State machine rules |
| 8 | Cancel/Modify | Cancellation + refunds; modification rules where allowed | Reduced anxiety | Compensations + UI |
| 9 | Reliability + Invoice | Saga reliability improvements; invoices (download/email) | Confidence | Idempotency + docs |
| 10 | Multi-payments | Choose payment method; clear failure/retry messaging | Conversion | Adapter interfaces |
| 11 | Coupons + Retry | Promo codes; payment retry robustness | Growth lever | Validation rules |
| 12 | React Query | Faster UI; caching; less loading flicker | UX polish | API contracts stable |
| 13 | Global state + Forms | Better forms and state; fewer UI bugs | Fewer drop-offs | Validation/DoD |
| 14 | PWA + A11y | More accessible and installable experience | Inclusivity | WCAG checks |
| 15 | Errors + Micro-UX | Better error boundaries; refined micro-interactions | Trust | Edge cases |
| 16 | Storybook + Perf | Consistent UI components; performance gains | Quality | Perf budgets |
| 17 | Backend tests | Fewer regressions; more stable releases | Confidence | Coverage targets |
| 18 | Integration + E2E | End-to-end reliability in CI (user journeys) | Predictability | Test matrices |
| 19 | CI basics | Automated builds/tests; visible status | Delivery speed | Quality gates defined |
| 20 | Versioning/Quality | Release discipline; quality reports | Governance | Conventional commits |
| 21 | K8s setup | Deployable environment becomes repeatable | Operability | Runbooks begin |
| 22 | Helm + Ingress | Easier deploy/rollback; stable routing | Time-to-restore | Config hygiene |
| 23 | Storage + Scaling | Persistence and HPA patterns | Resilience | Capacity signals |
| 24 | Mesh/GitOps (opt) | Optional advanced ops | Risk mgmt | Decide scope |
| 25 | Logging | Better diagnostics; correlation IDs | Faster triage | Sensitive data rules |
| 26 | Metrics/Dashboards | Product + system health visible | Proactive ops | SLO framing |
| 27 | Tracing | Cross-service latency visibility | Performance | Trace coverage |
| 28 | Notifications | Confirmation + updates; user trust grows | Retention | Template rules |
| 29 | Recommendations | “Also bought” style discovery | Conversion | Evaluation metrics |
| 30–31 | Admin | Admin can manage products/prices/inventory | Scale | RBAC + audit |
| 32 | Advanced search + realtime | Better search; live updates (optional) | Differentiation | Rollout safety |
| 33 | Caching + rate limit | Faster + safer APIs | Stability | Cache invalidation |
| 34 | Security hardening | Headers, validation, secrets mgmt | Risk reduction | Security DoD |
| 35 | Security testing | Scans + fixes + re-scan | Compliance posture | Evidence captured |

---

## Detailed “Product Look & Feel” Narratives (Q1–Q2)

### Sprint 1: Categories & Type System
**What users experience**
- Browsing feels like an electronics store (clear categories and browsing structure).

**PM success criteria**
- Discovery clarity improves (users can find relevant categories quickly).

**PO acceptance focus**
- Category/type model is consistent across API + DB + UI; filtering endpoints exist.

**Demo script**
- Show category navigation → filter results → view a product detail.

### Sprint 2: Variant Selection
**What users experience**
- Users can select variants (e.g., storage/color) and see correct price/stock behavior.

**PM success criteria**
- Higher decision confidence; fewer “which one am I buying?” moments.

**PO acceptance focus**
- Variant rules, SKU logic, and stock rules are testable and documented.

**Demo script**
- Open product → switch variants → show price and availability changes → add to cart.

### Sprint 3: Pricing + Specs
**What users experience**
- Discounts are displayed transparently; product specs are visible and structured.

**PM success criteria**
- Users trust pricing and can compare options faster.

**PO acceptance focus**
- Pricing strategy behavior is deterministic; specs have a stable schema.

**Demo script**
- Show a discounted product → explain the calculation → show specs section and a simple spec filter.

### Sprint 4: Media + Search/Filter
**What users experience**
- Product images feel complete (gallery) and search/filter becomes a primary navigation path.

**PM success criteria**
- Findability improves (users reach the right product in fewer steps).

**PO acceptance focus**
- Search supports sort/pagination; filter combinations are stable and performant enough for MVP scale.

**Demo script**
- Search “laptop” → apply price + RAM filter → sort by price → open a product gallery.

### Sprint 5: Inventory Signals + Reviews
**What users experience**
- Clear stock signals and early reviews/ratings increase confidence.

**PM success criteria**
- Trust signals improve; users spend more time on product details.

**PO acceptance focus**
- Review creation constraints (e.g., verified buyer) and moderation hooks are defined.

**Demo script**
- Show low stock messaging → place order → leave a review → see rating aggregate update.

### Sprint 6: Wishlist + Comparison
**What users experience**
- Users can save items and compare similar products side-by-side.

**PM success criteria**
- Retention and repeat visits improve (users have a reason to return).

**PO acceptance focus**
- Constraints are explicit (max compare count, same-category rules, persistence behavior).

**Demo script**
- Add 2–4 products → compare → highlight spec differences → add one to wishlist.

---

### Sprint 7: Order Lifecycle State Machine
**What users experience**
- Orders display a clear status with consistent transitions.

**PM success criteria**
- Fewer “did it work?” moments after checkout; post‑purchase trust increases.

**PO acceptance focus**
- State transition rules are explicit and enforced; history tracking exists.

**Demo script**
- Create order → show order status progression and history log.

### Sprint 8: Cancellation/Refund + Modification Rules
**What users experience**
- Users can cancel (when allowed) and understand refund outcomes; modifications are permitted only within clear boundaries.

**PM success criteria**
- Reduced anxiety; fewer failures that require manual intervention.

**PO acceptance focus**
- Compensation logic is robust; UI messaging is clear and accurate.

**Demo script**
- Create order → cancel in allowed state → show wallet refund + order status update.

### Sprint 9: Reliability + Invoice
**What users experience**
- Fewer weird edge cases; invoices are available (trust artifact).

**PM success criteria**
- Higher perceived professionalism; fewer “support-style” issues.

**PO acceptance focus**
- Idempotency and rollback coverage improved; invoice rules defined.

**Demo script**
- Simulate a failure scenario → show safe compensation → download invoice for completed order.

### Sprint 10: Multi‑Payment Methods
**What users experience**
- Choice of payment method with predictable outcomes and errors.

**PM success criteria**
- Checkout conversion improves; fewer drop-offs from payment step.

**PO acceptance focus**
- Payment adapter contract stable; method selection stored/handled correctly.

**Demo script**
- Checkout → select method → pay → show order created and payment recorded.

### Sprint 11: Coupons + Payment Retry
**What users experience**
- Users apply promos and recover from transient payment failures.

**PM success criteria**
- Promo adoption increases conversion without breaking margins/abuse controls (later).

**PO acceptance focus**
- Coupon validation rules are correct and test-covered; retries don’t double-charge.

**Demo script**
- Apply valid coupon → place order → show discount breakdown → simulate retry flow.

---

## How PM & PO Use This Each Sprint

### PM Checklist (Outcome)
- What user problem got easier this sprint?
- What metric should move (even slightly)?
- What’s the next riskiest assumption?

### PO Checklist (Execution)
- Acceptance criteria are testable and unambiguous.
- Demo script shows user-visible change.
- DoD is met (see `DEFINITION_OF_DONE.md`).

