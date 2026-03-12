# Start Here — "Fly-through" Guide

> **Your role-based navigation hub for FreshHarvest Market**

---

## 🎯 Quick Navigation by Role

| Role | Start Here | Then Go To | Time |
|------|-----------|-----------|------|
| **🎓 Learning Developer** | [`2-learning-guide/LEARNING_GUIDE.md`](2-learning-guide/LEARNING_GUIDE.md) | [`5-user-flows/`](5-user-flows/) → [`7-services/`](7-services/) | 4-6 hrs |
| **📊 Product Owner/PM** | [`0-product-owner-onboarding/`](0-product-owner-onboarding/) ⭐ **NEW PO?** | [`3-product-owner/`](3-product-owner/) → [`4-epics-and-pbis/`](4-epics-and-pbis/) | 2-3 hrs |
| **📊 Experienced PO/PM** | [`3-product-owner/PRODUCT_VISION_AND_PRINCIPLES.md`](3-product-owner/PRODUCT_VISION_AND_PRINCIPLES.md) | [`4-epics-and-pbis/`](4-epics-and-pbis/) → [`9-roadmap-and-tracking/`](9-roadmap-and-tracking/) | 2-3 hrs |
| **🔍 QA/Tester** | [`5-user-flows/`](5-user-flows/) | [`7-services/`](7-services/) → Swagger UIs | 1-2 hrs |
| **💻 Frontend Developer** | [`5-user-flows/`](5-user-flows/) | [`7-services/API_GATEWAY.md`](7-services/API_GATEWAY.md) → API endpoints | 1-2 hrs |
| **🚀 DevOps Engineer** | [`1-getting-started/PROJECT_OVERVIEW.md`](1-getting-started/PROJECT_OVERVIEW.md#getting-started) | [`6-architecture/SYSTEM_ARCHITECTURE.md`](6-architecture/SYSTEM_ARCHITECTURE.md) | 1 hr |
| **🏗️ Architect** | [`6-architecture/SYSTEM_ARCHITECTURE.md`](6-architecture/SYSTEM_ARCHITECTURE.md) | [`6-architecture/LOW_LEVEL_DESIGN.md`](6-architecture/LOW_LEVEL_DESIGN.md) → [`8-platform/`](8-platform/) | 3-4 hrs |

**Can't find what you need?** → [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) - Complete catalog of all 53 docs

---

## 📚 About This Documentation

This repo is intentionally documented from multiple viewpoints:

- **Product Owner / Product Manager**: what the product is and what users do
- **Developer**: how requests move through the gateway/services and where the code lives
- **Tester (QA)**: what to verify, common failure modes, where to observe behavior (Swagger, logs)
- **Frontend developer**: which APIs exist and which flows depend on which services
- **DevOps / platform**: how to run it, what ports exist, health checks

---

## Quick orientation (5 minutes)

- **What this is**: FreshHarvest Market - an organic food marketplace designed as a **learning system** for “enterprise-ish” patterns (microservices, gateway, distributed workflows, rollback/compensation).
- **What users can do (MVP)**: signup, login, browse products, manage a cart (frontend-only), add wallet balance, checkout (order + payment + stock), view order history.
- **Where the code lives**:
  - Frontend: `frontend/`
  - Gateway: `gateway/`
  - Services: `services/*-service/`
  - Infra (docker-compose): `infra/`

If some terms feel "too enterprise", open: [`2-learning-guide/GLOSSARY.md`](2-learning-guide/GLOSSARY.md)

---

## Choose your path (by role)

### If you are a **PO / PM** (understand the product)

**New Product Owner?** Start here: [`0-product-owner-onboarding/`](0-product-owner-onboarding/) ⭐

**For all POs/PMs, read in this order:**

1. **Product overview** (new POs): [`0-product-owner-onboarding/PRODUCT_OVERVIEW_FOR_PO.md`](0-product-owner-onboarding/PRODUCT_OVERVIEW_FOR_PO.md) OR **Project overview** (experienced): [`1-getting-started/PROJECT_OVERVIEW.md`](1-getting-started/PROJECT_OVERVIEW.md)
2. **User journeys (MVP flows)**: [`5-user-flows/README.md`](5-user-flows/README.md)
3. **Product thinking** (vision/strategy/roadmap): [`3-product-owner/`](3-product-owner/)

What you should get at the end:

- What the MVP includes and excludes
- Why this product category and what's next
- How the user journeys map to services
- How to plan and execute sprints (new POs)

---

### If you are a **Developer** (understand the system + code flow)

Read in this order:

1. "Novel style" walkthrough (best single document): [`2-learning-guide/LEARNING_GUIDE.md`](2-learning-guide/LEARNING_GUIDE.md)
2. Architecture: [`6-architecture/SYSTEM_ARCHITECTURE.md`](6-architecture/SYSTEM_ARCHITECTURE.md) and [`6-architecture/LOW_LEVEL_DESIGN.md`](6-architecture/LOW_LEVEL_DESIGN.md)
3. Services index: [`7-services/README.md`](7-services/README.md)
4. Decisions + patterns (how to extend it correctly): [`2-learning-guide/ENGINEERING_PLAYBOOK.md`](2-learning-guide/ENGINEERING_PLAYBOOK.md)

What you should get at the end:

- How a request travels: UI → Gateway → Service → DB (and sometimes service → service)
- Where “orchestration” happens (Order Service) and how rollback works
- How to decide future implementations (catalog patterns, async messaging, idempotency)

---

### If you are a **Tester / QA** (what to verify and how)

Start here:

1. User flows: [`5-user-flows/README.md`](5-user-flows/README.md)
2. Services index (endpoints + error codes): [`7-services/README.md`](7-services/README.md)

How to test quickly:

- **Swagger UIs** (after running the stack):
  - Auth: `http://localhost:5001/swagger`
  - User: `http://localhost:5005/swagger`
  - Product: `http://localhost:5002/swagger`
  - Order: `http://localhost:5004/swagger`
  - Payment: `http://localhost:5003/swagger`

High-value test scenarios (MVP):

- **Signup**:
  - Duplicate email → `409`
  - Duplicate phone → `409`
  - User Service down → `503` (registration should not “partially create” a user)
- **Login**:
  - Wrong password → `401`
- **Add balance**:
  - Negative/zero amount → `400`
- **Checkout**:
  - Insufficient wallet → `409`
  - Insufficient stock → `409`
  - Stock reservation failure after payment → refund should happen (compensation)

Where to learn "expected failures":

- [`2-learning-guide/ENGINEERING_PLAYBOOK.md`](2-learning-guide/ENGINEERING_PLAYBOOK.md) (failure modes and why they happen)

---

### If you are a **Frontend developer**

Start here:

1. User journeys: [`5-user-flows/README.md`](5-user-flows/README.md)
2. Gateway routing concept: [`7-services/API_GATEWAY.md`](7-services/API_GATEWAY.md)
3. Endpoint contracts: service docs in [`7-services/`](7-services/)

Important reality in MVP:

- Cart is **frontend-only** right now (documented in `ADD_TO_CART_FLOW.md`). This is a deliberate MVP simplification.

---

### If you are **DevOps / running the stack**

Start here:

- **Run everything**: `infra/docker-compose.yml` (referenced from [`README.md`](README.md))
- **Service ports**: [`7-services/README.md`](7-services/README.md#quick-reference)
- **Health endpoints**: each service exposes `/health` (see service docs / compose config)

---

## "I only have 30 minutes"

- Read [`2-learning-guide/LEARNING_GUIDE.md`](2-learning-guide/LEARNING_GUIDE.md) sections 1–4 (product + architecture + request lifecycle)
- Then read the two most important service docs:
  - [`7-services/ORDER_SERVICE.md`](7-services/ORDER_SERVICE.md) (the orchestrator)
  - [`7-services/PAYMENT_SERVICE.md`](7-services/PAYMENT_SERVICE.md) (wallet debit/refund + audit trail)

---

## How to extend the project (without guessing)

When you add new features (catalog, search, messaging, etc.), use:

- [`2-learning-guide/ENGINEERING_PLAYBOOK.md`](2-learning-guide/ENGINEERING_PLAYBOOK.md) — the "why this pattern" guide
- [`2-learning-guide/GLOSSARY.md`](2-learning-guide/GLOSSARY.md) — shared vocabulary so docs stay consistent

