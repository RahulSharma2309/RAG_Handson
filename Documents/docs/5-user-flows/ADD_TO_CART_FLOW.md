# Add to Cart Flow - Request Journey

This document explains how the shopping cart works in the frontend (no backend persistence).

## Architecture Overview

```
Frontend (React) → Browser localStorage + React State
```

**Note**: Cart is stored entirely in the frontend - no backend API calls for cart operations.

## Complete Add to Cart Flow

### Step 1: User Views Products (Frontend)

- **Location**: User navigates to `/products`
- **Component**: `frontend/src/components/ProductSearchPage.js` and `ProductList.js`
- **Initial Load**: Products fetched from Product Service:
  - `GET /api/products`
  - Returns list of all products with stock

### Step 2: User Clicks "Add to Cart"

- **Location**: `frontend/src/components/ProductList.js`
- User clicks "Add to Cart" button on a product
- Button shows:
  - Product name
  - Price (₹1999)
  - Stock availability
  - "Add to Cart" button (disabled if out of stock)

### Step 3: Add to Cart Function Called

**Location**: `frontend/src/App.js`

#### 3a. Cart State Structure

```javascript
// Cart items stored in React state
const [cart, setCart] = useState([]);

// Each cart item has:
{
  productId: "bb89025b-260f-4b91-87e9-47b5fee317b3",  // Guid as string
  name: "Coffee Mug",
  price: 999,
  quantity: 1
}
```

#### 3b. Add to Cart Logic

```javascript
const addToCart = (product) => {
  // Check if product already in cart
  const existingIndex = cart.findIndex(item => item.productId === product.id);
  
  if (existingIndex >= 0) {
    // Product exists - increment quantity
    const updated = [...cart];
    updated[existingIndex].quantity += 1;
    setCart(updated);
  } else {
    // New product - add to cart
    setCart([
      ...cart,
      {
        productId: product.id,
        name: product.name,
        price: product.price,
        quantity: 1,
      }
    ]);
  }
  
  // Optional: Show success message
  // "Added to cart: Coffee Mug"
};
```

### Step 4: Cart State Updates

**Location**: `frontend/src/App.js`

When cart state changes:

#### 4a. React Re-renders

- Header updates item count: "Cart (3)"
- Cart badge shows total items
- No API call - pure React state update

#### 4b. localStorage Sync (Optional)

**Not currently implemented**, but could be:
```javascript
useEffect(() => {
  localStorage.setItem('cart', JSON.stringify(cart));
}, [cart]);
```

This would persist cart across browser sessions.

### Step 5: View Cart

- **Location**: User clicks "Cart" button in header
- **Route**: `/cart`
- **Component**: `frontend/src/components/CartPage.js` and `Cart.js`

#### 5a. Display Cart Items

For each item in cart:
- Product name
- Quantity × Price (₹999)
- Subtotal (₹1998)
- "Remove" button

#### 5b. Calculate Total

```javascript
const total = cart.reduce((sum, item) => {
  return sum + (item.price * item.quantity);
}, 0);
```

Displayed as: **Total: ₹5997.00**

### Step 6: Remove from Cart

**Location**: `frontend/src/App.js`

```javascript
const removeFromCart = (productId) => {
  setCart(cart.filter(item => item.productId !== productId));
};
```

- Removes entire item from cart
- No decrease quantity option (remove completely)

### Step 7: Clear Cart

**Location**: `frontend/src/App.js`

```javascript
const clearCart = () => {
  setCart([]);
};
```

Called automatically after successful checkout.

## Cart State Flow Diagram

