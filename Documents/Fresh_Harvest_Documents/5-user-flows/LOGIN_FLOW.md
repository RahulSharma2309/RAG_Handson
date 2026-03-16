# User Login Flow - Request Journey

This document explains how requests flow through the system when a user logs in.

## Architecture Overview

```
Frontend (React) → API Gateway (Ocelot/YARP) → Auth Service
```

## Complete Login Flow

### Step 1: User Fills Login Form (Frontend)

- **Location**: `frontend/src/components/Login.js`
- User enters: Email, Password
- Client-side validation:
  - Email and password are required
  - No format validation at this stage (server validates)

### Step 2: Frontend Sends Login Request

- **Request**: `POST /api/auth/login`
- **Destination**: API Gateway (http://localhost:5000)
- **Payload**:
  ```json
  {
    "Email": "user@example.com",
    "Password": "SecurePass123!"
  }
  ```

### Step 3: API Gateway Routes Request

- **Location**: `gateway/ocelot.json` or `gateway/ocelot.docker.json`
- Gateway receives: `POST /api/auth/login`
- Route matching: Path matches `/api/auth/{**catch-all}`
- Cluster: Routes to `authCluster`
- **Forwarded to**: Auth Service
  - Local dev: `http://localhost:5001/api/auth/login`
  - Docker: `http://auth-service:80/api/auth/login`

### Step 4: Auth Service Login Processing

**Location**: `services/auth-service/Controllers/AuthController.cs`

#### 4a. Validate Input

- Checks that email and password are provided
- Returns `400 Bad Request` if missing

#### 4b. Find User by Email

- Queries Auth Service database: `SELECT * FROM Users WHERE Email = @email`
- If user not found → Returns `404 Not Found` with code `USER_NOT_FOUND`
  - Frontend redirects to registration page with message
  - Pre-fills email in registration form

#### 4c. Verify Password

- Uses BCrypt to verify password: `BCrypt.Verify(password, user.PasswordHash)`
- Compares provided password with stored hash
- If password invalid → Returns `401 Unauthorized` with error "Invalid credentials"

#### 4d. Generate JWT Token

- **Location**: `services/auth-service/Program.cs` - `JwtService`
- Creates JWT token with claims:
  ```csharp
  {
    NameIdentifier: user.Id.ToString(),  // Guid converted to string for JWT
    Email: user.Email,
    fullName: user.FullName
  }
  ```
- Token settings:
  - Expiration: 6 hours
  - Algorithm: HMAC SHA256
  - Signing Key: From configuration

#### 4e. Return Response

- **Response**: `200 OK`
- **Body**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 21600,
    "userId": "a93ac0d5-a5aa-4f57-a666-e3da19f5e389",  // Guid
    "email": "user@example.com"
  }
  ```

### Step 5: Frontend Processes Response

**Location**: `frontend/src/components/Login.js` and `frontend/src/App.js`

#### 5a. Store Authentication Data

- Stores in `localStorage`:
  - `token`: JWT token
  - `userId`: User ID (Guid as string)
- **Location**: Browser localStorage

#### 5b. Set Application State

- Updates React state via `handleLogin` function:
  - `token`: Set from response
  - `userId`: Set from response
  - `isAuthenticated`: Set to true

#### 5c. Fetch Initial Data

- **Fetch Products**: `GET /api/products`
- **Fetch User Profile**: `GET /api/users/by-userid/{userId}`
  - Gets wallet balance and profile details

#### 5d. Redirect User

- Redirects to `/products` page (home for authenticated users)

### Step 6: Token Validation on Page Load

**Location**: `frontend/src/hooks/useAuth.js`

When user refreshes or returns to the site:

#### 6a. Read from localStorage

- Reads `token` and `userId` from localStorage

#### 6b. Validate Token

- **Request**: `GET /api/auth/me`
- **Headers**: `Authorization: Bearer {token}`
- **Flow**: Frontend → Gateway → Auth Service

#### 6c. Auth Service Validates Token

- Extracts user ID from JWT claims
- Queries database to ensure user exists
- Returns user info if valid

#### 6d. Handle Invalid Token

- If token invalid or user not found:
  - Clears localStorage
  - Redirects to login page
- If token valid:
  - User remains logged in

## Request Flow Diagram

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ 1. POST /api/auth/login
       │    { email, password }
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
       │ 3a. Validate input (email, password)
       │ 3b. Find user by email
       │     SELECT * FROM Users WHERE Email = @email
       │ 3c. Verify password (BCrypt)
       │ 3d. Generate JWT token
       │     Claims: { userId (Guid), email, fullName }
       │     Expiration: 6 hours
       │ 3e. Return response
       ▼
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 4. Store in localStorage
       │    - token
       │    - userId (Guid as string)
       │
       │ 5. Set app state (isAuthenticated = true)
       │
       │ 6. Fetch initial data
       │    - Products: GET /api/products
       │    - Profile: GET /api/users/by-userid/{userId}
       │
       │ 7. Redirect to /products
       ▼
```

## Key Points

1. **Authentication**:
   - Stateless authentication using JWT tokens
   - Token stored in browser localStorage
   - Token expires after 6 hours

2. **Password Security**:
   - Passwords never stored in plain text
   - BCrypt hashing with salt
   - Password verification on each login

3. **User ID Consistency**:
   - Auth Service stores and returns user ID as `Guid`
   - Frontend stores as string in localStorage (JavaScript compatibility)
   - All backend services use `Guid` for type safety

4. **Token Validation**:
   - On app load, token is validated via `/api/auth/me` endpoint
   - Invalid tokens are cleared and user is logged out
   - Prevents using expired or tampered tokens

5. **Error Handling**:
   - User not found (404): Frontend redirects to registration with pre-filled email
   - Invalid password (401): Shows error message
   - Generic errors (500): Shows user-friendly error

6. **Session Persistence**:
   - Token and userId stored in localStorage
   - User remains logged in across browser sessions
   - Manual logout required to clear session

7. **React Router Integration**:
   - Protected routes check authentication status
   - Unauthenticated users redirected to login
   - Authenticated users can access protected routes


