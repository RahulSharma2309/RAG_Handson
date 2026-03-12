# 🔐 Auth Service - Complete Documentation

**Authentication & User Management Microservice**

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Architecture & Design](#2-architecture--design)
3. [Database Schema](#3-database-schema)
4. [API Endpoints](#4-api-endpoints)
5. [Business Logic Deep Dive](#5-business-logic-deep-dive)
6. [Service-to-Service Communication](#6-service-to-service-communication)
7. [Security Implementation](#7-security-implementation)
8. [Configuration](#8-configuration)
9. [Code Walkthrough](#9-code-walkthrough)
10. [Error Handling](#10-error-handling)
11. [Best Practices](#11-best-practices)

---

## 1. Service Overview

### Purpose

The **Auth Service** is responsible for:

- User registration with atomic profile creation
- User authentication (login)
- JWT token generation and validation
- Password management (reset)
- Email uniqueness validation
- Orchestrating user profile creation with User Service

### Key Responsibilities

| Responsibility        | Description                                     |
| --------------------- | ----------------------------------------------- |
| **Registration**      | Create auth user + orchestrate profile creation |
| **Authentication**    | Verify credentials and issue JWT tokens         |
| **Validation**        | Email format, password strength, phone format   |
| **Atomic Operations** | Ensure user + profile created atomically        |
| **Rollback**          | Delete auth user if profile creation fails      |
| **Token Management**  | Generate and validate JWT tokens                |

### Technology Stack

- **.NET 8** - Framework
- **Entity Framework Core** - ORM
- **SQL Server** - Database (authdb)
- **BCrypt.NET** - Password hashing
- **JWT** - Authentication tokens
- **HttpClientFactory** - Service communication

### Port & Database

- **Port**: `5001`
- **Database**: `authdb`
- **Docker Service Name**: `auth-service`

---

## 2. Architecture & Design

### High-Level Architecture

```
┌──────────────────────────────────────────────┐
│            API Gateway (YARP)                │
│            Port: 5000                        │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│           Auth Service (Port 5001)           │
│                                              │
│  Controllers:                                │
│  • AuthController - /api/auth/*             │
│                                              │
│  Services:                                   │
│  • JwtService - Token generation            │
│                                              │
│  Data:                                       │
│  • AppDbContext - EF Core                   │
│  • User entity                               │
│                                              │
│  External Communication:                     │
│  • HttpClient → User Service                │
│    - Phone validation                        │
│    - Profile creation                        │
└───────────────────┬──────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌────────────────┐    ┌────────────────┐
│  SQL Server    │    │  User Service  │
│  authdb        │    │  Port: 5005    │
└────────────────┘    └────────────────┘
```

### Service Dependencies

**Depends On:**

- **User Service** (for phone validation and profile creation)

**Depended On By:**

- **Frontend** (for login/registration)
- **API Gateway** (routes requests to Auth Service)

### Design Patterns

1. **Repository Pattern** (EF Core DbContext)
2. **Service Pattern** (JwtService for token logic)
3. **DTO Pattern** (Data Transfer Objects for API contracts)
4. **Saga Pattern** (Orchestrated registration with rollback)
5. **Factory Pattern** (HttpClientFactory for service calls)

---

## 3. Database Schema

### Database: `authdb`

### Table: `Users`

| Column         | Type          | Constraints                  | Description            |
| -------------- | ------------- | ---------------------------- | ---------------------- |
| `Id`           | Guid          | PRIMARY KEY, DEFAULT NEWID() | Unique user identifier |
| `Email`        | nvarchar(256) | UNIQUE, NOT NULL             | User's email address   |
| `PasswordHash` | nvarchar(MAX) | NOT NULL                     | BCrypt hashed password |
| `FullName`     | nvarchar(256) | NULL                         | User's full name       |
| `CreatedAt`    | datetime2     | DEFAULT GETUTCDATE()         | Registration timestamp |

### Entity Model

```csharp
public class User
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Email { get; set; } = null!;
    public string PasswordHash { get; set; } = null!;
    public string? FullName { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
```

### Key Characteristics

- **Guid Primary Key**: Ensures unique, distributed ID generation
- **Email Uniqueness**: Enforced at database level
- **No Phone Number**: Phone stored only in User Service
- **Password Security**: Only hashed passwords stored, never plain text
- **UTC Timestamps**: All timestamps in UTC for consistency

---

## 4. API Endpoints

### Base Path: `/api/auth`

### 1. **POST /api/auth/register** - User Registration

**Description**: Register a new user with atomic profile creation

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "fullName": "John Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St, City, Country"
}
```

**Validation Rules**:

- ✅ Email: Required, valid format
- ✅ Password: Required, 8+ chars, uppercase, lowercase, number, special char
- ✅ ConfirmPassword: Must match password
- ✅ FullName: Required
- ✅ PhoneNumber: Required, 10-15 digits
- ✅ Address: Optional

**Success Response (201 Created)**:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "fullName": "John Doe"
}
```

**Error Responses**:

| Status | Error                           | Description                      |
| ------ | ------------------------------- | -------------------------------- |
| `400`  | Invalid email format            | Email doesn't match regex        |
| `400`  | Password validation failed      | Weak password                    |
| `400`  | Passwords do not match          | Mismatch between password fields |
| `409`  | Email already registered        | Duplicate email                  |
| `409`  | Phone number already registered | Duplicate phone                  |
| `503`  | User Service unavailable        | Cannot validate phone            |

---

### 2. **POST /api/auth/login** - User Login

**Description**: Authenticate user and issue JWT token

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK)**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 21600,
  "userId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com"
}
```

**Token Details**:

- **Algorithm**: HS256
- **Expiry**: 6 hours (21600 seconds)
- **Claims**: UserId, Email, FullName

**Error Responses**:

| Status | Error                       | Description             |
| ------ | --------------------------- | ----------------------- |
| `400`  | Email and password required | Missing credentials     |
| `401`  | Invalid credentials         | Wrong email or password |

---

### 3. **POST /api/auth/reset-password** - Password Reset

**Description**: Reset user password (simplified version)

**Request Body**:

```json
{
  "email": "user@example.com",
  "newPassword": "NewSecurePass123!"
}
```

**Success Response (200 OK)**:

```json
{
  "status": "password reset"
}
```

**Error Responses**:

| Status | Error                           | Description         |
| ------ | ------------------------------- | ------------------- |
| `400`  | Email and new password required | Missing fields      |
| `404`  | User not found                  | Email doesn't exist |

**⚠️ Note**: This is a simplified version. Production should include:

- Email verification
- OTP/token-based reset
- Old password verification

---

### 4. **GET /api/auth/me** - Get Current User

**Description**: Get authenticated user details

**Authorization**: Required (JWT Bearer token)

**Success Response (200 OK)**:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "fullName": "John Doe",
  "createdAt": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Error          | Description                     |
| ------ | -------------- | ------------------------------- |
| `401`  | Unauthorized   | Missing or invalid token        |
| `404`  | User not found | User deleted after token issued |

---

## 5. Business Logic Deep Dive

### Registration Flow (Atomic Operation)

The registration process is a **distributed transaction** ensuring atomicity:

```
1. Validate Input
   ├─ Email format
   ├─ Password strength
   ├─ Phone format
   └─ Password match

2. Check Email Uniqueness
   └─ Query authdb

3. Check Phone Uniqueness (MANDATORY)
   ├─ HTTP call to User Service
   ├─ If unavailable → 503 (abort)
   └─ If duplicate → 409 (abort)

4. Hash Password
   └─ BCrypt with salt

5. Create Auth User
   └─ INSERT into authdb

6. Create User Profile (CRITICAL)
   ├─ HTTP call to User Service
   ├─ Pass: UserId, FirstName, LastName, Phone, Address
   │
   ├─ If SUCCESS:
   │   └─ Return 201 Created
   │
   └─ If FAILURE:
       ├─ DELETE auth user (rollback)
       ├─ Log error
       └─ Return error response
```

### Code Implementation

```csharp
[HttpPost("register")]
public async Task<IActionResult> Register(RegisterDto dto)
{
    // 1. Validate input (email, password, phone)
    // ... validation logic ...

    // 2. Check email uniqueness
    var emailExists = await _db.Users.AnyAsync(u => u.Email == dto.Email);
    if (emailExists) return Conflict(new { error = "Email already registered" });

    // 3. Check phone uniqueness via User Service (MANDATORY)
    try
    {
        var httpClient = _httpClientFactory.CreateClient("user");
        var phoneCheckResponse = await httpClient.GetAsync(
            $"/api/users/phone-exists/{Uri.EscapeDataString(dto.PhoneNumber)}"
        );

        if (!phoneCheckResponse.IsSuccessStatusCode)
        {
            // User Service unavailable - ABORT registration
            return StatusCode(503, new { error = "Unable to validate phone number" });
        }

        var phoneCheckResult = await phoneCheckResponse.Content
            .ReadFromJsonAsync<PhoneExistsResponse>();

        if (phoneCheckResult?.Exists == true)
            return Conflict(new { error = "Phone number already registered" });
    }
    catch (Exception ex)
    {
        // Cannot reach User Service - ABORT registration
        _logger.LogError(ex, "Failed to check phone number");
        return StatusCode(503, new { error = "Unable to validate phone number" });
    }

    // 4. Hash password
    var passwordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password);

    // 5. Create auth user
    var user = new User
    {
        Email = dto.Email,
        PasswordHash = passwordHash,
        FullName = dto.FullName
    };
    _db.Users.Add(user);
    await _db.SaveChangesAsync();

    // 6. Create user profile (ATOMIC OPERATION)
    try
    {
        var names = dto.FullName.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        var profileDto = new
        {
            UserId = user.Id,  // Guid
            FirstName = names.Length > 0 ? names[0] : "",
            LastName = names.Length > 1 ? string.Join(" ", names.Skip(1)) : "",
            PhoneNumber = dto.PhoneNumber,
            Address = dto.Address
        };

        var profileResponse = await httpClient.PostAsJsonAsync("/api/users", profileDto);

        if (!profileResponse.IsSuccessStatusCode)
        {
            // ROLLBACK: Delete auth user
            _db.Users.Remove(user);
            await _db.SaveChangesAsync();

            _logger.LogError("Profile creation failed. Auth user rolled back.");
            return StatusCode(500, new { error = "Registration failed" });
        }
    }
    catch (Exception ex)
    {
        // ROLLBACK: Delete auth user
        _db.Users.Remove(user);
        await _db.SaveChangesAsync();

        _logger.LogError(ex, "Profile creation failed. Auth user rolled back.");
        return StatusCode(500, new { error = "Registration failed" });
    }

    return CreatedAtAction(nameof(Me), new { id = user.Id },
        new { user.Id, user.Email, user.FullName });
}
```

### Login Flow

```
1. Validate Input
   └─ Check email and password are provided

2. Find User by Email
   └─ Query authdb

3. Verify Password
   ├─ BCrypt.Verify(plainPassword, storedHash)
   └─ Compare timing-safe

4. Generate JWT Token
   ├─ Claims: UserId, Email, FullName
   ├─ Expiry: 6 hours
   └─ Sign with secret key

5. Return Token
   └─ Include: token, expiresIn, userId, email
```

---

## 6. Service-to-Service Communication

### Communication with User Service

**Purpose**: Phone validation and profile creation

**Configuration**:

```csharp
// Startup.cs
services.AddHttpClient("user", client =>
{
    var userServiceUrl = Configuration.GetValue<string>("ServiceUrls:UserService");
    client.BaseAddress = new Uri(userServiceUrl);
    client.Timeout = TimeSpan.FromSeconds(30);
});
```

**Environment Variables** (docker-compose.yml):

```yaml
auth-service:
  environment:
    - ServiceUrls__UserService=http://user-service:80
```

### API Calls to User Service

#### 1. Check Phone Exists

```csharp
GET /api/users/phone-exists/{phoneNumber}

Response:
{
  "exists": true
}
```

#### 2. Create User Profile

```csharp
POST /api/users

Body:
{
  "userId": "guid",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St"
}

Response: 201 Created
{
  "id": "profile-guid",
  "userId": "user-guid",
  ...
}
```

### Error Handling for Service Calls

| Scenario               | HTTP Status | Action             |
| ---------------------- | ----------- | ------------------ |
| User Service down      | 503         | Abort registration |
| Phone exists           | 409         | Return conflict    |
| Profile creation fails | 500         | Rollback auth user |
| Network timeout        | 503         | Abort registration |

---

## 7. Security Implementation

### Password Hashing

**Algorithm**: BCrypt with auto-generated salt

```csharp
// Hashing during registration
var passwordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password);

// Verification during login
var valid = BCrypt.Net.BCrypt.Verify(dto.Password, user.PasswordHash);
```

**Why BCrypt?**

- ✅ Adaptive hashing (configurable work factor)
- ✅ Built-in salt generation
- ✅ Resistant to rainbow tables
- ✅ Timing-attack safe comparison

### JWT Token Generation

**Configuration**:

```csharp
// appsettings.json
{
  "Jwt": {
    "Key": "your-256-bit-secret-key-min-32-chars",
    "Issuer": "AuthService",
    "Audience": "ECommerceApp"
  }
}
```

**Token Structure**:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "fullName": "John Doe",
    "iat": 1735041000,
    "exp": 1735062600,
    "iss": "AuthService",
    "aud": "ECommerceApp"
  },
  "signature": "..."
}
```

**Claims**:

| Claim                  | Type      | Description             |
| ---------------------- | --------- | ----------------------- |
| `sub` (NameIdentifier) | Guid      | User ID                 |
| `email` (Email)        | string    | User's email            |
| `fullName`             | string    | User's full name        |
| `iat`                  | timestamp | Issued at               |
| `exp`                  | timestamp | Expires at (6 hours)    |
| `iss`                  | string    | Issuer (AuthService)    |
| `aud`                  | string    | Audience (ECommerceApp) |

### Password Validation Rules

```regex
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$
```

**Requirements**:

- Minimum 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one digit
- At least one special character

### Email Validation

```regex
^[^@\s]+@[^@\s]+\.[^@\s]+$
```

### Phone Validation

```regex
^\+?\d{10,15}$
```

**Requirements**:

- 10-15 digits
- Optional `+` prefix for country code

---

## 8. Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost,1433;Database=authdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;"
  },
  "Jwt": {
    "Key": "your-super-secret-key-that-is-at-least-32-characters-long",
    "Issuer": "AuthService",
    "Audience": "ECommerceApp",
    "ExpiryHours": 6
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
auth-service:
  build:
    context: ../services/auth-service
    dockerfile: Dockerfile
  ports:
    - "5001:80"
  environment:
    - ASPNETCORE_ENVIRONMENT=Development
    - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=authdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;
    - Jwt__Key=your-super-secret-key-that-is-at-least-32-characters-long
    - Jwt__Issuer=AuthService
    - Jwt__Audience=ECommerceApp
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
auth-service/
├── Controllers/
│   └── AuthController.cs         # API endpoints
├── Models/ (in Program.cs)
│   └── User.cs                   # User entity
├── Services/
│   └── JwtService.cs             # Token generation
├── Data/
│   └── AppDbContext.cs           # EF Core context
├── Dtos/
│   ├── RegisterDto.cs            # Registration request
│   ├── LoginDto.cs               # Login request
│   └── AuthResponseDto.cs        # Token response
├── Startup.cs                    # Service configuration
├── Program.cs                    # Application entry
├── appsettings.json              # Configuration
└── auth-service.csproj           # Project file
```

### Startup.cs

```csharp
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Database
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(Configuration.GetConnectionString("DefaultConnection")));

        // JWT
        var jwtKey = Configuration["Jwt:Key"];
        var jwtIssuer = Configuration["Jwt:Issuer"];
        var jwtAudience = Configuration["Jwt:Audience"];

        services.AddSingleton<IJwtService>(
            new JwtService(jwtKey, jwtIssuer, jwtAudience));

        // JWT Authentication
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = jwtIssuer,
                    ValidAudience = jwtAudience,
                    IssuerSigningKey = new SymmetricSecurityKey(
                        Encoding.UTF8.GetBytes(jwtKey))
                };
            });

        // HttpClient for User Service
        services.AddHttpClient("user", client =>
        {
            var userServiceUrl = Configuration.GetValue<string>("ServiceUrls:UserService");
            client.BaseAddress = new Uri(userServiceUrl);
        });

        services.AddControllers();
        services.AddSwaggerGen();
    }
}
```

---

## 10. Error Handling

### Error Response Format

**Standard Error Response**:

```json
{
  "error": "Human-readable error message"
}
```

### Error Scenarios

| Scenario                | Status Code | Response                                         |
| ----------------------- | ----------- | ------------------------------------------------ |
| Missing email           | 400         | `{ "error": "Email is required" }`               |
| Invalid email format    | 400         | `{ "error": "Invalid email format" }`            |
| Weak password           | 400         | `{ "error": "Password must be 8+ chars..." }`    |
| Password mismatch       | 400         | `{ "error": "Passwords do not match" }`          |
| Email already exists    | 409         | `{ "error": "Email already registered" }`        |
| Phone already exists    | 409         | `{ "error": "Phone number already registered" }` |
| User Service down       | 503         | `{ "error": "Unable to validate phone number" }` |
| Profile creation failed | 500         | `{ "error": "Registration failed" }`             |
| Invalid credentials     | 401         | `{ "error": "Invalid credentials" }`             |
| Missing token           | 401         | `Unauthorized`                                   |

### Logging Strategy

```csharp
// Info level
_logger.LogInformation("User registered successfully: {Email}", dto.Email);

