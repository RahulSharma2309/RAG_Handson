# 📊 Epics & PBIs (Product Backlog) - FreshHarvest Market

> **Complete catalog of all epics and product backlog items for organic products marketplace**

---

## 🌱 Product Pivot (Jan 2026)

**Previous Domain:** Electronics & Smart Devices E-Commerce  
**Current Domain:** **Organic Products Marketplace** (FreshHarvest Market)  
**Architecture:** White-label ready for easy domain switching

**What Changed:**
- Product model enhanced with organic-specific fields (certification, origin, expiration)
- Frontend rebranded with organic green theme
- White-label configuration architecture for future flexibility
- All epics updated to reflect organic products domain

---

## 🎯 Overview

This folder contains all epics and their Product Backlog Items (PBIs). Each epic is organized in its own folder with the epic overview and all related PBIs.

**Total Story Points:** 864  
**Total Epics:** 10  
**Completed Epics:** 0 (MVP completed separately)  
**In Progress:** Epic 1 (PBI 1.1 ✅ COMPLETED)

---

## 📋 Epic Catalog

| Epic | Title | Story Points | Sprints | Status |
|------|-------|--------------|---------|--------|
| **MVP** | Core E-Commerce Platform | 89 | 3 | ✅ Complete |
| **Epic 1** | Enhanced Product Domain & Design Patterns | 144 | 5 | 📂 Planned |
| **Epic 2** | Advanced Order Management | 89 | 4 | 📋 Planned |
| **Epic 3** | Advanced Payment | 55 | 3 | 📋 Planned |
| **Epic 4** | Frontend Architecture | 89 | 4 | 📋 Planned |
| **Epic 5** | Testing Strategy | 55 | 3 | 📋 Planned |
| **Epic 6** | CI/CD Pipeline | 55 | 2 | 📋 Planned |
| **Epic 7** | Kubernetes Deployment | 89 | 4 | 📋 Planned |
| **Epic 8** | Observability | 55 | 3 | 📋 Planned |
| **Epic 9** | Advanced Features | 89 | 5 | 📋 Planned |
| **Epic 10** | Performance & Security | 55 | 3 | 📋 Planned |

---

## 📁 Epic 1: Enhanced Product Domain - Organic Products (144 pts)

**Location:** [`EPIC_1/`](EPIC_1/)

**Goal:** Upgrade product catalog for organic products marketplace with enterprise-grade design patterns and white-label flexibility

**Progress:** 13/144 story points (9% complete) - ✅ **PBI 1.1 COMPLETED**

### Documents
- [`EPIC_1.md`](EPIC_1/EPIC_1.md) - Epic overview, goals, scope (organic products)
- [`EPIC_1_UX_DESIGN.md`](EPIC_1/EPIC_1_UX_DESIGN.md) - UX guidelines (organic theme)

### PBIs

| PBI | Title | Pattern | Story Points | Status |
|-----|-------|---------|--------------|--------|
| [`PBI_1_1`](EPIC_1/EPIC_1_PBI_1_1.md) | Product Categories & Organic Fields | Factory | 13 | ✅ **DONE** |
| [`PBI_1_2`](EPIC_1/EPIC_1_PBI_1_2.md) | Product Variants (SKUs) | Builder | 13 | 📋 Planned |
| [`PBI_1_3`](EPIC_1/EPIC_1_PBI_1_3.md) | Dynamic Pricing | Strategy | 13 | 📋 Planned |
| [`PBI_1_4`](EPIC_1/EPIC_1_PBI_1_4.md) | Product Specifications | EAV | 13 | 📋 Planned |
| PBI 1.5 | Product Images & Media | - | 13 | 📋 Planned |
| PBI 1.6 | Search & Filtering (Organic Categories) | Specification | 21 | 📋 Planned |
| PBI 1.7 | Inventory & Stock Alerts | Observer | 13 | 📋 Planned |
| PBI 1.8 | Reviews & Ratings | - | 13 | 📋 Planned |
| PBI 1.9 | Wishlist | Observer | 13 | 📋 Planned |
| PBI 1.10 | Product Comparison | - | 8 | 📋 Planned |

**Total:** 144 story points  
**Completed:** 13 points (PBI 1.1)

---

## 📁 Future Epics

### Epic 2-10 (Coming Soon)
As epics are worked on, they will be documented in their own folders following the same pattern:
```
4-epics-and-pbis/
├── EPIC_1/          ✅ Documented
├── EPIC_2/          🚧 Future
├── EPIC_3/          🚧 Future
└── ...
```

---

## 🔗 How Epics Connect to Other Docs

### Epic → User Flow Mapping

| Epic | Creates/Modifies User Flows |
|------|---------------------------|
| MVP | All current flows in [`5-user-flows/`](../5-user-flows/) |
| Epic 1 | Enhanced product browsing, variant selection |
| Epic 2 | Order tracking, cancellation flows |
| Epic 3 | Multiple payment methods |
| Epic 4 | PWA, offline mode |

### Epic → Service Mapping

| Epic | Primary Service(s) | Secondary Services |
|------|-------------------|-------------------|
| Epic 1 | Product Service | Order (reservation updates) |
| Epic 2 | Order Service | All services (state machine) |
| Epic 3 | Payment Service | User (wallet alternatives) |
| Epic 4 | Frontend | Gateway (API changes) |

---

## 📊 Progress Tracking

**Overall Progress:** 102/864 story points (11.8%)

### By Epic
- ✅ MVP: 89/89 (100%)
- 🚧 Epic 1 (Organic Products): 13/144 (9%) - PBI 1.1 ✅ COMPLETED
- 📋 Epic 2-10: Not started

**Estimated Timeline:** 36 sprints (72 weeks @ 20 hrs/week)

**Recent Milestone (Jan 2026):** Pivoted to organic products domain with white-label architecture

See detailed tracking: [`../9-roadmap-and-tracking/ITERATION_CHECKLIST.md`](../9-roadmap-and-tracking/ITERATION_CHECKLIST.md)

---

## 🎯 Working with Epics & PBIs

### As a Developer:
1. Read Epic overview (EPIC_X.md)
2. Choose a PBI
3. Read PBI acceptance criteria
4. Check related user flows
5. Review service architecture docs
6. Implement + test + document

### As a Product Owner:
1. Review epic goals and scope
2. Refine PBI acceptance criteria
3. Prioritize within epic
4. Validate Definition of Done
5. Track progress

---

**Back to:** [Documentation Index](../DOCUMENTATION_INDEX.md) | [START HERE](../START_HERE.md)


















