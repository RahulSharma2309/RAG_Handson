# 06 — Functions and Transformations

**Source:** Math Foundation Bootcamp — Krish Naik (Udemy). Comprehensive lecture notes.

---

## 1. Functions in Linear Algebra

**Definition:** A function maps elements from one set (the **domain**, Set X) to another set (the **codomain**, Set Y).

**Notation:** f: X → Y  
Meaning: f maps elements from X to Y.

If x is an element of X, then **f(x)** is the corresponding element in Y.

**Example (scalar):**  
f(x) = 2x + 3 maps a real number x to the real number 2x + 3.

- f(2) = 7 — maps 2 (real number) to 7 (real number)
- Domain: ℝ (reals), Codomain: ℝ

**Vector function example:**  
f([x, y, z]) = [x + y, 6z]

- Maps **ℝ³ → ℝ²** (3D space to 2D space!)
- f([1, 2, 3]) = [1 + 2, 6×3] = [3, 18]

ASCII diagram — 3D → 2D mapping:

```
    ℝ³ (3D)                    ℝ² (2D)
    --------                   --------
         z
         |
         |  • [1,2,3]          y
         | /                    |
        /|                      |   • [3, 18]
       / |                      |  /
      x--+--y                   --+--x
         |                      |
    input: [1, 2, 3]       output: [3, 18]
         |                      ^
         |    f([x,y,z])        |
         +----> = [x+y, 6z] ----+
```

This dimension-changing capability is key to **dimensionality reduction** in machine learning (e.g., PCA reduces many dimensions to fewer).

**Why it matters in ML:** When you have 100 features and want to compress to 10, you use a function from ℝ¹⁰⁰ → ℝ¹⁰. Each of the 10 new features is a linear combination of the original 100.

---

## 2. Vector Transformation

**Definition:** A **vector transformation** is an operation that maps vectors from one space to another, changing magnitude, direction, or both.

**Notation:** T: ℝⁿ → ℝᵐ  
(T takes vectors from n-dimensional space and outputs vectors in m-dimensional space.)

### Types of transformations (with ASCII visualizations)

**Scaling** — changes magnitude, keeps direction.

- v = [2, 3] scaled by 2 → [4, 6]
- Used in: data normalization, image resizing

```
    Before scaling          After scaling (×2)
    ----------------       ------------------
         y                      y
         |                      |
         |   • [2,3]            |     • [4,6]
         |  /                   |    /
         | /                    |   /
         |/                     |  /
    -----+------ x         -----+------ x
         |                      |
    same direction,         same direction,
    length × 2              longer vector
```

**Rotation** — turns vectors around the origin.

- [1, 0] rotated 90° counterclockwise → [0, 1]
- Used in: image processing, robotics, deep learning augmentation

```
    90° counterclockwise
    --------------------
         y                    y
         |                    |
         |     • [0,1]        |   • [1,0]
         |                    |
         |                    |
    -----+-------- x     -----+-------- x
         |                    |
    [1,0] → [0,1]        (before → after)
```

**Reflection** — flips across an axis.

- [3, 4] reflected across y-axis → [-3, 4]
- Element-wise: [3, 4] ⊙ [-1, 1] = [-3, 4]
- Used in: image mirroring, computer graphics

```
    Reflection across y-axis
    ------------------------
         y                    y
         |                    |
         |  • [-3,4]   • [3,4]|
         |      \       /     |
         |       \     /      |
    -----+--------+---+--- x
         |        |   |
         |     mirror line (y-axis)
```

**Combining transformations:** You can apply scaling, then rotation, then reflection. When all are linear, the combined effect is a single matrix multiplication (matrix product).

---

## 3. Linear Transformation

**Definition:** A transformation T is **linear** if it preserves vector addition and scalar multiplication.

Two required properties:

1. **Additivity:** T(u + v) = T(u) + T(v)
2. **Homogeneity:** T(cu) = c·T(u) for any scalar c

**Visual properties:** The origin stays fixed; straight lines remain straight lines (no bending).

### Full proof example: Reflection across y-axis

T(x) = Ax where A = [[-1, 0], [0, 1]]

So T([x₁, x₂]) = [-x₁, x₂].

**Prove additivity:**

- Let u = [u₁, u₂], v = [v₁, v₂].
- u + v = [u₁ + v₁, u₂ + v₂].
- T(u + v) = [-(u₁ + v₁), u₂ + v₂] = [-u₁ - v₁, u₂ + v₂].
- T(u) = [-u₁, u₂], T(v) = [-v₁, v₂].
- T(u) + T(v) = [-u₁ - v₁, u₂ + v₂].
- So T(u + v) = T(u) + T(v). ✓

**Prove homogeneity:**

- Let c be a scalar. cu = [cu₁, cu₂].
- T(cu) = [-cu₁, cu₂] = c[-u₁, u₂] = c·T(u). ✓

**Conclusion:** Reflection across the y-axis IS a linear transformation.

### Counter-example: Translation is NOT linear

