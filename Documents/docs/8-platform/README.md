# 🏗️ Ep.Platform - Infrastructure Library

> **Centralized infrastructure abstractions for all microservices**

---

## 📋 Overview

**Ep.Platform** is a private NuGet package that provides infrastructure abstractions and common functionality for all microservices in this project.

**Package Information:**
- **Name:** Ep.Platform
- **Version:** 1.0.2
- **Type:** Private NuGet (GitHub Packages)
- **Purpose:** Eliminate infrastructure duplication across services

---

## 📚 Documents in This Section

### 1. [Platform Guide](PLATFORM_GUIDE.md)
**Purpose:** How to use Ep.Platform in your services  
**Content:**
- Installation and setup
- Available extensions
- Usage examples
- Configuration

**When to Read:** Using Platform in a service

---

### 2. [Platform Architecture](../6-architecture/PLATFORM_ARCHITECTURE.md)
**Purpose:** Design philosophy and internal architecture  
**Content:**
- Why Platform exists
- What it provides vs what services own
- NuGet package design
- Dependency hierarchy

**When to Read:** Understanding Platform design

---

## 🎯 What Platform Provides

### 1. Security Abstractions
```csharp
using Ep.Platform.Security;

// Password hashing (no direct BCrypt dependency)
public interface IPasswordHasher
{
    string HashPassword(string password);
    bool VerifyPassword(string password, string hash);
}

// JWT token generation (no direct JWT library dependency)
public interface IJwtTokenGenerator
{
    string GenerateToken(Dictionary<string, string> claims, TimeSpan? expires = null);
}
```

### 2. Database Extensions
```csharp
using Ep.Platform.DependencyInjection;

// SQL Server DbContext setup (no direct EF Core dependency)
services.AddEpSqlServerDbContext<AppDbContext>(Configuration);
```

### 3. Authentication Extensions
```csharp
// JWT Bearer authentication (no direct JWT bearer dependency)
services.AddEpJwtAuth(Configuration);

// Security services (Password + JWT)
services.AddEpSecurityServices();
```

### 4. HTTP Client Extensions
```csharp
// HttpClient with Polly resilience (no direct Polly dependency)
services.AddEpHttpClient("user", Configuration, "ServiceUrls:UserService");
```

### 5. Swagger Extensions
```csharp
// Swagger with JWT UI (no direct Swashbuckle dependency)
services.AddEpSwaggerWithJwt("Auth Service", "v1");
```

### 6. CORS Extensions
```csharp
// CORS for SPA (standardized)
services.AddEpDefaultCors("AllowLocalhost3000", new[] { "http://localhost:3000" });
```

### 7. Hosting Extensions
```csharp
using Ep.Platform.Hosting;

// Database initialization
await app.EnsureDatabaseAsync<AppDbContext>(applyMigrations: false);
```

---

## 📦 Platform Dependencies (Owned by Platform)

Platform encapsulates these libraries so services don't need them:

- ✅ BCrypt.Net-Next (4.0.3)
- ✅ Microsoft.EntityFrameworkCore.SqlServer (8.0.0)
- ✅ Microsoft.AspNetCore.Authentication.JwtBearer (8.0.0)
- ✅ System.IdentityModel.Tokens.Jwt (8.0.0)
- ✅ Microsoft.Extensions.Http.Polly (8.0.0)
- ✅ Swashbuckle.AspNetCore (7.0.0)

**Result:** Services have ZERO direct infrastructure dependencies!

---

## 🚀 Quick Start

### 1. Add Platform to Your Service

```xml
<!-- YourService.csproj -->
<ItemGroup>
  <PackageReference Include="Ep.Platform" Version="1.0.2" />
</ItemGroup>
```

### 2. Configure in Startup.cs

```csharp
using Ep.Platform.DependencyInjection;

public void ConfigureServices(IServiceCollection services)
{
    // All infrastructure from Platform
    services.AddEpSqlServerDbContext<YourDbContext>(Configuration);
    services.AddEpJwtAuth(Configuration);
    services.AddEpSecurityServices();
    services.AddEpHttpClient("other-service", Configuration, "ServiceUrls:OtherService");
    services.AddEpSwaggerWithJwt("Your Service", "v1");
    services.AddEpDefaultCors();

    // Only register your business logic
    services.AddScoped<IYourRepository, YourRepository>();
    services.AddScoped<IYourService, YourService>();
}
```

### 3. Use Platform Abstractions

```csharp
using Ep.Platform.Security;

public class YourService
{
    private readonly IPasswordHasher _passwordHasher;  // From Platform
    private readonly IJwtTokenGenerator _jwtGenerator;  // From Platform
    
    public YourService(IPasswordHasher passwordHasher, IJwtTokenGenerator jwtGenerator)
    {
        _passwordHasher = passwordHasher;
        _jwtGenerator = jwtGenerator;
    }
    
    public async Task<User> Register(string email, string password)
    {
        // Use Platform abstractions - no BCrypt/JWT knowledge
        var hash = _passwordHasher.HashPassword(password);
        // ...
    }
}
```

---

## 📖 Further Reading

- **Architecture Details:** [`../6-architecture/PLATFORM_ARCHITECTURE.md`](../6-architecture/PLATFORM_ARCHITECTURE.md)
- **Example Service:** [`../7-services/AUTH_SERVICE.md`](../7-services/AUTH_SERVICE.md)
- **N-Tier Usage:** [`../6-architecture/service-specific/AUTH_SERVICE_ARCHITECTURE.md`](../6-architecture/service-specific/AUTH_SERVICE_ARCHITECTURE.md)

---

**Back to:** [Documentation Index](../DOCUMENTATION_INDEX.md) | [START HERE](../START_HERE.md)


















