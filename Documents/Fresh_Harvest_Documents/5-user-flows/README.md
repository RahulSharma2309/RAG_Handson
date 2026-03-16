# FreshHarvest Market - User Flow Documentation

This directory contains comprehensive documentation for all user journeys in the FreshHarvest Market organic food marketplace application.

## New here?

- Role-based guided tour: [`../START_HERE.md`](../START_HERE.md)
- Terms in plain language: [`../GLOSSARY.md`](../GLOSSARY.md)

## 📚 Available Documentation

### 1. [SIGNUP_FLOW.md](./SIGNUP_FLOW.md)
**User Registration Journey**

Documents the complete flow when a user creates a new account:
- Frontend form validation
- API Gateway routing
- Auth Service user creation
- User Service profile creation (atomic operation)
- Automatic login after registration
- Rollback mechanism for failed registrations

**Key Technologies**: React, BCrypt, JWT, Guid

---

### 2. [LOGIN_FLOW.md](./LOGIN_FLOW.md)
**User Authentication Journey**

Documents how users log in to the application:
- Email and password validation
- JWT token generation
- Token storage in localStorage
- Token validation on app load
- Session persistence
- Protected route access

**Key Technologies**: JWT, BCrypt, React Router, localStorage

---

### 3. [ADD_TO_CART_FLOW.md](./ADD_TO_CART_FLOW.md)
**Shopping Cart Management**

Documents how the shopping cart works (frontend-only):
- Adding products to cart
- Updating quantities
- Removing items
- Cart state management
- Total calculation
- No backend persistence (currently)

**Key Technologies**: React State, Props

---

### 4. [CHECKOUT_ORDER_FLOW.md](./CHECKOUT_ORDER_FLOW.md)
**Order Creation & Payment Journey**

Documents the multi-service order processing flow:
- Order validation
- **Payment Service integration** (NEW)
  - Wallet debit via User Service
  - Payment transaction recording
- Product stock validation and reservation
- Order creation
- Rollback mechanisms for failures
- Atomic transactions

**Key Technologies**: Payment Service, User Service, Product Service, Order Service, Guid

---

### 5. [ORDER_HISTORY_FLOW.md](./ORDER_HISTORY_FLOW.md)
**View Past Orders Journey**

Documents how users view their order history:
- Fetching user's orders
- Displaying order details
- **Filtering** by amount range and date range
- **Sorting** by date or amount
- Client-side filter/sort (no extra API calls)
- Real-time updates

**Key Technologies**: React State, Array filtering/sorting

---

### 6. [ADD_BALANCE_FLOW.md](./ADD_BALANCE_FLOW.md)
**Wallet Top-up Journey**

Documents how users add money to their wallet:
- Wallet balance display
- Amount input and validation
- Wallet credit operation
- Real-time balance updates across UI
- State synchronization (local + global)

**Key Technologies**: User Service, React State management

---

### 7. [PROFILE_EDIT_FLOW.md](./PROFILE_EDIT_FLOW.md)
**Profile View & Edit Journey**

Documents how users view and update their profile details:
- Fetch profile by Auth `userId`
- Edit form behavior (frontend state)
- Partial updates via `PATCH` (market-standard)
- Phone uniqueness conflicts and error codes

**Key Technologies**: User Service, PATCH semantics, React State management

---

## 🏗️ Architecture Overview

```
┌──────────────┐
│   Frontend   │  React SPA (Port 3000)
│  (React.js)  │  - Components, Routing, State Management
└──────┬───────┘  - localStorage for auth persistence
       │
       │ HTTP Requests (REST API)
       ▼
┌──────────────────┐
│   API Gateway    │  Ocelot/YARP (Port 5000)
│  (Ocelot/YARP)   │  - Route matching & forwarding
└──────┬───────────┘  - /api/auth/* → Auth Service
       │              - /api/users/* → User Service
       │              - /api/products/* → Product Service
       │              - /api/orders/* → Order Service
       │              - /api/payments/* → Payment Service
       │
       ├─────────────────────┬─────────────────┬──────────────────┬─────────────────┐
       ▼                     ▼                 ▼                  ▼                 ▼
┌────────────┐      ┌────────────┐    ┌────────────┐    ┌────────────┐   ┌────────────┐
│   Auth     │      │   User     │    │  Product   │    │   Order    │   │  Payment   │
│  Service   │◄─────┤  Service   │◄───┤  Service   │    │  Service   │   │  Service   │
│ (Port 5001)│      │ (Port 5005)│    │ (Port 5002)│    │ (Port 5004)│   │ (Port 5003)│
└────┬───────┘      └────┬───────┘    └────┬───────┘    └────┬───────┘   └────┬───────┘
     │                   │                   │                   │                │
     ▼                   ▼                   ▼                   ▼                ▼
┌──────────┐       ┌──────────┐        ┌──────────┐       ┌──────────┐    ┌──────────┐
│  authdb  │       │  userdb  │        │ productdb│       │ orderdb  │    │ paymentdb│
│ (MSSQL)  │       │ (MSSQL)  │        │ (MSSQL)  │       │ (MSSQL)  │    │ (MSSQL)  │
└──────────┘       └──────────┘        └──────────┘       └──────────┘    └──────────┘
```

