# Epic 1 — PBI 1.2: Product Variant System (Builder Pattern)
**Epic:** Epic 1 — Enhanced Product Domain & Design Patterns  
**PBI:** 1.2  
**Story Points:** 21  
**Target Sprint:** Sprint 1–2  
**Last Updated:** 2025-12-27

---

## 1) Objective (what to do)
Extend the Product domain to support **SKU-level variants** (e.g., color/storage/RAM) so that a single product (e.g., “iPhone 15”) can have multiple purchasable configurations with their own **price adjustments** and **stock**.

This PBI should enable later work on pricing strategies (PBI 1.3), rich specs (PBI 1.4), and comparison (PBI 1.10) without forcing “variant logic” into controllers or frontend hacks.

---

## 2) Product expectation (what “good” looks like)
### End-user expectations
- On product detail, users can select a variant (e.g., “Black / 256GB / 8GB”).
- The selected variant clearly affects:
  - displayed price (base + adjustment, if any)
  - available stock
- Adding to cart should capture the selected variant (not just the base product).

### Developer/platform expectations
- Variants are first-class entities/value objects (not a JSON blob with ad-hoc parsing).
- Variant construction is safe and consistent (no partial/invalid SKUs).
- APIs remain stable and well-documented; contracts clearly distinguish “product” vs “variant”.

---

## 3) Scope
### In scope
- Domain model changes in Product Service:
  - `ProductVariant` entity (or aggregate member) with:
    - unique SKU
    - option values (color/storage/RAM etc.)
    - per-variant stock
    - optional price override or price adjustment
    - status (active/discontinued)
  - Variant option model (e.g., `VariantOption` + `VariantOptionValue`)
- **Builder Pattern** implementation:
  - `ProductVariantBuilder` (or `VariantBuilder`) to construct valid variants and SKU consistently
- Product Service API:
  - Create product variants
  - Read product with variants
  - Update stock at variant level (as appropriate for this epic)
- Minimal frontend updates:
  - Variant selector UI (dropdowns/buttons)
  - Cart payload includes `variantId`/`sku`

### Out of scope (for this PBI)
- Complex pricing rules and promotions (PBI 1.3)
- Flexible attribute/EAV system (PBI 1.4)
- Media gallery (PBI 1.5)
- Advanced search facets on variant attributes (introduced in PBI 1.6)

---

## 4) Technologies and patterns to use
### Existing stack constraints
- **Backend:** .NET 8 Web API
- **ORM:** Entity Framework Core
- **DB:** SQL Server (productdb)

### New pattern introduced
- **Builder Pattern**:
  - build a complex `ProductVariant` from validated inputs (options + stock + pricing fields)
  - centralize SKU generation rules to one place

---

## 5) Data model design (recommended approach)
### Recommended model
- `Products` (from PBI 1.1)
- `ProductVariants`
  - `Id`
  - `ProductId` (FK)
  - `Sku` (unique index)
  - `IsActive`
  - `StockOnHand`
  - `PriceAdjustment` (nullable) and/or `PriceOverride` (nullable)
  - `CreatedAt`
- `ProductVariantOptions` (optional; normalized)
  - `VariantId`
  - `Key` (e.g., `color`, `storageGb`, `ramGb`)
  - `Value` (string; can be typed later in PBI 1.4)

### SKU generation guidance
- SKU should be deterministic and stable.
- Example: `IPH15-BLK-256-8` or `SKU-{ProductId}-{hash(options)}`
- Enforce uniqueness at DB level.

---

## 6) API contract changes (what endpoints should do)
> Keep base routes stable (`/api/products`) so Gateway/Frontend routing stays simple.

### GET /api/products/{id}
- Include variants array:
  - each variant exposes `id`, `sku`, `options`, `stock`, and effective price fields (as applicable)

### POST /api/products/{id}/variants
- Create one or more variants for a product.
- Implementation uses `ProductVariantBuilder` to validate and build.

### PATCH /api/products/variants/{variantId}/stock
- Update variant stock (admin/internal use).

### Cart/Order integration note
- If Order Service currently reserves by `productId`, introduce a **backwards-compatible** path:
  - keep existing reserve by product working for products with a single “default variant”, or
  - add a new reserve endpoint for `variantId` while keeping the old one for MVP flows until migrated.

---

## 7) Developer “how-to” guide (implementation steps)
### Step 1 — Add variant entities
- Create `ProductVariant` and option model(s).
- Define invariants:
  - options must be complete for the product’s variant schema
  - stock must be >= 0
  - SKU must be non-empty and unique

### Step 2 — Implement Variant Builder
- `IProductVariantBuilder` + `ProductVariantBuilder`
- Validate inputs and construct:
  - options dictionary / normalized rows
  - SKU generation
  - pricing fields

### Step 3 — Update persistence layer
- Add EF Core mappings and migrations.
- Add unique index for `Sku`.

### Step 4 — Update Product API
- Add endpoints for creating and fetching variants.
- Ensure serialization is stable and documented (Swagger).

### Step 5 — Frontend minimal variant selection
- On PDP, render option selectors and compute selected variant.
- Ensure “Add to cart” includes selected variant identifier.

---

## 8) Testing guide (how to test it)
### Unit tests
- Builder:
  - valid inputs produce correct SKU and option set
  - invalid options/duplicates are rejected
- SKU generation:
  - deterministic for same inputs
  - uniqueness enforced by tests (and DB index)

### Integration tests
- Create variants via API → 201
- Fetch product → variants included and correct
- Stock update endpoint works and persists

### Manual smoke checks
- UI: pick variant → price/stock changes
- Add to cart → variant preserved

---

## 9) Learnings captured (services, tools, patterns, alternatives)
### What you learn in this PBI
- Modeling SKU-level purchase units cleanly in a product catalog.
- Using Builder to prevent partial/invalid variant creation.

### Key decisions to record (and why)
- Variant options modeling:
  - normalized rows vs JSON (tradeoff: queryability vs flexibility)
- How Order/Reserve adapts:
  - keep backwards compatibility vs introduce a parallel contract

### Alternative ways to solve the same problem
- Store options as JSON only (fast to ship, harder to query/filter later).
- Make each variant its own Product row (simpler purchasing, harder merchandising).

---

## 10) Acceptance criteria (checklist)
- [ ] Product variants exist as first-class model with SKU, options, stock
- [ ] Variants can be created via API using Builder pattern
- [ ] Product detail API returns variants
- [ ] SKU uniqueness enforced in DB
- [ ] Frontend supports selecting variant and adding it to cart
- [ ] Tests exist for builder and basic API flows
