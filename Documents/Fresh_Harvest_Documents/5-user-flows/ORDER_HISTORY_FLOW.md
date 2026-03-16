# Order History Flow - Request Journey

This document explains how requests flow through the system when a user views their order history.

## Architecture Overview

```
Frontend (React) → API Gateway → Order Service
```

## Complete Order History Flow

### Step 1: User Navigates to Orders Page (Frontend)

- **Location**: User clicks "Orders" button in header
- **Route**: `/orders`
- **Component**: `frontend/src/components/OrderHistory.js`
- **Protected Route**: Requires authentication

### Step 2: Frontend Fetches Order History

- **Request**: `GET /api/orders/user/{userId}`
- **Destination**: API Gateway (http://localhost:5000)
- **Headers**: `Authorization: Bearer {token}`
- **URL Parameter**: `userId` - Guid of logged-in user

### Step 3: API Gateway Routes Request

- Gateway receives: `GET /api/orders/user/{userId}`
- Route matching: Path matches `/api/orders/{**catch-all}`
- Cluster: Routes to `orderCluster`
- **Forwarded to**: Order Service
  - Local dev: `http://localhost:5004/api/orders/user/{userId}`
  - Docker: `http://order-service:80/api/orders/user/{userId}`

### Step 4: Order Service Retrieves Orders

**Location**: `services/order-service/Controllers/OrdersController.cs`

#### 4a. Query Database

- Queries Order Service database:
  ```sql
  SELECT o.*, oi.*
  FROM Orders o
  LEFT JOIN OrderItems oi ON o.Id = oi.OrderId
  WHERE o.UserId = @userId
  ORDER BY o.CreatedAt DESC
  ```
- Includes related order items (using Entity Framework `Include`)
- Orders sorted by creation date (newest first)

#### 4b. Return Response

- **Response**: `200 OK`
- **Body**: Array of orders
  ```json
  [
    {
      "id": "order-guid-1",
      "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
      "totalAmount": 5997,
      "createdAt": "2025-12-24T10:30:00Z",
      "items": [
        {
          "id": "item-guid-1",
          "orderId": "order-guid-1",
          "productId": "product-guid-1",
          "quantity": 2,
          "unitPrice": 1999
        },
        {
          "id": "item-guid-2",
          "orderId": "order-guid-1",
          "productId": "product-guid-2",
          "quantity": 1,
          "unitPrice": 1999
        }
      ]
    },
    {
      "id": "order-guid-2",
      "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
      "totalAmount": 1999,
      "createdAt": "2025-12-23T15:20:00Z",
      "items": [...]
    }
  ]
  ```

### Step 5: Frontend Processes and Displays Orders

**Location**: `frontend/src/components/OrderHistory.js`

#### 5a. Store Orders in State

- Stores raw orders in `orders` state
- Creates copy in `filteredOrders` state for filtering/sorting

#### 5b. Display Order Cards

For each order:
- **Order Header**:
  - Order ID (first 8 characters)
  - Creation date (formatted: "Dec 24, 2025, 10:30 AM")

- **Order Items Table**:
  - Product ID, Quantity, Unit Price, Subtotal
  - Formatted as table with headers

- **Order Footer**:
  - Total Amount (large, highlighted)

#### 5c. Filtering System

**Filters Available**:

1. **Amount Range**:
   - Min Amount input (₹)
   - Max Amount input (₹)
   - Filters orders where: `minAmount <= totalAmount <= maxAmount`

2. **Date Range**:
   - Start Date picker
   - End Date picker
   - Filters orders where: `startDate <= createdAt <= endDate`
   - End date includes full day (23:59:59)

**Implementation**:
```javascript
// Apply filters
let filtered = [...orders];

if (minAmount) {
  filtered = filtered.filter(order => order.totalAmount >= parseFloat(minAmount));
}
if (maxAmount) {
  filtered = filtered.filter(order => order.totalAmount <= parseFloat(maxAmount));
}
if (startDate) {
  filtered = filtered.filter(order => new Date(order.createdAt) >= new Date(startDate));
}
if (endDate) {
  const endDateTime = new Date(endDate);
  endDateTime.setHours(23, 59, 59, 999);
  filtered = filtered.filter(order => new Date(order.createdAt) <= endDateTime);
}
```

#### 5d. Sorting System

**Sort Options**:

1. **Date (Newest First)** - Default
   - `ORDER BY createdAt DESC`

2. **Date (Oldest First)**
   - `ORDER BY createdAt ASC`

3. **Amount (High to Low)**
   - `ORDER BY totalAmount DESC`

4. **Amount (Low to High)**
   - `ORDER BY totalAmount ASC`

**Implementation**:
```javascript
filtered.sort((a, b) => {
  switch (sortBy) {
    case "date-desc":
      return new Date(b.createdAt) - new Date(a.createdAt);
    case "date-asc":
      return new Date(a.createdAt) - new Date(b.createdAt);
    case "amount-desc":
      return b.totalAmount - a.totalAmount;
    case "amount-asc":
      return a.totalAmount - b.totalAmount;
  }
});
```

#### 5e. Real-time Updates

- Filters and sorting applied **client-side**
- No additional API calls needed
- Instant updates as user changes filters
- Shows count: "Showing X of Y orders"

#### 5f. Clear Filters Button

- Resets all filters to default:
  - Clears min/max amount
  - Clears date range
  - Resets sort to "Date (Newest First)"

### Step 6: Empty States

- **No Orders**: "No orders found matching your filters."
- **Loading**: "Loading order history..."
- **Error**: Shows error message from API

## Request Flow Diagram

```
┌─────────────┐
│   Frontend  │
│  /orders    │
└──────┬──────┘
       │ 1. Component mounts
       │    useEffect(() => fetchOrders(), [userId])
       │
       │ 2. GET /api/orders/user/{userId}
       │    Headers: { Authorization: Bearer token }
       ▼
┌─────────────────────┐
│   API Gateway       │
│   Port: 5000        │
└──────┬──────────────┘
       │ 3. Route to Order Service
       ▼
┌─────────────────────┐
│   Order Service     │
│   Port: 5004        │
│   Database: orderdb │
└──────┬──────────────┘
       │ 4. Query database
       │    SELECT Orders with Items
       │    WHERE UserId = @userId
       │    ORDER BY CreatedAt DESC
       │
       │ 5. Return orders array
       ▼
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 6. Store in state:
       │    - orders (raw data)
       │    - filteredOrders (for display)
       │
       │ 7. Apply filters & sorting (client-side)
       │    - Amount range filter
       │    - Date range filter
       │    - Sort by date/amount
       │
       │ 8. Render order cards
       │    - Order header (ID, date)
       │    - Items table
       │    - Total amount
       ▼
```

## Key Points

1. **Single API Call**:
   - All orders fetched once on page load
   - Filtering and sorting done client-side
   - No additional API calls when changing filters

2. **Performance**:
   - Backend query optimized with indexes on `UserId` and `CreatedAt`
   - Includes related items in single query (no N+1 problem)
   - Client-side filtering is instant (no loading)

3. **User Experience**:
   - Real-time filtering and sorting
   - Shows count of filtered vs total orders
   - Clear visual hierarchy with cards
   - Responsive design for mobile

4. **Data Display**:
   - Orders sorted newest first by default
   - Dates formatted in readable format
   - Amounts displayed in INR (₹)
   - Product IDs truncated for readability

5. **Filter Combinations**:
   - All filters work together (AND logic)
   - Amount + Date range can be combined
   - Sorting applied after filtering

6. **State Management**:
   - `orders`: Original data from API
   - `filteredOrders`: Filtered and sorted data for display
   - Filter states: `minAmount`, `maxAmount`, `startDate`, `endDate`, `sortBy`

7. **Authentication**:
   - Protected route - requires login
   - JWT token sent in Authorization header
   - Only returns orders for authenticated user

8. **Guid Consistency**:
   - `userId` is Guid (from Auth Service)
   - Order Service stores and queries by Guid
   - Type-safe throughout the flow


