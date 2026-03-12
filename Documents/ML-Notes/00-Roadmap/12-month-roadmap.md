# 12-Month AI/ML Learning Roadmap — Krish Naik Course Track

**Learner:** Rahul Sharma  
**Profile:** 10-year distributed systems architect (C#/.NET, Kubernetes, microservices)  
**Reference Platform:** FreshHarvest-Market (e-commerce)

**Target Identity:** AI-Native Distributed Systems Architect / GenAI Platform Engineer / Production ML Engineer

---

## Strategy Note: Course Selection

**Primary track uses 5 Krish Naik Udemy courses in this order.** The following courses are **optional/skipped** per this strategy:

- **#4 — Computer Vision** — Optional; not in core path (vision covered at intro level in Course #7).
- **#6 — GenAI with LangChain/HuggingFace** — Optional; RAG and agent content covered by Courses #1 and #3.
- **#8 — Gemini Pro** — Optional; focus is on concepts and LangChain/LangGraph, not vendor-specific LLM APIs.

Use the five courses below as the **primary** learning path; supplements (3Blue1Brown, StatQuest, etc.) are for intuition and reference only.

---

## ASCII Overview — All 12 Months

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         12-MONTH AI/ML ROADMAP — 5 PHASES (Krish Naik Udemy)                             │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬────────┤
│   M1     │   M2     │   M3     │   M4     │   M5     │   M6     │   M7     │   M8     │   M9     │  M10   │
│ Linear   │ Prob &   │ Diff     │ Classical│ Deep     │ NLP      │ RAG      │ Agentic  │ Agentic  │ MLOps  │
│ Algebra  │ Stats    │ Calculus │ ML       │ Learning │          │ Found.   │ RAG +    │ AI       │ Core   │
│          │          │ & Optim │          │          │          │ + Adv    │ LangSmith│          │        │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼────────┤
│  M11     │  M12     │          │          │          │          │          │          │          │        │
│ ML       │ Cloud    │          │          │          │          │          │          │          │        │
│ Pipelines│ Deploy   │          │          │          │          │          │          │          │        │
│ & CI/CD  │ & Monitor│          │          │          │          │          │          │          │        │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴────────┘

PHASE 1: Math Foundations (M1–M3)     → Course #2 — Build Strong Math Foundation
PHASE 2: Core ML + DL + NLP (M4–M6)  → Course #7 — Master Theory + Math + ML + DL + NLP
PHASE 3: RAG Systems (M7–M8)         → Course #1 — Ultimate RAG Bootcamp (LangChain, LangGraph, LangSmith)
PHASE 4: Agentic AI (M9)             → Course #3 — Complete Agentic AI Bootcamp (LangGraph, LangChain)
PHASE 5: MLOps & Production AI (M10–M12) → Course #5 — Complete MLOps Bootcamp (10+ End-to-End ML Projects)
```

---

# PHASE 1 — Math Foundations (Months 1–3)

**Primary Course:** #2 — Build Strong Math Foundation with Linear Algebra, Stats, Probability, Differential Calculus (Udemy, Krish Naik)

**Goal:** Build mathematical intuition so that ML/DL concepts (layers, loss, optimization, inference) are not black boxes. Connect every concept to neural nets, embeddings, and optimization.

---

## MONTH 1 — Linear Algebra

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Understand vectors, matrices, and linear transformations as the language of neural layers and embeddings; interpret dot products and similarity geometrically. |
| **Computational** | Implement dot products, matrix multiplication, norms, and SVD in code; compute eigenvalues for small matrices. |
| **Application** | Connect linear algebra to embedding-based search (vector similarity, attention), and to the forward pass of a single layer: y = Wx + b. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #2 — Build Strong Math Foundation with Linear Algebra, Stats, Probability, Differential Calculus (Udemy, Krish Naik) |
| **Focus this month** | Linear Algebra module only: vectors, matrices, dot products, eigenvalues, SVD. Complete all exercises and code-alongs in this section. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Vectors, vector operations, norms | Embeddings are vectors; similarity is geometry (distance, angle). | Vector class with dot, norm, cosine similarity. |
| Dot products, cosine similarity | Attention uses scaled dot product; retrieval uses cosine. | Similarity search over 100+ vectors from scratch. |
| Matrices, matrix multiplication | Neural layer = matrix multiply: y = Wx + b. | Matrix multiply from scratch (no NumPy for core algo). |
| Basis, span, linear transformations | Latent space, representation learning, change of basis. | 2D transformation demo or notes. |
| Eigenvalues and eigenvectors | PCA, spectral methods, dimensionality reduction. | PCA from SVD on small dataset; plot first 2 components. |
| SVD (Singular Value Decomposition) | Recommender factorizations, low-rank approximations, numerical stability. | SVD wrapper; use for PCA or low-rank approx. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Vectors, vector operations, dot product, geometric interpretation | Complete Course #2 Linear Algebra Week 1; implement dot product and norm in Python | `vectors.py`: Vector class, dot product, norm, cosine similarity |
| **Week 2** | Matrices, multiplication, inverses, systems of linear equations | Solve Ax = b by hand for 2×2; implement matrix multiply from scratch | `matrices.py`: Matrix multiply, inverse (small), SVD wrapper |
| **Week 3** | Basis, span, transformations, change of basis | Explain how a linear map changes coordinates; 2D transformation demo | Notes + small demo script for 2D transformations |
| **Week 4** | Eigenvalues, eigenvectors, SVD intuition, PCA preview | Compute top-2 PCA by hand on small matrix; SVD in NumPy | `pca_demo.py`: PCA from SVD on toy data; plot |

### Implementation Task (FreshHarvest-Market)

Build a **product similarity search** module for the FreshHarvest catalog:

- Define product embeddings (e.g., category + price bins, or simple feature vector).
- Implement cosine similarity manually (no sklearn for similarity).
- Given a product_id, return top-K similar products with similarity scores.
- Scope: 100–500 products; precomputed or simple embeddings.

### Production-Level Deliverable

A **similarity search module** callable from a service: input `product_id`, output list of `(product_id, similarity_score)`. Document the API contract for future integration into FreshHarvest-Market search or recommendation service.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or repo: ml-foundations-linear-algebra/)
├── ml-foundations/
│   ├── vectors.py              # Vector class, dot product, norm, cosine similarity
│   ├── matrices.py             # Matrix multiply, inverse (small), SVD wrapper
│   ├── pca_demo.py             # PCA from SVD on toy data
│   └── similarity_search/
│       ├── embeddings.py       # Build product embeddings (FreshHarvest schema)
│       ├── search.py           # Top-K similarity search
│       └── README.md           # How to run; link to FreshHarvest
└── README.md
```

### Architecture Diagram to Design

**Product Similarity Search — Data Flow:** Draw a diagram showing: (1) FreshHarvest product catalog / DB as source, (2) embedding generation step (features → vector), (3) in-memory or file-based vector store, (4) query flow: product_id → embedding lookup → cosine similarity over all vectors → top-K results. Label where this would sit relative to existing microservices (e.g., Search API, Recommendation Service).

### Evaluation Criteria

- [ ] Explain in one paragraph how matrix multiplication appears in a single neural layer.
- [ ] Implement cosine similarity and use it to find similar vectors in O(n) for n items.
- [ ] Describe how embedding-based search scales (brute-force vs approximate indexes) in production.
- [ ] Run similarity search on FreshHarvest product set and document one example query + results.

---

## MONTH 2 — Probability & Statistics

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Model uncertainty; connect distributions to likelihoods and training objectives; interpret Bayes theorem and MLE. |
| **Computational** | Derive MLE for common distributions; implement sampling and basic hypothesis tests; implement logistic regression from scratch. |
| **Application** | Churn probability, A/B testing design, model evaluation (precision, recall, ROC); bias–variance tradeoff. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #2 — Build Strong Math Foundation (Udemy, Krish Naik) |
| **Focus this month** | Probability & Statistics module: Bayes, distributions, MLE, hypothesis testing, bias–variance. Complete all exercises. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Random variables, PMF/PDF, CDF | Modeling outputs and uncertainties; loss design. | PMF/PDF/CDF for Bernoulli, Gaussian in code. |
| Expectation, variance | Loss design, evaluation metrics, convergence. | Derive E[X], Var(X) for Bernoulli and Gaussian. |
| Gaussian, Bernoulli, Binomial, Poisson | Common likelihoods and priors in ML. | Sampling and plotting for each distribution. |
| Bayes theorem, conditional probability | Naive Bayes, Bayesian inference, posterior updates. | Bayes demo (e.g., medical test example). |
| MLE (Maximum Likelihood Estimation) | Training objective; cross-entropy as MLE of Bernoulli. | MLE for Gaussian mean; link to logistic regression. |
| Hypothesis testing, confidence intervals | A/B tests, model comparison, statistical significance. | t-test or bootstrap CI script. |
| Bias–variance tradeoff | Underfitting vs overfitting; regularization intuition. | Short write-up with learning curve interpretation. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Random variables, PMF/PDF, CDF, expectation, variance | Derive E[X] and Var(X) for Bernoulli and Gaussian; code sampling | `distributions.py`: PMF/PDF/CDF for Bernoulli, Gaussian |
| **Week 2** | Common distributions (Bernoulli, Binomial, Gaussian, Poisson), CLT | When to use which; CLT demo with sample means | Add Binomial, Poisson; CLT demo script |
| **Week 3** | Bayes theorem, conditional probability, Bayesian thinking | Bayes by hand (e.g., medical test); posterior vs prior | `bayes_demo.py`: Bayes theorem examples |
| **Week 4** | MLE, MAP, hypothesis testing, confidence intervals | MLE for Gaussian mean; t-test for two means; bootstrap CI | `mle_map.py`: MLE for Gaussian, MAP with prior; logistic from scratch |

### Implementation Task (FreshHarvest-Market)

Build a **churn probability estimator**:

- Implement logistic regression from scratch (gradient ascent/descent on log-likelihood; no sklearn for core algorithm).
- Use synthetic or public data (e.g., Telco churn) with features mappable to FreshHarvest: tenure → order frequency, usage → basket size, contract type → subscription.
- Output: trained coefficients; predict P(churn); report accuracy, precision, recall, ROC-AUC.

### Production-Level Deliverable

**Churn probability API contract:** input (customer_id or feature vector), output P(churn). Document how this would plug into FreshHarvest-Market (e.g., retention campaign triggers, segment scoring).

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or probability-stats-implementations/)
├── ml-foundations/
│   ├── distributions.py   # PMF/PDF/CDF for Bernoulli, Gaussian, etc.
│   ├── bayes_demo.py      # Bayes theorem examples
│   ├── mle_map.py         # MLE for Gaussian, MAP with prior
│   └── logistic_regression/
│       ├── model.py       # From-scratch logistic regression
│       ├── train.py       # Training loop, data load
│       ├── evaluate.py    # Metrics, ROC curve
│       └── README.md      # FreshHarvest churn use case
└── README.md
```

### Architecture Diagram to Design

**Churn Scoring Pipeline:** Diagram showing: (1) source of customer/order data (DB or warehouse), (2) feature computation (tenure, order frequency, basket size, etc.), (3) model inference (logistic regression), (4) output P(churn) consumed by campaign service or segment builder. Include where A/B testing or monitoring would hook in.

### Evaluation Criteria

- [ ] Write the Bernoulli likelihood and show how maximizing it gives logistic regression.
- [ ] Design an A/B test (null, alternative, metric, sample size intuition) for a model change.
- [ ] Explain how you would monitor a production classifier (metrics, confidence, drift).
- [ ] Deliver trained churn model with reported metrics and one paragraph on FreshHarvest integration.

---

## MONTH 3 — Differential Calculus & Optimization

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Gradients as direction of steepest ascent; chain rule as backpropagation; why learning rate and batch size matter. |
| **Computational** | Implement gradient descent (batch, SGD, mini-batch); compute partial derivatives and gradients for toy functions. |
| **Application** | Loss minimization, learning rates, batch size vs convergence; backprop intuition for neural nets. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #2 — Build Strong Math Foundation (Udemy, Krish Naik) |
| **Focus this month** | Differential Calculus & Optimization: derivatives, gradients, gradient descent, chain rule, backprop intuition. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Derivatives, rules of differentiation | Rate of change of loss w.r.t. parameters. | Derivative of polynomial, exp, log; tangent line demo. |
| Partial derivatives, gradients | ∇L(θ) for multi-parameter models. | ∇f(x,y) by hand; numerical gradient in code. |
| Chain rule, computation graphs | Backpropagation = chain rule on a graph. | 2-layer net as graph; ∂L/∂W for one layer on paper. |
| Gradient descent (batch, SGD, mini-batch) | How neural nets are trained. | GD, SGD, mini-batch GD; plot loss curves. |
| Optimization landscape (convex, saddle) | Why initialization and learning rate matter. | 2D contour plot of loss with trajectory overlay. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Derivatives, rules of differentiation, intuition | Derivative of polynomial, exp, log; tangent line = steepest ascent | Notes + small derivative exercises in code |
| **Week 2** | Partial derivatives, gradients, directional derivatives | ∇f(x,y) by hand; implement gradient for 2D function | `derivatives.py`: numerical/symbolic gradient for toy functions |
| **Week 3** | Chain rule, computation graphs, backpropagation math | Draw 2-layer net as graph; write ∂L/∂W for one layer symbolically | Hand-written derivation + 1-page doc |
| **Week 4** | Gradient descent variants, learning rate, convergence | Code GD, SGD, mini-batch GD; plot loss; try different learning rates | `gradient_descent.py`, `linear_regression_gd.py`, visualizations |

### Implementation Task (FreshHarvest-Market)

Implement **gradient descent from scratch** and optionally tie to FreshHarvest:

- Fit linear regression (y = Wx + b) using GD only (MSE loss).
- Optional: use a tiny slice of FreshHarvest data (e.g., price vs demand or quantity sold) for the linear fit.
- Visualize: 2D contour plot of loss with trajectory overlay; compare batch vs SGD vs mini-batch convergence.

### Production-Level Deliverable

**Reusable gradient descent module** with batch/SGD/mini-batch options and logging of loss per step. Document how this translates to “training infrastructure” (batch size, iteration count, GPU vs CPU).

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or calculus-gradient-descent/)
├── ml-foundations/
│   ├── derivatives.py         # Symbolic or numerical gradients for toy functions
│   ├── gradient_descent.py    # Batch, SGD, mini-batch
│   ├── linear_regression_gd.py # Fit y = Wx + b with GD
│   ├── visualizations/        # Loss surfaces and trajectories
│   └── README.md
└── README.md
```

