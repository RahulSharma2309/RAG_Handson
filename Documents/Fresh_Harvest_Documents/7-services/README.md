# 📘 Service Documentation Index

**Complete documentation for all microservices in the FreshHarvest Market organic food marketplace**

---

## New here?

- Role-based guided tour: [`../START_HERE.md`](../START_HERE.md)
- Patterns + decisions (HTTP vs service bus, catalog patterns): [`../ENGINEERING_PLAYBOOK.md`](../ENGINEERING_PLAYBOOK.md)
- Terms in plain language: [`../GLOSSARY.md`](../GLOSSARY.md)

## 📚 Table of Contents

- [Overview](#overview)
- [Service Documentation](#service-documentation)
- [Architecture Diagram](#architecture-diagram)
- [Service Communication Matrix](#service-communication-matrix)
- [Quick Reference](#quick-reference)
- [Getting Started](#getting-started)

---

## Overview

This directory contains comprehensive documentation for each microservice in the application. Each document follows a consistent structure covering architecture, API endpoints, business logic, service communication, configuration, and best practices.

### Documentation Structure

Each service documentation includes:

✅ **Service Overview** - Purpose and responsibilities  
✅ **Architecture & Design** - High-level design and patterns  
✅ **Database Schema** - Tables, entities, and relationships  
✅ **API Endpoints** - Complete endpoint documentation  
✅ **Business Logic** - Deep dive into implementation  
✅ **Service Communication** - Inter-service dependencies  
✅ **Configuration** - Settings and environment variables  
✅ **Code Walkthrough** - Project structure and key code  
✅ **Error Handling** - Common errors and solutions  
✅ **Best Practices** - Guidelines and recommendations  
✅ **Future Enhancements** - Suggested improvements  

---

## Service Documentation

### 🌐 [API Gateway](API_GATEWAY.md)

**Technology**: YARP (Yet Another Reverse Proxy)  
**Port**: 5000  
**Purpose**: Reverse proxy and request routing

**Key Topics**:
- Evolution of API Gateways (traditional vs. modern)
- What is a Reverse Proxy?
- YARP architecture and features
- Why use an API Gateway?
- Data aggregation strategies
- Configuration files (`ocelot.json` vs `ocelot.docker.json`)
- Route configuration and setup
- Health checks

**Quick Links**:
- [Configuration Files](API_GATEWAY.md#7-configuration-files-oceletjson-vs-oceletdockerjson)
- [Routing Configuration](API_GATEWAY.md#9-routing-configuration)
- [Health Checks](API_GATEWAY.md#10-health-checks)

---

### 🔐 [Auth Service](AUTH_SERVICE.md)

**Technology**: .NET 8 + BCrypt + JWT  
**Port**: 5001  
**Database**: authdb  
**Purpose**: Authentication and user registration

**Key Topics**:
- User registration with atomic profile creation
- Password hashing with BCrypt
- JWT token generation and validation
- Email and phone number validation
- Orchestrated registration with User Service
- Rollback mechanisms on failure
- Password reset functionality

**Quick Links**:
- [Registration Flow](AUTH_SERVICE.md#5-business-logic-deep-dive)
- [JWT Implementation](AUTH_SERVICE.md#7-security-implementation)
- [Service Communication](AUTH_SERVICE.md#6-service-to-service-communication)

---

### 👤 [User Service](USER_SERVICE.md)

**Technology**: .NET 8 + EF Core  
**Port**: 5005  
**Database**: userdb  
**Purpose**: User profile and wallet management

**Key Topics**:
- User profile CRUD operations
- Wallet balance management (debit/credit)
- Phone number uniqueness validation
- Repository and service layer patterns
- Wallet operations for payments
- Add balance functionality

**Quick Links**:
- [Wallet Management](USER_SERVICE.md#6-wallet-management)
- [Database Schema](USER_SERVICE.md#3-database-schema)
- [API Endpoints](USER_SERVICE.md#4-api-endpoints)

---

### 📦 [Product Service](PRODUCT_SERVICE.md)

**Technology**: .NET 8 + EF Core  
**Port**: 5002  
**Database**: productdb  
**Purpose**: Product catalog and inventory management

**Key Topics**:
- Product catalog management
- Stock reservation and release
- Inventory tracking
- Price management (stored in paise)
- Product validation
- Seed data for development

**Quick Links**:
- [Stock Management](PRODUCT_SERVICE.md#6-stock-management)
- [Product Creation](PRODUCT_SERVICE.md#5-business-logic-deep-dive)
- [API Endpoints](PRODUCT_SERVICE.md#4-api-endpoints)

---

### 🛒 [Order Service](ORDER_SERVICE.md)

**Technology**: .NET 8 + EF Core + Saga Pattern  
**Port**: 5004  
**Database**: orderdb  
**Purpose**: Order orchestration and management

**Key Topics**:
- Order orchestration (Saga pattern)
- Multi-service coordination
- Payment processing via Payment Service
- Stock reservation via Product Service
- Rollback and compensation logic
- Order history

**Quick Links**:
- [Order Orchestration](ORDER_SERVICE.md#6-order-orchestration)
- [Rollback Mechanisms](ORDER_SERVICE.md#10-error-handling--rollback)
- [Service Communication](ORDER_SERVICE.md#7-service-to-service-communication)

---

### 💳 [Payment Service](PAYMENT_SERVICE.md)

**Technology**: .NET 8 + EF Core  
**Port**: 5003  
**Database**: paymentdb  
**Purpose**: Payment processing and transaction recording

**Key Topics**:
- Payment orchestration
- Wallet operations via User Service
- Transaction recording
- Refund handling
- Payment history
- Status management

**Quick Links**:
- [Payment Processing](PAYMENT_SERVICE.md#6-payment-processing-flow)
- [Refund Flow](PAYMENT_SERVICE.md#6-payment-processing-flow)
- [API Endpoints](PAYMENT_SERVICE.md#4-api-endpoints)

---

## Architecture Diagram

### Overall System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│         Port: 3000 (Nginx)              │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────┐
│       API Gateway (YARP)                │
│       Port: 5000                        │
│  • Routes requests to services          │
│  • Load balancing (future)              │
│  • Health checks (future)               │
└───┬─────┬──────┬──────┬─────────────────┘
    │     │      │      │
    ▼     ▼      ▼      ▼
┌────────┬──────┬──────┬──────┬──────┐
│  Auth  │ User │Product│Order │Payment│
│:5001   │:5005 │:5002 │:5004 │:5003  │
└───┬────┴──┬───┴──┬───┴──┬───┴───┬───┘
    │       │      │      │       │
    └───────┴──────┴──────┴───────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │   SQL Server (MSSQL)    │
    │   Port: 1433            │
    │                         │
    │  • authdb               │
    │  • userdb               │
    │  • productdb            │
    │  • orderdb              │
    │  • paymentdb            │
    └─────────────────────────┘
```

### Service Communication Flow

```
┌───────────────────────────────────────────────┐
│  Frontend → Gateway → Auth Service            │
│  (Registration & Login)                       │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│  Auth Service → User Service                  │
│  (Phone validation, Profile creation)         │
└───────────────────────────────────────────────┘

┌───────────────────────────────────────────────┐
│  Frontend → Gateway → Order Service           │
│  (Create Order - Orchestrator)                │
└───────────────┬───────────────────────────────┘
                │
        ┌───────┴───────┬──────────┐
        ▼               ▼          ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│ User Service │ │  Product │ │ Payment  │
│ (Get Profile)│ │ (Stock)  │ │(Process) │
└──────────────┘ └──────────┘ └────┬─────┘
                                    │
                                    ▼
                              ┌──────────┐
                              │   User   │
                              │ (Wallet) │
                              └──────────┘
```

---

## Service Communication Matrix

| Service | Calls | Called By | Purpose |
|---------|-------|-----------|---------|
| **API Gateway** | All services | Frontend | Request routing |
| **Auth Service** | User Service | Frontend | Registration, login |
| **User Service** | None | Auth, Payment, Order | Profile, wallet management |
| **Product Service** | None | Order | Product info, stock management |
| **Order Service** | User, Product, Payment | Frontend | Order orchestration |
| **Payment Service** | User | Order | Payment processing |

---

## Quick Reference

### Service Ports

| Service | Local Port | Docker Port | Database |
|---------|-----------|-------------|----------|
| Frontend | 3000 | 3000 | - |
| Gateway | 5000 | 5000 | - |
| Auth | 5001 | 80 | authdb |
| Product | 5002 | 80 | productdb |
| Payment | 5003 | 80 | paymentdb |
| Order | 5004 | 80 | orderdb |
| User | 5005 | 80 | userdb |
| SQL Server | 1433 | 1433 | All databases |

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | .NET 8, ASP.NET Core Web API |
| **ORM** | Entity Framework Core |
| **Database** | SQL Server 2019 |
| **Auth** | JWT (HS256), BCrypt password hashing |
| **Gateway** | YARP (Yet Another Reverse Proxy) |
| **Frontend** | React 18 |
| **Containerization** | Docker, Docker Compose |

### Design Patterns Used

| Pattern | Service | Purpose |
|---------|---------|---------|
| **Saga Pattern** | Order Service | Distributed transaction orchestration |
| **Repository Pattern** | User, Product | Data access abstraction |
| **Service Layer Pattern** | All services | Business logic encapsulation |
| **DTO Pattern** | All services | Data transfer objects |
| **Factory Pattern** | All services | HttpClientFactory for service calls |
| **Orchestrator Pattern** | Order, Payment | Multi-service coordination |

---

## Getting Started

### 1. Prerequisites

- Docker Desktop installed
- Ports 3000, 5000-5005, 1433 available

### 2. Start All Services

```bash
cd infra
docker-compose up --build -d
```

### 3. Verify Services

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access Swagger Documentation

- **Auth Service**: http://localhost:5001/swagger
- **User Service**: http://localhost:5005/swagger
- **Product Service**: http://localhost:5002/swagger
- **Order Service**: http://localhost:5004/swagger
- **Payment Service**: http://localhost:5003/swagger

### 5. Access Frontend

http://localhost:3000

### 6. Stop All Services

```bash
docker-compose down
```

---

## Documentation Best Practices

When reading service documentation:

1. **Start with Overview** - Understand the service's purpose
2. **Review Architecture** - See how it fits in the system
3. **Check API Endpoints** - Learn the available operations
4. **Understand Business Logic** - Deep dive into implementation
5. **Study Service Communication** - See dependencies and flows
6. **Review Error Handling** - Learn about failure scenarios
7. **Follow Best Practices** - Apply recommended patterns

---

## Related Documentation

### User Journey Documentation

Complete user flow documentation is available in [`docs/Functionality/`](../Functionality/):

- [SIGNUP_FLOW.md](../Functionality/SIGNUP_FLOW.md) - User registration process
- [LOGIN_FLOW.md](../Functionality/LOGIN_FLOW.md) - User authentication flow
- [ADD_TO_CART_FLOW.md](../Functionality/ADD_TO_CART_FLOW.md) - Shopping cart management
- [CHECKOUT_ORDER_FLOW.md](../Functionality/CHECKOUT_ORDER_FLOW.md) - Order creation flow
- [ORDER_HISTORY_FLOW.md](../Functionality/ORDER_HISTORY_FLOW.md) - View past orders
- [ADD_BALANCE_FLOW.md](../Functionality/ADD_BALANCE_FLOW.md) - Wallet top-up

---

## Contributing to Documentation

When adding or updating service documentation:

1. Follow the established structure
2. Include code examples with proper syntax highlighting
3. Add diagrams using ASCII art or Mermaid
4. Provide clear, step-by-step explanations
5. Include error scenarios and solutions
6. Keep best practices section updated
7. Add future enhancements section

---

## Feedback & Questions

For questions or feedback on the documentation:

1. Review the specific service documentation
2. Check related user flow documentation
3. Examine code examples and implementations
4. Open an issue on GitHub (if applicable)

---

**Documentation Version:** 1.0  
**Last Updated:** December 24, 2025  
**Maintained By:** FreshHarvest Market Team  

**Total Documentation Pages:** 6  
**Total Services Documented:** 5 + Gateway  
**Coverage:** 100%  

---

## Document Change Log

| Date | Changes | Author |
|------|---------|--------|
| 2025-12-24 | Initial creation of all service documentation | MVP Team |
| 2025-12-24 | Added API Gateway documentation | MVP Team |
| 2025-12-24 | Completed all 6 service documents | MVP Team |

---

**🎯 All services are fully documented and ready for development, deployment, and maintenance!**


