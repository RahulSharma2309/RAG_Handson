# 🧭 Roadmap-Complete Architecture (Target State)

This folder contains **future-state** architecture diagrams for the platform **after the roadmap is fully delivered** (CI/CD, Kubernetes, observability, performance/security hardening, and advanced product features).

**Source of truth used to derive this target view:**
- `docs/9-roadmap-and-tracking/PROJECT_ROADMAP.md`
- `docs/3-product-owner/PRODUCT_ROADMAP_PM_PO.md`

> Note: Some components below (e.g., **Notification**, **Recommendation**, **Search/Elasticsearch**, **Redis**, **Vault**, **GitOps**) are **planned roadmap items** and may not exist in the current codebase yet.

---

## 📚 Diagrams

### 1) Service level
- `01-service-level/service-interactions.mmd` — core services + sync calls + async events
- `01-service-level/checkout-saga.mmd` — future checkout flow with saga + notifications

### 2) Whole system level
- `02-system-level/system-overview.mmd` — end-to-end (clients → edge → services → data)
- `02-system-level/k8s-deployment.mmd` — deployment view (K8s namespaces, ingress, ops)

### 3) CI/CD
- `03-ci-cd/ci-cd-pipeline.mmd` — CI → image build → release → deploy (staging/prod)

### 4) Data
- `04-data/data-stores.mmd` — service DBs + Redis + Elasticsearch + object storage

### 5) Observability
- `05-observability/observability-stack.mmd` — logs/metrics/traces + dashboards/alerts