### Architecture Diagram to Design

**Training Loop — High-Level:** Diagram showing: (1) data batch → (2) forward pass (model) → (3) loss → (4) backward pass (gradients) → (5) parameter update → (6) repeat. Annotate where batch size, learning rate, and GPU (large matrix multiplies) fit in. One paragraph on when to use GPU vs CPU.

### Evaluation Criteria

- [ ] Derive ∂L/∂W for one layer (e.g., linear layer + MSE).
- [ ] Explain the tradeoff between batch size, iteration count, and convergence.
- [ ] Justify when to use GPU (large matrix multiplies) vs CPU (small models, preprocessing).
- [ ] Produce at least one convergence plot and one contour plot with trajectory.

---

### PHASE 1 — Supplementary Resources (Supplements Only)

| Type | Resource | Use |
|------|----------|-----|
| YouTube | 3Blue1Brown — Linear Algebra, Essence of Calculus | Visual intuition for vectors, matrices, derivatives |
| YouTube | StatQuest — Statistics Fundamentals | Probability and stats intuition |
| Blog | Distill.pub — Linear Algebra, Calculus | Clear explanations |
| Book | Linear Algebra and Its Applications (Gilbert Strang) | Reference |
| Paper / Wiki | Matrix Calculus (Wikipedia / Petersen) | Chain rule reference |

