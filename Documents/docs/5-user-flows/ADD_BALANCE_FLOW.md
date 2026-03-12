# Add Balance to Wallet Flow - Request Journey

This document explains how requests flow through the system when a user adds money to their wallet.

## Architecture Overview

```
Frontend (React) → API Gateway → User Service
```

## Complete Add Balance Flow

### Step 1: User Navigates to Profile (Frontend)

- **Location**: User clicks "Profile" button in header
- **Route**: `/profile`
- **Component**: `frontend/src/components/Profile.js`
- **Protected Route**: Requires authentication

### Step 2: User Initiates Add Balance

- **Location**: `frontend/src/components/Profile.js`
- User sees current wallet balance
- Clicks "Add Balance" button
- UI expands to show:
  - Amount input field
  - "Add" button
  - "Cancel" button

### Step 3: User Enters Amount

- User enters desired amount (in INR)
- Frontend validation:
  - Amount must be greater than 0
  - Amount must be a valid number

### Step 4: Frontend Sends Add Balance Request

- **Request**: `POST /api/users/{userId}/add-balance`
- **Destination**: API Gateway (http://localhost:5000)
- **Headers**: `Authorization: Bearer {token}`
- **Payload**:
  ```json
  {
    "Amount": 10000.00
  }
  ```

### Step 5: API Gateway Routes Request

- Gateway receives: `POST /api/users/{userId}/add-balance`
- Route matching: Path matches `/api/users/{**catch-all}`
- Cluster: Routes to `userCluster`
- **Forwarded to**: User Service
  - Local dev: `http://localhost:5005/api/users/{userId}/add-balance`
  - Docker: `http://user-service:80/api/users/{userId}/add-balance`

### Step 6: User Service Processing

**Location**: `services/user-service/Controllers/UsersController.cs`

#### 6a. Validate Input

- Reads `userId` from the route (Guid)
- Checks that `Amount` > 0
- Returns `400 Bad Request` if invalid

#### 6b. Get User Profile

- Queries User Service database:
  ```sql
  SELECT * FROM UserProfiles WHERE UserId = @userId
  ```
- If user not found → Returns `404 Not Found`

#### 6c. Credit Wallet

**Location**: `services/user-service/Services/UserServiceImpl.cs`

- Calls `CreditWalletAsync(profileId, amount)`
- Updates wallet balance:
  ```csharp
  var user = await _db.Users.FirstOrDefaultAsync(u => u.Id == profileId);
  user.WalletBalance += amount;  // Add to current balance
  user.UpdatedAt = DateTime.UtcNow;
  await _db.SaveChangesAsync();
  return user.WalletBalance;  // Return new balance
  ```

#### 6d. Return Response

- **Response**: `200 OK`
- **Body**:
  ```json
  {
    "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",
    "balance": 610000.00,  // New balance
    "message": "Successfully added ₹10000 to wallet. New balance: ₹610000"
  }
  ```

### Step 7: Frontend Processes Response

**Location**: `frontend/src/components/Profile.js`

#### 7a. Update Local State

- Updates `profile` state with new balance
- Shows success message

#### 7b. Refresh Wallet Display

- Calls `onBalanceUpdate()` callback
- Updates wallet balance in header (via App.js)
- New balance shows immediately

#### 7c. Reset UI

- Clears amount input field
- Collapses add balance section
- Returns to normal profile view

### Step 8: Wallet Balance Propagation

**Location**: `frontend/src/App.js`

When `onBalanceUpdate` is called:

1. **Fetch Updated Wallet**:
   - `GET /api/users/by-userid/{userId}`
   - Gets latest user profile with updated balance

2. **Update Global State**:
   - Updates `wallet` state in App.js
   - Header automatically re-renders with new balance

3. **Visible Changes**:
   - Header shows: "Wallet: ₹610000.00"
   - Profile page shows updated balance
   - Checkout page shows updated balance

## Request Flow Diagram

```
┌─────────────┐
│   Frontend  │
│  /profile   │
└──────┬──────┘
       │ 1. User clicks "Add Balance"
       │    Input: amount (₹10000)
       │
       │ 2. POST /api/users/add-balance
       │    { UserId (Guid), Amount }
       │    Headers: { Authorization: Bearer token }
       ▼
┌─────────────────────┐
│   API Gateway       │
│   Port: 5000        │
└──────┬──────────────┘
       │ 3. Route to User Service
       ▼
┌─────────────────────┐
│   User Service      │
│   Port: 5005        │
│   Database: userdb  │
└──────┬──────────────┘
       │ 4a. Validate input (userId, amount > 0)
       │
       │ 4b. Get user profile
       │     SELECT * FROM UserProfiles
       │     WHERE UserId = @userId
       │
       │ 4c. Credit wallet
       │     UPDATE UserProfiles
       │     SET WalletBalance = WalletBalance + @amount,
       │         UpdatedAt = GETUTCDATE()
       │     WHERE Id = @profileId
       │
       │ 4d. Return response
       │     { userId, balance, message }
       ▼
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 5. Update profile state
       │    - Show success message
       │    - Update local balance display
       │
       │ 6. Call onBalanceUpdate()
       │    ▼
       │  ┌──────────────────────────────┐
       │  │ App.js - fetchWallet()       │
       │  │ GET /api/users/by-userid/{id}│
       │  │ Update global wallet state   │
       │  └──────────────────────────────┘
       │
       │ 7. UI updates everywhere
       │    - Header: Wallet: ₹610000.00
       │    - Profile: Balance updated
       │    - Checkout: Balance available
       ▼
```

## Key Points

1. **Wallet Structure**:
   - Each user has one wallet (part of UserProfile)
   - Balance stored as `decimal(18,2)` in database
   - Supports fractional amounts (paise)

2. **Transaction Type**:
   - This is a "credit" operation (adds money)
   - Uses same `CreditWalletAsync` method as payment refunds
   - Atomic database update (no race conditions)

3. **Amount Handling**:
   - Frontend: User enters amount in rupees (₹10000)
   - Backend: Stored as decimal without conversion
   - Display: Formatted with ₹ symbol and 2 decimal places

4. **Real-time Updates**:
   - Balance updates immediately in database
   - Frontend reflects change instantly
   - No page refresh needed

5. **State Synchronization**:
   - Local state updated first (Profile component)
   - Global state updated via callback (App.js)
   - Header, Profile, and Checkout all show same balance

6. **Security**:
   - Requires authentication (JWT token)
   - UserId validated against user profile
   - Cannot add balance to other users' wallets

7. **Error Handling**:
   - Invalid amount: "Amount must be greater than 0"
   - User not found: "User profile not found"
   - Network error: "Failed to add balance. Please try again."

8. **User Experience**:
   - Simple, single-step process
   - Immediate feedback with success message
   - Balance updates without page reload
   - Can add balance multiple times

9. **No Payment Gateway**:
   - Currently a direct wallet credit
   - In production, would integrate:
     - Payment gateway (Razorpay, Stripe, etc.)
     - Bank verification
     - Transaction receipts

10. **Audit Trail**:
    - Updated timestamp recorded
    - In production, would also log:
      - Transaction ID
      - Payment method
      - Source of funds


