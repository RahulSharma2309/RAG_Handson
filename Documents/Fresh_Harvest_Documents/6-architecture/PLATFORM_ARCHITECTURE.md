# Platform NuGet Architecture - Complete Guide

## 🎯 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Ep.Platform Library                    │
│  (NuGet Package: Ep.Platform v1.0.2)                     │
│                                                            │
│  Exposes:                                                 │
│  - IPasswordHasher (BCrypt abstraction)                  │
│  - IJwtTokenGenerator (JWT abstraction)                  │
│  - AddEpSqlServerDbContext<T>() (EF Core)               │
│  - AddEpJwtAuth() (JWT Authentication)                   │
│  - AddEpSecurityServices() (Password + JWT)              │
│  - AddEpHttpClient() (HttpClient + Polly)                │
│  - AddEpSwaggerWithJwt() (Swagger)                       │
│  - AddEpDefaultCors() (CORS)                             │
│  - EnsureDatabaseAsync<T>() (DB initialization)          │
│                                                            │
│  Owns Infrastructure:                                     │
│  - BCrypt.Net-Next                                        │
│  - Microsoft.EntityFrameworkCore.SqlServer                │
│  - System.IdentityModel.Tokens.Jwt                       │
│  - Microsoft.Extensions.Http.Polly                        │
│  - Swashbuckle.AspNetCore                                │
└──────────────────────────────────────────────────────────┘
                           │
                           │ NuGet Reference
                           │ (No Project Reference!)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   Auth Service (Consumer)                 │
│                                                            │
│  Dependencies:                                            │
│  ✅ PackageReference: Ep.Platform (1.0.2)                │
│  ✅ Microsoft.EntityFrameworkCore.Design (tools only)    │
│  ❌ NO BCrypt                                             │
│  ❌ NO JWT libraries                                      │
│  ❌ NO EF Core SqlServer                                  │
│  ❌ NO Polly                                              │
│  ❌ NO Swashbuckle                                        │
│                                                            │
│  Uses Platform Through:                                   │
│  - IPasswordHasher (injected)                            │
│  - IJwtTokenGenerator (injected)                         │
│  - Extension methods (AddEp...)                          │
└──────────────────────────────────────────────────────────┘
```

## 📦 1. Platform Library (Ep.Platform)

### Purpose
Centralized infrastructure library that ALL services consume via NuGet.

### Package Information
```xml
<PackageId>Ep.Platform</PackageId>
<Version>1.0.2</Version>
<Description>
  Enterprise platform library providing infrastructure abstractions 
  for ASP.NET Core services
</Description>
```

### What It Exposes

#### A. Security Abstractions
```csharp
namespace Ep.Platform.Security;

// Password Hashing
public interface IPasswordHasher
{
    string HashPassword(string password);
    bool VerifyPassword(string password, string hash);
}

// JWT Token Generation
public interface IJwtTokenGenerator
{
    string GenerateToken(Dictionary<string, string> claims, TimeSpan? expires = null);
}
```

#### B. Dependency Injection Extensions
```csharp
namespace Ep.Platform.DependencyInjection;

// Database
public static IServiceCollection AddEpSqlServerDbContext<TContext>(
    this IServiceCollection services,
    IConfiguration configuration,
    string connectionName = "DefaultConnection")

// Security Services
public static IServiceCollection AddEpSecurityServices(
    this IServiceCollection services)

// JWT Authentication
public static IServiceCollection AddEpJwtAuth(
    this IServiceCollection services,
    IConfiguration configuration,
    string sectionName = "Jwt")

// HTTP Client with Polly
public static IHttpClientBuilder AddEpHttpClient(
    this IServiceCollection services,
    string name,
    IConfiguration configuration,
    string? baseAddressKey = null)

// Swagger
public static IServiceCollection AddEpSwaggerWithJwt(
    this IServiceCollection services,
    string title,
    string version = "v1")

// CORS
public static IServiceCollection AddEpDefaultCors(
    this IServiceCollection services,
    string policyName = "AllowLocalhost3000",
    string[]? origins = null)
