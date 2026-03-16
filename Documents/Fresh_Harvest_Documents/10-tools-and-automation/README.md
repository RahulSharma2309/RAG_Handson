# 🛠️ Tools & Automation - FreshHarvest Market

> **Scripts, tools, and automation for development and project management**

---

## 📋 Quick Links

| Resource | Purpose | Location |
|----------|---------|----------|
| **Automation Scripts** | Build, version, tag images | [`../../scripts/`](../../scripts/) |
| **Docker Commands** | Quick reference for Docker | [`DOCKER_COMMANDS.md`](DOCKER_COMMANDS.md) |
| **Dockerfile Guide** | Build optimization explained | [`DOCKERFILE_EXPLAINED.md`](DOCKERFILE_EXPLAINED.md) |
| **GitHub Import** | Import PBIs to GitHub | [`github-import/`](github-import/) |
| **CI/CD Documentation** | Pipeline & versioning | [`../6-ci-cd/`](../6-ci-cd/) |

---

## 🔧 Automation Scripts

**Location:** [`../../scripts/`](../../scripts/)

See [`../../scripts/README.md`](../../scripts/README.md) for complete documentation.

### Quick Reference

```powershell
# Build and start all services (daily development)
.\scripts\docker-build-start.ps1

# Calculate next version (CI/CD automation)
.\scripts\get-next-version.ps1 -BranchName "feat/add-feature"

# Tag images for release (CI/CD automation)
.\scripts\tag-images.ps1 -Version "1.0.0"
```

---

## 🐳 Docker Quick Reference

**File:** [`DOCKER_COMMANDS.md`](DOCKER_COMMANDS.md)

Quick commands for local Docker development:

```powershell
# Automated (recommended)
.\scripts\docker-build-start.ps1

# Manual
cd infra
$env:DOCKER_BUILDKIT=0
docker-compose build
docker-compose up -d
```

---

## 📦 Docker Build Optimization

**File:** [`DOCKERFILE_EXPLAINED.md`](DOCKERFILE_EXPLAINED.md)

**Purpose:** Understand Docker layer caching and build optimization

**Content:**
- Why we COPY files separately
- Layer caching explained
- Performance comparisons
- Real-world examples

---

## 📊 GitHub Import Tools

**Location:** [`github-import/`](github-import/)

**Purpose:** Automate importing epics and PBIs into GitHub Issues/Projects

**Files:**
- [`GITHUB_IMPORT_GUIDE.md`](github-import/GITHUB_IMPORT_GUIDE.md) - Complete guide (4 methods)
- [`epics_and_pbis.csv`](github-import/epics_and_pbis.csv) - All PBIs in CSV format
- [`github_import.py`](github-import/github_import.py) - Python automation script

**Methods Available:**
1. **Manual UI** - Good for learning
2. **GitHub CLI** - Semi-automated (recommended)
3. **Python Script** - Fully automated
4. **GitHub API** - For API learning

---

## 🔗 Related Documentation

- **CI/CD Pipeline:** [`../6-ci-cd/`](../6-ci-cd/) - Automated builds, versioning, image tagging
- **Image Tagging Strategy:** [`../6-ci-cd/IMAGE_TAGGING_STRATEGY.md`](../6-ci-cd/IMAGE_TAGGING_STRATEGY.md)
- **Project Setup:** [`../1-getting-started/PROJECT_OVERVIEW.md`](../1-getting-started/PROJECT_OVERVIEW.md)
- **Epic/PBI List:** [`../4-epics-and-pbis/`](../4-epics-and-pbis/)

---

**Back to:** [Documentation Index](../DOCUMENTATION_INDEX.md) | [START HERE](../START_HERE.md)
