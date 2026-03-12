# 05 — Matrices and Matrix Operations

**Source:** Math Foundation Bootcamp — Krish Naik (Udemy)  
**Topic:** Matrices, notation, data science applications, and core operations.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [04 — Vectors and Vector Operations](04-vectors-and-vector-operations.md) | [Month 01 — Linear Algebra](../Month-01-Linear-Algebra.md) | [06 — Determinants and Matrix Inverses](06-determinants-and-matrix-inverses.md) |

---

## 1. What is a Matrix?

**Definition:** A matrix is a **rectangular array of numbers** arranged in **rows** (horizontal) and **columns** (vertical). It is the natural extension of a vector to two dimensions.

**Notation:**
- We denote a matrix by a capital letter, e.g. **A**.
- Each element is written as **a_ij**, where:
  - **i** = row index (1 to m)
  - **j** = column index (1 to n)
- The **shape** (or size) of a matrix is written as **m × n** (read "m by n"): m rows and n columns.

**Generic matrix diagram:**

```
         col 1   col 2   col 3   ...   col n
         ─────   ─────   ─────         ─────
row 1  │  a₁₁     a₁₂     a₁₃    ...   a₁ₙ   │
row 2  │  a₂₁     a₂₂     a₂₃    ...   a₂ₙ   │
row 3  │  a₃₁     a₃₂     a₃₃    ...   a₃ₙ   │
  ...  │  ...     ...     ...    ...   ...   │
row m  │  aₘ₁     aₘ₂     aₘ₃    ...   aₘₙ   │
         ─────   ─────   ─────         ─────

Matrix A has shape m × n.
```

So: **a_ij** = element in row i and column j. The first subscript is always row, the second is column.

---

## 2. Matrices in Data Science

Matrices are not just abstract math — they are how we store and process data in ML and data science.

---

### 2.1 Data Representation

**Every dataset is a matrix.** Convention:
- **Rows** = records, samples, or observations (one per data point).
- **Columns** = features, variables, or attributes (one per dimension).

**Example: Student scores dataset**

Three students, three subjects (Math, Physics, Biology). As a table:

```
┌──────────┬───────┬─────────┬──────────┐
│ Student  │ Math  │ Physics │ Biology  │
├──────────┼───────┼─────────┼──────────┤
│ Student1 │  85   │   72    │   90     │
│ Student2 │  78   │   88    │   82     │
│ Student3 │  92   │   65    │   78     │
└──────────┴───────┴─────────┴──────────┘
```

**Equivalent matrix representation (3×3):**

```
        Math  Physics  Biology
       ─────  ───────  ───────
S1   │  85      72       90   │
S2   │  78      88       82   │
S3   │  92      65       78   │
       ─────  ───────  ───────

Shape: 3 × 3  (3 students, 3 features)
```

- **Shape:** 3 × 3 (3 rows = 3 samples, 3 columns = 3 features).
- For **10,000 records** with **50 features** → matrix of shape **10000 × 50**. Rows and columns scale with data size and number of features.

---

### 2.2 Images as Matrices

**Grayscale image:** A 2D matrix of pixel intensities.
- Each element = one pixel.
- Typical range: 0 (black) to 255 (white).

**Example: 3×3 grayscale image**

```
Pixel matrix (3 × 3):

     col0  col1  col2
     ────  ────  ────
row0  0    128   255   ← row of pixels
row1  64   192   128
row2  255  32    0

Interpretation: (0,0) is dark, (0,2) is bright, etc.
```

**RGB image:** Three matrices — one per channel (Red, Green, Blue).
- Each pixel has 3 values: (R, G, B).
- Stored as a 3D array: **height × width × 3**.
- For a 224×224 RGB image: 224 × 224 × 3 (e.g. for CNN input).

```
Conceptual view of one pixel at (i, j):

  R[i,j]   G[i,j]   B[i,j]
    │         │         │
    └─────────┴─────────┘
           one pixel
```

---

### 2.3 Confusion Matrix

In classification, we summarize predictions in a **confusion matrix** — a 2×2 matrix (for binary classification).

**Layout (rows = actual, columns = predicted):**

```
                    Predicted
                    ─────────────
                    No (0)  Yes (1)
              ┌─────┬───────┬───────┐
Actual  No(0) │ TN  │  FP   │       │  TN = True Negative   FP = False Positive
              ├─────┼───────┼───────┤
       Yes(1) │ FN  │  TP   │       │  FN = False Negative  TP = True Positive
              └─────┴───────┴───────┘
```

**Accuracy formula:**

```
Accuracy = (TP + TN) / (TP + FP + FN + TN)
```

So the confusion matrix is a small 2×2 matrix whose entries we use to compute accuracy, precision, recall, etc. For more detail (precision, recall, F1), see Phase-2 classification notes.

---

### 2.4 Neural Networks — Weight Matrices

In a fully connected layer, connections between layers are stored in a **weight matrix**.

**Example:** 2 inputs → 3 hidden neurons.

- **Weight matrix W:** 2 rows (inputs) × 3 columns (neurons) → shape **2 × 3**.

