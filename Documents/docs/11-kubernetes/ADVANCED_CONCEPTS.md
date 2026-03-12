# Advanced Kubernetes Concepts - Complete Guide

> **Understanding Pods, Nodes, Service Discovery, Ingress, LoadBalancer, and more using real-world analogies**

This document covers advanced Kubernetes concepts with practical examples from the FreshHarvest Market project.

---

## 📚 Table of Contents

1. [Pods vs Containers](#pods-vs-containers)
2. [Nodes](#nodes)
3. [Service Discovery](#service-discovery)
4. [Ingress](#ingress)
5. [LoadBalancer](#loadbalancer)
6. [NodePort](#nodeport)
7. [ClusterIP](#clusterip)
8. [Egress](#egress)
9. [ReplicaSet](#replicaset)
10. [StatefulSet vs Deployment](#statefulset-vs-deployment)
11. [ConfigMap vs Secret](#configmap-vs-secret)
12. [Resource Limits and Requests](#resource-limits-and-requests)
13. [Health Checks](#health-checks)
14. [Labels and Selectors](#labels-and-selectors)
15. [Annotations](#annotations)

---

## 🎯 Pods vs Containers

### Real-World Analogy

Think of a **Container** as a **shipping container** and a **Pod** as a **truck**:

```
🚚 Truck (Pod)
├── 📦 Container 1: auth-service (your application)
├── 📦 Container 2: sidecar (logging, monitoring) - optional
└── 🏷️ License plate: Pod name and labels
```

### What's the Difference?

| Concept        | Analogy                   | What It Is                           |
| -------------- | ------------------------- | ------------------------------------ |
| **Container**  | Shipping container        | The actual application code running  |
| **Pod**        | Truck carrying containers | Kubernetes unit that runs containers |
| **Deployment** | Fleet manager             | Manages multiple trucks (pods)       |

### In FreshHarvest Market

```yaml
# Deployment creates Pods
spec:
  replicas: 2 # Create 2 trucks (pods)
  template:
    spec:
      containers:
        - name: auth-service # Container inside the pod
          image: auth-service:v1.0.0
```

**Key Points:**

- **Pod** = Smallest deployable unit in Kubernetes
- **Container** = What runs inside the pod
- One pod can have multiple containers (sidecar pattern)
- Pods are ephemeral (can be created/destroyed)
- Deployment manages pod lifecycle

**Significance:** Pods are what actually run your application. Deployment creates and manages pods.

---

## 🖥️ Nodes

### Real-World Analogy

Think of a **Node** as a **physical server/computer** in your data center:

```
🏢 Data Center (Kubernetes Cluster)
├── 🖥️ Node 1 (Worker Node)
│   ├── Pod: auth-service-1
│   ├── Pod: user-service-1
│   └── Pod: product-service-1
├── 🖥️ Node 2 (Worker Node)
│   ├── Pod: auth-service-2
│   ├── Pod: order-service-1
│   └── Pod: payment-service-1
└── 🖥️ Node 3 (Master Node)
    └── Kubernetes Control Plane
```

### Types of Nodes

| Node Type       | Analogy          | What It Does                     |
| --------------- | ---------------- | -------------------------------- |
| **Master Node** | Building manager | Controls and manages the cluster |
| **Worker Node** | Office floor     | Runs your applications (pods)    |

### In FreshHarvest Market

When you deploy `auth-service` with `replicas: 2`:

```
Node 1: auth-service-pod-1
Node 2: auth-service-pod-2
```

Kubernetes distributes pods across nodes for:

- **High Availability:** If Node 1 fails, Node 2 still has a pod
- **Load Distribution:** Spreads work across nodes
- **Resource Optimization:** Uses available resources efficiently

**Significance:** Nodes are the physical/virtual machines that run your pods. Kubernetes manages pod placement across nodes.

---

## 🔍 Service Discovery

### Real-World Analogy

Think of **Service Discovery** as a **phone directory** or **reception desk**:

```
📞 Phone Directory (Service Discovery)
├── Name: auth-service
├── Number: http://auth-service:80
├── Routes to: Available pods
└── Load balancing: Distributes calls
```

### How It Works

**Without Service Discovery:**

```
❌ user-service: "I need auth-service, but where is it?"
   - Pod IP: 10.244.1.5 (changes when pod restarts!)
   - Pod IP: 10.244.2.3 (changes when pod restarts!)
   - Which one? What if it moves?
```

**With Service Discovery:**

```
✅ user-service: "I need auth-service"
   → DNS lookup: auth-service
   → Service: "Here's the stable address: http://auth-service:80"
   → Routes to: Available pod (load balanced)
```

### In FreshHarvest Market

**Service Definition:**

```yaml
# staging/deployments/auth-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service # This is the stable name!
spec:
  selector:
    app: auth-service # Routes to pods with this label
  ports:
    - port: 80
```

**How Other Services Use It:**

```yaml
# In user-service deployment
env:
  - name: ServiceUrls__AuthService
    value: "http://auth-service:80" # Stable DNS name!
```

**Key Points:**

- **Service** creates a stable DNS name
- Pods can come and go, but service name stays the same
- Kubernetes DNS resolves `auth-service` to the service IP
- Service load balances across multiple pods

**Significance:** Service Discovery makes services findable and accessible by name, not by changing IP addresses!

---

## 🌐 Ingress

### Real-World Analogy

Think of **Ingress** as a **receptionist at the building entrance**:

```
🏢 Office Building
├── 🚪 Front Door (Ingress)
│   ├── Routes: "API calls? Go to gateway"
│   ├── Routes: "Website? Go to frontend"
│   └── Security: "Check SSL certificates"
└── 🏢 Inside Building (Cluster)
    ├── gateway (internal)
    ├── frontend (internal)
    └── All other services (internal)
```

### What Ingress Does

| Feature                | Analogy                                 | What It Does                                 |
| ---------------------- | --------------------------------------- | -------------------------------------------- |
| **Routing**            | Receptionist directing visitors         | Routes external traffic to internal services |
| **SSL/TLS**            | Security guard checking IDs             | Terminates SSL certificates                  |
| **Load Balancing**     | Multiple reception desks                | Distributes traffic across services          |
| **Path-based Routing** | "API calls go here, website goes there" | Routes based on URL path                     |

### In FreshHarvest Market

**Example Ingress Configuration:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: freshharvest-market-ingress
  namespace: staging
spec:
  tls:
    - hosts:
        - api.staging.freshharvest-market.com
      secretName: tls-secret
  rules:
    - host: api.staging.freshharvest-market.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: gateway
                port:
                  number: 80
```

**How It Works:**

```
External Request: https://api.staging.freshharvest-market.com/api/auth/login
         ↓
Ingress Controller: "This is for /api path"
         ↓
Routes to: gateway service
         ↓
Gateway routes to: auth-service
```

**Key Points:**

- **Ingress** = Entry point for external traffic
- Handles SSL/TLS termination
- Routes based on domain name and path
- Only needed for external access (not for internal service-to-service)

**Significance:** Ingress is how external users access your application. It's the "front door" of your cluster.

---

## ⚖️ LoadBalancer

### Real-World Analogy

Think of **LoadBalancer** as a **traffic controller at a busy intersection**:

```
🚦 Traffic Controller (LoadBalancer)
├── External IP: 203.0.113.10
├── Routes to: Multiple services
└── Distributes: Traffic evenly
```

### What LoadBalancer Does

| Feature                  | Analogy                   | What It Does                        |
| ------------------------ | ------------------------- | ----------------------------------- |
| **External IP**          | Public address            | Gets a public IP address            |
| **Traffic Distribution** | Traffic controller        | Distributes traffic across services |
| **Cloud Integration**    | Works with cloud provider | Creates cloud load balancer         |

### In FreshHarvest Market

**LoadBalancer Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gateway-lb
  namespace: staging
spec:
  type: LoadBalancer # Creates external load balancer
  ports:
    - port: 80
      targetPort: 80
  selector:
    app: gateway
```

**How It Works:**

```
External User: http://203.0.113.10
         ↓
Cloud Load Balancer (AWS ELB, Azure LB, GCP LB)
         ↓
Routes to: gateway service
         ↓
Gateway routes to: Backend services
```

**Key Points:**

- **LoadBalancer** = Gets a public IP address
- Cloud provider creates actual load balancer
- More expensive than ClusterIP (uses cloud resources)
- Usually used with Ingress Controller

**Significance:** LoadBalancer provides external access with a public IP. Often used for production environments.

---

## 🔌 NodePort

### Real-World Analogy

Think of **NodePort** as a **specific door number on every building**:

```
🏢 Office Building
├── Door 1: NodePort 30001 → gateway
├── Door 2: NodePort 30002 → frontend
└── Every node has these doors
```

### What NodePort Does

| Feature           | Analogy                              | What It Does                                      |
| ----------------- | ------------------------------------ | ------------------------------------------------- |
| **Static Port**   | Door number                          | Opens a specific port (30000-32767) on every node |
| **Direct Access** | "Go to any building, use door 30001" | Access service via `<node-ip>:<port>`             |
| **Development**   | Quick access for testing             | Useful for development/testing                    |

### In FreshHarvest Market

**NodePort Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gateway-nodeport
  namespace: staging
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30001 # Access via <node-ip>:30001
  selector:
    app: gateway
```

**How It Works:**

```
External User: http://<any-node-ip>:30001
         ↓
NodePort Service
         ↓
Routes to: gateway service
```

**Key Points:**

- **NodePort** = Opens port on every node
- Port range: 30000-32767
- Access via `<node-ip>:<port>`
- Good for development, not recommended for production

**Significance:** NodePort provides quick external access for testing. Not ideal for production (use Ingress + LoadBalancer).

---

## 🏠 ClusterIP

### Real-World Analogy

Think of **ClusterIP** as an **internal phone extension**:

```
🏢 Office Building (Cluster)
├── Internal Extension: auth-service:80
├── Only works: Inside the building
└── Cannot call: From outside
```

### What ClusterIP Does

| Feature           | Analogy            | What It Does                   |
| ----------------- | ------------------ | ------------------------------ |
| **Internal Only** | Internal extension | Only accessible within cluster |
| **Stable IP**     | Extension number   | Gets a stable internal IP      |
| **Default Type**  | Most common        | Default service type           |

### In FreshHarvest Market

**ClusterIP Service (Default):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: staging
spec:
  type: ClusterIP # Default - can be omitted
  ports:
    - port: 80
  selector:
    app: auth-service
```

**How It Works:**

```
Internal Service: user-service
         ↓
Calls: http://auth-service:80
         ↓
ClusterIP Service
         ↓
Routes to: auth-service pods
```

**Key Points:**

- **ClusterIP** = Internal service (default)
- Only accessible within cluster
- Most services use this type
- No external access

**Significance:** ClusterIP is the default and most common service type. Used for internal service-to-service communication.

---

## 📤 Egress

### Real-World Analogy

Think of **Egress** as **outgoing mail/phone calls** from your office:

```
🏢 Office Building
├── 📤 Outgoing Calls (Egress)
│   ├── To: External APIs
│   ├── To: Database (external)
│   └── To: Third-party services
└── 🔒 Security: Network policies control what can leave
```

### What Egress Does

| Feature              | Analogy         | What It Does                                  |
| -------------------- | --------------- | --------------------------------------------- |
| **Outbound Traffic** | Outgoing calls  | Controls traffic leaving the cluster          |
| **Network Policies** | Security rules  | Defines what can connect to external services |
| **Default Behavior** | Usually allowed | By default, pods can reach external services  |

### In FreshHarvest Market

**Egress Network Policy:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: auth-service-egress
  namespace: staging
spec:
  podSelector:
    matchLabels:
      app: auth-service
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: staging
      ports:
        - protocol: TCP
          port: 80
    - to: [] # Allow all external traffic
```

**Key Points:**

- **Egress** = Outbound traffic (leaving cluster)
- Network Policies control egress
- By default, pods can reach external services
- Can restrict for security

**Significance:** Egress controls what your pods can connect to outside the cluster. Important for security.

---

## 🔄 ReplicaSet

### Real-World Analogy

Think of **ReplicaSet** as a **template for hiring employees**:

```
👥 HR Template (ReplicaSet)
├── Template: "We need employees matching this description"
├── Desired: 2 employees
├── Current: 2 employees ✅
└── If one leaves: Hire a replacement
```

### What ReplicaSet Does

| Feature                | Analogy                                | What It Does                       |
| ---------------------- | -------------------------------------- | ---------------------------------- |
| **Template**           | Job description                        | Defines what pods should look like |
| **Replica Management** | "Always have 2 employees"              | Ensures desired number of pods     |
| **Auto-recovery**      | "If employee leaves, hire replacement" | Creates new pod if one fails       |

### Relationship: Deployment → ReplicaSet → Pods

```
Deployment (Manager)
    ↓ manages
ReplicaSet (Template)
    ↓ creates
Pods (Actual workers)
```

### In FreshHarvest Market

**Deployment creates ReplicaSet:**

```yaml
# Deployment
spec:
  replicas: 2 # Desired number
  template:
    # This becomes the ReplicaSet template
    spec:
      containers:
        - name: auth-service
```

**What Happens:**

1. Deployment creates ReplicaSet
2. ReplicaSet creates 2 pods
3. If a pod dies, ReplicaSet creates a new one
4. Deployment manages ReplicaSet updates

**Key Points:**

- **ReplicaSet** = Ensures desired number of pods
- Created automatically by Deployment
- Manages pod lifecycle
- You rarely create ReplicaSet directly (Deployment does it)

**Significance:** ReplicaSet ensures you always have the right number of pods running. Deployment uses ReplicaSet under the hood.

---

## 📦 StatefulSet vs Deployment

### Real-World Analogy

**Deployment** = **Regular employees** (interchangeable)
**StatefulSet** = **Employees with assigned desks** (order matters)

```
👥 Deployment (Stateless)
├── Employee 1: Can sit anywhere
├── Employee 2: Can sit anywhere
└── Order doesn't matter

👥 StatefulSet (Stateful)
├── Employee 1: Assigned Desk A (has files)
├── Employee 2: Assigned Desk B (has files)
└── Order matters - can't swap desks
```

### Comparison

| Feature       | Deployment                   | StatefulSet                              |
| ------------- | ---------------------------- | ---------------------------------------- |
| **Use Case**  | Stateless apps               | Stateful apps (databases)                |
| **Pod Names** | Random (auth-service-abc123) | Ordered (auth-service-0, auth-service-1) |
| **Storage**   | Shared/Ephemeral             | Persistent per pod                       |
| **Scaling**   | Any order                    | Ordered (0, 1, 2...)                     |
| **Example**   | Web services                 | Databases, message queues                |

### In FreshHarvest Market

**Deployment (Current Setup):**

```yaml
# All services use Deployment (stateless)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 2
  # Pods: auth-service-abc123, auth-service-xyz789
```

**StatefulSet (If we had a database):**

```yaml
# If we deployed our own database
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mssql
spec:
  replicas: 3
  # Pods: mssql-0, mssql-1, mssql-2 (ordered!)
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
```

**Key Points:**

- **Deployment** = For stateless applications (our services)
- **StatefulSet** = For stateful applications (databases)
- FreshHarvest Market uses Deployment (services are stateless)

**Significance:** Use Deployment for stateless apps, StatefulSet for databases or apps that need ordered scaling.

---

## 🔐 ConfigMap vs Secret

### Real-World Analogy

**ConfigMap** = **Office manual** (anyone can read)
**Secret** = **Locked safe** (only authorized access)

```
📄 ConfigMap (Public)
├── Office hours: 9 AM - 5 PM
├── Log level: Information
└── Anyone can read

🔒 Secret (Private)
├── Database password: ********
├── API keys: ********
└── Only authorized can access
```

### Comparison

| Feature        | ConfigMap               | Secret           |
| -------------- | ----------------------- | ---------------- |
| **Data Type**  | Non-sensitive           | Sensitive        |
| **Storage**    | Plain text              | Base64 encoded   |
| **Access**     | Anyone with read access | Restricted       |
| **Example**    | Log levels, URLs        | Passwords, keys  |
| **Encryption** | At rest (optional)      | At rest (always) |

### In FreshHarvest Market

**ConfigMap:**

```yaml
# staging/configmaps/configmaps.yaml
data:
  ASPNETCORE_ENVIRONMENT: "Development"
  ASPNETCORE_URLS: "http://+:80"
  Logging__LogLevel__Default: "Information"
```

**Secret:**

```yaml
# staging/secrets/secrets.yaml
stringData:
  ConnectionStrings__DefaultConnection: "Server=...;Password=***;"
```

**Key Points:**

- **ConfigMap** = Non-sensitive configuration
- **Secret** = Sensitive data (passwords, keys)
- Both can be referenced in Deployments
- Secrets are base64 encoded (not encrypted, but obfuscated)

**Significance:** Always use Secrets for sensitive data. Never put passwords in ConfigMaps!

---

## 💻 Resource Limits and Requests

### Real-World Analogy

Think of **Resources** as **desk space and computer power**:

```
🖥️ Employee Desk (Pod)
├── Requested: "I need at least 256MB memory, 100m CPU"
├── Limit: "Maximum 512MB memory, 500m CPU"
└── Guaranteed: Gets at least what's requested
```

### What They Mean

| Term        | Analogy                        | What It Does                              |
| ----------- | ------------------------------ | ----------------------------------------- |
| **Request** | "Minimum desk space I need"    | Guaranteed resources                      |
| **Limit**   | "Maximum desk space I can use" | Hard cap on resources                     |
| **CPU**     | "Processing power"             | Measured in cores (100m = 0.1 core)       |
| **Memory**  | "RAM"                          | Measured in bytes (256Mi = 256 megabytes) |

### In FreshHarvest Market

**Resource Configuration:**

```yaml
# staging/deployments/auth-service/deployment.yaml
resources:
  requests:
    memory: "256Mi" # Guaranteed minimum
    cpu: "100m" # Guaranteed minimum
  limits:
    memory: "512Mi" # Maximum allowed
    cpu: "500m" # Maximum allowed
```

**What Happens:**

- **Request:** Kubernetes guarantees at least 256Mi memory, 100m CPU
- **Limit:** Pod cannot use more than 512Mi memory, 500m CPU
- If pod exceeds limit: Kubernetes kills it (OOMKilled)

**Key Points:**

- **Request** = Guaranteed resources
- **Limit** = Maximum resources
- Helps with scheduling (Kubernetes finds nodes with enough resources)
- Prevents one pod from consuming all resources

**Significance:** Resource limits prevent resource starvation. Requests help Kubernetes schedule pods efficiently.

---

## ❤️ Health Checks

### Real-World Analogy

Think of **Health Checks** as **employee wellness checks**:

```
👤 Employee (Pod)
├── Liveness Probe: "Are you alive?" (every 10 seconds)
│   └── If no: Fire and hire replacement
└── Readiness Probe: "Are you ready to work?" (every 5 seconds)
    └── If no: Don't send work until ready
```

### Types of Health Checks

| Type                | Analogy                      | What It Does                     |
| ------------------- | ---------------------------- | -------------------------------- |
| **Liveness Probe**  | "Is employee alive?"         | Checks if pod is running         |
| **Readiness Probe** | "Is employee ready to work?" | Checks if pod can accept traffic |
| **Startup Probe**   | "Is employee starting up?"   | Checks if pod is starting        |

### In FreshHarvest Market

**Health Check Configuration:**

```yaml
# staging/deployments/auth-service/deployment.yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 80
  initialDelaySeconds: 30 # Wait 30s before first check
  periodSeconds: 10 # Check every 10s
  timeoutSeconds: 5 # 5s timeout
  failureThreshold: 3 # Kill after 3 failures

readinessProbe:
  httpGet:
    path: /api/health
    port: 80
  initialDelaySeconds: 10 # Wait 10s before first check
  periodSeconds: 5 # Check every 5s
  failureThreshold: 3 # Remove from service after 3 failures
```

**What Happens:**

1. **Liveness Probe fails:** Kubernetes kills pod, creates new one
2. **Readiness Probe fails:** Kubernetes removes pod from service (no traffic)
3. **Both pass:** Pod receives traffic normally

**Key Points:**

- **Liveness** = Is pod alive? (restart if not)
- **Readiness** = Can pod handle traffic? (remove from service if not)
- Prevents sending traffic to unhealthy pods
- Auto-recovery for crashed pods

**Significance:** Health checks ensure only healthy pods receive traffic. Critical for reliability!

---

## 🏷️ Labels and Selectors

### Real-World Analogy

Think of **Labels** as **name tags** and **Selectors** as **search filters**:

```
👤 Employee Name Tags (Labels)
├── Name: auth-service
├── Department: backend
├── Environment: staging
└── Team: authentication

🔍 Search Filter (Selector)
├── Find: app=auth-service
├── Find: environment=staging
└── Result: All pods matching these labels
```

### How They Work

**Labels (on Pods):**

```yaml
metadata:
  labels:
    app: auth-service
    environment: staging
    managed-by: freshharvest-market
```

**Selector (in Service):**

```yaml
spec:
  selector:
    app: auth-service
    environment: staging
  # Routes to all pods with these labels
```

### In FreshHarvest Market

**Labels Used:**

- `app: auth-service` - Which service
- `environment: staging` - Which environment
- `managed-by: freshharvest-market` - Who manages it

**Selectors Used:**

- Service selector: Routes to pods with matching labels
- Deployment selector: Manages pods with matching labels

**Key Points:**

- **Labels** = Tags for organizing resources
- **Selectors** = Filters to find resources
- Services use selectors to find pods
- Deployments use selectors to manage pods

**Significance:** Labels and selectors are how Kubernetes connects resources together. Essential for service discovery!

---

## 📝 Annotations

### Real-World Analogy

Think of **Annotations** as **sticky notes** with extra information:

```
📄 Sticky Note (Annotation)
├── "Last updated: 2024-01-15"
├── "Managed by: CI/CD pipeline"
└── "Documentation: https://..."
```

### What Annotations Are

| Feature               | Analogy               | What It Does              |
| --------------------- | --------------------- | ------------------------- |
| **Metadata**          | Sticky notes          | Additional information    |
| **Not for Selection** | Can't search by these | Not used for filtering    |
| **Tooling**           | For external tools    | Used by monitoring, CI/CD |

### In FreshHarvest Market

**Example Annotations:**

```yaml
metadata:
  annotations:
    description: "Staging environment for final testing"
    last-updated: "2024-01-15"
    managed-by: "freshharvest-market-ci"
```

**Key Points:**

- **Annotations** = Extra metadata (not for selection)
- **Labels** = For selection and filtering
- Annotations are for humans and tools
- Labels are for Kubernetes

**Significance:** Annotations provide additional context. Labels are for Kubernetes, annotations are for humans/tools.

---

## 🔗 How Everything Connects

### Complete Flow Diagram

```
External User
    ↓
Ingress (Entry Point)
    ↓
LoadBalancer (Public IP)
    ↓
Service (Service Discovery)
    ↓
Deployment (Manages Pods)
    ↓
ReplicaSet (Ensures Replicas)
    ↓
Pods (Running on Nodes)
    ├── Uses: ConfigMap (Configuration)
    ├── Uses: Secret (Passwords)
    ├── Uses: ServiceAccount (Identity)
    └── Health Checks: Liveness + Readiness
```

### In FreshHarvest Market Context

```
1. User → https://api.staging.freshharvest-market.com/api/auth/login
2. Ingress → Routes to gateway service
3. Gateway Service → Routes to auth-service pod
4. Auth-Service Pod:
   - Uses ConfigMap (log levels, URLs)
   - Uses Secret (database password)
   - Uses ServiceAccount (identity)
   - Health checks running
5. Response → Back to user
```

---

## 📚 Related Documents

- **[LAYMAN_ANALOGY.md](./LAYMAN_ANALOGY.md)** - Basic concepts with office building analogy
- **[CONCEPTS.md](./CONCEPTS.md)** - Deep dive into core concepts
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference

---

## 🎯 Key Takeaways

1. **Pods** = Smallest unit, run containers
2. **Nodes** = Physical/virtual machines
3. **Service Discovery** = How services find each other
4. **Ingress** = Entry point for external traffic
5. **LoadBalancer** = Public IP for external access
6. **ClusterIP** = Internal service (default)
7. **Deployment** = Manages stateless apps
8. **StatefulSet** = Manages stateful apps (databases)
9. **Resources** = CPU/Memory limits and requests
10. **Health Checks** = Ensure pods are healthy
11. **Labels/Selectors** = How resources connect

---

This completes the advanced concepts! See other documents for more details. 🚀
