# 08 — Inverse Functions and Matrices

**Source:** Math Foundation Bootcamp — Krish Naik (Udemy).

---

## 1. Inverse Functions

**Definition:** The inverse of a function reverses the effect of the original function.

- If f maps x → y, then f⁻¹ maps y → x.
- **Notation:** f: X → Y, then f⁻¹: Y → X.

**Conditions for inverse:**
- f⁻¹(f(x)) = x   (inverse undoes the function)
- f(f⁻¹(y)) = y   (function undoes the inverse)

**ASCII diagram — Set X and Set Y with f and f⁻¹:**

```
    Set X                    Set Y
    -----                    -----
      x  ---- f -------->    y
      ^                      |
      |                      |
      +------ f⁻¹ -----------+
      
    f:    x → y
    f⁻¹:  y → x
```

**Example: f(x) = 2x + 3**

1. Solve for x in terms of y:
   - y = 2x + 3
   - y - 3 = 2x
   - x = (y - 3) / 2

2. So the inverse is: **f⁻¹(y) = (y - 3) / 2**

3. Verify:
   - f(2) = 2(2) + 3 = 7
   - f⁻¹(f(2)) = f⁻¹(7) = (7 - 3) / 2 = 4 / 2 = 2  ✓

**Bijective requirement:** A function has an inverse only if it is:
- **Injective (1-to-1):** different inputs always give different outputs.
- **Surjective (onto):** every element in the codomain is hit by some input.

Together: the function must be **bijective** for an inverse to exist.

---

## 2. Identity Function

**Definition:** The identity function maps every element to itself: **I(x) = x**.

**Identity matrix (2×2):**
```
    I₂ = [ 1  0 ]
         [ 0  1 ]
```

**Identity matrix (3×3):**
```
    I₃ = [ 1  0  0 ]
         [ 0  1  0 ]
         [ 0  0  1 ]
```

**Key property:** A × I = A (multiplying any matrix by the identity gives the same matrix).

**Properties of the identity:**
- Preserves every element (no change).
- Represents a linear transformation that does nothing.
- Is its own inverse: I⁻¹ = I.
- Structure: diagonal entries are 1, all other entries are 0.

---

## 3. Applications of Inverse Functions in Data Science

### 3.1 Standardization (Z-score Scaling)

**Forward transform:** z = (x - μ) / σ  
- Transforms data to mean = 0, standard deviation = 1.

**Inverse transform:** x = zσ + μ  
- Transforms back to the original scale.

**Why it's needed:** Features are often on different scales. We standardize to train the model, then use the inverse to convert predictions back to the original scale (e.g., real prices).

**Worked example:** rooms = [1, 2, 3, 4]
- Mean μ = 2.5, Std σ ≈ 1.29
- z₁ = (1 - 2.5) / 1.29 ≈ -1.16, z₂ ≈ -0.39, z₃ ≈ 0.39, z₄ ≈ 1.16
- Inverse: x = z(1.29) + 2.5 recovers [1, 2, 3, 4].

**ASCII pipeline:**
```
  Raw Data  →  Standardization  →  Train Model  →  Predict  →  Inverse Standardization  →  Real Prices
      x              z = (x-μ)/σ       (model)        ẑ              x̂ = ẑσ + μ                 x̂
```

### 3.2 Min-Max Normalization

**Forward:** z = (x - min) / (max - min)  — scales to [0, 1].

**Inverse:** x = z(max - min) + min.

Heavily used in image processing: pixel values [0, 255] → divide by 255 → [0, 1]. Inverse brings back to [0, 255] when needed.

### 3.3 Log Transformation

**Forward:** y = log(x) — often used to convert right-skewed data toward a normal distribution.

**Inverse:** x = eʸ.

Used for: financial data (income, sales), fixing skewed distributions for ML models.

### 3.4 Data Encryption/Decryption

- **Encrypt:** E(plaintext) → ciphertext.
- **Decrypt:** D(ciphertext) → plaintext — D is the inverse of E.

---

## 4. Inverse of a Matrix

### 4.1 Determinant

**Definition:** The determinant is a scalar value computed from a square matrix. It tells us whether the matrix is invertible.

**Geometric meaning (2×2):** The absolute value of the determinant is the area of the parallelogram formed by the two column vectors (or the two row vectors) after the transformation.

**Formula (2×2):**
```
    A = [ a  b ]     det(A) = ad - bc
        [ c  d ]
```

- If **det(A) = 0** → matrix is **NOT** invertible (singular). The columns (and rows) are linearly dependent; the transformation “collapses” space.
- If **det(A) ≠ 0** → matrix **IS** invertible. The transformation is one-to-one and onto.

### 4.2 Finding the Inverse (2×2)

**Formula:** A⁻¹ = (1 / det(A)) × (swap diagonal, negate off-diagonal)

For A = [[a,b],[c,d]]:
```
    A⁻¹ = (1/(ad - bc)) × [  d  -b ]
                          [ -c   a ]
```

**Full worked example:** A = [[4, 7], [2, 6]]

1. det(A) = (4)(6) - (7)(2) = 24 - 14 = **10**.

2. A⁻¹ = (1/10) × [[6, -7], [-2, 4]] = [[0.6, -0.7], [-0.2, 0.4]].

3. Verification: take x = [1, 1].
   - y = Ax = [4(1)+7(1), 2(1)+6(1)] = [11, 8].
   - A⁻¹y = [0.6(11)-0.7(8), -0.2(11)+0.4(8)] = [6.6-5.6, -2.2+3.2] = [1, 1]  ✓

---

## 5. Key Takeaways

- Inverse function f⁻¹ undoes f: f⁻¹(f(x)) = x and f(f⁻¹(y)) = y.
- A function needs to be bijective (1-to-1 and onto) to have an inverse.
- Identity matrix I has 1s on the diagonal, 0s elsewhere; A × I = A.
- Data science uses inverse transforms: standardization, min-max, log, and decryption.
- Matrix inverse exists only when det(A) ≠ 0; for 2×2, A⁻¹ = (1/det(A)) × [[d,-b],[-c,a]].

---

## 6. Python Quick Check

```python
import numpy as np

# Inverse function: f(x)=2x+3, so f⁻¹(y)=(y-3)/2
def f(x): return 2*x + 3
def finv(y): return (y - 3) / 2
print(finv(f(2)))  # 2.0

# Identity matrix
I = np.eye(2)
A = np.array([[4, 7], [2, 6]])
print((A @ I == A).all())  # True

# Matrix inverse
A_inv = np.linalg.inv(A)
x = np.array([1, 1])
y = A @ x
print(np.allclose(A_inv @ y, x))  # True
```

---

**Navigation:** Previous → [07](07-dot-product-and-projections.md) · Next → [09](09-eigenvalues-and-eigenvectors.md)
