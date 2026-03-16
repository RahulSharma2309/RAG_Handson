# Kubernetes Files Reference - FreshHarvest Market

> **Complete reference guide for all Kubernetes manifest files**

## Table of Contents

1. [Namespaces](#namespaces)
2. [RBAC Files](#rbac-files)
3. [ConfigMaps](#configmaps)
4. [Secrets](#secrets)
5. [Deployments](#deployments)
6. [Services](#services)

---

## Namespaces

### File: `infra/k8s/staging/namespaces/namespace.yaml`

**Purpose:** Creates the staging namespace

**What it does:**
- Creates isolated workspace for staging environment
- Allows resource organization
- Enables RBAC and resource quotas
- Provides environment separation

**Key Fields:**
```yaml
metadata:
  name: staging                    # Namespace name
  labels:
    environment: staging           # Environment label
    managed-by: freshharvest-market # Management label
    cost-center: qa               # Cost tracking label
  annotations:
    description: "Staging environment for final testing before production"
```

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/namespaces/
kubectl get namespace staging
```

---

### File: `infra/k8s/prod/namespaces/namespace.yaml`

**Purpose:** Creates the production namespace

**Same structure as staging, but:**
- `name: prod`
- `environment: production`
- `cost-center: operations`
- More restrictive annotations

---

## RBAC Files

### File: `infra/k8s/staging/rbac/service-accounts.yaml`

**Purpose:** Creates ServiceAccounts for all services in staging

**What it contains:**
- ServiceAccount for each service
- Labels and metadata
- Namespace: staging

**ServiceAccounts:**
1. `auth-service-sa`
2. `user-service-sa`
3. `product-service-sa`
4. `order-service-sa`
5. `payment-service-sa`
6. `gateway-sa`
7. `frontend-sa`

**Structure:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auth-service-sa
  namespace: staging
  labels:
    app: auth-service
    environment: staging
    managed-by: freshharvest-market
```

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/rbac/service-accounts.yaml
kubectl get serviceaccounts -n staging
```

---

### File: `infra/k8s/staging/rbac/roles.yaml`

**Purpose:** Defines permissions (Roles) for staging namespace

**What it contains:**
1. **service-role** - Read-only permissions
   - Read: ConfigMaps, Secrets, Services, Endpoints, Pods
   - Verbs: get, list, watch
   - Used by: Application services

2. **deployment-role** - Full permissions
   - Full access: Deployments, Services, ConfigMaps, Secrets, Pods
   - Read: Pod logs
   - Used by: CI/CD tools

**Structure:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: service-role
  namespace: staging
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
```

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/rbac/roles.yaml
kubectl get roles -n staging
kubectl describe role service-role -n staging
```

---

### File: `infra/k8s/staging/rbac/role-bindings.yaml`

**Purpose:** Connects ServiceAccounts to Roles

**What it contains:**
- RoleBinding for each service
- Links ServiceAccount to service-role
- One binding per service (7 total)

**Structure:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: auth-service-binding
  namespace: staging
subjects:
  - kind: ServiceAccount
    name: auth-service-sa
    namespace: staging
roleRef:
  kind: Role
  name: service-role
  apiGroup: rbac.authorization.k8s.io
```

**What it does:**
- Gives `auth-service-sa` the permissions defined in `service-role`
- Each service gets read-only permissions
- CI/CD tools can get deployment-role permissions

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/rbac/role-bindings.yaml
kubectl get rolebindings -n staging
kubectl describe rolebinding auth-service-binding -n staging
```

---

## ConfigMaps

### File: `infra/k8s/staging/configmaps/configmaps.yaml`

**Purpose:** Stores non-sensitive configuration for staging

**What it contains:**
- ConfigMap for each service
- Environment variables
- Log levels
- Application settings

**Services with ConfigMaps:**
1. `auth-service-config`
2. `user-service-config`
3. `product-service-config`
4. `order-service-config`
5. `payment-service-config`
6. `gateway-config`
7. `frontend-config`

**Structure:**
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

**Key Values:**
- `ASPNETCORE_ENVIRONMENT`: Development (staging) / Production (prod)
- `ASPNETCORE_URLS`: HTTP endpoint binding
- `Logging__LogLevel__Default`: Information (staging) / Warning (prod)

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/configmaps/
kubectl get configmaps -n staging
kubectl get configmap auth-service-config -n staging -o yaml
```

**How Deployments use it:**
```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: auth-service-config
        key: ASPNETCORE_ENVIRONMENT
```

---

### File: `infra/k8s/prod/configmaps/configmaps.yaml`

**Same structure as staging, but:**
- Environment: Production
- Log levels: Warning/Error (less verbose)
- Different values as needed

---

## Secrets

### File: `infra/k8s/staging/secrets/secrets.yaml`

**Purpose:** Stores sensitive data for staging

**What it contains:**
- Secret for each service's database connection
- Database passwords
- Connection strings

**Secrets:**
1. `database-secret` - Shared database credentials
2. `auth-service-db-secret` - Auth service database connection
3. `user-service-db-secret` - User service database connection
4. `product-service-db-secret` - Product service database connection
5. `order-service-db-secret` - Order service database connection
6. `payment-service-db-secret` - Payment service database connection

**Structure:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-service-db-secret
  namespace: staging
type: Opaque
stringData:
  ConnectionStrings__DefaultConnection: "Server=mssql-service,1433;Database=authdb;User Id=sa;Password=Your_password123;TrustServerCertificate=True;"
```

**⚠️ Security Notes:**
- Secrets are base64 encoded (not encrypted by default)
- Don't commit real production secrets to git
- Use cloud secret stores in production
- Kubernetes encrypts secrets at rest (if enabled)

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/secrets/
kubectl get secrets -n staging
kubectl get secret auth-service-db-secret -n staging -o yaml
```

**How Deployments use it:**
```yaml
env:
  - name: ConnectionStrings__DefaultConnection
    valueFrom:
      secretKeyRef:
        name: auth-service-db-secret
        key: ConnectionStrings__DefaultConnection
```

---

### File: `infra/k8s/prod/secrets/secrets.yaml`

**Same structure as staging, but:**
- ⚠️ **TODO:** Replace with production values
- Use proper secret management
- Never commit real secrets to git

---

## Deployments

### File: `infra/k8s/staging/deployments/<service>/deployment.yaml`

**Purpose:** Defines how to run each service

**Structure for each service:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <service-name>
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: <service-name>
  template:
    metadata:
      labels:
        app: <service-name>
    spec:
      serviceAccountName: <service-name>-sa
      containers:
        - name: <service-name>
          image: <service-name>:v1.0.0
          ports:
            - containerPort: 80
          env:
            # From ConfigMap
            - name: ASPNETCORE_ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: <service-name>-config
            # From Secret
            - name: ConnectionStrings__DefaultConnection
              valueFrom:
                secretKeyRef:
                  name: <service-name>-db-secret
          livenessProbe:
            httpGet:
              path: /api/health
              port: 80
          readinessProbe:
            httpGet:
              path: /api/health
              port: 80
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

**Services with Deployments:**
1. `auth-service`
2. `user-service`
3. `product-service`
4. `order-service`
5. `payment-service`
6. `gateway`
7. `frontend`

**Key Fields:**
- `replicas`: 2 (staging) / 3 (prod)
- `image`: Service image tag (v1.0.0)
- `serviceAccountName`: ServiceAccount to use
- `env`: Environment variables from ConfigMaps/Secrets
- `resources`: CPU and memory limits
- `livenessProbe`: Health check for container restart
- `readinessProbe`: Health check for traffic routing

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/deployments/<service>/
kubectl get deployments -n staging
kubectl describe deployment <service-name> -n staging
kubectl get pods -n staging
```

**Differences: Staging vs Production**

| Field | Staging | Production |
|-------|---------|------------|
| replicas | 2 | 3 |
| imagePullPolicy | IfNotPresent | Always |
| resource requests | 256Mi / 100m | 512Mi / 200m |
| resource limits | 512Mi / 500m | 1Gi / 1000m |
| environment | Development | Production |

---

## Services

### File: `infra/k8s/staging/deployments/<service>/service.yaml`

**Purpose:** Makes services accessible within cluster

**Structure:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
  namespace: staging
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
  selector:
    app: <service-name>
    environment: staging
```

**What it does:**
- Creates stable endpoint: `http://<service-name>:80`
- Routes traffic to pods with matching labels
- Load balances across replicas
- Provides DNS name for service discovery

**Service Types:**
- **ClusterIP** (default) - Internal only
  - Used by: All backend services
  - Access: `http://<service-name>:80` (within cluster)
- **NodePort** - Exposes on node IP
  - Used by: Frontend (for external access)
  - Access: `<node-ip>:30000` (from outside cluster)

**Usage:**
```bash
kubectl apply -f infra/k8s/staging/deployments/<service>/service.yaml
kubectl get services -n staging
kubectl get endpoints -n staging
```

**Service Discovery:**
```
Other services call:
  http://auth-service:80
  http://user-service:80
  http://product-service:80
  etc.
```

---

## File Relationships

### How Files Connect

```
Namespace (namespace.yaml)
  ├─> RBAC (service-accounts.yaml, roles.yaml, role-bindings.yaml)
  │     └─> Deployment (deployment.yaml) uses ServiceAccount
  ├─> ConfigMap (configmaps.yaml)
  │     └─> Deployment references ConfigMap values
  ├─> Secret (secrets.yaml)
  │     └─> Deployment references Secret values
  └─> Deployment (deployment.yaml)
        ├─> Uses ServiceAccount from RBAC
        ├─> References ConfigMap
        ├─> References Secret
        └─> Creates Pods
             └─> Service (service.yaml) routes traffic to Pods
```

### Application Order

**Recommended order for applying:**
1. Namespaces
2. RBAC (ServiceAccounts, Roles, RoleBindings)
3. ConfigMaps
4. Secrets
5. Deployments
6. Services (can be applied with Deployments)

**Example:**
```bash
# 1. Create namespace
kubectl apply -f infra/k8s/staging/namespaces/

# 2. Set up RBAC
kubectl apply -f infra/k8s/staging/rbac/

# 3. Create ConfigMaps
kubectl apply -f infra/k8s/staging/configmaps/

# 4. Create Secrets
kubectl apply -f infra/k8s/staging/secrets/

# 5. Create Deployments and Services
kubectl apply -f infra/k8s/staging/deployments/
```

---

## 📚 Related Documents

- **[LEARNING_PATH.md](./LEARNING_PATH.md)** - Complete learning guide
- **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** - Real-world analogies
- **[CONCEPTS.md](./CONCEPTS.md)** - Deep dive into concepts
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced topics
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s

---

## Summary

This reference covers:

✅ **Namespaces** - Environment isolation
✅ **RBAC Files** - ServiceAccounts, Roles, RoleBindings
✅ **ConfigMaps** - Non-sensitive configuration
✅ **Secrets** - Sensitive data
✅ **Deployments** - Application definitions
✅ **Services** - Service discovery and networking
✅ **File Relationships** - How files connect

**Key Takeaways:**
- Each file has a specific purpose
- Files reference each other
- Apply in correct order
- Separate staging/prod folders
- Use labels and namespaces for organization

**Quick Reference:**
- Namespace: Environment isolation
- RBAC: Security and access control
- ConfigMap: Configuration
- Secret: Sensitive data
- Deployment: Application runtime
- Service: Service discovery