```
Input layer (2)     Weights W (2×3)      Hidden layer (3)
     x₁ ────────────── w₁₁ ─────────────→  h₁
      \               w₂₁                   
       \              w₁₂ ─────────────→  h₂
        \             w₂₂                   
         \            w₁₃ ─────────────→  h₃
      x₂ ───────────── w₂₃                   

Weight matrix W:
         neuron1  neuron2  neuron3
         ───────  ───────  ───────
input1  │  w₁₁     w₁₂     w₁₃   │
input2  │  w₂₁     w₂₂     w₂₃   │
         ───────  ───────  ───────
```

**Forward propagation (vector form):**
- Input vector **x** = [x₁, x₂].
- Bias vector **b** = [b₁, b₂, b₃].
- **output = Wᵀ × x + b**  (often written as Wᵀ x + b in code).
- So we use the **transpose** of W so that (2×3)ᵀ = 3×2, and (3×2)·(2×1) + (3×1) gives a 3×1 output.

Bias: one scalar per neuron: **[b₁, b₂, b₃]**.

---

### 2.5 NLP — Text as Matrices

In NLP, we turn text into **embeddings** (vectors). Multiple sentences become multiple vectors, which we **stack** into a matrix.

**Example:** Two reviews and their embedding vectors (dimension 3 for illustration):

- "food is bad"  → vector [0.1, 0.2, 0.3]
- "food is good" → vector [0.4, 0.5, 0.6]

**Input matrix (2 samples × 3 embedding dims):**

```
         dim1   dim2   dim3
        ─────  ─────  ─────
rev1   │ 0.1    0.2    0.3  │  "food is bad"
rev2   │ 0.4    0.5    0.6  │  "food is good"
        ─────  ─────  ─────

Shape: 2 × 3
```

**Labels (output):** sentiment 0 or 1 → **y = [0, 1]** (one label per row). So the model takes a **matrix** of embeddings and predicts a **vector** of labels.

---

### 2.6 Linear Regression as Matrix Operation

**Single feature:** y = m·x + c (one slope m, one intercept c).

**Multiple features:** We use a weight vector **M** and input vector **x**:
- **y = Mᵀ × x + c**
- M = [m₁, m₂], x = [x₁, x₂] → Mᵀ x = m₁·x₁ + m₂·x₂, then add c.

So linear regression is a **matrix (vector) multiplication** plus bias. For many samples, X is a matrix (rows = samples, columns = features) and we compute **X × M + c** (with proper shapes) to get predictions.

---

## 3. Matrix Operations

---

### 3.1 Matrix Addition and Subtraction

**Rule:** Both matrices must have the **same dimensions** (same m and n). We add or subtract **element by element**.

**Data science example:** Store A sales and Store B sales (same products, same weeks) → add to get total sales.

**Worked example:** 3×3 matrices A and B; find C = A + B.

```
     A              B              C = A + B
┌─────────┐   ┌─────────┐   ┌─────────┐
│ 1  2  3 │   │ 4  5  6 │   │ 5  7  9 │
│ 4  5  6 │ + │ 1  2  3 │ = │ 5  7  9 │
│ 7  8  9 │   │ 2  1  0 │   │ 9  9  9 │
└─────────┘   └─────────┘   └─────────┘

c_ij = a_ij + b_ij  for every i, j
```

**ASCII table for one element:**

```
  i  j   a_ij   b_ij   c_ij = a_ij + b_ij
  ───────────────────────────────────────
  1  1     1      4        5
  1  2     2      5        7
  ... (same for all 9 elements)
```

Subtraction is the same idea: **D = A − B** with d_ij = a_ij − b_ij.

---

### 3.2 Scalar Matrix Multiplication

Multiply **every element** of the matrix by a single number (scalar).

**Example 1 — 5% inflation on product prices:** Multiply all prices by **1.05**.

```
Prices (3×3):          After 5% inflation (× 1.05):
┌─────────────┐        ┌─────────────┐
│ 100  200  50│        │ 105  210  52.5│
│ 150  300  75│   →    │ 157.5 315 78.75│
│ 80   120  40│        │ 84  126  42  │
└─────────────┘        └─────────────┘
```

**Example 2 — 6% salary adjustment:** Multiply salary matrix by **1.06**.

```
Original salaries  × 1.06  =  Adjusted salaries
     (3×3)                        (3×3)
```

So: **B = k · A** means b_ij = k · a_ij for every i, j. Shape of B is the same as A.

---

### 3.3 Matrix Multiplication (Dot Product)

**Rule:** For **A × B** to be defined:
- **Columns of A** must equal **rows of B**.
- If A is **m × n** and B is **n × p**, then **A × B** has shape **m × p**.

**Process:** The (i, j) entry of the product is the **dot product of row i of A** with **column j of B**. So we often need the **transpose** of one matrix so that “rows of first” match “columns of second” in length.

**Worked example:**

- **A** = 2×3, **B** = 3×2 (so A×B is 2×2). We use B as 3×2 so that (2×3)·(3×2) = 2×2.

