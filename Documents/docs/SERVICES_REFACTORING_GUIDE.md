# 🏗️ Services N-Tier Refactoring Guide

> **Complete guide for refactoring all remaining services to N-tier architecture with Platform integration**
>
> **Pattern established by:** User Service refactoring
>
> **Status:** User Service ✅ Complete | Payment, Product, Order ⏳ Pending

---

## 📋 Overview

This guide shows how to refactor each service to follow the same clean N-tier architecture used in Auth Service and User Service.

### Architecture Pattern

```
src/
├── {Service}.Abstraction/    ← Models, DTOs (no dependencies)
├── {Service}.Core/            ← Business logic, Repository (Platform dependency)
└── {Service}.API/             ← Controllers, Startup (Platform dependency)
```

---

## ✅ User Service (Reference Implementation)

**Status:** Complete  
**Location:** `services/user-service/src/`

### Structure Created

```
user-service/src/
├── UserService.Abstraction/
│   ├── Models/
│   │   └── UserProfile.cs
│   └── DTOs/
│       ├── CreateUserDto.cs
│       ├── UserProfileDto.cs
│       ├── WalletOperationDto.cs
│       └── AddBalanceDto.cs
│
├── UserService.Core/
│   ├── Data/
│   │   └── AppDbContext.cs
│   ├── Repository/
│   │   ├── IUserRepository.cs
│   │   └── UserRepository.cs
│   └── Business/
│       ├── IUserService.cs
│       └── UserServiceImpl.cs
│
└── UserService.API/
    ├── Controllers/
    │   ├── UsersController.cs
    │   └── HealthController.cs
    ├── Startup.cs
    ├── Program.cs
    └── appsettings.json
```

### Platform Integration

**Startup.cs** uses:
- `AddEpSqlServerDbContext<AppDbContext>` - Database
- `AddEpSwaggerWithJwt` - Swagger
- `AddEpDefaultCors` - CORS

**No direct dependencies** on:
- ❌ Entity Framework Core packages
- ❌ Swashbuckle packages
- ❌ JWT packages
- ✅ Only `Ep.Platform` NuGet

---

## 🔄 Refactoring Steps (Apply to Each Service)

### Step 1: Create Project Structure

```bash
cd services/{service-name}
mkdir src
cd src
mkdir {Service}.Abstraction
mkdir {Service}.Core
mkdir {Service}.API

# Create projects
cd {Service}.Abstraction
dotnet new classlib

cd ../{Service}.Core
dotnet new classlib

cd ../{Service}.API
dotnet new webapi

# Remove default files
Remove-Item {Service}.Abstraction\Class1.cs
Remove-Item {Service}.Core\Class1.cs
Remove-Item {Service}.API\WeatherForecast.cs
Remove-Item {Service}.API\Controllers\WeatherForecastController.cs
```

### Step 2: Set Target Framework (All 3 projects)

**Update `.csproj` files to:**
```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <ImplicitUsings>enable</ImplicitUsings>
  <Nullable>enable</Nullable>
</PropertyGroup>
```

### Step 3: Add Project References

```bash
# Core references Abstraction
cd {Service}.Core
dotnet add reference ../{Service}.Abstraction/{Service}.Abstraction.csproj

# API references both
cd ../{Service}.API
dotnet add reference ../{Service}.Core/{Service}.Core.csproj
dotnet add reference ../{Service}.Abstraction/{Service}.Abstraction.csproj
```

### Step 4: Add Platform NuGet Package

```bash
# Add to Core
cd {Service}.Core
dotnet add package Ep.Platform --version 1.0.2

# Add to API
cd ../{Service}.API
dotnet add package Ep.Platform --version 1.0.2
dotnet add package Microsoft.EntityFrameworkCore.Design --version 8.0.0
```

### Step 5: Move Existing Code

#### Abstraction Layer
- Move `Models/` → `{Service}.Abstraction/Models/`
- Move `Dtos/` → `{Service}.Abstraction/DTOs/`
- **Update namespaces** to `{Service}.Abstraction.Models` and `{Service}.Abstraction.DTOs`

#### Core Layer
- Move `Data/` → `{Service}.Core/Data/`
- Move `Repositories/` → `{Service}.Core/Repository/`
- Move `Services/` → `{Service}.Core/Business/`
- **Update namespaces** to `{Service}.Core.*`
- **Update using statements** to reference `{Service}.Abstraction.*`