### PHASE 1 — Checkpoint Criteria

- [ ] **Linear algebra:** Explain in 2 minutes how a single neural layer is a matrix multiply + nonlinearity; implement and run cosine similarity search on 500+ vectors.
- [ ] **Probability & stats:** Derive logistic regression from Bernoulli MLE; design one A/B test and one monitoring plan for a classifier.
- [ ] **Calculus:** Derive gradients for a 2-layer MLP (symbolically or on paper); implement and tune GD/SGD and explain batch size vs convergence in one paragraph.

---

# PHASE 2 — Core ML + Deep Learning + NLP (Months 4–6)

**Primary Course:** #7 — Master Theory + Math + ML + DL + NLP with End-to-End Projects (Udemy, Krish Naik)

**Goal:** Implement classical ML, deep learning, and NLP with end-to-end projects; connect each to FreshHarvest-Market where applicable.

---

## MONTH 4 — Classical ML

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Linear/logistic regression, decision trees, SVM, KNN, ensemble methods; evaluation metrics; bias–variance; pipelines. |
| **Computational** | Train and evaluate models with Scikit-learn; build preprocessing and evaluation pipelines. |
| **Application** | Product recommendation, demand prediction, classification for FreshHarvest; microservice design. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #7 — Master Theory + Math + ML + DL + NLP with End-to-End Projects (Udemy, Krish Naik) |
| **Focus this month** | Classical ML: linear regression, logistic regression, decision trees, SVM, KNN, ensemble methods, evaluation metrics. Complete ML theory and hands-on sections. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Linear regression (analytical + GD), cost function | Baseline, interpretability, gradient-based training. | Trained linear regression; coefficient interpretation. |
| Logistic regression, decision boundary, regularization (Ridge/Lasso) | Classification, overfitting control. | Regularized logistic model; learning curve plot. |
| Decision trees (splits, impurity) | Interpretability, ensemble building block. | Trained tree; feature importance. |
| SVM (linear and kernel), margin, C and gamma | High-dimensional classification. | SVM on non-linear data; when to use vs trees. |
| KNN | Simple baseline; similarity-based prediction. | KNN classifier; effect of k. |
| Ensemble methods (bagging, Random Forest, intro to boosting) | Robustness, production tabular ML. | Random Forest; feature importance; pipeline. |
| Evaluation metrics (accuracy, precision, recall, F1, RMSE, MAE, ROC-AUC) | Reliable evaluation and model selection. | Evaluation script; metrics report. |
| Pipelines, preprocessing (scaling, encoding) | Reproducibility, productionization. | End-to-end pipeline: raw data → features → model. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Linear regression, cost function, feature scaling | Implement or use sklearn; interpret coefficients; RMSE/R² | Trained linear regression; short report on coefficients |
| **Week 2** | Logistic regression, decision boundary, regularization | Binary classifier; regularization strength vs overfitting | Regularized logistic model; learning curve plot |
| **Week 3** | SVMs (margin, kernel), KNN; decision trees | SVM for non-linear data; KNN; when to use which | SVM + KNN + tree notebooks or scripts |
| **Week 4** | Ensemble (Random Forest, bagging), pipelines, evaluation | Train tree and small forest; feature importance; sklearn Pipeline | End-to-end pipeline: raw data → features → model; metrics |

### Implementation Task (FreshHarvest-Market)

Build a **product recommendation engine** using classical ML:

- Collaborative filtering (user–item matrix): matrix factorization or k-NN on embeddings.
- Evaluate with RMSE/MAE or ranking metric (e.g., NDCG, hit rate).
- Expose via REST API: “recommended for user X”, “similar to item Y”.
- Document how to deploy as a K8s microservice (Dockerfile, health checks).

### Production-Level Deliverable

