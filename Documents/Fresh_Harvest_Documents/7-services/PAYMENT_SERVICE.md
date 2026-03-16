# 💳 Payment Service - Complete Documentation

**Payment Processing & Wallet Management Microservice**

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Architecture & Design](#2-architecture--design)
3. [Database Schema](#3-database-schema)
4. [API Endpoints](#4-api-endpoints)
5. [Business Logic Deep Dive](#5-business-logic-deep-dive)
6. [Payment Processing Flow](#6-payment-processing-flow)
7. [Service-to-Service Communication](#7-service-to-service-communication)
8. [Configuration](#8-configuration)
9. [Code Walkthrough](#9-code-walkthrough)
10. [Error Handling](#10-error-handling)
11. [Best Practices](#11-best-practices)

---

## 1. Service Overview

### Purpose

The **Payment Service** acts as the **orchestrator for all payment operations**:

- Process payments (debit wallet via User Service)
- Record all payment transactions
- Handle refunds (credit wallet via User Service)
- Maintain payment history
- Provide payment status information

### Key Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Payment Processing** | Orchestrate wallet debit via User Service |
| **Transaction Recording** | Store all payment records in paymentdb |
| **Refund Handling** | Orchestrate wallet credit for refunds |
| **Payment History** | Track all transactions |
| **Status Management** | Maintain payment status (Paid, Refunded) |

### Technology Stack

- **.NET 8** - Framework
- **Entity Framework Core** - ORM
- **SQL Server** - Database (paymentdb)
- **HttpClientFactory** - Service communication

### Port & Database

- **Port**: `5003`
- **Database**: `paymentdb`
- **Docker Service Name**: `payment-service`

---

## 2. Architecture & Design

### High-Level Architecture

```
┌──────────────────────────────────────────────┐
│       Order Service (Port 5004)              │
│  Orchestrator for order creation            │
│                                              │
│  Calls Payment Service for:                  │
│  • Process payment (wallet debit)           │
│  • Refund payment (on order failure)        │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│      Payment Service (Port 5003)             │
│      **Payment Orchestrator**                │
│                                              │
│  Responsibilities:                           │
│  1. Orchestrate wallet operations           │
│  2. Record payment transactions             │
│  3. Handle refunds                          │
│                                              │
│  Controllers:                                │
│  • PaymentsController - /api/payments/*     │
│                                              │
│  Data:                                       │
│  • AppDbContext - EF Core                   │
│  • PaymentRecord entity                      │
│  • Wallet entity (legacy)                   │
└───────────────────┬──────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌────────────────┐    ┌────────────────┐
│  User Service  │    │  SQL Server    │
│  Port: 5005    │    │  paymentdb     │
│                │    │                │
│  Wallet:       │    │  PaymentRecords│
│  • Debit       │    │  Wallets (legacy)│
│  • Credit      │    └────────────────┘
└────────────────┘
```

### Service Dependencies

**Depends On:**
- **User Service** (wallet debit/credit operations)

**Depended On By:**
- **Order Service** (payment processing, refunds)

### Design Patterns

1. **Orchestrator Pattern** - Payment Service coordinates wallet operations
2. **Transaction Recording** - Every payment operation recorded
3. **HttpClient Factory** - Manage HTTP connections
4. **DTO Pattern** - Data transfer objects for API contracts

---

## 3. Database Schema

### Database: `paymentdb`

### Table: `PaymentRecords`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | Guid | PRIMARY KEY, DEFAULT NEWID() | Payment record identifier |
| `OrderId` | Guid | NOT NULL | Associated order ID |
| `UserId` | Guid | NOT NULL | Auth service user ID |
| `Amount` | int | NOT NULL | Amount in paise (₹1 = 100 paise) |
| `Status` | nvarchar(50) | NOT NULL | Payment status (Paid, Refunded) |
| `Timestamp` | datetime2 | DEFAULT GETUTCDATE() | Transaction timestamp |

### Table: `Wallets` (Legacy)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | Guid | PRIMARY KEY | Wallet identifier |
| `UserId` | Guid | UNIQUE, NOT NULL | User identifier |
| `Balance` | int | NOT NULL, DEFAULT 0 | Balance in paise |

**⚠️ Note**: The `Wallets` table is **legacy** and not actively used. Wallet management is now handled by the User Service. This table remains for backward compatibility and migration purposes.

### Entity Models

```csharp
public class PaymentRecord
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid OrderId { get; set; }
    public Guid UserId { get; set; }
    public int Amount { get; set; }  // In paise
    public string Status { get; set; } = "Paid";  // "Paid" or "Refunded"
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

// Legacy - not used
public class Wallet
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public int Balance { get; set; }  // In paise
}
```

### Key Characteristics

- **Integer Amount**: Stored in paise to avoid floating-point issues
- **Status Tracking**: "Paid" for successful payments, "Refunded" for refunds
- **Negative Amounts**: Refunds stored with negative amount
- **UTC Timestamps**: All timestamps in UTC
- **Order Association**: Every payment linked to an order

### Indexes

```sql
CREATE INDEX IX_PaymentRecords_OrderId ON PaymentRecords(OrderId);
CREATE INDEX IX_PaymentRecords_UserId ON PaymentRecords(UserId);
CREATE INDEX IX_PaymentRecords_Timestamp ON PaymentRecords(Timestamp DESC);
```

---

## 4. API Endpoints

### Base Path: `/api/payments`

### 1. **POST /api/payments/process** - Process Payment

**Description**: Process payment by debiting wallet and recording transaction

**Request Body**:

```json
{
  "orderId": "order-guid",
  "userId": "user-guid",
  "userProfileId": "profile-guid",
  "amount": 4997
}
```

**Validation Rules**:
- ✅ Amount: Must be > 0
- ✅ OrderId, UserId, UserProfileId: Required (Guid)

**Success Response (200 OK)**:

```json
{
  "paymentId": "payment-guid",
  "orderId": "order-guid",
  "userId": "user-guid",
  "amount": 4997,
  "status": "Paid",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | Amount must be greater than 0 | Invalid amount |
| `404` | User not found | Invalid userProfileId |
| `409` | Insufficient wallet balance | Wallet balance < amount |
| `503` | User Service unavailable | Cannot reach User Service |

**Flow**:
1. Debit wallet via User Service
2. If successful, record payment in paymentdb
3. Return payment details

---

### 2. **POST /api/payments/refund** - Refund Payment

**Description**: Refund payment by crediting wallet

**Request Body**:

```json
{
  "orderId": "order-guid",
  "userId": "user-guid",
  "userProfileId": "profile-guid",
  "amount": 4997
}
```

**Validation Rules**:
- ✅ Amount: Must be > 0
- ✅ OrderId, UserId, UserProfileId: Required (Guid)

**Success Response (200 OK)**:

```json
{
  "paymentId": "payment-guid",
  "orderId": "order-guid",
  "userId": "user-guid",
  "amount": -4997,
  "status": "Refunded",
  "timestamp": "2025-12-24T10:35:00Z"
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | Amount must be greater than 0 | Invalid amount |
| `404` | User not found | Invalid userProfileId |
| `503` | User Service unavailable | Cannot reach User Service |

**Flow**:
1. Credit wallet via User Service
2. Record refund in paymentdb (negative amount)
3. Return refund details

---

### 3. **POST /api/payments/record** - Record Payment (Legacy)

**Description**: Record a payment transaction (legacy endpoint, kept for compatibility)

**Request Body**:

```json
{
  "orderId": "order-guid",
  "userId": "user-guid",
  "amount": 4997,
  "status": "Paid"
}
```

**Success Response (200 OK)**:

```json
{
  "orderId": "order-guid",
  "userId": "user-guid",
  "amount": 4997,
  "status": "Paid",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

**⚠️ Note**: This endpoint only records the payment. It does NOT debit the wallet. Use `/process` instead for complete payment processing.

---

### 4. **GET /api/payments/status/{orderId}** - Get Payment Status

**Description**: Get payment status for an order

**Parameters**:
- `orderId` (Guid) - Order ID

**Success Response (200 OK)**:

```json
{
  "orderId": "order-guid",
  "status": "Paid",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Description |
|--------|-------------|
| `404` | Payment not found for this order |

---

## 5. Business Logic Deep Dive

### Payment Processing Flow

```
1. Validate Input
   ├─ Amount > 0
   └─ All GUIDs provided

2. Create HttpClient for User Service
   └─ Use HttpClientFactory

3. Debit Wallet via User Service
   ├─ POST /api/users/{userProfileId}/wallet/debit
   ├─ Body: { amount }
   │
   ├─ If 404 → User not found
   ├─ If 409 → Insufficient balance
   ├─ If 503 → User Service unavailable
   └─ If success → Continue

4. Record Payment Transaction
   ├─ Create PaymentRecord entity
   ├─ OrderId = dto.OrderId
   ├─ UserId = dto.UserId
   ├─ Amount = dto.Amount
   ├─ Status = "Paid"
   └─ Timestamp = UtcNow

5. Save to Database
   └─ EF Core SaveChangesAsync()

6. Return Payment Details
   └─ Include paymentId, orderId, userId, amount, status, timestamp
```

### Code Implementation

```csharp
[HttpPost("process")]
public async Task<IActionResult> ProcessPayment(ProcessPaymentDto dto)
{
    if (dto.Amount <= 0) 
        return BadRequest(new { error = "Amount must be greater than 0" });
    
    var userClient = _httpClientFactory.CreateClient("user");
    
    try
    {
        // 1. Debit wallet via User Service
        var debitResponse = await userClient.PostAsJsonAsync(
            $"/api/users/{dto.UserProfileId}/wallet/debit", 
            new { Amount = dto.Amount }
        );
        
        if (debitResponse.StatusCode == HttpStatusCode.NotFound)
        {
            return NotFound(new { error = "User not found" });
        }
        
        if (debitResponse.StatusCode == HttpStatusCode.Conflict)
        {
            var conflictBody = await debitResponse.Content.ReadFromJsonAsync<object>();
            return Conflict(new { error = "Insufficient wallet balance", details = conflictBody });
        }
        
        if (!debitResponse.IsSuccessStatusCode)
        {
            _logger.LogError("User Service wallet debit failed with status {StatusCode}", 
                debitResponse.StatusCode);
            return StatusCode((int)debitResponse.StatusCode, new { error = "Wallet debit failed" });
        }
        
        // 2. Wallet debited successfully - record payment
        var payment = new PaymentRecord
        {
            OrderId = dto.OrderId,
            UserId = dto.UserId,
            Amount = dto.Amount,
            Status = "Paid",
            Timestamp = DateTime.UtcNow
        };
        
        _db.Payments.Add(payment);
        await _db.SaveChangesAsync();
        
        _logger.LogInformation("Payment processed successfully for Order {OrderId}, Amount: {Amount}", 
            dto.OrderId, dto.Amount);
        
        return Ok(new 
        { 
            paymentId = payment.Id,
            orderId = payment.OrderId, 
            userId = payment.UserId, 
            amount = payment.Amount, 
            status = payment.Status, 
            timestamp = payment.Timestamp 
        });
    }
    catch (HttpRequestException ex)
    {
        _logger.LogError(ex, "Failed to communicate with User Service");
        return StatusCode(503, new { error = "User Service unavailable" });
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Payment processing failed for Order {OrderId}", dto.OrderId);
        return StatusCode(500, new { error = "Payment processing failed" });
    }
}
```

---

## 6. Payment Processing Flow

### Refund Flow

```
1. Validate Input
   ├─ Amount > 0
   └─ All GUIDs provided

2. Create HttpClient for User Service
   └─ Use HttpClientFactory

3. Credit Wallet via User Service
   ├─ POST /api/users/{userProfileId}/wallet/credit
   ├─ Body: { amount }
   │
   ├─ If error → Log and continue (best effort)
   └─ If success → Continue

4. Record Refund Transaction
   ├─ Create PaymentRecord entity
   ├─ OrderId = dto.OrderId
   ├─ UserId = dto.UserId
   ├─ Amount = -dto.Amount (negative!)
   ├─ Status = "Refunded"
   └─ Timestamp = UtcNow

5. Save to Database
   └─ EF Core SaveChangesAsync()

6. Return Refund Details
   └─ Include paymentId, orderId, userId, amount, status, timestamp
```

### Code Implementation

```csharp
[HttpPost("refund")]
public async Task<IActionResult> RefundPayment(RefundPaymentDto dto)
{
    if (dto.Amount <= 0) 
        return BadRequest(new { error = "Amount must be greater than 0" });
    
    var userClient = _httpClientFactory.CreateClient("user");
    
    try
    {
        // 1. Credit the wallet back
        var creditResponse = await userClient.PostAsJsonAsync(
            $"/api/users/{dto.UserProfileId}/wallet/credit", 
            new { Amount = dto.Amount }
        );
        
        if (!creditResponse.IsSuccessStatusCode)
        {
            _logger.LogError("User Service wallet credit (refund) failed with status {StatusCode}", 
                creditResponse.StatusCode);
            // Continue to record refund even if wallet credit fails
            // This ensures we have a record of the attempted refund
        }
        
        // 2. Record refund payment entry
        var refundPayment = new PaymentRecord
        {
            OrderId = dto.OrderId,
            UserId = dto.UserId,
            Amount = -dto.Amount,  // Negative to indicate refund
            Status = "Refunded",
            Timestamp = DateTime.UtcNow
        };
        
        _db.Payments.Add(refundPayment);
        await _db.SaveChangesAsync();
        
        _logger.LogInformation("Payment refunded successfully for Order {OrderId}, Amount: {Amount}", 
            dto.OrderId, dto.Amount);
        
        return Ok(new 
        { 
            paymentId = refundPayment.Id,
            orderId = refundPayment.OrderId, 
            userId = refundPayment.UserId, 
            amount = refundPayment.Amount, 
            status = refundPayment.Status, 
            timestamp = refundPayment.Timestamp 
        });
    }
    catch (HttpRequestException ex)
    {
        _logger.LogError(ex, "Failed to communicate with User Service for refund");
        return StatusCode(503, new { error = "User Service unavailable" });
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Refund processing failed for Order {OrderId}", dto.OrderId);
        return StatusCode(500, new { error = "Refund processing failed" });
    }
}
```

---

## 7. Service-to-Service Communication

### HttpClient Configuration

**Startup.cs**:

```csharp
services.AddHttpClient("user", client =>
{
    var userServiceUrl = Configuration.GetValue<string>("ServiceUrls:UserService");
    client.BaseAddress = new Uri(userServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(30);
});
```

### Service Calls

#### To User Service

1. **Debit Wallet**:
   ```
   POST /api/users/{id}/wallet/debit
   Body: { amount: 4997 }
   Response: { id, balance }
   ```

2. **Credit Wallet**:
   ```
   POST /api/users/{id}/wallet/credit
   Body: { amount: 4997 }
   Response: { id, balance }
   ```

### Incoming Calls

#### From Order Service

1. **Process Payment**:
   ```
   POST /api/payments/process
   Body: { orderId, userId, userProfileId, amount }
   ```

2. **Refund Payment**:
   ```
   POST /api/payments/refund
   Body: { orderId, userId, userProfileId, amount }
   ```

---

## 8. Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost,1433;Database=paymentdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;"
  },
  "ServiceUrls": {
    "UserService": "http://localhost:5005"
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
payment-service:
  build:
    context: ../services/payment-service
    dockerfile: Dockerfile
  ports:
    - "5003:80"
  environment:
    - ASPNETCORE_ENVIRONMENT=Development
    - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=paymentdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;
    - ServiceUrls__UserService=http://user-service:80
  depends_on:
    - sqlserver
    - user-service
  networks:
    - ecommerce-network
```

---

## 9. Code Walkthrough

### Project Structure

```
payment-service/
├── Controllers/
│   └── PaymentsController.cs       # API endpoints
├── Models/ (in Program.cs)
│   ├── PaymentRecord.cs            # Payment record entity
│   └── Wallet.cs                   # Wallet entity (legacy)
├── Dtos/
│   ├── ProcessPaymentDto.cs        # Process payment request
│   ├── RefundPaymentDto.cs         # Refund request
│   └── RecordPaymentDto.cs         # Record payment request (legacy)
├── Data/
│   └── AppDbContext.cs             # EF Core context
├── Startup.cs                      # Service + HttpClient configuration
├── Program.cs                      # Application entry + models
└── payment-service.csproj          # Project file
```

### DTOs

```csharp
public record ProcessPaymentDto(Guid OrderId, Guid UserId, Guid UserProfileId, int Amount);
public record RefundPaymentDto(Guid OrderId, Guid UserId, Guid UserProfileId, int Amount);
public record RecordPaymentDto(Guid OrderId, Guid UserId, int Amount, string Status);
```

---

## 10. Error Handling

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "details": { ... }
}
```

### Common Errors

| Scenario | Status Code | Response |
|----------|-------------|----------|
| Invalid amount | 400 | `{ "error": "Amount must be greater than 0" }` |
| User not found | 404 | `{ "error": "User not found" }` |
| Insufficient balance | 409 | `{ "error": "Insufficient wallet balance", "details": {...} }` |
| User Service down | 503 | `{ "error": "User Service unavailable" }` |
| Payment processing failed | 500 | `{ "error": "Payment processing failed" }` |

### Exception Handling

```csharp
try
{
    // Process payment
}
catch (HttpRequestException ex)
{
    _logger.LogError(ex, "Failed to communicate with User Service");
    return StatusCode(503, new { error = "User Service unavailable" });
}
catch (Exception ex)
{
    _logger.LogError(ex, "Payment processing failed for Order {OrderId}", dto.OrderId);
    return StatusCode(500, new { error = "Payment processing failed" });
}
```

---

## 11. Best Practices

### ✅ Payment Processing

1. **Atomic Operations**: Debit wallet first, then record payment
2. **Transaction Recording**: Always record payment/refund in paymentdb
3. **Error Handling**: Handle all User Service error responses
4. **Logging**: Log all payment operations for audit

### ✅ Refund Handling

1. **Best Effort**: Continue recording refund even if wallet credit fails
2. **Negative Amounts**: Use negative amount to indicate refund
3. **Status Tracking**: Use "Refunded" status
4. **Audit Trail**: Maintain complete refund history

### ✅ Service Communication

1. **HttpClientFactory**: Use for connection pooling
2. **Timeouts**: Set reasonable timeouts (30 seconds)
3. **Status Codes**: Check and handle all HTTP status codes
4. **Retry Logic**: Consider implementing (future enhancement)

### ✅ Data Consistency

1. **Integer Amounts**: Store in paise to avoid floating-point issues
2. **UTC Timestamps**: Always use UTC
3. **Guid Consistency**: All IDs are Guid
4. **Foreign Keys**: Link payments to orders

---

## 12. Future Enhancements

### Suggested Improvements

1. **Payment Methods**
   - Support multiple payment methods (card, UPI, etc.)
   - Payment gateway integration (Razorpay, Stripe)
   - Payment method selection

2. **Payment Status Updates**
   - Support pending payments
   - Async payment confirmation
   - Webhook handling

3. **Idempotency**
   - Add `IdempotencyKey` to prevent duplicate charges
   - Return existing payment if duplicate request

4. **Payment History**
   - User-facing payment history API
   - Pagination and filtering
   - Export to PDF/CSV

5. **Fraud Detection**
   - Velocity checks (max amount per hour)
   - Suspicious activity detection
   - Admin alerts

6. **Retry Logic**
   - Implement Polly for resilience
   - Automatic retries with backoff
   - Circuit breaker pattern

7. **Audit Logging**
   - Enhanced audit trail
   - Who performed what action
   - IP address tracking

8. **Remove Legacy Wallet Table**
   - Migrate any remaining data
   - Drop `Wallets` table
   - Clean up codebase

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Service Port:** 5003  
**Database:** paymentdb  
**Pattern:** Payment Orchestrator  
**Author:** MVP E-Commerce Team


