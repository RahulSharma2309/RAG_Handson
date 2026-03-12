# Checkout & Order Creation Flow - Request Journey

This document explains how requests flow through the system when a user places an order.

## Architecture Overview

```
Frontend (React) → API Gateway → Order Service → Payment Service → User Service
                                        ↓              ↓
                                  Product Service  (Wallet debit)
```

## Complete Checkout Flow

### Step 1: User Reviews Cart (Frontend)

- **Location**: `frontend/src/components/Cart.js` or `frontend/src/App.js`
- User has items in cart (stored in React state)
- Each cart item has: `productId`, `quantity`, `price`
- User clicks "Checkout" button

### Step 2: Frontend Sends Order Request

- **Request**: `POST /api/orders/create`
- **Destination**: API Gateway (http://localhost:5000)
- **Payload**:
  ```json
  {
    "UserId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",  // Guid
    "Items": [
      {
        "ProductId": "bb89025b-260f-4b91-87e9-47b5fee317b3",
        "Quantity": 2
      },
      {
        "ProductId": "94008857-1534-4b14-8b17-de71f68ce301",
        "Quantity": 1
      }
    ]
  }
  ```

### Step 3: API Gateway Routes Request

- Gateway receives: `POST /api/orders/create`
- Route matching: Path matches `/api/orders/{**catch-all}`
- Cluster: Routes to `orderCluster`
- **Forwarded to**: Order Service
  - Local dev: `http://localhost:5004/api/orders/create`
  - Docker: `http://order-service:80/api/orders/create`

### Step 4: Order Service Processing

**Location**: `services/order-service/Controllers/OrdersController.cs`

#### 4a. Validate Input

- Checks that order has items
- Returns `400 Bad Request` if empty

#### 4b. Get User Profile

- **Request**: `GET /api/users/by-userid/{userId}`
- **Destination**: User Service (direct HTTP call)
- **Purpose**: Get user's internal profile ID (Guid) and wallet balance
- **Response**:
  ```json
  {
    "id": "99e05c86-1665-4ddf-897f-7d4f222ab808",  // Internal profile ID
    "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
    "firstName": "John",
    "walletBalance": 600000.00
  }
  ```
- If user not found → Returns `404 Not Found`

#### 4c. Validate Products & Stock

For each item in order:

- **Request**: `GET /api/products/{productId}`
- **Destination**: Product Service (direct HTTP call)
- **Validates**:
  - Product exists (if not → Returns `404 Not Found`)
  - Sufficient stock available (if not → Returns `409 Conflict`)
- **Collects**:
  - Product price
  - Product details
- **Calculates**: Total amount (sum of: quantity × price for each item)

#### 4d. Process Payment via Payment Service

**This is the key integration - Payment Service handles wallet debit AND records transaction**

- **Request**: `POST /api/payments/process`
- **Destination**: Payment Service (direct HTTP call)
- **Payload**:
  ```json
  {
    "OrderId": "temp-order-id-guid",  // Temporary ID
    "UserId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
    "Amount": 5997.00
  }
  ```

**Payment Service Processing** (`services/payment-service/Controllers/PaymentsController.cs`):

1. **Debit Wallet via User Service**:
   - `POST /api/users/{userId}/wallet/debit`
   - Deducts amount from user's wallet
   - If insufficient balance → Returns `409 Conflict`
   - If user not found → Returns `404 Not Found`

2. **Record Payment Transaction**:
   - Creates `PaymentRecord` in Payment Service database:
     ```csharp
     {
       Id: Guid (auto-generated),
       OrderId: tempOrderId,
       UserId: userId,
       Amount: 5997.00,
       Status: "Paid",
       Timestamp: DateTime.UtcNow
     }
     ```
   - Saves to `paymentdb`

3. **Return Success**:
   ```json
   {
     "paymentId": "payment-record-guid",
     "orderId": "temp-order-id-guid",
     "amount": 5997.00,
     "status": "Paid"
   }
   ```

**Payment Error Handling**:
- If payment fails (insufficient balance) → Order Service returns `409 Conflict` to frontend
- If User Service unavailable → Returns `503 Service Unavailable`

#### 4e. Reserve Stock in Product Service

For each item (only if payment successful):

- **Request**: `POST /api/products/{productId}/reserve`
- **Destination**: Product Service (direct HTTP call)
- **Payload**: `{ "Quantity": 2 }`
- **Action**: Decrements product stock
- **Rollback**: If reservation fails:
  1. **Refund Payment via Payment Service**:
     - `POST /api/payments/refund`
     - Credits wallet back via User Service
     - Records refund transaction
  2. Returns `409 Conflict` with error details

#### 4f. Create Order Record

- Creates `Order` in Order Service database:
  ```csharp
  {
    Id: Guid (auto-generated),
    UserId: "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",  // Guid
    TotalAmount: 5997,
    CreatedAt: DateTime.UtcNow,
    Items: [
      {
        Id: Guid (auto-generated),
        ProductId: "bb89025b-260f-4b91-87e9-47b5fee317b3",
        Quantity: 2,
        UnitPrice: 1999
      },
      {
        Id: Guid (auto-generated),
        ProductId: "94008857-1534-4b14-8b17-de71f68ce301",
        Quantity: 1,
        UnitPrice: 1999
      }
    ]
  }
  ```
- Saves to Order Service database (orderdb)

#### 4g. Return Response

- **Response**: `201 Created`
- **Body**:
  ```json
  {
    "id": "order-guid",
    "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
    "totalAmount": 5997
  }
  ```

### Step 5: Frontend Processes Response

**Location**: `frontend/src/components/Cart.js` and `frontend/src/App.js`

#### 5a. Success Actions

- Shows success message: "Order placed successfully!"
- Clears cart (removes all items from state)
- Refreshes products list (to show updated stock)
- Refreshes wallet balance (to show deducted amount)

#### 5b. Error Handling

- Insufficient balance: "Payment failed - insufficient balance"
- Out of stock: "Reservation failed - insufficient stock"
- Other errors: "Order failed - please try again"

## Request Flow Diagram

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 1. POST /api/orders/create
       │    { UserId (Guid), Items[] }
       ▼
┌─────────────────────┐
│   API Gateway       │
└──────┬──────────────┘
       │ 2. Route to Order Service
       ▼
┌─────────────────────────────────────────────────────────┐
│   Order Service                                         │
│   Port: 5004, Database: orderdb                         │
└──────┬──────────────────────────────────────────────────┘
       │ 3a. Get User Profile
       │     ┌────────────────────────────────┐
       │     │ GET /api/users/by-userid/{id}  │
       │     ▼                                 │
       │  ┌───────────────┐                   │
       │  │ User Service  │                   │
       │  └───────────────┘                   │
       │     │ Response: { id, walletBalance } │
       │     └─────────────────────────────────┘
       │
       │ 3b. Validate Products & Stock
       │     ┌──────────────────────────────────┐
       │     │ GET /api/products/{id} (each)    │
       │     ▼                                   │
       │  ┌──────────────────┐                  │
       │  │ Product Service  │                  │
       │  └──────────────────┘                  │
       │     │ Response: { price, stock }       │
       │     └───────────────────────────────────┘
       │
       │ 3c. Process Payment (CRITICAL STEP)
       │     ┌─────────────────────────────────────────┐
       │     │ POST /api/payments/process              │
       │     │ { orderId, userId, userProfileId, amt } │
       │     ▼                                         │
       │  ┌─────────────────────┐                     │
       │  │  Payment Service    │                     │
       │  │  Port: 5003         │                     │
       │  └──────┬──────────────┘                     │
       │         │ 1) Debit wallet via User Service   │
       │         │    POST /users/{id}/wallet/debit   │
       │         │    ▼                                │
       │         │ ┌───────────────┐                  │
       │         │ │ User Service  │                  │
       │         │ │ Updates wallet│                  │
       │         │ └───────────────┘                  │
       │         │                                     │
       │         │ 2) Record payment in paymentdb     │
       │         │    PaymentRecord { orderId, amt }  │
       │         │                                     │
       │         │ Response: { paymentId, status }    │
       │         └─────────────────────────────────────┘
       │
       │ 3d. Reserve Stock (if payment successful)
       │     ┌──────────────────────────────────────┐
       │     │ POST /api/products/{id}/reserve      │
       │     │ { Quantity }                         │
       │     ▼                                       │
       │  ┌──────────────────┐                      │
       │  │ Product Service  │                      │
       │  │ Decrements stock │                      │
       │  └──────────────────┘                      │
       │     │ If fails → Refund via Payment Service│
       │     │    POST /api/payments/refund         │
       │     └───────────────────────────────────────┘
       │
       │ 3e. Create Order in orderdb
       │     Order { id, userId, totalAmount, items[] }
       │
       │ 3f. Return response
       ▼
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 4. Success actions
       │    - Show success message
       │    - Clear cart
       │    - Refresh products & wallet
       ▼