**Recommendation microservice:** endpoints (e.g., GET /recommend?user_id=, GET /similar?product_id=); Dockerfile; optional K8s Deployment + Service; README with runbook.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or recommendation-microservice/)
├── services/
│   └── recommendation-service/
│       ├── app/           # FastAPI app
│       ├── model/         # Training script, data load
│       ├── Dockerfile
│       ├── k8s/           # Deployment, Service (optional)
│       └── README.md      # Run locally + K8s
└── README.md
```

### Architecture Diagram to Design

**Recommendation Service in FreshHarvest:** Diagram showing: (1) user/item interaction data source, (2) training pipeline (batch or periodic) producing model/embeddings, (3) recommendation service (load model, serve /recommend and /similar), (4) API gateway or BFF calling the service. Include caching and scaling considerations.

### Evaluation Criteria

- [ ] Train and evaluate a collaborative filtering or k-NN recommendation model (RMSE/MAE or ranking metric).
- [ ] Expose recommendations via REST API and document it.
- [ ] Describe how you would add health checks and readiness for K8s.
- [ ] One paragraph on how the recommendation service fits into FreshHarvest-Market architecture.

---

## MONTH 5 — Deep Learning

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Neural networks, backpropagation, CNNs, RNNs; regularization (dropout, L2); optimization (Adam, etc.). |
| **Computational** | Implement or use PyTorch/TensorFlow for MLP and CNN; train on product or image data. |
| **Application** | Product image classifier or tabular DL for FreshHarvest; deploy with FastAPI. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #7 — Master Theory + Math + ML + DL + NLP (Udemy, Krish Naik) |
| **Focus this month** | Deep Learning module: neural networks, backpropagation, CNNs, RNNs, regularization, optimization (Adam, etc.). Complete DL theory and projects. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Perceptron, activation functions (ReLU, sigmoid, softmax) | Building blocks of NNs. | 2-layer MLP from scratch or with framework. |
| Forward propagation, backward propagation | Training NNs. | Backprop for MLP; gradient check. |
| Regularization (L2, dropout), batch normalization | Stability and generalization. | Comparison with/without dropout. |
| Optimization: SGD, momentum, Adam, RMSProp | Practical training. | Train with Adam; plot loss. |
| CNNs: conv, pooling, architectures | Vision in production. | CNN for image classification. |
| RNNs, LSTM, GRU (intro) | Sequences; bridge to NLP. | Small RNN/LSTM on sequence data. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Perceptron, MLP, activations; forward pass | Implement 2-layer MLP in NumPy or PyTorch (forward only or full) | MLP code; forward pass verified |
| **Week 2** | Backpropagation, chain rule in layers | Backprop for MLP; gradient check | Backprop implementation; gradient check |
| **Week 3** | Regularization (dropout, L2), batch norm; optimization (Adam) | Train on overfitting-prone data; compare with/without dropout | Comparison report; tuned model |
| **Week 4** | CNNs: conv, pooling; product image classifier | Train CNN on product images by category; evaluate | CNN model; accuracy on held-out set |

### Implementation Task (FreshHarvest-Market)

Build a **product image classifier**:

- Use CNN (PyTorch or TensorFlow) on product images by category (FreshHarvest or public dataset).
- Report accuracy (and optionally precision/recall per class).
- Create inference script; optionally wrap in FastAPI.

### Production-Level Deliverable

**Image classification API:** input image(s), output category and confidence. Dockerfile; document batch vs single image and latency/throughput tradeoff.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or product-image-classifier/)
├── ml-models/
│   └── product-image-classifier/
│       ├── data/           # Loader, augmentation
│       ├── model/           # CNN definition
│       ├── train.py
│       ├── evaluate.py
│       ├── inference.py
│       └── README.md
├── services/
│   └── image-classifier-api/  # FastAPI, Dockerfile
└── README.md
```

### Architecture Diagram to Design

**Image Classification Service:** Diagram: (1) image upload or URL input, (2) preprocessing (resize, normalize), (3) CNN inference, (4) category + confidence output; (5) optional batch endpoint. Include where GPU would be used and how scaling (replicas, batch size) affects latency and cost.

### Evaluation Criteria

- [ ] Implement or use a CNN and report accuracy on a held-out set.
- [ ] Explain what dropout and batch norm do in one sentence each.
- [ ] Describe batch size vs GPU memory and throughput tradeoff.
- [ ] Ship inference script or API that can be called with an image.

---

## MONTH 6 — NLP

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Text preprocessing, word embeddings, sequence models, transformers intro; sentiment analysis; end-to-end NLP project. |
| **Computational** | Preprocess text; use embeddings (e.g., Word2Vec, or pretrained); build sequence model or fine-tune for sentiment. |
| **Application** | Product review sentiment, title/description classification for FreshHarvest; end-to-end NLP pipeline. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #7 — Master Theory + Math + ML + DL + NLP (Udemy, Krish Naik) |
| **Focus this month** | NLP module: text preprocessing, word embeddings, sequence models, transformers intro, sentiment analysis, end-to-end NLP project. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Text preprocessing (tokenization, lowercasing, stop words, stemming/lemmatization) | Input pipeline for NLP. | Preprocessing pipeline script. |
| Word embeddings (Word2Vec, GloVe, or pretrained) | Dense representation for retrieval and classification. | Embedding lookup; similarity demo. |
| Sequence models (RNN/LSTM for text) | Sentiment, sequence classification. | Trained RNN/LSTM for sentiment. |
| Transformers intro (attention, encoder–decoder) | Bridge to RAG and LLMs. | 1-page summary + diagram. |
| Sentiment analysis | Review scoring for e-commerce. | Sentiment model; eval metrics. |
| End-to-end NLP project | Full pipeline from raw text to prediction. | End-to-end project: data → model → API. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Text preprocessing, tokenization, embeddings | Preprocessing pipeline; load or train embeddings; similarity demo | Preprocessing script; embedding demo |
| **Week 2** | Sequence models (RNN/LSTM) for text | Train RNN/LSTM on sentiment or classification task | Trained model; loss curve |
| **Week 3** | Transformers intro; sentiment with pretrained model | Read transformer intro; fine-tune or use pretrained for sentiment | Sentiment model; eval metrics |
| **Week 4** | End-to-end NLP project | Full pipeline: raw reviews → preprocess → model → prediction; optional API | End-to-end project; README |

### Implementation Task (FreshHarvest-Market)

Build an **end-to-end NLP pipeline** for FreshHarvest:

- **Sentiment analysis** on product reviews: raw text → preprocess → model (RNN/LSTM or small transformer) → sentiment score or class.
- Optional: **product title/description → category** using same or separate model.
- Output: trained model(s), evaluation metrics, inference script or small API.

### Production-Level Deliverable

