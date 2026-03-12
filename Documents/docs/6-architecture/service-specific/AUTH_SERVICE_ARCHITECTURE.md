# Auth Service - Platform-First Architecture

## 🎯 Architecture Philosophy

The Auth Service follows a **Platform-First** approach where:
- ✅ **Platform Layer** owns all infrastructure concerns (EF Core, JWT, BCrypt, HttpClient, etc.)
- ✅ **Auth Service** only talks to Platform abstractions
- ✅ **No direct infrastructure dependencies** in business/core layers

## 📦 Dependency Hierarchy

```
┌─────────────────────────────────────────┐
│         AuthService.API                 │
│  (Controllers, Program, Startup)        │
│  - References: Core, Abstraction,       │
│                Platform                  │
└────────────────┬────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼──────────┐  ┌──────▼──────────────┐
│ AuthService.   │  │  AuthService.Core   │
│  Abstraction   │  │  (Business, Repo)   │
│  (Models, DTOs)│  │  - References:      │
│  - No deps     │  │    Abstraction,     │
└────────────────┘  │    Platform ONLY    │
                    └──────┬──────────────┘
                           │
                    ┌──────▼──────────────┐
                    │   Ep.Platform       │
                    │  (Infrastructure)   │
                    │  - EF Core          │
                    │  - JWT              │
                    │  - BCrypt           │
                    │  - HttpClient       │
                    │  - Polly            │
                    └─────────────────────┘
```

## 🔧 What Platform Provides

### 1. Database Access
**Platform Exposes:**
- `AddEpSqlServerDbContext<TContext>()` - EF Core SQL Server setup
- `EnsureDatabaseAsync<TContext>()` - Database creation/migration

**Auth Service Uses:**
- Inherits `DbContext` from Platform's transitive dependency
- Repository pattern uses EF Core types via Platform

### 2. Security - Password Hashing
**Platform Exposes:**
```csharp
public interface IPasswordHasher
{
    string HashPassword(string password);
    bool VerifyPassword(string password, string hash);
}
```

**Auth Service Uses:**
```csharp
public class AuthService : IAuthService
{
    private readonly IPasswordHasher _passwordHasher; // From Platform
    
    public async Task<User> RegisterAsync(RegisterDto dto)
    {
        var hash = _passwordHasher.HashPassword(dto.Password);
        // No direct BCrypt dependency
    }
}
```

### 3. Security - JWT Token Generation
**Platform Exposes:**
```csharp
public interface IJwtTokenGenerator
{
    string GenerateToken(Dictionary<string, string> claims, TimeSpan? expires = null);
}
```

**Auth Service Uses:**
```csharp
public class AuthController : ControllerBase
{
    private readonly IJwtTokenGenerator _jwtTokenGenerator; // From Platform
    
    public async Task<IActionResult> Login(LoginDto dto)
    {
        var claims = new Dictionary<string, string>
        {
            [ClaimTypes.NameIdentifier] = user.Id.ToString(),
            [ClaimTypes.Email] = user.Email
        };
        var token = _jwtTokenGenerator.GenerateToken(claims);
        // No direct JWT library dependency
    }
}
```

### 4. JWT Authentication
**Platform Exposes:**
- `AddEpJwtAuth(IConfiguration)` - Configures JWT Bearer authentication
- Reads from `Jwt` configuration section

**Auth Service Uses:**
- Just calls `services.AddEpJwtAuth(Configuration)`
- No manual JWT configuration

### 5. HTTP Client with Resilience
**Platform Exposes:**
- `AddEpHttpClient(name, IConfiguration, key)` - HttpClient with Polly retry policies

**Auth Service Uses:**
```csharp
services.AddEpHttpClient("user", Configuration, "ServiceUrls:UserService");
// Platform handles HttpClient factory + Polly automatically
```

### 6. Swagger with JWT
**Platform Exposes:**
- `AddEpSwaggerWithJwt(title, version)` - Swagger with JWT bearer UI

**Auth Service Uses:**
- Single line: `services.AddEpSwaggerWithJwt("Auth Service", "v1")`

### 7. CORS
**Platform Exposes:**
- `AddEpDefaultCors(policyName, origins[])` - CORS for SPA development

**Auth Service Uses:**
- `services.AddEpDefaultCors("AllowLocalhost3000", new[] { "http://localhost:3000" })`

## 📋 Core Layer Dependencies

**Before (❌ Wrong):**
```xml
<ItemGroup>
  <PackageReference Include="BCrypt.Net-Next" Version="4.0.3" />
  <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
  <PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="8.0.0" />
</ItemGroup>
```

**After (✅ Correct):**
```xml
<ItemGroup>
  <!-- Core only references Platform for infrastructure abstractions -->
  <ProjectReference Include="..\AuthService.Abstraction\AuthService.Abstraction.csproj" />
  <ProjectReference Include="..\..\..\..\platform\Ep.Platform\Ep.Platform.csproj" />
</ItemGroup>
```

## 🎯 Benefits

1. ✅ **Loose Coupling**: Auth Service doesn't know about EF Core, BCrypt, or JWT implementations
2. ✅ **Easy Testing**: Mock `IPasswordHasher` and `IJwtTokenGenerator` in unit tests
3. ✅ **Consistent Infrastructure**: All services use the same Platform configurations
4. ✅ **Easy Updates**: Update infrastructure libraries only in Platform
5. ✅ **Reusability**: Other services can use the same Platform abstractions
6. ✅ **Clean Architecture**: Business logic is pure, no infrastructure leakage

## 🔄 Service Registration Pattern

**Startup.cs:**
```csharp
public void ConfigureServices(IServiceCollection services)
{
    // Platform handles ALL infrastructure
    services.AddEpSqlServerDbContext<AppDbContext>(Configuration);
    services.AddEpJwtAuth(Configuration);
    services.AddEpSecurityServices();  // Password + JWT generation
    services.AddEpHttpClient("user", Configuration, "ServiceUrls:UserService");
    services.AddEpSwaggerWithJwt("Auth Service", "v1");
    services.AddEpDefaultCors("AllowLocalhost3000", new[] { "http://localhost:3000" });

    // Auth Service only registers its own business logic
    services.AddScoped<IUserRepository, UserRepository>();
    services.AddScoped<IAuthService, AuthService>();
}
```

## 📊 Summary

| Concern | Owned By | Auth Service Dependency |
|---------|----------|-------------------------|
| Database (EF Core) | Platform | `AddEpSqlServerDbContext<T>()` |
| Password Hashing | Platform | `IPasswordHasher` |
| JWT Generation | Platform | `IJwtTokenGenerator` |
| JWT Authentication | Platform | `AddEpJwtAuth()` |
| HTTP Client | Platform | `AddEpHttpClient()` |
| Swagger | Platform | `AddEpSwaggerWithJwt()` |
| CORS | Platform | `AddEpDefaultCors()` |
| Business Logic | Auth Service | Direct implementation |
| Domain Models | Auth Service | Direct implementation |

**Result**: Auth Service is a thin layer of business logic that leverages Platform for ALL infrastructure concerns! 🚀