```

## Key Points

1. **Multi-Service Orchestration**:
   - Order Service orchestrates calls to 3 other services
   - User Service: Get profile, debit wallet
   - Product Service: Validate products, reserve stock
   - Payment Service: Process payment, record transaction

2. **Payment Service Integration**:
   - **NEW**: Payment Service now handles all wallet operations
   - Debits wallet via User Service
   - Records every transaction in `paymentdb`
   - Provides audit trail of all payments

3. **Transaction Flow**:
   - Check stock → Process payment → Reserve stock → Create order
   - Each step can fail and triggers rollback

4. **Rollback Mechanism**:
   - If stock reservation fails AFTER payment:
     - Payment Service refunds the wallet
     - Records refund transaction
     - Order is not created

5. **Data Consistency**:
   - All IDs are `Guid` type for type safety
   - Payment records link orders to transactions
   - Wallet balance updated atomically

6. **Error Handling**:
   - Insufficient balance (409): Payment Service returns conflict
   - Out of stock (409): Product Service returns conflict, payment refunded
   - Service unavailable (503): Returns error, no partial operations

7. **Idempotency**:
   - Each order gets unique ID
   - Payment records prevent duplicate charges
   - Stock reservations are atomic

8. **Audit Trail**:
   - Every payment is recorded in `paymentdb`
   - Order details stored in `orderdb`
   - Can track: who paid what, when, for which order