**NLP service:** at least one endpoint (e.g., sentiment for review text, or category for title+description). Dockerfile; short doc on token limits and scaling (batch inference, model size).

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or nlp-sentiment-pipeline/)
├── ml-models/
│   └── nlp-models/
│       ├── preprocessing/   # Tokenization, cleaning
│       ├── sentiment/      # Sentiment model
│       ├── train.py
│       ├── evaluate.py
│       └── README.md
├── services/
│   └── nlp-api/            # FastAPI, Dockerfile
└── README.md
```

### Architecture Diagram to Design

**NLP Pipeline in FreshHarvest:** Diagram: (1) source of review text (DB, event stream), (2) preprocessing service or step, (3) model inference (sentiment/category), (4) output consumed by catalog service or analytics. Include batch vs real-time and where to cache results.

### Evaluation Criteria

- [ ] Deliver a preprocessing pipeline and at least one trained NLP model (sentiment or classification).
- [ ] Report accuracy/F1 and document token/sequence length handling.
- [ ] Explain in one paragraph how this fits into FreshHarvest (reviews, categories).
- [ ] Ship inference script or API with Dockerfile.

---

### PHASE 2 — Supplementary Resources (Supplements Only)

| Type | Resource | Use |
|------|----------|-----|
| YouTube | StatQuest — ML algorithms | Quick intuition |
| Book | Hands-On ML (Géron) | End-to-end projects |
| Docs | Scikit-learn user guide | Pipelines, APIs |
| Blog | Jay Alammar — RNNs, attention | NLP intuition |

### PHASE 2 — Checkpoint Criteria

- [ ] Train and evaluate at least two classical ML models (e.g., recommendation + one other).
- [ ] Train and evaluate a CNN (product images) and one NLP model (sentiment or classification).
- [ ] Deploy at least one ML/DL service (recommendation or image or NLP) with Docker; document K8s deployment.
- [ ] Produce one end-to-end pipeline from raw data to served prediction.

---

# PHASE 3 — RAG Systems (Months 7–8)

**Primary Course:** #1 — Ultimate RAG Bootcamp Using LangChain, LangGraph & LangSmith (Udemy, Krish Naik)

**Goal:** Design and build production-oriented RAG systems; use LangSmith for debugging and evaluation; deploy RAG to cloud.

---

## MONTH 7 — RAG Foundations + Advanced Techniques

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | RAG architecture (index, retrieve, generate); embeddings, vector DBs; chunking strategies; hybrid search; multimodal RAG; self-RAG, adaptive RAG. |
| **Computational** | Build RAG pipeline with LangChain; implement chunking, embedding, and retrieval; compare strategies. |
| **Application** | FreshHarvest product catalog as knowledge base; “ask about products” and search augmentation. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #1 — Ultimate RAG Bootcamp Using LangChain, LangGraph & LangSmith (Udemy, Krish Naik) |
| **Focus this month** | RAG architecture, embeddings, vector databases, chunking strategies, hybrid search, multimodal RAG, self-RAG, adaptive RAG. Complete foundations and advanced RAG sections. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| RAG architecture (index, retrieve, rerank, generate) | Core pattern for grounded LLM apps. | End-to-end RAG pipeline. |
| Embeddings (open-source vs API); vector DBs | Scalable similarity search. | Index 1k+ chunks in vector DB. |
| Chunking strategies (size, overlap, semantic) | Retrieval quality and relevance. | Compare 2+ chunking strategies; document choice. |
| Hybrid search (keyword + vector) | Better recall on mixed queries. | Hybrid retrieval implementation. |
| Multimodal RAG (text + images) | Richer product search. | Optional: image + text retrieval. |
| Self-RAG, adaptive RAG | Quality and efficiency. | Optional: self-query or adaptive retrieval. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | RAG architecture; embeddings; vector DB setup | Index FreshHarvest catalog (or subset) in vector DB; run similarity search | Indexed corpus; similarity search script |
| **Week 2** | Chunking (size, overlap, semantic); metadata | Compare chunking strategies; measure retrieval recall on sample | Chunking comparison doc; chosen strategy |
| **Week 3** | RAG pipeline: retrieve → rerank (optional) → prompt → LLM | End-to-end RAG on product catalog or docs | RAG pipeline code; example Q&A |
| **Week 4** | Hybrid search; optional self-RAG/adaptive | Implement hybrid search; optional advanced RAG variant | Hybrid retrieval; short doc on tradeoffs |

### Implementation Task (FreshHarvest-Market)

Build **RAG over FreshHarvest product catalog**:

- Ingest product catalog (or subset) into vector DB (Chroma, Qdrant, Pinecone, or similar via LangChain).
- Implement chunking (e.g., per product or by description); compare at least two strategies on a small eval set.
- Build pipeline: query → embed → retrieve → (rerank) → prompt → LLM → answer.
- Document failure modes (retrieval misses, hallucination) and one mitigation each (e.g., rerank, grounding, prompts).

### Production-Level Deliverable

**RAG service:** endpoint(s) for “ask about products” (and optional chat). Document failure modes and mitigations; API contract for integration with FreshHarvest front-end or search.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or rag-product-catalog/)
├── services/
│   └── rag-service/
│       ├── ingestion/      # Index catalog to vector DB
│       ├── chunking/      # Strategies and comparison
│       ├── pipeline/      # Retrieve, rerank, prompt, LLM
│       ├── api/           # FastAPI or LangChain serve
│       ├── docs/          # Architecture, failure modes
│       └── README.md
└── README.md
```

### Architecture Diagram to Design

**RAG System Architecture:** Diagram: (1) data source (product catalog/DB), (2) ingestion pipeline (chunk → embed → vector DB), (3) query path (user query → embed → retrieve → rerank → prompt + context → LLM → response). Label LangChain/LangGraph components, vector DB, and LLM. Add a small “failure modes” callout (retrieval miss, hallucination) with mitigation.

### Evaluation Criteria

- [ ] Run RAG end-to-end and show one example query with retrieved context and answer.
- [ ] Compare two chunking strategies with a small eval set (recall or relevance).
- [ ] Document failure modes and at least one mitigation each.
- [ ] Provide API or interface that could be integrated into FreshHarvest.

---

## MONTH 8 — Agentic RAG + LangSmith Evaluation

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Multi-agent RAG pipelines with LangGraph; autonomous RAG; LangSmith for debugging, tracking, evaluation. |
| **Computational** | Build multi-step or agentic RAG with LangGraph; use LangSmith for traces and eval; deploy RAG to cloud. |
| **Application** | Production RAG with observability; deploy to cloud (e.g., AWS, GCP, or Docker on cloud VM). |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #1 — Ultimate RAG Bootcamp (Udemy, Krish Naik) |
| **Focus this month** | Agentic RAG, multi-agent RAG with LangGraph, autonomous RAG, LangSmith for debugging/tracking/evaluation, deploy RAG to cloud. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Multi-agent RAG pipelines (LangGraph) | Complex workflows; routing, multi-step reasoning. | Multi-step RAG or agentic RAG pipeline. |
| Autonomous RAG (agent decides when to retrieve/generate) | Quality and cost. | Pipeline with conditional retrieve/generate. |
| LangSmith: debugging, tracing, tracking | Observability and iteration. | LangSmith project with traces and runs. |
| LangSmith: evaluation (correctness, relevance) | Production quality gates. | Eval dataset; metrics in LangSmith. |
| Deploy RAG to cloud | Production readiness. | Deployed RAG API (e.g., cloud run, ECS, or VM). |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | LangGraph for RAG; multi-step flows | Build RAG flow with LangGraph (retrieve → maybe reretrieve → generate) | LangGraph RAG pipeline |
| **Week 2** | LangSmith: tracing, debugging | Instrument pipeline; inspect traces and debug one failure | LangSmith project; trace examples |
| **Week 3** | LangSmith: evaluation | Create eval set; run evals; log metrics (correctness, relevance) | Eval dataset; LangSmith eval results |
| **Week 4** | Deploy RAG to cloud | Deploy RAG API to cloud (e.g., AWS Lambda + API GW, or container on ECS/Cloud Run) | Deployed endpoint; runbook |

