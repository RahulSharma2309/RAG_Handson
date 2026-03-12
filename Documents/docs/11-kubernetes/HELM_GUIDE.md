# Helm Charts - Complete Guide

> **Understanding Helm, the Kubernetes Package Manager, with real-world analogies**

This document explains Helm charts and how they're used in the FreshHarvest Market project.

---

## 📚 Table of Contents

1. [What is Helm?](#what-is-helm)
2. [Why Use Helm?](#why-use-helm)
3. [Helm Concepts](#helm-concepts)
4. [Our Helm Chart Structure](#our-helm-chart-structure)
5. [How to Use Our Chart](#how-to-use-our-chart)
6. [Templates and Values](#templates-and-values)
7. [Real-World Examples](#real-world-examples)

---

## 🎯 What is Helm?

### Real-World Analogy

Think of **Helm** as a **package manager** like npm, pip, or apt:

```
📦 npm install react
   ↓
   Installs React with all dependencies
   ↓
   Ready to use!

📦 helm install freshharvest-market
   ↓
   Installs all K8s resources (deployments, services, etc.)
   ↓
   Application ready!
```

### What Helm Does

| Concept | Analogy | What It Does |
|---------|---------|--------------|
| **Helm Chart** | Package (like .deb, .rpm) | Contains all K8s manifests |
| **Helm Template** | Recipe | Generates YAML from templates |
| **Values File** | Configuration | Customizes the deployment |
| **Helm Release** | Installed Package | Running instance of the chart |

---

## 🤔 Why Use Helm?

### Without Helm

```
❌ 40+ YAML files to manage
❌ Hard to update (change each file)
❌ No versioning
❌ Difficult to deploy to multiple environments
❌ Error-prone (copy-paste mistakes)
```

### With Helm

```
✅ One chart package
✅ Easy updates (helm upgrade)
✅ Versioned releases
✅ Environment-specific values
✅ Reusable templates
```

### Real-World Example

**Without Helm:**
```bash
# Deploy to staging
kubectl apply -f staging/namespaces/
kubectl apply -f staging/rbac/
kubectl apply -f staging/configmaps/
kubectl apply -f staging/secrets/
kubectl apply -f staging/deployments/auth-service/
kubectl apply -f staging/deployments/user-service/
# ... 30 more commands!
```

**With Helm:**
```bash
# Deploy to staging
helm install freshharvest-market . -f values-staging.yaml -n staging
# Done! ✅
```

---

## 📦 Helm Concepts

### 1. Chart

A **Chart** is a collection of files that describe a Kubernetes application.

**Structure:**
```
freshharvest-market/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
├── values-staging.yaml # Staging overrides
├── values-prod.yaml    # Production overrides
└── templates/          # Kubernetes templates
    ├── deployment.yaml
    ├── service.yaml
    └── ...
```

### 2. Template

A **Template** is a YAML file with placeholders that get filled with values.

**Example:**
```yaml
# Template
spec:
  replicas: {{ .Values.services.auth.replicas }}
  containers:
    - image: {{ .Values.global.imageRegistry }}/{{ .Values.services.auth.image.repository }}:{{ .Values.services.auth.image.tag }}

# Generated YAML (with values)
spec:
  replicas: 2
  containers:
    - image: ghcr.io/rahulsharma2309/freshharvest-market-auth:latest
```

### 3. Values

**Values** are configuration data that customize the chart.

**values.yaml:**
```yaml
services:
  auth:
    replicas: 2
    image:
      tag: latest
```

**values-prod.yaml:**
```yaml
services:
  auth:
    replicas: 5  # More replicas for production
    image:
      tag: v1.0.0  # Specific version
```

### 4. Release

A **Release** is a running instance of a chart.

```bash
# Install creates a release
helm install freshharvest-market . -n staging
# Release name: freshharvest-market
# Chart: current directory (.)
# Namespace: staging
```

---

## 🏗️ Our Helm Chart Structure

### Location

```
infra/k8s/helm/freshharvest-market/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default values
├── values-staging.yaml           # Staging environment
├── values-prod.yaml              # Production environment
├── README.md                      # Chart documentation
└── templates/                     # Kubernetes templates
    ├── _helpers.tpl              # Helper functions
    ├── deployment.yaml            # All service deployments
    ├── service.yaml               # All services
    ├── ingress.yaml               # Ingress configuration
    ├── rbac.yaml                  # RBAC resources
    ├── configmap.yaml             # ConfigMaps
    └── secret.yaml                # Secrets
```

### Key Files Explained

#### Chart.yaml

```yaml
apiVersion: v2
name: freshharvest-market
description: A Helm chart for FreshHarvest Market
version: 1.0.0
appVersion: "1.0.0"
```

**What it does:** Defines chart metadata (name, version, description)

#### values.yaml

```yaml
global:
  imageRegistry: ghcr.io/rahulsharma2309
  environment: staging

services:
  auth:
    enabled: true
    replicas: 2
    image:
      repository: freshharvest-market-auth
      tag: latest
```

**What it does:** Default configuration for all environments

#### templates/deployment.yaml

```yaml
{{- range $serviceName, $service := .Values.services }}
{{- if $service.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $serviceName }}-service
spec:
  replicas: {{ $service.replicas }}
  # ...
{{- end }}
{{- end }}
```

**What it does:** Generates deployment YAML for each enabled service

---

## 🚀 How to Use Our Chart

### Prerequisites

1. **Kubernetes cluster** (Docker Desktop, K3s, cloud)
2. **kubectl** configured
3. **Helm 3.x** (optional, but recommended)

### Installation

#### Staging Environment

```bash
# Navigate to chart directory
cd infra/k8s/helm/freshharvest-market

# Install to staging
helm install freshharvest-market . \
  --namespace staging \
  --create-namespace \
  -f values-staging.yaml

# Verify
helm list -n staging
kubectl get pods -n staging
```

#### Production Environment

```bash
# Install to production
helm install freshharvest-market . \
  --namespace prod \
  --create-namespace \
  -f values-prod.yaml
```

### Upgrading

```bash
# Upgrade staging
helm upgrade freshharvest-market . \
  --namespace staging \
  -f values-staging.yaml

# Upgrade production
helm upgrade freshharvest-market . \
  --namespace prod \
  -f values-prod.yaml
```

### Uninstalling

```bash
# Uninstall from staging
helm uninstall freshharvest-market --namespace staging

# Uninstall from production
helm uninstall freshharvest-market --namespace prod
```

---

## 📝 Templates and Values

### Template Syntax

Helm uses Go templates with special syntax:

```yaml
# Variables
{{ .Values.services.auth.replicas }}

# Conditionals
{{- if .Values.services.auth.enabled }}
# ...
{{- end }}

# Loops
{{- range .Values.services }}
# ...
{{- end }}

# Functions
{{ include "helper.name" . }}
```

### Helper Functions

Our chart includes helper functions in `_helpers.tpl`:

```yaml
# Generate labels
{{- include "freshharvest-market.labels" . }}

# Generate image reference
{{- include "freshharvest-market.image" (dict "Values" .Values "repository" "auth" "tag" "latest") }}
```

### Values Hierarchy

```
values.yaml (defaults)
  ↓
values-staging.yaml (overrides)
  ↓
--set flags (command-line overrides)
```

**Example:**
```bash
# Use staging values, but override replicas
helm install freshharvest-market . \
  -f values-staging.yaml \
  --set services.auth.replicas=5
```

---

## 💡 Real-World Examples

### Example 1: Deploy to Staging

```bash
# 1. Install chart
helm install freshharvest-market . \
  --namespace staging \
  --create-namespace \
  -f values-staging.yaml

# 2. Check status
helm status freshharvest-market -n staging

# 3. View generated resources
helm get manifest freshharvest-market -n staging
```

### Example 2: Update Image Tag

```bash
# Upgrade with new image tag
helm upgrade freshharvest-market . \
  --namespace staging \
  -f values-staging.yaml \
  --set services.auth.image.tag=v1.1.0
```

### Example 3: Scale Services

```bash
# Scale auth service to 5 replicas
helm upgrade freshharvest-market . \
  --namespace staging \
  -f values-staging.yaml \
  --set services.auth.replicas=5
```

### Example 4: Disable a Service

```bash
# Disable frontend temporarily
helm upgrade freshharvest-market . \
  --namespace staging \
  -f values-staging.yaml \
  --set services.frontend.enabled=false
```

---

## 🔗 How Helm Connects Everything

### Complete Flow

```
1. You: helm install freshharvest-market
   ↓
2. Helm: Reads Chart.yaml and values.yaml
   ↓
3. Helm: Processes templates with values
   ↓
4. Helm: Generates Kubernetes YAML
   ↓
5. Helm: Applies YAML to cluster
   ↓
6. Kubernetes: Creates all resources
   ↓
7. Application: Running! ✅
```

### In FreshHarvest Market

```
Helm Chart
├── Templates all 7 services
├── Configures RBAC
├── Sets up ConfigMaps/Secrets
├── Creates Ingress
└── Deploys to staging/prod
```

---

## 📚 Related Documents

- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced K8s concepts

---

## 🎯 Key Takeaways

1. **Helm** = Package manager for Kubernetes
2. **Chart** = Collection of templates and values
3. **Template** = YAML with placeholders
4. **Values** = Configuration data
5. **Release** = Running instance of chart
6. **Benefits**: Easy deployment, versioning, environment management

---

This completes the Helm guide! See other documents for more details. 🚀

---