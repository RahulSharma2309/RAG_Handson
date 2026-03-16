# Epic 1 — Enhanced Product Domain & Design Patterns
**Duration:** 4–5 sprints  
**Story Points:** 144  
**Owner(s):** Product/Engineering  
**Last Updated:** 2025-12-27

---

## 1) Epic goal (product requirement)
Upgrade the “Product” domain from a simple generic catalog into an **electronics-first, market-standard catalog** that supports:
- **Categories and typed products** (Smartphones, Laptops, Tablets, Accessories, Wearables)
- **Variants (SKU-level)** (color/storage/RAM etc.)
- **Pricing rules** (sale/bundle/seasonal) without littering code with `if/else`
- **Flexible specs/attributes** for different categories
- **Images/media** for a real product detail experience
- **Search, filtering, sorting, pagination**
- **Inventory improvements** (alerts, history)
- **Reviews, wishlist, comparison**

This epic is intentionally designed to teach and apply core design patterns while keeping the product roadmap grounded in an e-commerce reality.

---

## 2) End product should look like what (definition of “done” for this epic)
At the end of Epic 1, a user should be able to:
- Browse an **electronics catalog** with meaningful categories.
- Open a **product detail page** that shows:
  - Category/type-specific specs (e.g., smartphone screen size, RAM, storage)
  - Multiple images and a gallery/primary image
  - Ratings + reviews
  - Variant selection (e.g., “Black / 128GB / 8GB RAM”) that affects price + stock
- Search for products and apply filters (category, price range, brand, typed attributes), plus sorting + pagination.
- Maintain wishlist and compare products side-by-side (within category).

From a platform perspective, the end state should:
- Keep **backwards compatibility** where reasonable (or provide migration/transition plan).
- Keep **service boundaries intact**: Product concerns stay in Product Service; Order Service continues to reserve stock (and must evolve to handle variants later in this epic).
- Be well-documented and testable, with clear contracts.

---

## 3) What must be working by the end of the epic (functionality checklist)
### Core catalog capabilities
- **Typed product model** (category/type system) with category-specific data.
- **Variant model** (SKU-level inventory + pricing).
- **Inventory operations** remain correct under changes (reserve/release).

### Discoverability
- **Search** (by text) and **filtering** (category/price/brand/attributes).
- **Sorting** and **pagination**.

### Merchandising
- **Images/media** support (multi-image, ordering, primary image).
- **Dynamic pricing** (strategies/rules) with clear display on UI.

### Customer experience
- **Reviews and ratings** (verified buyer rule).
- **Wishlist** (add/remove, show list).
- **Comparison** (up to 4 products, within category).

### Non-functional expectations
- **API stability**: versioning or contract migration plan if breaking changes are required.
- **Performance**: indexes and query shapes appropriate for filters and pagination.
- **Observability readiness**: structured logs around pricing/stock operations.

---

## 4) Scope (what is included vs excluded)
### Included
- Product domain changes (model, schema, API) required by PBI 1.1–1.10.
- Frontend UI updates required to consume the new product/variant/search features.
- Documentation updates (service docs + user flows) for each delivered capability.

### Excluded (explicitly out of scope for Epic 1)
- New payment methods (Epic 3).
- Order state machine/saga reliability work (Epic 2).
- CI/testing infrastructure upgrades as a formal program (Epic 5/6), though each PBI should still add appropriate tests.
- Full production-grade object storage/CDN: define an integration point; production hardening comes later.

---

## 5) PBIs under this epic (reference list)
> The detailed PBI docs are expected to live alongside this epic document.

- **PBI 1.1 — Product Category & Type System** (Factory Pattern)
- **PBI 1.2 — Product Variant System** (Builder Pattern)
- **PBI 1.3 — Dynamic Pricing Strategy System** (Strategy Pattern)
- **PBI 1.4 — Product Specifications & Attributes System** (EAV / flexible attributes)
- **PBI 1.5 — Product Images & Media Management**
- **PBI 1.6 — Product Search & Filtering** (Specification Pattern)
- **PBI 1.7 — Inventory Management & Stock Alerts** (Observer Pattern)
- **PBI 1.8 — Product Reviews & Ratings**
- **PBI 1.9 — Wishlist Feature** (Observer Pattern for price tracking)
- **PBI 1.10 — Product Comparison Feature**

---

## 6) Learnings expected from Epic 1 (design + engineering)
### Services & boundaries
- Product Service evolves from a simple CRUD service into a **rich domain service** while keeping the dependency graph stable (Order depends on Product; Product remains a leaf).
- Contract evolution: how to change APIs safely without breaking consumers (frontend, order-service).

### Patterns & where they fit
- **Factory**: create correct typed Product from an input contract (type + attributes).
- **Builder**: compose a complex variant/sku structure safely.
- **Strategy**: pricing logic remains extensible and testable.
- **Specification**: composable search/filter queries without `if` explosion.
- **Observer**: stock alerts / price drop notifications.

### Alternatives and tradeoffs to understand (document per PBI)
- EF Core inheritance (**TPH vs TPT vs owned types vs JSON**) for category-specific fields.
- Variant modeling strategies (single table vs separate Variant table; SKU as value object vs entity).
- Search approaches (SQL LIKE/full-text vs external search later like Elasticsearch in Epic 9).

