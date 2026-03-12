# Phase 2 — Classical Machine Learning & Deep Learning (Months 4–6)

**Timeline:** Months 4–6  
**Learner:** Rahul Sharma — 10-year distributed systems architect with **FreshHarvest-Market** e-commerce platform.

**Primary course:** Master the Theory, Practice, and Math Behind Data Science, ML, DL, NLP — Krish Naik (Udemy).  
**Also:** ML with Python (Udemy) — course you are currently doing; use it alongside for hands-on classical ML.

---

## Phase Overview

This phase builds **classical machine learning** foundations—supervised learning, evaluation metrics, and production-ready pipelines—using the same rigor you apply to microservice design. You move from "ML as black box" to **model selection, feature engineering, and deployment as a K8s service**. The goal is to ship ML that fits your distributed systems mindset: versioned, observable, and scalable.

**In short:** Classical ML gives you **immediate business value** (recommendations, demand forecasting, fraud detection) and the **vocabulary** (loss, regularization, cross-validation) that carries into deep learning and MLOps.

---

## Timeline: Months 4–6

| Month | Focus | Main idea |
|-------|--------|-----------|
| **4** | Classical ML algorithms | Linear Regression, Logistic Regression, KNN, Decision Trees, SVM, ensemble methods, pipelines |
| **5** | Deep Learning | Neural networks, CNNs, RNNs, optimization, regularization; practical projects |
| **6** | NLP / Transformers intro | Attention, transformer fundamentals; bridges to Phase 4 (reference) and Phase 5 (RAG) |

---

## Folder Structure

```
Phase-2-Classical-ML/
├── README.md                                    ← You are here
├── 00-Key-Terms/
├── 01-Supervised-Learning/
├── 02-Evaluation-Metrics/
├── 03-ML-with-Python/
├── 04-Linear-Regression/
├── 05-Logistic-Regression/
├── 06-KNN/
├── 07-Decision-Trees-and-Random-Forests/
├── 08-SVM/
└── 09-Ensemble-Methods/
```

---

## Courses

