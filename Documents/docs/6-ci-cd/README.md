# 🚀 CI/CD Documentation

Complete documentation for the Continuous Integration and Continuous Deployment (CI/CD) pipeline for FreshHarvest Market.

---

## 📚 Essential Documents

### 1. **PIPELINE_EXECUTION_ORDER.md** 
**Complete Pipeline Flow & Architecture**

- How pipelines trigger (CI, CD, Release)
- Sequential execution order
- Deployment PR workflow
- Environment detection (staging vs production)
- Complete flow examples from code to deployment

**Use this to understand:** How the entire CI/CD system works together.

---

### 2. **SECURITY_SCANNING.md**
**Trivy Vulnerability Scanning**

- Current Trivy configuration
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Why we use `exit-code: "0"` (report-only mode)
- How to view scan results in GitHub Security tab
- Common vulnerabilities and fixes
- Local testing with Trivy

**Use this to understand:** How security scanning works and how to handle vulnerabilities.

---

### 3. **FIXES_APPLIED.md**
**Recent Pipeline Fixes & Changes**

- CD pipeline trigger fix (no longer runs on every PR)
- Release pipeline sequencing (runs after CI)
- Trivy deprecated parameter fixes
- Before/after pipeline comparison
- Verification checklist

**Use this to understand:** What was recently fixed and why.

---

## 🎯 Quick Reference

### Pipeline Triggers

| Event | Pipelines That Run | Purpose |
|-------|-------------------|---------|
| **Push to feature branch** | CI (builds alpha images, no push) | Validate build works |
| **Create PR to main** | CI (builds alpha images, no push) | Ensure PR is buildable |
| **Merge PR to main** | CI → Release (sequential) | Build, push, tag, create deployment PR |
| **Merge deployment PR** | CD (deploy to K8s) | Deploy to staging or prod |
| **Manual CI with PublishBuild=true** | CI (builds alpha, pushes) | Test deployment before merge |

### Key Files & Locations

```
.github/workflows/
├── ci.yml              # Main CI pipeline (build, push, scan)
├── cd-staging.yml      # CD pipeline (deploy to K8s)
├── release.yml         # Semantic release (tags, changelog)
└── test-runner.yml     # Runner environment test

scripts/
├── get-next-version.sh # Version calculation from commits
└── get-next-version.ps1

infra/
├── docker-compose.yml  # Local Docker setup
└── k8s/
    ├── staging/        # Staging K8s manifests
    └── prod/           # Production K8s manifests
```

### Image Naming Convention

**Production images (merge to main):**
```
ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.2.3
ghcr.io/rahulsharma2309/freshharvest-market-auth:v1.2.3-abc1234
ghcr.io/rahulsharma2309/freshharvest-market-auth:latest
```

**Alpha images (feature branches with PublishBuild=true):**
```
ghcr.io/rahulsharma2309/freshharvest-market-auth:alpha-1.2.3-abc1234
```

### Version Calculation

Based on commit messages:
- `feat:` → Minor version bump (1.2.0 → 1.3.0)
- `fix:` → Patch version bump (1.2.0 → 1.2.1)
- `BREAKING CHANGE:` → Major version bump (1.2.0 → 2.0.0)

---

## 🔄 Complete Flow

### Code Change to Production

```
1. Developer creates feature branch
   └─ feat/add-user-profile

2. Push to branch
   └─ CI runs (builds alpha, doesn't push)

3. Create PR to main
   └─ CI runs again (validates build)

4. Merge PR to main
   ├─ CI Pipeline runs
   │  ├─ Builds production images (v1.2.3)
   │  ├─ Pushes to GHCR
   │  ├─ Scans with Trivy
   │  └─ Creates deployment PR with label
   │
   └─ Release Pipeline runs (after CI succeeds)
      ├─ Creates Git tag (v1.2.3)
      ├─ Updates CHANGELOG.md
      └─ Creates GitHub Release

5. Review deployment PR
   ├─ Check image versions
   ├─ Verify label (deploy-to-staging or deploy-to-prod)
   └─ Approve & merge

6. Merge deployment PR
   └─ CD Pipeline runs
      ├─ Verifies images exist in GHCR
      ├─ Applies K8s manifests
      ├─ Waits for pods to be ready
      └─ Runs smoke tests

7. Deployment complete! ✅
```

