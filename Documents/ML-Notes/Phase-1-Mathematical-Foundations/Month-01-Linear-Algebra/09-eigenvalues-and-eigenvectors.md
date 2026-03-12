# 09 — Eigenvalues and Eigenvectors

---

## 1. What Are Eigenvalues and Eigenvectors?

**Visual intuition (see 3Blue1Brown for great visualizations):** When you apply a linear transformation (matrix) to most vectors, they change both length and **direction**. But some special vectors only get **scaled** — stretched or compressed — and their **direction stays the same**. Those special vectors are **eigenvectors**, and the scaling factor is the **eigenvalue** (λ).

**ASCII diagram — before/after transformation:**

```
    Not an eigenvector:          Eigenvector:
    direction changes            direction unchanged, only scaled
    
         *  (after)                  ------->  (after, same line)
        /                                  
       /  (before)                    ------>  (before)
      *                              
      
    "Normal" vector               Eigenvector v
    gets rotated/sheared          Av = λv (same line, scaled by λ)
```

---

## 2. Definitions

- **Eigenvector v:** A non-zero vector that, when a linear transformation is applied, only changes in **scale** (not direction). So Av is parallel to v.

- **Eigenvalue λ:** The scalar that says how much the eigenvector is stretched or compressed: Av = λv.

**Equation:** Av = λv

- Every square matrix has eigenvectors (over the complex numbers). A 2×2 matrix has 2 eigenvalues (counting multiplicity), a 3×3 has 3, etc.

---

## 3. How to Find Eigenvalues

Start from **Av = λv**:
- Av - λv = 0
- (A - λI)v = 0

For **non-trivial** solutions (v ≠ 0), the matrix (A - λI) must be singular, so:
- **det(A - λI) = 0**

This is the **characteristic equation**. Solving it gives the eigenvalues.

**Worked example:** A = [[4, 2], [1, 3]]

1. A - λI = [[4-λ, 2], [1, 3-λ]].

2. det(A - λI) = (4-λ)(3-λ) - (2)(1) = 12 - 4λ - 3λ + λ² - 2 = λ² - 7λ + 10.

3. Set det = 0: λ² - 7λ + 10 = 0.

4. Factor (or quadratic formula): (λ - 5)(λ - 2) = 0 → **λ₁ = 5**, **λ₂ = 2**.

**Note:** For larger matrices, the characteristic equation is a polynomial of degree n, and we solve for its roots. Numerical methods (e.g. in NumPy) are used when n is large.

---

## 4. How to Find Eigenvectors

For each eigenvalue λ, solve **(A - λI)v = 0** for a non-zero v.

**For λ₁ = 5:**
- A - 5I = [[4-5, 2], [1, 3-5]] = [[-1, 2], [1, -2]].
- (A - 5I)v = 0 → -x + 2y = 0 and x - 2y = 0 (second is -1 times the first).
- From -x + 2y = 0 we get **x = 2y**.
- Choose y = 1 → x = 2. So **v₁ = [2, 1]** (or any non-zero multiple, e.g. [1, 0.5]).

**For λ₂ = 2:**
- A - 2I = [[4-2, 2], [1, 3-2]] = [[2, 2], [1, 1]].
- (A - 2I)v = 0 → 2x + 2y = 0 and x + y = 0.
- So **y = -x**.
- Choose x = 1 → y = -1. So **v₂ = [1, -1]** (or any non-zero multiple).

**Verification:**
- Av₁ = [[4,2],[1,3]][2,1]ᵀ = [10,5]ᵀ = 5[2,1]ᵀ  ✓
- Av₂ = [[4,2],[1,3]][1,-1]ᵀ = [2,-2]ᵀ = 2[1,-1]ᵀ  ✓

---

## 5. Geometric Interpretation

- **Eigenvectors** are the directions along which the transformation acts by **pure stretching or compression** (no rotation in that direction).
- **Eigenvalues** tell **how much** stretching or compression:
  - λ > 1: stretching.
  - 0 < λ < 1: compression.
  - λ < 0: direction reverses and scale changes.

**ASCII — transformation applied to an eigenvector:**

```
    v  ------->  Av = λv  (same direction, length × λ)
    
    |----|          |--------|
      v                 λv
```

---

## 6. Application: Principal Component Analysis (PCA)

PCA uses eigenvalues and eigenvectors to reduce dimensions.

**Steps:**
1. Compute the **covariance matrix** of the data.
2. Find its **eigenvalues** and **eigenvectors**.
3. Sort by eigenvalue (largest first).
4. Pick the **top k** eigenvectors (principal components).
5. **Project** the data onto these directions.

- **Eigenvalues** indicate how much **variance** each direction captures.
- **Eigenvectors with largest eigenvalues** = principal components (main directions of variation).

**Uses:** Reduce 500 features to 2–3 for visualization, remove noise, speed up training.

**ASCII — PCA idea:**
```
    Data (many dimensions)  →  Covariance matrix  →  Eigenvalues & eigenvectors
                                                           ↓
    Project onto top k eigenvectors  ←  Pick top k by eigenvalue
                                                           ↓
    Lower-dimensional data (e.g. 2D for plotting)
```

---

## 7. Key Takeaways

- Eigenvector: non-zero v with Av = λv (direction unchanged, scaled by λ).
- Eigenvalue: that scalar λ.
- Find λ from det(A - λI) = 0; find v from (A - λI)v = 0 for each λ.
- λ > 1 stretch, 0 < λ < 1 compress, λ < 0 reverse and scale.
- PCA uses eigenvectors (principal components) and eigenvalues (variance explained) for dimensionality reduction.

---

## 8. Python Quick Check

```python
import numpy as np

A = np.array([[4, 2], [1, 3]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print("Eigenvalues:", eigenvalues)   # [5., 2.]
print("Eigenvectors (columns):\n", eigenvectors)

# Check Av = λv for first eigenvector
v0 = eigenvectors[:, 0]
lam0 = eigenvalues[0]
print(np.allclose(A @ v0, lam0 * v0))  # True
```

---

**Navigation:** Previous → [08](08-inverse-functions-and-matrices.md) · Next → [10](10-equations-lines-planes-hyperplanes.md)
