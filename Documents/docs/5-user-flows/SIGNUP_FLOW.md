# User Registration Flow - Request Journey

This document explains how requests flow through the system when a user clicks "Sign Up".

## Architecture Overview

```
Frontend (React) → API Gateway (Ocelot/YARP) → Auth Service → User Service
                                    ↓                ↓
                              (Routes requests)  (Direct HTTP call)
```

## Complete Registration Flow

### Step 1: User Fills Registration Form (Frontend)

- **Location**: `frontend/src/components/Register.js`
- User enters: Full Name, Email, Phone Number, Password, Confirm Password, Address (optional)
- Client-side validation occurs:
  - All mandatory fields checked
  - Email format validation
  - Phone format validation (10-15 digits)
  - Password strength validation (8+ chars, upper, lower, number, special)
  - Password match validation

### Step 2: Frontend Sends Registration Request

- **Request**: `POST /api/auth/register`
- **Destination**: API Gateway (http://localhost:5000)
- **Payload**:
  ```json
  {
    "Email": "user@example.com",
    "Password": "SecurePass123!",
    "ConfirmPassword": "SecurePass123!",
    "FullName": "John Doe",
    "PhoneNumber": "+1234567890",
    "Address": "123 Main St" // optional
  }
  ```

### Step 3: API Gateway Routes Request

- **Location**: `gateway/ocelot.json` or `gateway/ocelot.docker.json`
- Gateway receives: `POST /api/auth/register`
- Route matching: Path matches `/api/auth/{**catch-all}`
- Cluster: Routes to `authCluster`
- **Forwarded to**: Auth Service
  - Local dev: `http://localhost:5001/api/auth/register`
  - Docker: `http://auth-service:80/api/auth/register`

### Step 4: Auth Service Registration Processing

**Location**: `services/auth-service/Controllers/AuthController.cs`

#### 4a. Backend Validation

- Validates all mandatory fields (FullName, Email, PhoneNumber, Password, ConfirmPassword)
- Validates email format (regex: `^[^@\s]+@[^@\s]+\.[^@\s]+$`)
- Validates phone format (regex: `^\+?\d{10,15}$`)
- Validates password strength (regex: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$`)
- Validates password match

#### 4b. Duplicate Email Check

- Queries Auth Service database: `SELECT * FROM Users WHERE Email = @email`
- If email exists → Returns `409 Conflict` with error message

#### 4c. Duplicate Phone Number Check (Service-to-Service Call) - MANDATORY

- **Direct HTTP call** from Auth Service to User Service (bypassing gateway)
- **Request**: `GET /api/users/phone-exists/{phoneNumber}`
- **Destination**: User Service (http://localhost:5005 or http://user-service:80)
- **Purpose**: Check if phone number already exists in User Service database
- **Response**: `{ "exists": true/false }`
- If phone exists → Returns `409 Conflict` with error message
- **IMPORTANT**: If User Service unavailable or check fails → Returns `503 Service Unavailable` and registration is aborted (no user created)
- This ensures data integrity - no orphaned users are created

#### 4d. Password Hashing

- Hashes password using BCrypt: `BCrypt.HashPassword(password)`
- Secure hash stored, never plain text

#### 4e. Create User in Auth Service Database

- Creates new `User` record:
  ```csharp
  {
    Id: Guid (auto-generated),  // Type: Guid (not string)
    Email: "user@example.com",
    PasswordHash: "$2a$11$...",  // BCrypt hash
    FullName: "John Doe",
    CreatedAt: DateTime.UtcNow
  }
  ```
- Saves to Auth Service database (authdb)
- **Note**: All user IDs are stored as `Guid` type for consistency across all microservices

#### 4f. Create User Profile in User Service (Orchestrated by Auth Service)

- **Direct HTTP call** from Auth Service to User Service (bypassing gateway)
- **Request**: `POST /api/users`
- **Destination**: User Service (http://localhost:5005 or http://user-service:80)
- **Payload**:
  ```json
  {
    "UserId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",  // Guid from Auth Service
    "FirstName": "John",
    "LastName": "Doe",
    "PhoneNumber": "+1234567890",
    "Address": "123 Main St"
  }
  ```
- **Important**: UserId is sent as a Guid (not string). The Auth Service and User Service both use Guid for type safety and consistency.
- User Service validates and creates UserProfile record
- **Rollback Mechanism**: If profile creation fails:
  - Auth Service automatically deletes the user from authdb
  - Returns appropriate error (409 Conflict for duplicate phone, or 500 for other errors)
  - Ensures atomicity - either both user and profile are created, or neither is created

#### 4g. Return Response

- Only returns `201 Created` if both user and profile creation succeed
- Returns user info:
  ```json
  {
    "id": "guid",
    "email": "user@example.com",
    "fullName": "John Doe"
  }
  ```

### Step 6: Frontend Auto-Login (After Successful Registration)

**Location**: `frontend/src/components/Register.js`

#### 6a. Login Request

- **Request**: `POST /api/auth/login`
- **Flow**: Frontend → Gateway → Auth Service
- **Payload**:
  ```json
  {
    "Email": "user@example.com",
    "Password": "SecurePass123!"
  }
  ```

#### 6b. Auth Service Login Processing

- Validates credentials
- Returns JWT token and userId:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userId": "guid",
    "email": "user@example.com",
    "expiresIn": 21600
  }
  ```

### Step 7: Registration Complete

### Step 5: Registration Complete (Atomic Operation)

**Note**: Profile creation is now handled atomically as part of Step 4. The frontend does not make a separate profile creation call. This ensures data integrity - if profile creation fails, the auth user is automatically rolled back.

- Frontend receives success
- User is logged in (JWT token stored in localStorage)
- User redirected to products page
- Form cleared

## Request Flow Diagram

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ 1. POST /api/auth/register
       │    { email, password, phoneNumber, ... }
       ▼
┌─────────────────────┐
│   API Gateway       │
│   (Ocelot/YARP)     │
│   Port: 5000        │
└──────┬──────────────┘
       │ 2. Route /api/auth/* → authCluster
       │    Forward to Auth Service
       ▼
┌─────────────────────┐
│   Auth Service      │
│   Port: 5001        │
│   Database: authdb  │
└──────┬──────────────┘
       │ 3a. Validate fields, email, password, phone format
       │ 3b. Check duplicate email (local DB query)
       │ 3c. Check duplicate phone (MANDATORY - HTTP call to User Service)
       │     ┌───────────────────────────────┐
       │     │ Direct HTTP (bypass gateway)  │
       │     │ GET /api/users/phone-exists/  │
       │     ▼                               │
       │  ┌─────────────────────┐           │
       │  │  User Service       │           │
       │  │  Port: 5005         │           │
       │  │  Database: userdb   │           │
       │  └─────────────────────┘           │
       │     │                               │
       │     └─ Response: { exists: false }  │
       │     If unavailable → 503 error, abort│
       │                                     │
       │ 3d. Hash password (BCrypt)          │
       │ 3e. Create user in authdb           │
       │ 3f. Create profile (HTTP call to User Service)
       │     ┌───────────────────────────────┐
       │     │ Direct HTTP (bypass gateway)  │
       │     │ POST /api/users               │
       │     ▼                               │
       │  ┌─────────────────────┐           │
       │  │  User Service       │           │
       │  │  - Validate phone   │           │
       │  │  - Create profile   │           │
       │  │  - Save to userdb   │           │
       │  └─────────────────────┘           │
       │     │                               │
       │     └─ If fails → Rollback user     │
       │        Delete from authdb           │
       │                                     │
       │ 3g. Return 201 Created (only if both succeed)
       │                                     │
       └─────────────────────────────────────┘
       │ 4. Response: { id, email, fullName }
       ▼
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 5. Auto-login: POST /api/auth/login
       │    Flow: Frontend → Gateway → Auth Service
       │    Response: { token, userId, email }
       │
       │ 6. Registration complete, user logged in
       │    (Profile already created in Step 4)
       ▼
```

## Key Points

1. **Gateway Role**: Routes requests based on path patterns (`/api/auth/*` → Auth Service, `/api/users/*` → User Service)

2. **Service-to-Service Communication**:

   - Auth Service calls User Service directly (bypassing gateway) using HttpClient
   - This is for internal checks and avoids unnecessary gateway hops

3. **Data Separation**:

   - **Auth Service**: Stores authentication data (email, password hash, full name)
   - **User Service**: Stores profile data (name, phone, address, wallet balance)
   - Linked via `UserId` (from Auth Service)

4. **Validation Layers**:

   - **Frontend**: Client-side validation for UX
   - **Backend**: Server-side validation for security (cannot be bypassed)
   - **Both services**: Validate phone number (Auth Service checks before creating user, User Service validates on profile creation)

5. **Atomic Registration**:

   - Auth Service orchestrates both user and profile creation in a single registration call
   - If profile creation fails, Auth Service automatically rolls back user creation
   - Ensures data integrity - no orphaned users are created
   - Frontend makes only one registration call (no separate profile creation)

6. **Error Handling**:

   - Phone number check is **MANDATORY** - if User Service is unavailable, registration fails with 503
   - If profile creation fails after user creation, user is automatically deleted (rollback)
   - Registration is atomic - either both succeed or both fail

7. **Security**:
   - Passwords are never stored in plain text (BCrypt hashing)
   - All validations happen on backend
   - JWT tokens for authentication after registration
   - Atomic operations prevent partial registrations and data inconsistency
