# FreshHarvest Market – High-level Architecture

## 1. Overview

**FreshHarvest Market** is an organic food marketplace designed as a small, realistic microservices playground:

- **Frontend:** React SPA
- **API Gateway:** YARP (ASP.NET Core reverse proxy)
- **Backend:** ASP.NET Core microservices (.NET 8)
- **Data:** SQL Server (containerized); each service has its own database/schema
- **Auth:** JWT tokens issued by the Auth service
- **Runtime (dev):** `dotnet run` for services, `docker compose` for infrastructure

### Goals

- Practice modern **microservice** patterns with .NET 8 + React
- Explore **API gateway** routing with YARP
- Use **EF Core** with per-service databases
- Implement **end-to-end flows**: registration, login, browsing catalog, wallet, and order creation

---

## 2. High-level System Architecture

```mermaid
%% File: docs/architecture-system.mmd
flowchart LR
    subgraph Client
        BROWSER[React SPA\n(Frontend)]
    end

    subgraph Infra[Docker / Dev Environment]
        GATEWAY[YARP API Gateway\nASP.NET Core Reverse Proxy]

        subgraph Services[Backend Microservices (.NET 8)]
            AUTH[Auth Service\n(JWT issuance)]
            USER[User Service\n(Profile)]
            PRODUCT[Product Service\n(Catalog + Inventory)]
            ORDER[Order Service\n(Order orchestration)]
            PAYMENT[Payment Service\n(Wallet + Charges)]
        end

        subgraph Data[SQL Server Container]
            DBA[(authdb)]
            DBP[(productdb)]
            DBO[(orderdb)]
            DBW[(paymentdb)]
            DBU[(userdb)]
        end
    end

    BROWSER -->|HTTPS/HTTP JSON APIs| GATEWAY

    GATEWAY --> AUTH
    GATEWAY --> USER
    GATEWAY --> PRODUCT
    GATEWAY --> ORDER
    GATEWAY --> PAYMENT

    AUTH --> DBA
    USER --> DBU
    PRODUCT --> DBP
    ORDER --> DBO
    PAYMENT --> DBW
