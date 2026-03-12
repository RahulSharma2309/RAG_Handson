# Local Kubernetes Deployment - Deep Learning Guide

> **Purpose**: Understand the **why** and **how** behind every step in [TODO.md](./TODO.md)

This guide provides low-level explanations, concepts, and context for each phase of the local Kubernetes setup with ArgoCD.

---

## Table of Contents

1. [Phase 1: Prerequisites & Environment Setup](#phase-1-prerequisites--environment-setup)
2. [Phase 2: Kubernetes Namespace & RBAC Setup](#phase-2-kubernetes-namespace--rbac-setup)
3. [Phase 3: Install ArgoCD](#phase-3-install-argocd)
4. [Phase 4: Configure Kubernetes Resources](#phase-4-configure-kubernetes-resources)
5. [Phase 5: Setup ArgoCD Applications](#phase-5-setup-argocd-applications)
6. [Phase 6: Install and Configure Ingress](#phase-6-install-and-configure-ingress)
7. [Phase 7: Configure GitOps Automation](#phase-7-configure-gitops-automation)
8. [Phase 8: Integrate with CI/CD Pipeline](#phase-8-integrate-with-cicd-pipeline)
9. [Phase 9: Master Lens UI](#phase-9-master-lens-ui)
10. [Phase 10-12: Advanced Topics](#phase-10-12-advanced-topics)

---

## Phase 1: Prerequisites & Environment Setup

### 1.1: Docker Desktop Kubernetes

**What is it?**
Docker Desktop bundles a **single-node Kubernetes cluster** that runs locally on your machine. It's not a full production cluster, but perfect for development and learning.

**Components:**
- **Control Plane**: Manages the cluster (API server, scheduler, controller manager)
- **Kubelet**: Runs on your machine, manages pods
- **Container Runtime**: Docker engine itself
- **kubectl**: CLI tool to interact with the cluster

**Why Docker Desktop K8s?**
- ✅ Easy one-click setup
- ✅ Shares Docker images with your local Docker daemon (no registry needed for local builds)
- ✅ Works offline
- ✅ Integrated with Docker Desktop networking
- ❌ Single-node only (no multi-node features like pod affinity across nodes)
- ❌ Limited resources (uses your laptop's RAM/CPU)

**Under the Hood:**
When you enable K8s in Docker Desktop:
1. Docker creates a VM (on Windows) or uses Docker's Linux VM (on Mac)
2. Installs Kubernetes components as containers
3. Configures kubectl context to point to `docker-desktop`
4. Runs kube-system pods (DNS, metrics, storage provisioner)

**kubectl cluster-info explained:**
```
Kubernetes control plane is running at https://kubernetes.docker.internal:6443
CoreDNS is running at https://kubernetes.docker.internal:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```
- **6443**: Default Kubernetes API server port
- **kubernetes.docker.internal**: Docker Desktop's internal DNS name for localhost

---

### 1.2: kubectl

**What is kubectl?**
The **Kubernetes command-line tool** that lets you:
- Deploy applications
- Inspect cluster resources
- View logs
- Execute commands in containers
- Manage cluster objects

**How it works:**
1. Reads configuration from `~/.kube/config` (kubeconfig file)
2. Kubeconfig contains:
   - **Clusters**: API server endpoints
   - **Users**: Authentication credentials
   - **Contexts**: Cluster + User + Namespace combination
3. Sends HTTP requests to Kubernetes API server
4. API server authenticates, authorizes, and processes request

**Context concept:**
```yaml
contexts:
- context:
    cluster: docker-desktop
    user: docker-desktop
  name: docker-desktop
```
- **Cluster**: Which Kubernetes cluster to talk to
- **User**: Which credentials to use
- **Namespace**: Default namespace (optional)

**Why verify context?**
You might have multiple clusters (AWS EKS, GKE, Minikube, etc.) configured. Always confirm you're pointing to the right one before running commands!

```powershell
kubectl config current-context  # Shows active context
kubectl config get-contexts      # Lists all contexts
kubectl config use-context docker-desktop  # Switch context
```

---

### 1.3: Lens Desktop UI

**What is Lens?**
Think of Lens as **VS Code for Kubernetes**. It's an IDE for Kubernetes clusters that provides:
- Visual cluster exploration
- Real-time resource monitoring
- Built-in terminal
- Log aggregation
- Resource editing with YAML validation
- Multi-cluster management

**Why Lens over kubectl?**
| Task | kubectl | Lens |
|------|---------|------|
| View all pods | `kubectl get pods --all-namespaces` | Visual list with status colors |
| Check pod logs | `kubectl logs pod-name -f` | Click pod → Logs (with search) |
| Edit deployment | `kubectl edit deployment name` | Visual editor with validation |
| Debug | Multiple commands | Integrated shell, logs, events |
| Learning | Need to know commands | Discoverable through UI |

**Architecture:**
```
Lens Desktop (Your Laptop)
  ↓ (reads kubeconfig)
~/.kube/config
  ↓ (contains cluster info)
Docker Desktop K8s API Server
  ↓ (manages)
Your Pods/Services/etc.
```

Lens doesn't install anything in your cluster - it's just a sophisticated kubectl wrapper with a beautiful UI.

**Key Features:**
1. **Cluster Dashboard**: Real-time metrics (CPU, memory, pods)
2. **Workloads**: Pods, Deployments, StatefulSets, DaemonSets
3. **Config**: ConfigMaps, Secrets, Resource Quotas
4. **Network**: Services, Endpoints, Ingresses
5. **Storage**: PersistentVolumes, PersistentVolumeClaims
6. **Namespaces**: Filter entire view by namespace
7. **Custom Resources**: View CRDs (important for ArgoCD!)
8. **Terminal**: Built-in kubectl terminal

**Learning Benefit:**
Lens helps you **visualize** Kubernetes concepts. When you read about "Deployment creates ReplicaSet creates Pods," Lens shows you this hierarchy visually in the resource tree.

---

## Phase 2: Kubernetes Namespace & RBAC Setup

### 2.1: Namespaces

**What are Namespaces?**
Logical **partitions** of a Kubernetes cluster. Think of them as folders or virtual clusters within a cluster.

**Why use them?**
1. **Isolation**: Staging and production don't interfere
2. **Organization**: Group related resources
3. **Access Control**: RBAC policies per namespace
4. **Resource Quotas**: Limit CPU/memory per namespace
5. **Network Policies**: Control traffic between namespaces

**Built-in Namespaces:**
- `default`: Where resources go if you don't specify a namespace
- `kube-system`: Kubernetes system components (DNS, metrics)
- `kube-public`: Public info readable by everyone
- `kube-node-lease`: Node heartbeat data

**Your Namespaces:**
- `staging`: Pre-production environment for testing
- `production`: Live user-facing environment
- `argocd`: ArgoCD components (isolated from apps)

**Under the Hood:**
Namespaces are just a label on resources. When you run:
```bash
kubectl get pods -n staging
```
Kubernetes filters pods with `metadata.namespace: staging`.

**Namespace Scope:**
- ✅ Scoped: Pods, Services, Deployments, ConfigMaps, Secrets
- ❌ Not scoped: Nodes, PersistentVolumes, Namespaces themselves

**Best Practice:**
Always specify namespace in YAML:
```yaml
metadata:
  name: auth-service
  namespace: staging  # Explicit is better than implicit
```

---

### 2.2: GitHub Container Registry (GHCR) Secret

**The Problem:**
Your Docker images are stored in **GitHub Container Registry (GHCR)** at `ghcr.io/rahulsharma2309/...`. By default, GHCR images are **private**. Kubernetes needs credentials to pull them.

**Docker Registry Authentication:**
When you run `docker login ghcr.io`, Docker stores credentials in `~/.docker/config.json`. But Kubernetes doesn't have access to this file!

**Solution: imagePullSecrets**
Kubernetes has a special secret type: `kubernetes.io/dockerconfigjson` that stores registry credentials.

**How it works:**
1. You create a secret with registry credentials:
   ```bash
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=YOUR_USERNAME \
     --docker-password=YOUR_TOKEN
   ```

2. In your deployment YAML:
   ```yaml
   spec:
     imagePullSecrets:
       - name: ghcr-secret  # References the secret
     containers:
       - image: ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.0.0
   ```

3. When creating a pod, kubelet:
   - Reads the `ghcr-secret`
   - Extracts credentials
   - Authenticates with ghcr.io
   - Pulls the image

**Why per namespace?**
Secrets are **namespace-scoped**. A secret in `staging` can't be accessed by pods in `production`. This is a security feature - you need to explicitly create it in each namespace.

**GitHub Personal Access Token (PAT):**
- **Classic Token**: Works with GHCR, select `read:packages` scope
- **Fine-grained Token**: More secure, limit to specific repositories
- **Never commit tokens to Git!** Only store in Kubernetes secrets

**Verification:**
```bash
kubectl get secret ghcr-secret -n staging -o yaml
```
You'll see base64-encoded `.dockerconfigjson` - this contains your credentials.

---

### 2.3: Service Accounts and RBAC

**What is RBAC?**
**Role-Based Access Control** - who can do what in Kubernetes.

**Key Concepts:**

**1. ServiceAccount:**
- Identity for pods (like a user account, but for processes)
- Each pod runs with a ServiceAccount
- Default: `default` ServiceAccount in each namespace

**2. Role:**
- Defines permissions within a namespace
- Example: "can read pods, can create deployments"

**3. RoleBinding:**
- Grants Role permissions to a ServiceAccount

**Why create ServiceAccounts per microservice?**

**Security Principle: Least Privilege**
Each microservice should only have permissions it needs.

Example:
- Auth Service needs to read ConfigMaps and Secrets (for DB connection)
- Auth Service doesn't need to delete Deployments
- If Auth Service is compromised, attacker can't mess with other services

**Your RBAC Structure:**
```
infra/k8s/staging/rbac/
├── auth-service-sa.yaml
│   ├── ServiceAccount: auth-service-sa
│   ├── Role: auth-service-role (read ConfigMaps, Secrets)
│   └── RoleBinding: auth-service-binding
├── user-service-sa.yaml
└── ... (one per service)
```

**Example RBAC for Auth Service:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auth-service-sa
  namespace: staging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: auth-service-role
  namespace: staging
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]  # Read-only
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: auth-service-binding
  namespace: staging
subjects:
  - kind: ServiceAccount
    name: auth-service-sa
roleRef:
  kind: Role
  name: auth-service-role
  apiGroup: rbac.authorization.k8s.io
```

**Deployment uses ServiceAccount:**
```yaml
spec:
  serviceAccountName: auth-service-sa  # Pod runs as this SA
  containers:
    - name: auth-service
      image: ...
```

**Real-World Analogy:**
- **ServiceAccount**: Employee badge
- **Role**: Job description (permissions)
- **RoleBinding**: HR assigning job to employee
- **Pod**: Employee doing their job

**Verification:**
```bash
kubectl get serviceaccounts -n staging
kubectl describe serviceaccount auth-service-sa -n staging
```

---

## Phase 3: Install ArgoCD

### 3.1: ArgoCD Architecture

**What is ArgoCD?**
A **GitOps continuous delivery tool** for Kubernetes. It treats Git as the single source of truth for your cluster state.

**Core Concept:**
```
Git Repository (Desired State)
     ↕️  (ArgoCD syncs)
Kubernetes Cluster (Actual State)
```

If Git ≠ Cluster, ArgoCD makes Cluster match Git.

**ArgoCD Components (Pods you'll see):**

**1. argocd-server:**
- **Web UI and API**
- What you interact with via browser
- Exposes port 8080 (HTTP) and 8083 (gRPC)

**2. argocd-repo-server:**
- **Git repository interaction**
- Clones repos
- Generates Kubernetes manifests (from Helm, Kustomize, etc.)
- Caches repo contents

**3. argocd-application-controller:**
- **The brain of ArgoCD**
- Watches Applications (ArgoCD CRD)
- Compares Git vs Cluster
- Executes sync operations
- Monitors application health
- Runs reconciliation loop every 3 minutes

**4. argocd-redis:**
- **Caching layer**
- Stores repository data
- Improves performance

**5. argocd-dex-server:**
- **SSO integration**
- Authenticates users via OAuth/SAML
- Not needed for local single-user setup

**6. argocd-applicationset-controller:**
- **Manages ApplicationSets**
- Creates multiple Applications from templates
- Advanced feature (optional)

**Installation Command Breakdown:**
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

This installs:
- All ArgoCD CRDs (Custom Resource Definitions)
- All ArgoCD components (as Deployments)
- Services to expose ArgoCD
- RBAC rules for ArgoCD to manage your cluster

**Why in its own namespace?**
- Isolation: ArgoCD components separate from your apps
- Security: Different RBAC rules
- Organization: Easy to find and manage

**Health Check:**
```bash
kubectl get pods -n argocd
```
All pods should show `Running` and `1/1` or `2/2` ready.

---

### 3.2: Accessing ArgoCD UI

**Port Forwarding Explained:**

Kubernetes Services have **ClusterIP** type by default:
- Only accessible within the cluster
- Not exposed to your laptop

**Solution: kubectl port-forward**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**What this does:**
```
Your Browser (localhost:8080)
      ↓
kubectl port-forward (proxy)
      ↓
Kubernetes Service (argocd-server:443)
      ↓
argocd-server Pod (container port 8080)
```

kubectl acts as a tunnel from your laptop to the cluster.

**Why 8080:443?**
- `8080`: Local port on your laptop
- `443`: Service port in cluster (HTTPS)
- You access: `https://localhost:8080`

**Self-Signed Certificate Warning:**
ArgoCD generates its own SSL certificate. Your browser doesn't trust it. Safe to proceed on localhost.

**Initial Password:**
ArgoCD creates a random admin password on first install:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Password is base64-encoded in Kubernetes secrets:**
- Kubernetes stores all secret values as base64
- Not encryption! Just encoding (can be decoded easily)
- For encryption at rest, use sealed-secrets or external secrets

**Change Password:**
After first login, change password:
- User Info (top right) → Update Password
- Or via CLI: `argocd account update-password`

**Alternative Access Methods:**

**1. LoadBalancer Service (requires cloud provider):**
```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```
On Docker Desktop, this gives you `localhost` as external IP.

**2. Ingress (production setup):**
Create an Ingress rule for `argocd.yourdomain.com`

**3. NodePort:**
Exposes ArgoCD on a high port (30000-32767) on all nodes

---

### 3.3: ArgoCD CLI

**Why use CLI when there's a UI?**
- Automation in scripts
- CI/CD integration
- Faster for repetitive tasks
- Scripting bulk operations

**Common CLI Commands:**
```bash
# List applications
argocd app list

# Get application details
argocd app get auth-service-staging

# Sync application
argocd app sync auth-service-staging

# View application resources
argocd app resources auth-service-staging

# Get sync history
argocd app history auth-service-staging

# Rollback
argocd app rollback auth-service-staging 3  # Rollback to revision 3

# Delete application
argocd app delete auth-service-staging
```

**CLI vs UI:**
| Task | CLI | UI |
|------|-----|-----|
| Quick sync | Faster | Slower (navigate + click) |
| View diffs | Text output | Visual side-by-side |
| Debugging | Need to know commands | Click around |
| Automation | ✅ Scriptable | ❌ Manual |
| Learning | Steeper | Intuitive |

**Best Practice:**
- Learn via UI first (understand concepts)
- Automate with CLI later (efficiency)

---

## Phase 4: Configure Kubernetes Resources

### 4.1: ConfigMaps

**What are ConfigMaps?**
Store **non-sensitive configuration** as key-value pairs.

**Why separate config from code?**
- **12-Factor App Principle**: Config should be environment-specific
- Same Docker image works in dev, staging, production
- Change config without rebuilding images

**ConfigMap Structure:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-service-config
  namespace: staging
data:
  ASPNETCORE_ENVIRONMENT: "Staging"  # Plain text
  ASPNETCORE_URLS: "http://+:80"
  LOGGING_LEVEL: "Information"
```

**How Pods Use ConfigMaps:**

**1. Environment Variables:**
```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    valueFrom:
      configMapKeyRef:
        name: auth-service-config
        key: ASPNETCORE_ENVIRONMENT
```

**2. Volume Mounts (as files):**
```yaml
volumes:
  - name: config-volume
    configMap:
      name: auth-service-config
volumeMounts:
  - name: config-volume
    mountPath: /etc/config
```
Creates files: `/etc/config/ASPNETCORE_ENVIRONMENT` with content "Staging"

**ConfigMap Changes:**
- Pod must restart to see new values (env vars)
- Volume-mounted files update automatically (may take ~1 minute)

**When to use:**
- Application settings
- Feature flags
- URLs (internal service URLs)
- Non-sensitive data

**When NOT to use:**
- Passwords, tokens, API keys → Use Secrets instead

---

### 4.2: Secrets

**What are Secrets?**
Store **sensitive data** encoded in base64.

**Secret vs ConfigMap:**
| Aspect | ConfigMap | Secret |
|--------|-----------|--------|
| Purpose | Non-sensitive config | Sensitive data |
| Encoding | Plain text | Base64 |
| Encryption at rest | No (by default) | Yes (if configured) |
| RBAC | Same as ConfigMap | Can be more restricted |

**Creating Secrets:**

**Manually (YAML):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-service-db-secret
  namespace: staging
type: Opaque
data:
  ConnectionStrings__DefaultConnection: U2VydmVyPWxvY2FsaG9zdDsuLi4=  # base64
```

**Via kubectl:**
```bash
kubectl create secret generic auth-service-db-secret \
  --from-literal=DB_PASSWORD=supersecret \
  -n staging
```

**Encoding:**
```bash
echo -n "supersecret" | base64  # Encode
echo "c3VwZXJzZWNyZXQ=" | base64 -d  # Decode
```

**Important: Base64 ≠ Encryption!**
Anyone with cluster access can decode secrets:
```bash
kubectl get secret auth-service-db-secret -n staging -o jsonpath="{.data.DB_PASSWORD}" | base64 -d
```

**Production Security:**
- **Sealed Secrets**: Encrypt secrets, commit to Git
- **External Secrets Operator**: Sync from Vault, AWS Secrets Manager
- **Kubernetes Encryption at Rest**: Encrypt etcd database

**Your Secrets:**
- `auth-service-db-secret`: Database connection string
- `jwt-secret`: JWT signing key
- `payment-api-secret`: Payment gateway credentials

**Best Practice:**
- Never commit secrets to Git (gitignore them)
- Use secret management tools for production
- Rotate secrets regularly

---

## Phase 5: Setup ArgoCD Applications

### 5.1: ArgoCD Application CRD

**Custom Resource Definition (CRD):**
Kubernetes is extensible. ArgoCD adds new resource types:
- `Application`
- `AppProject`
- `ApplicationSet`

**Application Resource:**
Tells ArgoCD **what to deploy** and **where**.

**Example:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: auth-service-staging
  namespace: argocd  # Applications live in argocd namespace
spec:
  project: default
  
  source:
    repoURL: https://github.com/RahulSharma2309/FreshHarvest-Market
    targetRevision: main  # Git branch/tag
    path: infra/k8s/staging/deployments/auth-service  # Folder with YAMLs
  
  destination:
    server: https://kubernetes.default.svc  # Target cluster
    namespace: staging  # Target namespace
  
  syncPolicy:
    automated:
      prune: true      # Delete removed resources
      selfHeal: true   # Revert manual changes
    syncOptions:
      - CreateNamespace=true
```

**Key Fields Explained:**

**source.repoURL:**
- Git repository to watch
- Supports HTTPS, SSH
- Can be private (requires credentials)

**source.targetRevision:**
- Branch: `main`, `develop`
- Tag: `v1.0.0`
- Commit SHA: `abc123def456`

**source.path:**
- Folder containing Kubernetes manifests
- ArgoCD applies all YAML files in this folder
- Supports Helm charts, Kustomize, plain YAML

**destination.server:**
- Kubernetes cluster API endpoint
- `https://kubernetes.default.svc` = local cluster
- Can point to remote clusters

**destination.namespace:**
- Where to create resources
- Must exist (or use `CreateNamespace=true`)

**syncPolicy.automated:**
- `prune: true`: Delete resources removed from Git
  - Example: You delete `configmap.yaml` from Git → ArgoCD deletes ConfigMap from cluster
- `selfHeal: true`: Revert manual changes
  - Example: You run `kubectl scale deployment --replicas=5` → ArgoCD reverts to Git's value (2)

**Application Lifecycle:**
```
1. You create Application → ArgoCD sees it
2. ArgoCD clones Git repo
3. ArgoCD reads YAML files from path
4. ArgoCD compares with cluster (shows OutOfSync)
5. You click Sync (or auto-sync does it)
6. ArgoCD applies resources to cluster
7. ArgoCD watches resources (shows Healthy/Degraded)
8. On Git change, repeat from step 2
```

---

### 5.2: Application Health

**ArgoCD Health Status:**

**Healthy ✅:**
- All resources exist
- Pods are Running and Ready
- No errors

**Progressing 🔄:**
- Deployment rolling out
- Pods starting
- Temporary state

**Degraded ❌:**
- Pods CrashLoopBackOff
- Deployment replica count mismatched
- Container image pull failures

**Suspended ⏸️:**
- Deployment manually scaled to 0
- Resource paused

**Missing ❓:**
- Resource deleted from cluster

**Unknown ❔:**
- ArgoCD can't determine health

**How ArgoCD Determines Health:**

**Built-in Health Checks:**
- **Deployments**: Checks if desired replicas == ready replicas
- **Pods**: Checks if status is Running and all containers are Ready
- **Services**: Checks if Endpoints exist

**Custom Health Checks:**
You can define custom logic in `argocd-cm` ConfigMap.

**Health != Sync:**
- **Synced**: Cluster matches Git
- **Healthy**: Application is working correctly

Example:
- Synced but Unhealthy: Git says 2 replicas, cluster has 2 replicas, but both pods are crashing
- OutOfSync but Healthy: Git says replica=2, you manually scaled to 3, pods are running fine

---

### 5.3: Sync Strategies

**Manual Sync:**
- You click "Sync" button
- ArgoCD applies changes
- Good for: Production, critical apps

**Automatic Sync:**
- ArgoCD syncs on every Git change (after poll interval)
- No human approval needed
- Good for: Staging, dev environments

**Prune:**
- Delete resources removed from Git
- Without prune: Deleted YAML leaves resource in cluster (orphaned)
- With prune: ArgoCD cleans up

**Self-Heal:**
- Revert manual kubectl changes
- Enforces "Git is the source of truth"
- Without self-heal: Manual changes persist
- With self-heal: Manual changes reverted in ~3 minutes

**Sync Options:**
```yaml
syncOptions:
  - CreateNamespace=true    # Auto-create namespace if missing
  - Validate=true           # Validate YAML before applying
  - ApplyOutOfSyncOnly=true # Only apply changed resources
  - PruneLast=true          # Delete resources after creating new ones
```

**Sync Phases:**
1. **PreSync**: Run before sync (e.g., database backup)
2. **Sync**: Apply resources
3. **PostSync**: Run after sync (e.g., run tests)
4. **SyncFail**: Run if sync fails (e.g., rollback)

---

## Phase 6: Install and Configure Ingress

### 6.1: What is Ingress?

**Problem:**
You have 7 microservices, each with a Service:
- `auth-service:80`
- `user-service:80`
- `product-service:80`
- ...

How do external users access them?

**Bad Solutions:**
1. **Expose each service as LoadBalancer**: 7 public IPs, expensive, complex
2. **Use NodePort**: Ugly high ports (30000+), security risk

**Good Solution: Ingress**
- Single entry point (1 IP)
- HTTP routing based on hostname/path
- SSL termination
- Like a reverse proxy (Nginx, Apache) but Kubernetes-native

**Ingress Architecture:**
```
Internet
   ↓
Ingress Controller (Nginx pod)
   ↓ (routes based on rules)
   ├─→ frontend:80 (freshharvest-market.local/)
   ├─→ gateway:80  (freshharvest-market-api.local/api)
   └─→ auth:80     (freshharvest-market-api.local/auth)
```

---

### 6.2: Ingress Controller vs Ingress Resource

**Two Components:**

**1. Ingress Controller (Software):**
- Actual reverse proxy (Nginx, Traefik, HAProxy, etc.)
- Runs as Deployment in your cluster
- Watches Ingress resources
- Configures itself based on Ingress rules

**2. Ingress Resource (Configuration):**
- YAML that defines routing rules
- Tells Ingress Controller how to route
- Like a config file for Nginx

**Analogy:**
- **Ingress Controller** = Nginx software
- **Ingress Resource** = nginx.conf file

**Installation:**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

This installs:
- `ingress-nginx-controller` Deployment
- LoadBalancer Service (exposes on localhost for Docker Desktop)
- RBAC rules
- ConfigMaps for Nginx configuration

---

### 6.3: Ingress Rules

**Your Ingress YAML:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: freshharvest-market-ingress
  namespace: staging
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: freshharvest-market.local  # Frontend
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
    
    - host: freshharvest-market-api.local  # Backend APIs
      http:
        paths:
          - path: /api/auth
            pathType: Prefix
            backend:
              service:
                name: auth-service
                port:
                  number: 80
          
          - path: /api/users
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
          
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: gateway
                port:
                  number: 80
```

**How Routing Works:**

**Request:** `http://freshharvest-market.local/`
1. Browser resolves `freshharvest-market.local` → 127.0.0.1 (via hosts file)
2. Hits Ingress Controller on localhost:80
3. Ingress Controller checks `Host` header: `freshharvest-market.local`
4. Matches rule → backend: `frontend:80`
5. Forwards request to frontend Service
6. Service routes to frontend Pod

**Request:** `http://freshharvest-market-api.local/api/auth/login`
1. Resolves to localhost
2. Host: `freshharvest-market-api.local`
3. Path: `/api/auth/login`
4. Matches `/api/auth` rule → `auth-service:80`
5. Nginx rewrites path (if configured)
6. Forwards to auth-service

**PathType:**
- `Exact`: Exact match only
- `Prefix`: Matches path prefix
- `ImplementationSpecific`: Controller-dependent

---

### 6.4: Hosts File (DNS)

**Problem:**
`freshharvest-market.local` is not a real domain. DNS servers don't know about it.

**Solution: Local DNS Override**
Windows hosts file: `C:\Windows\System32\drivers\etc\hosts`

Add:
```
127.0.0.1 freshharvest-market.local
127.0.0.1 freshharvest-market-api.local
```

**How it works:**
1. Browser tries to resolve `freshharvest-market.local`
2. OS checks hosts file first (before DNS)
3. Finds entry → returns 127.0.0.1
4. Browser connects to localhost
5. Ingress Controller receives request with `Host: freshharvest-market.local`

**Production Alternative:**
Buy a real domain, configure DNS:
```
A Record: freshharvest-market.com → LoadBalancer IP
A Record: api.freshharvest-market.com → LoadBalancer IP
```

---

## Phase 7: Configure GitOps Automation

### 7.1: Auto-Sync

**Manual vs Automatic Sync:**

**Manual (Default):**
- Git changes → ArgoCD detects (shows OutOfSync)
- You review changes in UI
- You click "Sync"
- ArgoCD applies

**Automatic:**
- Git changes → ArgoCD detects
- ArgoCD automatically syncs (no approval)
- Fast, hands-off

**When to use each:**
| Environment | Manual | Auto | Reason |
|-------------|--------|------|--------|
| Production | ✅ | ❌ | Need approval, safety |
| Staging | ❌ | ✅ | Fast iteration, testing |
| Dev | ❌ | ✅ | Experiment freely |

**Poll Interval:**
ArgoCD checks Git every **3 minutes** by default.

Change it:
```yaml
# In argocd-cm ConfigMap
data:
  timeout.reconciliation: 180s  # 3 minutes
```

For faster updates:
- Use **webhooks**: Git → ArgoCD webhook → instant sync
- Or lower poll interval (increases API calls to GitHub)

---

### 7.2: Self-Heal

**Scenario:**
Developer runs: `kubectl scale deployment auth-service --replicas=5`

**Without Self-Heal:**
- Git says: 2 replicas
- Cluster has: 5 replicas
- ArgoCD shows: OutOfSync
- Manual intervention needed

**With Self-Heal:**
- Git says: 2 replicas
- Cluster has: 5 replicas (manual change)
- ArgoCD detects drift (within 3 min)
- ArgoCD reverts to 2 replicas
- ArgoCD shows: Synced

**Why Use Self-Heal:**
- **Prevents drift**: Ensures cluster always matches Git
- **Enforces GitOps**: All changes must go through Git
- **Audit trail**: Git history shows all changes

**When NOT to use:**
- Debugging/troubleshooting (manual changes get reverted)
- Development environments (too restrictive)

**Disable temporarily:**
```bash
argocd app set auth-service-staging --self-heal=false
```

---

### 7.3: Prune

**Scenario:**
You delete `configmap.yaml` from Git.

**Without Prune:**
- Git: No ConfigMap
- Cluster: ConfigMap still exists (orphaned)
- ArgoCD: Shows Synced (ignores extra resources)

**With Prune:**
- Git: No ConfigMap
- Cluster: ConfigMap exists
- ArgoCD detects extra resource
- ArgoCD deletes ConfigMap
- Cluster matches Git

**Danger:**
Prune can **delete production data** if you remove the wrong YAML!

**Best Practice:**
- Enable prune for stateless apps
- Be cautious with StatefulSets, PVCs
- Test in staging first

---

## Phase 8: Integrate with CI/CD Pipeline

### 8.1: Push vs Pull Based Deployment

**Traditional CI/CD (Push-Based):**
```
Code Push → CI builds image → CD pushes to K8s → K8s deploys
                                     ↓
                              kubectl apply
```

**GitOps with ArgoCD (Pull-Based):**
```
Code Push → CI builds image → CI updates manifests in Git
                                        ↓
                        ArgoCD polls Git → Sees change → Pulls → Deploys
```

**Key Differences:**

| Aspect | Push (Traditional) | Pull (GitOps) |
|--------|-------------------|---------------|
| Who deploys? | CI/CD pipeline | ArgoCD |
| Access needed | CI needs cluster credentials | ArgoCD already in cluster |
| Security | External system touches production | No external access needed |
| Audit | CI logs | Git history |
| Rollback | Re-run pipeline | Git revert |
| Drift detection | None | Automatic |
| Manual changes | Persist | Reverted |

---

### 8.2: CI Pipeline with GitOps

**Your Current CI (`ci.yml`):**
```yaml
1. Build Docker images
2. Push to GHCR with version tag (v1.2.3)
3. Update K8s manifests:
   - Change image: ...auth:v1.2.2 → image: ...auth:v1.2.3
4. Commit manifest changes back to Git
5. ❌ kubectl apply (OLD - not needed with ArgoCD!)
```

**GitOps-Optimized CI:**
```yaml
1. Build Docker images
2. Push to GHCR
3. Update K8s manifests in Git
4. Commit and push
5. Done! ✅ (ArgoCD takes over from here)
```

**Manifest Update Script:**
```bash
# CI updates image tags
sed -i "s|image: ghcr.io/.*/auth:.*|image: ghcr.io/.../auth:v${VERSION}|g" \
  infra/k8s/staging/deployments/auth-service/deployment.yaml

# Commit
git add infra/k8s/staging/
git commit -m "ci: update staging to v${VERSION} [skip ci]"
git push origin main

# ArgoCD polls, detects change, syncs
```

**[skip ci] Explanation:**
- Prevent infinite loop: Commit → CI runs → Commit → CI runs → ...
- `[skip ci]` tells GitHub Actions to skip this commit

---

### 8.3: CD Pipeline Changes

**Before ArgoCD:**
`cd-staging.yml` ran `kubectl apply -f ...`

**With ArgoCD:**
Option 1: **Delete CD pipeline** (ArgoCD replaces it)
Option 2: **Minimal CD** - just trigger ArgoCD sync:

```yaml
- name: Trigger ArgoCD Sync
  run: |
    argocd app sync auth-service-staging --async
    argocd app sync user-service-staging --async
    # ... all services
```

**Why Option 1 is better:**
- Simpler (fewer pipelines to maintain)
- ArgoCD auto-syncs anyway (if enabled)
- Less moving parts = fewer bugs

**When to keep CD:**
- Manual approval workflows in production
- Integration tests between CI and deploy
- Notifications/Slack alerts

---

## Phase 9: Master Lens UI

### 9.1: Lens Navigation

**Cluster Dashboard (Home):**
- **Top Metrics**: CPU, Memory, Pod count
- **Graphs**: Real-time usage over time
- **Events**: Recent cluster events
- **Capacity**: Node resources

**Workloads:**
- **Pods**: Running containers
- **Deployments**: Manages pods
- **StatefulSets**: Stateful apps (databases)
- **DaemonSets**: One pod per node (logging agents)
- **Jobs**: One-off tasks
- **CronJobs**: Scheduled tasks

**Config:**
- **ConfigMaps**: App configuration
- **Secrets**: Sensitive data
- **HPA**: Horizontal Pod Autoscalers
- **Resource Quotas**: Namespace limits

**Network:**
- **Services**: Internal load balancers
- **Endpoints**: Service backends (pods)
- **Ingresses**: External routing
- **Network Policies**: Firewall rules

**Storage:**
- **PersistentVolumes**: Cluster storage
- **PersistentVolumeClaims**: Storage requests
- **StorageClasses**: Storage types

**Namespaces:**
- Filter view by namespace
- Select multiple namespaces

**Custom Resources:**
- ArgoCD Applications
- Other CRDs

---

### 9.2: Lens Features

**Resource Details:**
Click any resource → Detailed view:
- **Overview**: Basic info, status
- **Metadata**: Labels, annotations
- **Spec**: Resource definition
- **Status**: Current state
- **Events**: Related events

**Logs:**
- **Live tail**: Auto-scrolls
- **Search**: Filter logs
- **Timestamp**: Toggle on/off
- **Previous container**: Crashed container logs
- **Multiple pods**: View logs from multiple pods side-by-side

**Shell:**
- Exec into container
- Like `kubectl exec -it pod -- /bin/sh`
- Full terminal with autocomplete
- Can install tools (`apt-get install curl`)

**Port Forwarding:**
- Right-click pod → Forward Port
- Access pod's port on localhost
- Debug internal services

**Edit Resource:**
- Click Edit (pencil icon)
- YAML editor with syntax highlighting
- Validation before saving
- Safer than `kubectl edit` (checks for errors)

**Delete Resource:**
- Right-click → Delete
- Confirmation dialog
- Force delete option

**Scale Deployment:**
- Click Deployment → Scale button
- Slider or text input
- Instant scaling

---

### 9.3: Debugging with Lens

**Scenario: Pod is CrashLoopBackOff**

**Step 1: Check Events**
- Click pod → Events tab
- Look for: `Error: ImagePullBackOff`, `CrashLoopBackOff`, `OOMKilled`

**Step 2: Check Logs**
- Logs tab → Previous container
- See error message before crash

**Step 3: Describe Pod**
- Overview tab
- Check: Image tag, environment variables, volumes

**Step 4: Check Liveness Probe**
- Deployment → YAML
- Look for liveness/readiness probe failures

**Common Issues:**
- **ImagePullBackOff**: Wrong image tag, missing imagePullSecret
- **CrashLoopBackOff**: App error on startup
- **OOMKilled**: Out of memory (increase limits)
- **Pending**: Not enough resources (CPU/memory)

---

## Phase 10-12: Advanced Topics

### Production Deployment Strategy

**Blue-Green Deployment:**
- Keep old version running (blue)
- Deploy new version (green)
- Test green
- Switch traffic to green
- Keep blue for rollback

**Canary Deployment:**
- Deploy new version to 10% of pods
- Monitor metrics
- Gradually increase to 100%

**ArgoCD Rollouts:**
ArgoCD Rollouts (separate project) supports:
- Blue-green
- Canary
- Progressive delivery
- Automated rollback on metrics

---

### Sync Waves

**Problem:**
Services depend on each other:
- Database migrations must run before app
- ConfigMaps must exist before Deployment references them

**Solution: Sync Waves**

Add annotation:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "0"  # Deploys first
```

Waves:
- `-5`: Pre-requisites (namespaces, RBAC)
- `0`: Database migrations
- `1`: Backend services
- `2`: Frontend
- `3`: Ingress

ArgoCD deploys in order, waits for each wave to be healthy before proceeding.

---

### ApplicationSets

**Problem:**
Creating 7 similar Applications (auth, user, product, ...) is repetitive.

**Solution: ApplicationSet**

Single YAML generates multiple Applications:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices-staging
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - service: auth
          - service: user
          - service: product
          - service: order
          - service: payment
          - service: gateway
          - service: frontend
  template:
    metadata:
      name: '{{service}}-service-staging'
    spec:
      project: default
      source:
        repoURL: https://github.com/RahulSharma2309/FreshHarvest-Market
        targetRevision: main
        path: 'infra/k8s/staging/deployments/{{service}}-service'
      destination:
        server: https://kubernetes.default.svc
        namespace: staging
```

Creates 7 Applications automatically!

---

### Sealed Secrets

**Problem:**
Can't commit regular Secrets to Git (plain base64).

**Solution: Sealed Secrets**

1. Encrypt secret with public key
2. Commit encrypted secret to Git
3. Sealed Secrets controller decrypts in cluster

```bash
# Encrypt
kubeseal < secret.yaml > sealed-secret.yaml

# Commit sealed-secret.yaml (safe!)
git add sealed-secret.yaml
git commit -m "Add sealed secret"

# Apply
kubectl apply -f sealed-secret.yaml

# Controller creates regular Secret
kubectl get secrets  # Regular secret now exists
```

Only the controller (with private key) can decrypt.

---

## Key Takeaways

1. **GitOps = Git as Single Source of Truth**
   - All changes go through Git
   - ArgoCD ensures cluster matches Git

2. **Pull > Push**
   - More secure (no external access to cluster)
   - Built-in drift detection
   - Easier rollback (Git revert)

3. **Declarative > Imperative**
   - Define desired state (YAML in Git)
   - Let ArgoCD reconcile
   - Don't run manual kubectl commands

4. **Observability is Key**
   - Use Lens to understand cluster state
   - Check logs, events, metrics
   - Understand failure modes

5. **Automation with Safety**
   - Auto-sync for staging (fast iteration)
   - Manual sync for production (safety)
   - Self-heal to prevent drift

---

## Further Learning

**Books:**
- "Kubernetes Up & Running" by Kelsey Hightower
- "GitOps and Kubernetes" by Billy Yuen

**Documentation:**
- ArgoCD: https://argo-cd.readthedocs.io/
- Kubernetes: https://kubernetes.io/docs/

**Hands-On:**
- Break things intentionally
- Simulate failures
- Practice debugging

**Next Steps:**
- Service Mesh (Istio/Linkerd)
- Observability (Prometheus + Grafana)
- Multi-cluster management

---

**Remember:** The best way to learn is by doing. Don't just read - follow the [TODO.md](./TODO.md), experiment, break things, and learn from failures!
