# 🛒 Order Service - Complete Documentation

**Order Management & Orchestration Microservice**

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Architecture & Design](#2-architecture--design)
3. [Database Schema](#3-database-schema)
4. [API Endpoints](#4-api-endpoints)
5. [Business Logic Deep Dive](#5-business-logic-deep-dive)
6. [Order Orchestration](#6-order-orchestration)
7. [Service-to-Service Communication](#7-service-to-service-communication)
8. [Configuration](#8-configuration)
9. [Code Walkthrough](#9-code-walkthrough)
10. [Error Handling & Rollback](#10-error-handling--rollback)
11. [Best Practices](#11-best-practices)

---

## 1. Service Overview

### Purpose

The **Order Service** is the **orchestrator** for the entire order creation process:

- Validates product availability
- Processes payments via Payment Service
- Reserves stock via Product Service
- Creates order records
- Handles rollbacks on failures
- Provides order history

### Key Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Order Orchestration** | Coordinate multi-service order flow |
| **Payment Processing** | Call Payment Service for wallet debit |
| **Stock Reservation** | Call Product Service for inventory |
| **Order Creation** | Store order and order items |
| **Rollback Management** | Refund payment on failure |
| **Order History** | Retrieve user's past orders |

### Technology Stack

- **.NET 8** - Framework
- **Entity Framework Core** - ORM
- **SQL Server** - Database (orderdb)
- **HttpClientFactory** - Service communication
- **Saga Pattern** - Distributed transaction management

### Port & Database

- **Port**: `5004`
- **Database**: `orderdb`
- **Docker Service Name**: `order-service`

---

## 2. Architecture & Design

### High-Level Architecture

```
┌──────────────────────────────────────────────┐
│            Frontend (React)                  │
│  User clicks "Checkout" with cart items     │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│          API Gateway (YARP)                  │
│  POST /api/orders/create                     │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│       Order Service (Port 5004)              │
│       **ORCHESTRATOR**                       │
│                                              │
│  Orchestrates:                               │
│  1. Get user profile (User Service)         │
│  2. Validate products (Product Service)     │
│  3. Process payment (Payment Service)       │
│  4. Reserve stock (Product Service)         │
│  5. Create order record (orderdb)           │
│                                              │
│  On Failure:                                 │
│  - Refund payment (Payment Service)         │
│  - Release stock (Product Service)          │
└───────┬──────────┬──────────┬────────────────┘
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │  User  │ │Product │ │Payment │
   │Service │ │Service │ │Service │
   │ :5005  │ │ :5002  │ │ :5003  │
   └────────┘ └────────┘ └────────┘
        │
        ▼
   ┌────────────────┐
   │  SQL Server    │
   │  orderdb       │
   │                │
   │  Orders        │
   │  OrderItems    │
   └────────────────┘
```

### Service Dependencies

**Depends On:**
- **User Service** (get user profile)
- **Product Service** (product info, stock reservation/release)
- **Payment Service** (payment processing, refunds)

**Depended On By:**
- **Frontend via Gateway** (order creation, order history)

### Design Patterns

1. **Saga Pattern** - Orchestrated distributed transaction
2. **Compensation** - Rollback on failure (refund, release stock)
3. **Orchestrator Pattern** - Order Service coordinates all steps
4. **HttpClient Factory** - Manage HTTP connections
5. **DTO Pattern** - Data transfer objects

---

## 3. Database Schema

### Database: `orderdb`

### Table: `Orders`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | Guid | PRIMARY KEY, DEFAULT NEWID() | Order unique identifier |
| `UserId` | Guid | NOT NULL | Auth service user ID |
| `TotalAmount` | int | NOT NULL | Total in paise (₹1 = 100 paise) |
| `CreatedAt` | datetime2 | DEFAULT GETUTCDATE() | Order timestamp |

### Table: `OrderItems`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | Guid | PRIMARY KEY, DEFAULT NEWID() | Item unique identifier |
| `OrderId` | Guid | FOREIGN KEY → Orders(Id) | Parent order |
| `ProductId` | Guid | NOT NULL | Product identifier |
| `Quantity` | int | NOT NULL | Quantity purchased |
| `UnitPrice` | int | NOT NULL | Price per unit in paise |

### Entity Models

```csharp
public class Order
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public int TotalAmount { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public ICollection<OrderItem> Items { get; set; } = new List<OrderItem>();
}

public class OrderItem
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid OrderId { get; set; }
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
    public int UnitPrice { get; set; }
}
```

### Key Characteristics

- **Guid Primary Keys**: Unique IDs across all entities
- **Foreign Key**: OrderItems → Orders
- **Integer Amounts**: Stored in paise to avoid floating-point issues
- **No Product Details**: Only ProductId stored (reference data)
- **Denormalized Price**: UnitPrice stored to preserve historical price

### Indexes

```sql
CREATE INDEX IX_Orders_UserId ON Orders(UserId);
CREATE INDEX IX_Orders_CreatedAt ON Orders(CreatedAt DESC);
CREATE INDEX IX_OrderItems_OrderId ON OrderItems(OrderId);
```

---

## 4. API Endpoints

### Base Path: `/api/orders`

### 1. **POST /api/orders/create** - Create Order

**Description**: Create a new order (orchestrates entire checkout flow)

**Request Body**:

```json
{
  "userId": "user-guid",
  "items": [
    {
      "productId": "product-guid-1",
      "quantity": 2
    },
    {
      "productId": "product-guid-2",
      "quantity": 1
    }
  ]
}
```

**Validation Rules**:
- ✅ UserId: Required (Guid)
- ✅ Items: Required, not empty
- ✅ Each item: ProductId (Guid), Quantity (>0)

**Success Response (201 Created)**:

```json
{
  "id": "order-guid",
  "userId": "user-guid",
  "totalAmount": 4997
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | Order must contain items | Empty items array |
| `404` | Product not found | Invalid product ID |
| `404` | User profile not found | Invalid user ID |
| `409` | Insufficient stock | Product out of stock |
| `409` | Payment failed - insufficient balance | Wallet balance < total |
| `500` | Order creation failed | Internal error, payment refunded |

---

### 2. **GET /api/orders/{id}** - Get Order by ID

**Description**: Get order details by order ID

**Parameters**:
- `id` (Guid) - Order ID

**Success Response (200 OK)**:

```json
{
  "id": "order-guid",
  "userId": "user-guid",
  "totalAmount": 4997,
  "createdAt": "2025-12-24T10:30:00Z",
  "items": [
    {
      "id": "item-guid-1",
      "orderId": "order-guid",
      "productId": "product-guid-1",
      "quantity": 2,
      "unitPrice": 1999
    },
    {
      "id": "item-guid-2",
      "orderId": "order-guid",
      "productId": "product-guid-2",
      "quantity": 1,
      "unitPrice": 999
    }
  ]
}
```

**Error Responses**:

| Status | Description |
|--------|-------------|
| `404` | Order not found |

---

### 3. **GET /api/orders/user/{userId}** - Get User's Orders

**Description**: Get all orders for a specific user (order history)

**Parameters**:
- `userId` (Guid) - Auth service user ID

**Success Response (200 OK)**:

```json
[
  {
    "id": "order-guid-1",
    "userId": "user-guid",
    "totalAmount": 4997,
    "createdAt": "2025-12-24T10:30:00Z",
    "items": [
      {
        "id": "item-guid-1",
        "orderId": "order-guid-1",
        "productId": "product-guid-1",
        "quantity": 2,
        "unitPrice": 1999
      }
    ]
  },
  {
    "id": "order-guid-2",
    "userId": "user-guid",
    "totalAmount": 999,
    "createdAt": "2025-12-23T15:20:00Z",
    "items": [...]
  }
]
```

**Note**: Orders returned in descending order (newest first)

**Error Responses**:

| Status | Description |
|--------|-------------|
| `200` | Empty array if no orders |

---

## 5. Business Logic Deep Dive

### Order Creation Flow (Saga Pattern)

```
Step 0: Get User Profile
   ├─ GET /api/users/by-userid/{userId}
   ├─ Extract profile ID (needed for wallet operations)
   └─ If not found → 404

Step 1: Validate Products & Calculate Total
   For each item:
   ├─ GET /api/products/{productId}
   ├─ Check product exists
   ├─ Validate stock >= quantity
   ├─ Collect price
   └─ Calculate total: sum(price × quantity)

Step 2: Process Payment (via Payment Service)
   ├─ POST /api/payments/process
   ├─ Body: { orderId, userId, userProfileId, amount }
   ├─ Payment Service debits wallet
   ├─ If insufficient balance → 409 (abort)
   └─ If success → continue

Step 3: Reserve Stock (for each product)
   ├─ POST /api/products/{productId}/reserve
   ├─ Body: { quantity }
   ├─ If insufficient stock:
   │   ├─ Refund payment (POST /api/payments/refund)
   │   └─ Return 409 (abort)
   └─ If success → track reserved items

Step 4: Create Order Record
   ├─ Create Order entity (userId, totalAmount)
   ├─ Create OrderItem entities
   ├─ Save to orderdb
   └─ Return 201 Created

On Any Failure After Payment:
   ├─ POST /api/payments/refund
   └─ Return error response
```

---

## 6. Order Orchestration

### Complete Code Implementation

```csharp
[HttpPost("create")]
public async Task<IActionResult> CreateOrder(CreateOrderDto dto)
{
    if (dto.Items == null || !dto.Items.Any()) 
        return BadRequest(new { error = "Order must contain items" });
    
    var productClient = _http.CreateClient("product");
    var paymentClient = _http.CreateClient("payment");
    var userClient = _http.CreateClient("user");
    
    // Step 0: Get user profile
    var userProfileResp = await userClient.GetAsync($"/api/users/by-userid/{dto.UserId}");
    if (userProfileResp.StatusCode == HttpStatusCode.NotFound) 
        return NotFound(new { error = "User profile not found" });
    
    var userProfile = await userProfileResp.Content.ReadFromJsonAsync<UserProfileDto>();
    if (userProfile == null) 
        return StatusCode(500, new { error = "Failed to read user profile" });
    
    // Step 1: Validate products and calculate total
    int total = 0;
    var productInfos = new List<(Guid productId, int quantity, int unitPrice)>();
    
    foreach (var item in dto.Items)
    {
        var res = await productClient.GetAsync($"/api/products/{item.ProductId}");
        if (res.StatusCode == HttpStatusCode.NotFound) 
            return NotFound(new { error = "Product not found", productId = item.ProductId });
        
        var product = await res.Content.ReadFromJsonAsync<ProductDto>();
        if (product == null) 
            return StatusCode(500, new { error = "Failed to read product info" });
        
        if (product.Stock < item.Quantity) 
            return Conflict(new { error = "Insufficient stock", 
                productId = item.ProductId, available = product.Stock });
        
        total += product.Price * item.Quantity;
        productInfos.Add((item.ProductId, item.Quantity, product.Price));
    }
    
    // Step 2: Process payment
    var tempOrderId = Guid.NewGuid();
    var paymentResp = await paymentClient.PostAsJsonAsync("/api/payments/process", new 
    { 
        OrderId = tempOrderId,
        UserId = dto.UserId,
        UserProfileId = userProfile.Id,
        Amount = total 
    });
    
    if (paymentResp.StatusCode == HttpStatusCode.Conflict)
    {
        var body = await paymentResp.Content.ReadFromJsonAsync<object>();
        return Conflict(new { error = "Payment failed - insufficient balance", details = body });
    }
    
    if (!paymentResp.IsSuccessStatusCode) 
        return StatusCode((int)paymentResp.StatusCode, new { error = "Payment processing failed" });
    
    // Step 3: Reserve stock for each product
    var reserved = new List<(Guid productId, int quantity)>();
    foreach (var p in productInfos)
    {
        var res = await productClient.PostAsJsonAsync($"/api/products/{p.productId}/reserve", 
            new { Quantity = p.quantity });
        
        if (!res.IsSuccessStatusCode)
        {
            // Rollback: Refund payment
            await paymentClient.PostAsJsonAsync("/api/payments/refund", new 
            { 
                OrderId = tempOrderId,
                UserId = dto.UserId,
                UserProfileId = userProfile.Id,
                Amount = total 
            });
            
            var body = await res.Content.ReadFromJsonAsync<object>();
            return Conflict(new { error = "Reservation failed", details = body });
        }
        
        reserved.Add((p.productId, p.quantity));
    }
    
    // Step 4: Create order record
    var order = new Order { UserId = dto.UserId, TotalAmount = total };
    foreach (var r in productInfos)
    {
        order.Items.Add(new OrderItem 
        { 
            ProductId = r.productId, 
            Quantity = r.quantity, 
            UnitPrice = r.unitPrice 
        });
    }
    
    _db.Orders.Add(order);
    await _db.SaveChangesAsync();
    
    return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, 
        new { order.Id, order.UserId, order.TotalAmount });
}
```

---

## 7. Service-to-Service Communication

### HttpClient Configuration

**Startup.cs**:

```csharp
// User Service client
services.AddHttpClient("user", client =>
{
    var userServiceUrl = Configuration.GetValue<string>("ServiceUrls:UserService");
    client.BaseAddress = new Uri(userServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(30);
});

// Product Service client
services.AddHttpClient("product", client =>
{
    var productServiceUrl = Configuration.GetValue<string>("ServiceUrls:ProductService");
    client.BaseAddress = new Uri(productServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(30);
});

// Payment Service client
services.AddHttpClient("payment", client =>
{
    var paymentServiceUrl = Configuration.GetValue<string>("ServiceUrls:PaymentService");
    client.BaseAddress = new Uri(paymentServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(30);
});
```

### Service Calls Summary

| Service | Endpoint | Purpose |
|---------|----------|---------|
| **User Service** | `GET /api/users/by-userid/{userId}` | Get profile ID |
| **Product Service** | `GET /api/products/{id}` | Validate product, get price |
| **Product Service** | `POST /api/products/{id}/reserve` | Reserve stock |
| **Product Service** | `POST /api/products/{id}/release` | Release stock (unused) |
| **Payment Service** | `POST /api/payments/process` | Debit wallet |
| **Payment Service** | `POST /api/payments/refund` | Refund payment |

---

## 8. Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost,1433;Database=orderdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;"
  },
  "ServiceUrls": {
    "UserService": "http://localhost:5005",
    "ProductService": "http://localhost:5002",
    "PaymentService": "http://localhost:5003"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

### Docker Configuration

**docker-compose.yml**:

```yaml
order-service:
  build:
    context: ../services/order-service
    dockerfile: Dockerfile
  ports:
    - "5004:80"
  environment:
    - ASPNETCORE_ENVIRONMENT=Development
    - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=orderdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;
    - ServiceUrls__UserService=http://user-service:80
    - ServiceUrls__ProductService=http://product-service:80
    - ServiceUrls__PaymentService=http://payment-service:80
  depends_on:
    - sqlserver
    - user-service
    - product-service
    - payment-service
  networks:
    - ecommerce-network
```

---

## 9. Code Walkthrough

### Project Structure

```
order-service/
├── Controllers/
│   └── OrdersController.cs         # API endpoints + orchestration
├── Models/ (in Program.cs)
│   ├── Order.cs                    # Order entity
│   └── OrderItem.cs                # OrderItem entity
├── Dtos/
│   ├── CreateOrderDto.cs           # Order creation request
│   ├── OrderItemDto.cs             # Order item in request
│   ├── ProductDto.cs               # Product response from Product Service
│   └── UserProfileDto.cs           # User profile from User Service
├── Data/
│   └── AppDbContext.cs             # EF Core context
├── Startup.cs                      # Service + HttpClient configuration
├── Program.cs                      # Application entry + models
└── order-service.csproj            # Project file
```

### DTOs for Service Communication

```csharp
public record CreateOrderDto(Guid UserId, List<OrderItemDto> Items);
public record OrderItemDto(Guid ProductId, int Quantity);
public record ProductDto(Guid Id, string Name, string? Description, int Price, int Stock);
public record UserProfileDto(Guid Id, Guid UserId, string? Name, string? Email, 
    string? PhoneNumber, decimal WalletBalance);
```

---

## 10. Error Handling & Rollback

### Rollback Scenarios

| Scenario | Action Taken |
|----------|--------------|
| **User profile not found** | Abort immediately (404) |
| **Product not found** | Abort immediately (404) |
| **Insufficient stock** | Abort immediately (409) |
| **Payment failed** | Abort immediately (409) |
| **Stock reservation failed** | Refund payment, return 409 |
| **Order save failed** | Refund payment, return 500 |

### Compensation Logic

```csharp
// After payment success, if stock reservation fails:
if (!stockReservationSuccessful)
{
    // Compensate: Refund payment
    await paymentClient.PostAsJsonAsync("/api/payments/refund", new 
    { 
        OrderId = tempOrderId,
        UserId = dto.UserId,
        UserProfileId = userProfile.Id,
        Amount = total 
    });
    
    return Conflict(new { error = "Stock reservation failed. Payment refunded." });
}
```

### Logging Strategy

```csharp
// Log each major step
_logger.LogInformation("Starting order creation for user {UserId}", dto.UserId);
_logger.LogInformation("Payment processed successfully for order {OrderId}", tempOrderId);
_logger.LogInformation("Stock reserved for {Count} products", productInfos.Count);
_logger.LogInformation("Order {OrderId} created successfully", order.Id);

// Log errors
_logger.LogError("Payment failed for user {UserId}: {StatusCode}", 
    dto.UserId, paymentResp.StatusCode);
_logger.LogError("Stock reservation failed, payment refunded for order {OrderId}", tempOrderId);
```

---

## 11. Best Practices

### ✅ Orchestration Pattern

1. **Single Orchestrator**: Order Service coordinates all services
2. **Saga Pattern**: Multi-step distributed transaction
3. **Compensation**: Always rollback on failure
4. **Idempotency**: Support retries safely (future enhancement)

### ✅ Error Handling

1. **Early Validation**: Check products and stock before payment
2. **Payment Before Stock**: Ensure funds available before reserving
3. **Rollback Logic**: Always refund payment on subsequent failures
4. **Detailed Errors**: Return specific error messages

### ✅ Service Communication

1. **HttpClientFactory**: Use for connection pooling
2. **Timeouts**: Set reasonable timeouts
3. **Status Codes**: Check and handle all HTTP status codes
4. **Retry Logic**: Consider implementing (future enhancement)

### ✅ Data Consistency

1. **Denormalize Price**: Store unit price in OrderItem
2. **Guid Consistency**: All IDs are Guid
3. **UTC Timestamps**: Always use UTC
4. **Foreign Keys**: Enforce referential integrity

---

## 12. Future Enhancements

### Suggested Improvements

1. **Order Status**
   - Add `Status` field (Pending, Confirmed, Shipped, Delivered, Cancelled)
   - Support order status updates
   - Track order lifecycle

2. **Idempotency**
   - Add `IdempotencyKey` to prevent duplicate orders
   - Return existing order if duplicate request

3. **Async Processing**
   - Use message queue (RabbitMQ, Azure Service Bus)
   - Process orders asynchronously
   - Better scalability

4. **Circuit Breaker**
   - Implement Polly for resilience
   - Circuit breaker for service calls
   - Automatic retries with backoff

5. **Distributed Transactions**
   - Consider 2-Phase Commit
   - Or event sourcing pattern
   - Or CQRS pattern

6. **Order Cancellation**
   - Allow users to cancel orders
   - Refund payment
   - Release stock

7. **Order Tracking**
   - Add shipping information
   - Track delivery status
   - Notifications

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Service Port:** 5004  
**Database:** orderdb  
**Pattern:** Saga Orchestrator  
**Author:** MVP E-Commerce Team