### Implementation Task (FreshHarvest-Market)

**Agentic RAG + production deployment:**

- Extend Month 7 RAG with LangGraph: multi-step or conditional retrieval (e.g., self-query, adaptive).
- Instrument with LangSmith: log runs, traces, and eval results.
- Deploy to cloud: containerized RAG service behind an API (e.g., AWS ECS, Cloud Run, or EC2 + Docker).
- Document runbook: how to redeploy, check LangSmith, rollback.

### Production-Level Deliverable

**Production RAG service** on cloud with LangSmith observability: deployed API, tracing, and evaluation dashboard; runbook and one paragraph on scaling and cost.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or rag-production/)
├── services/
│   └── rag-service/
│       ├── pipeline/      # LangGraph RAG
│       ├── evaluation/   # LangSmith eval config and dataset
│       ├── deploy/       # Dockerfile, cloud config (e.g., ECS, Cloud Run)
│       ├── runbook.md
│       └── README.md
└── README.md
```

### Architecture Diagram to Design

**Production RAG + LangSmith:** Diagram: (1) User/API → (2) RAG service (LangGraph pipeline) → (3) Vector DB + LLM; (4) LangSmith receiving traces and eval runs. Add cloud boundary (e.g., VPC, load balancer, container service). Label where logs and metrics go (LangSmith, cloud logging).

### Evaluation Criteria

- [ ] Build a multi-step or agentic RAG pipeline with LangGraph.
- [ ] Use LangSmith for tracing and at least one evaluation metric (e.g., faithfulness, relevance).
- [ ] Deploy RAG to cloud and document the deployment.
- [ ] Write runbook with redeploy and rollback steps.

---

### PHASE 3 — Supplementary Resources (Supplements Only)

| Type | Resource | Use |
|------|----------|-----|
| Docs | LangChain, LangGraph, LangSmith | Implementation and patterns |
| Blog | RAG survey posts, retrieval best practices | Design choices |

### PHASE 3 — Checkpoint Criteria

- [ ] Ship a RAG pipeline over FreshHarvest catalog (or equivalent) with at least two chunking strategies compared.
- [ ] Use LangSmith for tracing and evaluation.
- [ ] Deploy RAG to cloud and document architecture and runbook.

---

# PHASE 4 — Agentic AI (Month 9)

**Primary Course:** #3 — Complete Agentic AI Bootcamp with LangGraph and LangChain (Udemy, Krish Naik)

**Goal:** Build single and multi-agent systems with memory and tools; design event-driven workflows and state transitions; apply to FreshHarvest use cases (research, task automation).

---

## MONTH 9 — Agentic AI

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Single agents with memory and tools; multi-agent collaboration; event-driven workflows; state transitions; autonomous research agents; task automation bots. |
| **Computational** | Build agents with LangChain/LangGraph; implement tools, memory, and multi-agent orchestration; state machines. |
| **Application** | Inventory or pricing agent, research agent, or task automation bot for FreshHarvest. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #3 — Complete Agentic AI Bootcamp with LangGraph and LangChain (Udemy, Krish Naik) |
| **Focus this month** | Single agents (memory, tools), multi-agent collaboration, event-driven workflows, state transitions, autonomous research agents, task automation bots. Complete all modules and projects. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Single agents: tools (function calling), memory | Agents that use APIs and retain context. | Agent with 2+ tools and memory. |
| Multi-agent collaboration (orchestrator + specialists) | Complex tasks; separation of concerns. | Multi-agent design or implementation. |
| Event-driven workflows | Production integration; async. | Workflow that reacts to events. |
| State transitions (LangGraph state machine) | Reliable multi-step behavior. | Graph with clear states and transitions. |
| Autonomous research agents | Gather and synthesize information. | Research agent (e.g., product/supplier research). |
| Task automation bots | Repetitive tasks (orders, alerts). | Bot that automates one concrete task. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Single agent: tools, LLM chooses tool and args; memory | Agent that can query product API and answer user questions with memory | Agent with 2+ tools and memory; example dialogue |
| **Week 2** | Multi-agent: orchestrator + specialists | Design or implement inventory + pricing (or search) agents; orchestrator coordinates | Multi-agent design doc or code |
| **Week 3** | Event-driven workflows; state transitions (LangGraph) | Build workflow with state machine (e.g., order approval, research steps) | LangGraph workflow with states and transitions |
| **Week 4** | Autonomous research agent or task automation bot | Research agent (e.g., “find suppliers for X”) or task bot (e.g., low-stock alerts → draft order) | End-to-end agent or bot; README |

### Implementation Task (FreshHarvest-Market)

Build an **inventory management AI agent** (or equivalent):

- At least 2–3 tools: e.g., “get low-stock items”, “get pricing history”, “place order” (mock).
- Optional: auto-generate supplier orders (rule-based or simple model) as tool or sub-agent.
- Optional: pricing trend analysis as tool or sub-agent.
- Document one risk (e.g., wrong tool, wrong args) and a mitigation; sketch tracing/logging for production.

### Production-Level Deliverable

**Agent service:** agent loop (ReAct or LangGraph) with tools; mock or real APIs; README and architecture diagram; document reliability (timeouts, retries, idempotency for orders) and security (tool scope, input validation, audit logging).

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or inventory-agent/)
├── services/
│   └── inventory-agent/
│       ├── tools/          # get_low_stock, get_pricing_history, place_order (mock)
│       ├── agent/          # LangGraph or ReAct loop
│       ├── memory/         # If applicable
│       ├── docs/           # Architecture, risks, tracing
│       └── README.md
└── README.md
```

### Architecture Diagram to Design

**Agent System Architecture:** Diagram: (1) User or event input → (2) Agent (LangGraph) with state; (3) Tools (product API, inventory API, order API); (4) Memory store; (5) Logging/tracing (e.g., LangSmith). Label failure points (timeout, wrong tool, invalid args) and where retries and validation sit.

### Evaluation Criteria

- [ ] Demonstrate an agent that uses at least two tools correctly in one run.
- [ ] Document one risk of agentic systems (e.g., wrong tool, wrong args) and a mitigation.
- [ ] Sketch how you would trace and log agent decisions in production.
- [ ] Deliver architecture diagram and one paragraph on reliability (timeouts, idempotency) and security (tool scope, audit).

---

### PHASE 4 — Supplementary Resources (Supplements Only)

| Type | Resource | Use |
|------|----------|-----|
| Docs | LangChain Agents, LangGraph | Implementation |
| Blog | Lilian Weng — LLM Agent survey | Theory and patterns |

### PHASE 4 — Checkpoint Criteria

- [ ] Ship an agent with at least two tools and memory (or multi-agent).
- [ ] Document risks and mitigations and production tracing.
- [ ] Produce architecture diagram for the agent system.

---

# PHASE 5 — MLOps & Production AI (Months 10–12)

