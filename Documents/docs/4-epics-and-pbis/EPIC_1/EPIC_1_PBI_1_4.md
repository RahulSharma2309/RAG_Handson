# Epic 1 — PBI 1.4: Product Specifications & Attributes System (Flexible Attributes)
**Epic:** Epic 1 — Enhanced Product Domain & Design Patterns  
**PBI:** 1.4  
**Story Points:** 8  
**Target Sprint:** Sprint 3  
**Last Updated:** 2025-12-27

---

## 1) Objective (what to do)
Introduce a flexible **specifications/attributes** system so different product types (Smartphones, Laptops, etc.) can store and display rich specs without forcing the database into an ever-growing wide table or requiring frequent migrations for every new attribute.

---

## 2) Product expectation (what “good” looks like)
### End-user expectations
- Product detail shows a clear “Specifications” section.
- Specs differ by category/type (e.g., smartphones show battery and screen; laptops show CPU and RAM).

### Developer/platform expectations
- Adding a new spec (e.g., `refreshRateHz`) does not require major refactors.
- Specs remain queryable enough to support filtering in PBI 1.6 (at least for a defined subset).
- Data validation is not completely abandoned (typed attributes where possible).

---

## 3) Scope
### In scope
- Add a flexible attribute model (EAV-like) in Product Service:
  - `ProductAttribute` with key/value (and optional typed value support)
  - Attribute grouping (optional): “Display”, “Performance”, “Battery”
- API updates:
  - Create/update attributes for product (and optionally variant)
  - Read product returns attributes grouped for UI
- Define a small initial catalog of standard keys per type:
  - Smartphone: `screenSizeInches`, `batteryMah`, `storageGb`, `ramGb`
  - Laptop: `cpuModel`, `ramGb`, `storageGb`, `screenSizeInches`
- Validation approach:
  - enforce allowed keys per product type (initially)
  - enforce basic typing rules (number vs string) for known keys

### Out of scope (for this PBI)
- Full admin UI for managing attribute schemas
- External search engine integration (later epic)
- Complex unit normalization (e.g., cm vs inches) beyond basic conventions

---

## 4) Technologies and patterns to use
### Existing stack constraints
- **Backend:** .NET 8 Web API
- **ORM:** Entity Framework Core
- **DB:** SQL Server (productdb)

### Patterns/approaches introduced
- Flexible attributes via **EAV** (entity-attribute-value) or “key/value specs”
- Optional: simple schema registry concept (allowed keys per type)

---

## 5) Data model design (recommended approach)
### Recommended entities
- `ProductAttributes`
  - `Id`
  - `ProductId` (FK)
  - `Key` (string)
  - `ValueString` (nullable)
  - `ValueNumber` (nullable, decimal)
  - `ValueBoolean` (nullable)
  - `Unit` (nullable, string; e.g., `GB`, `in`, `mAh`)
  - `Group` (nullable, string; e.g., “Display”)

### Indexing guidance (for future filtering)
- Index on `(ProductId, Key)`
- If numeric filtering is required later, consider index on `(Key, ValueNumber)`

---

## 6) API contract changes (what endpoints should do)
> Keep base routes stable (`/api/products`) so Gateway/Frontend routing stays simple.

### GET /api/products/{id}
- Include `attributes`:
  - grouped list or a flat list with `group` metadata

### PUT /api/products/{id}/attributes
- Replace attributes set for product (idempotent).
- Validate keys against allowed list for the product’s type (initial policy).

### PATCH /api/products/{id}/attributes
- Optional: partial updates (add/remove a single key).

---

## 7) Developer “how-to” guide (implementation steps)
### Step 1 — Add attribute entities and EF mappings
- Create `ProductAttribute` entity and relations.
- Add migrations.

### Step 2 — Define allowed keys and types
- Add an in-code registry (simple dictionary):
  - `ProductType` → allowed keys + expected value type + unit
- Keep it replaceable later by DB-driven schema.

### Step 3 — Implement validation and mapping
- Validate incoming attributes in service layer.
- Store values in typed columns where possible.

### Step 4 — Update read APIs and frontend rendering
- Ensure PDP can render grouped attributes cleanly.

---

## 8) Testing guide (how to test it)
### Unit tests
- Validation rejects unknown keys for a type.
- Numeric keys reject non-numeric input.
- Grouping output is stable.

### Integration tests
- Create product → set attributes → GET returns attributes correctly.

### Manual smoke checks
- PDP shows specs section; different product types show different keys.

---

## 9) Learnings captured (services, tools, patterns, alternatives)
### What you learn in this PBI
- Tradeoffs of EAV/flexible attributes: schema agility vs query complexity.
- How to keep “flexible data” still validated and documented.

### Key decisions to record (and why)
- EAV vs JSON column vs widening the Products table.
- How strict the allowed-key validation should be at this stage.

### Alternative ways to solve the same problem
- Store all specs as JSON (simpler schema, harder typed validation/query).
- Keep adding columns (query-friendly, migration-heavy).

---

## 10) Acceptance criteria (checklist)
- [ ] Products can store and return flexible attributes/specifications
- [ ] Basic validation exists (allowed keys + type checks for known keys)
- [ ] APIs support setting and reading attributes
- [ ] PDP can render attributes in a usable format
- [ ] Tests cover key validation and serialization
