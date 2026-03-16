# Epic 1 — PBI 1.3: Dynamic Pricing Strategy System (Strategy Pattern)
**Epic:** Epic 1 — Enhanced Product Domain & Design Patterns  
**PBI:** 1.3  
**Story Points:** 13  
**Target Sprint:** Sprint 3  
**Last Updated:** 2025-12-27

---

## 1) Objective (what to do)
Implement an extensible **dynamic pricing system** for the Product domain so that price calculation can support multiple pricing modes (Regular, Sale, Bundle, Seasonal) without spreading conditional logic (`if/else`) across controllers, services, and UI.

---

## 2) Product expectation (what “good” looks like)
### End-user expectations
- Product and variant prices display correctly for:
  - regular pricing
  - sale pricing (discounted)
  - time-bound pricing (seasonal window)
- Pricing feels consistent across listing, product detail, and cart.

### Developer/platform expectations
- New pricing rules can be added with minimal code changes and strong testability.
- Price calculation is centralized and explainable (why this price?).
- Pricing logic is independent from storage and transport (DTOs).

---

## 3) Scope
### In scope
- Define `IPricingStrategy` and concrete strategies:
  - `RegularPriceStrategy`
  - `SalePriceStrategy`
  - `SeasonalPriceStrategy`
  - `BundlePriceStrategy` (initial minimal implementation)
- Add a `PriceCalculator` (domain/service) to select and apply strategies.
- Introduce persistence for pricing rules (simple initial model):
  - product-level and/or variant-level rule association
  - optional effective date range for time-based rules
- Product Service API updates:
  - endpoints to set pricing rules (admin/internal)
  - endpoints to return “effective price” for product/variant reads

### Out of scope (for this PBI)
- A full rules engine DSL
- Multi-currency and tax/VAT (future epic)
- Personalized pricing per user segment

---

## 4) Technologies and patterns to use
### Existing stack constraints
- **Backend:** .NET 8 Web API
- **ORM:** Entity Framework Core
- **DB:** SQL Server (productdb)

### New pattern introduced
- **Strategy Pattern**:
  - Pricing strategies implement a common interface
  - `PriceCalculator` delegates to the chosen strategy

---

## 5) Data model design (recommended approach)
### Recommended entities
- `PricingRule`
  - `Id`
  - `RuleType` (Regular/Sale/Seasonal/Bundle)
  - `AppliesTo` (ProductId or VariantId)
  - `DiscountPercent` and/or `DiscountAmount`
  - `EffectiveFrom`, `EffectiveTo` (nullable)
  - `IsActive`
- Pricing rule selection precedence (document and test):
  - Variant rule overrides product rule (if both exist)
  - Active, within date window takes priority

---

## 6) API contract changes (what endpoints should do)
> Keep base routes stable (`/api/products`) so Gateway/Frontend routing stays simple.

### GET /api/products and GET /api/products/{id}
- Return both:
  - base price
  - effective price (calculated)
  - optional pricing metadata for UI (e.g., “On sale”, “Ends on …”)

### POST /api/pricing-rules
- Create a pricing rule and attach it to a product/variant.

### PATCH /api/pricing-rules/{id}
- Activate/deactivate or update date window/discount values.

---

## 7) Developer “how-to” guide (implementation steps)
### Step 1 — Define pricing contracts
- `Money`/decimal handling conventions (rounding rules).
- `IPricingStrategy.Calculate(basePrice, context)` signature.

### Step 2 — Implement strategies and calculator
- Keep strategies pure and unit-testable.
- `PriceCalculator` selects strategy based on rule type and context.

### Step 3 — Persistence and selection logic
- Add EF Core model and migrations for `PricingRule`.
- Implement rule lookup and precedence rules.

### Step 4 — Wire into product read flows
- Ensure listing and product detail use the same calculation path.

---

## 8) Testing guide (how to test it)
### Unit tests
- Each strategy returns correct value for representative inputs.
- Date-window logic works (active/inactive).
- Precedence: variant rule overrides product rule.

### Integration tests
- Create product + rule → GET returns effective price.
- Update rule window → price changes accordingly.

### Manual smoke checks
- UI displays “sale” state and correct price on listing and PDP.

---

## 9) Learnings captured (services, tools, patterns, alternatives)
### What you learn in this PBI
- Keeping business rules extensible using Strategy.
- Avoiding `if` explosion by isolating variability.

### Key decisions to record (and why)
- Rule precedence and conflict resolution.
- Whether pricing metadata is returned to the UI and in what shape.

### Alternative ways to solve the same problem
- Hardcode rule types with conditionals (fast, becomes unmaintainable).
- Use a full rules engine (powerful, higher complexity and operational cost).

---

## 10) Acceptance criteria (checklist)
- [ ] Multiple pricing strategies implemented behind a common interface
- [ ] Central price calculation service selects and applies strategies
- [ ] Pricing rules persist and support optional date windows
- [ ] Product/variant read endpoints return effective prices
- [ ] Tests cover strategy math and rule precedence
