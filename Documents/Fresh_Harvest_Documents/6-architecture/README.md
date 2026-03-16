# 🏛️ Architecture Documentation

> **System design, patterns, and architecture decisions**

---

## 📋 Documents in This Section

### High-Level Architecture

| File | Content | Detail Level |
|------|---------|--------------|
| [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) | Overall system design, services, communication | High-level |
| [`LOW_LEVEL_DESIGN.md`](LOW_LEVEL_DESIGN.md) | Detailed component design, data flow | Deep dive |
| [`PLATFORM_ARCHITECTURE.md`](PLATFORM_ARCHITECTURE.md) | Platform NuGet library design | Deep dive |

---

### Architecture Diagrams

**Location:** [`diagrams/`](diagrams/)

| File | Type | Description |
|------|------|-------------|
| [`architecture-system.mmd`](diagrams/architecture-system.mmd) | Mermaid | System-level diagram |
| [`architecture-sequence.mmd`](diagrams/architecture-sequence.mmd) | Mermaid | Sequence diagrams |
| [`low-level-design.mmd`](diagrams/low-level-design.mmd) | Mermaid | Component diagrams |
| [`rendered/`](diagrams/rendered/) | PNG/SVG | Pre-rendered diagrams |
| [`render-diagrams.ps1`](diagrams/render-diagrams.ps1) | PowerShell | Diagram generation script |

**How to Render:**
```bash
cd diagrams
./render-diagrams.ps1
# Outputs PNG and SVG to rendered/
```

---

### Roadmap-Complete (Target State) Diagrams

**Location:** [`roadmap-complete/`](roadmap-complete/)

These diagrams show how the system looks **after** the roadmap is completed (Kubernetes, CI/CD, observability, caching/search, etc.).

| Folder | Description |
|------|-------------|
| [`01-service-level/`](roadmap-complete/01-service-level/) | Service interactions + saga checkout |
| [`02-system-level/`](roadmap-complete/02-system-level/) | Whole-system + K8s deployment views |
| [`03-ci-cd/`](roadmap-complete/03-ci-cd/) | CI/CD pipeline view |
| [`04-data/`](roadmap-complete/04-data/) | Databases + shared data stores |
| [`05-observability/`](roadmap-complete/05-observability/) | Logging/metrics/tracing stack |

Start here: [`roadmap-complete/README.md`](roadmap-complete/README.md)

---

### Service-Specific Architecture

**Location:** [`service-specific/`](service-specific/)

| File | Service | Content |
|------|---------|---------|
| [`AUTH_SERVICE_ARCHITECTURE.md`](service-specific/AUTH_SERVICE_ARCHITECTURE.md) | Auth Service | N-tier architecture, Platform usage |
| [`EF_CORE_DESIGN.md`](service-specific/EF_CORE_DESIGN.md) | All Services | Why EF Core Design package is needed |

**Note:** These are copies from service folders for centralized reference. Originals remain in service directories.

---

## 🏗️ Architecture Overview

### Microservices Pattern
```
Frontend (React) → Gateway (YARP) → Services → Databases
                        ↓
            Service-to-Service Communication
```

### Key Architectural Decisions

1. **Database-per-Service:** Each service owns its data
2. **API Gateway:** Single entry point for frontend
3. **Platform Library:** Shared infrastructure via NuGet
4. **N-Tier per Service:** Abstraction → Core → API layers
5. **Orchestration:** Order Service orchestrates checkout
6. **Compensation:** Rollback mechanisms for failures

---

## 🎯 Architecture Principles

### 1. Service Independence
- Each service can be deployed independently
- No shared databases
- Communicate via HTTP/REST

### 2. Platform-First Design
- Infrastructure concerns in Platform library
- Services consume via NuGet package
- Zero direct infrastructure dependencies

### 3. Clear Boundaries
- Each service has well-defined responsibility
- No circular dependencies
- Clear API contracts

### 4. Resilience
- Retry policies (Polly)
- Compensation transactions
- Graceful degradation

---

## 🔗 Related Documentation

### For Understanding Services:
- [`../7-services/`](../7-services/) - Individual service docs
- [`../5-user-flows/`](../5-user-flows/) - End-to-end workflows

### For Implementation:
- [`../8-platform/`](../8-platform/) - Platform library usage
- [`../2-learning-guide/ENGINEERING_PLAYBOOK.md`](../2-learning-guide/ENGINEERING_PLAYBOOK.md) - Design decisions

### For Learning:
- [`../2-learning-guide/LEARNING_GUIDE.md`](../2-learning-guide/LEARNING_GUIDE.md) - Request lifecycle walkthrough
- [`../2-learning-guide/LEARNING_ROADMAP.md`](../2-learning-guide/LEARNING_ROADMAP.md) - Design patterns

---

## 📖 Reading Order

### For Architects:
1. SYSTEM_ARCHITECTURE.md (overview)
2. Platform_ARCHITECTURE.md (infrastructure)
3. LOW_LEVEL_DESIGN.md (deep dive)
4. Service-specific docs (details)

### For Developers:
1. SYSTEM_ARCHITECTURE.md
2. Pick service from ../7-services/
3. Read related architecture doc
4. Study code

---

**Back to:** [Documentation Index](../DOCUMENTATION_INDEX.md) | [START HERE](../START_HERE.md)


















