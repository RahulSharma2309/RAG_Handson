# Phase 1 — Mathematical Foundations (Months 1–3)

**Timeline:** Months 1–3  
**Learner:** Rahul Sharma — 10-year distributed systems architect with **FreshHarvest-Market** e-commerce platform, transitioning into AI.

**Primary course:** Build Strong Math Foundation with Linear Algebra, Stats, Probability, Differential Calculus — Krish Naik (Udemy).

---

## Phase Overview

This phase builds the **mathematical foundations** you need to understand how machine learning algorithms work, debug models, and design production AI systems. As a distributed systems architect, you already think in terms of state, consistency, and scaling; here you add the language of **vectors, probabilities, and gradients** that underpin modern ML.

### Why Math Matters for ML — It's Not Optional

| Without Math | With Math |
|--------------|-----------|
| Treat models as black boxes; debugging is guesswork | Interpret loss curves, diagnose vanishing gradients, tune learning rates |
| Copy-paste architectures without understanding capacity vs. overfitting | Reason about model capacity, regularization, and generalization |
| Struggle to explain results to stakeholders or auditors | Use probability (confidence intervals, Bayes) for uncertainty and A/B tests |
| Hit walls when implementing papers or custom layers | Derive gradients, implement custom losses, understand optimization |

**In short:** Math is the **foundation** of ML, not an optional extra. It's the difference between operating frameworks and understanding why they behave the way they do—especially when things go wrong in production.

---

## Timeline: Months 1–3

| Month | Topic | Main idea | Deliverable |
|-------|--------|-----------|-------------|
| **1** | Linear Algebra | Data as vectors; similarity and change of basis | Vector similarity search |
| **2** | Probability & Statistics | Uncertainty, inference, and decision-making | Churn predictor |
| **3** | Calculus for ML | How learning = following gradients downhill | Gradient descent visualizer |

---

## Folder Structure

```
Phase-1-Mathematical-Foundations/
├── README.md                              ← You are here
├── Month-01-Linear-Algebra/
│   └── 01-learning-guide.md
├── Month-02-Probability-and-Statistics/
│   └── 01-learning-guide.md
└── Month-03-Calculus-for-ML/
    └── 01-learning-guide.md
```

---

## Courses

| Course | Role | Platform | Notes |
|--------|------|----------|-------|
| **Build Strong Math Foundation with Linear Algebra, Stats, Probability, Differential Calculus** | **PRIMARY** | Krish Naik, Udemy | Covers linear algebra, probability, statistics, and calculus for ML across Months 1–3 |
| Essence of Linear Algebra | SUPPLEMENTARY | 3Blue1Brown, YouTube | [YouTube — Essence of Linear Algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDn6-jXOUVqIZGQJ3w1q0WB) |
| Essence of Calculus | SUPPLEMENTARY | 3Blue1Brown, YouTube | [YouTube — Essence of Calculus](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr) |
| StatQuest (Statistics, PCA, etc.) | SUPPLEMENTARY | StatQuest, YouTube | Visual intuition for stats and ML concepts |
| Khan Academy (Algebra, Precalculus, Statistics) | SUPPLEMENTARY | Khan Academy | Brush-up or alternate explanations |

---

## Month-by-Month Summary

| Month | Focus | Key concepts | Notes / guide |
|-------|--------|--------------|---------------|
| **Month 1** | Linear Algebra | Vectors, matrices, dot products, eigenvalues, SVD; embeddings, similarity, PCA | [Month 1 — Linear Algebra](Month-01-Linear-Algebra/01-learning-guide.md) |
| **Month 2** | Probability & Statistics | Random variables, distributions, Bayes, MLE/MAP, hypothesis testing; classification, A/B testing | [Month 2 — Probability & Statistics](Month-02-Probability-and-Statistics/01-learning-guide.md) |
| **Month 3** | Calculus for ML | Derivatives, gradients, chain rule, gradient descent, convergence; training loops, backprop | [Month 3 — Calculus for ML](Month-03-Calculus-for-ML/01-learning-guide.md) |

---

## Prerequisites

- **Python basics:** Variables, functions, loops, lists/dicts. Comfort with at least one language (C#/.NET is fine; concepts transfer).
- **NumPy basics:** Arrays, shape, indexing. You'll use NumPy for all hands-on math (dot products, gradients, etc.).
- **High school math:** Algebra, basic geometry, functions (e.g. `f(x) = x²`). No calculus or linear algebra required before starting—both are built from scratch in this phase.

---

## Key Deliverables by End of Phase

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Vector similarity search** | Mini-project: e.g. cosine similarity over product embeddings (foundation for recommendation and search). |
| 2 | **Churn predictor** | Probability-based: e.g. logistic regression from scratch or simple classifier using Bayes; ties to Phase 2. |
| 3 | **Gradient descent visualizer** | Implement gradient descent from scratch (e.g. 2D surface); show effect of learning rate and convergence. |

---

## Architecture Connection: How Math Powers Production AI Systems

| Math area | Powers in production |
|-----------|----------------------|
| **Linear algebra** | Neural net inference (matrix multiplies), embeddings and vector DBs, PCA, attention (query/key/value as matrices), recommendation similarity. |
| **Probability** | Model confidence scores, uncertainty quantification, A/B tests, monitoring (e.g. anomaly detection with distributions). |
| **Calculus** | Model training: gradient descent, backpropagation, custom optimizers, learning rate schedules; understanding why training can diverge or plateau. |

```
  Phase 1 (Math)                    Production AI (FreshHarvest-Market and beyond)
  ─────────────                     ─────────────────────────────────────────────
  Linear Algebra     ───────────►   Embeddings, similarity search, neural layers
  Probability       ───────────►   Confidence, A/B tests, monitoring
  Calculus          ───────────►   Training loops, backprop, distributed training
```

---

## Links to Each Month's Learning Guide

| Month | Topic | Link |
|-------|--------|------|
| Month 1 | Linear Algebra | [Month-01-Linear-Algebra/01-learning-guide.md](Month-01-Linear-Algebra/01-learning-guide.md) |
| Month 2 | Probability & Statistics | [Month-02-Probability-and-Statistics/01-learning-guide.md](Month-02-Probability-and-Statistics/01-learning-guide.md) |
| Month 3 | Calculus for ML | [Month-03-Calculus-for-ML/01-learning-guide.md](Month-03-Calculus-for-ML/01-learning-guide.md) |

---

*Next: [Phase 2 — Classical Machine Learning](../Phase-2-Classical-ML/README.md).*
