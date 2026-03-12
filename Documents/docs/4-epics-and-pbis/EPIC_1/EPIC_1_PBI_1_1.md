# Epic 1 — PBI 1.1: Product Category & Type System (Factory Pattern)
**Epic:** Epic 1 — Enhanced Product Domain & Design Patterns  
**PBI:** 1.1  
**Story Points:** 13  
**Target Sprint:** Sprint 1–2  
**Last Updated:** 2025-12-27

---

## 1) Objective (what to do)
Evolve the current Product model (today: `id, name, description, price, stock`) into a **typed electronics catalog** where each product belongs to a **ProductType** (e.g., Smartphone, Laptop, Tablet, Accessory, Wearable) and supports **type-specific attributes**.

This PBI is the foundation for variants, pricing strategies, specs, comparison, and search in later PBIs.

---

## 2) Product expectation (what “good” looks like)
### End-user expectations
- A product is clearly categorized (e.g., “Smartphone” vs “Laptop”).
- Users can filter/browse by category/type (at minimum).
- Product detail can show **type-specific fields** (even if the UI is basic in this PBI).

### Developer/platform expectations
- The Product Service has a clear domain model that can grow without turning into:
  - One massive `Product` class with dozens of nullable fields and `if (type == …)` everywhere
  - Or a schema that is impossible to query efficiently
- APIs remain consistent and discoverable (Swagger docs updated).
- Minimal breakage to existing MVP flows (catalog listing, reserve/release by Order Service).

---

## 3) Scope
### In scope
- Product domain changes:
  - `ProductType` enum
  - Typed product classes (Smartphone/Laptop/Tablet/Accessory/Wearable)
  - Category-specific attributes (initial set, extensible)
- Database schema update using EF Core inheritance (TPH or TPT)
- Product Service API updates:
  - Create product requires `type` + relevant fields
  - Get endpoints return type and type-specific fields
  - Add “filter by type” support on listing endpoint
- Seed data updated to include electronics examples

### Out of scope (for this PBI)
- Variant-level modeling (SKU, color/storage/RAM combos) → PBI 1.2
- Dynamic pricing strategies → PBI 1.3
- Flexible attributes/EAV system → PBI 1.4 (if you decide not to model every spec as a column here)
- Images/media → PBI 1.5

---

## 4) Technologies and patterns to use
### Existing stack constraints
- **Backend:** .NET 8 Web API
- **ORM:** Entity Framework Core
- **DB:** SQL Server (productdb)
- **Architecture in service:** Repository + Service layer + Validator + DTO patterns (already present)

### New pattern introduced
- **Factory Pattern** for product creation:
  - One input contract (Create DTO includes `productType`)  
  - A factory maps `ProductType` → correct concrete class + validation

---

## 5) Data model design (recommended approach)
You have two reasonable choices. Pick one and document the decision in the PR.

### Option A (recommended for this codebase): EF Core TPH (Table-Per-Hierarchy)
- **Pros**
  - One table, simple migrations, simple queries, easiest for an MVP evolution
  - Works well with filters and pagination
- **Cons**
  - Many nullable columns as categories grow
  - Requires discipline to avoid “everything in columns” later

**TPH sketch**
- Table: `Products`
- Columns:
  - Common: `Id, Name, Description, Price, Stock, CreatedAt, ProductType (discriminator)`
  - Smartphone examples: `ScreenSizeInches, BatteryMah, StorageGb, RamGb`
  - Laptop examples: `CpuModel, RamGb, StorageGb, ScreenSizeInches`

### Option B: EF Core TPT (Table-Per-Type)
- **Pros**
  - Cleaner separation of category fields
  - Avoids a wide table of nullable columns
- **Cons**
  - More complex migrations and query shapes (joins)
  - Performance can degrade without careful indexing

---

## 6) API contract changes (what endpoints should do)
> Keep base routes stable (`/api/products`) so Gateway/Frontend routing stays simple.

### GET /api/products
- **Add query filtering**
  - Example: `/api/products?type=Smartphone`
  - (Optional) allow multi-type: `/api/products?type=Smartphone&type=Laptop`

### GET /api/products/{id}
- Return base fields + `type` + type-specific attributes.

### POST /api/products
- Request includes:
  - Base fields: `name, description, price, stock`
  - `type`
  - Type-specific fields (minimal initial set)
- Implementation uses **ProductFactory** to instantiate the correct model.