#### API Layer
- Move `Controllers/` → `{Service}.API/Controllers/`
- Create `Startup.cs` (see template below)
- Create `Program.cs` (see template below)
- Copy `appsettings.json`
- **Update namespaces** to `{Service}.API.*`
- **Update using statements** to reference `{Service}.Core.*` and `{Service}.Abstraction.*`

### Step 6: Create Startup.cs (Template)

```csharp
using Ep.Platform.DependencyInjection;
using Ep.Platform.Hosting;
using {Service}.Core.Business;
using {Service}.Core.Data;
using {Service}.Core.Repository;

namespace {Service}.API;

public class Startup
{
    private readonly IConfiguration _config;
    public Startup(IConfiguration config) => _config = config;

    public void ConfigureServices(IServiceCollection services)
    {
        services.AddControllers();
        services.AddEndpointsApiExplorer();

        // Platform extensions for infrastructure
        services.AddEpSwaggerWithJwt("{Service Name}", "v1");
        services.AddEpDefaultCors("AllowLocalhost3000", new[] { "http://localhost:3000" });
        services.AddEpSqlServerDbContext<AppDbContext>(_config);

        // Service-specific HttpClients (if needed)
        // services.AddEpHttpClient("user", _config, "ServiceUrls:UserService");
        // services.AddEpHttpClient("payment", _config, "ServiceUrls:PaymentService");

        // Register business and repository services
        services.AddScoped<I{Service}Repository, {Service}Repository>();
        services.AddScoped<I{Service}Service, {Service}ServiceImpl>();
    }

    public void Configure(WebApplication app, IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
        {
            app.UseDeveloperExceptionPage();
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseRouting();
        app.UseCors("AllowLocalhost3000");
        app.UseAuthorization();
        app.MapControllers();
    }
}
```

### Step 7: Create Program.cs (Template)

```csharp
using {Service}.API;

var builder = WebApplication.CreateBuilder(args);
var startup = new Startup(builder.Configuration);
startup.ConfigureServices(builder.Services);

var app = builder.Build();
startup.Configure(app, app.Environment);

app.Run();
```

### Step 8: Update Dockerfile

Create `src/Dockerfile`:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project files
COPY ["{Service}.API/{Service}.API.csproj", "{Service}.API/"]
COPY ["{Service}.Core/{Service}.Core.csproj", "{Service}.Core/"]
COPY ["{Service}.Abstraction/{Service}.Abstraction.csproj", "{Service}.Abstraction/"]

# Copy nuget.config for Platform package
COPY ["../../nuget.config", "./"]

# Restore
RUN dotnet restore "{Service}.API/{Service}.API.csproj"

# Copy everything
COPY . .

# Build and publish
WORKDIR "/src/{Service}.API"
RUN dotnet publish -c Release -o /app

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .

# Health check tools
RUN apt-get update && apt-get install -y curl netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV APP_DLL={Service}.API.dll
ENV ASPNETCORE_URLS=http://+:80
ENV ConnectionStrings__DefaultConnection="Server=mssql,1433;Database={servicedb};User Id=sa;Password=Your_password123;TrustServerCertificate=True;"

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
```

### Step 9: Update .csproj Files

**{Service}.API.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Ep.Platform" Version="1.0.2" />
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.22" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
    </PackageReference>
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\\{Service}.Core\\{Service}.Core.csproj" />
    <ProjectReference Include="..\\{Service}.Abstraction\\{Service}.Abstraction.csproj" />
  </ItemGroup>
</Project>
```

**{Service}.Core.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Ep.Platform" Version="1.0.2" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\\{Service}.Abstraction\\{Service}.Abstraction.csproj" />
  </ItemGroup>
</Project>
```

**{Service}.Abstraction.csproj:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

### Step 10: Build & Test

```bash
cd {Service}.API
dotnet build
dotnet run
```

Visit: `http://localhost:{port}/swagger`

---

## 📊 Service-Specific Details

### 2️⃣ Payment Service

**Database:** paymentdb  
**Port:** 5003  
**Key Models:**
- `PaymentTransaction`

**Key DTOs:**
- `ProcessPaymentDto`
- `RefundPaymentDto`
- `PaymentResponseDto`

**Special Notes:**
- Uses `IHttpClientFactory` for User Service calls
- Records all transactions in paymentdb
- Handles wallet debit/credit via User Service

**HttpClients needed:**
```csharp
services.AddEpHttpClient("user", _config, "ServiceUrls:UserService");
```

---

### 3️⃣ Product Service

**Database:** productdb  
**Port:** 5002  
**Key Models:**
- `Product`

**Key DTOs:**
- `ProductDto`
- `CreateProductDto`
- `ReserveStockDto`

**Special Notes:**
- Stock reservation logic
- Concurrent reservation handling

