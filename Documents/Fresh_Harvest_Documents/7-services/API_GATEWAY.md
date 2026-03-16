# 🌐 Modern API Gateway Architecture with YARP

**Concepts + Implementation Guide - API Gateway**

---

## Table of Contents

1. [Evolution of API Gateways](#1-evolution-of-api-gateways)
2. [What is a Reverse Proxy?](#2-what-is-a-reverse-proxy)
3. [What is YARP?](#3-what-is-yarp)
4. [Why Use an API Gateway?](#4-why-use-an-api-gateway)
5. [Data Aggregation Strategies](#5-data-aggregation-strategies)
6. [Gateway Implementation](#6-gateway-implementation)
7. [Configuration Files](#7-configuration-files-oceletjson-vs-oceletdockerjson)
8. [Service Registration](#8-service-registration)
9. [Routing Configuration](#9-routing-configuration)
10. [Health Checks](#10-health-checks)
11. [Architecture Diagram](#11-architecture-diagram)
12. [Key Takeaways](#12-key-takeaways)

---

## 1. Evolution of API Gateways

### 🔴 Traditional API Gateway (Old Approach)

Earlier API Gateways behaved like **"mini backend applications"**:

- Had Controllers with business logic
- Orchestrated multiple microservices
- Aggregated responses before returning
- Contained domain knowledge

**Flow:**

```
Frontend → Gateway Controller → User + Orders + Payments → Combined Response
```

**Problems:**

- ❌ Heavy and complex gateway
- ❌ Business logic drift from services
- ❌ Tight coupling
- ❌ Hard to scale and maintain
- ❌ Single point of failure for logic
- ❌ Testing complexity

---

### 🟢 Modern API Gateway (Current Best Practice)

Modern architecture clearly **separates responsibilities**.

Gateway now primarily acts as a **Reverse Proxy**:

- ✅ No business logic
- ✅ No aggregation (by default)
- ✅ No controllers required (unless for BFF)
- ✅ Focused purely on infrastructure concerns

**Flow:**

```
Frontend → Gateway → Target Microservice
```

**Gateway becomes:**

- ⚡ Lightweight
- 🔒 Secure
- 🚀 Faster
- 🛠️ Easier to maintain
- 📈 Highly scalable

---

## 2. What is a Reverse Proxy?

A **Reverse Proxy** is a server that sits in front of backend services and forwards client requests to them.

### Responsibilities:

| Function            | Description                                    |
| ------------------- | ---------------------------------------------- |
| **Routing**         | Direct traffic to appropriate services         |
| **SSL Termination** | Handle HTTPS at edge                           |
| **Security**        | Authentication, rate limiting, DDoS protection |
| **Load Balancing**  | Distribute traffic across instances            |
| **Observability**   | Centralized logging and monitoring             |
| **Caching**         | Edge caching for performance                   |

### Common Reverse Proxies:

- **NGINX** - Fast, lightweight web server & reverse proxy
- **Envoy** - Cloud-native proxy (used by Istio)
- **Azure API Management** - Enterprise API gateway
- **AWS API Gateway** - Managed AWS service
- **Traefik** - Modern, cloud-native proxy
- **🟢 YARP** - Microsoft's .NET reverse proxy

---

## 3. What is YARP?

### **YARP = Yet Another Reverse Proxy**

Microsoft-built reverse proxy framework specifically for .NET:

```
🎯 Purpose: High-performance request forwarding in .NET applications
```

### Key Features:

| Feature               | Description                                             |
| --------------------- | ------------------------------------------------------- |
| **Performance**       | Built on Kestrel - extremely fast                       |
| **Configuration**     | JSON or code-based configuration                        |
| **Extensibility**     | Custom middleware and transforms                        |
| **Load Balancing**    | Multiple strategies (round-robin, least requests, etc.) |
| **Health Checks**     | Active and passive health monitoring                    |
| **Resilience**        | Retry policies, circuit breakers                        |
| **No Business Logic** | Pure proxy by design                                    |

### YARP Philosophy:

> "YARP does not do aggregation by default — **by design**. It's a pure reverse proxy that focuses on doing one thing exceptionally well: routing requests."

---

## 4. Why Use an API Gateway?

### The Question:

> "If Gateway is 'just routing', why not let the frontend call microservices directly?"

### The Answer: Gateway Provides Critical Infrastructure

#### 🔒 **Security**

```
✔ Single exposed endpoint
✔ Internal services remain private
✔ Central authentication & authorization
✔ JWT validation at edge
✔ Rate limiting & DDoS protection
✔ IP whitelisting / blacklisting
```

#### 🎯 **Simplicity**

```
✔ One hostname (api.yourdomain.com)
✔ One SSL certificate
✔ One trust boundary
✔ Simplified CORS management
```

#### 🔄 **Stability**

```
✔ Backend changes don't break frontend
✔ Service versioning handled centrally
✔ Gradual rollouts possible
✔ Better DevOps capabilities
```

#### ⚡ **Performance**

```
✔ Connection pooling
✔ Edge caching
✔ Response compression
✔ Protocol translation (HTTP/1.1 ↔ HTTP/2)
✔ Reduced network hops
```

#### 📊 **Observability**

```
✔ Centralized logging
✔ Request tracing
✔ Metrics collection
✔ Error monitoring
```

---

## 5. Data Aggregation Strategies

When UI needs data from multiple services (User + Orders + Payments), where does aggregation happen?

### ✔ **Option A: Frontend Aggregation** (Simple Case)

UI makes multiple parallel calls:

```javascript
// React component
const [user, setUser] = useState(null);
const [orders, setOrders] = useState([]);
const [payments, setPayments] = useState([]);

useEffect(() => {
  Promise.all([
    api.get("/user/123"),
    api.get("/orders?userId=123"),
    api.get("/payments?userId=123"),
  ]).then(([userData, ordersData, paymentsData]) => {
    setUser(userData);
    setOrders(ordersData);
    setPayments(paymentsData);
  });
}, []);
```

**Good for:**

- ✅ Simple screens
- ✅ 2-3 service calls max
- ✅ Lightweight data joins
- ✅ Independent data sections

**Not good for:**

- ❌ Complex data transformations
- ❌ Many service calls (>3)
- ❌ Mobile apps (battery/network)
- ❌ Complex business rules

---

### ✔ **Option B: BFF / Aggregator Service** (Recommended)

Create a **Backend For Frontend (BFF)** service:

```
Frontend → Gateway → BFF → Calls User + Orders + Payments → Aggregated Response
```

**BFF Implementation:**

```csharp
[HttpGet("dashboard/{userId}")]
public async Task<DashboardDto> GetDashboard(Guid userId)
{
    // Parallel calls to multiple services
    var userTask = _userClient.GetAsync($"/users/{userId}");
    var ordersTask = _orderClient.GetAsync($"/orders/user/{userId}");
    var paymentsTask = _paymentClient.GetAsync($"/payments/user/{userId}");

    await Task.WhenAll(userTask, ordersTask, paymentsTask);

    // Aggregate and shape for UI
    return new DashboardDto
    {
        User = await userTask.Content.ReadFromJsonAsync<UserDto>(),
        RecentOrders = await ordersTask.Content.ReadFromJsonAsync<OrderDto[]>(),
        PaymentHistory = await paymentsTask.Content.ReadFromJsonAsync<PaymentDto[]>()
    };
}
```

**Benefits:**

- ✅ Single API call from frontend
- ✅ Better performance (parallel backend calls)
- ✅ Reusable aggregation logic
- ✅ Platform-specific responses (Web vs Mobile)
- ✅ Backend-level optimizations
- ✅ Reduced frontend complexity

---

### ✔ **Option C: Domain Aggregation** (Use Carefully)

Service like `OrderService` internally calls other services.

**Example:**

```csharp
// OrderService calls UserService and ProductService internally
public async Task<Order> CreateOrder(CreateOrderDto dto)
{
    var user = await _userClient.GetUser(dto.UserId);
    var product = await _productClient.GetProduct(dto.ProductId);

    // Create order with aggregated data
}
```

**Use when:**

- Service truly owns the aggregation logic
- Strong bounded context justification
- Part of the domain workflow

**Avoid when:**

- Just for convenience
- Creates tight coupling
- Can be done at BFF layer

---

## 6. Gateway Implementation

### Project Structure

```
gateway/
├── Program.cs                 # Application entry point
├── Startup.cs                # Service configuration
├── ocelot.json              # Local development config
├── ocelot.docker.json       # Docker environment config
└── appsettings.json         # App settings
```

### **Startup.cs** - Configuration Selection

```csharp
public class Startup
{
    private readonly IConfiguration _config;

    public Startup(IConfiguration config) => _config = config;

    public void ConfigureServices(IServiceCollection services)
    {
        // 🎯 KEY: Select config based on environment
        var useDocker = _config.GetValue<string>("USE_DOCKER_NETWORK")
            ?? Environment.GetEnvironmentVariable("USE_DOCKER_NETWORK");

        var configFile = string.Equals(useDocker, "true", StringComparison.OrdinalIgnoreCase)
            ? "ocelot.docker.json"    // 🐳 Docker networking
            : "ocelot.json";          // 💻 Local development

        // Load selected configuration
        _config.AddJsonFile(configFile, optional: false, reloadOnChange: true);

        // Register YARP Reverse Proxy
        services.AddReverseProxy()
                .LoadFromConfig(_config.GetSection("ReverseProxy"));

        // Optional: Add controllers if building BFF
        services.AddControllers();

        // Optional: Swagger for documentation
        services.AddSwaggerGen();
    }

    public void Configure(WebApplication app, IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
        {
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseRouting();

        // Map YARP routes
        app.MapReverseProxy();

        // Map custom controllers (if any)
        app.MapControllers();
    }
}
```

---

### **Program.cs** - Application Entry Point (.NET 8)

```csharp
using Gateway;

var builder = WebApplication.CreateBuilder(args);

// Initialize Startup class
var startup = new Startup(builder.Configuration);

// Register services
startup.ConfigureServices(builder.Services);

// Build application
var app = builder.Build();

// Configure middleware pipeline
startup.Configure(app, app.Environment);

// Run gateway
app.Run();
```

**What This Does:**

1. 🏗️ Build hosting environment
2. 📦 Load Startup class
3. 🔧 Register DI + Services
4. 🎨 Configure middleware pipeline
5. 🚀 Start API Gateway

---

## 7. Configuration Files: `ocelot.json` vs `ocelot.docker.json`

### Why Two Configuration Files?

**Problem:** Services have different addresses in different environments.

| Environment           | Service Address     | Example                  |
| --------------------- | ------------------- | ------------------------ |
| **Local Development** | `localhost:port`    | `http://localhost:5001`  |
| **Docker**            | `service-name:port` | `http://auth-service:80` |

---

### 🟢 **ocelot.json** (Local Development)

Used when running services **directly on your machine**.

```json
{
  "ReverseProxy": {
    "Routes": [
      {
        "RouteId": "auth-route",
        "ClusterId": "authCluster",
        "Match": {
          "Path": "/api/auth/{**catch-all}"
        }
      },
      {
        "RouteId": "user-route",
        "ClusterId": "userCluster",
        "Match": {
          "Path": "/api/users/{**catch-all}"
        }
      }
    ],
    "Clusters": {
      "authCluster": {
        "Destinations": {
          "authService": {
            "Address": "http://localhost:5001/"
          }
        }
      },
      "userCluster": {
        "Destinations": {
          "userService": {
            "Address": "http://localhost:5005/"
          }
        }
      }
    }
  }
}
```

**Characteristics:**

- Uses `localhost` + port numbers
- Services run on host machine
- Standard development workflow
- Easy debugging with IDE

---

### 🟡 **ocelot.docker.json** (Docker Environment)

Used when running services **inside Docker containers**.

```json
{
  "ReverseProxy": {
    "Routes": [
      {
        "RouteId": "auth-route",
        "ClusterId": "authCluster",
        "Match": {
          "Path": "/api/auth/{**catch-all}"
        }
      },
      {
        "RouteId": "user-route",
        "ClusterId": "userCluster",
        "Match": {
          "Path": "/api/users/{**catch-all}"
        }
      }
    ],
    "Clusters": {
      "authCluster": {
        "Destinations": {
          "authService": {
            "Address": "http://auth-service:80/"
          }
        }
      },
      "userCluster": {
        "Destinations": {
          "userService": {
            "Address": "http://user-service:80/"
          }
        }
      }
    }
  }
}
```

**Characteristics:**

- Uses Docker service names (from docker-compose.yml)
- Services communicate via Docker network
- Internal DNS resolution
- Standard port 80 inside containers

---

### 🔍 **Comparison Summary**

| Feature             | `ocelot.json`    | `ocelot.docker.json`    |
| ------------------- | ---------------- | ----------------------- |
| **Environment**     | Local Machine    | Docker / Kubernetes     |
| **Service Address** | `localhost:port` | `service-name:port`     |
| **Networking**      | Host networking  | Container networking    |
| **DNS**             | OS resolver      | Docker DNS              |
| **Purpose**         | Development      | Deployment              |
| **Debugging**       | Easy (IDE)       | Requires container logs |

**This Allows:**

- ✅ Same codebase for all environments
- ✅ No code changes between dev and prod
- ✅ Configuration-driven deployment
- ✅ Perfect DevOps practice

---

## 8. Service Registration

### Reverse Proxy Registration

```csharp
services.AddReverseProxy()
        .LoadFromConfig(_config.GetSection("ReverseProxy"));
```

**What This Does:**

- Registers YARP services in DI container
- Loads routing rules from configuration
- Sets up request forwarding pipeline
- Configures load balancing and health checks

---

### Optional: Controllers for BFF

```csharp
services.AddControllers();
```

**Add Only If:**

- Building a BFF (Backend For Frontend)
- Need custom endpoints
- Adding health check APIs
- Implementing custom middleware logic

---

### Optional: Swagger Documentation

```csharp
services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "API Gateway",
        Version = "v1",
        Description = "Centralized API Gateway for microservices"
    });
});
```

---

## 9. Routing Configuration

### YARP Route Structure

```json
{
  "ReverseProxy": {
    "Routes": [
      {
        "RouteId": "unique-route-id",
        "ClusterId": "target-cluster",
        "Match": {
          "Path": "/api/service/{**catch-all}",
          "Methods": ["GET", "POST"]
        },
        "Transforms": [
          {
            "PathPattern": "/internal/{**catch-all}"
          }
        ]
      }
    ],
    "Clusters": {
      "target-cluster": {
        "Destinations": {
          "destination1": {
            "Address": "http://service:80/"
          }
        },
        "LoadBalancingPolicy": "RoundRobin"
      }
    }
  }
}
```

### Key Components:

#### **Routes:**

- Define incoming request patterns
- Match based on path, method, headers
- Apply transformations
- Forward to clusters

#### **Clusters:**

- Group of destination services
- Load balancing configuration
- Health check settings
- Timeout policies

#### **Destinations:**

- Individual service instances
- Can have multiple for load balancing
- Health status tracked independently

---

### Example: Complete Routing Setup

```json
{
  "ReverseProxy": {
    "Routes": [
      {
        "RouteId": "auth",
        "ClusterId": "authCluster",
        "Match": { "Path": "/api/auth/{**catch-all}" }
      },
      {
        "RouteId": "users",
        "ClusterId": "userCluster",
        "Match": { "Path": "/api/users/{**catch-all}" }
      },
      {
        "RouteId": "products",
        "ClusterId": "productCluster",
        "Match": { "Path": "/api/products/{**catch-all}" }
      },
      {
        "RouteId": "orders",
        "ClusterId": "orderCluster",
        "Match": { "Path": "/api/orders/{**catch-all}" }
      },
      {
        "RouteId": "payments",
        "ClusterId": "paymentCluster",
        "Match": { "Path": "/api/payments/{**catch-all}" }
      }
    ],
    "Clusters": {
      "authCluster": {
        "Destinations": {
          "authService": { "Address": "http://auth-service:80/" }
        }
      },
      "userCluster": {
        "Destinations": {
          "userService": { "Address": "http://user-service:80/" }
        }
      },
      "productCluster": {
        "Destinations": {
          "productService": { "Address": "http://product-service:80/" }
        }
      },
      "orderCluster": {
        "Destinations": {
          "orderService": { "Address": "http://order-service:80/" }
        }
      },
      "paymentCluster": {
        "Destinations": {
          "paymentService": { "Address": "http://payment-service:80/" }
        }
      }
    }
  }
}
```

**Result:**

- `/api/auth/*` → Auth Service
- `/api/users/*` → User Service
- `/api/products/*` → Product Service
- `/api/orders/*` → Order Service
- `/api/payments/*` → Payment Service

---

## 10. Health Checks

YARP supports comprehensive health monitoring:

### Active Health Checks

```json
{
  "Clusters": {
    "userCluster": {
      "Destinations": {
        "userService": { "Address": "http://user-service:80/" }
      },
      "HealthCheck": {
        "Active": {
          "Enabled": true,
          "Interval": "00:00:10",
          "Timeout": "00:00:05",
          "Policy": "ConsecutiveFailures",
          "Path": "/health"
        }
      }
    }
  }
}
```

**Features:**

- Periodic health pings
- Remove unhealthy destinations
- Automatic recovery detection
- Configurable policies

---

### Passive Health Checks

```json
{
  "HealthCheck": {
    "Passive": {
      "Enabled": true,
      "Policy": "TransportFailureRate",
      "ReactivationPeriod": "00:01:00"
    }
  }
}
```

**Features:**

- Monitor actual request failures
- Circuit breaker pattern
- Automatic destination exclusion
- Gradual reactivation

---

## 11. Architecture Diagram

```
┌─────────────────────────────────────────┐
│         Frontend (React / Mobile)       │
│         http://localhost:3000           │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP Requests
                 ▼
┌─────────────────────────────────────────┐
│          API Gateway (YARP)             │
│         http://localhost:5000           │
│                                         │
│  Responsibilities:                      │
│  • Route requests to services           │
│  • JWT validation                       │
│  • Rate limiting                        │
│  • Logging & monitoring                 │
│  • SSL termination                      │
│  • Load balancing                       │
└────┬───────┬────────┬─────────┬────────┘
     │       │        │         │
     │       │        │         │
┌────▼──┐ ┌──▼───┐ ┌─▼────┐ ┌──▼─────┐
│ Auth  │ │ User │ │Product│ │ Order  │
│Service│ │Service│ │Service│ │Service │
│:5001  │ │:5005 │ │ :5002 │ │ :5004  │
└───┬───┘ └──┬───┘ └──┬────┘ └───┬────┘
    │        │         │          │
    ▼        ▼         ▼          ▼
┌────────────────────────────────────┐
│        SQL Server (MSSQL)          │
│  authdb, userdb, productdb, etc.   │
└────────────────────────────────────┘
```

**Gateway Responsibilities:**

- 🔀 Routes traffic to appropriate services
- 🔒 Secures all service endpoints
- 📊 Provides centralized logging
- 🎯 Manages cross-cutting concerns
- ⚡ Does NOT aggregate (unless via BFF controllers)

---

## 12. Key Takeaways

### ✅ Core Principles

1. **Modern Gateway = Reverse Proxy**

   - Not a business logic container
   - Focus on infrastructure concerns
   - Keep it lightweight and fast

2. **YARP is Microsoft's Modern Proxy Engine**

   - Built for .NET ecosystem
   - High performance on Kestrel
   - Configuration-driven architecture

3. **Gateway Provides:**

   - 🔒 Security (auth, rate limiting)
   - 🔀 Routing (path-based forwarding)
   - 📊 Observability (logging, metrics)
   - ⚡ Performance (caching, pooling)
   - 🔄 Stability (versioning, failover)

4. **Aggregation Options:**

   - **Frontend** - Simple, < 3 calls
   - **BFF Service** - Recommended for complex UIs
   - **Domain Service** - Use with caution

5. **Configuration Files:**

   - `ocelot.json` → Local development (`localhost:port`)
   - `ocelot.docker.json` → Docker environment (`service-name:port`)
   - Environment-specific without code changes

6. **Clean Architecture:**
   - `Program.cs` → Application entry
   - `Startup.cs` → Service configuration
   - Config files → Environment-specific routing

---

### 📚 Further Reading

- [YARP Documentation](https://microsoft.github.io/reverse-proxy/)
- [Microservices Patterns](https://microservices.io/patterns/apigateway.html)
- [BFF Pattern](https://samnewman.io/patterns/architectural/bff/)

---

### 🎯 Next Steps

Consider implementing:

- ✔ JWT authentication middleware
- ✔ Rate limiting policies
- ✔ Request/response logging
- ✔ Distributed tracing (OpenTelemetry)
- ✔ Health check dashboard
- ✔ BFF service for complex aggregations

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Author:** MVP E-Commerce Team

