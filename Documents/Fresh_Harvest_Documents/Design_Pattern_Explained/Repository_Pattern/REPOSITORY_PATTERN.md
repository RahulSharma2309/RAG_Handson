# Understanding the Repository Pattern Through Product Service

## Table of Contents

1. [Introduction](#introduction)
2. [The Problem: Traditional Approach](#the-problem-traditional-approach)
3. [Problems with Direct Database Access](#problems-with-direct-database-access)
4. [The Solution: Repository Pattern](#the-solution-repository-pattern)
5. [Understanding the Components](#understanding-the-components)
6. [How It Works: Complete Flow](#how-it-works-complete-flow)
7. [Key Benefits Explained](#key-benefits-explained)
8. [Dependency Injection: The Glue](#dependency-injection-the-glue)
9. [Testing: The Game Changer](#testing-the-game-changer)
10. [Real-World Example: Stock Reservation](#real-world-example-stock-reservation)
11. [Common Patterns and Practices](#common-patterns-and-practices)
12. [Summary](#summary)

---

## Introduction

The **Repository Pattern** is a design pattern that provides an abstraction layer between business logic and data access. It acts as a mediator between the domain and data mapping layers, using a collection-like interface for accessing domain objects.

**In simple terms**: Instead of directly accessing the database from business logic, the repository pattern creates a layer that handles all database operations, making the code more maintainable, testable, and flexible.

This guide uses the **Product Service** from the FreshHarvest Market codebase to demonstrate every aspect of the repository pattern, from the problems it solves to its complete implementation.

---

## The Problem: Traditional Approach

### How It Used to Be Done

Before the repository pattern, applications typically accessed the database directly from controllers or business logic. Let's see what this looked like:

```csharp
// ❌ TRADITIONAL APPROACH - Direct DbContext Usage
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly AppDbContext _db;  // Direct database access

    public ProductsController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        // Database query directly in controller
        var product = await _db.Products.FindAsync(id);
        
        if (product == null)
            return NotFound();
            
        return Ok(product);
    }

    [HttpPost]
    public async Task<IActionResult> Create(CreateProductDto dto)
    {
        // Business validation mixed with database code
        if (string.IsNullOrWhiteSpace(dto.Name))
            return BadRequest("Name is required");
            
        if (dto.Price < 0)
            return BadRequest("Price must be >= 0");

        // Database operation directly in controller
        var product = new Product
        {
            Name = dto.Name,
            Price = dto.Price,
            Stock = dto.Stock
        };
        
        _db.Products.Add(product);
        await _db.SaveChangesAsync();
        
        return CreatedAtAction(nameof(GetById), new { id = product.Id }, product);
    }

    [HttpPost("{id}/reserve")]
    public async Task<IActionResult> Reserve(Guid id, int quantity)
    {
        // Complex transaction logic in controller
        using var tx = await _db.Database.BeginTransactionAsync();
        
        var product = await _db.Products.FindAsync(id);
        if (product == null)
            return NotFound();
            
        if (product.Stock < quantity)
            return Conflict("Insufficient stock");
            
        product.Stock -= quantity;
        await _db.SaveChangesAsync();
        await tx.CommitAsync();
        
        return Ok(new { remaining = product.Stock });
    }
}
```

### What's Wrong Here?

This approach has several issues:

1. **Tight Coupling**: Controllers are directly coupled to Entity Framework (`AppDbContext`)
2. **Mixed Responsibilities**: HTTP concerns, business logic, and data access are all mixed together
3. **Hard to Test**: Requires a real database connection for testing
4. **Code Duplication**: Same database queries scattered across multiple controllers
5. **Difficult to Change**: Switching databases requires changing code everywhere
6. **No Abstraction**: Business logic knows about database implementation details

---

## Problems with Direct Database Access

Let's examine each problem in detail:

### Problem 1: Tight Coupling

**Issue**: Controllers directly depend on `AppDbContext`, which is an Entity Framework Core class.

```csharp
// Controller is tightly coupled to Entity Framework
private readonly AppDbContext _db;  // Can't easily swap this out
```

**Impact**: If you want to switch from SQL Server to MongoDB, you'd need to change every controller.

### Problem 2: Testing Nightmare

**Issue**: To test controllers, you need a real database.

```csharp
// How do you test this without a database?
[Fact]
public async Task GetById_ReturnsProduct()
{
    // ❌ Need to set up SQL Server, create test data, etc.
    var controller = new ProductsController(realDbContext);
    var result = await controller.GetById(testId);
    // ...
}
```

**Impact**: Tests are slow, require database setup, and are fragile.

### Problem 3: Code Duplication

**Issue**: The same database queries appear in multiple places.

```csharp
// In ProductsController
var product = await _db.Products.FindAsync(id);

// In OrderService (if it needs product info)
var product = await _db.Products.FindAsync(id);

// In PaymentService
var product = await _db.Products.FindAsync(id);
```

**Impact**: If the query logic changes, you must update it in multiple places.

### Problem 4: Mixed Responsibilities

**Issue**: Controllers handle HTTP, business logic, AND data access.

```csharp
[HttpPost]
public async Task<IActionResult> Create(CreateProductDto dto)
{
    // HTTP concern: reading request
    // Business logic: validation
    if (string.IsNullOrWhiteSpace(dto.Name))
        return BadRequest("Name is required");
    
    // Data access: database operation
    _db.Products.Add(product);
    await _db.SaveChangesAsync();
    
    // HTTP concern: returning response
    return CreatedAtAction(...);
}
```

**Impact**: Violates Single Responsibility Principle, makes code harder to maintain.

### Problem 5: No Abstraction

**Issue**: Business logic knows about database implementation details.

```csharp
// Business logic knows about Entity Framework
var product = await _db.Products
    .Include(p => p.Category)  // EF-specific
    .FirstOrDefaultAsync(p => p.Id == id);
```

**Impact**: Changing ORM or database requires changing business logic.

---

## The Solution: Repository Pattern

The repository pattern solves all these problems by introducing an abstraction layer between business logic and data access.

### The Core Concept

Instead of accessing the database directly, we create a **repository** that acts as a collection-like interface for domain objects. The repository handles all database operations, and business logic only interacts with the repository interface.

### Architecture Overview

```
┌─────────────────────────────────────┐
│   Controller (HTTP Layer)           │
│   - Handles HTTP requests/responses │
│   - No database knowledge           │
└──────────────┬──────────────────────┘
               │ depends on
┌──────────────▼──────────────────────┐
│   Service (Business Logic)          │
│   - Business rules & validation     │
│   - Orchestration                   │
│   - No database knowledge           │
└──────────────┬──────────────────────┘
               │ depends on
┌──────────────▼──────────────────────┐
│   Repository Interface              │
│   - Defines data operations         │
│   - No implementation details       │
└──────────────┬──────────────────────┘
               │ implemented by
┌──────────────▼──────────────────────┐
│   Repository Implementation         │
│   - Database queries                │
│   - Transactions                    │
│   - Entity Framework code           │
└──────────────┬──────────────────────┘
               │ uses
┌──────────────▼──────────────────────┐
│   DbContext (Entity Framework)      │
│   - ORM layer                       │
│   - SQL generation                  │
└──────────────┬──────────────────────┘
               │ connects to
┌──────────────▼──────────────────────┐
│   Database (SQL Server)             │
└─────────────────────────────────────┘
```

### How Product Service Implements It

Let's see how the Product Service implements the repository pattern:

**1. Repository Interface** (`IProductRepository`)
```csharp
public interface IProductRepository
{
    Task<List<Product>> GetAllAsync();
    Task<Product?> GetByIdAsync(Guid id);
    Task AddAsync(Product p);
    Task<int> ReserveAsync(Guid id, int quantity);
    Task<int> ReleaseAsync(Guid id, int quantity);
}
```

**2. Repository Implementation** (`ProductRepository`)
```csharp
public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _db;
    private readonly ILogger<ProductRepository> _logger;

    public ProductRepository(AppDbContext db, ILogger<ProductRepository> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        return await _db.Products.FindAsync(id);
    }
    
    // ... other methods
}
```

**3. Business Service** (`ProductServiceImpl`)
```csharp
public class ProductServiceImpl : IProductService
{
    private readonly IProductRepository _repo;  // Interface, not implementation!

    public ProductServiceImpl(IProductRepository repo)
    {
        _repo = repo;
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        // No database code here - just business logic
        return await _repo.GetByIdAsync(id);
    }
}
```

**4. Controller** (`ProductsController`)
```csharp
public class ProductsController : ControllerBase
{
    private readonly IProductService _service;  // Service, not repository!

    public ProductsController(IProductService service)
    {
        _service = service;
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        // No database code, no business logic - just HTTP
        var product = await _service.GetByIdAsync(id);
        if (product == null)
            return NotFound();
        return Ok(product);
    }
}
```

---

## Understanding the Components

Let's examine each component in detail using the Product Service example:

### 1. Repository Interface (`IProductRepository`)

**Purpose**: Defines the contract for data operations without implementation details.

**Location**: `services/product-service/src/ProductService.Core/Repository/IProductRepository.cs`

```csharp
public interface IProductRepository
{
    Task<List<Product>> GetAllAsync();
    Task<Product?> GetByIdAsync(Guid id);
    Task AddAsync(Product p);
    Task<int> ReserveAsync(Guid id, int quantity);
    Task<int> ReleaseAsync(Guid id, int quantity);
}
```

**Key Points**:
- **No implementation**: Only method signatures
- **Domain-focused**: Methods use domain objects (`Product`), not database entities
- **Async by default**: All operations are asynchronous
- **Clear contract**: Each method has a single, well-defined responsibility

**Why an Interface?**
- Enables dependency injection
- Allows mocking for testing
- Provides abstraction (can swap implementations)
- Follows Dependency Inversion Principle

### 2. Repository Implementation (`ProductRepository`)

**Purpose**: Contains the actual database access code.

**Location**: `services/product-service/src/ProductService.Core/Repository/ProductRepository.cs`

```csharp
public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _db;
    private readonly ILogger<ProductRepository> _logger;

    public ProductRepository(AppDbContext db, ILogger<ProductRepository> logger)
    {
        _db = db ?? throw new ArgumentNullException(nameof(db));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        _logger.LogDebug("Fetching product {ProductId} from database", id);
        try
        {
            var product = await _db.Products.FindAsync(id);
            if (product == null)
            {
                _logger.LogDebug("Product {ProductId} not found in database", id);
            }
            return product;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching product {ProductId} from database", id);
            throw;
        }
    }

    public async Task<int> ReserveAsync(Guid id, int quantity)
    {
        if (quantity <= 0)
            throw new ArgumentException("Quantity must be > 0", nameof(quantity));

        using var tx = await _db.Database.BeginTransactionAsync();
        try
        {
            var product = await _db.Products.FirstOrDefaultAsync(p => p.Id == id);
            if (product == null)
                throw new KeyNotFoundException("Product not found");

            if (product.Stock < quantity)
                throw new InvalidOperationException("Insufficient stock");

            product.Stock -= quantity;
            await _db.SaveChangesAsync();
            await tx.CommitAsync();

            return product.Stock;
        }
        catch
        {
            await tx.RollbackAsync();
            throw;
        }
    }
}
```

**Key Points**:
- **Implements interface**: `ProductRepository : IProductRepository`
- **Database-specific**: Contains Entity Framework code (`_db.Products`, `FindAsync`, etc.)
- **Transaction handling**: Manages database transactions
- **Error handling**: Catches and logs database errors
- **Logging**: Logs all database operations

**Responsibilities**:
- Execute database queries
- Handle transactions
- Map database results to domain objects
- Handle database-specific errors

### 3. Business Service (`ProductServiceImpl`)

**Purpose**: Contains business logic and orchestrates operations.

**Location**: `services/product-service/src/ProductService.Core/Business/ProductServiceImpl.cs`

```csharp
public class ProductServiceImpl : IProductService
{
    private readonly IProductRepository _repo;  // Interface, not implementation!
    private readonly ILogger<ProductServiceImpl> _logger;

    public ProductServiceImpl(IProductRepository repo, ILogger<ProductServiceImpl> logger)
    {
        _repo = repo ?? throw new ArgumentNullException(nameof(repo));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<Product?> GetByIdAsync(Guid id)
    {
        _logger.LogDebug("Fetching product {ProductId}", id);
        try
        {
            var product = await _repo.GetByIdAsync(id);
            // Business logic can be added here (e.g., caching, authorization)
            return product;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching product {ProductId}", id);
            throw;
        }
    }

    public async Task CreateAsync(Product p)
    {
        _logger.LogInformation("Creating new product: {ProductName}", p.Name);
        
        // Business validation
        ValidateForCreate(p);
        
        // Delegate to repository
        await _repo.AddAsync(p);
        
        _logger.LogInformation("Product created successfully: {ProductId}", p.Id);
    }

    private static void ValidateForCreate(Product p)
    {
        if (string.IsNullOrWhiteSpace(p.Name))
            throw new ArgumentException("Name is required", nameof(p.Name));

        if (p.Price < 0)
            throw new ArgumentException("Price must be >= 0", nameof(p.Price));

        if (p.Stock < 0)
            throw new ArgumentException("Stock must be >= 0", nameof(p.Stock));
    }
}
```

**Key Points**:
- **Depends on interface**: Uses `IProductRepository`, not `ProductRepository`
- **Business logic**: Contains validation, orchestration, business rules
- **No database code**: Doesn't know about Entity Framework or SQL
- **Reusable**: Can be used by multiple controllers or other services

**Responsibilities**:
- Business validation
- Business rules enforcement
- Orchestrating multiple repository calls
- Caching (if needed)
- Authorization checks

### 4. Controller (`ProductsController`)

**Purpose**: Handles HTTP requests and responses.

**Location**: `services/product-service/src/ProductService.API/Controllers/ProductsController.cs`

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _service;  // Service, not repository!
    private readonly ILogger<ProductsController> _logger;

    public ProductsController(IProductService service, ILogger<ProductsController> logger)
    {
        _service = service ?? throw new ArgumentNullException(nameof(service));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        _logger.LogDebug("Fetching product {ProductId}", id);

        try
        {
            var product = await _service.GetByIdAsync(id);
            if (product == null)
            {
                _logger.LogWarning("Product {ProductId} not found", id);
                return NotFound();
            }

            _logger.LogInformation("Successfully retrieved product {ProductId}", id);
            return Ok(product);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving product {ProductId}", id);
            return StatusCode(500, new { error = "Failed to retrieve product" });
        }
    }
}
```

**Key Points**:
- **Depends on service**: Uses `IProductService`, not repository directly
- **HTTP concerns only**: Routing, status codes, serialization
- **No business logic**: Doesn't contain validation or business rules
- **No database code**: Doesn't know about Entity Framework or SQL

**Responsibilities**:
- Handle HTTP requests
- Map HTTP responses (status codes, headers)
- Serialize/deserialize data
- Handle HTTP-specific errors

### 5. DbContext (`AppDbContext`)

**Purpose**: Entity Framework Core's database context.

**Location**: `services/product-service/src/ProductService.Core/Data/AppDbContext.cs`

```csharp
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options)
    {
    }

    public DbSet<Product> Products { get; set; } = null!;
}
```

**Key Points**:
- **ORM layer**: Entity Framework Core abstraction over database
- **Used by repository**: Repository uses this, not controllers or services
- **Database mapping**: Maps C# classes to database tables

---

## How It Works: Complete Flow

Let's trace a complete request through all layers:

### Example: Getting a Product by ID

**Request**: `GET /api/products/{id}`

#### Step 1: HTTP Request Arrives
```
HTTP GET /api/products/123e4567-e89b-12d3-a456-426614174000
```

#### Step 2: Controller Receives Request
```csharp
// ProductsController.GetById()
[HttpGet("{id}")]
public async Task<IActionResult> GetById(Guid id)
{
    // Controller only knows about the service interface
    var product = await _service.GetByIdAsync(id);
    // ...
}
```

**What happens**: Controller extracts the ID from the route and calls the service.

#### Step 3: Service Processes Request
```csharp
// ProductServiceImpl.GetByIdAsync()
public async Task<Product?> GetByIdAsync(Guid id)
{
    // Service only knows about the repository interface
    var product = await _repo.GetByIdAsync(id);
    // Could add business logic here (caching, authorization, etc.)
    return product;
}
```

**What happens**: Service may add business logic (caching, authorization) and delegates to repository.

#### Step 4: Repository Queries Database
```csharp
// ProductRepository.GetByIdAsync()
public async Task<Product?> GetByIdAsync(Guid id)
{
    // Repository knows about Entity Framework
    var product = await _db.Products.FindAsync(id);
    return product;
}
```

**What happens**: Repository uses Entity Framework to query the database.

#### Step 5: Entity Framework Generates SQL
```sql
SELECT * FROM Products WHERE Id = @id
```

**What happens**: Entity Framework converts the LINQ query to SQL and executes it.

#### Step 6: Database Returns Data
```
Product: { Id: "123e4567...", Name: "Laptop", Price: 1000, Stock: 5 }
```

#### Step 7: Data Flows Back Up
```
Database → Entity Framework → Repository → Service → Controller → HTTP Response
```

#### Step 8: HTTP Response
```json
HTTP 200 OK
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Laptop",
  "price": 1000,
  "stock": 5
}
```

### Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ HTTP Request: GET /api/products/{id}                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ProductsController.GetById(id)                              │
│ - Extracts ID from route                                    │
│ - Calls _service.GetByIdAsync(id)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ProductServiceImpl.GetByIdAsync(id)                         │
│ - Business logic (if any)                                   │
│ - Calls _repo.GetByIdAsync(id)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ ProductRepository.GetByIdAsync(id)                          │
│ - Uses _db.Products.FindAsync(id)                           │
│ - Entity Framework query                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ AppDbContext.Products.FindAsync(id)                         │
│ - Entity Framework Core                                     │
│ - Generates SQL: SELECT * FROM Products WHERE Id = @id     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ SQL Server Database                                         │
│ - Executes query                                            │
│ - Returns product data                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼ (Data flows back up)
┌─────────────────────────────────────────────────────────────┐
│ HTTP Response: 200 OK { "id": "...", "name": "Laptop" }    │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Benefits Explained

Now let's see how the repository pattern solves each problem:

### Benefit 1: Separation of Concerns ✅

**Before (Traditional)**:
```csharp
// Controller does everything
[HttpPost]
public async Task<IActionResult> Create(CreateProductDto dto)
{
    // HTTP concern
    if (string.IsNullOrWhiteSpace(dto.Name))
        return BadRequest("Name is required");
    
    // Business logic
    if (dto.Price < 0)
        return BadRequest("Price must be >= 0");
    
    // Data access
    var product = new Product { ... };
    _db.Products.Add(product);
    await _db.SaveChangesAsync();
    
    // HTTP concern
    return CreatedAtAction(...);
}
```

**After (Repository Pattern)**:
```csharp
// Controller: Only HTTP concerns
[HttpPost]
public async Task<IActionResult> Create(CreateProductDto dto)
{
    var product = new Product { ... };
    await _service.CreateAsync(product);  // Delegate to service
    return CreatedAtAction(...);
}

// Service: Only business logic
public async Task CreateAsync(Product p)
{
    ValidateForCreate(p);  // Business validation
    await _repo.AddAsync(p);  // Delegate to repository
}

// Repository: Only data access
public async Task AddAsync(Product p)
{
    _db.Products.Add(p);
    await _db.SaveChangesAsync();
}
```

**Result**: Each layer has a single, clear responsibility.

### Benefit 2: Testability ✅

**Before (Traditional)**:
```csharp
// ❌ Hard to test - needs real database
[Fact]
public async Task GetById_ReturnsProduct()
{
    // Must set up SQL Server, create test data, etc.
    var options = new DbContextOptionsBuilder<AppDbContext>()
        .UseSqlServer("Server=...;Database=TestDb;...")
        .Options;
    
    using var context = new AppDbContext(options);
    var controller = new ProductsController(context);
    
    // Slow, requires database setup
    var result = await controller.GetById(testId);
    // ...
}
```

**After (Repository Pattern)**:
```csharp
// ✅ Easy to test - mock the repository
[Fact]
public async Task GetById_ReturnsProduct()
{
    // Arrange: Create mock repository
    var mockRepo = new Mock<IProductRepository>();
    var expectedProduct = new Product 
    { 
        Id = testId, 
        Name = "Test Product" 
    };
    
    mockRepo.Setup(r => r.GetByIdAsync(testId))
        .ReturnsAsync(expectedProduct);
    
    // Act: Test service with mock
    var service = new ProductServiceImpl(mockRepo.Object, logger);
    var result = await service.GetByIdAsync(testId);
    
    // Assert: Verify behavior
    Assert.NotNull(result);
    Assert.Equal("Test Product", result.Name);
    
    // Fast, no database needed!
}
```

**Result**: Tests are fast, don't require a database, and are reliable.

### Benefit 3: Flexibility ✅

**Before (Traditional)**:
```csharp
// Tightly coupled to Entity Framework
private readonly AppDbContext _db;

// To switch to MongoDB, must change every controller
var product = await _db.Products.FindAsync(id);  // EF-specific
```

**After (Repository Pattern)**:
```csharp
// Service depends on interface, not implementation
private readonly IProductRepository _repo;

// To switch to MongoDB, only change repository implementation
// Service and controller code remain unchanged!

// New MongoDB repository
public class MongoProductRepository : IProductRepository
{
    private readonly IMongoCollection<Product> _collection;
    
    public async Task<Product?> GetByIdAsync(Guid id)
    {
        return await _collection.Find(p => p.Id == id).FirstOrDefaultAsync();
    }
}

// Register in DI container
services.AddScoped<IProductRepository, MongoProductRepository>();
// That's it! No other code changes needed.
```

**Result**: Can swap database implementations without changing business logic.

### Benefit 4: Code Reusability ✅

**Before (Traditional)**:
```csharp
// Same query duplicated in multiple places
// In ProductsController
var product = await _db.Products.FindAsync(id);

// In OrderService
var product = await _db.Products.FindAsync(id);

// In PaymentService
var product = await _db.Products.FindAsync(id);
```

**After (Repository Pattern)**:
```csharp
// Query defined once in repository
public async Task<Product?> GetByIdAsync(Guid id)
{
    return await _db.Products.FindAsync(id);
}

// Used everywhere through interface
// In ProductsController
var product = await _service.GetByIdAsync(id);

// In OrderService
var product = await _productRepo.GetByIdAsync(id);

// In PaymentService
var product = await _productRepo.GetByIdAsync(id);
```

**Result**: Database queries are centralized and reusable.

### Benefit 5: Maintainability ✅

**Before (Traditional)**:
```csharp
// Database queries scattered everywhere
// Hard to find and update
// In Controller 1
var products = await _db.Products.Where(p => p.Price > 100).ToListAsync();

// In Controller 2
var products = await _db.Products.Where(p => p.Price > 100).ToListAsync();

// In Service
var products = await _db.Products.Where(p => p.Price > 100).ToListAsync();
```

**After (Repository Pattern)**:
```csharp
// All queries in one place
public class ProductRepository : IProductRepository
{
    public async Task<List<Product>> GetExpensiveProductsAsync()
    {
        return await _db.Products.Where(p => p.Price > 100).ToListAsync();
    }
}

// Used everywhere
var products = await _repo.GetExpensiveProductsAsync();
```

**Result**: Easy to find, update, and maintain database queries.

---

## Dependency Injection: The Glue

Dependency Injection (DI) is what makes the repository pattern work. It allows us to inject interfaces instead of concrete classes.

### How It Works in Product Service

**Registration** (in `Startup.cs`):
```csharp
public void ConfigureServices(IServiceCollection services)
{
    // Register DbContext
    services.AddDbContext<AppDbContext>(options =>
        options.UseSqlServer(connectionString));
    
    // Register Repository (interface → implementation)
    services.AddScoped<IProductRepository, ProductRepository>();
    
    // Register Service (interface → implementation)
    services.AddScoped<IProductService, ProductServiceImpl>();
}
```

**What This Means**:
- When something asks for `IProductRepository`, give it `ProductRepository`
- When something asks for `IProductService`, give it `ProductServiceImpl`
- `AddScoped` means one instance per HTTP request

### Dependency Chain

```
ProductsController
    constructor(IProductService service)  ← DI injects ProductServiceImpl
        ↓
ProductServiceImpl
    constructor(IProductRepository repo)  ← DI injects ProductRepository
        ↓
ProductRepository
    constructor(AppDbContext db)  ← DI injects AppDbContext
        ↓
AppDbContext
    constructor(DbContextOptions<AppDbContext> options)  ← DI injects options
```

### Why This Matters

**Without DI**:
```csharp
// ❌ Hard-coded dependencies
public class ProductsController : ControllerBase
{
    private readonly IProductService _service;
    
    public ProductsController()
    {
        // Can't easily swap implementations
        var db = new AppDbContext(...);
        var repo = new ProductRepository(db);
        _service = new ProductServiceImpl(repo);
    }
}
```

**With DI**:
```csharp
// ✅ Dependencies injected
public class ProductsController : ControllerBase
{
    private readonly IProductService _service;
    
    public ProductsController(IProductService service)  // Injected!
    {
        _service = service;
    }
}
```

**Benefits**:
- Easy to swap implementations (just change DI registration)
- Easy to test (inject mocks)
- Loose coupling (depends on interfaces, not implementations)

---

## Testing: The Game Changer

The repository pattern makes testing dramatically easier. Let's see how:

### Testing the Service Layer

**Example: Testing ProductService.GetByIdAsync()**

```csharp
[Fact]
public async Task GetByIdAsync_ReturnsProduct_WhenProductExists()
{
    // Arrange
    var productId = Guid.NewGuid();
    var expectedProduct = new Product
    {
        Id = productId,
        Name = "Test Laptop",
        Price = 1000,
        Stock = 5
    };
    
    // Create mock repository
    var mockRepo = new Mock<IProductRepository>();
    mockRepo.Setup(r => r.GetByIdAsync(productId))
        .ReturnsAsync(expectedProduct);
    
    var logger = new Mock<ILogger<ProductServiceImpl>>();
    var service = new ProductServiceImpl(mockRepo.Object, logger.Object);
    
    // Act
    var result = await service.GetByIdAsync(productId);
    
    // Assert
    Assert.NotNull(result);
    Assert.Equal(productId, result.Id);
    Assert.Equal("Test Laptop", result.Name);
    
    // Verify repository was called correctly
    mockRepo.Verify(r => r.GetByIdAsync(productId), Times.Once);
}
```

**Key Points**:
- ✅ No database needed
- ✅ Fast execution
- ✅ Isolated testing (only tests service logic)
- ✅ Can test edge cases easily

### Testing the Controller Layer

**Example: Testing ProductsController.GetById()**

```csharp
[Fact]
public async Task GetById_ReturnsOk_WhenProductExists()
{
    // Arrange
    var productId = Guid.NewGuid();
    var product = new Product { Id = productId, Name = "Test Product" };
    
    // Mock service (not repository!)
    var mockService = new Mock<IProductService>();
    mockService.Setup(s => s.GetByIdAsync(productId))
        .ReturnsAsync(product);
    
    var logger = new Mock<ILogger<ProductsController>>();
    var controller = new ProductsController(mockService.Object, logger.Object);
    
    // Act
    var result = await controller.GetById(productId);
    
    // Assert
    var okResult = Assert.IsType<OkObjectResult>(result);
    var returnedProduct = Assert.IsType<Product>(okResult.Value);
    Assert.Equal(productId, returnedProduct.Id);
}
```

**Key Points**:
- ✅ Tests HTTP layer in isolation
- ✅ No need to mock repository (service is mocked)
- ✅ Fast and reliable

### Testing the Repository Layer

**Example: Testing ProductRepository with In-Memory Database**

```csharp
[Fact]
public async Task GetByIdAsync_ReturnsProduct_WhenProductExists()
{
    // Arrange: Use in-memory database for testing
    var options = new DbContextOptionsBuilder<AppDbContext>()
        .UseInMemoryDatabase(databaseName: "TestDb")
        .Options;
    
    using var context = new AppDbContext(options);
    var product = new Product { Id = Guid.NewGuid(), Name = "Test Product" };
    context.Products.Add(product);
    await context.SaveChangesAsync();
    
    var logger = new Mock<ILogger<ProductRepository>>();
    var repository = new ProductRepository(context, logger.Object);
    
    // Act
    var result = await repository.GetByIdAsync(product.Id);
    
    // Assert
    Assert.NotNull(result);
    Assert.Equal(product.Id, result.Id);
    Assert.Equal("Test Product", result.Name);
}
```

**Key Points**:
- ✅ Uses in-memory database (fast, no SQL Server needed)
- ✅ Tests actual database queries
- ✅ Isolated from other tests

---

## Real-World Example: Stock Reservation

Let's examine a complex operation that demonstrates the repository pattern's power: **stock reservation**.

### The Requirement

When a customer places an order, we need to:
1. Reserve stock (decrease available quantity)
2. Ensure atomicity (all-or-nothing)
3. Handle concurrent requests
4. Rollback on failure

### Traditional Approach (Problems)

```csharp
// ❌ Problems with this approach:
[HttpPost("{id}/reserve")]
public async Task<IActionResult> Reserve(Guid id, int quantity)
{
    // Transaction logic in controller
    using var tx = await _db.Database.BeginTransactionAsync();
    
    try
    {
        // Business logic mixed with data access
        var product = await _db.Products.FindAsync(id);
        if (product == null)
            return NotFound();
            
        if (product.Stock < quantity)
            return Conflict("Insufficient stock");
            
        // Database update
        product.Stock -= quantity;
        await _db.SaveChangesAsync();
        await tx.CommitAsync();
        
        return Ok(new { remaining = product.Stock });
    }
    catch
    {
        await tx.RollbackAsync();
        throw;
    }
}
```

**Problems**:
- Transaction logic in controller
- Business logic mixed with data access
- Hard to test
- Can't reuse this logic elsewhere

### Repository Pattern Approach (Solution)

**Repository** (handles transaction):
```csharp
// ProductRepository.ReserveAsync()
public async Task<int> ReserveAsync(Guid id, int quantity)
{
    if (quantity <= 0)
        throw new ArgumentException("Quantity must be > 0", nameof(quantity));

    // Transaction is a data access concern - belongs in repository
    using var tx = await _db.Database.BeginTransactionAsync();
    try
    {
        var product = await _db.Products.FirstOrDefaultAsync(p => p.Id == id);
        if (product == null)
            throw new KeyNotFoundException("Product not found");

        if (product.Stock < quantity)
            throw new InvalidOperationException("Insufficient stock");

        product.Stock -= quantity;
        await _db.SaveChangesAsync();
        await tx.CommitAsync();

        _logger.LogInformation("Reserved {Quantity} units. New stock: {Stock}", 
            quantity, product.Stock);
        
        return product.Stock;
    }
    catch
    {
        await tx.RollbackAsync();
        throw;
    }
}
```

**Service** (handles business logic):
```csharp
// ProductServiceImpl.ReserveAsync()
public async Task<int> ReserveAsync(Guid id, int quantity)
{
    _logger.LogInformation("Reserving {Quantity} units of product {ProductId}", 
        quantity, id);
    
    try
    {
        // Business logic: validation, logging, orchestration
        // Delegates transaction to repository
        var newStock = await _repo.ReserveAsync(id, quantity);
        
        _logger.LogInformation("Successfully reserved. New stock: {Stock}", newStock);
        return newStock;
    }
    catch (KeyNotFoundException ex)
    {
        _logger.LogWarning(ex, "Product {ProductId} not found", id);
        throw;
    }
    catch (InvalidOperationException ex)
    {
        _logger.LogWarning(ex, "Insufficient stock for product {ProductId}", id);
        throw;
    }
}
```

**Controller** (handles HTTP):
```csharp
// ProductsController.Reserve()
[HttpPost("{id}/reserve")]
public async Task<IActionResult> Reserve(Guid id, [FromBody] ReleaseDto dto)
{
    if (dto.Quantity <= 0)
        return BadRequest(new { error = "Quantity must be > 0" });

    try
    {
        var remaining = await _service.ReserveAsync(id, dto.Quantity);
        return Ok(new { id, remaining });
    }
    catch (KeyNotFoundException)
    {
        return NotFound();
    }
    catch (InvalidOperationException ex)
    {
        return Conflict(new { error = ex.Message });
    }
}
```

### Why This Is Better

1. **Separation of Concerns**:
   - Transaction logic → Repository
   - Business logic → Service
   - HTTP concerns → Controller

2. **Reusability**:
   ```csharp
   // Can be used by OrderService, PaymentService, etc.
   await _productRepo.ReserveAsync(productId, quantity);
   ```

3. **Testability**:
   ```csharp
   // Easy to test service without database
   var mockRepo = new Mock<IProductRepository>();
   mockRepo.Setup(r => r.ReserveAsync(id, quantity))
       .ReturnsAsync(5);
   
   var service = new ProductServiceImpl(mockRepo.Object, logger);
   var result = await service.ReserveAsync(id, quantity);
   ```

4. **Maintainability**:
   - Transaction logic in one place
   - Easy to modify or debug
   - Clear responsibilities

---

## Common Patterns and Practices

### Pattern 1: Generic Repository (Optional)

Some projects use a generic repository for common operations:

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(Guid id);
    Task<List<T>> GetAllAsync();
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(Guid id);
}

// Then specific repositories extend it
public interface IProductRepository : IRepository<Product>
{
    // Product-specific methods
    Task<List<Product>> GetByPriceRangeAsync(int min, int max);
    Task<int> ReserveAsync(Guid id, int quantity);
}
```

**Note**: Product Service doesn't use this pattern - it uses a specific repository interface, which is often clearer and more explicit.

### Pattern 2: Unit of Work (For Complex Transactions)

When you need transactions across multiple repositories:

```csharp
public interface IUnitOfWork
{
    IProductRepository Products { get; }
    IOrderRepository Orders { get; }
    Task<int> SaveChangesAsync();
    Task BeginTransactionAsync();
    Task CommitTransactionAsync();
}

// Usage
await _unitOfWork.BeginTransactionAsync();
try
{
    await _unitOfWork.Products.ReserveAsync(productId, quantity);
    await _unitOfWork.Orders.CreateAsync(order);
    await _unitOfWork.SaveChangesAsync();
    await _unitOfWork.CommitTransactionAsync();
}
catch
{
    await _unitOfWork.RollbackTransactionAsync();
    throw;
}
```

**Note**: Product Service handles transactions within individual repository methods, which works well for most cases.

### Pattern 3: Specification Pattern (For Complex Queries)

For complex, reusable queries:

```csharp
public interface ISpecification<T>
{
    Expression<Func<T, bool>> Criteria { get; }
    List<Expression<Func<T, object>>> Includes { get; }
}

public class ExpensiveProductsSpecification : ISpecification<Product>
{
    public Expression<Func<Product, bool>> Criteria => p => p.Price > 1000;
    public List<Expression<Func<Product, object>>> Includes => new();
}

// Repository method
public async Task<List<Product>> FindAsync(ISpecification<Product> spec)
{
    var query = _db.Products.Where(spec.Criteria);
    foreach (var include in spec.Includes)
    {
        query = query.Include(include);
    }
    return await query.ToListAsync();
}
```

**Note**: Product Service uses explicit methods for queries, which is simpler and more readable for most cases.

---

## Summary

### What We Learned

1. **The Problem**: Direct database access in controllers creates tight coupling, makes testing difficult, and mixes responsibilities.

2. **The Solution**: Repository pattern introduces an abstraction layer that separates data access from business logic.

3. **The Components**:
   - **Repository Interface**: Defines the contract
   - **Repository Implementation**: Contains database code
   - **Service**: Contains business logic
   - **Controller**: Handles HTTP concerns

4. **The Benefits**:
   - ✅ Separation of concerns
   - ✅ Testability (mock repositories)
   - ✅ Flexibility (swap implementations)
   - ✅ Code reusability
   - ✅ Maintainability

5. **How It Works**: 
   - Dependency Injection wires everything together
   - Each layer depends on interfaces, not implementations
   - Data flows: Controller → Service → Repository → Database

### Key Takeaways

- **Repository Pattern = Abstraction Layer**: Hides database implementation details
- **Interfaces Enable Flexibility**: Can swap implementations without changing business logic
- **Dependency Injection is Essential**: Makes the pattern work by injecting interfaces
- **Testing Becomes Easy**: Mock repositories instead of using real databases
- **Each Layer Has One Job**: Controller (HTTP), Service (Business), Repository (Data)

### The Product Service Example

The Product Service demonstrates the repository pattern perfectly:
- Clear separation of concerns
- Easy to test
- Flexible and maintainable
- Well-structured code

By studying this implementation, you can understand how to apply the repository pattern to any service or application.

---

**Remember**: The repository pattern is about **abstraction** and **separation of concerns**. Keep database code in repositories, business logic in services, and HTTP concerns in controllers. This makes your code more maintainable, testable, and flexible.
