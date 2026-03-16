# Engineering Playbook — FreshHarvest Market Patterns & Decisions (Practical, Layman-Friendly)

This document answers questions like:

- “If I connect two microservices, should I use **HTTP** or a **service bus**? Why?”
- “If we build an **organic product catalog**, what patterns should we apply and what’s the benefit?”
- “How do we keep data consistent across services without a shared database?”

It’s written for people learning enterprise systems: **simple language first**, then the deeper technical reasoning.

---

## 1) How to connect microservices: HTTP vs Service Bus (decision guide)

### 1.1 Plain-language summary

- **HTTP** is like a phone call: you ask a question and you wait for the answer **right now**.
- A **service bus / message queue** is like leaving a voicemail: you send a message, the other service processes it **when it can**, and you might get a separate reply later.

Both are valid. The “best” choice depends on what the user experience and consistency requirements are.

---

### 1.2 Use HTTP when…

You should prefer **HTTP (sync request/response)** when:

- The **user is waiting** on the screen for the result (login, checkout validation, “show me my orders”).
- You need an immediate **success/failure** answer.
- The operation is naturally a “query” (read) or a simple “command” (write) with low fan-out.
- You need **stronger consistency** (or at least immediate confirmation).

**Examples in this repo (already using HTTP):**

- Auth Service calling User Service to check phone uniqueness during registration.
- Order Service calling Product Service + Payment Service during checkout.

**Benefits**

- Easier to understand and debug.
- Simpler infrastructure (no broker required).
- Immediate error handling is straightforward.

**Costs**

- More runtime coupling: if Service B is down, Service A may fail right now.
- More “distributed failure” cases: timeouts, partial results, retries.

---

### 1.3 Use a service bus when…

You should prefer **async messaging** (RabbitMQ, Azure Service Bus, Kafka, etc.) when:

- The user **does not need to wait** (notifications, analytics, “send email”, “update search index”).
- You want **decoupling**: Service A can keep working even if Service B is down.
- You need to handle **bursty load** (queue smooths spikes).
- The action is a “fact” that happened: *OrderCreated*, *PaymentSucceeded*, *ProductUpdated*.

**Benefits**

- Better resilience and scalability.
- Services become less dependent on each other’s uptime.
- Works well for event-driven systems and background processing.

**Costs (the “enterprise complexity tax”)**

- You must handle duplicates (at-least-once delivery is common) → **idempotency** is mandatory.
- You must handle out-of-order messages and eventual consistency.
- Debugging requires broker visibility and correlation IDs.

---

### 1.4 A practical decision tree (quick)

Pick **HTTP** if:

- “User is waiting” OR “I need an answer right now” OR “I must block the workflow on this result”.

Pick **service bus** if:

- “Work can happen later” OR “I’m broadcasting an event” OR “I want to decouple and tolerate downtime”.

Hybrid is common:

- Use HTTP for the critical synchronous path (checkout confirmation).
- Publish events for side effects (email receipt, update search index, metrics).

---

## 2) “We need an organic product catalog next” — recommended patterns and why

Catalog seems simple (“list products”), but it becomes hard when you add:

- search, filters (certifications, origin, freshness), sorting, pagination
- price changes, stock changes, seasonal promotions
- high traffic and caching
- freshness tracking and expiry alerts
- eventual consistency (search index lags behind source-of-truth)

### 2.1 What we have now (MVP)

Today, the catalog is handled by **Product Service**:

- single database (`productdb`)
- simple REST endpoints
- repository + service layer pattern
- stock reservation/release endpoints for checkout workflows

This is correct for MVP learning.

---

### 2.2 Next-step catalog patterns (useful and realistic)

#### A) Pagination + filtering contracts

**Pattern**

- Add explicit query parameters (page/size, cursor, sort, filters).

**Why**

- Prevents “load everything” endpoints.
- Enables UI scalability.

**Benefit**

- Performance and a stable API contract for UI.

---

#### B) CQRS (Command Query Responsibility Segregation) — *when it starts to hurt*

**Pattern**

- Split “write model” (Product Service DB) from “read model” optimized for queries (projection table, cache, or search index).

**Why**

- Catalog reads become complex and expensive; writes need strong rules.

**Benefit**

- Faster reads, simpler domain rules, easier scaling.

**When not to do it**

- If you only have a small catalog and simple queries—CQRS is extra moving parts.

---

#### C) Search indexing (Elasticsearch / OpenSearch) + events

**Pattern**

- Product Service remains the **source of truth**.
- Product changes emit events like *ProductCreated/Updated/Deleted*.
- A “Search Indexer” consumer updates a search index.

**Why**

- SQL is great for transactions; dedicated search engines are better for search relevance and full-text queries.

**Benefit**

- Fast, flexible search with good UX.

**Tradeoff**

- Search becomes **eventually consistent** (a product update may take seconds to appear in search).

---

#### D) Cache-aside for hot catalog reads

**Pattern**

- UI or BFF calls Catalog API.
- Cache stores common responses; on cache miss → fetch from Product Service and store.

**Why**

- Catalog reads are often repetitive.

**Benefit**

- Lower DB load, faster UI.

**Risk**

- Stale cache if invalidation is wrong (use TTLs and versioning).

---

## 3) Keeping cross-service data consistent (without shared DB)

This project already demonstrates a core idea: **distributed workflows need compensation**.

### 3.1 What pattern we use now (MVP)

- **Saga-like orchestration** in Order Service:
  - validate → payment → reserve stock → create order
  - if later step fails → refund (compensation)

This is intentionally understandable and good for learning.

---

### 3.2 What you’ll need as the system grows

#### A) Idempotency (must-have)

**Problem**

- Retries happen (timeouts, network failure, client retry).
- With async messaging, duplicates are normal.

**Pattern**

- Use an **Idempotency Key** per request (or per message).
- Store processed keys/results and return the previous result for duplicates.

**Benefit**

- Prevents double-charging, double-ordering, double-reserving stock.

---

#### B) Outbox pattern (reliable events)

**Problem**

- “I saved to DB, then I tried to publish an event, and the publish failed.”

**Pattern**

- Save “domain event” into an `Outbox` table in the same DB transaction as your business change.
- A background worker publishes outbox events to the message broker.

**Benefit**

- You don’t lose events and you don’t publish events for changes that never committed.

---

## 4) Where to put aggregation logic (UI vs BFF vs domain service)

This repo’s gateway doc already explains options; here’s the short rule:

- **Frontend aggregation**: small screens, 2–3 calls, simple.
- **BFF (Backend for Frontend)**: when UI becomes complex (recommended evolution).
- **Domain service aggregation**: only when it’s part of the domain workflow (e.g., checkout orchestration).

---

## 5) How to use this playbook during development

When you add a feature, ask:

1. Is the user waiting for this result?
   - Yes → HTTP path
   - No → async messaging can be better
2. Does it create side effects in multiple services?
   - If yes → plan for compensation + idempotency (and later outbox)
3. Is read complexity growing (catalog/search)?
   - If yes → consider CQRS + indexing + caching

---

## Related docs

- Role-based navigation: [`START_HERE.md`](START_HERE.md)
- Definitions of terms: [`GLOSSARY.md`](GLOSSARY.md)
- Gateway and aggregation options: [`Services/API_GATEWAY.md`](Services/API_GATEWAY.md)
- Orchestration example: [`Services/ORDER_SERVICE.md`](Services/ORDER_SERVICE.md)