```

#### C. Hosting Extensions
```csharp
namespace Ep.Platform.Hosting;

public static Task EnsureDatabaseAsync<TContext>(
    this IHost host,
    bool applyMigrations = true,
    CancellationToken cancellationToken = default)
    where TContext : DbContext
```

### Package Dependencies (Owned by Platform)
```xml
<ItemGroup>
  <PackageReference Include="BCrypt.Net-Next" Version="4.0.3" />
  <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
  <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
  <PackageReference Include="Microsoft.Extensions.Http.Polly" Version="8.0.0" />
  <PackageReference Include="Swashbuckle.AspNetCore" Version="7.0.0" />
  <PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="8.0.0" />
</ItemGroup>
```

### Building & Publishing Platform

```bash
# 1. Update version in Ep.Platform.csproj
<Version>1.0.2</Version>

# 2. Build and pack
cd platform/Ep.Platform
dotnet pack -c Release

# 3. Push to GitHub Packages (with GITHUB_TOKEN set)
dotnet nuget push "bin/Release/Ep.Platform.1.0.2.nupkg" \
  --source github \
  --api-key $GITHUB_TOKEN \
  --skip-duplicate

# 4. Or use local source for development
# (Add local source to nuget.config)
```

## 🔧 2. Auth Service (Consumer)

### Project Structure
```
services/auth-service/
├── src/
│   ├── AuthService.Abstraction/     # Domain models/DTOs
│   ├── AuthService.Core/            # Business logic
│   │   └── AuthService.Core.csproj
│   │       └── <PackageReference Include="Ep.Platform" Version="1.0.2" />
│   └── AuthService.API/             # Web API
│       └── AuthService.API.csproj
│           └── <PackageReference Include="Ep.Platform" Version="1.0.2" />
└── nuget.config                     # Package sources configuration
```

### Auth Service Dependencies

**AuthService.Core.csproj**
```xml
<ItemGroup>
  <!-- ONLY Platform NuGet and Abstraction project -->
  <ProjectReference Include="..\AuthService.Abstraction\AuthService.Abstraction.csproj" />
  <PackageReference Include="Ep.Platform" Version="1.0.2" />
</ItemGroup>
```

**AuthService.API.csproj**
```xml
<ItemGroup>
  <!-- Platform NuGet + EF Core Design tools -->
  <PackageReference Include="Ep.Platform" Version="1.0.2" />
  <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.0" />
  <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.22" />
</ItemGroup>
```

### NuGet Configuration

**services/auth-service/nuget.config**
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="github" value="https://nuget.pkg.github.com/RahulSharma2309/index.json" />
    <add key="local" value="../../platform/Ep.Platform/bin/Release" />
  </packageSources>
  <packageSourceCredentials>
    <github>
      <add key="Username" value="RahulSharma2309" />
      <add key="ClearTextPassword" value="%GITHUB_TOKEN%" />
    </github>
  </packageSourceCredentials>
</configuration>
```

### Using Platform in Auth Service

**Startup.cs**
```csharp
using Ep.Platform.DependencyInjection;
using Ep.Platform.Security;

public void ConfigureServices(IServiceCollection services)
{
    // All infrastructure from Platform NuGet
    services.AddEpSqlServerDbContext<AppDbContext>(Configuration);
    services.AddEpJwtAuth(Configuration);
    services.AddEpSecurityServices();  // Registers IPasswordHasher & IJwtTokenGenerator
    services.AddEpHttpClient("user", Configuration, "ServiceUrls:UserService");
    services.AddEpSwaggerWithJwt("Auth Service", "v1");
    services.AddEpDefaultCors();

    // Only auth-specific business logic
    services.AddScoped<IUserRepository, UserRepository>();
    services.AddScoped<IAuthService, AuthService>();
}
```