T(x) = x + [1, 1] (translation by fixed vector [1, 1]).

**Show it FAILS additivity:**

- u = [2, 3], v = [4, -1].
- u + v = [6, 2].
- T(u + v) = [6, 2] + [1, 1] = [7, 3].
- T(u) = [2, 3] + [1, 1] = [3, 4].
- T(v) = [4, -1] + [1, 1] = [5, 0].
- T(u) + T(v) = [3, 4] + [5, 0] = [8, 4].
- [7, 3] ≠ [8, 4] → T(u + v) ≠ T(u) + T(v). ✗

So T fails additivity. It also fails homogeneity (e.g. T(2u) ≠ 2·T(u) because of the fixed [1,1] shift).

**Conclusion:** Translation is NOT a linear transformation.

**Why translation fails:** Moving the origin breaks “T(0) = 0”. For any linear T, T(0) must equal 0. Here T(0) = [1,1], so the origin is not fixed.

---

## 4. Visualization of Linear vs Non-Linear Transformations

**Linear:** Origin stays fixed; lines stay lines. (Credit: 3Blue1Brown.)

**1D examples:**

- T(x) = 2x — stretches the number line (every point moves twice as far from 0)
- T(x) = 0.5x — compresses the number line (points move halfway toward 0)
- T(x) = -3x — flips and stretches (negative side becomes positive and scaled)

**2D linear:** Grid lines stay parallel and evenly spaced.

```
    Linear (e.g. scaling/rotation)     Non-linear (e.g. curve)
    ------------------------------     ----------------------
    |     |     |     |                \   /   \   /
    |     |     |     |                 \ /     \ /
    +-----+-----+-----+       →          X       X
    |     |     |     |                 / \     / \
    |     |     |     |                /   \   /   \
    grid stays parallel               lines become curves
    and evenly spaced                 origin may move
```

**Non-linear:** Origin may move; lines can become curves.

```
    Before any T                After LINEAR T           After NON-LINEAR T
    -------------               ----------------         ------------------
    +---+---+---+               +---+---+---+             ~  ~  ~  ~
    |   |   |   |               |   |   |   |              \   \   \
    +---+---+---+       →       +---+---+---+       →       ~---+---~
    |   |   |   |               |   |   |   |                /   /   /
    +---+---+---+               +---+---+---+             ~  ~  ~  ~
    straight grid               straight grid             curved grid
```

---

## 5. Applications of Linear Transformation (10 key areas)

| # | Application | How Linear Transformation is Used |
|---|-------------|-----------------------------------|
| 1 | Dimensionality reduction (PCA) | Project data onto principal components; each component is a linear combination of original features. |
| 2 | Feature engineering | Build new features as linear combinations of existing ones (e.g. x₁ + x₂, 2x₁ - x₃). |
| 3 | Data preprocessing | Normalization and standardization are linear (scale + shift). |
| 4 | Neural networks | Forward propagation is matrix-vector products (linear); non-linearity comes from activation functions. |
| 5 | Image processing | CNN convolution filters apply linear operations (sum of element-wise products) on patches. |
| 6 | Signal processing | Filters and Fourier analysis rely on linearity (superposition). |
| 7 | Linear regression | Finding coefficients β such that Xβ ≈ y is solving a linear system in the column space of X. |
| 8 | Ridge/Lasso regression | Same as above with penalty; solution is still a linear function of the data. |
| 9 | Recommendation systems | Matrix factorization and latent factor models use linear structure in user-item matrices. |
| 10 | Computer graphics | Scaling, rotation, reflection (and composition of these) are linear; applied via matrices. |

**Note:** In neural networks, the linear part is the weight matrix; activation functions (ReLU, sigmoid) add non-linearity so the network can learn complex decision boundaries.

---

## 6. Key Takeaways

| Topic | Takeaway |
|-------|----------|
| Function f: X → Y | Maps each element of domain X to an element in codomain Y. |
| Vector functions | Can change dimension (e.g. ℝ³ → ℝ²); basis for dimensionality reduction. |
| Vector transformation | Maps vectors to vectors; can scale, rotate, reflect. |
| Linear transformation | Preserves addition and scalar multiplication; origin fixed, lines stay lines. |
| Additivity | T(u + v) = T(u) + T(v). |
| Homogeneity | T(cu) = c·T(u). |
| Matrix form | Every linear T: ℝⁿ → ℝᵐ can be written as T(x) = Ax for some matrix A. |
| Translation | T(x) = x + b is NOT linear (fails additivity/homogeneity). |
| Applications | PCA, feature engineering, preprocessing, neural nets, images, signals, regression, graphics. |

**Summary:** Functions map inputs to outputs; vector functions can change dimension. Linear transformations are those that preserve addition and scalar multiplication (and thus keep the origin fixed and lines straight). They are the backbone of many ML and graphics algorithms.

---

**Navigation:** [Previous → 05](05-dot-product-and-angle.md) | [Next → 07](07-vector-magnitude-and-projections.md)
