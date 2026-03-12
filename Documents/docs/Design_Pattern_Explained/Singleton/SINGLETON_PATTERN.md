# Understanding the Singleton Pattern

## Table of Contents

1. [Introduction](#introduction)
2. [The Problem It Solves](#the-problem-it-solves)
3. [Classic Singleton Implementation](#classic-singleton-implementation)
4. [Thread-Safe Singleton](#thread-safe-singleton)
5. [Problems with Classic Singleton](#problems-with-classic-singleton)
6. [Static Class vs Singleton Pattern](#static-class-vs-singleton-pattern)
7. [Modern Approach: Dependency Injection](#modern-approach-dependency-injection)
8. [Singleton in FreshHarvest Market](#singleton-in-freshharvest-market)
9. [When to Use Singleton](#when-to-use-singleton)
10. [Summary](#summary)

---

## Introduction

The **Singleton Pattern** ensures that a class has only one instance and provides a global point of access to that instance.

**In simple terms**: No matter how many times you try to create an object of a singleton class, you always get the same instance.

### Real-World Analogy

Think of a **company's CEO**:
- There's only one CEO at a time
- Everyone in the company refers to the same person
- You can't create multiple CEOs
- The CEO is accessible from anywhere in the company

---

## The Problem It Solves

### Scenario: Configuration Manager

Imagine you have a `ConfigurationManager` class that reads settings from a file:

```csharp
// ❌ PROBLEM: Multiple instances waste resources
public class ConfigurationManager
{
    private Dictionary<string, string> _settings;
    
    public ConfigurationManager()
    {
        // Expensive operation: reading from file
        _settings = LoadSettingsFromFile();
    }
    
    public string GetSetting(string key)
    {
        return _settings[key];
    }
}

// Usage
var config1 = new ConfigurationManager();  // Reads file
var config2 = new ConfigurationManager();  // Reads file again!
var config3 = new ConfigurationManager();  // Reads file again!
```

**Problems**:
- ❌ Multiple instances read the file multiple times (wasteful)
- ❌ Memory waste (multiple copies of the same data)
- ❌ Inconsistency (if file changes, different instances have different data)

### Solution: Singleton Pattern

```csharp
// ✅ SOLUTION: Only one instance exists
public class ConfigurationManager
{
    private static ConfigurationManager? _instance;
    private Dictionary<string, string> _settings;
    
    // Private constructor prevents external instantiation
    private ConfigurationManager()
    {
        _settings = LoadSettingsFromFile();  // Only called once
    }
    
    // Global access point
    public static ConfigurationManager GetInstance()
    {
        if (_instance == null)
        {
            _instance = new ConfigurationManager();
        }
        return _instance;
    }
    
    public string GetSetting(string key)
    {
        return _settings[key];
    }
}

// Usage
var config1 = ConfigurationManager.GetInstance();  // Creates instance
var config2 = ConfigurationManager.GetInstance();  // Returns same instance
var config3 = ConfigurationManager.GetInstance();  // Returns same instance

// All three variables point to the SAME object
Console.WriteLine(ReferenceEquals(config1, config2));  // True
Console.WriteLine(ReferenceEquals(config2, config3));  // True
```

**Benefits**:
- ✅ Only one instance exists
- ✅ File is read only once
- ✅ Memory efficient
- ✅ Consistent data across the application

---

## Classic Singleton Implementation

### Basic Singleton (Not Thread-Safe)

```csharp
public class Singleton
{
    // Static field to hold the single instance
    private static Singleton? _instance;
    
    // Private constructor prevents external instantiation
    private Singleton()
    {
        // Initialization code
    }
    
    // Public static method to get the instance
    public static Singleton GetInstance()
    {
        // Lazy initialization: create only when first requested
        if (_instance == null)
        {
            _instance = new Singleton();
        }
        return _instance;
    }
    
    // Instance methods
    public void DoSomething()
    {
        Console.WriteLine("Doing something...");
    }
}

// Usage
var instance1 = Singleton.GetInstance();
var instance2 = Singleton.GetInstance();

Console.WriteLine(instance1 == instance2);  // True - same instance
```

**Key Components**:
1. **Private static field** (`_instance`): Holds the single instance
2. **Private constructor**: Prevents `new Singleton()` from outside
3. **Public static method** (`GetInstance()`): Provides access to the instance

---

## Thread-Safe Singleton

The basic implementation above has a problem: **it's not thread-safe**. In multi-threaded environments, multiple threads could create multiple instances.

### Problem: Race Condition

```csharp
// ❌ NOT THREAD-SAFE
public static Singleton GetInstance()
{
    if (_instance == null)  // Thread 1 checks: null
    {
        // Thread 2 also checks: null (before Thread 1 creates)
        _instance = new Singleton();  // Both threads create instances!
    }
    return _instance;
}
```

### Solution 1: Lock-Based (Thread-Safe)

```csharp
public class Singleton
{
    private static Singleton? _instance;
    private static readonly object _lock = new object();
    
    private Singleton() { }
    
    public static Singleton GetInstance()
    {
        // Double-check locking pattern
        if (_instance == null)
        {
            lock (_lock)  // Only one thread can enter at a time
            {
                if (_instance == null)  // Check again after acquiring lock
                {
                    _instance = new Singleton();
                }
            }
        }
        return _instance;
    }
}
```

**How it works**:
1. First check (outside lock): Fast path if instance already exists
2. Lock: Only one thread can enter the critical section
3. Second check (inside lock): Ensure instance wasn't created by another thread
4. Create instance: Only if still null

### Solution 2: Lazy<T> (Recommended for .NET)

```csharp
public class Singleton
{
    // Lazy<T> handles thread-safety automatically
    private static readonly Lazy<Singleton> _instance = 
        new Lazy<Singleton>(() => new Singleton());
    
    private Singleton() { }
    
    public static Singleton GetInstance()
    {
        return _instance.Value;  // Thread-safe, lazy initialization
    }
}
```

**Benefits of `Lazy<T>`**:
- ✅ Thread-safe by default
- ✅ Lazy initialization (created only when accessed)
- ✅ Cleaner code
- ✅ Better performance (no locking overhead after first access)

### Solution 3: Static Constructor (Eager Initialization)

```csharp
public class Singleton
{
    // Created immediately when class is first accessed
    private static readonly Singleton _instance = new Singleton();
    
    // Static constructor ensures thread-safety
    static Singleton()
    {
    }
    
    private Singleton() { }
    
    public static Singleton GetInstance()
    {
        return _instance;
    }
}
```

**Characteristics**:
- ✅ Thread-safe (CLR guarantees static constructor runs once)
- ❌ Eager initialization (created even if never used)
- ✅ Simple and performant

---

## Problems with Classic Singleton

While the singleton pattern solves the "one instance" problem, it introduces other issues:

### Problem 1: Global State

```csharp
// ❌ Global state makes testing difficult
public class Logger
{
    private static Logger? _instance;
    
    public static Logger GetInstance()
    {
        if (_instance == null)
            _instance = new Logger();
        return _instance;
    }
    
    public void Log(string message)
    {
        // Writes to file
    }
}

// In tests, you can't easily replace this
public void TestSomething()
{
    // How do you mock Logger? It's a static singleton!
    var service = new MyService();
    service.DoSomething();  // Uses real Logger, writes to real file
}
```

**Issue**: Hard to test because you can't inject a mock.

### Problem 2: Hidden Dependencies

```csharp
// ❌ Hidden dependency - not obvious from class signature
public class OrderService
{
    public void ProcessOrder(Order order)
    {
        // Hidden dependency on Logger singleton
        Logger.GetInstance().Log("Processing order");
        // ...
    }
}

// You can't tell OrderService depends on Logger just by looking at it
```

**Issue**: Dependencies are not explicit, making code harder to understand.

### Problem 3: Tight Coupling

```csharp
// ❌ Tightly coupled to specific implementation
public class PaymentService
{
    public void ProcessPayment()
    {
        // Can't swap DatabaseConnection for a test double
        var db = DatabaseConnection.GetInstance();
        // ...
    }
}
```

**Issue**: Can't easily swap implementations for testing or different environments.

### Problem 4: Lifecycle Management

```csharp
// ❌ When does the singleton get disposed?
public class ResourceManager
{
    private static ResourceManager? _instance;
    private FileStream _fileStream;
    
    private ResourceManager()
    {
        _fileStream = new FileStream("data.txt", FileMode.Open);
    }
    
    // When does _fileStream get closed?
    // Application shutdown? Never?
}
```

**Issue**: No clear lifecycle management.

---

## Static Class vs Singleton Pattern

A common question is: **What's the difference between a static class and a singleton pattern?** Both ensure only one instance exists, but they have important differences.

### Static Class

A **static class** is a class that cannot be instantiated and contains only static members.

```csharp
// Static class - cannot be instantiated
public static class MathHelper
{
    // Static methods only
    public static int Add(int a, int b)
    {
        return a + b;
    }
    
    public static int Multiply(int a, int b)
    {
        return a * b;
    }
}

// Usage: Call methods directly on the class
var result = MathHelper.Add(5, 3);  // No instance needed
```

**Characteristics**:
- ✅ Cannot be instantiated (`new MathHelper()` is not allowed)
- ✅ All members must be static
- ✅ Cannot implement interfaces
- ✅ Cannot inherit from other classes (except Object)
- ✅ Loaded into memory when first accessed
- ✅ Lives for entire application lifetime

### Singleton Pattern

A **singleton** is a regular class that can be instantiated, but only once.

```csharp
// Singleton - can be instantiated, but only once
public class Logger
{
    private static Logger? _instance;
    
    private Logger() { }
    
    public static Logger GetInstance()
    {
        if (_instance == null)
            _instance = new Logger();
        return _instance;
    }
    
    // Instance methods
    public void Log(string message)
    {
        Console.WriteLine(message);
    }
}

// Usage: Get instance, then call methods
var logger = Logger.GetInstance();
logger.Log("Hello");  // Instance method
```

**Characteristics**:
- ✅ Can be instantiated (but only once)
- ✅ Can have instance methods and properties
- ✅ Can implement interfaces
- ✅ Can inherit from other classes
- ✅ Created lazily (when first requested)
- ✅ Lives for entire application lifetime

### Key Differences

| Aspect | Static Class | Singleton Pattern |
|--------|-------------|------------------|
| **Instantiation** | ❌ Cannot be instantiated | ✅ Can be instantiated (once) |
| **Methods** | Static methods only | Instance methods (and static) |
| **Interfaces** | ❌ Cannot implement interfaces | ✅ Can implement interfaces |
| **Inheritance** | ❌ Cannot inherit (except Object) | ✅ Can inherit from classes |
| **Polymorphism** | ❌ No polymorphism | ✅ Supports polymorphism |
| **Dependency Injection** | ❌ Cannot be injected | ✅ Can be injected (as interface) |
| **Testing** | ❌ Hard to mock/test | ✅ Easier to mock/test |
| **Memory** | Loaded immediately | Created lazily (on demand) |
| **State** | Static state (shared) | Instance state (but only one instance) |

### Example Comparison

#### Static Class Example

```csharp
// Static class - utility functions
public static class StringHelper
{
    public static string ToUpperCase(string input)
    {
        return input.ToUpper();
    }
    
    public static string Reverse(string input)
    {
        return new string(input.Reverse().ToArray());
    }
}

// Usage
var result = StringHelper.ToUpperCase("hello");  // Direct call
```

**Use Case**: Utility functions, helper methods, stateless operations

#### Singleton Pattern Example

```csharp
// Singleton - stateful service
public class Cache : ICache
{
    private static Cache? _instance;
    private Dictionary<string, object> _data = new();
    
    private Cache() { }
    
    public static Cache GetInstance()
    {
        if (_instance == null)
            _instance = new Cache();
        return _instance;
    }
    
    // Instance methods
    public void Set(string key, object value)
    {
        _data[key] = value;  // Instance state
    }
    
    public object? Get(string key)
    {
        return _data.TryGetValue(key, out var value) ? value : null;
    }
}

// Usage
var cache = Cache.GetInstance();
cache.Set("user", userData);  // Instance method
var user = cache.Get("user");
```

**Use Case**: Stateful services, objects that need to implement interfaces

### When to Use Static Class

Use a **static class** when:

1. **Utility Functions** (stateless operations)
   ```csharp
   public static class MathHelper
   {
       public static double CalculateArea(double radius) { ... }
       public static double CalculateCircumference(double radius) { ... }
   }
   ```

2. **Extension Methods**
   ```csharp
   public static class StringExtensions
   {
       public static bool IsValidEmail(this string email) { ... }
   }
   ```

3. **Constants**
   ```csharp
   public static class Constants
   {
       public const int MaxRetries = 3;
       public const string DefaultConnection = "Server=...";
   }
   ```

4. **No State Needed**
   ```csharp
   public static class Validator
   {
       public static bool IsValid(string input) { ... }  // No state
   }
   ```

### When to Use Singleton Pattern

Use a **singleton** when:

1. **Need to Implement Interfaces**
   ```csharp
   public class Logger : ILogger  // Can implement interface
   {
       private static Logger? _instance;
       // ...
   }
   ```

2. **Need Instance State**
   ```csharp
   public class ConfigurationManager
   {
       private Dictionary<string, string> _settings;  // Instance state
       // ...
   }
   ```

3. **Need Dependency Injection**
   ```csharp
   // Can be injected as interface
   services.AddSingleton<ILogger, Logger>();
   
   public class Service
   {
       public Service(ILogger logger) { ... }  // Injected
   }
   ```

4. **Need Polymorphism**
   ```csharp
   public class FileLogger : ILogger { ... }
   public class DatabaseLogger : ILogger { ... }
   
   // Can swap implementations
   ILogger logger = FileLogger.GetInstance();
   ```

5. **Need Inheritance**
   ```csharp
   public class BaseLogger { ... }
   public class FileLogger : BaseLogger  // Can inherit
   {
       // ...
   }
   ```

### Real-World Example: Logger

#### Static Class Approach (Limited)

```csharp
// ❌ Static class - cannot implement interface
public static class Logger
{
    private static List<string> _logs = new();  // Static state
    
    public static void Log(string message)
    {
        _logs.Add(message);
        Console.WriteLine(message);
    }
    
    public static List<string> GetLogs()
    {
        return _logs;
    }
}

// Problems:
// - Cannot implement ILogger interface
// - Cannot be injected via DI
// - Hard to test (static state)
// - Cannot swap implementations
```

#### Singleton Pattern Approach (Better)

```csharp
// ✅ Singleton - can implement interface
public class Logger : ILogger
{
    private static Logger? _instance;
    private List<string> _logs = new();  // Instance state
    
    private Logger() { }
    
    public static Logger GetInstance()
    {
        if (_instance == null)
            _instance = new Logger();
        return _instance;
    }
    
    public void Log(string message)
    {
        _logs.Add(message);
        Console.WriteLine(message);
    }
    
    public List<string> GetLogs()
    {
        return _logs;
    }
}

// Benefits:
// - Can implement ILogger interface
// - Can be injected via DI
// - Easier to test (can mock ILogger)
// - Can swap implementations (FileLogger, DatabaseLogger, etc.)
```

### Modern Approach: DI Container Singleton

In modern .NET, prefer **DI container singleton** over both static class and classic singleton:

```csharp
// ✅ BEST: DI Container Singleton
public interface ILogger
{
    void Log(string message);
}

public class FileLogger : ILogger
{
    private List<string> _logs = new();
    
    public void Log(string message)
    {
        _logs.Add(message);
        File.AppendAllText("log.txt", message);
    }
}

// Register as singleton
services.AddSingleton<ILogger, FileLogger>();

// Inject and use
public class Service
{
    private readonly ILogger _logger;
    
    public Service(ILogger logger)  // Injected
    {
        _logger = logger;
    }
    
    public void DoWork()
    {
        _logger.Log("Working...");  // Uses singleton instance
    }
}
```

**Why This Is Best**:
- ✅ Implements interface (flexible)
- ✅ Dependency injection (testable)
- ✅ Can swap implementations
- ✅ Explicit dependencies
- ✅ Lifecycle management

### Summary: Static Class vs Singleton

| Requirement | Use Static Class | Use Singleton | Use DI Singleton |
|------------|-----------------|---------------|-----------------|
| **Utility functions** | ✅ Yes | ❌ No | ❌ No |
| **No state** | ✅ Yes | ⚠️ Overkill | ⚠️ Overkill |
| **Need interface** | ❌ No | ✅ Yes | ✅ Yes |
| **Need DI** | ❌ No | ⚠️ Possible | ✅ Yes |
| **Need polymorphism** | ❌ No | ✅ Yes | ✅ Yes |
| **Need inheritance** | ❌ No | ✅ Yes | ✅ Yes |
| **Testability** | ❌ Hard | ⚠️ Moderate | ✅ Easy |
| **Modern .NET** | ⚠️ Limited use | ❌ Avoid | ✅ Recommended |

### Quick Decision Guide

```
Do you need to:
├─ Implement an interface? → Use Singleton or DI Singleton
├─ Use dependency injection? → Use DI Singleton
├─ Have instance state? → Use Singleton or DI Singleton
├─ Support polymorphism? → Use Singleton or DI Singleton
├─ Just utility functions? → Use Static Class
└─ Just constants? → Use Static Class
```

---

## Modern Approach: Dependency Injection

In modern .NET applications, **Dependency Injection (DI) containers** provide a better way to achieve singleton behavior without the problems of the classic pattern.

### How DI Containers Handle Singletons

Instead of using the classic singleton pattern, register services as singletons in the DI container:

```csharp
// In Startup.cs or Program.cs
public void ConfigureServices(IServiceCollection services)
{
    // Register as singleton - container manages the single instance
    services.AddSingleton<ILogger, FileLogger>();
    services.AddSingleton<IConfigurationManager, ConfigurationManager>();
    services.AddSingleton<ICache, MemoryCache>();
}
```

### Benefits Over Classic Singleton

1. **Testable**: Can inject mocks in tests
   ```csharp
   // In tests
   var mockLogger = new Mock<ILogger>();
   var service = new OrderService(mockLogger.Object);  // Inject mock
   ```

2. **Explicit Dependencies**: Dependencies are visible in constructor
   ```csharp
   public class OrderService
   {
       private readonly ILogger _logger;  // Explicit dependency
       
       public OrderService(ILogger logger)  // Injected
       {
           _logger = logger;
       }
   }
   ```

3. **Flexible**: Can swap implementations easily
   ```csharp
   // Development
   services.AddSingleton<ILogger, ConsoleLogger>();
   
   // Production
   services.AddSingleton<ILogger, FileLogger>();
   ```

4. **Lifecycle Management**: Container manages object lifecycle
   ```csharp
   // Container handles disposal automatically
   services.AddSingleton<IDisposableResource, Resource>();
   ```

---

## Singleton in FreshHarvest Market

The FreshHarvest Market codebase uses **DI container singletons** rather than classic singleton pattern. Here are examples:

### Example 1: Security Services

**Location**: `platform/Ep.Platform/DependencyInjection/SecurityExtensions.cs`

```csharp
public static class SecurityExtensions
{
    public static IServiceCollection AddEpSecurityServices(this IServiceCollection services)
    {
        // Registered as singletons - one instance for entire application
        services.AddSingleton<IPasswordHasher, BcryptPasswordHasher>();
        services.AddSingleton<IJwtTokenGenerator, JwtTokenGenerator>();
        
        return services;
    }
}
```

**Why Singleton?**
- `BcryptPasswordHasher`: Stateless, no need for multiple instances
- `JwtTokenGenerator`: Stateless, expensive to create (reads config), safe to share

### Example 2: Usage in Services

**Location**: `services/auth-service/src/AuthService.Core/Business/AuthService.cs`

```csharp
public class AuthService : IAuthService
{
    private readonly IPasswordHasher _passwordHasher;  // Injected singleton
    
    public AuthService(
        IUserRepository userRepository,
        IPasswordHasher passwordHasher,  // DI container provides same instance
        ILogger<AuthService> logger)
    {
        _passwordHasher = passwordHasher;
        // ...
    }
    
    public async Task<User> RegisterAsync(RegisterDto dto)
    {
        // Uses the singleton instance
        var hashedPassword = _passwordHasher.HashPassword(dto.Password);
        // ...
    }
}
```

**How It Works**:
1. `IPasswordHasher` is registered as singleton in DI container
2. Container creates **one instance** of `BcryptPasswordHasher`
3. Every class that needs `IPasswordHasher` gets the **same instance**
4. No need for `GetInstance()` calls - DI handles it

### DI Container Lifetime Options

In .NET DI, there are three lifetime options:

```csharp
// 1. Transient - New instance every time
services.AddTransient<IService, Service>();
// Each request gets a new instance

// 2. Scoped - One instance per HTTP request
services.AddScoped<IService, Service>();
// Same instance within one HTTP request

// 3. Singleton - One instance for entire application
services.AddSingleton<IService, Service>();
// Same instance for entire application lifetime
```

**When to Use Each**:
- **Transient**: Stateless services, lightweight objects
- **Scoped**: Request-specific data (like DbContext)
- **Singleton**: Stateless services, expensive to create, thread-safe objects

---

## When to Use Singleton

### Good Use Cases ✅

1. **Stateless Services**
   ```csharp
   // No internal state, safe to share
   services.AddSingleton<IPasswordHasher, BcryptPasswordHasher>();
   services.AddSingleton<IJwtTokenGenerator, JwtTokenGenerator>();
   ```

2. **Configuration/Settings**
   ```csharp
   // Read once, used everywhere
   services.AddSingleton<IConfiguration>(configuration);
   ```

3. **Caching**
   ```csharp
   // One cache instance for entire application
   services.AddSingleton<IMemoryCache, MemoryCache>();
   ```

4. **Logging**
   ```csharp
   // One logger instance (though usually scoped in modern apps)
   services.AddSingleton<ILogger, FileLogger>();
   ```

5. **Expensive to Create**
   ```csharp
   // Expensive initialization, create once
   services.AddSingleton<IExpensiveService, ExpensiveService>();
   ```

### Bad Use Cases ❌

1. **Stateful Services**
   ```csharp
   // ❌ BAD: Has state, shouldn't be singleton
   public class ShoppingCart
   {
       private List<Item> _items;  // State!
       
       public void AddItem(Item item) { _items.Add(item); }
   }
   // Multiple users would share the same cart!
   ```

2. **Not Thread-Safe**
   ```csharp
   // ❌ BAD: Not thread-safe, can't be singleton
   public class UnsafeCounter
   {
       private int _count;  // Not thread-safe
       
       public void Increment() { _count++; }
   }
   ```

3. **DbContext (Usually)**
   ```csharp
   // ❌ BAD: DbContext should be scoped, not singleton
   services.AddSingleton<AppDbContext>();  // Wrong!
   
   // ✅ GOOD: Scoped per request
   services.AddDbContext<AppDbContext>();  // Creates new instance per request
   ```

---

## Summary

### Key Takeaways

1. **Singleton Pattern**: Ensures only one instance of a class exists
2. **Classic Implementation**: Private constructor + static `GetInstance()` method
3. **Thread-Safety**: Use `Lazy<T>` or double-check locking for thread-safe singletons
4. **Modern Approach**: Use DI container singletons (`AddSingleton`) instead of classic pattern
5. **Benefits of DI Singletons**:
   - ✅ Testable (can inject mocks)
   - ✅ Explicit dependencies
   - ✅ Flexible (can swap implementations)
   - ✅ Lifecycle management

### Comparison

| Aspect | Classic Singleton | DI Container Singleton |
|--------|------------------|----------------------|
| **Access** | `Singleton.GetInstance()` | Injected via constructor |
| **Testability** | ❌ Hard to test | ✅ Easy to test (inject mocks) |
| **Dependencies** | ❌ Hidden | ✅ Explicit |
| **Flexibility** | ❌ Tightly coupled | ✅ Can swap implementations |
| **Thread-Safety** | ⚠️ Must implement | ✅ Handled by container |
| **Lifecycle** | ❌ Manual management | ✅ Automatic management |

### Best Practice

**In modern .NET applications, prefer DI container singletons over the classic singleton pattern.**

```csharp
// ✅ RECOMMENDED: DI Container Singleton
services.AddSingleton<IService, Service>();

// ❌ AVOID: Classic Singleton Pattern
public class Service
{
    private static Service? _instance;
    public static Service GetInstance() { ... }
}
```

**Why?**
- More testable
- Better separation of concerns
- Follows dependency inversion principle
- Easier to maintain and extend

---

**Remember**: The singleton pattern ensures one instance, but in modern .NET, use Dependency Injection containers to achieve this rather than the classic singleton pattern implementation.
