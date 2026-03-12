# 🗺️ Product Roadmap (PM/PO) — Outcome + Release View

This roadmap is written from a **Product Manager + Product Owner** viewpoint and is **mapped to the existing engineering epics** in `docs/PROJECT_ROADMAP.md`.

---

## Current State (Baseline: MVP ✅)

The MVP already supports:
- Signup/login (JWT)
- Product catalog browsing
- Cart (frontend)
- Checkout using wallet payment
- Order creation + order history

Key gap: the product is functional but not yet “best-in-class” for **organic food decisioning** (variants/specs/search/compare/reviews) or **production maturity** (tests, CI/CD, observability, security hardening).

---

## Roadmap Principles (How we prioritize)

1. **User decisioning first** (organic buyers need certifications/origin/freshness/search)
2. **Checkout trust second** (order lifecycle clarity, safe failure handling)
3. **Quality gates enable scale** (tests/CI/observability/security)
4. **Admin + growth levers last** (dashboard, recommendations, promos, advanced search)

---

## Now / Next / Later

### Now (0–3 months)
- Make product browsing and selection *feel like organic food commerce*, not a generic catalog.
- Improve discovery and transparency: categories, certifications, origin, pricing logic, freshness, images, search/filter.

**Engineering mapping:** Epic 1 (Enhanced Product Domain)

### Next (3–6 months)
- Make purchasing and post-purchase *trustworthy and explicit*.
- Introduce lifecycle states, cancellation/refunds, reliability patterns, and better payments.

**Engineering mapping:** Epics 2–3 (Order + Payment)

### Later (6–12 months)
- Make the platform *scalable and operable*.
- Modernize frontend patterns, testing, CI/CD, Kubernetes, observability, and security.
- Add growth capabilities (admin, notifications, recommendations).

**Engineering mapping:** Epics 4–10

---

## Quarterly Roadmap (12 Months)

> Assumption: 2-week sprints. “Sprint numbers” reference `docs/ITERATION_CHECKLIST.md`.

### Q1 (Sprints 1–6): “Electronics-grade Catalog”
**Outcome:** Users can **find and choose** electronics confidently.

- **User-visible improvements**
  - Categories/types (Smartphones, Laptops, etc.)
  - Variants (color/storage/RAM) with SKU and stock per variant
  - Pricing strategies (sale/bundle/seasonal)
  - Specs/attributes and filters
  - Images + gallery
  - Search + sorting + pagination
  - Reviews and early trust signals
  - Wishlist + comparison (nice-to-have toward end of Q1)

- **Success metrics (targets)**
  - +X% add-to-cart rate (baseline → improved)
  - +X% product-to-cart conversion
  - Reduced “decision friction” (fewer bounces from product details)

- **Engineering mapping**
  - Epic 1: PBIs 1.1–1.10

### Q2 (Sprints 7–11): “Trustworthy Orders & Checkout”
**Outcome:** Users trust the purchase lifecycle and the system handles failure safely.

- **User-visible improvements**
  - Clear order states (pending → processing → shipped → delivered)
  - Order cancellation and refunds with transparent messaging
  - Order modifications (where allowed)
  - Payment method choices (wallet + mock cards/UPI) + retry behavior
  - Promotional codes
  - Invoice download (optional but high-value trust artifact)

- **Success metrics (targets)**
  - Higher checkout success rate
  - Lower payment failure rate (or clearer recovery)
  - Lower “where is my order?” confusion (proxy = fewer support-like issues)

- **Engineering mapping**
  - Epic 2: PBIs 2.1–2.6
  - Epic 3: PBIs 3.1–3.4

### H2 (Sprints 12–35): “Scale, Quality, and Growth”
**Outcome:** The platform becomes production-grade and extensible.

#### Q3 (Sprints 12–18): “Frontend Modernization + Testing”
- React Query, Zustand, forms, performance, accessibility
- Unit/integration/E2E testing foundations

**Engineering mapping:** Epic 4 + Epic 5

#### Q4 (Sprints 19–27): “Delivery + Platform Operations”
- CI/CD, versioning, quality gates
- Kubernetes, Helm, ingress, autoscaling
- Observability: logs/metrics/tracing/dashboards

**Engineering mapping:** Epics 6–8

#### Year-end (Sprints 28–35): “Growth + Security Hardening”
- Notifications, recommendations, admin dashboard, advanced search, real-time
- Redis caching, rate limiting, security headers, validation, secrets management, security testing

**Engineering mapping:** Epics 9–10

---

## Release Slices (How we ship value)

- **Release A (end of Sprint 2):** Categories + variants (baseline electronics feel)
- **Release B (end of Sprint 4):** Specs + search + media (decisioning improvements)
- **Release C (end of Sprint 6):** Reviews + comparison/wishlist (trust + retention)
- **Release D (end of Sprint 9):** Order lifecycle + cancellation/refunds + saga reliability
- **Release E (end of Sprint 11):** Multi-payments + coupons (checkout conversion levers)
- **Release F (end of Sprint 18):** Frontend modernization + testing base (quality step change)
- **Release G (end of Sprint 27):** CI/CD + K8s + observability (operability)
- **Release H (end of Sprint 35):** Security hardening + growth features (scale readiness)

---

## Key Risks (PM/PO Watchlist)

- **Scope creep:** keep Q1 focused on decisioning essentials.
- **Data model complexity:** variants/specs can explode if not constrained.
- **Operational debt:** without testing/CI, velocity will drop mid-year.
- **Security debt:** must be addressed before “growth” features.

