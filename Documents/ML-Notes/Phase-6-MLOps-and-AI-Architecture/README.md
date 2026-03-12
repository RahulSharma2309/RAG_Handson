# Phase 6 — MLOps & AI Systems Architecture (Months 10–12)

**Learner:** Rahul Sharma — 10-year distributed systems architect with **FreshHarvest-Market** e-commerce platform.

---

## Phase Overview

**This is your differentiation zone.** Any developer can call an API. Very few can architect, deploy, monitor, and scale AI systems in production. Your distributed systems background—K8s, microservices, observability, SLOs—makes this your superpower. Here you close the loop: from data and training to serving, monitoring, and feedback.

| Attribute | Value |
|-----------|--------|
| **Timeline** | Months 10–12 |
| **Primary course** | Complete MLOps Bootcamp with 10+ End-to-End ML Projects — Krish Naik (Udemy) |
| **Prerequisites** | All previous phases + existing K8s and distributed systems experience |
| **Target outcome** | Production AI platform: lifecycle, pipelines, CI/CD, cloud, monitoring |

---

## Folder Structure

```
Phase-6-MLOps-and-AI-Architecture/
├── README.md                        ← You are here
├── 01-Model-Lifecycle/              # Experiment tracking, versioning, registry
├── 02-Model-Serving-and-Scaling/   # FastAPI, TorchServe, BentoML, autoscaling
├── 03-AI-Infrastructure-on-K8s/    # GPU scheduling, vLLM, TGI, KServe
└── 04-Observability-and-Cost/      # Metrics, token usage, drift, cost dashboards
```

---

## Courses & Resources

| Resource | Role | Notes |
|----------|------|--------|
| **Complete MLOps Bootcamp with 10+ End-to-End ML Projects** | **PRIMARY** | Krish Naik, Udemy — Months 10–12: Core MLOps, Pipelines & CI/CD, Cloud & Monitoring |
| [Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) | SUPPLEMENTARY | Book (Chip Huyen) — systems design for ML at scale |
| [MLflow Documentation](https://mlflow.org/docs/latest/index.html) | SUPPLEMENTARY | Experiment tracking, model registry, projects |
| [Kubeflow Documentation](https://www.kubeflow.org/docs/) | SUPPLEMENTARY | ML pipelines and training on K8s |
| [Seldon Core](https://docs.seldon.io/projects/seldon-core/) / [KServe](https://kserve.github.io/website/) | SUPPLEMENTARY | Model serving on Kubernetes |

---

## Month 10 — Core MLOps

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **Git/GitHub for ML** | Repos, branching, versioning code and configs for ML projects |
| **2** | **Docker for ML** | Containerizing training and serving; Dockerfiles for ML workloads |
| **3** | **MLflow** | Experiment tracking, runs, metrics, artifacts; model registry and stage promotion |
| **4** | **DVC & DagsHub** | Data and model versioning; train/serve consistency; collaboration |

---

## Month 11 — Pipelines & CI/CD

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **Apache Airflow + Astro** | Orchestrating ML and ETL pipelines; DAGs for training and data jobs |
| **2** | **ETL pipelines** | Data ingestion, transformation, and loading for ML |
| **3** | **GitHub Actions CI/CD** | Trigger training on data/config changes; model tests; deploy to staging/prod |
| **4** | **End-to-end ML project** | Full pipeline from data to deployed model (per bootcamp projects) |

---

## Month 12 — Cloud & Monitoring

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **AWS SageMaker** | Training and deployment on AWS; managed ML services |
| **2** | **HuggingFace NLP deployment** | Deploying NLP/transformer models in production |
| **3** | **Gen AI on AWS** | Generative AI workloads and services on AWS |
| **4** | **Grafana + PostgreSQL monitoring** | Metrics, dashboards, alerts; cost and performance monitoring |

---

## Key Deliverables

| Deliverable | Description |
|-------------|-------------|
| **ML pipeline on K8s** | Training job (or pipeline) that runs on K8s, logs to MLflow, and registers the model |
| **LLM microservice with autoscaling** | One LLM endpoint (e.g. vLLM or TGI) on K8s with HPA and GPU scheduling |
| **Evaluation dashboard** | Dashboard (e.g. Grafana) for accuracy, latency, token usage, and business metrics |
| **Cost monitoring** | Track cost per model, per endpoint, per tenant; set budgets and alerts |

---

## Architecture: Production AI Platform on K8s

This phase *is* the architecture. Below is a high-level flow you will implement or align with.

```
                    ┌─────────────────────────────────────────────────────────────────────────┐
                    │                    PRODUCTION AI PLATFORM (Kubernetes)                    │
                    └─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
  │   INGESTION  │────▶│  FEATURE STORE  │────▶│    TRAINING     │────▶│   MODEL REGISTRY     │
  │ (events,     │     │ (Feast / custom)│     │ (Kubeflow /     │     │ (MLflow / custom)   │
  │  batch)     │     │ versioned feats │     │  GPU jobs)      │     │ version + stage      │
  └──────────────┘     └─────────────────┘     └────────┬────────┘     └──────────┬───────────┘
        │                         │                         │                         │
        │                         │                         │                         ▼
        │                         │                         │              ┌─────────────────────┐
        │                         │                         │              │      SERVING        │
        │                         │                         │              │ (KServe / Seldon /   │
        │                         │                         │              │  vLLM / TGI)        │
        │                         │                         │              │ autoscale, GPU       │
        │                         │                         │              └──────────┬───────────┘
        │                         │                         │                         │
        │                         │                         │                         ▼
        │                         │                         │              ┌─────────────────────┐
        │                         │                         └─────────────▶│    MONITORING       │
        │                         │                                        │ (Prometheus,        │
        │                         │                                        │  latency, drift,     │
        │                         │                                        │  token cost)        │
        │                         │                                        └──────────┬───────────┘
        │                         │                                                   │
        │                         │                         ┌──────────────────────────┘
        │                         │                         │
        │                         ▼                         ▼
        │              ┌─────────────────────┐     ┌─────────────────────┐
        └─────────────▶│   FEEDBACK LOOP    │◀────│  EVALUATION &       │
                       │ (labels, outcomes, │     │  A/B TESTING        │
                       │  corrections)      │     │ (canary, shadow)    │
                       └─────────────────────┘     └─────────────────────┘
```

**Design principles you already know:** stateless serving where possible, versioned contracts, feature consistency between train and serve, and observability at every stage.

---

## Key Concepts to Master

| Concept | Why it matters |
|---------|----------------|
| **Model drift** | Performance degrades as the world changes; detect via ongoing evaluation and trigger retrains |
| **Data drift** | Input distribution shifts; monitor feature stats and alert; can invalidate model assumptions |
| **Shadow deployment** | Run new model in parallel, log predictions, compare with current model before switch |
| **Canary releases for models** | Route a small % of traffic to new model; compare latency and quality before full rollout |
| **A/B testing models** | Same idea as product A/B tests: measure business metrics per model variant |
| **Model versioning** | Every deployable model = immutable artifact + config; trace from data and code for reproducibility |

---

## Navigation

- **Previous:** [Phase 5 — RAG & Agentic AI](../Phase-5-RAG-and-Agents/README.md)
- **Root:** [ML-Notes](../README.md)
- **Back to roadmap:** [ML-Notes](../README.md)