**HttpClients needed:** None

---

### 4️⃣ Order Service

**Database:** orderdb  
**Port:** 5004  
**Key Models:**
- `Order`
- `OrderItem`

**Key DTOs:**
- `CreateOrderDto`
- `OrderDto`
- `OrderItemDto`

**Special Notes:**
- Orchestrates: User, Product, Payment services
- Complex service-to-service calls
- Compensation logic (refunds on failure)

**HttpClients needed:**
```csharp
services.AddEpHttpClient("user", _config, "ServiceUrls:UserService");
services.AddEpHttpClient("product", _config, "ServiceUrls:ProductService");
services.AddEpHttpClient("payment", _config, "ServiceUrls:PaymentService");
```

---

## ✅ Verification Checklist (Per Service)

### Build & Structure
- [ ] All 3 projects target net8.0
- [ ] All projects build without errors
- [ ] No direct infrastructure packages in Core (only Platform)
- [ ] API has Platform + EF Design only

### Code Quality
- [ ] All namespaces updated to new structure
- [ ] All using statements reference correct layers
- [ ] Controllers use `{Service}.Abstraction.DTOs`
- [ ] Business layer uses `{Service}.Core.Business`
- [ ] Repository uses `{Service}.Core.Repository`

### Platform Integration
- [ ] Startup uses `AddEpSqlServerDbContext`
- [ ] Startup uses `AddEpSwaggerWithJwt`
- [ ] Startup uses `AddEpDefaultCors`
- [ ] HttpClients use `AddEpHttpClient` (if needed)

### Docker
- [ ] Dockerfile in `src/` folder
- [ ] ENV APP_DLL points to `{Service}.API.dll`
- [ ] entrypoint.sh copied to src/
- [ ] Builds successfully with Docker

---

## 🔄 Docker Compose Updates

After refactoring all services, update `infra/docker-compose.yml`:

### User Service
```yaml
user-service:
  build:
    context: ../services/user-service/src
    dockerfile: Dockerfile
  # ... rest unchanged
```

### Payment Service
```yaml
payment-service:
  build:
    context: ../services/payment-service/src
    dockerfile: Dockerfile
  # ... rest unchanged
```

### Product Service
```yaml
product-service:
  build:
    context: ../services/product-service/src
    dockerfile: Dockerfile
  # ... rest unchanged
```

### Order Service
```yaml
order-service:
  build:
    context: ../services/order-service/src
    dockerfile: Dockerfile
  # ... rest unchanged
```

---

## 🎯 Benefits Achieved

### Before Refactoring
- ❌ Flat structure (all files in one project)
- ❌ Direct infrastructure dependencies
- ❌ Inconsistent between services
- ❌ Hard to test business logic
- ❌ Platform not utilized

### After Refactoring
- ✅ Clean N-tier architecture
- ✅ Zero infrastructure dependencies in Core
- ✅ Consistent across all services
- ✅ Business logic easily testable
- ✅ Platform handles all infrastructure
- ✅ Auth Service pattern followed everywhere

---

## 📝 Notes

1. **Namespace Convention:**
   - Abstraction: `{Service}.Abstraction.{Models|DTOs}`
   - Core: `{Service}.Core.{Business|Repository|Data}`
   - API: `{Service}.API.{Controllers}`

2. **Platform Version:**
   - Always use `Ep.Platform 1.0.2`
   - Managed via `nuget.config` in root

3. **Testing:**
   - Run each service individually first
   - Then test via Docker
   - Finally test end-to-end flows

4. **Migrations:**
   - Run from API project: `dotnet ef migrations add ...`
   - Migrations stored in Core/Data/Migrations

---

## 🚀 Quick Command Reference

```bash
# Create structure
mkdir src && cd src
mkdir {Service}.Abstraction {Service}.Core {Service}.API

# Create projects
dotnet new classlib -n {Service}.Abstraction
dotnet new classlib -n {Service}.Core
dotnet new webapi -n {Service}.API

# Add references
cd {Service}.Core && dotnet add reference ../{Service}.Abstraction
cd {Service}.API && dotnet add reference ../{Service}.Core ../{Service}.Abstraction

# Add Platform
cd {Service}.Core && dotnet add package Ep.Platform --version 1.0.2
cd {Service}.API && dotnet add package Ep.Platform --version 1.0.2

# Build
cd {Service}.API && dotnet build

# Run
dotnet run
```

---

**Status:** Guide Complete ✅  
**Next:** Apply to Payment, Product, Order services  
**Expected Time:** 1-2 hours per service following this guide




