# Month 1 — Linear Algebra for Machine Learning

**Duration:** 4 weeks  
**Phase:** Mathematical Foundations

---

## Table of Contents

1. [Primary & Supplementary Resources](#primary--supplementary-resources)
2. [Learning Objectives for the Month](#learning-objectives-for-the-month)
3. [Topic Breakdown with ML Relevance](#topic-breakdown-with-ml-relevance)
4. [Weekly Plan (Week 1–4)](#weekly-plan-week-14)
5. [Key Formulas Reference](#key-formulas-reference)
6. [Practice Exercises (Python-based)](#practice-exercises-python-based)
7. [Mini-Project: Vector Similarity Search Engine](#mini-project-vector-similarity-search-engine)
8. [Self-Check Questions](#self-check-questions)
9. [My Notes (Placeholder)](#my-notes-placeholder)

---

## Primary & Supplementary Resources

| Resource | Type | Link / Location | When to Use |
|----------|------|-----------------|-------------|
| **Mathematics for Machine Learning: Linear Algebra** | Course | [Coursera — Imperial College London](https://www.coursera.org/learn/linear-algebra-machine-learning) | Primary: follow module-by-module; complete quizzes and assignments |
| **Essence of Linear Algebra** | Video playlist | 3Blue1Brown (YouTube) | Before or alongside course: build geometric intuition for every concept |

**Suggested flow:** Watch the relevant 3Blue1Brown video for a topic, then complete the corresponding Imperial module, then run the Python examples in this guide.

---

## Learning Objectives for the Month

By the end of Month 1, you should be able to:

- Represent data as **vectors** and explain why feature vectors and word embeddings are vectors.
- Compute and interpret **dot product** and **cosine similarity** and relate them to similarity search and attention.
- Perform **matrix multiplication** and explain how a single neural network layer is a linear transformation (matrix × vector).
- Set up and solve **systems of linear equations** in matrix form (e.g., for closed-form solutions to linear models).
- Describe **linear transformations** geometrically and as matrices.
- Use **basis**, **span**, and **linear independence** to reason about feature spaces and dimensionality.
- Compute **eigenvalues** and **eigenvectors** and explain their role in **PCA** and dimensionality reduction.
- Apply **SVD** conceptually and in code for recommendation systems and data compression.

---

## Topic Breakdown with ML Relevance

### 1. Vectors (what they are, operations, geometric intuition)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Vector** | Ordered list of numbers; arrow in space with magnitude and direction | **Feature vectors:** each data point (e.g., user, product) is a vector of features. **Word embeddings:** each word is a vector in a high-dimensional space. |
| **Vector addition** | Component-wise; geometrically: head-to-tail | Combining or comparing feature representations. |
| **Scalar multiplication** | Scale length; direction unchanged (unless negative) | Normalization, scaling features. |
| **Vector norm** | Length: `‖v‖ = sqrt(v₁² + ... + vₙ²)` | Measuring magnitude; normalizing to unit vectors for fair similarity. |

**Why it matters for ML:** Every input to a model is a vector (e.g., pixel values, word IDs turned into embeddings). You need to add, scale, and measure length of these vectors constantly.

---

### 2. Dot Product & Cosine Similarity

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Dot product** | `a · b = Σᵢ(aᵢ bᵢ) = ‖a‖ ‖b‖ cos(θ)` | **Similarity search:** high dot product ⇒ similar. **Attention:** attention scores are often dot products between query and key vectors. |
| **Cosine similarity** | `cos(θ) = (a · b) / (‖a‖ ‖b‖)`; angle between vectors, ignores length | Comparing embeddings when magnitude doesn’t matter (e.g., text similarity). |

**Why it matters for ML:** Recommendation (“find items similar to this one”) and transformer attention both rely on dot products and cosine similarity between vectors.

---

### 3. Matrices & Matrix Operations

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Matrix** | Rectangular array of numbers; rows and columns | **Neural network layer:** weights stored in a matrix **W**; output = `Wx + b`. |
| **Matrix–vector product** | **Ax**: linear combination of columns of **A** | One layer: multiply weight matrix by input vector to get pre-activation. |
| **Matrix–matrix product** | `(AB)ᵢⱼ = Σₖ Aᵢₖ Bₖⱼ` | Batch of inputs: **XWᵀ** processes many vectors at once. |

**Why it matters for ML:** Training and inference in neural networks are dominated by matrix multiplications. Understanding shape and meaning of **Wx** is essential.

---

### 4. Systems of Linear Equations

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **System** | **Ax = b**; find **x** | **Solving for parameters:** e.g., normal equations **XᵀXw = Xᵀy** for linear regression. |
| **Unique / many / no solution** | Depends on rank and dimensions of **A** | Determines whether a unique set of weights exists or we need regularization / iterative methods. |

**Why it matters for ML:** Closed-form solutions (linear regression, some Bayesian updates) reduce to solving linear systems. Iterative methods (gradient descent) are used when systems are large or not invertible.

---

### 5. Linear Transformations

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Linear transformation** | Map *T* with `T(v+w) = T(v) + T(w)` and `T(cv) = c·T(v)` | **What a layer does:** each layer applies a linear map (matrix) then (often) a nonlinearity. |
| **Matrix as transformation** | Columns of **A** are where basis vectors go | Intuition for how weight matrix stretches/rotates the input space. |

**Why it matters for ML:** A neural network layer is “linear transformation + activation.” Understanding linear maps helps you reason about capacity and behavior of networks.

---

### 6. Basis, Span, Linear Independence

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Span** | All linear combinations of a set of vectors | **Feature space:** the set of outputs you can get from a layer with given weights. |
| **Linear independence** | No vector in the set is a linear combination of the others | **Redundant features:** linearly dependent features add no new information; can cause multicollinearity. |
| **Basis** | Linearly independent set that spans the space; dimension = size of basis | **Latent dimensions:** e.g., PCA finds a new basis for the data; embeddings live in a space with a certain dimension. |

**Why it matters for ML:** You reason about “how many effective dimensions” your data or representation has, and whether your features are redundant.

---

### 7. Eigenvalues & Eigenvectors

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **Eigenvector** | **Av = λv**; direction unchanged by **A** | **PCA:** principal components are eigenvectors of the covariance matrix. |
| **Eigenvalue** | λ: scale factor along that direction | **Dimensionality reduction:** keep directions with largest eigenvalues; drop small ones. |

**Why it matters for ML:** PCA, LDA, and many spectral methods rely on eigenvalues and eigenvectors. They tell you which directions in the data have the most variance.

---

### 8. Singular Value Decomposition (SVD)

| Concept | Definition / Intuition | ML Relevance |
|---------|------------------------|---------------|
| **SVD** | `A = UΣVᵀ`; orthogonal matrices + diagonal singular values | **Recommendation systems:** low-rank approximation of user–item matrix. **Data compression:** approximate **A** with few singular values. |
| **Low-rank approximation** | Keep top *k* singular values; reconstruct **A**_k | Compression; denoising; collaborative filtering. |

**Why it matters for ML:** Matrix factorization (e.g., in recommenders) and many dimensionality-reduction and compression techniques are SVD under the hood.

---

## Weekly Plan (Week 1–4)

### Week 1: Vectors, Dot Product, Cosine Similarity

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Vectors: definition, addition, scalar multiplication, norm | Coursera Week 1; 3B1B “Vectors, what even are they?” |
| 3 | Dot product: algebraic and geometric (length × length × cos θ) | 3B1B “Dot products”; compute by hand in 2D |
| 4 | Cosine similarity; angle between vectors | NumPy: `np.dot`, normalize, then dot product = cosine similarity |
| 5 | Review + practice | Coursera quiz; implement “angle between two vectors” in Python |

---

### Week 2: Matrices, Systems of Equations, Linear Transformations

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Matrices; matrix–vector and matrix–matrix multiplication | Coursera; 3B1B “Matrix multiplication as composition” |
| 3 | Systems of linear equations **Ax = b**; inverse when square and invertible | Coursera; `np.linalg.solve` |
| 4 | Linear transformations; matrix as transformation | 3B1B “Linear transformations”; relate to one layer of a NN |
| 5 | Review + practice | Mini exercise: implement `Y = XWᵀ + b` for a batch |

---

### Week 3: Basis, Span, Linear Independence; Eigenvalues & Eigenvectors

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | Span, linear independence, basis, dimension | Coursera; 3B1B “Span”, “Linear dependence” |
| 3 | Eigenvalues and eigenvectors: **Av = λv** | Coursera; 3B1B “Eigenvalues and eigenvectors” |
| 4 | Computing eigenvalues/eigenvectors in Python; link to PCA | `np.linalg.eig` or `eigh` for symmetric |
| 5 | Review + practice | Quiz; derive “eigenvectors of covariance ⇒ principal directions” |

---

### Week 4: SVD and Mini-Project

| Day | Topic | Activities |
|-----|------|------------|
| 1–2 | SVD: `A = UΣVᵀ`; low-rank approximation | Coursera; 3B1B “Change of basis” (conceptually); `np.linalg.svd` |
| 3 | Use SVD for recommendation / compression (conceptual or small example) | Small matrix: truncate Σ, reconstruct, compare |
| 4–5 | **Mini-project:** Vector Similarity Search Engine (see below) | Implement; test on toy product vectors |

---

## Key Formulas Reference

| Concept | Formula |
|---------|---------|
| **Vector norm** | `‖v‖ = sqrt(Σᵢ vᵢ²) = sqrt(v·v)` |
| **Dot product** | `a·b = Σᵢ aᵢ bᵢ = ‖a‖ ‖b‖ cos(θ)` |
| **Cosine similarity** | `cos(θ) = (a·b) / (‖a‖ ‖b‖)` |
| **Matrix–vector product** | `(Ax)ᵢ = Σⱼ Aᵢⱼ xⱼ` |
| **Matrix–matrix product** | `(AB)ᵢⱼ = Σₖ Aᵢₖ Bₖⱼ` |
| **Eigenvalue equation** | `Av = λv` |
| **SVD** | `A = UΣVᵀ`, **U**, **V** orthogonal, **Σ** diagonal |
| **Low-rank approx** | `Aₖ = Uₖ Σₖ Vₖᵀ` (first *k* singular values) |

---

## Practice Exercises (Python-based)

### Exercise 1: Vector operations and cosine similarity

```python
import numpy as np

# Create two 5D vectors (e.g., product feature vectors)
v1 = np.array([1.0, 2.0, 0.5, 3.0, 1.5])
v2 = np.array([2.0, 1.0, 1.0, 2.0, 2.0])

# Norm
print("||v1|| =", np.linalg.norm(v1))

# Dot product
dot = np.dot(v1, v2)
print("v1 · v2 =", dot)

# Cosine similarity (normalize then dot product)
v1_norm = v1 / np.linalg.norm(v1)
v2_norm = v2 / np.linalg.norm(v2)
cos_sim = np.dot(v1_norm, v2_norm)
print("Cosine similarity =", cos_sim)
```

### Exercise 2: Matrix as linear transformation

```python
# Weight matrix W (3 output dims, 4 input dims) and input x
W = np.array([[1, 0, -1, 0],
              [0, 1, 0, -1],
              [1, 1, 1, 1]], dtype=float)
x = np.array([1.0, 2.0, 0.5, 0.5])

# One layer: y = Wx (no bias for simplicity)
y = W @ x
print("y = Wx =", y)
```

### Exercise 3: SVD and low-rank approximation

```python
# Small matrix (e.g., user-item ratings)
A = np.array([[5, 4, 0, 1],
              [4, 0, 4, 1],
              [1, 1, 0, 5],
              [0, 1, 5, 4]], dtype=float)

U, S, Vt = np.linalg.svd(A)
# Low-rank-2 approximation
k = 2
A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
print("Rank-2 approximation:\n", np.round(A_k, 2))
```

---

## Mini-Project: Vector Similarity Search Engine

**Goal:** Build a small “search engine” that, given a query product (as a vector), returns the most similar products using dot product or cosine similarity.

**Steps:**

1. **Data:** Create 10–20 “products” as vectors (e.g., 5–10 features: price norm, category one-hot, popularity score). Store in a matrix **P** (each row = one product).
2. **Query:** Take one product vector **q**.
3. **Similarity:** Compute similarity of **q** to every row of **P** (dot product or cosine similarity). Use vectorized operations: `similarities = P @ q` or normalize rows and `q`, then `P_norm @ q_norm`.
4. **Rank:** Sort by similarity (descending); return top *k* product indices (or names).
5. **Optional:** Add a simple CLI or Jupyter interface: input “product id”, output “top 5 similar products”.

**Success criteria:** You use only NumPy (no sklearn.neighbors). You can explain why dot product or cosine similarity is a reasonable “similarity” for recommendations.

---

## Self-Check Questions

1. What is the geometric interpretation of the dot product of two unit vectors?
2. Why do we often normalize vectors before comparing them in ML (e.g., for similarity)?
3. If **W** is (64, 128) and **x** is (128,), what is the shape of **Wx**?
4. In one sentence, what does a linear transformation do geometrically?
5. What do eigenvalues of a covariance matrix represent in PCA?
6. Give one ML application of SVD.

---

## My Notes (Placeholder)

*Use the sections below to add your own notes as you learn. Delete this line when you start.*

### Vectors and dot product
<!-- Your notes here -->


### Matrices and linear transformations
<!-- Your notes here -->


### Basis, eigenvalues, SVD
<!-- Your notes here -->


### Mini-project and takeaways
<!-- Your notes here -->