## 🔄 Service-to-Service Communication

Some services communicate directly (bypassing the gateway):

1. **Auth Service → User Service**
   - Phone number existence check
   - User profile creation during registration

2. **Order Service → User Service**
   - Get user profile by userId
   - (Via Payment Service for wallet operations)

3. **Order Service → Product Service**
   - Validate products
   - Reserve stock

4. **Order Service → Payment Service** (NEW)
   - Process payment (wallet debit + record transaction)
   - Refund payment (on order failure)

5. **Payment Service → User Service** (NEW)
   - Debit wallet
   - Credit wallet (for refunds)

## 🔑 Key Concepts

### Guid Consistency
- All user IDs, product IDs, order IDs are **Guid** type
- Ensures type safety across all microservices
- Frontend stores as strings (JavaScript compatibility)
- Backend uses Guid for all ID fields

### Atomic Operations
- **User Registration**: Auth user + User profile created atomically
- **Order Creation**: Payment + Stock reservation + Order creation
- **Rollback mechanisms** ensure no partial operations

### Payment Service Integration
- **Central payment handling**: All wallet operations go through Payment Service
- **Transaction recording**: Every payment logged in paymentdb
- **Audit trail**: Complete history of all transactions
- **Refund support**: Automatic wallet refunds on order failures

### Authentication Flow
- **JWT tokens** for stateless authentication
- **6-hour expiration** on tokens
- **Token validation** on every app load
- **localStorage** for persistence

### Error Handling
- **User not found (404)**: Redirects to registration
- **Insufficient balance (409)**: Shows error, suggests adding funds
- **Service unavailable (503)**: Shows retry message
- **Validation errors (400)**: Shows specific field errors

## 📊 Data Flow Patterns

### 1. Request Flow (Frontend → Backend)
```
User Action → React Component → API Call → Gateway → Microservice → Database
```

### 2. Response Flow (Backend → Frontend)
```
Database → Microservice → Gateway → React Component → UI Update
```

### 3. State Management (Frontend)
```
API Response → React State → Component Props → DOM Rendering
```

## 🛠️ Technology Stack

### Frontend
- **React 18**: UI framework
- **React Router v6**: Client-side routing
- **Axios**: HTTP client
- **localStorage**: Session persistence
- **CSS3**: Styling (modularized)

### Backend
- **.NET 8**: Microservices framework
- **Entity Framework Core**: ORM
- **BCrypt.NET**: Password hashing
- **JWT**: Authentication tokens
- **Ocelot/YARP**: API Gateway

### Database
- **SQL Server 2019**: All databases
- **Separate databases per service**: authdb, userdb, productdb, orderdb, paymentdb

### DevOps
- **Docker & Docker Compose**: Containerization
- **Nginx**: Frontend web server

## 📝 Documentation Conventions

Each flow document follows this structure:

1. **Architecture Overview**: High-level diagram
2. **Step-by-step Flow**: Detailed walkthrough
3. **Request/Response Examples**: JSON payloads
4. **Request Flow Diagram**: Visual representation
5. **Key Points**: Important concepts and gotchas

## 🚀 Getting Started

To understand the application flow:

1. **Start with**: [SIGNUP_FLOW.md](./SIGNUP_FLOW.md)
2. **Then read**: [LOGIN_FLOW.md](./LOGIN_FLOW.md)
3. **For shopping**: [ADD_TO_CART_FLOW.md](./ADD_TO_CART_FLOW.md) → [CHECKOUT_ORDER_FLOW.md](./CHECKOUT_ORDER_FLOW.md)
4. **For history**: [ORDER_HISTORY_FLOW.md](./ORDER_HISTORY_FLOW.md)
5. **For wallet**: [ADD_BALANCE_FLOW.md](./ADD_BALANCE_FLOW.md)

## 🔗 Related Documentation

- **Architecture Diagrams**: `docs/diagram/`
- **API Documentation**: Swagger UI available at:
  - Auth: http://localhost:5001/swagger
  - User: http://localhost:5005/swagger
  - Product: http://localhost:5002/swagger
  - Order: http://localhost:5004/swagger
  - Payment: http://localhost:5003/swagger

## 📅 Last Updated

December 24, 2025

## 🤝 Contributing

When adding new features:
1. Update relevant flow documentation
2. Add new flow document if it's a major feature
3. Update this README with links
4. Include request/response examples
5. Add diagrams for complex flows


