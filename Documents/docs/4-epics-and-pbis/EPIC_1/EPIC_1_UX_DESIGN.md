# Epic 1 — UX Design (Epic + PBI-level blueprint)
**Epic:** Epic 1 — Enhanced Product Domain & Design Patterns  
**Covers PBIs:** 1.1–1.4 (this folder currently contains 1.1–1.4)  
**Last Updated:** 2025-12-28

---

## Purpose
Define a **Figma-ready UX blueprint** for Epic 1 so each PBI can ship incrementally without redesigning screens repeatedly.

This document intentionally stays **low fidelity** (wireframe + behaviors + component contracts) to avoid prematurely locking visual style.

---

## Information architecture (IA) & screen map

```mermaid
flowchart TD
  A[Landing] --> B[Product Search / Listing]
  B --> C[Product Detail (PDP)]
  C --> D[Cart]
  D --> E[Checkout]
  A --> F[Login/Register]
  A --> G[Profile]
  A --> H[Order History]

  %% Epic 1 focus
  B --> B1[Type filter (PBI 1.1)]
  C --> C1[Variant selector (PBI 1.2)]
  C --> C2[Price state display (PBI 1.3)]
  C --> C3[Specifications (PBI 1.4)]
```

---

## Primary user journeys (Epic 1)

### Journey A — Browse electronics catalog by type (PBI 1.1)
- User opens listing.
- User filters by **Product Type** (Smartphone/Laptop/Tablet/Accessory/Wearable).
- User opens a product.

### Journey B — Select variant + add to cart (PBI 1.2)
- On PDP user selects variant options (e.g., Color, Storage, RAM).
- UI reflects effective price + stock for selected variant.
- Add to cart stores `variantId` (or SKU) alongside product.

### Journey C — Understand dynamic price (PBI 1.3)
- Listing + PDP show effective price with clear state:
  - Regular
  - Sale (strike-through base)
  - Seasonal (badge + end date)
  - Bundle (minimal initial disclosure)

### Journey D — Scan specifications (PBI 1.4)
- PDP shows grouped specs with consistent labels and units.
- Specs support “Show more/less” and are readable on mobile.

---

## Figma structure (frames, components, naming)

### Frames (desktop)
- `S/LISTING — Product Search`
- `S/PDP — Product Detail`
- `S/CART — Cart`

### Frames (mobile)
- `M/LISTING — Product Search`
- `M/PDP — Product Detail`
- `M/CART — Cart`

### Components (shared)
- `C/App Header`
- `C/Product Card`
- `C/Filter Bar`
- `C/Chip`
- `C/Price Display`
- `C/Variant Picker`
- `C/Specs Table`
- `C/Badge`
- `C/Button`

### Component conventions
- Use **Auto-layout** everywhere possible.
- Use variants for states, example:
  - `C/Price Display` → `state=regular|sale|seasonal|bundle`
  - `C/Chip` → `state=default|selected|disabled`
  - `C/Button` → `type=primary|secondary|ghost`, `state=default|hover|disabled|loading`

---

## Design tokens (pragmatic starter set)

### Spacing
- 4, 8, 12, 16, 24, 32

### Typography (semantic)
- `H1` page title
- `H2` section title
- `Body` default text
- `Meta` helper text

### Color (semantic)
- `text/default`, `text/muted`
- `surface/default`, `surface/subtle`
- `border/default`
- `accent/primary`
- `status/sale`, `status/lowStock`, `status/outOfStock`

---

## Interaction rules (cross-PBI)

### Loading
- Listing: skeleton cards (3–6).
- PDP: skeleton for gallery + title + price + variant panel + specs.

### Errors
- Listing: non-blocking inline error with “Retry”.
- PDP: if selected variant cannot be priced/stocked, disable “Add to cart” and show reason.

### Accessibility (baseline)
- Keyboard navigable filters and variant options.
- Visible focus states.
- Price changes should be announced (ARIA live region) on variant selection (frontend detail; design must anticipate).

---

## Incremental delivery mapping
- **PBI 1.1**: Listing filter by type + show type label on card + PDP shows type label.
- **PBI 1.2**: PDP variant picker + cart line item shows variant summary.
- **PBI 1.3**: `C/Price Display` states across listing/PDP/cart.
- **PBI 1.4**: PDP specs section (`C/Specs Table`) grouped by category.

