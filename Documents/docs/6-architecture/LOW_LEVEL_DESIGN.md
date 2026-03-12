
---

## 2. Low-level Design Doc – `docs/low-level-design.md`

```markdown
# FreshHarvest Market – Low-level Design

## 1. Code Structure (Per Service)

Each microservice follows a similar structure:

- `Controllers/` – ASP.NET Core API controllers
- `Models/` – Domain entities (e.g., `Product`, `Order`, `Wallet`)
- `Dtos/` – Request/response DTOs
- `Data/` – EF Core `DbContext` (e.g., `ProductDbContext`, `OrderDbContext`)
- `Repositories/` – Data access abstraction
- `Services/` – Business logic and orchestration
- `Program.cs` / `Startup.cs` – DI setup, middleware pipeline, Swagger

### 1.1 Layered Pattern (per service)

- **Controller layer**
  - Handles HTTP concerns: routing, model binding, validation attributes
  - Calls **service layer** interfaces

- **Service layer**
  - Business rules, validation, orchestration
  - Depends on repository and external HTTP clients
  - Example interfaces:
    - `IProductService`
    - `IOrderService`
    - `IPaymentService`

- **Repository layer**
  - Encapsulates EF Core queries and transactions
  - Example interfaces:
    - `IProductRepository`
    - `IOrderRepository`
    - `IWalletRepository`

- **Data layer**
  - EF Core DbContexts + entity configurations
  - Runs migrations / schema initialization

---

## 2. Dependency Injection

### 2.1 Registration

In each service:

- Register DbContext:
  - `services.AddDbContext<ProductDbContext>(options => options.UseSqlServer(Configuration.GetConnectionString("DefaultConnection")));`
- Register repositories:
  - `services.AddScoped<IProductRepository, ProductRepository>();`
- Register business services:
  - `services.AddScoped<IProductService, ProductService>();`
- Register HTTP clients (Order service):
  - `services.AddHttpClient<IProductClient, ProductClient>(...)`
  - `services.AddHttpClient<IPaymentClient, PaymentClient>(...)`

Controllers take only **interfaces** as constructor dependencies.

---

## 3. Order Service – Detailed Behavior

### 3.1 Order Creation Flow (Happy Path)

1. **Controller** (`OrdersController.CreateOrder`)
   - Validates request DTO (items, quantities)
   - Extracts `UserId` from JWT claims
   - Calls `IOrderService.CreateOrderAsync(...)`

2. **Service** (`OrderService.CreateOrderAsync`)
   - Validates business rules (e.g., total > 0, items not empty)
   - For each line item:
     - Calls Product client: `POST /api/products/{id}/reserve`
   - Calls Payment client: `POST /api/payments/charge`
   - On success:
     - Creates `Order` entity with status `Completed`
     - Saves via `IOrderRepository`

3. **Repository** (`OrderRepository`)
   - Uses `OrderDbContext` within a transaction
   - Persists `Order` + `OrderItems`

### 3.2 Failure + Compensation

- If any product reservation **fails**:
  - Do not call payment
  - Return meaningful error to client
- If payment fails **after** reservation:
  - Trigger **compensation**:
    - Call Product service to release inventory
  - Persist order with `Failed` status (optional design choice)

> Future: replace manual compensation with **saga** / **outbox** pattern.

---

## 4. HTTP Clients (Inter-service Communication)

### 4.1 Configuration

Order service uses `HttpClientFactory`:

- Typed clients for:
  - Product service
  - Payment service
- Base addresses:
  - Through **gateway** (recommended for symmetry with external clients), or
  - Direct container DNS name in docker network (e.g. `http://product-service`)

### 4.2 Resilience (Future)

- Add:
  - Retry policies (e.g., Polly)
  - Timeouts
  - Circuit breakers

---

## 5. Security & Auth (Low Level)

### 5.1 Auth Service

- Exposes:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
- Uses:
  - `BCrypt.Net-Next` for password hashing
  - `JwtSecurityTokenHandler` for JWT creation
- JWT contents (typical):
  - `sub`: user id
  - `email`
  - `exp`: expiry

### 5.2 Other Services

- Configure `JwtBearer` middleware:
  - Validate:
    - Issuer
    - Audience
    - Signing key
- Controllers:
  - Mark protected endpoints with `[Authorize]`
  - Extract user id from `User.Claims`

---

## 6. EF Core & Transactions

### 6.1 Per-service transactions

- Repository methods use `DbContext` transactions for local consistency
- Example:
  - Product reservation: check stock, decrement stock, commit

### 6.2 Cross-service workflows

- There is **no distributed transaction** across services
- Consistency managed by:
  - Request ordering
  - Compensating actions (release stock)
- Future:
  - **Outbox** pattern to publish domain events reliably
  - **Saga orchestrator** to drive multi-step workflows

---

## 7. Logging, Monitoring, and Health

### 7.1 Health Endpoints

- API gateway exposes `/api/health` used by:
  - Smoke tests
  - CI pipeline

### 7.2 Logging (Baseline)

- Use ASP.NET Core logging abstractions
- Log at:
  - Controller entry for key operations
  - Service layer for major decision branches
  - Error handling paths

> Future: integrate structured logging + distributed tracing.

---

## 8. Test Strategy

### 8.1 Unit Tests

- Service layer tests:
  - Mock repositories and HTTP clients
  - Verify business rules (e.g., no order with zero items)
- Repository tests:
  - Use in-memory or test SQL database

### 8.2 Integration / Smoke Tests

- Existing script: `infra/smoke-test.sh`
  - Spin up full stack via `docker compose`
  - Exercises:
    - Health check
    - Register + login
    - Wallet creation
    - Product listing
    - Order creation

> CI should run smoke tests on each main branch build.

