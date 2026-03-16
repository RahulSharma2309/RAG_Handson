# CI/CD Integration with Kubernetes

> **How the CI/CD pipeline automatically deploys to Kubernetes**

This document explains how the FreshHarvest Market CI/CD pipeline integrates with Kubernetes to automatically deploy services to the staging environment.

---

## 🎯 Overview

**CI/CD Pipeline Flow:**
```
Code Push → CI Build → Docker Images → CD Deploy → Kubernetes Staging
```

**What Happens:**
1. **CI Pipeline** (`.github/workflows/ci.yml`): Builds, tests, and creates Docker images
2. **CD Pipeline** (`.github/workflows/cd-staging.yml`): Deploys images to Kubernetes staging namespace
3. **Smoke Tests**: Verifies deployment success
4. **Notifications**: Reports deployment status

---

## 📋 CI Pipeline (Continuous Integration)

**File:** `.github/workflows/ci.yml`

### What It Does

1. **Build & Test** - Compiles all services and runs tests
2. **Dependency Scanning** - Scans for vulnerabilities in:
   - .NET NuGet packages
   - npm packages (frontend)
   - Docker images (Trivy)
3. **Docker Build** - Creates Docker images for all 7 services
4. **Push to Registry** - Pushes images to `ghcr.io/rahulsharma2309`

### Key Phases

#### Phase 1: Calculate Version
- Determines version number from git history
- Gets git SHA for tagging
- Sets mode (production vs alpha)

#### Phase 2-3: Build & Test
- Parallel builds for all .NET services
- Frontend build and tests
- Uploads test results and coverage

#### Phase 4-6: Dependency Scanning
- **.NET Services**: Scans NuGet packages for vulnerabilities
- **Frontend**: Runs `npm audit` for security issues
- **Docker Images**: Uses Trivy to scan container images
- **Fails on high/critical vulnerabilities**

#### Phase 7: SonarCloud Analysis
- Code quality checks
- Security vulnerability detection
- Code smell analysis

#### Phase 8: Docker Build & Push
- Builds all 7 service images in parallel
- Tags with version numbers:
  - Production: `v1.0.0`, `v1.0.0-abc123d`, `latest`
  - Alpha: `alpha-1.0.0-abc123d`
- Pushes to GitHub Container Registry

---

## 🚀 CD Pipeline (Continuous Deployment)

**File:** `.github/workflows/cd-staging.yml`

### What It Does

1. **Triggers on:** Push to `main` branch
2. **Verifies Images:** Ensures Docker images exist in registry
3. **Deploys to K8s:** Applies Kubernetes manifests to staging namespace
4. **Smoke Tests:** Verifies services are running
5. **Reports Status:** Creates deployment summary

### Key Phases

#### Phase 1: Prepare Deployment
- Calculates version and git SHA
- Gets repository owner for image paths

#### Phase 2: Verify Images
- Checks that all Docker images exist in registry
- Verifies image tags are correct
- Fails if images are missing

#### Phase 3: Deploy to Kubernetes

**Steps:**
1. **Set up kubectl** - Configures Kubernetes CLI
2. **Verify namespace** - Ensures `staging` namespace exists
3. **Update image tags** - Updates deployment YAMLs with new image versions
4. **Apply manifests** - Applies all Kubernetes resources in order:
   ```bash
   kubectl apply -f infra/k8s/staging/namespaces/
   kubectl apply -f infra/k8s/staging/rbac/
   kubectl apply -f infra/k8s/staging/configmaps/
   kubectl apply -f infra/k8s/staging/secrets/
   kubectl apply -f infra/k8s/staging/deployments/
   kubectl apply -f infra/k8s/staging/ingress/
   kubectl apply -f infra/k8s/staging/storage/
   ```
5. **Wait for readiness** - Waits up to 5 minutes for all deployments to be ready

#### Phase 4: Smoke Tests
- Tests gateway health endpoint
- Tests auth-service health endpoint
- Verifies services are accessible

#### Phase 5: Deployment Summary
- Creates GitHub Actions summary
- Lists deployed services
- Provides next steps and access URLs

---

## 🔄 Complete Flow Example

### Scenario: Developer pushes code to main

```
1. Developer pushes code
   ↓
2. CI Pipeline triggers
   ↓
3. Build & Test (10-15 min)
   - ✅ All tests pass
   - ✅ No vulnerabilities found
   ↓
4. Docker Build (5-10 min)
   - ✅ All 7 images built
   - ✅ Images pushed to ghcr.io
   ↓
5. CD Pipeline triggers (on merge to main)
   ↓
6. Verify Images (1 min)
   - ✅ All images exist in registry
   ↓
7. Deploy to Kubernetes (2-5 min)
   - ✅ Namespace exists
   - ✅ RBAC applied
   - ✅ ConfigMaps/Secrets applied
   - ✅ Deployments updated
   - ✅ Services running
   ↓
8. Smoke Tests (1 min)
   - ✅ Gateway health check passes
   - ✅ Auth service health check passes
   ↓
9. Deployment Complete! 🎉
   - Services available at:
     - Frontend: http://staging.freshharvest-market.local
     - API: http://api.staging.freshharvest-market.local
```

---

## 📁 File Structure

```
.github/
├── workflows/
│   ├── ci.yml              # CI Pipeline (build, test, scan, build images)
│   ├── cd-staging.yml      # CD Pipeline (deploy to staging)
│   └── release.yml         # Semantic versioning and releases
└── dependabot.yml          # Automated dependency updates

infra/k8s/
└── staging/                 # Kubernetes manifests for staging
    ├── namespaces/
    ├── rbac/
    ├── configmaps/
    ├── secrets/
    ├── deployments/
    ├── ingress/
    └── storage/
```

