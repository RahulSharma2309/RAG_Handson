# Lens Desktop - Complete UI Guide

Your visual window into Kubernetes clusters.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Workloads](#workloads)
4. [Configuration](#configuration)
5. [Network](#network)
6. [Storage](#storage)
7. [Debugging Features](#debugging-features)
8. [Common Tasks](#common-tasks)

---

## Getting Started

### Installation

1. Download Lens from: https://k8slens.dev/
2. Install for Windows
3. Launch Lens Desktop
4. Lens auto-detects clusters from `~/.kube/config`
5. Click on "docker-desktop" cluster to connect

### First Launch

**Catalog View:**
- Lists all available clusters
- Shows connection status
- Displays Kubernetes version

**Connect to Cluster:**
- Click cluster name
- Lens loads cluster data
- Dashboard appears

---

## Dashboard Overview

### Cluster Dashboard (Home)

**Top Metrics Bar:**
```
CPU: 15% (2.4 GHz / 16 GHz)
Memory: 4.2 GB / 16 GB
Pods: 24 / 110
```

**What these mean:**
- **CPU**: Cluster-wide CPU usage
- **Memory**: Total memory used by all pods
- **Pods**: Running pods / Max pods allowed

**Graphs:**
- **CPU Usage**: Real-time graph (updates every few seconds)
- **Memory Usage**: Shows trends over last hour
- **Pod Count**: Number of pods over time
- **Network I/O**: In/out traffic

**Events Panel:**
Shows recent cluster events:
```
5s ago   Normal   Created   Pod nginx-abc123   Created container
10s ago  Normal   Pulling   Pod nginx-abc123   Pulling image
```

**Node Information:**
- Node name: `docker-desktop`
- Status: Ready
- CPU/Memory capacity
- Pod capacity
- Kubernetes version

---

## Workloads

### Pods View

**Location:** Workloads → Pods

**Pod List:**
Each row shows:
- **Name**: Pod name (click to see details)
- **Namespace**: Which namespace it's in
- **Ready**: Containers ready/total (e.g., 2/2)
- **Status**: Running, Pending, CrashLoopBackOff, etc.
- **Restarts**: How many times containers restarted
- **Age**: How long pod has been running
- **CPU**: Current CPU usage
- **Memory**: Current memory usage
- **Node**: Which node it's on (docker-desktop)

**Status Colors:**
- 🟢 **Green**: Running and healthy
- 🟡 **Yellow**: Pending, ContainerCreating
- 🔴 **Red**: CrashLoopBackOff, Error, ImagePullBackOff
- ⚪ **Gray**: Completed, Terminated

**Filter Bar:**
- Search by name
- Filter by namespace
- Filter by labels
- Filter by status

---

### Pod Details

**Click on any pod** to open details panel.

#### **Overview Tab**

**Status Section:**
- **Phase**: Running, Pending, Failed
- **QoS Class**: Guaranteed, Burstable, BestEffort
- **Pod IP**: Internal IP address
- **Node**: Which node it's scheduled on

**Container Section:**
- **Name**: Container name
- **Image**: Docker image
- **Image Pull Policy**: IfNotPresent, Always
- **Status**: Running, Waiting, Terminated
- **Ready**: True/False
- **Restart Count**: Number of restarts

**Resource Requests/Limits:**
```
Requests:
  CPU: 100m
  Memory: 256Mi
Limits:
  CPU: 500m
  Memory: 512Mi
```

**Probes:**
- Liveness Probe: HTTP GET /api/health on port 80
- Readiness Probe: HTTP GET /api/health on port 80

**Environment Variables:**
Lists all env vars (values visible for ConfigMaps, masked for Secrets)

**Volumes:**
- ConfigMap volumes
- Secret volumes
- EmptyDir volumes
- PersistentVolumeClaims

---

#### **Logs Tab**

**Features:**
- **Live Tail**: Auto-scrolls as new logs appear
- **Search**: Filter logs by keyword
- **Timestamp**: Toggle timestamps on/off
- **Previous**: Show logs from previous container (if crashed)
- **Multiple Containers**: Select which container to view (if multi-container pod)
- **Download**: Save logs to file

**Search:**
Type keyword → Logs filter in real-time

Example: Search "ERROR" → Shows only lines with ERROR

**Timestamps:**
```
2026-01-26 20:30:15.123 [INFO] Application started
2026-01-26 20:30:16.456 [INFO] Listening on port 80
2026-01-26 20:30:17.789 [ERROR] Database connection failed
```

**Previous Container:**
If pod crashed and restarted, view logs from crashed container:
- Dropdown at top: "Current" → "Previous"
- See error logs that caused crash

**Use Cases:**
- Debug crashes: Check previous container logs
- Monitor application: Live tail during requests
- Find errors: Search for "ERROR", "Exception", "Failed"
- Performance: Look for slow queries, timeouts

---

#### **Shell Tab**

**Opens terminal inside container:**

```bash
/ # ls
bin   dev   etc   home  ...

/ # pwd
/app

/ # ps aux
PID   USER     COMMAND
1     root     dotnet AuthService.dll
```

**Common Commands:**
```bash
# Check files
ls -la
cat /etc/config/app-settings.json

# Network debugging
curl http://user-service/api/health
wget -O- http://localhost/api/health

# Process inspection
ps aux | grep dotnet
top

# Environment
env | grep DATABASE
printenv

# Install tools (ephemeral - lost on pod restart)
apt-get update && apt-get install -y curl
```

**Use Cases:**
- **Debug config**: Check if files mounted correctly
- **Test connectivity**: Curl other services
- **Inspect process**: Check if app is running
- **Emergency fix**: Temporarily modify files (not recommended for prod)

---

#### **Events Tab**

Shows Kubernetes events related to this pod:

```
Type     Reason      Age   Message
Normal   Scheduled   5m    Successfully assigned staging/auth-service-abc123
Normal   Pulling     5m    Pulling image "ghcr.io/.../auth:v1.2.3"
Normal   Pulled      4m    Successfully pulled image
Normal   Created     4m    Created container auth-service
Normal   Started     4m    Started container auth-service
```

**Event Types:**
- **Normal**: Routine operations (pulling image, starting container)
- **Warning**: Potential issues (failed health check, restart)
- **Error**: Failures (image pull failed, crash)

**Use Cases:**
- **Debug ImagePullBackOff**: See which image failed to pull
- **Check restart reasons**: See why container restarted
- **Troubleshoot scheduling**: Why pod is pending

---

### Deployments View

**Location:** Workloads → Deployments

**Deployment List:**
- **Name**: Deployment name
- **Namespace**: Namespace
- **Pods**: Ready pods / Desired replicas (2/2)
- **Age**: How long deployment exists
- **Images**: Container images used

**Click on deployment** → Details:

#### **Overview Tab**
- **Strategy**: RollingUpdate, Recreate
- **Replicas**: Desired, current, ready
- **Selector**: Label selectors
- **Labels**: Deployment labels
- **Annotations**: Metadata

#### **Pods Tab**
Lists pods created by this deployment.

#### **ReplicaSets Tab**
Shows ReplicaSet history (for rollbacks).

#### **Events Tab**
Deployment-level events (scaling, rolling update).

#### **Scale Tab**
**Quick scaling:**
- Slider: Drag to change replica count
- Or type number: Input replicas directly
- Click "Scale"

**Use Cases:**
- Scale up for load testing
- Scale down to save resources
- Scale to 0 to stop app without deleting

---

## Configuration

### ConfigMaps View

**Location:** Config → Config Maps

**ConfigMap List:**
- **Name**: ConfigMap name
- **Namespace**: Namespace
- **Keys**: Number of keys (e.g., 5 keys)
- **Age**: Creation time

**Click on ConfigMap** → See key-value pairs:
```
ASPNETCORE_ENVIRONMENT: Staging
ASPNETCORE_URLS: http://+:80
LOGGING_LEVEL: Information
```

**Edit ConfigMap:**
1. Click "Edit" (pencil icon)
2. Modify values
3. Save
4. **Note**: Pods must restart to see changes (for env vars)

---

### Secrets View

**Location:** Config → Secrets

**Secret List:**
- **Name**: Secret name
- **Type**: Opaque, kubernetes.io/dockerconfigjson, etc.
- **Keys**: Number of keys
- **Age**: Creation time

**Click on Secret** → See keys:
```
Keys:
  DB_PASSWORD: ****** (masked)
  JWT_SECRET: ****** (masked)
```

**Reveal Secret:**
Click "eye" icon → Shows base64-decoded value

**Security Note:**
Anyone with cluster access can view secrets in Lens!

---

## Network

### Services View

**Location:** Network → Services

**Service List:**
- **Name**: Service name
- **Namespace**: Namespace
- **Type**: ClusterIP, LoadBalancer, NodePort
- **Cluster IP**: Internal IP
- **Ports**: Port mappings (80:8080/TCP)
- **Age**: Creation time

**Service Types Explained:**

**ClusterIP (default):**
- Only accessible within cluster
- Other pods can reach it
- Not accessible from your laptop

**LoadBalancer:**
- External IP assigned
- Accessible from outside cluster
- On Docker Desktop, external IP is localhost

**NodePort:**
- Accessible on each node's IP
- High port number (30000-32767)

**Click on Service** → See:
- **Endpoints**: List of pod IPs backing this service
- **Selectors**: Label selectors to find pods
- **Ports**: Port mappings

---

### Endpoints View

**Location:** Network → Endpoints

Shows pod IPs that Services route traffic to.

**Example:**
```
Service: auth-service
Endpoints:
  - 10.1.0.45:80 (auth-service-abc123)
  - 10.1.0.67:80 (auth-service-def456)
```

**Use Cases:**
- **Debug service routing**: Check if service finds pods
- **Verify selectors**: Ensure labels match

---

### Ingresses View

**Location:** Network → Ingresses

**Ingress List:**
- **Name**: Ingress name
- **Namespace**: Namespace
- **Rules**: Number of routing rules
- **Age**: Creation time

**Click on Ingress** → See:
- **Hosts**: Domain names (freshharvest-market.local)
- **Paths**: URL paths and backend services
- **TLS**: SSL/TLS configuration (if any)

**Example:**
```
Host: freshharvest-market.local
  Path: /           → frontend:80
  
Host: freshharvest-market-api.local
  Path: /api/auth   → auth-service:80
  Path: /api/users  → user-service:80
  Path: /api        → gateway:80
```

---

## Storage

### Persistent Volumes (PVs)

**Location:** Storage → Persistent Volumes

Shows cluster-wide storage available.

**PV List:**
- **Name**: PV name
- **Capacity**: Storage size (10Gi)
- **Access Modes**: ReadWriteOnce, ReadOnlyMany, ReadWriteMany
- **Status**: Available, Bound, Released
- **Claim**: Which PVC is using it

---

### Persistent Volume Claims (PVCs)

**Location:** Storage → Persistent Volume Claims

Shows storage requests by pods.

**PVC List:**
- **Name**: PVC name
- **Namespace**: Namespace
- **Status**: Bound, Pending
- **Volume**: Which PV it's bound to
- **Capacity**: Requested size
- **Access Mode**: ReadWriteOnce, etc.

**Click on PVC** → See:
- **Volume**: Bound PV
- **StorageClass**: Storage type
- **Mounted By**: Which pods are using it

---

## Debugging Features

### Port Forwarding

**Access pod's port on localhost:**

1. Right-click on pod
2. Select "Forward Port"
3. Choose:
   - **Pod Port**: Container port (e.g., 80)
   - **Local Port**: Your laptop's port (e.g., 5000)
4. Click "Start"

**Result:**
```
http://localhost:5000 → Pod container:80
```

**Use Cases:**
- **Debug API**: Test endpoints locally
- **Database access**: Connect to DB pod with SQL client
- **Admin panels**: Access internal admin UIs

**Stop forwarding:**
Click "Stop" button.

---

### Resource Editing

**Edit any resource:**

1. Click on resource
2. Click "Edit" (pencil icon)
3. YAML editor opens
4. Make changes
5. Click "Save"

**Features:**
- **Syntax Highlighting**: YAML syntax colored
- **Validation**: Checks for errors before saving
- **Auto-complete**: Suggests field names
- **Error Messages**: Shows validation errors

**Use Cases:**
- **Quick fixes**: Change env var, increase replicas
- **Temporary changes**: Test config changes
- **Emergency**: Fix prod issue quickly

**Warning:**
Changes are not in Git! ArgoCD will revert them if self-heal is enabled.

---

### Cluster Shell

**Built-in kubectl terminal:**

**Location:** Cluster icon → Terminal

**Features:**
- Full kubectl access
- Your current kubeconfig context
- PowerShell or Bash (depending on OS)

**Common Commands:**
```bash
# Get resources
kubectl get pods -A
kubectl get deployments -n staging

# Describe resource
kubectl describe pod auth-service-abc123 -n staging

# Logs
kubectl logs -f auth-service-abc123 -n staging

# Port forward
kubectl port-forward svc/auth-service 5000:80 -n staging

# Apply manifest
kubectl apply -f deployment.yaml

# Delete resource
kubectl delete pod auth-service-abc123 -n staging
```

---

### Metrics and Monitoring

**Resource Usage Graphs:**

**Pod Metrics:**
- Click pod → Overview tab
- See CPU and Memory graphs
- Last hour of data
- Real-time updates

**Node Metrics:**
- Dashboard → Node section
- CPU, Memory, Disk, Network
- Historical trends

**Enable Metrics:**
If metrics don't show, install Metrics Server:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## Common Tasks

### Task 1: Find Why Pod is CrashLooping

**Steps:**
1. Workloads → Pods
2. Look for red status
3. Click pod
4. Check Events tab → Look for errors
5. Check Logs tab → Select "Previous" container
6. Read error message
7. Fix issue in code or config

**Common Causes:**
- Missing environment variable
- Database connection failed
- Wrong configuration
- Out of memory (OOMKilled)

---

### Task 2: Scale Deployment

**Steps:**
1. Workloads → Deployments
2. Click deployment
3. Overview tab → Click "Scale" button
4. Set new replica count (e.g., 5)
5. Click "Scale"
6. Watch Pods tab → New pods appear

**Result:**
Deployment scales from 2 to 5 replicas.

---

### Task 3: View Logs from Multiple Pods

**Steps:**
1. Workloads → Pods
2. Filter by label (e.g., app=auth-service)
3. Click first pod → Logs tab → Keep open
4. Right-click second pod → Open in new tab
5. Switch between tabs to compare logs

**Use Case:**
Debug issue affecting multiple pod replicas.

---

### Task 4: Debug Service Not Working

**Steps:**
1. Network → Services
2. Click service (e.g., auth-service)
3. Check **Endpoints** section
4. Should show pod IPs
5. If empty → Check selector labels
6. Go to deployment → Verify pod labels match service selector

**Common Issue:**
Service selector doesn't match pod labels:
```yaml
# Service selector
selector:
  app: auth-service

# Pod labels (wrong!)
labels:
  app: authentication-service  # Doesn't match!
```

---

### Task 5: Check ConfigMap Values

**Steps:**
1. Config → Config Maps
2. Filter namespace: staging
3. Click ConfigMap (e.g., auth-service-config)
4. See all key-value pairs
5. Verify values are correct

**If values are wrong:**
1. Edit in Git
2. ArgoCD syncs
3. Restart pods to load new values

---

### Task 6: Access Database Pod

**Steps:**
1. Workloads → Pods
2. Find database pod (e.g., postgres-0)
3. Click pod → Shell tab
4. Run SQL client:
```bash
psql -U postgres
\l  # List databases
\c electronic_paradise  # Connect to DB
\dt # List tables
SELECT * FROM users;
```

**Use Case:**
Verify data, run queries, debug data issues.

---

### Task 7: Check Resource Usage

**Steps:**
1. Dashboard → Top metrics
2. See cluster-wide CPU/Memory
3. Workloads → Pods
4. Sort by CPU or Memory column
5. Find resource-hungry pods
6. Click pod → Overview → See graphs

**Action:**
If pod uses too much:
- Increase limits in deployment
- Optimize application code
- Add more replicas (scale horizontally)

---

### Task 8: Restart Pods

**Steps:**
1. Workloads → Deployments
2. Click deployment
3. Scale to 0 replicas
4. Wait for pods to terminate
5. Scale back to 2 replicas
6. Wait for pods to start

**Alternative (faster):**
```bash
kubectl rollout restart deployment auth-service -n staging
```

Lens terminal → Run command

---

## Lens Pro Tips

### Keyboard Shortcuts

- **Ctrl+K**: Command palette (quick navigation)
- **Ctrl+T**: Switch between clusters
- **Ctrl+F**: Search in current view
- **Ctrl+R**: Refresh current view

### Multi-Cluster Management

**Add multiple clusters:**
1. Catalog view → Add Cluster
2. Choose kubeconfig file
3. Or paste kubeconfig YAML
4. Connect to cluster

**Switch between clusters:**
- Catalog view → Click cluster

**Use Case:**
Manage dev, staging, production clusters simultaneously.

---

### Hotbar (Quick Access)

**Pin frequently used resources:**
1. Right-click resource
2. "Add to Hotbar"
3. Hotbar appears at bottom
4. Click to quickly access

**Use Case:**
Quick access to specific deployments, pods, or services.

---

### Extensions

**Extend Lens functionality:**

**Settings → Extensions**

Popular extensions:
- **Resource Map**: Visual cluster topology
- **Pod Security**: Security policy checking
- **Cost Estimation**: Estimate cluster costs

---

## Troubleshooting Lens

### Cluster Not Connecting

**Check:**
1. Is Kubernetes running? (`kubectl cluster-info`)
2. Is kubeconfig valid? (`~/.kube/config`)
3. Firewall blocking connection?

**Fix:**
- Restart Docker Desktop
- Reconnect cluster in Lens
- Check kubeconfig context

---

### Metrics Not Showing

**Issue:** CPU/Memory graphs empty

**Fix:**
Install Metrics Server:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Wait 1-2 minutes for metrics to populate.

---

### Lens Slow or Laggy

**Causes:**
- Too many pods/resources
- Large log files
- Multiple clusters connected

**Fix:**
- Filter by namespace (reduce visible resources)
- Close unused cluster connections
- Restart Lens
- Increase Lens memory limit (Settings → Preferences)

---

## Next Steps

- **Practice**: Navigate all views, click everything
- **Break Things**: Delete pods, scale deployments, see what happens
- **Learn kubectl**: Lens is visual kubectl wrapper, learn both
- **Explore Extensions**: Add useful extensions

---

**Lens is your eyes into Kubernetes. Master it, and you'll debug 10x faster!**
