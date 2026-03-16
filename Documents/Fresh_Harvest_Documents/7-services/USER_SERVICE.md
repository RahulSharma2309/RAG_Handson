# 👤 User Service - Complete Documentation

**User Profile & Wallet Management Microservice**

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Architecture & Design](#2-architecture--design)
3. [Database Schema](#3-database-schema)
4. [API Endpoints](#4-api-endpoints)
5. [Business Logic Deep Dive](#5-business-logic-deep-dive)
6. [Wallet Management](#6-wallet-management)
7. [Service-to-Service Communication](#7-service-to-service-communication)
8. [Configuration](#8-configuration)
9. [Code Walkthrough](#9-code-walkthrough)
10. [Error Handling](#10-error-handling)
11. [Best Practices](#11-best-practices)

---

## 1. Service Overview

### Purpose

The **User Service** is responsible for:

- User profile management (personal information)
- Wallet management (balance operations)
- Phone number uniqueness validation
- User data storage and retrieval
- Wallet debit/credit operations for payments

### Key Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Profile Management** | Create, read, update user profiles |
| **Wallet Operations** | Debit, credit, and balance management |
| **Phone Validation** | Check phone number uniqueness |
| **Data Persistence** | Store user profiles in userdb |
| **Balance Tracking** | Maintain wallet balance with transactions |

### Technology Stack

- **.NET 8** - Framework
- **Entity Framework Core** - ORM
- **SQL Server** - Database (userdb)
- **Repository Pattern** - Data access layer
- **Service Layer** - Business logic encapsulation

### Port & Database

- **Port**: `5005`
- **Database**: `userdb`
- **Docker Service Name**: `user-service`

---

## 2. Architecture & Design

### High-Level Architecture

```
┌──────────────────────────────────────────────┐
│         Auth Service (Port 5001)             │
│  Calls User Service for:                     │
│  • Phone validation during registration      │
│  • Profile creation after auth user created  │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│          User Service (Port 5005)            │
│                                              │
│  Controllers:                                │
│  • UsersController - /api/users/*           │
│                                              │
│  Services:                                   │
│  • UserServiceImpl - Business logic         │
│                                              │
│  Repositories:                               │
│  • UserRepository - Data access             │
│                                              │
│  Data:                                       │
│  • AppDbContext - EF Core                   │
│  • UserProfile entity                        │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
        ┌────────────────────┐
        │   SQL Server       │
        │   userdb           │
        │                    │
        │  UserProfiles      │
        └────────────────────┘

┌──────────────────────────────────────────────┐
│     Payment Service (Port 5003)              │
│  Calls User Service for:                     │
│  • Wallet debit (payment processing)         │
│  • Wallet credit (refunds)                   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│      Order Service (Port 5004)               │
│  Calls User Service for:                     │
│  • Get user profile by userId                │
└──────────────────────────────────────────────┘
```

### Service Dependencies

**Depends On:**
- None (User Service is independent)

**Depended On By:**
- **Auth Service** (phone validation, profile creation)
- **Payment Service** (wallet operations)
- **Order Service** (user profile retrieval)

### Design Patterns

1. **Repository Pattern** - Data access abstraction
2. **Service Layer Pattern** - Business logic encapsulation
3. **DTO Pattern** - Data transfer objects for API contracts
4. **Dependency Injection** - Loose coupling
5. **Unit of Work** - EF Core DbContext

---

## 3. Database Schema

### Database: `userdb`

### Table: `UserProfiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | Guid | PRIMARY KEY, DEFAULT NEWID() | Profile unique identifier |
| `UserId` | Guid | UNIQUE, NOT NULL | Auth service user ID |
| `FirstName` | nvarchar(100) | NULL | User's first name |
| `LastName` | nvarchar(100) | NULL | User's last name |
| `Address` | nvarchar(500) | NULL | User's address |
| `PhoneNumber` | nvarchar(50) | UNIQUE, NOT NULL | User's phone number |
| `WalletBalance` | decimal(18,2) | DEFAULT 0 | Wallet balance in INR |
| `CreatedAt` | datetime2 | DEFAULT GETUTCDATE() | Profile creation timestamp |
| `UpdatedAt` | datetime2 | DEFAULT GETUTCDATE() | Last update timestamp |

### Entity Model

```csharp
public class UserProfile
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid UserId { get; set; }  // Maps to Auth Service user ID
    
    [MaxLength(100)]
    public string? FirstName { get; set; }
    
    [MaxLength(100)]
    public string? LastName { get; set; }
    
    [MaxLength(500)]
    public string? Address { get; set; }
    
    [MaxLength(50)]
    public string? PhoneNumber { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal WalletBalance { get; set; } = 0;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
```

### Key Characteristics

- **Two IDs**: 
  - `Id` - Internal profile ID (Guid)
  - `UserId` - Auth Service user ID (Guid)
- **Phone Uniqueness**: Enforced at database level
- **Decimal Precision**: `decimal(18,2)` for wallet balance
- **UTC Timestamps**: All timestamps in UTC
- **INR Currency**: Wallet balance in Indian Rupees

### Indexes

```sql
CREATE UNIQUE INDEX IX_UserProfiles_UserId ON UserProfiles(UserId);
CREATE UNIQUE INDEX IX_UserProfiles_PhoneNumber ON UserProfiles(PhoneNumber);
CREATE INDEX IX_UserProfiles_CreatedAt ON UserProfiles(CreatedAt);
```

---

## 4. API Endpoints

### Base Path: `/api/users`

### 1. **GET /api/users/{id}** - Get Profile by ID

**Description**: Get user profile by internal profile ID

**Parameters**:
- `id` (Guid) - Profile ID

**Success Response (200 OK)**:

```json
{
  "id": "profile-guid",
  "userId": "user-guid",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St, City",
  "walletBalance": 5000.00,
  "createdAt": "2025-12-24T10:30:00Z",
  "updatedAt": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Description |
|--------|-------------|
| `404` | Profile not found |

---

### 2. **GET /api/users/by-userid/{userId}** - Get Profile by User ID

**Description**: Get user profile by Auth Service user ID

**Parameters**:
- `userId` (Guid) - Auth Service user ID

**Success Response (200 OK)**:

```json
{
  "id": "profile-guid",
  "userId": "user-guid",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St, City",
  "walletBalance": 5000.00,
  "createdAt": "2025-12-24T10:30:00Z",
  "updatedAt": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Description |
|--------|-------------|
| `404` | Profile not found for this userId |

**Usage**: Called by Order Service to get profile details

---

### 3. **GET /api/users/phone-exists/{phoneNumber}** - Check Phone Exists

**Description**: Check if phone number is already registered

**Parameters**:
- `phoneNumber` (string) - Phone number to check

**Success Response (200 OK)**:

```json
{
  "exists": true
}
```

**Usage**: Called by Auth Service during registration

---

### 4. **POST /api/users** - Create User Profile

**Description**: Create a new user profile (called by Auth Service)

**Request Body**:

```json
{
  "userId": "user-guid",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St, City"
}
```

**Validation Rules**:
- ✅ UserId: Required (Guid, not Empty)
- ✅ PhoneNumber: Required, 10-15 digits
- ✅ Phone must be unique

**Success Response (201 Created)**:

```json
{
  "id": "profile-guid",
  "userId": "user-guid",
  "firstName": "John",
  "lastName": "Doe",
  "phoneNumber": "+919876543210",
  "address": "123 Main St, City",
  "walletBalance": 0.00,
  "createdAt": "2025-12-24T10:30:00Z",
  "updatedAt": "2025-12-24T10:30:00Z"
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | UserId is required | Missing userId |
| `400` | Phone number is required | Missing phone |
| `400` | Invalid phone number format | Invalid format |
| `400` | Phone number already registered | Duplicate phone |

---

### 5. **PUT /api/users/{id}** - Update User Profile

**Description**: Update existing user profile

**Parameters**:
- `id` (Guid) - Profile ID

**Request Body**:

```json
{
  "userId": "user-guid",  // Ignored in update
  "firstName": "John",
  "lastName": "Smith",
  "phoneNumber": "+919876543210",
  "address": "456 New St, City"
}
```

**Success Response (200 OK)**:

```json
{
  "id": "profile-guid",
  "userId": "user-guid",  // Unchanged
  "firstName": "John",
  "lastName": "Smith",
  "phoneNumber": "+919876543210",
  "address": "456 New St, City",
  "walletBalance": 5000.00,
  "createdAt": "2025-12-24T10:30:00Z",
  "updatedAt": "2025-12-24T12:00:00Z"
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `404` | Profile not found | Invalid profile ID |
| `400` | Phone number already registered | Duplicate phone |

---

### 6. **POST /api/users/{id}/wallet/debit** - Debit Wallet

**Description**: Debit amount from user's wallet (called by Payment Service)

**Parameters**:
- `id` (Guid) - Profile ID

**Request Body**:

```json
{
  "amount": 1999.00
}
```

**Success Response (200 OK)**:

```json
{
  "id": "profile-guid",
  "balance": 3001.00
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | Amount must be > 0 | Invalid amount |
| `404` | Profile not found | Invalid profile ID |
| `409` | Insufficient balance | Balance < amount |

---

### 7. **POST /api/users/{id}/wallet/credit** - Credit Wallet

**Description**: Credit amount to user's wallet (refunds, add balance)

**Parameters**:
- `id` (Guid) - Profile ID

**Request Body**:

```json
{
  "amount": 2000.00
}
```

**Success Response (200 OK)**:

```json
{
  "id": "profile-guid",
  "balance": 7000.00
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | Amount must be > 0 | Invalid amount |
| `404` | Profile not found | Invalid profile ID |

---

### 8. **POST /api/users/add-balance** - Add Balance (Public Endpoint)

**Description**: Add balance to user's wallet using userId

**Request Body**:

```json
{
  "userId": "user-guid",
  "amount": 5000.00
}
```

**Success Response (200 OK)**:

```json
{
  "userId": "user-guid",
  "balance": 10000.00,
  "message": "Successfully added ₹5000 to wallet. New balance: ₹10000"
}
```

**Error Responses**:

| Status | Error | Description |
|--------|-------|-------------|
| `400` | UserId is required | Missing userId |
| `400` | Amount must be greater than 0 | Invalid amount |
| `404` | User profile not found | Invalid userId |

---

## 5. Business Logic Deep Dive

### Profile Creation Flow

```
1. Validate Input
   ├─ UserId must not be Guid.Empty
   ├─ PhoneNumber required
   └─ PhoneNumber format validation (regex)

2. Check Phone Uniqueness
   └─ Query userdb by PhoneNumber

3. Check Existing Profile by UserId
   ├─ If exists → Update and return
   └─ If not exists → Create new

4. Create UserProfile
   ├─ Generate new Guid (Id)
   ├─ Set UserId from request
   ├─ Set WalletBalance = 0
   ├─ Set CreatedAt = UtcNow
   └─ Set UpdatedAt = UtcNow

5. Save to Database
   └─ EF Core SaveChangesAsync()

6. Return DTO
   └─ Convert entity to UserProfileDto
```

### Code Implementation

```csharp
public async Task<UserProfileDto> CreateAsync(CreateUserDto dto)
{
    // 1. Validate input
    if (dto.UserId == Guid.Empty)
        throw new ArgumentException("UserId is required");
    
    if (string.IsNullOrWhiteSpace(dto.PhoneNumber))
        throw new ArgumentException("Phone number is required");
    
    if (!Regex.IsMatch(dto.PhoneNumber, @"^\+?\d{10,15}$"))
        throw new ArgumentException("Invalid phone number format");
    
    // 2. Check phone uniqueness
    var existingPhone = await _repo.GetByPhoneNumberAsync(dto.PhoneNumber);
    if (existingPhone != null)
        throw new ArgumentException("Phone number already registered");
    
    // 3. Check if profile already exists for this UserId
    var existing = await _repo.GetByUserIdAsync(dto.UserId);
    if (existing != null)
    {
        // Update existing profile (idempotency)
        existing.FirstName = dto.FirstName;
        existing.LastName = dto.LastName;
        existing.Address = dto.Address;
        existing.PhoneNumber = dto.PhoneNumber;
        existing.UpdatedAt = DateTime.UtcNow;
        
        var updated = await _repo.UpdateAsync(existing);
        return UserProfileDto.FromModel(updated);
    }
    
    // 4. Create new profile
    var model = new UserProfile
    {
        UserId = dto.UserId,
        FirstName = dto.FirstName,
        LastName = dto.LastName,
        Address = dto.Address,
        PhoneNumber = dto.PhoneNumber,
        WalletBalance = 0,
        CreatedAt = DateTime.UtcNow,
        UpdatedAt = DateTime.UtcNow
    };
    
    // 5. Save to database
    var created = await _repo.CreateAsync(model);
    
    // 6. Return DTO
    return UserProfileDto.FromModel(created);
}
```

---

## 6. Wallet Management

### Wallet Debit Operation

**Purpose**: Deduct amount from wallet (payment processing)

**Flow**:

```
1. Validate Input
   └─ Amount must be > 0

2. Get User Profile
   └─ By profile ID (Guid)

3. Check Sufficient Balance
   ├─ If balance < amount → throw InvalidOperationException
   └─ If balance >= amount → proceed

4. Debit Wallet
   ├─ walletBalance -= amount
   └─ updatedAt = UtcNow

5. Save Changes
   └─ EF Core SaveChangesAsync()

6. Return New Balance
   └─ Return decimal balance
```

**Code Implementation**:

```csharp
public async Task<decimal> DebitWalletAsync(Guid id, decimal amount)
{
    if (amount <= 0)
        throw new ArgumentException("Amount must be greater than 0");
    
    var profile = await _context.UserProfiles.FindAsync(id);
    if (profile == null)
        throw new KeyNotFoundException($"User profile not found: {id}");
    
    if (profile.WalletBalance < amount)
        throw new InvalidOperationException(
            $"Insufficient balance. Available: {profile.WalletBalance}, Required: {amount}");
    
    profile.WalletBalance -= amount;
    profile.UpdatedAt = DateTime.UtcNow;
    
    await _context.SaveChangesAsync();
    
    return profile.WalletBalance;
}
```

### Wallet Credit Operation

**Purpose**: Add amount to wallet (refunds, add balance)

**Flow**:

```
1. Validate Input
   └─ Amount must be > 0

2. Get User Profile
   └─ By profile ID (Guid)

3. Credit Wallet
   ├─ walletBalance += amount
   └─ updatedAt = UtcNow

4. Save Changes
   └─ EF Core SaveChangesAsync()

5. Return New Balance
   └─ Return decimal balance
```

**Code Implementation**:

```csharp
public async Task<decimal> CreditWalletAsync(Guid id, decimal amount)
{
    if (amount <= 0)
        throw new ArgumentException("Amount must be greater than 0");
    
    var profile = await _context.UserProfiles.FindAsync(id);
    if (profile == null)
        throw new KeyNotFoundException($"User profile not found: {id}");
    
    profile.WalletBalance += amount;
    profile.UpdatedAt = DateTime.UtcNow;
    
    await _context.SaveChangesAsync();
    
    return profile.WalletBalance;
}
```

### Add Balance Flow (Public API)

**Purpose**: Allow users to add money to their wallet

**Flow**:

```
1. Validate Input
   ├─ userId must not be Guid.Empty
   └─ amount must be > 0

2. Get Profile by userId
   └─ Call GetByUserIdAsync(userId)

3. If Not Found
   └─ Return 404

4. Credit Wallet
   └─ Call CreditWalletAsync(profile.Id, amount)

5. Return Success Response
   └─ Include userId, new balance, message
```

---

## 7. Service-to-Service Communication

### Incoming Calls

#### From Auth Service

1. **Phone Number Check**:
   ```
   GET /api/users/phone-exists/{phoneNumber}
   ```

2. **Profile Creation**:
   ```
   POST /api/users
   Body: { userId, firstName, lastName, phoneNumber, address }
   ```

#### From Payment Service

1. **Wallet Debit**:
   ```
   POST /api/users/{id}/wallet/debit
   Body: { amount }
   ```

2. **Wallet Credit (Refund)**:
   ```
   POST /api/users/{id}/wallet/credit
   Body: { amount }
   ```

#### From Order Service

1. **Get Profile**:
   ```
   GET /api/users/by-userid/{userId}
   ```

### No Outgoing Calls

User Service does **not** call any other services. It's a leaf node in the dependency graph.

---

## 8. Configuration

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost,1433;Database=userdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

### Docker Configuration

**docker-compose.yml**:

```yaml
user-service:
  build:
    context: ../services/user-service
    dockerfile: Dockerfile
  ports:
    - "5005:80"
  environment:
    - ASPNETCORE_ENVIRONMENT=Development
    - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=userdb;User=sa;Password=YourPassword123!;TrustServerCertificate=True;
  depends_on:
    - sqlserver
  networks:
    - ecommerce-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

---

## 9. Code Walkthrough

### Project Structure

```
user-service/
├── Controllers/
│   └── UsersController.cs          # API endpoints
├── Models/
│   └── UserProfile.cs              # Entity model
├── Services/
│   ├── IUserService.cs             # Service interface
│   └── UserServiceImpl.cs          # Service implementation
├── Repositories/
│   ├── IUserRepository.cs          # Repository interface
│   └── UserRepository.cs           # Repository implementation
├── Dtos/
│   ├── UserProfileDto.cs           # Profile response DTO
│   ├── CreateUserDto.cs            # Create request DTO
│   ├── AddBalanceDto.cs            # Add balance request DTO
│   └── WalletOperationDto.cs       # Wallet operation DTO
├── Data/
│   └── AppDbContext.cs             # EF Core context
├── Startup.cs                      # Service configuration
├── Program.cs                      # Application entry
└── user-service.csproj             # Project file
```

### Layered Architecture

```
Controllers (HTTP Layer)
    ↓ calls
Services (Business Logic Layer)
    ↓ calls
Repositories (Data Access Layer)
    ↓ calls
Database (Persistence Layer)
```

### Repository Pattern Implementation

**IUserRepository.cs**:

```csharp
public interface IUserRepository
{
    Task<UserProfile?> GetByIdAsync(Guid id);
    Task<UserProfile?> GetByUserIdAsync(Guid userId);
    Task<UserProfile?> GetByPhoneNumberAsync(string phoneNumber);
    Task<UserProfile> CreateAsync(UserProfile profile);
    Task<UserProfile> UpdateAsync(UserProfile profile);
    Task<decimal> DebitWalletAsync(Guid id, decimal amount);
    Task<decimal> CreditWalletAsync(Guid id, decimal amount);
}
```

**UserRepository.cs**:

```csharp
public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;
    
    public async Task<UserProfile?> GetByIdAsync(Guid id)
    {
        return await _context.UserProfiles.FindAsync(id);
    }
    
    public async Task<UserProfile?> GetByUserIdAsync(Guid userId)
    {
        return await _context.UserProfiles
            .FirstOrDefaultAsync(u => u.UserId == userId);
    }
    
    public async Task<UserProfile?> GetByPhoneNumberAsync(string phoneNumber)
    {
        return await _context.UserProfiles
            .FirstOrDefaultAsync(u => u.PhoneNumber == phoneNumber);
    }
    
    // ... other methods
}
```

---

## 10. Error Handling

### Error Response Format

```json
{
  "error": "Human-readable error message"
}
```

### Common Errors

| Scenario | Status Code | Response |
|----------|-------------|----------|
| Profile not found | 404 | `NotFound()` |
| Invalid amount | 400 | `{ "error": "Amount must be > 0" }` |
| Insufficient balance | 409 | `{ "error": "Insufficient balance" }` |
| Duplicate phone | 400 | `{ "error": "Phone number already registered" }` |
| Invalid phone format | 400 | `{ "error": "Invalid phone number format" }` |
| Missing userId | 400 | `{ "error": "UserId is required" }` |

### Exception Handling

```csharp
[HttpPost("{id:guid}/wallet/debit")]
public async Task<IActionResult> DebitWallet(Guid id, [FromBody] WalletOperationDto dto)
{
    try
    {
        var balance = await _service.DebitWalletAsync(id, dto.Amount);
        return Ok(new { id, balance });
    }
    catch (KeyNotFoundException)
    {
        return NotFound();
    }
    catch (InvalidOperationException ex)
    {
        return Conflict(new { error = ex.Message });
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Wallet debit failed for profile {Id}", id);
        return StatusCode(500, new { error = "Wallet operation failed" });
    }
}
```

---

## 11. Best Practices

### ✅ Data Consistency

1. **Guid Usage**: All IDs are Guid for consistency
2. **Decimal for Money**: Use `decimal(18,2)` for currency
3. **UTC Timestamps**: Always use UTC for timestamps
4. **UpdatedAt**: Update timestamp on every modification

### ✅ Validation

1. **Phone Format**: Use regex for validation
2. **Amount Validation**: Always check amount > 0
3. **Uniqueness**: Enforce phone uniqueness
4. **Idempotency**: Update if profile exists for userId

### ✅ Repository Pattern

1. **Separation of Concerns**: Data access logic isolated
2. **Testability**: Easy to mock repositories
3. **Maintainability**: Change data access without changing business logic

### ✅ Service Layer

1. **Business Logic**: Keep all logic in service layer
2. **Validation**: Perform validation in service layer
3. **Exception Handling**: Throw meaningful exceptions

### ✅ Wallet Operations

1. **Atomicity**: Use database transactions
2. **Balance Checks**: Always verify sufficient balance
3. **Logging**: Log all wallet operations
4. **Audit Trail**: Consider adding wallet transaction history (future)

---

## 12. Future Enhancements

### Suggested Improvements

1. **Wallet Transaction History**
   - Create `WalletTransactions` table
   - Record every debit/credit with timestamp
   - Provide transaction history API

2. **Profile Photos**
   - Add `ProfilePhotoUrl` field
   - Support image upload
   - Use blob storage (Azure, S3)

3. **Email Notification**
   - Send email on balance changes
   - Low balance alerts

4. **Soft Delete**
   - Add `IsDeleted` flag
   - Archive instead of hard delete

5. **Pagination**
   - Add pagination for profile lists
   - Search and filter capabilities

6. **Caching**
   - Cache frequently accessed profiles
   - Use Redis for distributed cache

7. **Audit Logging**
   - Track all profile changes
   - Who changed what and when

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Service Port:** 5005  
**Database:** userdb  
**Author:** MVP E-Commerce Team


