# 📖 FreshHarvest Market — A Read‑Like‑a‑Novel Learning Guide

> **Goal:** Help a learning developer understand **what**, **why**, and **how** this project works — end-to-end — without “just doing it because AI said so”.
>
> **How to read this:** Start at the top and keep going. Every chapter builds on the previous one.
>
> **Last updated:** 2025-12-27

---

## Table of contents

- [0. What you’re looking for (and what already exists)](#0-what-youre-looking-for-and-what-already-exists)
- [1. The product, in plain language (MVP scope)](#1-the-product-in-plain-language-mvp-scope)
- [2. The system, at a glance (architecture)](#2-the-system-at-a-glance-architecture)
- [3. “User journeys” = the epic/PO-level story](#3-user-journeys--the-epicpo-level-story)
- [4. From “what happens” to “what code runs” (request lifecycle)](#4-from-what-happens-to-what-code-runs-request-lifecycle)
- [5. Code tour (the important functions and why they exist)](#5-code-tour-the-important-functions-and-why-they-exist)
- [6. Decisions, alternatives, and tradeoffs (why this way?)](#6-decisions-alternatives-and-tradeoffs-why-this-way)
- [7. How to study this repo like a developer (a repeatable method)](#7-how-to-study-this-repo-like-a-developer-a-repeatable-method)
- [8. Learning exercises (guided practice)](#8-learning-exercises-guided-practice)

---

## 0. What you’re looking for (and what already exists)

You asked for three kinds of documentation:

- **Epic / Product Owner (PO) view**: “In layman terms what functionality must be delivered, and what the expected user flow is.”
- **Developer guide**: “How to do it step by step in technical terms — what to plug where — like a learning process.”
- **Rationale**: “Alternatives and why we chose this approach.”

This repo already has “two-thirds” of that:

- **PO/User-flow style docs (what happens, step-by-step)**: `docs/Functionality/*`
  - Example: signup, login, add balance, checkout/order.
- **Service + architecture docs (technical, but still high-level)**:
  - `docs/Services/*` (per-service responsibilities, APIs, etc.)
  - `docs/diagram/*` (system + low-level design explanations)
- **Strategy / planning** (product/priorities, “why this product”): `docs/product-documents/*`, plus `docs/PRODUCT_STRATEGY.md`

What’s *not* present as a **single read-through narrative** is:

- “Here’s the story of the app, then the exact code path (functions), then the tradeoffs.”

That’s what this document provides.

---

## 1. The product, in plain language (MVP scope)

This MVP is an e-commerce “skeleton” that focuses on learning:

- **Users can register and login**
- **Users have a profile + wallet**
  - They can **add balance**
  - Wallet is used as the payment method in checkout
- **Users can browse an organic product catalog** (fruits, vegetables, grains, dairy, herbs)
- **Users can build a cart** (currently frontend-only)
- **Users can place an order**
  - Stock is reserved
  - Payment is processed
  - Failures trigger “undo” steps (refund)
- **Users can view order history**

In other words: it’s the minimum set of workflows that lets you practice “real” microservice coordination and error handling, using the domain of certified organic food.

---

## 2. The system, at a glance (architecture)

### The big picture

- **Frontend**: React SPA (`frontend/`)
- **Gateway**: an ASP.NET Core reverse proxy (`gateway/`)
- **Backend services** (`services/`):
  - `auth-service`: user credentials + JWT
  - `user-service`: user profile + wallet
  - `product-service`: organic products + stock + certifications
  - `order-service`: orchestrates checkout/order workflow
  - `payment-service`: processes wallet payments + records transactions
- **Data**: SQL Server; “database-per-service” pattern (each service has its own database)

### Why a gateway exists at all

A gateway exists so the frontend can call *one* base URL, and the gateway decides which service should receive the request. That keeps the frontend simpler and isolates service port details.

In this repo, the gateway loads one of two config files:

- `gateway/ocelot.json`
- `gateway/ocelot.docker.json`

Even though the filenames say “ocelot”, the gateway is actually using **YARP reverse proxy** (`AddReverseProxy().LoadFromConfig(...)`).

---

## 3. “User journeys” = the epic/PO-level story

If you want the **PO-level** understanding, read these documents in order:

1. `docs/Functionality/SIGNUP_FLOW.md`
2. `docs/Functionality/LOGIN_FLOW.md`
3. `docs/Functionality/ADD_TO_CART_FLOW.md`
4. `docs/Functionality/ADD_BALANCE_FLOW.md`
5. `docs/Functionality/CHECKOUT_ORDER_FLOW.md`
6. `docs/Functionality/ORDER_HISTORY_FLOW.md`

The key “epic-level” capabilities in MVP terms are:

- **Identity epic**: signup + login (Auth Service)
- **Customer account epic**: profile + wallet top-up (User Service)
- **Catalog epic**: view organic products with certifications (Product Service)
- **Purchase epic**: checkout/order (Order + Payment + Product + User services)
- **Post-purchase epic**: view order history (Order Service)

---

## 4. From “what happens” to “what code runs” (request lifecycle)

Every feature in this repo follows a similar “path”:

1. **React UI** triggers an HTTP call
2. Request hits the **Gateway**
3. Gateway forwards request to the correct service (Auth/User/Product/Order/Payment)
4. Service controller validates input and runs business logic
5. Service updates its **own** database (EF Core + SQL Server)
6. Response flows back to the UI

Some workflows also include **service-to-service calls** (backend calling backend). That’s where things get interesting.

---

## 5. Code tour (the important functions and why they exist)

This section is your “map of the code”.

### 5.1 Gateway — how requests get routed

Files:

- `gateway/Program.cs`
- `gateway/Startup.cs`

Key responsibilities:

- Decide whether to load `ocelot.json` or `ocelot.docker.json` based on `USE_DOCKER_NETWORK`.
- Configure YARP with `LoadFromConfig(_config.GetSection("ReverseProxy"))`.
- Expose Swagger for the gateway itself (development).

Why this matters:

- A beginner often gets lost because requests “disappear”. In a microservices app, the first debugging question is: **did the gateway route to the service you expect?**

---

### 5.2 Auth Service — registration and login are a workflow, not just a DB insert

Key file:

- `services/auth-service/Controllers/AuthController.cs`

#### `Register(...)`

What it does:

- Validates input (name/email/password/phone).
- Checks for duplicate email in **Auth DB**.
- Checks for duplicate phone via **User Service**.
- Creates auth user (stores hashed password).
- Calls **User Service** to create the user profile.
- If profile creation fails, it **rolls back** the auth user (deletes it).

Why it’s designed this way:

- In microservices, “create user” spans multiple databases. This repo uses an **orchestrated workflow** + **compensation (rollback)** to keep things consistent.

What to learn here:

- Input validation patterns
- “Check external dependency before committing state”
- Compensating actions when cross-service operations fail

#### `Login(...)`

What it does:

- Validates input.
- Looks up user by email.
- Verifies password hash (BCrypt).
- Issues a JWT via `IJwtService`.

What to learn:

- Auth is “validate then issue token”
- Passwords are never stored in plaintext

---

### 5.3 User Service — wallet is just another domain rule

Key file:

- `services/user-service/Controllers/UsersController.cs`

Important endpoints:

- `POST /api/users` — create profile (called by Auth during signup)
- `GET /api/users/by-userid/{userId}` — fetch profile by Auth user id
- `POST /api/users/add-balance` — “top up” using userId
- `POST /api/users/{id}/wallet/debit` — debit wallet (used by Payment Service)
- `POST /api/users/{id}/wallet/credit` — credit wallet (used for refunds)

What to learn:

- The wallet is intentionally implemented in the **User Service** (it “owns” user finances).
- The controller is thin; real business rules should live in the service layer (`IUserService`).

---

### 5.4 Product Service — stock reservation is a concurrency problem

Key file:

- `services/product-service/Controllers/ProductsController.cs`

Important endpoints:

- `GET /api/products` — list organic products
- `GET /api/products/{id}` — get organic product details with certifications
- `POST /api/products` — create product (with validation)
- `POST /api/products/{id}/reserve` — reserve stock (decrement)
- `POST /api/products/{id}/release` — release stock (increment; used by compensation/rollback flows)

What to learn:

- Stock reservation is the “resource lock” pattern in organic food e-commerce, especially important for perishable items.
- In real production you’d worry about race conditions; EF Core + a single DB transaction is the first step.

---

### 5.5 Payment Service — wallet debit + transaction record

Key file:

- `services/payment-service/Controllers/PaymentsController.cs`

#### `ProcessPayment(...)`

What it does:

- Validates amount.
- Calls User Service to **debit wallet**.
  - If insufficient funds → returns `409 Conflict`.
  - If user not found → `404 NotFound`.
  - If user service down → `503`.
- Records a `PaymentRecord` in Payment DB as “Paid”.

Why it’s separated from User Service:

- The **Payment Service** becomes the system’s “payment ledger”.
- User Service owns the wallet balance; Payment Service owns the payment history/audit trail.

#### `RefundPayment(...)`

What it does:

- Calls User Service to **credit wallet back**.
- Records a negative payment record marked “Refunded”.

What to learn:

- Refunds are part of the same workflow, not an afterthought.

---

### 5.6 Order Service — the orchestrator (where “checkout” actually happens)

Key file:

- `services/order-service/Controllers/OrdersController.cs`

#### `CreateOrder(...)` (the heart of the app)

This method is the “story of checkout”:

1. Validates items exist
2. Calls User Service to get user profile (because wallet debit uses profile id)
3. For each item:
   - Calls Product Service to get product
   - Checks stock
   - Builds total price
4. Calls Payment Service to process payment
5. Reserves stock in Product Service
6. Creates the order record in Order DB
7. If reservation fails after payment:
   - Calls Payment Service to refund

What to learn:

- This is a simplified **Saga-like orchestration** (sequence + compensations).
- Notice the order: “validate → pay → reserve → persist order”. That’s a design choice with tradeoffs (see next chapter).

---

## 6. Decisions, alternatives, and tradeoffs (why this way?)

### 6.1 Microservices vs monolith

- **Chosen**: microservices (Auth/User/Product/Order/Payment)
- **Why**: learning service boundaries, inter-service HTTP, compensation patterns
- **Alternative**: a modular monolith (simpler, fewer network failures)

### 6.2 Database-per-service

- **Chosen**: each service has its own DB
- **Why**: enforces boundaries and mirrors real production patterns
- **Alternative**: shared DB (easier joins/reporting, but tighter coupling)

### 6.3 JWT auth

- **Chosen**: JWT token (stateless)
- **Why**: common for SPAs + APIs; good learning value
- **Alternative**: server sessions + cookies (simpler for some apps; different security concerns)

### 6.4 “Checkout order” sequencing

The current order flow uses a temporary order id for payment processing, then creates the final order record later.

- **Why it works**: lets Payment Service record a transaction before the order exists in Order DB.
- **Tradeoff**: the Payment record may reference an order id that never becomes a “real” Order entity (if later steps fail).
- **Alternative A**: create Order first as `Pending`, then process payment, then reserve stock, then mark `Completed`.
- **Alternative B**: use an outbox + saga orchestrator (more advanced, more reliable; more code).

---

## 7. How to study this repo like a developer (a repeatable method)

When you want to understand any feature:

1. Start with the **user flow doc** in `docs/Functionality/`.
2. Identify which service “owns” the feature (look at the API endpoint).
3. Open the controller method handling it (search for the route).
4. For that method, write down:
   - **Inputs** (DTOs, route params)
   - **Validation**
   - **Dependencies** (DbContext, HttpClients)
   - **Side effects** (DB writes, external calls)
   - **Failure modes** and how they’re handled
5. Repeat for every downstream service call.

If you do this consistently, you stop “copying code” and start *seeing systems*.

---

## 8. Learning exercises (guided practice)

These are designed so you learn the “why”:

### Exercise 1 — draw the checkout workflow

On paper, draw the exact sequence from `OrdersController.CreateOrder(...)`:

- Which service is called first?
- Where can it fail?
- What does the system do to “undo” the failure?

### Exercise 2 — pick one method and write its contract

Choose one method (example: `PaymentsController.ProcessPayment`) and write:

- Preconditions (what must be true before calling)
- Postconditions (what must be true after success)
- Failure cases and the exact HTTP status codes

### Exercise 3 — propose a safer “order state” design

Design an alternative flow where you:

- Create the order as `Pending`
- Process payment
- Reserve stock
- Mark order as `Completed` or `Failed`

Then compare tradeoffs with the current design.

---

## Where to go next

- If you want **PO-level storytelling**: continue with `docs/Functionality/*`.
- If you want **technical depth per service**: `docs/Services/*`.
- If you want **big-picture architecture**: `docs/diagram/architecture.md` and `docs/diagram/low-level-design.md`.

