# Kubernetes Implementation Guide - FreshHarvest Market

> **Your comprehensive guide to understanding Kubernetes concepts and how they're implemented in FreshHarvest Market**

## 📚 Table of Contents

1. [Overview](#overview)
2. [What is Kubernetes?](#what-is-kubernetes)
3. [Key Concepts Explained](#key-concepts-explained)
4. [Our Implementation Structure](#our-implementation-structure)
5. [File-by-File Guide](#file-by-file-guide)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [How to Use](#how-to-use)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This directory contains comprehensive documentation about Kubernetes implementation for FreshHarvest Market. This guide explains:

- **What Kubernetes is** and why we use it
- **Key concepts** (Namespaces, RBAC, Deployments, Services, etc.)
- **How we've implemented** Kubernetes in our project
- **What each file does** and why it exists
- **How to use** the Kubernetes manifests

### Prerequisites

- Basic understanding of containers and Docker
- Kubernetes cluster (Docker Desktop, Minikube, or cloud provider)
- `kubectl` installed and configured

### Quick Links

#### 🚀 Getting Started
- **[LOCAL_DEPLOYMENT_GUIDE.md](./LOCAL_DEPLOYMENT_GUIDE.md)** - 🎯 **NEW USERS START HERE!** Complete step-by-step guide to run FreshHarvest Market on your local machine

#### 📖 Learning Resources
- **[LEARNING_PATH.md](./LEARNING_PATH.md)** - Complete learning guide for Kubernetes concepts
- **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** - Real-world analogies for all concepts
- **[CONCEPTS.md](./CONCEPTS.md)** - Deep dive into core concepts
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced topics (Ingress, LoadBalancer, etc.)

#### 🔧 Implementation Details
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s in this project
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference
- **[STORAGE_GUIDE.md](./STORAGE_GUIDE.md)** - Persistent storage explained
- **[HELM_GUIDE.md](./HELM_GUIDE.md)** - Complete Helm charts guide
- **[CI_CD_INTEGRATION.md](./CI_CD_INTEGRATION.md)** - How CI/CD deploys to K8s

---

## What is Kubernetes?

**Kubernetes (K8s)** is a container orchestration platform that automates deploying, scaling, and managing containerized applications.

### Real-World Analogy

Think of Kubernetes as a **smart factory manager**:

```
Traditional Approach (Docker Compose):
- You manually tell each machine: "Run this container"
- If a container crashes, you manually restart it
- To scale, you manually start more containers
- Everything is manual and time-consuming

Kubernetes Approach:
- You tell Kubernetes: "I want 3 copies of auth-service running"
- Kubernetes automatically:
  - Finds machines with resources
  - Starts containers
  - Monitors health
  - Restarts if they crash
  - Load balances traffic
  - Scales up/down as needed
```

### Why Kubernetes?

**For FreshHarvest Market:**

1. **Scalability**: Easily scale services based on demand
2. **High Availability**: Automatic restart of failed containers
3. **Resource Management**: Efficient use of cluster resources
4. **Service Discovery**: Services can find each other automatically
5. **Environment Separation**: Clean separation between staging and production
6. **Security**: RBAC, Secrets management, network policies
7. **Production Ready**: Industry-standard for deploying microservices

---

## Key Concepts Explained

### 1. Namespace

**What it is:** A virtual cluster inside your Kubernetes cluster.

**Real-World Analogy:**
- Think of a namespace as a **floor in an office building**
- Floor 1 = Staging (testing)
- Floor 2 = Production (live)
- Each floor is isolated - what happens on one doesn't affect the other

**Why we need it:**
- Prevents accidents (can't delete production when working on staging)
- Resource organization
- Access control
- Cost tracking

**In our project:**
- `staging` namespace - For testing and QA
- `prod` namespace - For live production environment

**Location:** `infra/k8s/staging/namespaces/` and `infra/k8s/prod/namespaces/`

---

### 2. RBAC (Role-Based Access Control)

**What it is:** Security system that controls who can do what in Kubernetes.

**Real-World Analogy:**
- **ServiceAccount** = Employee ID card (who you are)
- **Role** = Job description (what you're allowed to do)
- **RoleBinding** = Assignment (connecting the ID card to the job)

**Why we need it:**
- Security: Services only get permissions they need
- Auditing: Track who did what
- Isolation: Services can't interfere with each other

**Components:**

1. **ServiceAccount** - Identity for pods/services
   - Each service gets its own ServiceAccount
   - Example: `auth-service-sa`, `user-service-sa`

2. **Role** - Defines permissions (what actions are allowed)
   - `service-role` - Read-only permissions for services
   - `deployment-role` - Full permissions for CI/CD

3. **RoleBinding** - Connects ServiceAccount to Role
   - Links who gets what permissions

**Location:** `infra/k8s/staging/rbac/` and `infra/k8s/prod/rbac/`

---

### 3. ConfigMap

**What it is:** Stores non-sensitive configuration data.

**Real-World Analogy:**
- Like a **settings file** that multiple services can read
- Environment variables, log levels, feature flags

**Why we need it:**
- Separate configuration from code
- Easy to update without rebuilding images
- Shared configuration across services

**In our project:**
- Environment variables (ASPNETCORE_ENVIRONMENT, log levels)
- Service URLs
- Application settings

**Location:** `infra/k8s/staging/configmaps/` and `infra/k8s/prod/configmaps/`

---

### 4. Secret

**What it is:** Stores sensitive data (passwords, API keys, certificates).

**Real-World Analogy:**
- Like a **locked safe** for sensitive information
- Database passwords, API keys, certificates

**Why we need it:**
- Security: Encrypted at rest by Kubernetes
- Never hardcode passwords in code
- Easy to rotate secrets

**In our project:**
- Database connection strings
- API keys
- Passwords

**Location:** `infra/k8s/staging/secrets/` and `infra/k8s/prod/secrets/`

**⚠️ Important:** In production, use proper secret management (Azure Key Vault, AWS Secrets Manager, etc.)

---

### 5. Deployment

**What it is:** Tells Kubernetes how to run your application.

**Real-World Analogy:**
- Like a **job description** for Kubernetes
- "Run 2 copies of auth-service using this image, with these settings"

**Why we need it:**
- Defines what to run (Docker image)
- How many copies (replicas)
- Resource limits (CPU, memory)
- Health checks
- Restart policy

**In our project:**
- Each service has a Deployment
- Staging: 2 replicas per service
- Production: 3 replicas per service

**Location:** `infra/k8s/staging/deployments/` and `infra/k8s/prod/deployments/`

---

### 6. Service

**What it is:** Makes pods accessible within the cluster.

**Real-World Analogy:**
- Like a **phone book** or **name tag**
- Pods have random IPs (they change when restarted)
- Service gives them a stable name: `http://auth-service:80`

**Why we need it:**
- Service discovery: Services find each other by name
- Load balancing: Distributes traffic across replicas
- Stable endpoints: IPs change, names don't

**In our project:**
- Each service has a Kubernetes Service
- Internal communication: `http://auth-service:80`
- Type: ClusterIP (internal only)

**Location:** `infra/k8s/staging/deployments/<service>/service.yaml`

---

## Our Implementation Structure

```
infra/k8s/
├── staging/                    # Staging environment
│   ├── namespaces/
│   │   └── namespace.yaml      # Staging namespace
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
│       ├── user-service/
│       ├── product-service/
│       ├── order-service/
│       ├── payment-service/
│       ├── gateway/
│       └── frontend/
│
└── prod/                       # Production environment
    ├── namespaces/
    ├── rbac/
    ├── configmaps/
    ├── secrets/
    └── deployments/
        └── (same structure as staging)
```

### Why Separate Folders?

1. **Clear Separation**: Staging and prod configs are completely separate
2. **Easier Management**: Apply staging changes without affecting prod
3. **Safety**: Reduces risk of deploying to wrong environment
4. **Team Collaboration**: Different teams can work on different environments

---

## File-by-File Guide

### Namespaces

**File:** `infra/k8s/staging/namespaces/namespace.yaml`
**Purpose:** Creates the staging namespace

**Key Fields:**
- `name: staging` - Namespace name
- `labels` - Metadata for filtering
- `annotations` - Descriptive information

**What it does:**
- Creates an isolated workspace for staging
- Allows resource organization
- Enables RBAC and resource quotas

---

### RBAC Files

#### Service Accounts
**File:** `infra/k8s/staging/rbac/service-accounts.yaml`
**Purpose:** Creates ServiceAccounts for each service

**What it does:**
- Creates unique identity for each service
- Enables security and auditing
- Required for RBAC

**Services with ServiceAccounts:**
- auth-service-sa
- user-service-sa
- product-service-sa
- order-service-sa
- payment-service-sa
- gateway-sa
- frontend-sa

---

#### Roles
**File:** `infra/k8s/staging/rbac/roles.yaml`
**Purpose:** Defines what permissions are allowed

**Roles defined:**
1. **service-role** - Read-only permissions
   - Read ConfigMaps, Secrets, Services, Endpoints, Pods
   - Used by application services

2. **deployment-role** - Full permissions
   - Create/Update/Delete Deployments, Services, ConfigMaps, Secrets
   - Used by CI/CD tools

**Key Concept:**
- Roles are namespace-scoped
- Define what actions (verbs) are allowed on what resources
- Verbs: get, list, watch, create, update, delete

---

#### Role Bindings
**File:** `infra/k8s/staging/rbac/role-bindings.yaml`
**Purpose:** Connects ServiceAccounts to Roles

**What it does:**
- Links who (ServiceAccount) gets what (Role) permissions
- Each service gets `service-role` permissions
- CI/CD tools get `deployment-role` permissions

**Example:**
```yaml
# Gives auth-service-sa the permissions defined in service-role
RoleBinding:
  - ServiceAccount: auth-service-sa
  - Role: service-role
```

---

### ConfigMaps

**File:** `infra/k8s/staging/configmaps/configmaps.yaml`
**Purpose:** Stores non-sensitive configuration

**What it contains:**
- Environment variables (ASPNETCORE_ENVIRONMENT)
- Log levels
- Service URLs
- Application settings

**How services use it:**
- Deployments reference ConfigMap values
- Injected as environment variables
- Can be updated without rebuilding images

---

### Secrets

**File:** `infra/k8s/staging/secrets/secrets.yaml`
**Purpose:** Stores sensitive data

**What it contains:**
- Database connection strings
- Passwords
- API keys

**⚠️ Security Note:**
- Secrets are base64 encoded (not encrypted by default)
- In production, use proper secret management
- Never commit actual production secrets to git

**How services use it:**
- Deployments reference Secret values
- Injected as environment variables
- Kubernetes encrypts secrets at rest

---

### Deployments

**File:** `infra/k8s/staging/deployments/<service>/deployment.yaml`
**Purpose:** Defines how to run each service

**What it contains:**
- Docker image to use
- Number of replicas
- Resource limits (CPU, memory)
- Environment variables (from ConfigMaps/Secrets)
- Health checks (liveness, readiness)
- ServiceAccount to use

**Example Structure:**
```yaml
Deployment:
  replicas: 2
  template:
    spec:
      serviceAccountName: auth-service-sa
      containers:
        - name: auth-service
          image: auth-service:v1.0.0
          resources:
            requests: { memory: "256Mi", cpu: "100m" }
            limits: { memory: "512Mi", cpu: "500m" }
          env:
            - name: ConnectionStrings__DefaultConnection
              valueFrom:
                secretKeyRef:
                  name: auth-service-db-secret
          livenessProbe: ...
          readinessProbe: ...
```

---

### Services

**File:** `infra/k8s/staging/deployments/<service>/service.yaml`
**Purpose:** Makes services accessible within cluster

**What it contains:**
- Service name (used for service discovery)
- Port mapping
- Pod selector

**How it works:**
- Other services call: `http://auth-service:80`
- Kubernetes routes to healthy pods
- Load balances across replicas

**Service Types:**
- **ClusterIP** (default) - Internal only
- **NodePort** - Exposes on node IP
- **LoadBalancer** - Cloud provider load balancer
- **Ingress** - HTTP/HTTPS routing

---

## Step-by-Step Implementation

This section documents how we implemented Kubernetes for FreshHarvest Market.

### Phase 1: Understanding Concepts

1. **Namespaces**
   - Learned what namespaces are and why they're important
   - Decided on 2 namespaces: staging and prod

2. **RBAC**
   - Understood ServiceAccounts, Roles, RoleBindings
   - Designed permission structure
   - Created ServiceAccounts for each service

3. **Deployments**
   - Learned how Deployments manage pods
   - Designed resource requirements
   - Planned health checks

### Phase 2: Creating Infrastructure

1. **Created Folder Structure**
   ```
   infra/k8s/
   ├── staging/
   └── prod/
   ```

2. **Created Namespaces**
   - Staging namespace for testing
   - Production namespace for live environment

3. **Created RBAC**
   - ServiceAccounts for all 7 services
   - Roles (service-role, deployment-role)
   - RoleBindings connecting them

4. **Created ConfigMaps**
   - Application configuration
   - Environment-specific settings

5. **Created Secrets**
   - Database connection strings
   - Sensitive credentials

6. **Created Deployments**
   - All 7 services (auth, user, product, order, payment, gateway, frontend)
   - Staging and production versions

7. **Created Services**
   - Kubernetes Services for service discovery
   - Internal communication setup

### Phase 3: Security Improvements

1. **Removed pods/exec permission** (security hardening)
2. **Fixed image tags** (replaced "latest" with version tags)
3. **Added resource limits** (prevent resource exhaustion)
4. **Added health checks** (automatic recovery)
5. **Separated staging/prod** (folder structure)

---

## How to Use

### Prerequisites

1. **Kubernetes Cluster**
   ```bash
   # Docker Desktop (Windows/Mac)
   # Enable Kubernetes in Docker Desktop settings

   # Or Minikube
   minikube start

   # Or Cloud Provider (AKS, EKS, GKE)
   ```

2. **kubectl installed**
   ```bash
   # Verify installation
   kubectl version --client
   ```

### Apply Namespaces

```bash
# Apply staging namespace
kubectl apply -f infra/k8s/staging/namespaces/

# Apply production namespace
kubectl apply -f infra/k8s/prod/namespaces/

# Verify
kubectl get namespaces
```

### Apply RBAC

```bash
# Apply staging RBAC
kubectl apply -f infra/k8s/staging/rbac/

# Apply production RBAC
kubectl apply -f infra/k8s/prod/rbac/

# Verify
kubectl get serviceaccounts -n staging
kubectl get roles -n staging
kubectl get rolebindings -n staging
```

### Apply ConfigMaps and Secrets

```bash
# Apply staging ConfigMaps
kubectl apply -f infra/k8s/staging/configmaps/

# Apply staging Secrets
kubectl apply -f infra/k8s/staging/secrets/

# Verify
kubectl get configmaps -n staging
kubectl get secrets -n staging
```

### Apply Deployments

```bash
# Apply all staging deployments
kubectl apply -f infra/k8s/staging/deployments/

# Verify
kubectl get deployments -n staging
kubectl get pods -n staging
kubectl get services -n staging
```

### Common Commands

```bash
# Check status
kubectl get all -n staging

# View logs
kubectl logs -n staging deployment/auth-service

# Describe resource
kubectl describe deployment auth-service -n staging

# Scale deployment
kubectl scale deployment auth-service --replicas=3 -n staging

# Update image
kubectl set image deployment/auth-service \
  auth-service=my-image:v2.0.0 -n staging
```

---

## Best Practices

### 1. Security

- ✅ **Use ServiceAccounts** - Each service has its own identity
- ✅ **Principle of Least Privilege** - Only give services permissions they need
- ✅ **Use Secrets for sensitive data** - Never hardcode passwords
- ✅ **Version image tags** - Don't use "latest" in production
- ✅ **Separate staging/prod** - Clear separation of environments

### 2. Resource Management

- ✅ **Set resource limits** - Prevent one service from using all resources
- ✅ **Set resource requests** - Help Kubernetes schedule pods
- ✅ **Use appropriate replica counts** - 2 for staging, 3+ for production

### 3. Reliability

- ✅ **Use health checks** - Liveness and readiness probes
- ✅ **Multiple replicas** - High availability
- ✅ **Use Deployments** - Automatic restart of failed pods
- ✅ **Graceful shutdowns** - Handle termination signals

### 4. Maintainability

- ✅ **Organize by environment** - Separate staging/prod folders
- ✅ **Use ConfigMaps** - Separate config from code
- ✅ **Document everything** - Comments and README files
- ✅ **Version control** - All manifests in git

### 5. Production Readiness

- ✅ **Use specific image tags** - Not "latest"
- ✅ **Proper secret management** - Use cloud secret stores
- ✅ **Resource quotas** - Limit resource usage per namespace
- ✅ **Network policies** - Control traffic between services
- ✅ **Monitoring** - Set up logging and metrics
- ✅ **Backup strategies** - Backup secrets and configs

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n staging

# View pod events
kubectl describe pod <pod-name> -n staging

# View logs
kubectl logs <pod-name> -n staging

# Common issues:
# - Image pull errors (check image name/tag)
# - Resource limits too low
# - Health check failures
# - Missing ConfigMaps/Secrets
```

### Services Not Accessible

```bash
# Check service exists
kubectl get services -n staging

# Check endpoints (pods behind service)
kubectl get endpoints -n staging

# Test service from inside cluster
kubectl run test-pod --image=curlimages/curl -it --rm -- \
  curl http://auth-service:80/api/health
```

### RBAC Issues

```bash
# Check ServiceAccount exists
kubectl get serviceaccounts -n staging

# Check RoleBinding
kubectl get rolebindings -n staging

# Test permissions
kubectl auth can-i get configmaps \
  --as=system:serviceaccount:staging:auth-service-sa -n staging
```

### Configuration Issues

```bash
# Check ConfigMap
kubectl get configmap <name> -n staging -o yaml

# Check Secret (values are base64 encoded)
kubectl get secret <name> -n staging -o yaml

# Decode secret
kubectl get secret <name> -n staging -o jsonpath='{.data.key}' | base64 -d
```

---

## Next Steps

1. **Complete file splitting** - Finish splitting all files into staging/prod
2. **Set up database** - Deploy SQL Server in Kubernetes
3. **Build and push images** - Create Docker images for all services
4. **Set up Ingress** - Configure external access
5. **Set up monitoring** - Add logging and metrics
6. **Set up CI/CD** - Automate deployments
7. **Production hardening** - Network policies, resource quotas, etc.

---

## Additional Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Concepts](https://kubernetes.io/docs/concepts/)
- [RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

## Documentation Guide

### 📖 All Available Documents

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[LEARNING_PATH.md](./LEARNING_PATH.md)** | Complete learning guide | Start here! |
| **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** | Real-world analogies | First read - easiest to understand |
| **[CONCEPTS.md](./CONCEPTS.md)** | Deep dive into concepts | After analogies - detailed explanations |
| **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** | Advanced topics | After basics - Ingress, LoadBalancer, etc. |
| **[HELM_GUIDE.md](./HELM_GUIDE.md)** | Helm charts explained | Package management and templating |
| **[STORAGE_GUIDE.md](./STORAGE_GUIDE.md)** | Persistent storage | Databases and data persistence |
| **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** | How we implemented | See real-world decisions |
| **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** | Complete file reference | Reference guide for all files |
| **[README.md](./README.md)** | Overview and quick start | Quick reference and commands |

### 🗺️ Concept Coverage

**Basic Concepts:**
- Namespace → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#1-namespace) | [CONCEPTS.md](./CONCEPTS.md#namespace-deep-dive)
- RBAC → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#2-serviceaccount) | [CONCEPTS.md](./CONCEPTS.md#rbac-deep-dive)
- Deployment → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#7-deployment) | [CONCEPTS.md](./CONCEPTS.md#deployments-deep-dive)
- Service → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#8-service) | [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#service-discovery)
- ConfigMap → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#5-configmap) | [CONCEPTS.md](./CONCEPTS.md#configmaps-deep-dive)
- Secret → [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md#6-secret) | [CONCEPTS.md](./CONCEPTS.md#secrets-deep-dive)

**Advanced Concepts:**
- Pods & Nodes → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#pods-vs-containers)
- Service Discovery → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#service-discovery)
- Ingress → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#ingress)
- LoadBalancer → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#loadbalancer)
- Health Checks → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#health-checks)
- Resource Limits → [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md#resource-limits-and-requests)

**Package Management & Storage:**
- Helm Charts → [HELM_GUIDE.md](./HELM_GUIDE.md) - Complete Helm guide
- Persistent Storage → [STORAGE_GUIDE.md](./STORAGE_GUIDE.md) - PVCs, PVs, StorageClasses

### 🎓 Learning Paths

**Path 1: Complete Beginner**
1. [LEARNING_PATH.md](./LEARNING_PATH.md) - Overview
2. [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md) - Understand with analogies
3. [CONCEPTS.md](./CONCEPTS.md) - Deep dive
4. [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md) - Advanced topics
5. [HELM_GUIDE.md](./HELM_GUIDE.md) - Package management
6. [STORAGE_GUIDE.md](./STORAGE_GUIDE.md) - Persistent storage
7. [IMPLEMENTATION.md](./IMPLEMENTATION.md) - See how we did it
8. [FILE_REFERENCE.md](./FILE_REFERENCE.md) - Reference guide

**Path 2: Quick Understanding**
1. [LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md) - All concepts with analogies
2. [ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md) - Advanced topics
3. [FILE_REFERENCE.md](./FILE_REFERENCE.md) - File reference

**Path 3: Practical Implementation**
1. [IMPLEMENTATION.md](./IMPLEMENTATION.md) - How we did it
2. [FILE_REFERENCE.md](./FILE_REFERENCE.md) - File reference
3. [README.md](./README.md) - Commands and usage

---

## Summary

This guide covers:

✅ **What Kubernetes is** and why we use it
✅ **Key concepts** (Namespaces, RBAC, Deployments, Services, ConfigMaps, Secrets)
✅ **Our implementation** structure and organization
✅ **What each file does** and why it exists
✅ **How to use** the Kubernetes manifests
✅ **Best practices** for security, reliability, and maintainability
✅ **Troubleshooting** common issues

**Remember:** Kubernetes is powerful but complex. Start simple, test in staging, and gradually add features. Always test changes in staging before applying to production!
