# Kubernetes Implementation Details - FreshHarvest Market

> **Detailed documentation of how Kubernetes is implemented in FreshHarvest Market**

## Table of Contents

1. [Implementation Journey](#implementation-journey)
2. [File Structure](#file-structure)
3. [Implementation Decisions](#implementation-decisions)
4. [Security Implementation](#security-implementation)
5. [Environment Separation](#environment-separation)
6. [Service Architecture](#service-architecture)
7. [Configuration Management](#configuration-management)

---

## Implementation Journey

### Phase 1: Learning and Planning

**Goal:** Understand Kubernetes concepts and plan implementation

**What we learned:**
1. **Namespaces** - Environment separation (staging/prod)
2. **RBAC** - Security and access control
3. **Deployments** - Application lifecycle management
4. **Services** - Service discovery and networking
5. **ConfigMaps/Secrets** - Configuration management

**Decisions made:**
- Use 2 namespaces: staging and prod
- Separate folders for staging/prod configs
- Each service gets its own ServiceAccount
- Use ConfigMaps for non-sensitive config
- Use Secrets for sensitive data

### Phase 2: Infrastructure Setup

**Step 1: Create Namespaces**
- Created staging namespace
- Created prod namespace
- Applied labels and annotations

**Step 2: Set up RBAC**
- Created ServiceAccounts for all 7 services
- Defined Roles (service-role, deployment-role)
- Created RoleBindings linking ServiceAccounts to Roles

**Step 3: Create Configuration**
- Created ConfigMaps for application settings
- Created Secrets for database connections
- Environment-specific values for staging/prod

**Step 4: Create Deployments**
- Defined Deployment for each service
- Configured replicas, resources, health checks
- Linked to ConfigMaps and Secrets

**Step 5: Create Services**
- Created Kubernetes Service for each service
- Configured service discovery
- Set up internal communication

### Phase 3: Security Hardening

**Improvements made:**
1. Removed `pods/exec` permission (security risk)
2. Replaced `latest` tags with version tags
3. Added resource limits to all containers
4. Added comments explaining HTTP usage (internal cluster communication)
5. Set `automountServiceAccountToken: false` for frontend (doesn't need RBAC)

### Phase 4: Folder Restructuring

**Current structure:**
- Original: All files in one folder, staging/prod in same files
- New: Separate staging/ and prod/ folders

**Benefits:**
- Clear separation of environments
- Easier to manage
- Reduced risk of deploying to wrong environment
- Better for team collaboration

---

## File Structure

### Current Structure (Work in Progress)

```
infra/k8s/
├── staging/                    # Staging environment
│   ├── namespaces/
│   │   └── namespace.yaml
│   ├── rbac/
│   │   ├── service-accounts.yaml
│   │   ├── roles.yaml          # To be split
│   │   └── role-bindings.yaml  # To be split
│   ├── configmaps/
│   │   └── configmaps.yaml     # To be split
│   ├── secrets/
│   │   └── secrets.yaml        # To be split
│   └── deployments/
│       └── (to be created)
│
└── prod/                       # Production environment
    ├── namespaces/
    │   └── namespace.yaml
    ├── rbac/
    │   ├── service-accounts.yaml
    │   ├── roles.yaml          # To be split
    │   └── role-bindings.yaml  # To be split
    ├── configmaps/
    │   └── configmaps.yaml     # To be split
    ├── secrets/
    │   └── secrets.yaml        # To be split
    └── deployments/
        └── (to be created)
```

### Target Structure (Complete)

```
infra/k8s/
├── staging/
│   ├── namespaces/
│   │   └── namespace.yaml
│   ├── rbac/
│   │   ├── service-accounts.yaml
│   │   ├── roles.yaml
│   │   └── role-bindings.yaml
│   ├── configmaps/
│   │   └── configmaps.yaml
│   ├── secrets/
│   │   └── secrets.yaml
│   └── deployments/
│       ├── auth-service/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── user-service/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── product-service/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── order-service/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── payment-service/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── gateway/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── frontend/
│           ├── deployment.yaml
│           └── service.yaml
│
└── prod/
    └── (same structure as staging)
```

---

## Implementation Decisions

### 1. Namespace Strategy

**Decision:** Use 2 namespaces (staging and prod)

**Rationale:**
- Clear environment separation
- Prevents accidents (can't delete prod when working on staging)
- Enables environment-specific RBAC and resource quotas
- Industry standard practice

**Implementation:**
- Separate namespace YAML files
- Clear naming: `staging` and `prod`
- Labels and annotations for metadata

### 2. RBAC Strategy

**Decision:** 
- Each service gets its own ServiceAccount
- Two Roles: service-role (read-only) and deployment-role (full access)
- RoleBindings connect ServiceAccounts to Roles

**Rationale:**
- Security: Services only get permissions they need
- Auditing: Track which service did what
- Isolation: Services can't interfere with each other
- Principle of least privilege

**Implementation:**
- ServiceAccounts: One per service (7 total)
- Roles: 2 roles (service-role, deployment-role)
- RoleBindings: 7 bindings (one per service to service-role)

### 3. Deployment Strategy

**Decision:**
- Staging: 2 replicas per service
- Production: 3 replicas per service
- Resource limits based on environment

**Rationale:**
- Staging: Lower resources (cost optimization)
- Production: Higher resources (performance, reliability)
- Multiple replicas: High availability, load distribution

**Resource Allocation:**

**Staging:**
- Requests: CPU 100m, Memory 256Mi
- Limits: CPU 500m, Memory 512Mi
- Replicas: 2

**Production:**
- Requests: CPU 200m, Memory 512Mi
- Limits: CPU 1000m, Memory 1Gi
- Replicas: 3

### 4. Service Discovery Strategy

**Decision:** Use Kubernetes Services (ClusterIP) for internal communication

**Rationale:**
- Built-in service discovery
- Load balancing across replicas
- Stable endpoints (names don't change)
- DNS-based resolution

**Implementation:**
- Service name = application name
- Port: 80 (standard HTTP port)
- Type: ClusterIP (internal only)
- DNS: `http://service-name:80`

### 5. Configuration Management Strategy

**Decision:**
- ConfigMaps for non-sensitive configuration
- Secrets for sensitive data (passwords, connection strings)
- Environment-specific values

**Rationale:**
- Separation of config from code
- Easy to update without rebuilding images
- Security: Secrets encrypted at rest
- Environment-specific: Different values for staging/prod

**Implementation:**
- ConfigMaps: Environment variables, log levels, URLs
- Secrets: Database connection strings, passwords
- Referenced in Deployments via `env` or `envFrom`

### 6. Image Tagging Strategy

**Decision:** Use version tags (not "latest")

**Rationale:**
- Reproducibility: Same image version every time
- Rollback capability: Can rollback to previous version
- Security: "latest" tag can change unexpectedly
- Best practice for production

**Implementation:**
- Format: `service-name:v1.0.0`
- Future: Use semantic versioning
- Production: `imagePullPolicy: Always`
- Staging: `imagePullPolicy: IfNotPresent`

---

## Security Implementation

### 1. RBAC (Role-Based Access Control)

**ServiceAccounts:**
- One per service (7 total)
- Unique identity for each service
- Used for authentication and auditing

**Roles:**
- `service-role`: Read-only permissions
  - Read: ConfigMaps, Secrets, Services, Endpoints, Pods
  - Cannot: Create, update, delete
- `deployment-role`: Full permissions (for CI/CD)
  - Full access to Deployments, Services, ConfigMaps, Secrets
  - Read-only access to Pods in production

**RoleBindings:**
- Each service bound to `service-role`
- CI/CD tools bound to `deployment-role`

### 2. Secrets Management

**Current Implementation:**
- Secrets stored in Kubernetes
- Base64 encoded (not encrypted by default)
- Referenced in Deployments

**Security Notes:**
- ⚠️ In production, use proper secret management
- ⚠️ Never commit real secrets to git
- ✅ Use cloud secret stores (Azure Key Vault, AWS Secrets Manager)
- ✅ Use sealed-secrets or external-secrets operators

### 3. Network Security

**Current:**
- Internal communication only (ClusterIP)
- No external access (except frontend via NodePort)

**Future:**
- Network Policies (control traffic between services)
- Ingress with TLS (HTTPS for external access)
- Service Mesh (Istio/Linkerd for advanced networking)

### 4. Image Security

**Implementation:**
- Version tags (not "latest")
- Image pull policies
- Resource limits (prevent resource exhaustion)

**Future:**
- Image scanning (vulnerability scanning)
- Image signing (verify image integrity)
- Private registries (control image access)

---

## Environment Separation

### Staging Environment

**Purpose:** Testing and QA

**Characteristics:**
- Lower resource allocation
- 2 replicas per service
- Development-like configuration
- More permissive (for testing)

**Access:**
- Developers
- QA team
- CI/CD pipelines

**Configuration:**
- Environment: Development
- Log level: Information
- Debug features enabled

### Production Environment

**Purpose:** Live production serving real users

**Characteristics:**
- Higher resource allocation
- 3+ replicas per service
- Production-optimized configuration
- Restricted access

**Access:**
- DevOps team
- SRE team
- Automated deployments only

**Configuration:**
- Environment: Production
- Log level: Warning/Error
- Debug features disabled
- Monitoring and alerting enabled

---

## Service Architecture

### Services in FreshHarvest Market

1. **auth-service** - Authentication and authorization
2. **user-service** - User profiles and wallet management
3. **product-service** - Product catalog and inventory
4. **order-service** - Order processing and orchestration
5. **payment-service** - Payment processing
6. **gateway** - API Gateway (YARP)
7. **frontend** - React frontend application

### Service Dependencies

```
Frontend
  └─> Gateway
        ├─> auth-service
        ├─> user-service
        ├─> product-service
        ├─> order-service
        │     ├─> product-service
        │     ├─> payment-service
        │     └─> user-service
        └─> payment-service
              └─> user-service
```

### Service Communication

**Pattern:** Service-to-service communication via Kubernetes Services

**Example:**
```
order-service needs to call product-service:
  http://product-service:80/api/products/{id}

order-service needs to call payment-service:
  http://payment-service:80/api/payments/record
```

**Benefits:**
- Service discovery (no hardcoded IPs)
- Load balancing (automatically distributed)
- Health checking (only healthy pods receive traffic)

---

## Configuration Management

### ConfigMaps

**Location:** `infra/k8s/staging/configmaps/configmaps.yaml`

**Contains:**
- Environment variables
- Log levels
- Service URLs
- Application settings

**Example:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-service-config
  namespace: staging
data:
  ASPNETCORE_ENVIRONMENT: "Development"
  ASPNETCORE_URLS: "http://+:80"
  Logging__LogLevel__Default: "Information"
```

### Secrets

**Location:** `infra/k8s/staging/secrets/secrets.yaml`

**Contains:**
- Database connection strings
- Passwords
- API keys

**Example:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-service-db-secret
  namespace: staging
type: Opaque
stringData:
  ConnectionStrings__DefaultConnection: "Server=mssql;Database=authdb;..."
```

### Environment-Specific Values

**Staging:**
- Database: Staging database
- Log level: Information (verbose)
- Environment: Development

**Production:**
- Database: Production database
- Log level: Warning/Error (less verbose)
- Environment: Production

---

## 📚 Related Documents

- **[LEARNING_PATH.md](./LEARNING_PATH.md)** - Complete learning guide
- **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** - Real-world analogies
- **[CONCEPTS.md](./CONCEPTS.md)** - Deep dive into concepts
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced topics
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference

---

## Summary

This document covered:

✅ **Implementation Journey** - How we got here
✅ **File Structure** - Current and target structure
✅ **Implementation Decisions** - Why we made each decision
✅ **Security Implementation** - RBAC, Secrets, Network security
✅ **Environment Separation** - Staging vs Production
✅ **Service Architecture** - Services and dependencies
✅ **Configuration Management** - ConfigMaps and Secrets

**Key Takeaways:**
- Clear separation of staging/prod
- Security-first approach (RBAC, Secrets)
- Resource optimization per environment
- Service discovery for microservices
- Configuration management best practices

**Next Steps:**
- Complete file splitting (staging/prod folders)
- Set up database in Kubernetes
- Build and push Docker images
- Deploy to cluster
- Set up monitoring and logging
- Configure CI/CD pipelines
