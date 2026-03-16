# ArgoCD Complete Guide

Comprehensive guide to understanding and using ArgoCD for GitOps deployments.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [UI Walkthrough](#ui-walkthrough)
3. [Application Lifecycle](#application-lifecycle)
4. [Sync Strategies](#sync-strategies)
5. [Health Assessment](#health-assessment)
6. [Common Operations](#common-operations)
7. [Best Practices](#best-practices)

---

## Core Concepts

### What is GitOps?

**GitOps = Operations by Pull Request**

Traditional:
```
Developer → CI/CD pushes → Kubernetes
```

GitOps:
```
Developer → Git commit → ArgoCD pulls → Kubernetes
```

**Principles:**
1. **Declarative**: System state described declaratively (YAML)
2. **Versioned**: State stored in Git (version control)
3. **Immutable**: New versions, not in-place changes
4. **Pulled**: ArgoCD pulls from Git, not pushed from CI
5. **Continuously Reconciled**: ArgoCD ensures actual == desired state

---

### ArgoCD Application

The **Application** is ArgoCD's core concept.

**What it represents:**
- A deployable unit (microservice, helm chart, etc.)
- Link between Git repository and Kubernetes cluster
- Sync configuration and policies

**Anatomy:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: auth-service-staging      # Unique name
  namespace: argocd               # Always in argocd namespace
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Cleanup on delete
spec:
  # Where to get manifests
  source:
    repoURL: https://github.com/RahulSharma2309/FreshHarvest-Market
    targetRevision: main           # Branch, tag, or commit SHA
    path: infra/k8s/staging/deployments/auth-service  # Folder with YAMLs
  
  # Where to deploy
  destination:
    server: https://kubernetes.default.svc  # Target cluster
    namespace: staging                      # Target namespace
  
  # How to deploy
  project: default                 # Project for grouping/RBAC
  
  syncPolicy:
    automated:                     # Auto-sync settings
      prune: true                  # Delete removed resources
      selfHeal: true               # Revert manual changes
      allowEmpty: false            # Fail if path is empty
    
    syncOptions:
      - CreateNamespace=true       # Create namespace if missing
      - PrunePropagationPolicy=foreground
      - PruneLast=false
    
    retry:
      limit: 5                     # Retry failed syncs
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

---

## UI Walkthrough

### Dashboard View

**Location:** https://localhost:8080/applications

**Elements:**

**1. Application Cards:**
- **Name**: Application name
- **Status Badge**: 
  - Green checkmark: Synced + Healthy
  - Yellow clock: OutOfSync
  - Red X: Sync Failed or Unhealthy
- **Sync Status**: Synced, OutOfSync, Unknown
- **Health Status**: Healthy, Progressing, Degraded, Suspended
- **Project**: default
- **Namespace**: Target namespace
- **Repository**: Git repo URL (truncated)

**2. Filters (Top Bar):**
- **Search**: Filter by name
- **Sync Status**: Show only synced/out-of-sync
- **Health Status**: Show only healthy/degraded
- **Labels**: Filter by labels
- **Projects**: Filter by project

**3. Actions:**
- **New App**: Create new application
- **Refresh**: Refresh application list
- **Sync All**: Sync all applications

---

### Application Details View

**Click on any application** to see detailed view.

#### **Summary Tab**

**Top Section:**
- **Application Name**
- **Sync Button**: Manually trigger sync
- **Refresh Button**: Re-check Git repository
- **Delete Button**: Delete application
- **App Details**: Edit application settings

**Status Cards:**
- **Health Status**: Current application health
- **Sync Status**: Git vs Cluster comparison
- **Last Sync**: When last synced, by whom
- **Repository**: Git repo, branch, commit SHA
- **Destination**: Cluster and namespace

**Live Manifests:**
Shows actual state in cluster (YAML)

**Desired Manifests:**
Shows desired state from Git (YAML)

**Parameters:**
For Helm charts and Kustomize

---

#### **Resource Tree View**

**Visual representation of Kubernetes resources:**

```
Application: auth-service-staging
├── Deployment: auth-service
│   └── ReplicaSet: auth-service-7d8f5b6c9d
│       ├── Pod: auth-service-7d8f5b6c9d-abcde ✅ Healthy
│       └── Pod: auth-service-7d8f5b6c9d-fghij ✅ Healthy
├── Service: auth-service ✅ Healthy
├── ConfigMap: auth-service-config ✅ Synced
└── Secret: auth-service-db-secret ✅ Synced
```

**Node Colors:**
- **Green**: Healthy and Synced
- **Yellow**: Progressing or OutOfSync
- **Red**: Degraded or Failed
- **Gray**: Suspended or Unknown

**Click on any node** to see:
- **Summary**: Basic info
- **Manifest**: YAML definition
- **Diff**: Difference from desired state (if OutOfSync)
- **Events**: Kubernetes events for this resource
- **Logs**: For pods only

---

#### **Events Tab**

Shows ArgoCD-specific events:
- Sync started/completed/failed
- Health assessment changes
- Resource pruned/created/updated
- Manual operations

Example:
```
2026-01-26 20:30:15  Sync      Sync operation completed successfully
2026-01-26 20:30:10  Health    Application health status changed to Healthy
2026-01-26 20:30:05  Sync      Syncing application: auth-service-staging
```

---

#### **Parameters Tab**

For Helm charts, shows overridable values:
```
replicaCount: 2
image.tag: v1.2.3
resources.limits.cpu: 500m
```

For Kustomize, shows overlays.

For plain YAML, shows available parameters (if using ArgoCD parameter files).

---

#### **Diff Tab**

**Shows changes between Git and Cluster:**

**Three-way diff:**
1. **Desired State**: What's in Git
2. **Live State**: What's in cluster
3. **Last Synced State**: What ArgoCD last applied

**Diff indicators:**
- Green `+`: Line added in desired state
- Red `-`: Line removed from desired state
- No color: Line unchanged

**Example:**
```diff
  spec:
    replicas: 2
    template:
      spec:
        containers:
        - name: auth-service
-         image: ghcr.io/.../auth:v1.2.2
+         image: ghcr.io/.../auth:v1.2.3
          resources:
            limits:
-             cpu: 500m
+             cpu: 600m
```

**Compact Diff:**
Shows only changed resources (not entire YAML).

**Full Diff:**
Shows complete YAML for all resources.

---

#### **History Tab**

**Deployment history:**

Each row shows:
- **Revision**: Sync attempt number
- **Date**: When synced
- **User**: Who triggered (admin, auto-sync)
- **Git Commit**: Commit SHA from Git
- **Status**: Success, Failed, Running

**Actions:**
- **Rollback**: Revert to previous revision
- **View Manifest**: See what was deployed

**Rollback:**
Click rollback → ArgoCD applies previous Git commit state.

---

### Settings Views

#### **Projects**

Group applications with shared settings:
- Source repositories allowed
- Destination clusters allowed
- RBAC rules
- Resource whitelist/blacklist

Default project: Allows everything.

#### **Repositories**

List of Git repositories ArgoCD watches:
- **Type**: Git, Helm
- **URL**: Repository URL
- **Connection Status**: Connected, Failed
- **Credentials**: SSH key, HTTPS token

#### **Clusters**

List of Kubernetes clusters:
- **Name**: Cluster name
- **URL**: API server URL
- **Status**: Connected, Unreachable
- **Server Version**: Kubernetes version

#### **Accounts**

User accounts and API tokens.

#### **Certificates**

SSH known hosts, TLS certificates.

---

## Application Lifecycle

### 1. Creation

**Via UI:**
1. Applications → New App
2. Fill form (name, repo, path, cluster, namespace)
3. Create

**Via CLI:**
```bash
argocd app create auth-service-staging \
  --repo https://github.com/RahulSharma2309/FreshHarvest-Market \
  --path infra/k8s/staging/deployments/auth-service \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace staging
```

**Via YAML:**
```bash
kubectl apply -f application.yaml -n argocd
```

**State after creation:** OutOfSync (resources not yet deployed)

---

### 2. Initial Sync

**Manual:**
Click "Sync" → Synchronize

**Automatic:**
If auto-sync enabled, happens automatically.

**What happens:**
1. ArgoCD clones Git repository
2. Reads YAML files from specified path
3. Validates manifests
4. Applies to Kubernetes
5. Watches resources until healthy

**State after sync:** Synced + Healthy (if successful)

---

### 3. Ongoing Reconciliation

**Every 3 minutes** (default), ArgoCD:
1. Polls Git repository for changes
2. Compares Git state vs Cluster state
3. If different → marks OutOfSync
4. If auto-sync enabled → syncs automatically
5. If self-heal enabled → reverts manual changes

**State:** Synced (if no changes) or OutOfSync (if Git changed)

---

### 4. Updates

**Git change detected:**
1. Developer commits to Git
2. ArgoCD polls, sees new commit
3. Status changes to OutOfSync
4. Auto-sync triggers (if enabled)
5. ArgoCD applies changes
6. Rolling update happens in K8s
7. Status returns to Synced + Healthy

---

### 5. Deletion

**Delete application:**
```bash
argocd app delete auth-service-staging
```

**What happens:**
1. By default, deletes ArgoCD Application only
2. Kubernetes resources remain in cluster
3. To delete resources too: `--cascade` flag

```bash
argocd app delete auth-service-staging --cascade
```

**Finalizer:**
`resources-finalizer.argocd.argoproj.io` ensures cleanup.

---

## Sync Strategies

### Manual Sync

**When:** You control when to deploy.

**Setup:**
```yaml
syncPolicy: {}  # No automated section
```

**Workflow:**
1. Git changes → OutOfSync
2. Review changes in Diff tab
3. Click Sync when ready
4. Choose sync options
5. Synchronize

**Use case:** Production deployments requiring approval.

---

### Automatic Sync

**When:** Deploy immediately on Git changes.

**Setup:**
```yaml
syncPolicy:
  automated: {}
```

**Workflow:**
1. Git changes → OutOfSync
2. ArgoCD auto-syncs (within 3 min)
3. Status → Synced + Healthy

**Use case:** Staging, dev environments.

---

### Pruning

**Without prune:**
```
Git: deployment.yaml deleted
Cluster: Deployment still exists (orphaned)
ArgoCD: Shows Synced (ignores extra resources)
```

**With prune:**
```yaml
syncPolicy:
  automated:
    prune: true
```
```
Git: deployment.yaml deleted
Cluster: Deployment exists
ArgoCD: Detects extra resource, deletes it
Cluster: Deployment removed
```

**Danger:** Can delete production resources if misconfigured!

---

### Self-Heal

**Without self-heal:**
```
Manual change: kubectl scale deployment --replicas=10
ArgoCD: Shows OutOfSync
Action: Manual sync required to revert
```

**With self-heal:**
```yaml
syncPolicy:
  automated:
    selfHeal: true
```
```
Manual change: kubectl scale deployment --replicas=10
ArgoCD: Detects drift (within 3 min)
ArgoCD: Automatically reverts to Git state (replicas=2)
Status: Synced
```

**Use case:** Enforce "Git is the source of truth".

---

## Health Assessment

### Built-in Health Checks

ArgoCD knows how to assess health for common resources:

**Deployment:**
- Healthy: `desiredReplicas == readyReplicas`
- Progressing: Rolling update in progress
- Degraded: Some replicas not ready

**Pod:**
- Healthy: Status = Running, all containers ready
- Progressing: ContainerCreating, PodInitializing
- Degraded: CrashLoopBackOff, Error

**Service:**
- Healthy: Has endpoints (backing pods exist)
- Progressing: Creating
- Degraded: No endpoints

**Ingress:**
- Healthy: Rules configured
- Progressing: Creating
- Degraded: Invalid rules

**StatefulSet:**
- Healthy: All replicas ready, in order
- Progressing: Updating
- Degraded: Pod failures

---

### Custom Health Checks

Define custom logic in `argocd-cm` ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations: |
    apps/Deployment:
      health.lua: |
        hs = {}
        if obj.status.readyReplicas == obj.spec.replicas then
          hs.status = "Healthy"
          hs.message = "All replicas ready"
        else
          hs.status = "Progressing"
          hs.message = "Waiting for replicas"
        end
        return hs
```

---

## Common Operations

### Sync Application

**UI:** Click "Sync" → Synchronize

**CLI:**
```bash
argocd app sync auth-service-staging
```

**Options:**
- `--prune`: Delete resources not in Git
- `--force`: Force apply (can cause downtime)
- `--dry-run`: Preview changes without applying
- `--async`: Don't wait for completion

---

### Refresh Application

**Force ArgoCD to check Git immediately** (don't wait for 3min poll):

**UI:** Click "Refresh"

**CLI:**
```bash
argocd app get auth-service-staging --refresh
```

---

### Rollback

**Revert to previous Git state:**

**UI:** History tab → Click revision → Rollback

**CLI:**
```bash
argocd app rollback auth-service-staging 123  # Revision number
```

**What happens:**
ArgoCD applies the previous Git commit's manifests.

---

### Diff

**Preview changes before syncing:**

**UI:** Diff tab → See changes

**CLI:**
```bash
argocd app diff auth-service-staging
```

Shows what would change if you sync now.

---

### Delete and Re-Create

**Recreate application from scratch:**

**CLI:**
```bash
# Delete (keep cluster resources)
argocd app delete auth-service-staging

# Re-create
argocd app create auth-service-staging ...

# Sync
argocd app sync auth-service-staging
```

---

## Best Practices

### 1. Project Structure

**Organize by environment:**
```
infra/k8s/
├── staging/
│   ├── deployments/
│   │   ├── auth-service/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   └── ...
│   ├── services/
│   └── ingress/
└── production/
    └── (same structure)
```

**One Application per microservice:**
- auth-service-staging
- auth-service-production

**Don't:**
- One Application for entire environment (too coarse)
- One Application per YAML file (too granular)

---

### 2. Sync Policies

| Environment | Auto-Sync | Self-Heal | Prune |
|-------------|-----------|-----------|-------|
| Dev | ✅ | ✅ | ✅ |
| Staging | ✅ | ✅ | ✅ |
| Production | ❌ | ❌ | ❌ |

**Production:**
- Manual approval for safety
- Review changes before deploying
- Controlled rollout

---

### 3. Git Workflow

**Feature branch:**
```bash
git checkout -b feat/new-feature
# Make code changes
git commit -m "feat: add new feature"
git push origin feat/new-feature
# Create PR
```

**CI builds image, doesn't deploy:**
- Creates alpha image: `v1.2.3-alpha-abc123`
- Doesn't update manifests yet

**Merge to main:**
- CI builds production image: `v1.2.3`
- CI updates manifests in Git
- ArgoCD syncs staging automatically
- Production requires manual sync

---

### 4. Secrets Management

**Never commit secrets to Git!**

**Options:**

**Sealed Secrets:**
```bash
kubeseal < secret.yaml > sealed-secret.yaml
git add sealed-secret.yaml
```

**External Secrets Operator:**
Sync from Vault, AWS Secrets Manager, etc.

**ArgoCD Vault Plugin:**
Inject secrets from Vault during sync.

---

### 5. Monitoring

**Set up alerts:**
- Sync failures
- Health degradation
- Drift detection

**Tools:**
- ArgoCD Notifications (Slack, Discord, email)
- Prometheus metrics
- Grafana dashboards

---

### 6. RBAC

**Production access control:**
```yaml
# Read-only access to production
- group: developers
  permission: get
  resource: applications
  project: production

# Full access to staging
- group: developers
  permission: *
  resource: applications
  project: staging
```

---

## Troubleshooting

### Application Stuck OutOfSync

**Check:**
1. Diff tab → See what's different
2. Events tab → Look for errors
3. Logs → ArgoCD application-controller logs

**Common causes:**
- Manual kubectl changes (disable self-heal temporarily)
- Invalid YAML (check events for validation errors)
- Namespace doesn't exist

---

### Sync Failed

**Check:**
1. Events tab → Error message
2. Last sync result → See which resource failed

**Common causes:**
- Resource already exists (owned by another application)
- RBAC: ArgoCD doesn't have permission
- Invalid manifest syntax

---

### Application Unhealthy

**Check:**
1. Resource tree → Which resource is unhealthy?
2. Click resource → Events
3. If pod → Check logs

**Common causes:**
- Pod CrashLoopBackOff (app error)
- ImagePullBackOff (wrong image or secret)
- Insufficient resources (CPU/memory limits)

---

## Next Steps

- **Explore Advanced Features**: Sync waves, hooks, ApplicationSets
- **Integrate with CI/CD**: Automate image updates
- **Multi-Cluster**: Manage multiple K8s clusters
- **Progressive Delivery**: Use ArgoCD Rollouts for canary deployments

---

**Master ArgoCD by doing! Break things, fix them, learn from failures.**
