# Kubernetes Local Deployment - Troubleshooting Guide

Common issues and their solutions when deploying to local Docker Desktop Kubernetes with ArgoCD.

---

## Table of Contents

1. [Docker Desktop & Kubernetes Issues](#docker-desktop--kubernetes-issues)
2. [ArgoCD Issues](#argocd-issues)
3. [Pod Issues](#pod-issues)
4. [Networking Issues](#networking-issues)
5. [Image Pull Issues](#image-pull-issues)
6. [Resource Issues](#resource-issues)
7. [Configuration Issues](#configuration-issues)
8. [ArgoCD Sync Issues](#argocd-sync-issues)

---

## Docker Desktop & Kubernetes Issues

### Issue: Kubernetes Won't Start

**Symptoms:**
- Kubernetes icon shows yellow or red in Docker Desktop
- kubectl commands fail with "connection refused"

**Diagnosis:**
```powershell
kubectl cluster-info
# Error: Unable to connect to the server: dial tcp 127.0.0.1:6443: connect: connection refused
```

**Solutions:**

**1. Restart Kubernetes:**
- Docker Desktop → Settings → Kubernetes
- Uncheck "Enable Kubernetes"
- Click "Apply & Restart"
- Wait 30 seconds
- Check "Enable Kubernetes" again
- Click "Apply & Restart"
- Wait 2-3 minutes

**2. Reset Kubernetes Cluster:**
- Docker Desktop → Troubleshoot → Reset Kubernetes Cluster
- **Warning**: Deletes all resources!
- Wait 3-5 minutes for clean install

**3. Restart Docker Desktop:**
- Right-click Docker Desktop icon → Quit
- Restart Docker Desktop
- Wait for Kubernetes to start

**4. Check Resources:**
- Docker Desktop → Settings → Resources
- Ensure enough RAM allocated (minimum 4GB, recommended 8GB)
- Ensure enough CPU (minimum 2 cores, recommended 4)

---

### Issue: kubectl Command Not Found

**Symptoms:**
```powershell
kubectl : The term 'kubectl' is not recognized
```

**Solutions:**

**1. Install kubectl:**
```powershell
# With Chocolatey
choco install kubernetes-cli

# Or download from https://kubernetes.io/docs/tasks/tools/
```

**2. Check PATH:**
```powershell
$env:PATH
# Should include: C:\Program Files\Docker\Docker\resources\bin
```

**3. Restart Terminal:**
After installation, close and reopen PowerShell.

---

### Issue: Wrong Kubernetes Context

**Symptoms:**
- Commands work but affect wrong cluster
- ArgoCD deploys to wrong cluster

**Diagnosis:**
```powershell
kubectl config current-context
# Shows: minikube (wrong!)
```

**Solution:**
```powershell
# List contexts
kubectl config get-contexts

# Switch to docker-desktop
kubectl config use-context docker-desktop

# Verify
kubectl config current-context
# Should show: docker-desktop
```

---

## ArgoCD Issues

### Issue: Can't Access ArgoCD UI

**Symptoms:**
- https://localhost:8080 doesn't load
- "This site can't be reached"

**Diagnosis:**
```powershell
# Check if ArgoCD pods are running
kubectl get pods -n argocd

# Check port forward
netstat -ano | findstr :8080
```

**Solutions:**

**1. Verify ArgoCD is Running:**
```powershell
kubectl get pods -n argocd
# All pods should be Running
```

If pods are not running:
```powershell
kubectl get pods -n argocd --watch
# Wait for all to show Running status
```

**2. Start Port Forward:**
```powershell
# Kill existing port forward (if any)
taskkill /F /IM kubectl.exe

# Start new port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**3. Try Different Port:**
If 8080 is in use:
```powershell
kubectl port-forward svc/argocd-server -n argocd 8081:443
# Access: https://localhost:8081
```

**4. Check Firewall:**
- Windows Defender Firewall might block localhost
- Add exception for kubectl.exe

---

### Issue: ArgoCD Login Fails

**Symptoms:**
- "Invalid username or password"
- Can't get initial password

**Solutions:**

**1. Get Initial Password:**
```powershell
# For PowerShell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```

**2. Reset Admin Password:**
```powershell
# Via CLI (if you have access)
argocd account update-password --account admin --new-password NEW_PASSWORD

# Via kubectl
kubectl -n argocd delete secret argocd-initial-admin-secret
kubectl -n argocd rollout restart deployment argocd-server
# New password will be generated
```

**3. Check Username:**
- Username is `admin` (lowercase)
- Password is case-sensitive

---

### Issue: ArgoCD Application Stuck Syncing

**Symptoms:**
- Application shows "Syncing" forever
- Progress bar doesn't move

**Diagnosis:**
```powershell
# Check ArgoCD controller logs
kubectl logs -n argocd deployment/argocd-application-controller --tail=100
```

**Solutions:**

**1. Refresh Application:**
- ArgoCD UI → Application → Refresh button
- Or CLI: `argocd app get APP_NAME --refresh`

**2. Hard Refresh:**
- ArgoCD UI → App Details → Edit
- Change something (e.g., add annotation)
- Save
- Revert change
- Save again

**3. Delete and Recreate Sync:**
- ArgoCD UI → Application → Terminate Sync
- Click "Sync" again

**4. Check Resource Hooks:**
If using sync hooks (PreSync, PostSync):
```powershell
kubectl get jobs -n NAMESPACE
# Check if hook jobs are stuck
```

Delete stuck jobs:
```powershell
kubectl delete job HOOK_JOB_NAME -n NAMESPACE
```

---

## Pod Issues

### Issue: ImagePullBackOff

**Symptoms:**
```
Pod status: ImagePullBackOff or ErrImagePull
```

**Diagnosis:**
```powershell
kubectl describe pod POD_NAME -n NAMESPACE
# Look for: Failed to pull image "ghcr.io/.../auth:v1.2.3": unauthorized
```

**Common Causes & Solutions:**

**1. Missing imagePullSecret:**
```powershell
# Check if secret exists
kubectl get secret ghcr-secret -n NAMESPACE

# If missing, create it
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n NAMESPACE
```

**2. Wrong Image Tag:**
```powershell
# Check if image exists in GHCR
# Go to: https://github.com/YOUR_USERNAME?tab=packages

# Or try pulling manually
docker pull ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.2.3
```

If image doesn't exist:
- Check CI pipeline logs
- Verify image was pushed successfully
- Check image tag in deployment YAML

**3. Private Repository:**
Ensure GitHub PAT has `read:packages` scope.

**4. Wrong Registry:**
Check deployment YAML:
```yaml
image: ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.2.3
#      ^^^ Correct registry
```

---

### Issue: CrashLoopBackOff

**Symptoms:**
```
Pod status: CrashLoopBackOff
Restarts: 5 (increasing)
```

**Diagnosis:**
```powershell
# Check current logs
kubectl logs POD_NAME -n NAMESPACE

# Check previous container logs (before crash)
kubectl logs POD_NAME -n NAMESPACE --previous
```

**Common Causes & Solutions:**

**1. Application Error:**
```
Error: Cannot connect to database
```
**Fix:**
- Check database connection string in Secrets
- Verify database pod is running
- Check network connectivity

**2. Missing Environment Variable:**
```
Error: Environment variable 'JWT_SECRET' not found
```
**Fix:**
- Check ConfigMap or Secret
- Verify env vars in deployment YAML
- Ensure ConfigMap/Secret is applied

**3. Port Already in Use:**
```
Error: Address already in use (port 80)
```
**Fix:**
- Check if multiple containers bind to same port
- Verify containerPort in deployment

**4. Startup Command Failed:**
```powershell
# Check pod events
kubectl describe pod POD_NAME -n NAMESPACE
# Look for: BackOff restarting failed container
```

**Fix:**
- Verify Docker image entrypoint
- Check if app starts locally: `docker run IMAGE`

---

### Issue: Pod Pending Forever

**Symptoms:**
```
Pod status: Pending
Age: 10 minutes
```

**Diagnosis:**
```powershell
kubectl describe pod POD_NAME -n NAMESPACE
# Look for events at bottom
```

**Common Causes & Solutions:**

**1. Insufficient Resources:**
```
Events:
  Warning FailedScheduling: 0/1 nodes are available: 1 Insufficient cpu
```
**Fix:**
- Reduce CPU/memory requests in deployment
- Increase Docker Desktop resources (Settings → Resources)
- Delete unused pods to free resources

**2. ImagePullBackOff:**
See [ImagePullBackOff section](#issue-imagepullbackoff)

**3. Node Not Ready:**
```powershell
kubectl get nodes
# Should show: docker-desktop Ready
```

If not Ready, restart Docker Desktop.

**4. Pending PVC:**
If pod mounts PersistentVolumeClaim:
```powershell
kubectl get pvc -n NAMESPACE
# Should show: Bound
```

If Pending, check PV:
```powershell
kubectl get pv
# Should have Available PV with matching size
```

---

### Issue: Pod OOMKilled (Out of Memory)

**Symptoms:**
```
Pod status: OOMKilled or Error
Events: Container exceeded memory limit
```

**Diagnosis:**
```powershell
kubectl describe pod POD_NAME -n NAMESPACE
# Look for: OOMKilled
```

**Solution:**
Increase memory limit in deployment:
```yaml
resources:
  limits:
    memory: "512Mi"  # Increase from 256Mi
```

Or optimize application memory usage.

---

## Networking Issues

### Issue: Service Has No Endpoints

**Symptoms:**
```powershell
kubectl get endpoints SERVICE_NAME -n NAMESPACE
# Shows: <none>
```

**Diagnosis:**
Service can't find pods.

**Solutions:**

**1. Check Selector Match:**
```powershell
# Get service selector
kubectl get svc SERVICE_NAME -n NAMESPACE -o yaml | grep -A 5 selector

# Get pod labels
kubectl get pods -n NAMESPACE --show-labels
```

Service selector must match pod labels:
```yaml
# Service
selector:
  app: auth-service

# Pod labels (must match!)
labels:
  app: auth-service
```

**Fix:**
Update service selector or pod labels.

**2. Pods Not Ready:**
```powershell
kubectl get pods -n NAMESPACE
# Check Ready column: Should be 1/1 or 2/2
```

If not ready, debug pod issues first.

---

### Issue: Can't Access Service from Another Pod

**Symptoms:**
```bash
# Inside pod
curl http://auth-service
# Error: Could not resolve host
```

**Solutions:**

**1. Use Namespace in DNS:**
```bash
# Correct: Include namespace
curl http://auth-service.staging.svc.cluster.local

# Or if both pods in same namespace
curl http://auth-service
```

**2. Check Service Exists:**
```powershell
kubectl get svc -n NAMESPACE
```

**3. Check DNS:**
```powershell
# From pod shell
nslookup auth-service
# Should return service IP
```

If DNS fails:
```powershell
# Check CoreDNS
kubectl get pods -n kube-system | grep coredns
# Should be Running
```

---

### Issue: Ingress Not Working

**Symptoms:**
- http://freshharvest-market.local doesn't load
- "This site can't be reached"

**Diagnosis:**
```powershell
# Check ingress controller
kubectl get pods -n ingress-nginx
# Should show running ingress-nginx-controller pod

# Check ingress resource
kubectl get ingress -n NAMESPACE
# Should show ADDRESS (usually localhost for Docker Desktop)

# Check hosts file
notepad C:\Windows\System32\drivers\etc\hosts
# Should have: 127.0.0.1 freshharvest-market.local
```

**Solutions:**

**1. Install Ingress Controller:**
```powershell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

**2. Wait for Ingress Controller:**
```powershell
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

**3. Fix Hosts File:**
Run Notepad as Administrator:
```
# Add these lines
127.0.0.1 freshharvest-market.local
127.0.0.1 freshharvest-market-api.local
```

**4. Check Ingress Rules:**
```powershell
kubectl describe ingress INGRESS_NAME -n NAMESPACE
# Verify rules are correct
```

**5. Check Backend Service:**
```powershell
kubectl get svc -n NAMESPACE
# Verify services exist and have endpoints
```

**6. Test Direct Service Access:**
```powershell
kubectl port-forward svc/frontend 8000:80 -n staging
# Try: http://localhost:8000
```

If direct access works, issue is with Ingress.

---

## Image Pull Issues

### Issue: Rate Limit Exceeded (Docker Hub)

**Symptoms:**
```
Error: toomanyrequests: You have reached your pull rate limit
```

**Solution:**
Use GHCR instead of Docker Hub, or authenticate:
```powershell
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_DOCKERHUB_USERNAME \
  --docker-password=YOUR_DOCKERHUB_TOKEN \
  -n NAMESPACE
```

---

### Issue: Wrong Image Architecture

**Symptoms:**
```
Error: image's platform (linux/amd64) does not match the expected platform (windows/amd64)
```

**Solution:**
Build multi-platform images:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t IMAGE .
```

For Docker Desktop, ensure using Linux containers:
- Docker Desktop → Settings → General
- Check "Use WSL 2 based engine" or ensure "Linux containers"

---

## Resource Issues

### Issue: Cluster Running Out of Resources

**Symptoms:**
- New pods stuck Pending
- Nodes show pressure (MemoryPressure, DiskPressure)

**Diagnosis:**
```powershell
kubectl top nodes
kubectl top pods -A
```

**Solutions:**

**1. Increase Docker Desktop Resources:**
- Docker Desktop → Settings → Resources
- Increase Memory (8GB recommended)
- Increase CPU (4 cores recommended)
- Click "Apply & Restart"

**2. Delete Unused Resources:**
```powershell
# Delete completed pods
kubectl delete pod --field-selector=status.phase==Succeeded -A

# Delete failed pods
kubectl delete pod --field-selector=status.phase==Failed -A

# Delete unused namespaces
kubectl delete namespace OLD_NAMESPACE
```

**3. Reduce Resource Requests:**
In deployment YAML:
```yaml
resources:
  requests:
    memory: "128Mi"  # Reduce from 256Mi
    cpu: "50m"       # Reduce from 100m
```

---

### Issue: Disk Pressure

**Symptoms:**
```
Node: DiskPressure
```

**Solutions:**

**1. Clean Docker Images:**
```powershell
docker system prune -a --volumes
# WARNING: Deletes all unused images and volumes
```

**2. Increase Docker Desktop Disk:**
- Docker Desktop → Settings → Resources → Disk image size
- Increase limit
- Restart

---

## Configuration Issues

### Issue: ConfigMap Changes Not Reflected

**Symptoms:**
- Updated ConfigMap
- Pod still uses old values

**Cause:**
Pods load ConfigMap values at startup (for env vars).

**Solution:**
Restart pods:
```powershell
kubectl rollout restart deployment DEPLOYMENT_NAME -n NAMESPACE
```

Or scale to 0 and back:
```powershell
kubectl scale deployment DEPLOYMENT_NAME --replicas=0 -n NAMESPACE
kubectl scale deployment DEPLOYMENT_NAME --replicas=2 -n NAMESPACE
```

**Alternative:**
Use ConfigMap as volume mount (updates automatically, ~1 min delay).

---

### Issue: Secret Not Found

**Symptoms:**
```
Error: secret "auth-service-db-secret" not found
```

**Diagnosis:**
```powershell
kubectl get secrets -n NAMESPACE
```

**Solutions:**

**1. Create Missing Secret:**
```powershell
kubectl apply -f infra/k8s/NAMESPACE/secrets/auth-service-secret.yaml
```

**2. Check Namespace:**
Secret must be in same namespace as pod.

**3. Verify Secret Name:**
Match secret name in deployment:
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: auth-service-db-secret  # Must match actual secret name
        key: DB_PASSWORD
```

---

## ArgoCD Sync Issues

### Issue: Application OutOfSync but No Changes

**Symptoms:**
- ArgoCD shows OutOfSync
- Git and cluster look the same

**Diagnosis:**
Click "Diff" tab in ArgoCD → See what's different

**Common Causes:**

**1. Default Values:**
Kubernetes adds default values not in Git:
```yaml
# Git
spec:
  containers:
    - name: app

# Cluster (with defaults)
spec:
  containers:
    - name: app
      terminationMessagePath: /dev/termination-log  # Default added
```

**Solution:**
Ignore these fields in ArgoCD:
```yaml
# In Application or argocd-cm ConfigMap
spec:
  ignoreDifferences:
    - kind: Deployment
      jsonPointers:
        - /spec/template/spec/containers/0/terminationMessagePath
```

**2. Manual Changes:**
Someone ran kubectl commands.

**Solution:**
- Enable self-heal to auto-revert
- Or manually sync to revert

---

### Issue: Prune Deletes Wrong Resources

**Symptoms:**
- ArgoCD deletes resources you want to keep

**Cause:**
Prune deletes resources not in Git.

**Solution:**

**1. Add Annotation to Skip Prune:**
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-options: Prune=false
```

**2. Disable Prune:**
```yaml
syncPolicy:
  automated:
    prune: false  # Manual deletion only
```

**3. Use Separate Namespace:**
Keep resources ArgoCD shouldn't manage in different namespace.

---

### Issue: Sync Fails with "Resource Already Exists"

**Symptoms:**
```
Error: resource already exists and is not managed by ArgoCD
```

**Cause:**
Resource was created manually (not by ArgoCD).

**Solutions:**

**1. Delete and Recreate:**
```powershell
kubectl delete RESOURCE_TYPE RESOURCE_NAME -n NAMESPACE
# Then sync in ArgoCD
```

**2. Adopt Existing Resource:**
```yaml
# Add annotation to existing resource
metadata:
  annotations:
    argocd.argoproj.io/tracking-id: APP_NAME:apps/Deployment:NAMESPACE/RESOURCE_NAME
```

---

## Getting Help

### Enable Debug Logging

**ArgoCD:**
```powershell
# Increase log level
kubectl edit configmap argocd-cm -n argocd
# Add: data.application.logging.level: debug

# Restart controller
kubectl rollout restart deployment argocd-application-controller -n argocd

# View logs
kubectl logs -f deployment/argocd-application-controller -n argocd
```

**Application Pod:**
```powershell
kubectl logs -f POD_NAME -n NAMESPACE
```

---

### Collect Diagnostic Info

```powershell
# Cluster info
kubectl cluster-info dump > cluster-info.txt

# All resources in namespace
kubectl get all -n NAMESPACE -o yaml > resources.yaml

# Events
kubectl get events -n NAMESPACE --sort-by='.lastTimestamp' > events.txt

# Logs
kubectl logs POD_NAME -n NAMESPACE --previous > pod-logs.txt
```

---

### Useful Commands

```powershell
# Check node status
kubectl get nodes -o wide

# Check all pods
kubectl get pods -A

# Check resource usage
kubectl top nodes
kubectl top pods -A

# Check API server
kubectl get --raw /healthz

# Check component status
kubectl get componentstatuses

# Describe everything
kubectl describe pod POD_NAME -n NAMESPACE
kubectl describe svc SERVICE_NAME -n NAMESPACE
kubectl describe ingress INGRESS_NAME -n NAMESPACE
```

---

## When All Else Fails

### Nuclear Option: Reset Everything

**1. Delete All Resources:**
```powershell
kubectl delete namespace staging
kubectl delete namespace production
kubectl delete namespace argocd
```

**2. Reset Kubernetes:**
- Docker Desktop → Troubleshoot → Reset Kubernetes Cluster

**3. Start Fresh:**
Follow [TODO.md](./TODO.md) from scratch.

---

**Remember:** Breaking things is part of learning. Don't be afraid to experiment and fail - you're local, nothing is at risk!
