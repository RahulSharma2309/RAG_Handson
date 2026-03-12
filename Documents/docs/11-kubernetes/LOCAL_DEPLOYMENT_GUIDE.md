# 🚀 FreshHarvest Market - Local Kubernetes Deployment Guide

> **Complete step-by-step guide to run FreshHarvest Market on your local Kubernetes cluster**

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Accessing Services](#accessing-services)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Prerequisites

### What You Need

- ✅ **Windows 10/11** with WSL2 enabled
- ✅ **Docker Desktop** installed and running
- ✅ **Kubernetes enabled** in Docker Desktop
- ✅ **kubectl** command-line tool (comes with Docker Desktop)
- ✅ **Git** to clone the repository

### Check Your Setup

Run these commands to verify everything is installed:

```powershell
# Check Docker
docker --version
# Expected: Docker version 20.x or higher

# Check Kubernetes
kubectl version --short
# Expected: Client and Server versions

# Check cluster is running
kubectl get nodes
# Expected: NAME: docker-desktop, STATUS: Ready

# Check current context
kubectl config current-context
# Expected: docker-desktop
```

If any command fails, see [Troubleshooting](#troubleshooting).

---

## Quick Start

For experienced developers, here's the TL;DR:

```powershell
# 1. Clone and navigate
git clone https://github.com/RahulSharma2309/FreshHarvest-Market.git
cd FreshHarvest-Market

# 2. Deploy everything
kubectl apply -f infra/k8s/freshharvest-market/namespace.yaml
kubectl apply -f infra/k8s/freshharvest-market/configmap.yaml
kubectl apply -f infra/k8s/freshharvest-market/database/
kubectl apply -f infra/k8s/freshharvest-market/services/
kubectl apply -f infra/k8s/freshharvest-market/ingress-all-services.yaml

# 3. Install Nginx Ingress Controller (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 4. Update hosts file (run Notepad as Admin)
# Add lines from: infra/k8s/freshharvest-market/hosts-file-update.txt

# 5. Wait for pods to be ready
kubectl get pods -n freshharvest-market -w

# 6. Access application
Start-Process "http://app.freshharvest-market.local"
```

Continue reading for detailed explanations of each step.

---

## Detailed Setup

### Step 1: Enable Kubernetes in Docker Desktop

1. **Open Docker Desktop**
2. **Go to Settings** → **Kubernetes**
3. **Check "Enable Kubernetes"**
4. **Click "Apply & Restart"**
5. **Wait for "Kubernetes is running" status** (green indicator)

<details>
<summary>Why Docker Desktop Kubernetes?</summary>

**Pros:**
- ✅ Free and runs on your local machine
- ✅ No cloud costs
- ✅ Integrated with Docker Desktop
- ✅ Full Kubernetes features
- ✅ Easy reset if things break

**Alternatives:**
- **Minikube** - Good alternative, more setup
- **K3s** - Lightweight, good for learning
- **GKE/EKS/AKS** - Cloud providers (costs money)

We chose Docker Desktop for simplicity.
</details>

---

### Step 2: Switch to Docker Desktop Context

If you've used other Kubernetes clusters (like GKE), switch context:

```powershell
# List all contexts
kubectl config get-contexts

# Switch to Docker Desktop
kubectl config use-context docker-desktop

# Verify
kubectl config current-context
# Should output: docker-desktop

# Test connection
kubectl get nodes
# Should show: docker-desktop   Ready
```

---

### Step 3: Install Nginx Ingress Controller

**What is Ingress?** It routes HTTP traffic to your services based on URLs (like a reverse proxy).

**Why Nginx?** It's the most popular Kubernetes Ingress controller.

```powershell
# Install Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Verify installation
kubectl get pods -n ingress-nginx

# Expected output (wait for all to be Running):
# NAME                                        READY   STATUS
# ingress-nginx-controller-xxxxxxxxxx-xxxxx   1/1     Running
# ingress-nginx-admission-create-xxxxx        0/1     Completed
# ingress-nginx-admission-patch-xxxxx         0/1     Completed
```

**Wait 2-3 minutes** for all pods to be ready.

<details>
<summary>What does this do?</summary>

- Installs Nginx Ingress Controller in `ingress-nginx` namespace
- Creates a LoadBalancer service on `localhost`
- Enables routing based on domain names (like `auth.freshharvest-market.local`)
- Without this, you can't access services via URLs
</details>

---

### Step 4: Clone the Repository

```powershell
# Clone the repo
git clone https://github.com/RahulSharma2309/FreshHarvest-Market.git

# Navigate to project
cd FreshHarvest-Market

# Verify Kubernetes manifests exist
ls infra/k8s/freshharvest-market/

# Expected output:
# - namespace.yaml
# - configmap.yaml
# - database/ (folder)
# - services/ (folder)
# - ingress-all-services.yaml
```

---

### Step 5: Deploy to Kubernetes

Deploy in this order (order matters!):

#### 5.1 Create Namespace

```powershell
kubectl apply -f infra/k8s/freshharvest-market/namespace.yaml
```

**What this does:** Creates an isolated environment called `freshharvest-market` for all our services.

**Verify:**
```powershell
kubectl get namespace freshharvest-market
# STATUS should be: Active
```

---

#### 5.2 Create ConfigMap

```powershell
kubectl apply -f infra/k8s/freshharvest-market/configmap.yaml
```

**What this does:** Creates configuration shared by all services (environment variables, URLs, etc.)

**Key configs:**
- `ASPNETCORE_ENVIRONMENT: Development` - Enables Swagger
- Service URLs for inter-service communication
- App name and branding

**Verify:**
```powershell
kubectl get configmap -n freshharvest-market
# Should show: freshharvest-market-config
```

---

#### 5.3 Deploy Database

```powershell
kubectl apply -f infra/k8s/freshharvest-market/database/
```

**What this deploys:**
1. **PersistentVolumeClaim** (`mssql-pvc.yaml`) - Allocates 5GB storage for database
2. **Secret** (`mssql-secret.yaml`) - Stores SQL Server SA password
3. **Deployment** (`mssql-deployment.yaml`) - Runs SQL Server 2019
4. **Service** (`mssql-deployment.yaml`) - Exposes database to other services
5. **Service Alias** (`mssql-service-alias.yaml`) - Creates `mssql` DNS name

**Why the alias?** Services look for `mssql:1433`, but the actual service is `freshharvest-market-mssql`. The alias bridges this gap.

**Verify:**
```powershell
kubectl get pods -n freshharvest-market
# Should show: freshharvest-market-mssql-xxxxxxxxxx   1/1   Running

kubectl get pvc -n freshharvest-market
# Should show: freshharvest-market-mssql-data   Bound   5Gi

kubectl get svc -n freshharvest-market
# Should show: mssql and freshharvest-market-mssql
```

**Wait for database pod to be ready** (takes ~1 minute):
```powershell
kubectl wait --for=condition=ready pod -l app=freshharvest-market-mssql -n freshharvest-market --timeout=120s
```

---

#### 5.4 Deploy All Microservices

```powershell
kubectl apply -f infra/k8s/freshharvest-market/services/
```

**What this deploys:**
- **Auth Service** - Authentication and JWT tokens
- **User Service** - User management
- **Product Service** - Product catalog
- **Order Service** - Order management
- **Payment Service** - Payment processing
- **Gateway** - API Gateway (routes to all services)
- **Frontend** - React application

Each service:
- Runs 2 replicas (pods) for high availability
- Has resource limits (CPU/Memory)
- Connects to the shared SQL Server database
- Uses the ConfigMap for configuration

**Verify:**
```powershell
kubectl get pods -n freshharvest-market

# Expected: 15 pods total
# - 2 auth pods
# - 2 user pods
# - 2 product pods
# - 2 order pods
# - 2 payment pods
# - 2 gateway pods
# - 2 frontend pods
# - 1 mssql pod
```

**Wait for all pods to be Running** (takes 2-3 minutes):
```powershell
kubectl get pods -n freshharvest-market -w
# Press Ctrl+C when all show 1/1 Running
```

<details>
<summary>Why 2 replicas?</summary>

- **High Availability:** If one pod crashes, the other handles traffic
- **Load Balancing:** Kubernetes distributes requests between pods
- **Zero Downtime Updates:** Can update one pod while the other serves traffic
- **Production-like:** Simulates real deployment scenarios
</details>

---

#### 5.5 Create Ingress Routes

```powershell
kubectl apply -f infra/k8s/freshharvest-market/ingress-all-services.yaml
```

**What this does:** Configures routing rules so you can access services via URLs:
- `app.freshharvest-market.local` → Frontend
- `api.freshharvest-market.local` → Gateway
- `auth.freshharvest-market.local` → Auth Service
- `user.freshharvest-market.local` → User Service
- `product.freshharvest-market.local` → Product Service
- `order.freshharvest-market.local` → Order Service
- `payment.freshharvest-market.local` → Payment Service

**Verify:**
```powershell
kubectl get ingress -n freshharvest-market

# Expected output:
# NAME                              HOSTS                 ADDRESS       PORTS
# freshharvest-market-ingress-all     app.freshharvest-... +6     localhost     80
```

**ADDRESS should be `localhost`** - this means Nginx is ready.

---

### Step 6: Configure Local DNS (Hosts File)

**Why?** Your browser needs to know that `*.freshharvest-market.local` points to `localhost`.

#### Option A: Manual Configuration

1. **Open Notepad as Administrator**
   - Press Windows Key
   - Type "Notepad"
   - Right-click → **Run as Administrator**

2. **Open Hosts File**
   - File → Open
   - Navigate to: `C:\Windows\System32\drivers\etc\`
   - Change file type to "All Files (*.*)"
   - Select `hosts` → Open

3. **Add These Lines at the Bottom**
   ```
   # FreshHarvest Market - Kubernetes Ingress URLs
   127.0.0.1 app.freshharvest-market.local
   127.0.0.1 api.freshharvest-market.local
   127.0.0.1 auth.freshharvest-market.local
   127.0.0.1 user.freshharvest-market.local
   127.0.0.1 product.freshharvest-market.local
   127.0.0.1 order.freshharvest-market.local
   127.0.0.1 payment.freshharvest-market.local
   ```

4. **Save** (Ctrl+S) and **Close**

#### Option B: Copy from File

```powershell
# View the pre-made configuration
Get-Content infra/k8s/freshharvest-market/hosts-file-update.txt

# Copy the lines starting with 127.0.0.1 to your hosts file
```

**Verify DNS Configuration:**
```powershell
# Check hosts file
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "freshharvest"

# Test DNS resolution
ping app.freshharvest-market.local
# Should resolve to 127.0.0.1
```

---

### Step 7: Install Kubernetes Dashboard (Optional but Recommended)

Get a visual UI for managing your cluster!

```powershell
# Install Kubernetes Dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user
kubectl apply -f infra/k8s/dashboard-admin.yaml

# Get access token
kubectl -n kubernetes-dashboard create token admin-user

# Copy the token output (you'll need it to login)

# Start dashboard proxy (in a new terminal)
kubectl proxy

# Open dashboard
Start-Process "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
```

**When prompted:**
1. Select "Token"
2. Paste the token you copied
3. Click "Sign In"
4. **Change namespace dropdown to `freshharvest-market`** to see your services

---

## Accessing Services

You have **two options** to access services: **Ingress (Recommended)** or **Port-Forward (Quick Testing)**.

### Option 1: Ingress (Recommended - Production-like) ✅

This is the **recommended approach** as it mirrors production setup. All services are accessible via domain names through Ingress.

#### Step 1: Update Hosts File

**Open Notepad as Administrator** and add these entries to `C:\Windows\System32\drivers\etc\hosts`:

```
# FreshHarvest Market - Staging
127.0.0.1 staging.freshharvest-market.local
127.0.0.1 api.staging.freshharvest-market.local
127.0.0.1 auth.staging.freshharvest-market.local
127.0.0.1 user.staging.freshharvest-market.local
127.0.0.1 product.staging.freshharvest-market.local
127.0.0.1 order.staging.freshharvest-market.local
127.0.0.1 payment.staging.freshharvest-market.local
```

**Or for freshharvest-market namespace:**

```
# FreshHarvest Market
127.0.0.1 app.freshharvest-market.local
127.0.0.1 api.freshharvest-market.local
127.0.0.1 auth.freshharvest-market.local
127.0.0.1 user.freshharvest-market.local
127.0.0.1 product.freshharvest-market.local
127.0.0.1 order.freshharvest-market.local
127.0.0.1 payment.freshharvest-market.local
```

#### Step 2: Access Services via Ingress

All services are accessible via your browser:

**For Staging Namespace:**
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://staging.freshharvest-market.local | React application UI |
| **API Gateway** | http://api.staging.freshharvest-market.local/swagger | Gateway Swagger docs |
| **Auth Service** | http://auth.staging.freshharvest-market.local/swagger | Authentication APIs |
| **User Service** | http://user.staging.freshharvest-market.local/swagger | User management APIs |
| **Product Service** | http://product.staging.freshharvest-market.local/swagger | Product catalog APIs |
| **Order Service** | http://order.staging.freshharvest-market.local/swagger | Order management APIs |
| **Payment Service** | http://payment.staging.freshharvest-market.local/swagger | Payment APIs |

**For FreshHarvest Market Namespace:**
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend (Main App)** | http://app.freshharvest-market.local | React application UI |
| **API Gateway** | http://api.freshharvest-market.local/swagger/index.html | Gateway Swagger docs |
| **Auth Service** | http://auth.freshharvest-market.local/swagger/index.html | Authentication APIs |
| **User Service** | http://user.freshharvest-market.local/swagger/index.html | User management APIs |
| **Product Service** | http://product.freshharvest-market.local/swagger/index.html | Product catalog APIs |
| **Order Service** | http://order.freshharvest-market.local/swagger/index.html | Order management APIs |
| **Payment Service** | http://payment.freshharvest-market.local/swagger/index.html | Payment APIs |

**Note:** 
- For staging namespace, use `/swagger` (e.g., `http://auth.staging.freshharvest-market.local/swagger`)
- For freshharvest-market namespace, use `/swagger/index.html` (e.g., `http://auth.freshharvest-market.local/swagger/index.html`)

#### Advantages of Ingress:
- ✅ Production-like setup
- ✅ No need to run port-forward commands
- ✅ Always available (no manual commands)
- ✅ Domain-based routing
- ✅ Easy to remember URLs
- ✅ Can add SSL/TLS easily in future

---

### Option 2: Port-Forward (Quick Testing) 🔧

Use this for **quick testing** or when you don't want to configure Ingress. This creates a temporary tunnel to access services directly.

#### How to Use Port-Forward

```powershell
# Auth Service
kubectl port-forward svc/auth-service 5001:80 -n staging
# Access at: http://localhost:5001/swagger

# User Service
kubectl port-forward svc/user-service 5002:80 -n staging
# Access at: http://localhost:5002/swagger

# Product Service
kubectl port-forward svc/product-service 5003:80 -n staging
# Access at: http://localhost:5003/swagger

# Order Service
kubectl port-forward svc/order-service 5004:80 -n staging
# Access at: http://localhost:5004/swagger

# Payment Service
kubectl port-forward svc/payment-service 5005:80 -n staging
# Access at: http://localhost:5005/swagger

# Gateway
kubectl port-forward svc/gateway 5000:80 -n staging
# Access at: http://localhost:5000/swagger
```

**For freshharvest-market namespace:**

```powershell
# Auth Service
kubectl port-forward svc/freshharvest-market-auth 5001:80 -n freshharvest-market
# Access at: http://localhost:5001/swagger

# User Service
kubectl port-forward svc/freshharvest-market-user 5002:80 -n freshharvest-market
# Access at: http://localhost:5002/swagger

# Product Service
kubectl port-forward svc/freshharvest-market-product 5003:80 -n freshharvest-market
# Access at: http://localhost:5003/swagger

# Order Service
kubectl port-forward svc/freshharvest-market-order 5004:80 -n freshharvest-market
# Access at: http://localhost:5004/swagger

# Payment Service
kubectl port-forward svc/freshharvest-market-payment 5005:80 -n freshharvest-market
# Access at: http://localhost:5005/swagger

# Gateway
kubectl port-forward svc/freshharvest-market-gateway 5000:80 -n freshharvest-market
# Access at: http://localhost:5000/swagger
```

#### Port-Forward Service URLs

| Service | Port-Forward Command | URL |
|---------|---------------------|-----|
| **Auth Service** | `kubectl port-forward svc/auth-service 5001:80 -n staging` | http://localhost:5001/swagger |
| **User Service** | `kubectl port-forward svc/user-service 5002:80 -n staging` | http://localhost:5002/swagger |
| **Product Service** | `kubectl port-forward svc/product-service 5003:80 -n staging` | http://localhost:5003/swagger |
| **Order Service** | `kubectl port-forward svc/order-service 5004:80 -n staging` | http://localhost:5004/swagger |
| **Payment Service** | `kubectl port-forward svc/payment-service 5005:80 -n staging` | http://localhost:5005/swagger |
| **Gateway** | `kubectl port-forward svc/gateway 5000:80 -n staging` | http://localhost:5000/swagger |

#### Advantages of Port-Forward:
- ✅ Quick setup (no hosts file needed)
- ✅ Good for quick testing
- ✅ No Ingress configuration required

#### Disadvantages of Port-Forward:
- ❌ Temporary (stops when terminal closes)
- ❌ Need to run command for each service
- ❌ Multiple terminal windows needed
- ❌ Not production-like
- ❌ Manual port management

---

### 🎯 Quick Test Script (Ingress)

```powershell
# Test all services via Ingress (Staging)
$services = @(
    @{Name="Frontend"; Url="http://staging.freshharvest-market.local"},
    @{Name="Gateway"; Url="http://api.staging.freshharvest-market.local/swagger"},
    @{Name="Auth"; Url="http://auth.staging.freshharvest-market.local/swagger"},
    @{Name="User"; Url="http://user.staging.freshharvest-market.local/swagger"},
    @{Name="Product"; Url="http://product.staging.freshharvest-market.local/swagger"},
    @{Name="Order"; Url="http://order.staging.freshharvest-market.local/swagger"},
    @{Name="Payment"; Url="http://payment.staging.freshharvest-market.local/swagger"}
)

foreach ($svc in $services) {
    try {
        $response = Invoke-WebRequest -Uri $svc.Url -Method Head -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ $($svc.Name) - OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($svc.Name) - Failed" -ForegroundColor Red
    }
}
```

### 🎯 Quick Test Script (FreshHarvest Market)

```powershell
# Test all services via Ingress (FreshHarvest Market)
$services = @(
    @{Name="Frontend"; Url="http://app.freshharvest-market.local"},
    @{Name="Gateway"; Url="http://api.freshharvest-market.local/swagger/index.html"},
    @{Name="Auth"; Url="http://auth.freshharvest-market.local/swagger/index.html"},
    @{Name="User"; Url="http://user.freshharvest-market.local/swagger/index.html"},
    @{Name="Product"; Url="http://product.freshharvest-market.local/swagger/index.html"},
    @{Name="Order"; Url="http://order.freshharvest-market.local/swagger/index.html"},
    @{Name="Payment"; Url="http://payment.freshharvest-market.local/swagger/index.html"}
)

foreach ($svc in $services) {
    try {
        $response = Invoke-WebRequest -Uri $svc.Url -Method Head -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ $($svc.Name) - OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($svc.Name) - Failed" -ForegroundColor Red
    }
}
```

### 📊 Comparison: Ingress vs Port-Forward

| Feature | Ingress | Port-Forward |
|---------|---------|--------------|
| **Setup** | One-time (hosts file) | Per service (command) |
| **Persistence** | Always available | Temporary (until terminal closes) |
| **Production-like** | ✅ Yes | ❌ No |
| **Multiple Services** | ✅ All at once | ❌ One per terminal |
| **Domain Names** | ✅ Yes | ❌ No (localhost only) |
| **SSL/TLS Ready** | ✅ Yes | ❌ No |
| **Best For** | Development & Production | Quick testing |

**Recommendation:** Use **Ingress** for regular development work. Use **Port-Forward** only for quick debugging or when Ingress is not configured.

---

## Verification

### Check Deployment Status

```powershell
# All pods should be Running
kubectl get pods -n freshharvest-market

# All services should have endpoints
kubectl get svc -n freshharvest-market

# Ingress should show localhost
kubectl get ingress -n freshharvest-market
```

### Check Pod Logs

```powershell
# View logs for a specific service
kubectl logs -n freshharvest-market -l app=freshharvest-market-auth --tail=50

# Follow logs in real-time
kubectl logs -n freshharvest-market -l app=freshharvest-market-payment -f

# Check if a pod is crashing
kubectl describe pod <pod-name> -n freshharvest-market
```

### Verify Database Connectivity

```powershell
# Check if database is ready
kubectl exec -it -n freshharvest-market $(kubectl get pod -n freshharvest-market -l app=freshharvest-market-mssql -o jsonpath='{.items[0].metadata.name}') -- /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'YourStrong@Passw0rd' -Q 'SELECT @@VERSION'
```

---

## Troubleshooting

### Issue 1: "This site can't be reached"

**Symptom:** Browser shows "This site can't be reached" for any freshharvest-market.local URL

**Causes & Solutions:**

1. **Hosts file not updated**
   ```powershell
   # Verify hosts file
   Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "freshharvest"
   ```
   If no results, re-add the entries from [Step 6](#step-6-configure-local-dns-hosts-file)

2. **Nginx Ingress not running**
   ```powershell
   # Check ingress controller
   kubectl get pods -n ingress-nginx
   
   # If not found, reinstall
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

3. **Wrong kubectl context**
   ```powershell
   # Switch to docker-desktop
   kubectl config use-context docker-desktop
   ```

---

### Issue 2: Pods are in "CrashLoopBackOff"

**Symptom:** `kubectl get pods` shows pods restarting repeatedly

**Diagnosis:**
```powershell
# Check pod status
kubectl describe pod <pod-name> -n freshharvest-market

# Check logs
kubectl logs <pod-name> -n freshharvest-market --previous
```

**Common Causes:**

1. **Database not ready** - Wait for `freshharvest-market-mssql` to be Running first
2. **Wrong connection string** - Check ConfigMap
3. **Resource limits** - Pod might need more memory/CPU

**Solutions:**
```powershell
# Restart all deployments
kubectl rollout restart deployment -n freshharvest-market

# Scale down and up
kubectl scale deployment --all --replicas=0 -n freshharvest-market
kubectl scale deployment --all --replicas=2 -n freshharvest-market
```

---

### Issue 3: "404 Not Found" on Swagger

**Symptom:** Service URL works but `/swagger` shows 404

**Solution:** Use `/swagger/index.html` instead of just `/swagger`
- ✅ `http://auth.freshharvest-market.local/swagger/index.html`
- ❌ `http://auth.freshharvest-market.local/swagger`

---

### Issue 4: Pods Show "ImagePullBackOff"

**Symptom:** Pods can't pull Docker images

**Cause:** Images don't exist in GitHub Container Registry

**Solution:** Build and push images first:
```powershell
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push (example for auth service)
cd services/auth-service
docker build -t ghcr.io/rahulsharma2309/freshharvest-market-auth:latest .
docker push ghcr.io/rahulsharma2309/freshharvest-market-auth:latest
```

Or use the CI/CD pipeline to build images automatically.

---

### Issue 5: "No space left on device"

**Symptom:** Docker runs out of disk space

**Solution:**
```powershell
# Clean up unused images and containers
docker system prune -a --volumes

# In Docker Desktop: Settings → Resources → Disk
# Increase Virtual Disk Limit to 64GB or more
```

---

### Issue 6: Kubernetes Dashboard Shows "No resources found"

**Symptom:** Dashboard loads but shows empty

**Solution:** **Change the namespace dropdown from `default` to `freshharvest-market`** (top-left corner)

---

### Complete Reset (Nuclear Option)

If everything is broken and you want to start fresh:

```powershell
# 1. Delete everything in freshharvest-market namespace
kubectl delete namespace freshharvest-market

# 2. Wait for namespace deletion
kubectl get namespace

# 3. Restart Docker Desktop
# Right-click Docker Desktop icon → Restart

# 4. Re-run deployment from Step 5
```

---

## Next Steps

### 🎓 Learn More

- **[CONCEPTS.md](./CONCEPTS.md)** - Understand Kubernetes concepts deeply
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Learn about Ingress, LoadBalancer, etc.
- **[CI_CD_INTEGRATION.md](./CI_CD_INTEGRATION.md)** - Automate deployments
- **[HELM_GUIDE.md](./HELM_GUIDE.md)** - Package deployments with Helm

### 🔧 Customize Your Deployment

#### Change Service Replicas
```powershell
# Scale a service to 3 replicas
kubectl scale deployment freshharvest-market-auth --replicas=3 -n freshharvest-market
```

#### Update Environment Variables
```powershell
# Edit ConfigMap
kubectl edit configmap freshharvest-market-config -n freshharvest-market

# Restart deployments to pick up changes
kubectl rollout restart deployment -n freshharvest-market
```

#### View Resource Usage
```powershell
# Check CPU/Memory usage
kubectl top pods -n freshharvest-market
kubectl top nodes
```

### 🚀 Deploy to Production

When ready for production:
1. Change `ASPNETCORE_ENVIRONMENT` to "Production" in ConfigMap
2. Enable HTTPS with TLS certificates
3. Set up proper Secrets management (Azure Key Vault, etc.)
4. Configure resource limits based on load testing
5. Set up monitoring (Prometheus, Grafana)
6. Configure backup for database PVC

See **[CI_CD_INTEGRATION.md](./CI_CD_INTEGRATION.md)** for automated production deployments.

---

## Useful Commands Cheat Sheet

```powershell
# View all resources in namespace
kubectl get all -n freshharvest-market

# Describe a resource
kubectl describe pod <pod-name> -n freshharvest-market
kubectl describe svc <service-name> -n freshharvest-market

# View logs
kubectl logs <pod-name> -n freshharvest-market
kubectl logs -f <pod-name> -n freshharvest-market  # Follow logs

# Execute commands in pod
kubectl exec -it <pod-name> -n freshharvest-market -- /bin/bash

# Port forward (temporary access - Option 2)
# For staging namespace:
kubectl port-forward svc/auth-service 5001:80 -n staging
# Access at: http://localhost:5001/swagger

# For freshharvest-market namespace:
kubectl port-forward svc/freshharvest-market-auth 8080:80 -n freshharvest-market
# Access at: http://localhost:8080/swagger

# Note: Use Ingress (Option 1) for production-like access instead

# Restart a deployment
kubectl rollout restart deployment <deployment-name> -n freshharvest-market

# Check rollout status
kubectl rollout status deployment <deployment-name> -n freshharvest-market

# View events
kubectl get events -n freshharvest-market --sort-by='.lastTimestamp'

# Delete a resource
kubectl delete pod <pod-name> -n freshharvest-market
kubectl delete -f <file.yaml>

# Apply changes
kubectl apply -f <file.yaml>
```

---

## Architecture Overview

```
User Browser
    │
    ├─→ http://app.freshharvest-market.local (Frontend)
    ├─→ http://api.freshharvest-market.local (Gateway)
    └─→ http://auth.freshharvest-market.local (Auth Service)
    
        ↓
        
Windows Hosts File (DNS Resolution)
    127.0.0.1 → All *.freshharvest-market.local
    
        ↓
        
Nginx Ingress Controller (Routing)
    Routes based on hostname
    
        ↓
        
Kubernetes Services (Load Balancing)
    ClusterIP services for each microservice
    
        ↓
        
Pods (Application Containers)
    2 replicas per service for HA
    
        ↓
        
SQL Server Database (Persistent Storage)
    Single mssql pod with 5GB PVC
```

---

## Summary

You now have a **complete local Kubernetes deployment** of FreshHarvest Market! 🎉

**What you've accomplished:**
- ✅ Deployed 7 microservices to Kubernetes
- ✅ Set up persistent database storage
- ✅ Configured ingress for enterprise-level URLs
- ✅ Enabled Swagger for API testing
- ✅ Created a production-like environment locally
- ✅ Learned Kubernetes fundamentals

**What's running:**
- 15 pods across 7 services
- 1 SQL Server database with persistent storage
- Nginx Ingress Controller for routing
- ConfigMaps and Secrets for configuration

**Access everything at:** http://app.freshharvest-market.local

---

**Need help?** Check other guides in this folder or open an issue on GitHub!