### Keep reserve/release stable
- Order Service currently calls reserve/release by `productId`.
- For this PBI, keep it working with the new model (no change to contract required yet).

---

## 7) Developer “how-to” guide (implementation steps)
### Step 1 — Add domain types
- Add `ProductType` enum in Product Service domain.
- Create an abstract/base `Product` (or keep `Product` as base class) and implement derived classes:
  - `SmartphoneProduct`, `LaptopProduct`, `TabletProduct`, `AccessoryProduct`, `WearableProduct`

### Step 2 — Choose inheritance mapping (TPH or TPT)
- Configure EF Core inheritance mapping in `AppDbContext` (or via attributes).
- Add the discriminator column + any required category-specific columns.

### Step 3 — DTOs and validation
- Update `CreateProductDto` to include `type` and fields required for each type.
  - If a single DTO gets too large, use:
    - a base DTO + per-type DTOs (recommended), or
    - a polymorphic JSON body (advanced; more work for validation and Swagger)
- Update validators:
  - Base validation (name/price/stock)
  - Type-specific validation (e.g., `RamGb > 0` for laptops)

### Step 4 — Implement ProductFactory
- Create `IProductFactory` + `ProductFactory`
- `CreateProduct(dto)` returns the correct derived `Product` object.
- Keep the factory pure and unit-testable (no DB calls inside the factory).

### Step 5 — Update controllers/services/repositories
- Ensure create/read endpoints serialize the new shape.
- Add filtering in `GetAll` (service/repository layer), ideally:
  - `GetAllAsync(ProductType? type = null)` or a simple filter object.

### Step 6 — Migrations + seed data
- Create migration and apply to `productdb`.
- Update seed products in `Program.cs` to include electronics examples per type.

### Step 7 — Frontend minimal updates (if included in this PBI)
- Add a basic type filter (dropdown/pills) on product listing.
- Display `type` on product cards/details until richer specs UI comes later.

---

## 8) Testing guide (how to test it)
### Unit tests (fast)
- **Factory tests**
  - Given `CreateProductDto(type=Smartphone, ...)` → returns `SmartphoneProduct` with correct properties
  - Invalid inputs per type throw validation errors (or return structured errors)
- **Validation tests**
  - Base rules: name required, price/stock >= 0
  - Type rules: required typed fields present and within range

### Integration tests (API + DB)
- Spin up Product Service with a real SQL Server (or TestContainers later in Epic 5):
  - POST product of each type → 201
  - GET by id returns correct `type` and fields
  - GET list with `?type=...` filters correctly

### End-to-end smoke checks (manual)
- Run full stack (Docker Compose):
  - Catalog still loads in the UI
  - Checkout still works (reserve/release unaffected)
  - Swagger shows updated Product endpoints + schemas

---

## 9) Learnings captured (services, tools, patterns, alternatives)
### What you learn in this PBI
- How to evolve a domain model in a microservice **without breaking dependent services**.
- How EF Core inheritance mapping works (and where it bites).
- How the **Factory Pattern** prevents conditional creation logic from spreading across controllers and services.

### Key decisions to record (and why)
- **TPH vs TPT** choice:
  - TPH is usually fastest to ship and easiest to query.
  - TPT is cleaner but adds join complexity.
- DTO strategy:
  - One DTO vs per-type DTOs vs polymorphic JSON
  - How that impacts Swagger clarity and validation

### Alternative ways to solve the same problem
- Keep a single `Product` table and store type-specific specs as **JSON** (SQL Server `nvarchar(max)` or JSON functions):
  - Faster schema changes, but harder validation/querying.
  - Often pairs well with a later dedicated Search system.
- Implement an **EAV model** immediately (entity-attribute-value):
  - Very flexible, but query complexity and validation complexity increase early.
- Create a separate `ProductType` table + FK:
  - Useful if types become configurable at runtime; overkill for a fixed electronics domain.

---

## 10) Acceptance criteria (checklist)
- [ ] Product domain supports `ProductType`
- [ ] Concrete product types exist (Smartphone/Laptop/Tablet/Accessory/Wearable)
- [ ] EF Core inheritance mapping implemented (TPH or TPT)
- [ ] DB schema migrated successfully
- [ ] Product creation uses `ProductFactory`
- [ ] Listing supports filtering by type
- [ ] Swagger updated and accurate
- [ ] Unit tests for factory + validators exist
- [ ] Existing MVP flows still function (catalog + order reserve/release)