---

## 🔐 Security Features

### Dependency Scanning

1. **.NET Dependencies**
   - Uses `dotnet list package --vulnerable`
   - Scans all NuGet packages
   - Fails on high/critical vulnerabilities

2. **npm Dependencies**
   - Uses `npm audit`
   - Scans frontend packages
   - Fails on high/critical vulnerabilities

3. **Docker Images**
   - Uses Trivy scanner
   - Scans container images for CVEs
   - Uploads results to GitHub Security

4. **Dependabot**
   - Automated dependency updates
   - Creates PRs for security patches
   - Weekly scans for all dependencies

### Image Security

- Images stored in GitHub Container Registry (private)
- Images tagged with version numbers (not just `latest`)
- Images scanned before deployment
- Only images that pass security checks are deployed

---

## 🛠️ Manual Deployment

If you need to deploy manually:

```bash
# 1. Set image version
export VERSION="1.2.0"
export SHA="abc123d"
export OWNER="rahulsharma2309"

# 2. Update image tags in deployments
find infra/k8s/staging/deployments -name "deployment.yaml" | \
  xargs sed -i "s|image: ghcr.io/.*/freshharvest-market-.*:.*|image: ghcr.io/${OWNER}/freshharvest-market-*:v${VERSION}|g"

# 3. Apply manifests
kubectl apply -f infra/k8s/staging/namespaces/
kubectl apply -f infra/k8s/staging/rbac/
kubectl apply -f infra/k8s/staging/configmaps/
kubectl apply -f infra/k8s/staging/secrets/
kubectl apply -f infra/k8s/staging/deployments/
kubectl apply -f infra/k8s/staging/ingress/

# 4. Wait for readiness
kubectl wait --for=condition=available --timeout=300s \
  deployment/auth-service \
  deployment/user-service \
  deployment/product-service \
  deployment/order-service \
  deployment/payment-service \
  deployment/gateway \
  deployment/frontend \
  -n staging

# 5. Verify
kubectl get pods -n staging
kubectl get services -n staging
```

---

## 🐛 Troubleshooting

### Deployment Fails

**Issue:** Pods not starting
```bash
# Check pod status
kubectl get pods -n staging

# Check pod events
kubectl describe pod <pod-name> -n staging

# Check logs
kubectl logs <pod-name> -n staging
```

**Common Causes:**
- Image pull errors (check image name/tag)
- Missing ConfigMaps/Secrets
- Resource limits too low
- Health check failures

### Images Not Found

**Issue:** CD pipeline can't find images
```bash
# Verify image exists
docker manifest inspect ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.2.0

# Check registry authentication
docker login ghcr.io -u rahulsharma2309 -p <token>
```

### Services Not Accessible

**Issue:** Services running but not accessible
```bash
# Check services
kubectl get services -n staging

# Check ingress
kubectl get ingress -n staging

# Test from inside cluster
kubectl run test-pod --image=curlimages/curl -it --rm -- \
  curl http://gateway:80/api/health
```

---

## 📊 Monitoring Deployment

### Check Deployment Status

```bash
# View all resources
kubectl get all -n staging

# View deployments
kubectl get deployments -n staging

# View pods
kubectl get pods -n staging -w  # Watch mode

# View services
kubectl get services -n staging

# View ingress
kubectl get ingress -n staging
```

### View Logs

```bash
# Service logs
kubectl logs -n staging deployment/auth-service

# Follow logs
kubectl logs -n staging deployment/auth-service -f

# Previous container logs (if restarted)
kubectl logs -n staging deployment/auth-service --previous
```

### Check Events

```bash
# Namespace events
kubectl get events -n staging --sort-by='.lastTimestamp'

# Pod events
kubectl describe pod <pod-name> -n staging
```

---

## 🎓 Key Concepts

### CI (Continuous Integration)
- **What:** Automatically builds and tests code on every commit
- **When:** On every push/PR
- **Goal:** Catch bugs early, ensure code quality

### CD (Continuous Deployment)
- **What:** Automatically deploys code to staging after CI passes
- **When:** On merge to main branch
- **Goal:** Keep staging environment up-to-date

### Dependency Scanning
- **What:** Scans code and images for security vulnerabilities
- **When:** During CI pipeline
- **Goal:** Prevent vulnerable dependencies from being deployed

### Smoke Tests
- **What:** Basic health checks after deployment
- **When:** After CD deployment completes
- **Goal:** Verify deployment was successful

---

## 📚 Related Documentation

- **[README.md](./README.md)** - Kubernetes overview and quick start
- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented Kubernetes
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference
- **[LEARNING_PATH.md](./LEARNING_PATH.md)** - Learning guide

---

## ✅ Summary

**CI/CD Integration provides:**
- ✅ Automated builds and tests
- ✅ Security scanning (dependencies and images)
- ✅ Automated deployment to staging
- ✅ Smoke tests for verification
- ✅ Deployment status reporting

**Benefits:**
- 🚀 Faster deployments (automated)
- 🔒 Security (vulnerability scanning)
- 📊 Visibility (deployment status)
- 🐛 Early bug detection (CI tests)
- 🔄 Consistency (same process every time)

**Next Steps:**
1. Monitor deployments in GitHub Actions
2. Review dependency scan results
3. Check smoke test results
4. Verify services in staging environment
