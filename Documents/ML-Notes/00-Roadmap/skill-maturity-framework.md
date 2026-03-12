# AI/ML Skill Maturity Framework

> **1–10 scale** · Self-assessment · Production alignment · Last updated: _fill in_

---

## 1. Scoring Rubric (1–10)

| Level | Band | Meaning |
|-------|------|--------|
| **1–2** | **Awareness** | Heard of it; can describe at a high level. Knows when/where it's used. Cannot implement without heavy guidance. |
| **3–4** | **Beginner** | Can follow tutorials and docs. Basic usage in familiar setups. Needs examples to extend or debug. |
| **5–6** | **Intermediate** | Can apply independently in new problems. Debugs issues and reads error messages. Can combine concepts with some design. |
| **7–8** | **Advanced** | Can architect solutions, choose trade-offs, and teach others. Comfortable with edge cases and production concerns. |
| **9–10** | **Expert** | Can innovate, contribute to the field or OSS, and set best practices. Deep intuition and rare bugs. |

---

## 2. Self-Assessment Table

_Score 1–10 for **Current** and **Target (12-month)**. **Phase** = roadmap month/phase where the skill is primarily learned._

### Math

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Linear Algebra | | | Month 1 |
| Probability & Statistics | | | Month 2 |
| Calculus & Optimization | | | Month 3 |

### Classical ML

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Supervised Learning Theory | | | Month 4–5 |
| Regression Models | | | Month 4–5 |
| Classification Models | | | Month 4–5 |
| Model Evaluation & Metrics | | | Month 4–5 |
| Feature Engineering | | | Month 4–5 |
| Scikit-Learn Proficiency | | | Month 4–5 |
| Data Preprocessing with Pandas | | | Month 4–5 |

### Deep Learning

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Neural Network Fundamentals | | | Month 6–7 |
| Backpropagation & Optimization | | | Month 6–7 |
| CNNs | | | Month 7 |
| RNNs & Sequence Models | | | Month 7 |
| PyTorch / TensorFlow | | | Month 6–7 |

### Transformers / LLMs

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Attention & Self-Attention | | | Month 8 |
| Transformer Architecture | | | Month 8 |
| Tokenization & Embeddings | | | Month 8–9 |
| Fine-Tuning & Transfer Learning | | | Month 8–9 |
| Prompt Engineering | | | Month 8–9 |

### RAG & Agents

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Vector Databases | | | Month 9 |
| RAG Pipeline Design | | | Month 9 |
| LangChain / LlamaIndex | | | Month 9 |
| Agent Architecture | | | Month 10 |
| Tool Calling & Planning | | | Month 10 |

### MLOps & Infrastructure

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Model Serving & APIs | | | Month 5, 11 |
| CI/CD for ML | | | Month 11 |
| Model Monitoring & Drift | | | Month 11 |
| Kubernetes for ML | | | Month 12 |
| GPU Scheduling & Scaling | | | Month 12 |
| Cost Optimization | | | Month 12 |

### Cross-Cutting

| Skill | Current Score | Target Score (12-mo) | Phase Where Learned |
|-------|----------------|----------------------|----------------------|
| Python for ML | | | Ongoing |
| Git & Version Control | | | Ongoing |
| System Design for AI | | | Month 10–12 |
| Technical Writing & Documentation | | | Ongoing |

---

## 3. Architecture Application Matrix

_How each skill area maps to production systems, with **FreshHarvest E-commerce Platform** examples aligned to the 5-phase roadmap (Math to Core ML to RAG to Agentic AI to MLOps)._