```
A (2×3):                    B (3×2):
┌─────────────┐             ┌───────┐
│ 1   2   3   │             │ 7   8 │
│ 4   5   6   │             │ 9  10 │
└─────────────┘             │11  12 │
                            └───────┘

C = A × B  (2×2)
```

**Step-by-step calculation:**

- **C₁₁** = row1(A) · col1(B) = 1·7 + 2·9 + 3·11 = 7 + 18 + 33 = **58**
- **C₁₂** = row1(A) · col2(B) = 1·8 + 2·10 + 3·12 = 8 + 20 + 36 = **64**
- **C₂₁** = row2(A) · col1(B) = 4·7 + 5·9 + 6·11 = 28 + 45 + 66 = **139**
- **C₂₂** = row2(A) · col2(B) = 4·8 + 5·10 + 6·12 = 32 + 50 + 72 = **154**

**Result:**

```
C = A × B:
┌─────────────┐
│ 58   64     │
│ 139  154    │
└─────────────┘
```

**Notation reminder:** (C_ij) = sum over k of (a_ik · b_kj). So we “multiply row by column” for each position in the output.

---

### 3.4 Matrix Transpose

**Definition:** Swap rows and columns. The (i, j) entry of **Aᵀ** is the (j, i) entry of A.

**Notation:** **Aᵀ** (A transpose).

**Example:**

```
     A (3×2)                    Aᵀ (2×3)
┌───────────┐                 ┌─────────────┐
│ 1   4     │                 │ 1   2   3   │
│ 2   5     │      →          │ 4   5   6   │
│ 3   6     │                 └─────────────┘
└───────────┘

Row 1 of A  becomes  Column 1 of Aᵀ
Column 1 of A  becomes  Row 1 of Aᵀ
```

Transpose is used constantly in:
- **Neural networks:** Wᵀ × x for forward pass.
- **Linear regression:** (Xᵀ X) and Xᵀ y in the normal equation.

---

## 4. Quick Reference — Matrix Rules

| Operation              | Dimension rule                    | Result dimension |
|------------------------|-----------------------------------|------------------|
| Addition A + B         | A and B same shape m×n            | m × n            |
| Subtraction A − B      | A and B same shape m×n            | m × n            |
| Scalar mult. k·A       | A is m×n, k scalar                | m × n            |
| Matrix mult. A × B     | A: m×n, B: n×p (n must match)     | m × p            |
| Transpose Aᵀ           | A is m×n                          | n × m            |

**Memory aid:** For A × B, the “inner” dimensions (n) must match; the “outer” dimensions (m and p) give the result size m×p.

---

## 5. Key Takeaways

| # | Takeaway |
|---|----------|
| 1 | A matrix is a rectangular array of numbers with shape m × n (rows × columns). |
| 2 | In data science, rows = samples, columns = features; every tabular dataset is a matrix. |
| 3 | Images are matrices (grayscale: 2D; RGB: height × width × 3). |
| 4 | Confusion matrix (2×2) summarizes classification results; accuracy = (TP+TN)/total. |
| 5 | Neural network layers use weight matrices; forward pass uses Wᵀ × x + b. |
| 6 | In NLP, sentences as embeddings are rows of an input matrix. |
| 7 | Linear regression with many features is y = Mᵀ × x + c (matrix/vector multiplication). |
| 8 | Addition/subtraction: same shape, element-wise. |
| 9 | Matrix multiplication: (m×n)·(n×p) = m×p; (i,j) entry = dot product of row i of first with column j of second. |
|10 | Transpose swaps rows and columns; used in neural nets and regression. |

---

## 6. Python Quick Check with NumPy

Use NumPy to create matrices and perform the operations above. Check shapes to match the rules.

```python
import numpy as np

# 1. Create matrices
A = np.array([[1, 2, 3],
              [4, 5, 6]])          # 2×3
B = np.array([[7, 8],
              [9, 10],
              [11, 12]])           # 3×2

# 2. Shape
print("Shape of A:", A.shape)      # (2, 3)
print("Shape of B:", B.shape)     # (3, 2)

# 3. Transpose
print("A transpose:\n", A.T)      # 3×2

# 4. Matrix multiplication (dot product)
C = np.dot(A, B)                   # or A @ B
print("A × B (2×2):\n", C)        # [[58, 64], [139, 154]]

# 5. Element-wise addition (same shape)
X = np.array([[1, 2], [3, 4]])
Y = np.array([[5, 6], [7, 8]])
print("X + Y:\n", X + Y)

# 6. Scalar multiplication
print("2 * X:\n", 2 * X)

# 7. Dataset example: 3 students, 3 subjects
scores = np.array([[85, 72, 90],
                   [78, 88, 82],
                   [92, 65, 78]])
print("Scores shape:", scores.shape)   # (3, 3)
```

Run this in a Python environment with NumPy installed to verify dimensions and numerical results.

---

**End of notes.** Next: [06 — Determinants and Matrix Inverses](06-determinants-and-matrix-inverses.md).