**AuthService.cs (Business Logic)**
```csharp
using Ep.Platform.Security;

public class AuthService : IAuthService
{
    private readonly IPasswordHasher _passwordHasher;  // From Platform NuGet
    
    public AuthService(
        IUserRepository userRepository,
        IPasswordHasher passwordHasher)  // Injected from Platform
    {
        _userRepository = userRepository;
        _passwordHasher = passwordHasher;
    }

    public async Task<User> RegisterAsync(RegisterDto dto)
    {
        // Use Platform abstraction, no BCrypt knowledge
        var hash = _passwordHasher.HashPassword(dto.Password);
        // ...
    }
}
```

**AuthController.cs**
```csharp
using Ep.Platform.Security;

public class AuthController : ControllerBase
{
    private readonly IJwtTokenGenerator _jwtTokenGenerator;  // From Platform NuGet
    
    public AuthController(IJwtTokenGenerator jwtTokenGenerator)
    {
        _jwtTokenGenerator = jwtTokenGenerator;
    }

    public async Task<IActionResult> Login(LoginDto dto)
    {
        var claims = new Dictionary<string, string>
        {
            [ClaimTypes.NameIdentifier] = user.Id.ToString(),
            [ClaimTypes.Email] = user.Email
        };
        
        // Use Platform abstraction, no JWT library knowledge
        var token = _jwtTokenGenerator.GenerateToken(claims);
        return Ok(new { token });
    }
}
```

## 🚀 3. Workflow

### Development Workflow

```bash
# 1. Update Platform library
cd platform/Ep.Platform
# ... make changes ...
dotnet pack -c Release

# 2. Update Auth Service to use new version
cd services/auth-service
# Update version in .csproj files
dotnet restore
dotnet build

# 3. When ready, publish Platform to GitHub Packages
cd platform/Ep.Platform
dotnet nuget push "bin/Release/Ep.Platform.1.0.2.nupkg" \
  --source github \
  --api-key $GITHUB_TOKEN
```

### Production Workflow

```bash
# Auth Service pulls Platform from GitHub Packages
cd services/auth-service
dotnet restore  # Gets Ep.Platform from GitHub Packages
dotnet build
dotnet run --project src/AuthService.API
```

## ✅ Benefits

### 1. **True Abstraction**
- Auth Service has ZERO direct infrastructure dependencies
- Only knows Platform interfaces

### 2. **NuGet Versioning**
- Platform versioned independently (1.0.2, 1.0.3, etc.)
- Auth Service pins specific Platform version
- Easy rollback if needed

### 3. **Centralized Updates**
- Update BCrypt? Change only Platform
- Update EF Core? Change only Platform
- All services get updates via NuGet upgrade

### 4. **Reusability**
- User Service, Product Service, etc. all use same Platform NuGet
- Consistent infrastructure across all services

### 5. **Testing**
- Mock `IPasswordHasher`, `IJwtTokenGenerator` in unit tests
- No need to mock BCrypt or JWT libraries

### 6. **Clear Boundaries**
```
Platform (NuGet)     →  Infrastructure concerns
Auth Service (App)   →  Business logic only
```

## 📊 Comparison

| Aspect | Before (Project Reference) | After (NuGet Package) |
|--------|---------------------------|----------------------|
| Coupling | Tight (source code) | Loose (versioned package) |
| Deployment | Must build Platform with service | Platform pre-built |
| Versioning | Git commits | Semantic versioning |
| Distribution | Source code | Binary package |
| Updates | Rebuild everything | Update package version |
| CI/CD | Build Platform + Service | Restore + Build Service only |

## 🎉 Summary

**End Goal Achieved:**
1. ✅ Perfect Platform library with all infrastructure
2. ✅ Platform exposed as NuGet package (Ep.Platform v1.0.2)
3. ✅ Auth Service uses Platform ONLY through NuGet
4. ✅ Zero direct infrastructure dependencies in Auth Service
5. ✅ Clean separation of concerns
6. ✅ Reusable across all services

**Auth Service now:**
- Imports `Ep.Platform` NuGet package
- Uses `IPasswordHasher` and `IJwtTokenGenerator` interfaces
- Calls `AddEp...()` extension methods
- Has NO knowledge of BCrypt, JWT, EF Core implementations
- Pure business logic focused on authentication