---

## 🛡️ Security

### Trivy Scanning
- **Mode:** Report-only (`exit-code: "0"`)
- **Severity:** CRITICAL, HIGH
- **Location:** GitHub Security tab → Code scanning
- **Action Required:** Regular review of findings

### Branch Protection (Recommended)
1. Go to Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require pull request before merging (1 approval)
   - ✅ Require status checks to pass (CI pipeline)
   - ✅ Do not allow bypassing the above settings

---

## 🐛 Troubleshooting

### Issue: CI not running on PR
**Solution:** Check that PR is targeting `main` branch.

### Issue: CD running on code PR merge
**Solution:** Check deployment PR has `deploy-to-staging` or `deploy-to-prod` label.

### Issue: Release not creating tags
**Solution:** Ensure commit messages follow conventional commits format (`feat:`, `fix:`, etc.)

### Issue: Trivy scan failing
**Solution:** Check `SECURITY_SCANNING.md` for configuration details.

### Issue: Images not found during CD
**Solution:** Verify images were pushed to GHCR (check CI logs, `docker-build` job).

---

## 📝 Common Tasks

### Deploy alpha version to staging
```bash
# Trigger CI manually with PublishBuild=true
# Go to Actions → CI Pipeline → Run workflow
# Set PublishBuild = true
# This will:
# 1. Build and push alpha images
# 2. Create deployment PR for staging
# 3. Merge PR to deploy to staging
```

### Deploy to production
```bash
# 1. Merge code PR to main (creates deployment PR for staging)
# 2. Test in staging
# 3. Create new branch to update prod K8s manifests:
git checkout -b chore/promote-to-prod
# Update image tags in infra/k8s/prod/deployments/*/deployment.yaml
git commit -m "chore: promote v1.2.3 to production"
git push
# 4. Create PR to main
# 5. Merge PR - CI creates deployment PR with 'deploy-to-prod' label
# 6. Merge deployment PR to deploy to production
```

### View Trivy vulnerability findings
```bash
# Go to: GitHub → Security tab → Code scanning
# Filter by: Trivy
# Review CRITICAL and HIGH severity items
```

### Update base Docker images
```dockerfile
# In services/*/src/Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine
# Update to:
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine3.20
```

---

## 🎓 Learning Resources

### External Documentation
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Trivy](https://trivy.dev/)
- [Semantic Release](https://semantic-release.gitbook.io/)
- [Kubernetes](https://kubernetes.io/docs/home/)

### Internal Scripts
- `/scripts/get-next-version.sh` - Version calculation logic
- `/scripts/get-next-version.ps1` - Windows version
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/cd-staging.yml` - CD deployment
- `.github/workflows/release.yml` - Release automation

---

## 📊 Diagrams

### Pipeline Flow Diagram
```
docs/6-ci-cd/diagrams/ci-pipeline-comparison.mmd
```

View in VS Code with Mermaid extension or online at [Mermaid Live](https://mermaid.live/).

---

## ✅ Summary

**Essential Files:**
1. `PIPELINE_EXECUTION_ORDER.md` - Complete flow & architecture
2. `SECURITY_SCANNING.md` - Trivy configuration & usage
3. `FIXES_APPLIED.md` - Recent changes & fixes
4. `README.md` - This file (quick reference)

**Total:** 4 core documents + 1 diagram

**Everything else has been consolidated or removed to keep documentation minimal and maintainable.**

---

**Need Help?** Check the relevant document above or review the workflow files in `.github/workflows/`.