| Course | Role | Platform | Notes |
|--------|------|----------|-------|
| **Master the Theory, Practice, and Math Behind Data Science, ML, DL, NLP** | **PRIMARY** | Krish Naik, Udemy | Covers classical ML (Month 4), Deep Learning (Month 5), and NLP/transformers intro (Month 6) |
| ML with Python | PRIMARY (hands-on) | Udemy (currently enrolled) | Your current course; use for classical ML implementation alongside Krish Naik |
| Hands-On ML with Scikit-Learn, Keras & TensorFlow | SUPPLEMENTARY (optional) | Aurélien Géron (book) | [O'Reilly](https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/) / [Amazon](https://www.amazon.com/Hands-Machine-Learning-Scikit-Learn-TensorFlow/dp/1492032646) — optional reading |

---

## Topics Covered (Status)

| Topic | Folder | Status | Notes |
|-------|--------|--------|-------|
| Key terms & definitions | `00-Key-Terms` | ✅ Has notes | [01-key-terms-and-definitions.md](00-Key-Terms/01-key-terms-and-definitions.md) |
| Supervised learning | `01-Supervised-Learning` | ✅ Has notes | [01-what-is-supervised-learning.md](01-Supervised-Learning/01-what-is-supervised-learning.md) |
| Classification metrics | `02-Evaluation-Metrics` | ✅ Has notes | [01-classification-metrics.md](02-Evaluation-Metrics/01-classification-metrics.md) |
| Confusion matrix | `02-Evaluation-Metrics` | ✅ Has notes | [02-confusion-matrix.md](02-Evaluation-Metrics/02-confusion-matrix.md) |
| Regression metrics | `02-Evaluation-Metrics` | ✅ Has notes | [03-regression-metrics.md](02-Evaluation-Metrics/03-regression-metrics.md) |
| Scikit-learn overview | `03-ML-with-Python` | ✅ Has notes | [01-scikit-learn-overview.md](03-ML-with-Python/01-scikit-learn-overview.md) |
| Linear regression | `04-Linear-Regression` | 📋 Placeholder | — |
| Logistic regression | `05-Logistic-Regression` | 📋 Placeholder | — |
| KNN | `06-KNN` | 📋 Placeholder | — |
| Decision trees & random forests | `07-Decision-Trees-and-Random-Forests` | 📋 Placeholder | — |
| SVM | `08-SVM` | 📋 Placeholder | — |
| Ensemble methods | `09-Ensemble-Methods` | 📋 Placeholder | — |

---

## Existing Notes Index

| # | Topic | File |
|---|-------|------|
| 1 | Key terms | [00-Key-Terms/01-key-terms-and-definitions.md](00-Key-Terms/01-key-terms-and-definitions.md) |
| 2 | Supervised learning | [01-Supervised-Learning/01-what-is-supervised-learning.md](01-Supervised-Learning/01-what-is-supervised-learning.md) |
| 3 | Classification metrics | [02-Evaluation-Metrics/01-classification-metrics.md](02-Evaluation-Metrics/01-classification-metrics.md) |
| 4 | Confusion matrix | [02-Evaluation-Metrics/02-confusion-matrix.md](02-Evaluation-Metrics/02-confusion-matrix.md) |
| 5 | Regression metrics | [02-Evaluation-Metrics/03-regression-metrics.md](02-Evaluation-Metrics/03-regression-metrics.md) |
| 6 | Scikit-learn overview | [03-ML-with-Python/01-scikit-learn-overview.md](03-ML-with-Python/01-scikit-learn-overview.md) |

---

## Month 4 Plan: Classical ML Algorithms

| Week | Topics | Notes location |
|------|--------|----------------|
| 4.1 | Linear regression (single/multiple), cost function, gradient descent | `04-Linear-Regression/` |
| 4.2 | Logistic regression, decision boundary, classification metrics | `05-Logistic-Regression/` |
| 4.3 | K-Nearest Neighbors; distance metrics; scaling | `06-KNN/` |
| 4.4 | Decision trees: splits, impurity (Gini, entropy), pruning; random forests, bagging | `07-Decision-Trees-and-Random-Forests/` |
| 4.5 | Support Vector Machines; kernels (linear, RBF); margin | `08-SVM/` |
| 4.6 | Ensemble methods: boosting, XGBoost, stacking; pipelines, cross-validation, grid search | `09-Ensemble-Methods/`, `03-ML-with-Python/` |

---

## Month 5 Plan: Deep Learning

| Week | Topics | Notes location |
|------|--------|----------------|
| 5.1 | Neural network fundamentals: perceptron, activation functions, forward/backward pass | See Phase 3 (reference) `01-Neural-Network-Fundamentals/` |
| 5.2 | Optimization, regularization (dropout, batch norm); training loops | See Phase 3 (reference) `04-Regularization-and-Optimization/` |
| 5.3 | CNNs: convolutions, pooling, transfer learning | See Phase 3 (reference) `02-CNNs/` |
| 5.4 | RNNs, LSTM, GRU; sequence models | See Phase 3 (reference) `03-RNNs-and-Sequence-Models/` |
| 5.5 | Practical projects: image classifier, sentiment model; deployment | Mini-project |

---

## Month 6 Plan: NLP / Transformers Intro (Krish Naik Master Theory)

| Week | Topics | Notes location |
|------|--------|----------------|
| 6.1–6.4 | NLP section of Master Theory course: attention, transformer fundamentals, text applications | See Phase 4 (reference) for deeper transformer study |

---

## Key Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Product recommendation engine** | Top-K recommendations (e.g. "customers who bought X also bought Y"); similarity or collaborative filtering; Scikit-learn or custom. |
| 2 | **Demand prediction model** | Predict demand (e.g. units per SKU per week); linear regression or XGBoost; pipeline with scaling/encoding; report RMSE/MAE. |
| 3 | **K8s microservice deployment** | Expose recommendation or demand model via REST API; Docker + K8s Deployment/Service; health checks; runbook for model rollback. |

---

## Architecture Connection: How Classical ML Powers Production Systems

| Use case | How classical ML fits | FreshHarvest-Market angle |
|----------|------------------------|----------------------------|
| **Recommendation engines** | Similarity (cosine, Jaccard), matrix factorization, or tree-based rankers | "Customers who bought this also bought…"; product discovery. |
| **Demand forecasting** | Linear regression, ARIMA, or gradient boosting (XGBoost) for time series / tabular | Inventory, restocking, promo planning. |
| **Fraud detection** | Classification (logistic regression, trees, ensembles) on transaction/behavior features | Anomaly scores, risk rules. |

Classical ML is **interpretable**, **fast to train**, and often **sufficient for tabular and behavioral data**—ideal for e-commerce features before you add deep learning (Phase 3+) for images and text.

---

## Navigation

| Link | Description |
|------|-------------|
| [Phase 1 — Mathematical Foundations](../Phase-1-Mathematical-Foundations/README.md) | Prerequisites (math) |
| [Phase 3 — Deep Learning (reference)](../Phase-3-Deep-Learning/README.md) | Deep learning notes and folder structure (content covered in this phase, Month 5) |
| [Phase 4 — Transformers & LLMs (reference)](../Phase-4-Transformers-and-LLMs/README.md) | Deeper transformer study (NLP intro in Month 6 here) |
| [Phase 5 — RAG & Agentic AI](../Phase-5-RAG-and-Agents/README.md) | Next phase |

---

*Next: [Phase 5 — RAG & Agentic AI](../Phase-5-RAG-and-Agents/README.md).*
