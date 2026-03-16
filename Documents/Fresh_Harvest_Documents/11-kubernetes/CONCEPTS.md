# Kubernetes Concepts - Deep Dive

> **Detailed explanation of all Kubernetes concepts used in FreshHarvest Market**

## Table of Contents

1. [Namespace Deep Dive](#namespace-deep-dive)
2. [RBAC Deep Dive](#rbac-deep-dive)
3. [Deployments Deep Dive](#deployments-deep-dive)
4. [Services Deep Dive](#services-deep-dive)
5. [ConfigMaps Deep Dive](#configmaps-deep-dive)
6. [Secrets Deep Dive](#secrets-deep-dive)
7. [Pods vs Containers](#pods-vs-containers)
8. [Service Discovery](#service-discovery)
9. [Health Checks](#health-checks)
10. [Resource Management](#resource-management)

---

## Namespace Deep Dive

### What is a Namespace?

A **namespace** provides a scope for names. Resources within a namespace must have unique names, but the same resource name can exist in different namespaces.

### Real-World Analogy

Think of namespaces like **separate office buildings**:

```
Building 1: Staging Office
├── Floor 1: auth-service team
├── Floor 2: user-service team
└── Floor 3: product-service team

Building 2: Production Office
├── Floor 1: auth-service team
├── Floor 2: user-service team
└── Floor 3: product-service team
```

- Each building is isolated
- Teams can have the same name in different buildings
- No confusion between buildings

### Why Namespaces Matter

1. **Prevent Accidents**
   ```bash
   # Without namespace: DANGEROUS!
   kubectl delete deployment auth-service
   # Which one? Staging? Production? 😱
   
   # With namespace: SAFE!
   kubectl delete deployment auth-service -n staging
   # Clear! Only staging ✅
   ```

2. **Resource Organization**
   - Group related resources together
   - Easy to see what belongs to staging vs production
   - Clean separation of concerns

3. **Access Control**
   - Different teams can have access to different namespaces
   - RBAC can be namespace-scoped
   - Security isolation

4. **Resource Quotas**
   - Set limits per namespace
   - Prevent one environment from using all resources
   - Cost tracking and allocation

### Our Namespaces

**Staging Namespace:**
- Purpose: Testing and QA
- Access: Developers, QA team
- Resources: Limited (lower replicas, smaller resource limits)

**Production Namespace:**
- Purpose: Live production environment
- Access: DevOps, SRE only
- Resources: Higher (more replicas, larger resource limits)

---

## RBAC Deep Dive

RBAC = **Role-Based Access Control**

### The Three Components

#### 1. ServiceAccount

**What it is:** An identity that pods use to authenticate to the Kubernetes API.

**Real-World Analogy:**
- Employee ID card
- Each service gets its own unique identity

**Why we need it:**
```yaml
# Without ServiceAccount:
Pod: "Hey Kubernetes API, I need to read ConfigMap"
Kubernetes: "Who are you?"
Pod: "Umm... I'm just a pod?"
Kubernetes: "Access denied!"

# With ServiceAccount:
Pod: "Hey Kubernetes API, I'm auth-service-sa"
Kubernetes: "Let me check your permissions..."
Kubernetes: "Access granted! You can read ConfigMaps"
```

**In our project:**
- Each service has its own ServiceAccount
- `auth-service-sa`, `user-service-sa`, etc.
- Used for authentication and auditing

#### 2. Role

**What it is:** Defines what permissions are allowed in a specific namespace.

**Structure:**
```yaml
Role:
  - Resources: ["configmaps", "secrets"]
  - Verbs: ["get", "list", "watch"]
```

**Key Concepts:**

**Resources:**
- What you can access (pods, services, configmaps, secrets, deployments, etc.)
- Grouped by API groups

**Verbs:**
- `get` - Read one specific resource
- `list` - Read all resources of this type
- `watch` - Monitor changes in real-time
- `create` - Create new resources
- `update` - Modify existing resources
- `patch` - Partially update resources
- `delete` - Remove resources

**API Groups:**
- `""` (empty) = Core Kubernetes API (pods, services, configmaps, secrets)
- `apps` = Apps API (deployments, replicasets, statefulsets)
- `rbac.authorization.k8s.io` = RBAC API (roles, rolebindings)

**Our Roles:**

1. **service-role** (for application services)
   - Read-only permissions
   - Can read: ConfigMaps, Secrets, Services, Endpoints, Pods
   - Cannot: Create, update, or delete anything

2. **deployment-role** (for CI/CD)
   - Full permissions
   - Can: Create, read, update, delete Deployments, Services, ConfigMaps, Secrets, Pods

#### 3. RoleBinding

**What it is:** Connects a ServiceAccount (or user) to a Role.

**Structure:**
```yaml
RoleBinding:
  subjects:      # WHO gets permissions
    - ServiceAccount: auth-service-sa
  roleRef:       # WHAT permissions they get
    - Role: service-role
```

**Real-World Analogy:**
- Like assigning a job to an employee
- "Give auth-service-sa the permissions defined in service-role"

**How it works:**
```
ServiceAccount (auth-service-sa)
    ↓
RoleBinding (connects them)
    ↓
Role (service-role - defines permissions)
```

---

## Deployments Deep Dive

### What is a Deployment?

A **Deployment** manages a set of identical pods. It ensures that a specified number of pods are running at any given time.

### Real-World Analogy

Think of a Deployment as a **manager in a factory**:

```
Manager (Deployment):
  "I need 3 workers (pods) doing job X"
  
Factory (Kubernetes):
  - Checks: Do we have 3 workers?
  - If not: Creates new workers
  - If too many: Stops extra workers
  - If a worker crashes: Creates replacement
  - Monitors: Are workers healthy?
```

### Deployment Components

#### 1. Replicas

```yaml
replicas: 2  # Run 2 copies of this service
```

**Why multiple replicas?**
- High availability (if one fails, others continue)
- Load distribution (spread traffic across pods)
- Zero-downtime updates (update one pod at a time)

**Our Replica Strategy:**
- Staging: 2 replicas per service
- Production: 3 replicas per service

#### 2. Selector

```yaml
selector:
  matchLabels:
    app: auth-service
```

**What it does:**
- Tells Deployment which pods it manages
- Must match pod labels
- Used by Service to find pods

#### 3. Template

```yaml
template:
  metadata:
    labels:
      app: auth-service
  spec:
    containers: ...
```

**What it does:**
- Defines how to create new pods
- Specifies container image, resources, environment variables
- Kubernetes uses this template to create pods

#### 4. Pod Template Spec

**Container Image:**
```yaml
containers:
  - name: auth-service
    image: auth-service:v1.0.0
    imagePullPolicy: Always
```

**Image Pull Policies:**
- `Always` - Always pull latest (production)
- `IfNotPresent` - Pull if not cached (staging/development)
- `Never` - Never pull (use local only)

**Environment Variables:**
```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: auth-service-config
        key: ASPNETCORE_ENVIRONMENT
  - name: ConnectionStrings__DefaultConnection
    valueFrom:
      secretKeyRef:
        name: auth-service-db-secret
        key: ConnectionStrings__DefaultConnection
```

**Resources:**
```yaml
resources:
  requests:      # Minimum guaranteed
    memory: "256Mi"
    cpu: "100m"
  limits:        # Maximum allowed
    memory: "512Mi"
    cpu: "500m"
```

**Why set resources?**
- Requests: Help Kubernetes schedule pods (needs at least X)
- Limits: Prevent pods from using all resources (can use at most Y)

**Health Checks:**

1. **Liveness Probe**
   - Checks if container is still running
   - If fails: Kubernetes restarts the container
   - Example: HTTP check on `/api/health`

2. **Readiness Probe**
   - Checks if container is ready to serve traffic
   - If fails: Service stops sending traffic to this pod
   - Example: HTTP check on `/api/health`

```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 80
  initialDelaySeconds: 30  # Wait 30s before first check
  periodSeconds: 10        # Check every 10s
  timeoutSeconds: 5        # Timeout after 5s
  failureThreshold: 3      # Restart after 3 failures
```

---

## Services Deep Dive

### What is a Service?

A **Service** provides a stable network endpoint for pods. Pods have ephemeral IPs (they change when restarted), but Services provide stable IPs and DNS names.

### Real-World Analogy

Think of a Service as a **phone book**:

```
Without Service:
- auth-service pod has IP: 10.244.1.5
- Pod crashes and restarts
- New IP: 10.244.2.8
- Other services: "Where did auth-service go?" 😱

With Service:
- Service name: auth-service
- Service IP: 10.96.0.1 (stable!)
- Pod crashes and restarts
- Service automatically updates to new pod IP
- Other services: "http://auth-service:80" (still works!) ✅
```

### How Services Work

1. **Service has a selector:**
   ```yaml
   selector:
     app: auth-service
   ```

2. **Service finds pods with matching labels:**
   - All pods with `app: auth-service` label
   - Service tracks their IPs

3. **Service provides stable endpoint:**
   - DNS name: `auth-service`
   - Service IP: Internal cluster IP
   - Port: 80

4. **Load balancing:**
   - Traffic to `http://auth-service:80` is distributed across all matching pods
   - Kubernetes handles load balancing automatically

### Service Types

1. **ClusterIP** (default)
   - Internal only (within cluster)
   - Accessible via: `http://service-name:port`
   - Used for: Service-to-service communication

2. **NodePort**
   - Exposes service on each node's IP
   - Accessible via: `<node-ip>:<node-port>`
   - Used for: External access (development/testing)

3. **LoadBalancer**
   - Cloud provider load balancer
   - Gets external IP from cloud provider
   - Used for: Production external access

4. **Ingress**
   - HTTP/HTTPS routing
   - Domain-based routing
   - Used for: Production (recommended)

**In our project:**
- Services use `ClusterIP` (internal communication)
- Frontend uses `NodePort` (external access)
- Future: Use Ingress for production

---

## ConfigMaps Deep Dive

### What is a ConfigMap?

A **ConfigMap** stores configuration data as key-value pairs. It's designed to store non-sensitive data.

### Why Use ConfigMaps?

**Without ConfigMap:**
```yaml
# Configuration hardcoded in Deployment
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: "Production"  # Hardcoded!
```

**Problems:**
- Need to rebuild image to change config
- Different configs for staging/prod require different images
- Config mixed with code

**With ConfigMap:**
```yaml
# Configuration in ConfigMap
ConfigMap:
  ASPNETCORE_ENVIRONMENT: "Production"

# Deployment references ConfigMap
env:
  - name: ASPNETCORE_ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: auth-service-config
        key: ASPNETCORE_ENVIRONMENT
```

**Benefits:**
- Change config without rebuilding image
- Same image for staging/prod (different ConfigMaps)
- Config separated from code
- Easy to update: `kubectl edit configmap`

### ConfigMap Structure

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

### Using ConfigMaps in Deployments

**Method 1: Individual Keys**
```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: auth-service-config
        key: ASPNETCORE_ENVIRONMENT
```

**Method 2: All Keys as Environment Variables**
```yaml
envFrom:
  - configMapRef:
      name: auth-service-config
```

**Method 3: As Volume Mount**
```yaml
volumes:
  - name: config
    configMap:
      name: auth-service-config
volumeMounts:
  - name: config
    mountPath: /etc/config
```

---

## Secrets Deep Dive

### What is a Secret?

A **Secret** stores sensitive data like passwords, API keys, and certificates. Similar to ConfigMap, but for sensitive data.

### Why Use Secrets?

**Never do this:**
```yaml
# DON'T DO THIS!
env:
  - name: DB_PASSWORD
    value: "MyPassword123"  # Exposed in YAML! 😱
```

**Use Secrets:**
```yaml
# Secret stores sensitive data
Secret:
  DB_PASSWORD: "MyPassword123"  # Encrypted at rest

# Deployment references Secret
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: database-secret
        key: DB_PASSWORD
```

### Secret Security

**Important Notes:**
1. **Base64 Encoded (not encrypted by default)**
   - Secrets are base64 encoded in YAML
   - Can be decoded: `echo <base64> | base64 -d`
   - **Don't commit real secrets to git!**

2. **Encrypted at Rest (if enabled)**
   - Kubernetes can encrypt secrets at rest (etcd encryption)
   - Requires enabling encryption at rest

3. **In Production:**
   - Use cloud secret stores (Azure Key Vault, AWS Secrets Manager, etc.)
   - Use sealed-secrets or external-secrets operators
   - Never hardcode secrets

### Secret Structure

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-service-db-secret
  namespace: staging
type: Opaque
stringData:  # Kubernetes encodes to base64 automatically
  ConnectionStrings__DefaultConnection: "Server=mssql;Database=authdb;..."
```

**Types:**
- `Opaque` - Arbitrary user-defined data (default)
- `kubernetes.io/dockerconfigjson` - Docker registry credentials
- `kubernetes.io/tls` - TLS certificate and key
- `kubernetes.io/service-account-token` - Service account token

### Using Secrets in Deployments

**Method 1: Individual Keys**
```yaml
env:
  - name: ConnectionStrings__DefaultConnection
    valueFrom:
      secretKeyRef:
        name: auth-service-db-secret
        key: ConnectionStrings__DefaultConnection
```

**Method 2: All Keys as Environment Variables**
```yaml
envFrom:
  - secretRef:
      name: auth-service-db-secret
```

**Method 3: As Volume Mount**
```yaml
volumes:
  - name: secrets
    secret:
      secretName: auth-service-db-secret
volumeMounts:
  - name: secrets
    mountPath: /etc/secrets
    readOnly: true
```

---

## Pods vs Containers

### Container

- **What it is:** A running instance of a Docker image
- **Example:** `docker run nginx`
- **Lifecycle:** Managed by Docker/container runtime

### Pod

- **What it is:** Smallest deployable unit in Kubernetes
- **Contains:** One or more containers
- **Lifecycle:** Managed by Kubernetes

### Relationship

```
Pod (Kubernetes)
└── Container (Docker)
    └── Application (Your code)
```

**Key Points:**
- Pod = Wrapper around containers
- Usually one container per pod
- Multiple containers in one pod share network and storage
- Pods are ephemeral (can be recreated)

---

## Service Discovery

### How Services Find Each Other

**Within Kubernetes Cluster:**

1. **DNS-based Discovery:**
   ```
   Service name: auth-service
   Namespace: staging
   DNS name: auth-service.staging.svc.cluster.local
   Short name: auth-service (in same namespace)
   ```

2. **Environment Variables:**
   ```
   AUTH_SERVICE_SERVICE_HOST=10.96.0.1
   AUTH_SERVICE_SERVICE_PORT=80
   ```

**In our project:**
- Services call: `http://auth-service:80`
- Kubernetes DNS resolves to service IP
- Service routes to healthy pods

---

## Health Checks

### Why Health Checks?

Kubernetes needs to know:
- Is the container still running? (Liveness)
- Is the container ready to serve traffic? (Readiness)

### Types of Health Checks

1. **Liveness Probe**
   - Purpose: Is container alive?
   - Action if fails: Restart container
   - Example: HTTP GET `/api/health`

2. **Readiness Probe**
   - Purpose: Is container ready?
   - Action if fails: Remove from Service (stop sending traffic)
   - Example: HTTP GET `/api/health`

3. **Startup Probe**
   - Purpose: Has container started?
   - Action if fails: Restart container
   - Used for: Slow-starting containers

### Probe Types

**HTTP GET:**
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 80
```

**TCP Socket:**
```yaml
livenessProbe:
  tcpSocket:
    port: 80
```

**Exec Command:**
```yaml
livenessProbe:
  exec:
    command:
      - cat
      - /tmp/healthy
```

### Our Implementation

```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 80
  initialDelaySeconds: 30  # Wait 30s after container starts
  periodSeconds: 10        # Check every 10s
  timeoutSeconds: 5        # Timeout after 5s
  failureThreshold: 3      # Restart after 3 consecutive failures

readinessProbe:
  httpGet:
    path: /api/health
    port: 80
  initialDelaySeconds: 10  # Wait 10s after container starts
  periodSeconds: 5         # Check every 5s
  timeoutSeconds: 3        # Timeout after 3s
  failureThreshold: 3      # Mark not ready after 3 failures
```

---

## Resource Management

### Resource Requests and Limits

**Requests:**
- Minimum resources guaranteed to the pod
- Used for scheduling (Kubernetes finds nodes with enough resources)
- Example: `requests: { cpu: "100m", memory: "256Mi" }`

**Limits:**
- Maximum resources pod can use
- Prevents resource exhaustion
- Example: `limits: { cpu: "500m", memory: "512Mi" }`

### CPU Units

- `1000m` = 1 CPU core
- `500m` = 0.5 CPU core
- `100m` = 0.1 CPU core

### Memory Units

- `1Gi` = 1024 MiB
- `512Mi` = 512 MiB
- `256Mi` = 256 MiB

### Our Resource Strategy

**Staging:**
- Requests: Lower (CPU: 100m, Memory: 256Mi)
- Limits: Moderate (CPU: 500m, Memory: 512Mi)
- Reason: Cost optimization, testing doesn't need full resources

**Production:**
- Requests: Higher (CPU: 200m, Memory: 512Mi)
- Limits: Higher (CPU: 1000m, Memory: 1Gi)
- Reason: Performance, reliability, user traffic

### Best Practices

1. **Always set both requests and limits**
   - Requests: Help with scheduling
   - Limits: Prevent resource exhaustion

2. **Set limits = 2x requests (guideline)**
   - Allows bursts
   - Prevents over-commitment

3. **Monitor actual usage**
   - Adjust based on metrics
   - Don't over-provision

4. **Different limits for staging/prod**
   - Staging: Lower (cost optimization)
   - Production: Higher (performance)

---

## 📚 Related Documents

- **[LEARNING_PATH.md](./LEARNING_PATH.md)** - Complete learning guide
- **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** - Real-world analogies (easier to understand)
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced topics (Ingress, LoadBalancer, Pods, Nodes)
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference

---

## Summary

This deep dive covered:

✅ **Namespaces** - Virtual clusters for isolation
✅ **RBAC** - Security (ServiceAccounts, Roles, RoleBindings)
✅ **Deployments** - Managing pods and applications
✅ **Services** - Service discovery and load balancing
✅ **ConfigMaps** - Non-sensitive configuration
✅ **Secrets** - Sensitive data management
✅ **Pods vs Containers** - Understanding the relationship
✅ **Service Discovery** - How services find each other
✅ **Health Checks** - Liveness and readiness probes
✅ **Resource Management** - CPU and memory limits

**Key Takeaways:**
- Kubernetes provides powerful abstractions
- Each concept has a specific purpose
- Understanding these concepts is key to using Kubernetes effectively
- Start simple, add complexity as needed
