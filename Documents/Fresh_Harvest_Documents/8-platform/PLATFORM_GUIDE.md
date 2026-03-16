# Ep.Platform

Shared infrastructure hooks extracted from the backend services. Focuses only on what is currently used: SQL Server DbContext registration, JWT bearer auth, Swagger with bearer support, typed HttpClients, and a small CORS helper. Also includes a host extension to apply migrations/seed data.

## Provided extensions
- `AddEpSqlServerDbContext<TContext>(config, connectionName = "DefaultConnection")`
- `AddEpJwtAuth(config, sectionName = "Jwt")`
- `AddEpSwaggerWithJwt(title, version = "v1")`
- `AddEpHttpClient(name, config, baseAddressKey = "ServiceUrls:{name}")` with retry policy
- `AddEpDefaultCors(policyName = "AllowLocalhost3000", origins?)`
- `host.EnsureDatabaseAsync<TContext>(applyMigrations: true)` + optional `IDbSeeder<TContext>`

## Example wiring in a service Startup
```csharp
// using Ep.Platform.DependencyInjection;
// using Ep.Platform.Hosting;

public void ConfigureServices(IServiceCollection services)
{
    services.AddControllers();
    services.AddEpDefaultCors();
    services.AddEpSwaggerWithJwt("Product Service");
    services.AddEpSqlServerDbContext<AppDbContext>(_config);
    services.AddEpJwtAuth(_config);
    services.AddEpHttpClient("user", _config); // pulls ServiceUrls:user
}
```

In `Program.cs`:
```csharp
var app = builder.Build();
await app.EnsureDatabaseAsync<AppDbContext>();
```

## 📦 Publishing New Versions

For detailed instructions on packing and publishing Ep.Platform to GitHub Packages, see:

**[Release Guide](../../../platform/Ep.Platform/RELEASE_GUIDE.md)** - Complete step-by-step guide for releasing new versions

The release guide covers:
- Version numbering
- Automated publishing scripts
- Manual publishing steps
- Updating services to use new versions
- Troubleshooting