```
┌─────────────────────┐
│   Products Page     │
│   Display products  │
└──────┬──────────────┘
       │ User clicks "Add to Cart"
       │ on Coffee Mug (₹999)
       ▼
┌─────────────────────────────────────┐
│   App.js - addToCart()              │
│                                     │
│   Current cart: [                   │
│     { productId: "tea", qty: 1 }    │
│   ]                                 │
│                                     │
│   Check if Coffee Mug exists        │
│   ├─ Yes → Increment quantity       │
│   └─ No  → Add new item             │
│                                     │
│   Updated cart: [                   │
│     { productId: "tea", qty: 1 },   │
│     { productId: "coffee", qty: 1 } │
│   ]                                 │
└──────┬──────────────────────────────┘
       │ setCart(updated)
       │ React state update
       ▼
┌─────────────────────────────────────┐
│   React Re-render                   │
│                                     │
│   ├─ Header updates                 │
│   │   "Cart (2)" badge              │
│   │                                 │
│   ├─ Cart page updates (if open)    │
│   │   Shows 2 items, total ₹1998    │
│   │                                 │
│   └─ Product page remains           │
│       Button still shows "Add"      │
└─────────────────────────────────────┘

User navigates to /cart ───────────────┐
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │   Cart Page              │
                        │                          │
                        │   Items:                 │
                        │   • Tea Mug × 1 = ₹999   │
                        │   • Coffee Mug × 1 = ₹999│
                        │                          │
                        │   Total: ₹1998.00        │
                        │                          │
                        │   [Checkout] [Clear]     │
                        └──────────────────────────┘
                                       │
User clicks "Remove" on Tea Mug ───────┤
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │   App.js                 │
                        │   removeFromCart("tea")  │
                        │                          │
                        │   Updated cart: [        │
                        │     { productId:         │
                        │       "coffee", qty: 1 } │
                        │   ]                      │
                        └──────────────────────────┘
                                       │
                                       ▼
                        Cart updates to show 1 item
```

## Key Points

1. **No Backend Persistence**:
   - Cart stored only in React state
   - Lost on page refresh (unless localStorage added)
   - No API calls for add/remove operations
   - Fast and responsive

2. **State Management**:
   - Cart state lives in `App.js` (top-level component)
   - Passed down to child components as props
   - Functions to modify cart also passed as props

3. **Item Quantity**:
   - Adding same product increases quantity
   - No separate "increase/decrease quantity" UI
   - Remove button removes entire item

4. **Cart Operations**:
   - **Add**: `addToCart(product)` - Adds or increments
   - **Remove**: `removeFromCart(productId)` - Removes completely
   - **Clear**: `clearCart()` - Empties entire cart

5. **Data Flow**:
   ```
   App.js (state)
     ├─ cart: []
     ├─ addToCart()
     ├─ removeFromCart()
     └─ clearCart()
   
   Passed to:
     ├─ Header (display count)
     ├─ ProductList (add function)
     ├─ CartPage (display items)
     └─ Checkout (use for order)
   ```

6. **Cart Item Structure**:
   ```javascript
   {
     productId: Guid,  // Links to product
     name: string,     // For display
     price: number,    // In rupees
     quantity: number  // How many
   }
   ```

7. **Calculate Total**:
   ```javascript
   const total = cart.reduce((sum, item) => 
     sum + (item.price * item.quantity), 0
   );
   ```

8. **Performance**:
   - All operations are O(n) or better
   - No network latency
   - Instant UI updates

9. **Checkout Integration**:
   - When user clicks "Checkout":
     - Cart data sent to Order Service
     - Order created with items from cart
     - Cart cleared on success

10. **Limitations**:
    - No persistence across sessions
    - No stock validation (done at checkout)
    - No price updates (static from add time)
    - Not synced across devices/tabs

## Future Enhancements

To add cart persistence:

1. **localStorage**:
   ```javascript
   // On load
   const [cart, setCart] = useState(() => {
     const saved = localStorage.getItem('cart');
     return saved ? JSON.parse(saved) : [];
   });
   
   // On change
   useEffect(() => {
     localStorage.setItem('cart', JSON.stringify(cart));
   }, [cart]);
   ```

2. **Backend Cart Service**:
   - Create Cart Service to persist carts
   - API endpoints:
     - `POST /api/cart/add`
     - `DELETE /api/cart/remove`
     - `GET /api/cart/{userId}`
   - Benefits:
     - Sync across devices
     - Persist after logout
     - Analytics on abandoned carts

3. **Quantity Controls**:
   - Add +/- buttons in cart
   - Set max based on available stock
   - Update subtotals in real-time

4. **Stock Validation**:
   - Check stock before adding
   - Disable add if out of stock
   - Show "Only X left" messages