// Warning level
_logger.LogWarning("Login attempt failed for: {Email}", dto.Email);

// Error level
_logger.LogError(ex, "Registration failed for {Email}", dto.Email);
_logger.LogError("User Service returned {StatusCode} when checking phone",
    phoneCheckResponse.StatusCode);
```

---

## 11. Best Practices

### ✅ Security Best Practices

1. **Never Log Passwords**: Always log email only, never passwords
2. **Use BCrypt**: Adaptive hashing with built-in salt
3. **JWT Expiry**: Set reasonable expiry (6 hours)
4. **HTTPS Only**: In production, enforce HTTPS
5. **Rate Limiting**: Implement on login endpoint (future)

### ✅ Atomic Operations

1. **Phone Check**: Mandatory before creating auth user
2. **Rollback**: Always delete auth user if profile creation fails
3. **Try-Catch**: Wrap all external calls
4. **Logging**: Log rollback operations for audit

### ✅ Validation

1. **Backend Validation**: Never trust frontend validation
2. **Regex Patterns**: Use strong patterns for email, password, phone
3. **Early Returns**: Validate and fail fast
4. **Clear Errors**: Provide specific error messages

### ✅ Service Communication

1. **Timeouts**: Set reasonable timeouts (30 seconds)
2. **Error Handling**: Handle all HTTP status codes
3. **Retry Logic**: Consider implementing retries (future)
4. **Circuit Breaker**: For resilience (future)

### ✅ Database

1. **Migrations**: Use EF Core migrations in production
2. **Indexing**: Index email column for fast lookups
3. **Connection Pooling**: Enabled by default in EF Core
4. **UTC Timestamps**: Always use UTC for consistency

---

## 12. Future Enhancements

### Suggested Improvements

1. **Email Verification**

   - Send verification email on registration
   - Verify email before allowing login

2. **Password Reset with OTP**

   - Email OTP for password reset
   - Time-limited reset tokens

3. **Account Lockout**

   - Lock account after N failed login attempts
   - Temporary lockout duration

4. **Refresh Tokens**

   - Implement refresh token mechanism
   - Long-lived refresh, short-lived access tokens

5. **Two-Factor Authentication (2FA)**

   - SMS or TOTP-based 2FA
   - Optional for users

6. **Rate Limiting**

   - Limit login attempts per IP
   - Prevent brute-force attacks

7. **Audit Logging**

   - Log all authentication events
   - Track login history

8. **OAuth/SSO Integration**
   - Google, Facebook, Microsoft login
   - SAML for enterprise

---

## 13. Testing

### Unit Test Examples

```csharp
[Fact]
public async Task Register_ValidInput_ReturnsCreated()
{
    // Arrange
    var dto = new RegisterDto(
        Email: "test@example.com",
        Password: "SecurePass123!",
        ConfirmPassword: "SecurePass123!",
        FullName: "Test User",
        PhoneNumber: "+919876543210",
        Address: "Test Address"
    );

    // Act
    var result = await _controller.Register(dto);

    // Assert
    Assert.IsType<CreatedAtActionResult>(result);
}

[Fact]
public async Task Login_ValidCredentials_ReturnsToken()
{
    // Arrange
    var dto = new LoginDto("test@example.com", "SecurePass123!");

    // Act
    var result = await _controller.Login(dto);

    // Assert
    var okResult = Assert.IsType<OkObjectResult>(result);
    var response = Assert.IsType<AuthResponseDto>(okResult.Value);
    Assert.NotNull(response.Token);
}
```

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Service Port:** 5001  
**Database:** authdb  
**Author:** MVP E-Commerce Team