**Primary Course:** #5 — Complete MLOps Bootcamp with 10+ End-to-End ML Projects (Udemy, Krish Naik)

**Goal:** Implement MLOps core (versioning, experiment tracking, pipelines, CI/CD) and deploy ML/Gen AI to cloud with monitoring.

---

## MONTH 10 — MLOps Core

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Git/GitHub for ML; Docker containerization; MLflow experiment tracking; DVC data versioning; DagsHub. |
| **Computational** | Set up versioning (DVC), experiment tracking (MLflow), and containerization for at least one ML project. |
| **Application** | Reproducible training and data lineage for FreshHarvest ML services. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #5 — Complete MLOps Bootcamp with 10+ End-to-End ML Projects (Udemy, Krish Naik) |
| **Focus this month** | Git/GitHub for ML, Docker containerization, MLflow experiment tracking, DVC data versioning, DagsHub. Complete MLOps fundamentals and first projects. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Git/GitHub for ML (code, config, not data in repo) | Version control and collaboration. | ML repo structure; .gitignore for data/models. |
| Docker containerization for ML | Reproducible environments; deployment. | Dockerfile for training and/or inference. |
| MLflow: experiment tracking (params, metrics, artifacts) | Reproducibility and comparison. | MLflow project with ≥2 runs logged. |
| DVC: data versioning (datasets, large files) | Data lineage and reproducibility. | DVC setup; versioned dataset. |
| DagsHub (or similar) integration | Unified ML project hub. | Optional: project on DagsHub. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Git/GitHub for ML; Docker for ML | ML repo structure; Dockerfile for one training or inference service | Repo with Dockerfile; run container locally |
| **Week 2** | MLflow: experiment tracking | Log params, metrics, artifacts for ≥2 training runs | MLflow project; compare runs in UI |
| **Week 3** | DVC: data versioning | Add DVC to project; version one dataset | DVC config; versioned dataset; dvc pull flow |
| **Week 4** | DagsHub or consolidate | Optional DagsHub; document versioning and experiment strategy | 1-page MLOps strategy doc |

### Implementation Task (FreshHarvest-Market)

Apply **MLOps core** to one existing FreshHarvest ML asset:

- Choose one project (e.g., recommendation, demand forecast, or NLP).
- Add Git-based repo structure (code + config only); Dockerfile for training or inference.
- Add MLflow for experiment tracking (log params, metrics, model artifact).
- Add DVC for data (or document why data is excluded); version one dataset or data config.

### Production-Level Deliverable

**MLOps-ready project:** versioned code (Git), versioned data (DVC where applicable), experiment tracking (MLflow), and containerized build (Docker). One-page document: how we version data and models and run experiments.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or mlops-core-demo/)
├── .gitignore        # data/, models/, .env
├── dvc.yaml          # Data pipeline (if using DVC)
├── Dockerfile        # Training or inference
├── mlflow_project/   # Or MLflow at repo root
│   └── ...
├── data/             # DVC-tracked or documented
├── docs/
│   └── mlops-strategy.md
└── README.md
```

### Architecture Diagram to Design

**MLOps Core — Data and Model Flow:** Diagram: (1) Raw data (versioned with DVC or external store), (2) Training job (Docker, MLflow run), (3) MLflow artifact store (model, metrics), (4) Inference service (load from MLflow or exported artifact). Label Git (code), DVC (data), MLflow (experiments, artifacts).

### Evaluation Criteria

- [ ] Have a Git repo with clear separation of code/config vs data/models.
- [ ] Run training (or inference) in Docker and document the image.
- [ ] Log at least 2 runs to MLflow with params, metrics, and artifact.
- [ ] Document data versioning (DVC or alternative) and one-page MLOps strategy.

---

## MONTH 11 — ML Pipelines & CI/CD

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | Apache Airflow (or Astro) for orchestration; ETL pipelines; CI/CD with GitHub Actions; end-to-end ML project deployment. |
| **Computational** | Build an ETL or training pipeline with Airflow/Astro; CI/CD that builds, tests, and deploys an ML service. |
| **Application** | Automated training and deployment for one FreshHarvest ML service. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #5 — Complete MLOps Bootcamp (Udemy, Krish Naik) |
| **Focus this month** | Apache Airflow with Astro, ETL pipelines, CI/CD with GitHub Actions, end-to-end ML project deployment. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| Apache Airflow (or Astro): DAGs, tasks, scheduling | Orchestration for ETL and training. | One DAG: data prep → train → (evaluate) → register. |
| ETL pipelines for ML (extract, transform, load) | Data readiness for training. | ETL DAG or script. |
| CI/CD with GitHub Actions | Automated test and deploy. | Workflow: build image, test, deploy (e.g., to staging/K8s). |
| End-to-end ML project deployment | From code push to running service. | Full pipeline: trigger on push or schedule → deploy. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | Airflow/Astro: DAGs, tasks | Create DAG with ≥2 tasks (e.g., fetch data, preprocess) | DAG code; run locally or in Astro |
| **Week 2** | ETL + train in pipeline | Extend DAG: data → train → log to MLflow (or save artifact) | End-to-end DAG |
| **Week 3** | GitHub Actions: build, test | CI: on push, run tests and build Docker image | .github/workflows/*.yml |
| **Week 4** | CI/CD: deploy to staging or K8s | CD: deploy image to staging or K8s; document rollback | Deploy workflow; rollback doc |

### Implementation Task (FreshHarvest-Market)

Build **CI/CD for one ML service**:

- Pipeline: code push → run tests → build Docker image → (optional) run training or use cached model → deploy to staging or K8s.
- Use Airflow/Astro for scheduled training or ETL if applicable.
- Document: how to trigger deployment, how to rollback to a previous image or model version.

### Production-Level Deliverable

**End-to-end ML deployment pipeline:** GitHub Actions (or equivalent) that builds, tests, and deploys one ML service (e.g., recommendation, demand forecast, or NLP); optional Airflow DAG for training/ETL; runbook with rollback.

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or mlops-pipeline/)
├── .github/
│   └── workflows/
│       ├── ci.yml          # Test, build
│       └── deploy.yml      # Deploy to staging/K8s
├── airflow_dags/           # Optional
│   └── ml_pipeline.py
├── services/
│   └── <ml-service>/       # One of recommendation, demand, nlp
│       ├── Dockerfile
│       └── ...
├── runbook.md              # Deploy, rollback
└── README.md
```

### Architecture Diagram to Design

**CI/CD + Pipeline Architecture:** Diagram: (1) Developer push → (2) GitHub Actions (test → build image → push to registry), (3) Deploy step (K8s or cloud service), (4) Optional: Airflow DAG (schedule) triggering training or ETL → MLflow/model store. Label rollback path (previous image or model version).

### Evaluation Criteria

- [ ] Have a CI workflow that runs tests and builds Docker image on push.
- [ ] Have a CD workflow (or manual step) that deploys to staging or K8s.
- [ ] Document rollback procedure (image or model version).
- [ ] Optional: one Airflow DAG for training or ETL.

