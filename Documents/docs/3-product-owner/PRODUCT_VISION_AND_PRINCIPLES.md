# 🎯 Product Vision & Principles (PM/PO)

## 🌱 Product Pivot (Jan 2026)
**Previous:** Electronics & Smart Devices E-Commerce  
**Current:** **Organic Products Marketplace**

## Product Name
**FreshHarvest Market** - Organic Products E-Commerce Platform

## Vision (North Star Statement)
Enable customers to **discover, trust, and purchase certified organic products** with a shopping experience that is **transparent, fresh, and sustainable**.

## Mission (What we do day-to-day)
Build an organic marketplace experience that:
- makes choosing organic products easier (certifications, origin, freshness, categories)
- makes checkout reliable (validation, payments, delivery tracking)
- makes the system white-label ready (configurable branding, multi-tenant architecture)
- ensures quality and freshness (expiration tracking, organic certification verification)

---

## Target Customers
- **Primary:** Health-conscious consumers seeking certified organic produce, grains, and groceries.
- **Secondary:** Environmentally aware shoppers who value sustainable farming and local sourcing.
- **Tertiary:** Families prioritizing chemical-free, natural food products.
- **Future (Admin/Operations):** Product and order admins managing organic catalog, certifications, supplier relationships, and freshness tracking.

---

## Product Principles (Non‑Negotiables)

1. **Clarity over cleverness**
   - Specs, pricing, and stock should be understandable and consistent.

2. **Trust is a feature**
   - Users must be confident that payment, stock, and order status are accurate.

3. **Fast paths for common journeys**
   - Browse → product details → add to cart → checkout must be low-friction.

4. **Failure must be safe**
   - If something fails (payment, stock reservation), the system compensates and leaves users in a correct state.

5. **Incremental delivery**
   - Ship improvements in slices that create visible user value every sprint (or every 1–2 sprints).

---

## North Star Metric (Primary Success Metric)
**Successful checkouts per active user per month**

Why:
- Combines *value delivered* (successful orders) with *engagement* (active users).

---

## Supporting Metrics (PM Dashboard)

### Acquisition & Activation
- **Signup conversion rate**
- **First-session product discovery success** (user views ≥ 3 products or uses search/filter)

### Engagement
- **Add-to-cart rate**
- **Return user rate (30-day)**
- **Wishlist usage (once available)**

### Monetization / Transaction Health
- **Checkout success rate**
- **Payment failure rate**
- **Refund rate** (and top reasons)

### Product Quality (User-Perceived)
- **Time to interactive / page load (p95)**
- **API error rate (p95)**
- **Order status accuracy incidents**

---

## Strategic Bets (12-Month)

1. **Transparency in organic certification drives trust**
   - Displaying certification details, origin, and farm information increases customer confidence.

2. **Freshness guarantee reduces waste & increases satisfaction**
   - Expiration tracking, delivery speed, and quality assurance.

3. **White-label architecture enables market expansion**
   - Multi-tenant design allows quick deployment for new product domains.

3. **Quality & operations enable scale**
   - Testing, CI/CD, observability, security.

---

## Constraints & Assumptions
- **Current state:** MVP is complete (auth, product catalog, cart, checkout with wallet, orders, payment recording).
- **Architecture:** Microservices + gateway; additional features should preserve service boundaries and reliability.
- **Learning goal:** This repo is also a learning platform, so the roadmap includes deliberate patterns and tooling.