| Skill Area | Production Application | Example: FreshHarvest E-commerce |
|------------|------------------------|----------------------------------|
| **Linear Algebra** | Embeddings, dimensionality reduction, vector similarity | Phase 1: Vector similarity search engine; product embeddings for similar items. |
| **Probability & Statistics** | A/B tests, uncertainty estimates, anomaly detection | Phase 1: A/B tests for recommendations; confidence intervals for churn and demand. |
| **Calculus & Optimization** | Training loops, hyperparameter tuning, gradient-based methods | Phase 1: Gradient descent visualizer; optimizing loss for churn predictor. |
| **Supervised Learning Theory** | Choosing model class, bias–variance, generalization | Phase 2: Picking regression vs classification for sales vs churn. |
| **Regression / Classification** | Demand forecasting, churn, propensity scores | Phase 2: Sales prediction model; customer churn classifier with Scikit-learn. |
| **Model Evaluation & Metrics** | Offline metrics, thresholds, business alignment | Phase 2: Precision/recall for churn; MAE/RMSE for sales forecasts. |
| **Feature Engineering** | Inputs that drive model performance | Phase 2: Time features, aggregates, user/product history for sales and churn. |
| **Scikit-Learn / Pandas** | End-to-end training and data pipelines | Phase 2: Preprocessing, training, evaluation for churn and sales pipelines. |
| **Neural Network Fundamentals** | Non-linear patterns, representation learning | Phase 2: Dense nets for tabular; foundations for product image classifier. |
| **Backpropagation & Optimization** | Stable training, convergence | Phase 2: Training product image classifier (CNN) and sentiment models. |
| **CNNs** | Image and signal understanding | Phase 2: Product image classifier (CNN) for FreshHarvest catalog. |
| **RNNs / Sequence Models** | Time series and sequences | Phase 2: Sales over time; sequence inputs for sentiment analysis pipeline. |
| **PyTorch / TensorFlow** | Custom models and deployment | Phase 2: Custom layers for classifier; export for API serving. |
| **Attention & Transformers** | Long-context, sequence-to-sequence | Phase 2: Transformers intro for sentiment analysis; query–product matching. |
| **Tokenization & Embeddings** | Text and multimodal inputs | Phase 2–3: Product titles/descriptions; semantic search for RAG. |
| **Fine-Tuning & Transfer Learning** | Domain-specific LLMs and models | Phase 2–3: Domain adaptation for FreshHarvest product taxonomy. |
| **Prompt Engineering** | Reliable LLM behavior in apps | Phase 3: Product descriptions, FAQs; AI shopping assistant prompts. |
| **Vector Databases** | Semantic search, retrieval | Phase 3: RAG-powered product search; find similar products over catalog. |
| **RAG Pipeline Design** | Grounded Q&A and search | Phase 3: RAG foundations and advanced techniques; product search and docs. |
| **LangChain / LlamaIndex** | Orchestration of retrieval and LLMs | Phase 3: AI shopping assistant with conversation memory; agentic RAG + LangSmith. |
| **Agent Architecture** | Multi-step reasoning and actions | Phase 4: Multi-agent research assistant; inventory management AI agent. |
| **Tool Calling & Planning** | APIs, DB, external services | Phase 4: Dynamic pricing agent; inventory agent calling stock and pricing APIs. |
| **Model Serving & APIs** | Real-time and batch inference | Phase 5: Production ML service on AWS SageMaker; REST endpoints for demand/churn. |
| **CI/CD for ML** | Reproducible, auditable model releases | Phase 5: Pipelines and CI/CD; end-to-end ML pipeline (Docker + MLflow + DVC). |
| **Model Monitoring & Drift** | Reliability and data quality | Phase 5: Grafana ML monitoring dashboard; drift and performance alerts. |
| **Kubernetes for ML** | Scalable, resilient serving | Phase 5: ML services and batch jobs; cloud deploy patterns. |
| **GPU Scheduling & Scaling** | Cost-effective GPU use | Phase 5: Scaling inference and training on cloud (e.g., SageMaker). |
| **Cost Optimization** | Budget and efficiency | Phase 5: Right-sizing instances; spot/preemptible; caching in production. |
| **Python for ML** | Scripts, notebooks, services | All phases: Training, RAG, agents, and MLOps code. |
| **Git & Version Control** | Code and config history | All phases: Repos for models, pipelines, and infra. |
| **System Design for AI** | End-to-end AI systems | Phase 5: Designing FreshHarvest ML stack (data to train to serve to monitor). |
| **Technical Writing & Documentation** | Runbooks, design docs, READMEs | All phases: Runbooks for pipelines; READMEs for portfolio artifacts. |

---

## 4. Quarterly Assessment Checkpoints

_Expected score bands by end of each quarter (assuming ~3 months per quarter), aligned to the 5-phase Krish Naik roadmap._

| Checkpoint | Months | Expected Focus | Typical Score Ranges |
|------------|--------|----------------|----------------------|
| **Q1** | 1–3 | Math Foundations complete (Linear Algebra, Probability & Statistics, Calculus & Optimization) | Math skills: 5–6; rest: 1–3 (awareness/beginner). |
| **Q2** | 4–6 | Core ML complete: Classical ML, Deep Learning, NLP & Transformers intro | ML/DL/NLP skills: 5–7; Math: 5–6. |
| **Q3** | 7–9 | RAG + Agentic AI complete (RAG foundations/advanced, Agentic RAG, Agents & Multi-Agent Systems) | RAG and Agent skills: 5–7; Core ML: 5–7. |
| **Q4** | 10–12 | MLOps complete (Core Tools, Pipelines & CI/CD, Cloud Deploy & Monitoring) | MLOps and infra skills: 6–8; end-to-end system design: 5–7. |

**How to use:** At the end of each quarter, re-run the self-assessment and compare to these bands. Adjust study plan if you're ahead or behind.

---

_End of Skill Maturity Framework_