---

## MONTH 12 — Cloud Deployment & Monitoring

### Learning Goals

| Goal Type      | Description |
|----------------|-------------|
| **Conceptual** | AWS SageMaker (or equivalent), HuggingFace NLP deployment, Gen AI on AWS; Grafana + PostgreSQL (or similar) for monitoring; full production pipeline. |
| **Computational** | Deploy one model to cloud (SageMaker or container); set up monitoring (Grafana + DB or cloud metrics). |
| **Application** | Production-ready ML/Gen AI service on cloud with monitoring and runbook. |

### Primary Course

| Item | Detail |
|------|--------|
| **Course** | #5 — Complete MLOps Bootcamp (Udemy, Krish Naik) |
| **Focus this month** | AWS SageMaker, HuggingFace NLP deployment, Gen AI on AWS, Grafana + PostgreSQL monitoring, full production pipeline. |

### Exact Topics

| Topic | Why It Matters for ML/AI | Key Deliverable |
|-------|---------------------------|-----------------|
| AWS SageMaker (training, hosting, or both) | Managed ML in production. | One model deployed on SageMaker (or equivalent). |
| HuggingFace NLP deployment (SageMaker HF DLC or container) | NLP models in production. | Deploy HuggingFace model (e.g., sentiment) to cloud. |
| Gen AI on AWS (Bedrock, or LLM in container) | RAG/agent in production. | Optional: RAG or LLM endpoint on AWS. |
| Grafana + PostgreSQL (or Prometheus + DB) for monitoring | Observability and SLOs. | Dashboard with latency, errors, or business metrics. |
| Full production pipeline | From data to monitored service. | End-to-end pipeline doc and runbook. |

### Weekly Milestones

| Week | Focus | Milestone | Deliverable |
|------|--------|-----------|-------------|
| **Week 1** | AWS SageMaker (or cloud ML hosting) | Deploy one model (e.g., sklearn or PyTorch) to SageMaker or container service | Deployed endpoint; invoke from script |
| **Week 2** | HuggingFace on cloud; Gen AI on AWS | Deploy HF model (e.g., sentiment); optional Bedrock/LLM | HF endpoint; optional Gen AI endpoint |
| **Week 3** | Monitoring: metrics, Grafana, PostgreSQL (or similar) | Instrument service (latency, errors); Grafana dashboard; optional DB for metrics | Dashboard; metric definitions |
| **Week 4** | Full production pipeline; runbook; one-pager | Tie together: versioning, CI/CD, deployment, monitoring; write runbook and one-pager | Runbook; one-pager: “Production AI pipeline” |

### Implementation Task (FreshHarvest-Market)

**Production deployment and monitoring:**

- Deploy one ML or Gen AI service (e.g., demand forecast, NLP, or RAG) to cloud (AWS SageMaker, ECS, or equivalent).
- Add monitoring: latency, errors, optional business metric (e.g., recommendation CTR placeholder); Grafana + PostgreSQL or cloud metrics.
- Write runbook: deploy, rollback, scale, alerting.
- Write one-pager: “Production AI Pipeline for FreshHarvest” (lifecycle, serving, monitoring, cost).

### Production-Level Deliverable

**Production-ready ML/Gen AI service** on cloud with monitoring dashboard and runbook; one-pager summarizing the full pipeline (versioning, CI/CD, deployment, monitoring, cost).

### GitHub Portfolio Artifact

```
FreshHarvest-Market/  (or ml-production/)
├── services/
│   └── <production-service>/
│       ├── app/
│       ├── Dockerfile
│       ├── deploy/         # SageMaker or K8s/ECS config
│       ├── monitoring/     # Grafana dashboards, metric config
│       └── runbook.md
├── docs/
│   └── production-ai-pipeline-onepager.md
└── README.md
```

### Architecture Diagram to Design

**Production AI — Full Stack:** Diagram: (1) Data/versioning (DVC, MLflow), (2) CI/CD (GitHub Actions) → build & deploy, (3) Cloud runtime (SageMaker / ECS / K8s) with ML or Gen AI service, (4) Monitoring (Grafana, PostgreSQL or Prometheus, alerts). Label cost and scaling levers (instance type, replicas, scale-to-zero).

### Evaluation Criteria

- [ ] Deploy at least one ML or Gen AI service to cloud (SageMaker or container).
- [ ] Expose at least one reliability or business metric and one dashboard (Grafana or cloud).
- [ ] Document runbook (deploy, rollback, alerting).
- [ ] Write one-pager: “Production AI Pipeline” (lifecycle, serving, monitoring, cost).

---

### PHASE 5 — Supplementary Resources (Supplements Only)

| Type | Resource | Use |
|------|----------|-----|
| Docs | MLflow, DVC, DagsHub | Versioning and experiments |
| Docs | GitHub Actions, Airflow/Astro | CI/CD and orchestration |
| Docs | AWS SageMaker, HuggingFace deployment | Cloud deployment |
| Docs | Grafana, Prometheus | Monitoring |

### PHASE 5 — Checkpoint Criteria

- [ ] Have versioning (Git, DVC, MLflow) and containerization (Docker) for at least one project.
- [ ] Have CI/CD that deploys an ML service to cloud or K8s.
- [ ] Have monitoring (dashboard + runbook) for at least one production-like deployment.
- [ ] Produce one-pager summarizing the production AI pipeline.

---

# Summary: 12 Months at a Glance

| Phase | Months | Primary Course | Key Outcome |
|-------|--------|----------------|-------------|
| **1. Math** | 1–3 | #2 — Math Foundation | Linear algebra, probability, calculus; similarity search, churn model, gradient descent from scratch |
| **2. ML + DL + NLP** | 4–6 | #7 — ML + DL + NLP | Classical ML (recommendation), deep learning (CNN), NLP (sentiment); end-to-end projects |
| **3. RAG** | 7–8 | #1 — RAG Bootcamp | RAG over catalog; LangGraph; LangSmith; deploy RAG to cloud |
| **4. Agentic AI** | 9 | #3 — Agentic AI Bootcamp | Single/multi-agent with tools and memory; inventory or task automation agent |
| **5. MLOps** | 10–12 | #5 — MLOps Bootcamp | Versioning (DVC, MLflow), Docker, CI/CD, Airflow, cloud deployment, Grafana monitoring |

**Target identity after 12 months:**  
**AI-Native Distributed Systems Architect / GenAI Platform Engineer** — capable of designing and implementing production ML and GenAI systems: math foundations, classical ML and deep learning, NLP, RAG, agentic AI, and MLOps (versioning, pipelines, CI/CD, cloud deployment, monitoring), with FreshHarvest-Market as the reference e-commerce platform.

---

*Document version: 3.0 | Based on Krish Naik Udemy courses #2, #7, #1, #3, #5 | Optional/skipped: #4 CV, #6 GenAI LangChain/HF, #8 Gemini Pro | Last updated: February 2025*
