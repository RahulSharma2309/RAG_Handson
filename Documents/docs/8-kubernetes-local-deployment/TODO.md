# Local Kubernetes Deployment - TODO List

> **Learning Goal**: Deploy FreshHarvest Market to local Docker Desktop K8s using GitOps with ArgoCD

📖 For detailed explanations of each step, see [LEARNING.md](./LEARNING.md)

---

## Phase 1: Prerequisites & Environment Setup

### ☐ 1.1: Verify Docker Desktop Kubernetes

**Tasks:**
- [ ] Open Docker Desktop → Settings → Kubernetes
- [ ] Check "Enable Kubernetes" checkbox
- [ ] Click "Apply & Restart"
- [ ] Wait for Kubernetes status to show green (⬤ Running)
- [ ] Verify installation: `kubectl cluster-info`
- [ ] Verify node: `kubectl get nodes`
  - Expected: `docker-desktop   Ready   control-plane`

**Success Criteria**: You see "Kubernetes control plane is running at..." message

---

### ☐ 1.2: Install kubectl (if not already installed)

**Tasks:**
- [ ] Check if kubectl exists: `kubectl version --client`
- [ ] If not installed:
  - Windows: `choco install kubernetes-cli` or download from [kubernetes.io](https://kubernetes.io/docs/tasks/tools/)
- [ ] Verify context points to Docker Desktop: `kubectl config current-context`
  - Expected: `docker-desktop`

**Success Criteria**: kubectl commands work without errors

---

### ☐ 1.3: Install Lens Desktop UI

**Tasks:**
- [ ] Download Lens from [k8slens.dev](https://k8slens.dev/)
- [ ] Install Lens Desktop application
- [ ] Launch Lens
- [ ] Lens should auto-detect your Docker Desktop cluster
- [ ] Click on the cluster to connect
- [ ] Explore the Workloads → Pods view (should be empty except system pods)

**Success Criteria**: Lens shows your local cluster with kube-system namespace pods

---

## Phase 2: Kubernetes Namespace & RBAC Setup

### ☐ 2.1: Create Namespaces

**Tasks:**
- [ ] Create staging namespace: `kubectl create namespace staging`
- [ ] Create production namespace: `kubectl create namespace production`
- [ ] Create argocd namespace: `kubectl create namespace argocd`
- [ ] Verify in Lens: Settings → Namespaces → Select all three
- [ ] Verify via CLI: `kubectl get namespaces`

**Success Criteria**: All three namespaces appear in both Lens and kubectl output

---

### ☐ 2.2: Create GitHub Container Registry Secret

**Tasks:**
- [ ] Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- [ ] Click "Generate new token (classic)"
- [ ] Give it a name: "K8s Local GHCR Pull"
- [ ] Select scope: `read:packages`
- [ ] Generate and copy the token (save it securely!)
- [ ] Create secret for staging:
  ```powershell
  kubectl create secret docker-registry ghcr-secret `
    --docker-server=ghcr.io `
    --docker-username=YOUR_GITHUB_USERNAME `
    --docker-password=YOUR_GITHUB_TOKEN `
    --docker-email=YOUR_EMAIL `
    -n staging
  ```
- [ ] Create secret for production:
  ```powershell
  kubectl create secret docker-registry ghcr-secret `
    --docker-server=ghcr.io `
    --docker-username=YOUR_GITHUB_USERNAME `
    --docker-password=YOUR_GITHUB_TOKEN `
    --docker-email=YOUR_EMAIL `
    -n production
  ```
- [ ] Verify in Lens: Config → Secrets → Filter namespace → See ghcr-secret

**Success Criteria**: Secret visible in both namespaces in Lens

---

### ☐ 2.3: Create Service Accounts

**Tasks:**
- [ ] Navigate to repo: `cd C:\Users\Lenovo\source\repos\FreshHarvest-Market`
- [ ] Apply RBAC configs for staging:
  ```powershell
  kubectl apply -f infra/k8s/staging/rbac/ -n staging
  ```
- [ ] Apply RBAC configs for production:
  ```powershell
  kubectl apply -f infra/k8s/production/rbac/ -n production
  ```
- [ ] Verify in Lens: Config → Service Accounts → Check each namespace
- [ ] Verify via CLI: `kubectl get serviceaccounts -n staging`

**Success Criteria**: Service accounts for each microservice exist in both namespaces

---

## Phase 3: Install ArgoCD

### ☐ 3.1: Install ArgoCD Core Components

**Tasks:**
- [ ] Install ArgoCD:
  ```powershell
  kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
  ```
- [ ] Wait for installation (takes 2-3 minutes)
- [ ] Watch pods coming up:
  ```powershell
  kubectl get pods -n argocd -w
  ```
  - Press Ctrl+C when all pods show "Running" status
- [ ] Verify in Lens: Workloads → Pods → argocd namespace
  - Should see: argocd-server, argocd-repo-server, argocd-application-controller, argocd-redis, etc.

**Success Criteria**: All ArgoCD pods in Running state (5-7 pods total)

---

### ☐ 3.2: Access ArgoCD UI

**Tasks:**
- [ ] Port forward ArgoCD server:
  ```powershell
  kubectl port-forward svc/argocd-server -n argocd 8080:443
  ```
  - Keep this terminal window open
- [ ] Open new PowerShell window for admin password:
  ```powershell
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
  ```
- [ ] Copy the password
- [ ] Open browser: https://localhost:8080
  - Click "Advanced" → "Proceed to localhost" (self-signed cert warning)
- [ ] Login:
  - Username: `admin`
  - Password: (paste from above)
- [ ] Change password: User Info → Update Password

**Success Criteria**: You see ArgoCD dashboard with "Applications" view

---

### ☐ 3.3: Install ArgoCD CLI (Optional but Recommended)

**Tasks:**
- [ ] Download ArgoCD CLI:
  - Windows: Download from [GitHub releases](https://github.com/argoproj/argo-cd/releases/latest)
  - Look for `argocd-windows-amd64.exe`
- [ ] Rename to `argocd.exe` and add to PATH
- [ ] Verify: `argocd version`
- [ ] Login via CLI:
  ```powershell
  argocd login localhost:8080 --username admin --password YOUR_PASSWORD --insecure
  ```

**Success Criteria**: `argocd app list` command works (shows empty list for now)

---

## Phase 4: Configure Kubernetes Resources

### ☐ 4.1: Create ConfigMaps

**Tasks:**
- [ ] Review ConfigMap files in: `infra/k8s/staging/configmaps/`
- [ ] Apply all staging ConfigMaps:
  ```powershell
  kubectl apply -f infra/k8s/staging/configmaps/ -n staging
  ```
- [ ] Verify in Lens: Config → Config Maps → staging namespace
- [ ] Check each ConfigMap content in Lens UI
- [ ] Repeat for production:
  ```powershell
  kubectl apply -f infra/k8s/production/configmaps/ -n production
  ```

**Success Criteria**: ConfigMaps for all 7 services visible in Lens

---

### ☐ 4.2: Create Secrets

**Tasks:**
- [ ] Review Secret files in: `infra/k8s/staging/secrets/`
- [ ] **IMPORTANT**: Update secret values for local environment
  - Edit connection strings to point to local databases
  - Update JWT secrets if needed
- [ ] Apply all staging Secrets:
  ```powershell
  kubectl apply -f infra/k8s/staging/secrets/ -n staging
  ```
- [ ] Verify in Lens: Config → Secrets → staging namespace
- [ ] Click on a secret to verify (values will be base64 encoded)

**Success Criteria**: Secrets for all services exist and contain correct values

---

## Phase 5: Setup ArgoCD Applications

### ☐ 5.1: Connect GitHub Repository to ArgoCD

**Tasks:**
- [ ] In ArgoCD UI: Settings → Repositories → Connect Repo
- [ ] Choose connection method: HTTPS
- [ ] Repository URL: `https://github.com/RahulSharma2309/FreshHarvest-Market`
- [ ] Leave credentials empty (public repo)
- [ ] Click "Connect"
- [ ] Status should show "Successful"

**Success Criteria**: Repository appears in list with green "Successful" status

---

### ☐ 5.2: Create ArgoCD Application for Auth Service

**Tasks:**
- [ ] In ArgoCD UI: Applications → New App
- [ ] Fill in details:
  - **Application Name**: `auth-service-staging`
  - **Project**: `default`
  - **Sync Policy**: `Manual` (we'll enable auto later)
  - **Repository URL**: `https://github.com/RahulSharma2309/FreshHarvest-Market`
  - **Revision**: `main`
  - **Path**: `infra/k8s/staging/deployments/auth-service`
  - **Cluster URL**: `https://kubernetes.default.svc` (select from dropdown)
  - **Namespace**: `staging`
- [ ] Click "Create"
- [ ] App appears with status "OutOfSync" (expected - not deployed yet)
- [ ] Click on the app to see the resource tree
- [ ] Click "Sync" → "Synchronize"
- [ ] Watch deployment happen in real-time!
- [ ] Wait for status to show "Healthy" and "Synced"

**Success Criteria**: 
- Auth service pods running in Lens (staging namespace)
- ArgoCD shows green "Healthy" and "Synced" status
- Resource tree shows Deployment → ReplicaSet → Pods

---

### ☐ 5.3: Create Applications for Remaining Services

**Tasks:**
Repeat 5.2 for each service:

- [ ] `user-service-staging` (path: `infra/k8s/staging/deployments/user-service`)
- [ ] `product-service-staging` (path: `infra/k8s/staging/deployments/product-service`)
- [ ] `order-service-staging` (path: `infra/k8s/staging/deployments/order-service`)
- [ ] `payment-service-staging` (path: `infra/k8s/staging/deployments/payment-service`)
- [ ] `gateway-staging` (path: `infra/k8s/staging/deployments/gateway`)
- [ ] `frontend-staging` (path: `infra/k8s/staging/deployments/frontend`)

- [ ] Sync each application one by one
- [ ] Verify all pods are running in Lens

**Success Criteria**: 
- All 7 applications visible in ArgoCD dashboard
- All showing "Healthy" and "Synced" status
- All pods running in Lens staging namespace

---

### ☐ 5.4: Create Services (Networking)

**Tasks:**
- [ ] Apply all service definitions:
  ```powershell
  kubectl apply -f infra/k8s/staging/services/ -n staging
  ```
- [ ] Verify in Lens: Network → Services → staging namespace
- [ ] Check each service has endpoints:
  ```powershell
  kubectl get endpoints -n staging
  ```
- [ ] In Lens, click on a service to see which pods it routes to

**Success Criteria**: Each microservice has a corresponding ClusterIP service with endpoints

---

## Phase 6: Install and Configure Ingress

### ☐ 6.1: Install NGINX Ingress Controller

**Tasks:**
- [ ] Install NGINX Ingress for Docker Desktop:
  ```powershell
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
  ```
- [ ] Wait for ingress controller to be ready:
  ```powershell
  kubectl wait --namespace ingress-nginx `
    --for=condition=ready pod `
    --selector=app.kubernetes.io/component=controller `
    --timeout=120s
  ```
- [ ] Verify in Lens: Workloads → Pods → ingress-nginx namespace
- [ ] Check service: `kubectl get svc -n ingress-nginx`
  - Look for `ingress-nginx-controller` with LoadBalancer type

**Success Criteria**: Ingress controller pod running, LoadBalancer service has localhost IP

---

### ☐ 6.2: Configure Ingress Rules

**Tasks:**
- [ ] Apply ingress configuration:
  ```powershell
  kubectl apply -f infra/k8s/staging/ingress/ -n staging
  ```
- [ ] Verify in Lens: Network → Ingresses → staging namespace
- [ ] Check ingress details: `kubectl get ingress -n staging`
- [ ] Note the HOST rules configured

**Success Criteria**: Ingress resource created with routing rules visible

---

### ☐ 6.3: Configure Local DNS (Hosts File)

**Tasks:**
- [ ] Open Notepad as Administrator
- [ ] Open file: `C:\Windows\System32\drivers\etc\hosts`
- [ ] Add these lines at the end:
  ```
  127.0.0.1 freshharvest-market.local
  127.0.0.1 freshharvest-market-api.local
  ```
- [ ] Save and close
- [ ] Verify DNS works:
  ```powershell
  ping freshharvest-market.local
  ```
  - Should respond from 127.0.0.1

**Success Criteria**: Ping resolves to localhost

---

### ☐ 6.4: Test Application Access

**Tasks:**
- [ ] Open browser: http://freshharvest-market.local
  - Should show frontend (may take a minute to load)
- [ ] Open browser: http://freshharvest-market-api.local/api/health
  - Should show gateway health endpoint
- [ ] Check logs in Lens:
  - Click on frontend pod → Logs tab
  - Should see application logs

**Success Criteria**: Both frontend and API gateway accessible via browser

---

## Phase 7: Configure GitOps Automation

### ☐ 7.1: Enable Auto-Sync for Staging Applications

**Tasks:**
For each staging application in ArgoCD UI:

- [ ] Click on application (e.g., auth-service-staging)
- [ ] Click "App Details" button (top right)
- [ ] Click "Edit"
- [ ] Under "Sync Policy":
  - Check "Automatic"
  - Check "Prune Resources" (delete resources removed from Git)
  - Check "Self Heal" (revert manual changes)
- [ ] Click "Save"
- [ ] Repeat for all 7 staging applications

**Success Criteria**: All staging apps show "Auto-Sync: Enabled" in ArgoCD UI

---

### ☐ 7.2: Test GitOps Workflow - Manual Change

**Tasks:**
- [ ] In Lens, manually edit a deployment:
  - Workloads → Deployments → auth-service (staging)
  - Click Edit (pencil icon)
  - Change replicas from 2 to 3
  - Click "Save"
- [ ] Watch what happens:
  - Deployment scales to 3 pods
  - Within 3 minutes, ArgoCD detects drift
  - ArgoCD reverts it back to 2 pods (as defined in Git)
- [ ] In ArgoCD UI:
  - Click on auth-service-staging
  - Go to "History" tab
  - See the self-heal event

**Success Criteria**: Self-heal reverts manual change back to Git state

---

### ☐ 7.3: Test GitOps Workflow - Git Change

**Tasks:**
- [ ] Open your repo in VS Code
- [ ] Edit: `infra/k8s/staging/deployments/auth-service/deployment.yaml`
- [ ] Change CPU limit from `500m` to `600m`
- [ ] Commit and push:
  ```powershell
  git add infra/k8s/staging/deployments/auth-service/deployment.yaml
  git commit -m "test: increase auth-service CPU to 600m"
  git push origin main
  ```
- [ ] In ArgoCD UI:
  - Watch auth-service-staging application
  - After ~3 minutes (default poll interval), status changes to "OutOfSync"
  - ArgoCD auto-syncs
  - Status returns to "Synced"
- [ ] In Lens:
  - Check auth-service deployment
  - Verify CPU limit is now 600m

**Success Criteria**: Git change automatically deployed to K8s within 3 minutes

---

## Phase 8: Integrate with CI/CD Pipeline

### ☐ 8.1: Understand Current CI/CD Flow

**Tasks:**
- [ ] Review: `.github/workflows/ci.yml`
  - Understand what happens when PR merges to main
  - Note: CI updates image tags in `infra/k8s/staging/deployments/*/deployment.yaml`
- [ ] Review: `.github/workflows/cd-staging.yml`
  - Note: Currently uses `kubectl apply` (push-based)
  - This is now redundant - ArgoCD handles deployment (pull-based)

**Success Criteria**: You understand the difference between push and pull-based deployment

---

### ☐ 8.2: Test Full CI/CD + GitOps Flow

**Tasks:**
- [ ] Create a test branch:
  ```powershell
  git checkout -b test/gitops-flow
  ```
- [ ] Make a code change (any minor change to trigger version bump)
- [ ] Commit and push:
  ```powershell
  git add .
  git commit -m "feat: test gitops integration"
  git push origin test/gitops-flow
  ```
- [ ] Create PR on GitHub
- [ ] Wait for CI to pass (builds images, but doesn't push)
- [ ] Merge PR to main
- [ ] Watch the flow:
  1. **CI Pipeline runs** (GitHub Actions)
     - Builds Docker images
     - Pushes to GHCR with new version (e.g., v1.2.4)
     - Updates image tags in staging deployment YAMLs
     - Commits changes back to main
  2. **ArgoCD detects Git change** (within 3 minutes)
     - Shows "OutOfSync" in UI
     - Auto-syncs applications
  3. **Kubernetes deployment happens**
     - Pulls new images from GHCR
     - Rolls out updated pods
  4. **Watch in Lens**
     - See old pods terminating
     - See new pods starting
     - Check logs of new pods
  5. **ArgoCD shows "Synced" and "Healthy"**

**Success Criteria**: 
- New version deployed without running `kubectl apply` manually
- You observed the entire flow from Git commit to running pods

---

## Phase 9: Master Lens UI

### ☐ 9.1: Explore Lens Workloads View

**Tasks:**
- [ ] In Lens, navigate to: Workloads → Deployments
- [ ] Filter by namespace: staging
- [ ] Click on `auth-service` deployment
- [ ] Explore tabs:
  - **Overview**: Replicas, strategy, selectors
  - **Pods**: Live list of pod instances
  - **Events**: Recent K8s events for this deployment
  - **Scale**: Scale replicas up/down
- [ ] Click on a Pod:
  - **Overview**: Status, IP, node, containers
  - **Logs**: Live tail of container logs
  - **Shell**: Open terminal inside container (try: `ls`, `pwd`)

**Success Criteria**: You can navigate between deployments, pods, and logs confidently

---

### ☐ 9.2: Use Lens for Debugging

**Tasks:**
- [ ] Simulate a pod crash:
  - In Lens, open shell for auth-service pod
  - Run: `kill 1` (kills the main process)
  - Watch pod restart automatically
- [ ] View crash events:
  - Go to deployment → Events tab
  - See "Pod Crashed" or "BackOff" events
- [ ] Check logs of crashed pod:
  - Lens keeps logs of previous container
  - Logs tab → Dropdown → Select "Previous"
- [ ] Use port-forwarding:
  - Right-click on auth-service pod
  - "Forward Port"
  - Choose local port (e.g., 5000)
  - Access: http://localhost:5000/api/health

**Success Criteria**: You successfully debugged a pod crash and used port-forwarding

---

### ☐ 9.3: Monitor Resource Usage in Lens

**Tasks:**
- [ ] In Lens: Workloads → Pods → staging namespace
- [ ] Enable metrics view (top toolbar)
- [ ] Observe CPU and Memory usage graphs
- [ ] Click on a pod → Metrics tab
- [ ] Generate some load:
  - Make multiple requests to your API
  - Watch CPU/memory spike in real-time

**Success Criteria**: You can see real-time resource metrics for pods

---

## Phase 10: Production Setup (Optional)

### ☐ 10.1: Create Production Applications in ArgoCD

**Tasks:**
- [ ] Repeat Phase 5 steps for production namespace
- [ ] Create applications:
  - `auth-service-production`
  - `user-service-production`
  - (etc. for all 7 services)
- [ ] Use path: `infra/k8s/production/deployments/*`
- [ ] Set namespace: `production`
- [ ] **Important**: Keep sync policy as **Manual** for production
  - No auto-sync for production!
  - Manual approval required for prod deployments

**Success Criteria**: All production apps created but NOT synced yet (OutOfSync status)

---

### ☐ 10.2: Test Production Deployment Flow

**Tasks:**
- [ ] Merge a feature to main (triggers CI)
- [ ] CI updates both staging and production manifest files
- [ ] Staging deploys automatically (via ArgoCD auto-sync)
- [ ] Production shows "OutOfSync" (waiting for manual approval)
- [ ] In ArgoCD UI:
  - Click on production application
  - Review changes in "Diff" tab
  - Click "Sync" when ready
  - Choose "Synchronize"
- [ ] Watch production deployment

**Success Criteria**: Production requires manual sync, giving you control

---

## Phase 11: Advanced Configurations (Optional)

### ☐ 11.1: Configure ArgoCD Sync Waves

**Tasks:**
- [ ] Learn about sync waves: https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/
- [ ] Add annotations to control deployment order
  - Deploy database migrations first (wave 0)
  - Deploy backend services (wave 1)
  - Deploy frontend (wave 2)
  - Deploy ingress (wave 3)

**Success Criteria**: Services deploy in correct order

---

### ☐ 11.2: Setup Slack/Discord Notifications

**Tasks:**
- [ ] In ArgoCD: Settings → Notifications
- [ ] Configure webhook for Slack/Discord
- [ ] Get notified when:
  - Sync succeeds
  - Sync fails
  - Application health degrades

**Success Criteria**: Receive notification on successful sync

---

### ☐ 11.3: Explore ArgoCD ApplicationSets

**Tasks:**
- [ ] Learn about ApplicationSets (for managing multiple similar apps)
- [ ] Create one ApplicationSet to manage all 7 staging services
- [ ] Benefit: Update one file instead of 7 individual applications

**Success Criteria**: ApplicationSet creates all 7 applications automatically

---

## Phase 12: Validation & Testing

### ☐ 12.1: End-to-End Flow Test

**Tasks:**
- [ ] Access frontend: http://freshharvest-market.local
- [ ] Test user flows:
  - [ ] Sign up new user
  - [ ] Login
  - [ ] Browse products
  - [ ] Add to cart
  - [ ] Checkout
  - [ ] View order history
- [ ] Check logs in Lens for each service interaction
- [ ] Verify data flow across microservices

**Success Criteria**: Complete user journey works without errors

---

### ☐ 12.2: Disaster Recovery Test

**Tasks:**
- [ ] Delete all pods in staging:
  ```powershell
  kubectl delete pods --all -n staging
  ```
- [ ] Watch in ArgoCD and Lens:
  - Deployments automatically recreate pods
  - Services come back up
  - Application remains healthy
- [ ] Delete an entire deployment:
  ```powershell
  kubectl delete deployment auth-service -n staging
  ```
- [ ] ArgoCD detects missing resource (OutOfSync)
- [ ] ArgoCD self-heals (recreates deployment)

**Success Criteria**: All resources automatically recover to Git state

---

### ☐ 12.3: Rollback Test

**Tasks:**
- [ ] In ArgoCD UI, click on an application
- [ ] Go to "History" tab
- [ ] See list of previous syncs
- [ ] Click "Rollback" on a previous version
- [ ] Watch application revert to older version
- [ ] Verify in Lens that image tag changed
- [ ] Rollback to latest version again

**Success Criteria**: Successfully rollback and forward deployments

---

## 🎓 Completion Checklist

You've mastered local Kubernetes with GitOps when you can:

- [ ] Explain the difference between push-based (CI/CD) and pull-based (GitOps) deployments
- [ ] Deploy a new service by just committing a YAML file to Git
- [ ] Debug pod issues using Lens UI
- [ ] Understand ArgoCD's sync, prune, and self-heal features
- [ ] Manually rollback a deployment using ArgoCD
- [ ] Monitor application health in real-time
- [ ] Explain the flow from Git commit to running pod

---

## 📚 Next Steps

After completing this guide:

1. **Explore Helm**: Package your manifests as Helm charts for ArgoCD
2. **Multi-cluster setup**: Add a remote cluster to ArgoCD
3. **Advanced GitOps**: Sealed Secrets, External Secrets Operator
4. **Observability**: Add Prometheus + Grafana for metrics
5. **Service Mesh**: Explore Istio or Linkerd

---

**Questions?** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or [LEARNING.md](./LEARNING.md) for deeper explanations.
