# Element-wise and Scalar Multiplication

> **Source:** Math Foundation Bootcamp — Krish Naik (Udemy)  
> **Topic:** Remaining types of vector multiplication (Element-wise, Scalar)

---

## 1. Overview

There are **three main types of vector multiplication** in linear algebra and data science:

| Type | Brief description |
|------|-------------------|
| **Dot Product** | Two vectors → one scalar. Covered in [03-vector-operations](./03-vector-operations.md). |
| **Element-wise (Hadamard)** | Two vectors → new vector (same size). Multiply corresponding elements. |
| **Scalar Multiplication** | One scalar × one vector → new vector. Every element scaled by the same number. |

This note focuses on **element-wise multiplication** and **scalar multiplication**, with data-science applications (e-commerce, LSTMs, unit conversion, normalization).

---

## 2. Element-wise Multiplication (Hadamard Product)

### Definition

**Element-wise multiplication** (Hadamard product) multiplies **corresponding elements** of two vectors. The result is a **new vector of the same dimension** — not a scalar like the dot product.

**Notation:** a ⊙ b (circle with dot)

```
If   a = [a1, a2, a3]
and  b = [b1, b2, b3]

then a ⊙ b = [a1*b1,  a2*b2,  a3*b3]
```

### Worked Example

```
a = [1, 2, 3]
b = [3, 4, 5]

a ⊙ b = [1*3,  2*4,  3*5]
      = [3, 8, 15]
```

Result is a vector [3, 8, 15], not a single number.

### Application 1: Feature Engineering in E-commerce

**Scenario:** You have product prices and per-product discount rates. You want discounted prices.

- **Products vector (prices in $):** [1000, 500, 200]
- **Discounts vector (fraction):** [0.10, 0.20, 0.15]  (10%, 20%, 15% off)

**Step 1 — Element-wise multiply to get discount amounts:**

```
Discount amount = Prices ⊙ Discounts
                = [1000, 500, 200] ⊙ [0.10, 0.20, 0.15]
                = [100, 100, 30]
```

**Step 2 — Subtract from original to get final prices:**

```
Final price = Prices - Discount amount
            = [1000, 500, 200] - [100, 100, 30]
            = [900, 400, 170]
```

**ASCII table:**

```
+--------+--------+--------+--------+--------------+
| Product| Price  | Disc % | Disc $ | Final Price  |
+--------+--------+--------+--------+--------------+
|   P1   |  1000  |  0.10  |  100   |    900       |
|   P2   |   500  |  0.20  |  100   |    400       |
|   P3   |   200  |  0.15  |   30   |    170       |
+--------+--------+--------+--------+--------------+
         Prices ⊙ Discounts = [100, 100, 30]
```

### Application 2: Gate Mechanism in LSTM/GRU Neural Networks

In **LSTM** (Long Short-Term Memory) and **GRU** (Gated Recurrent Unit) networks, **gates** are vectors that decide what information to **keep** or **forget**. Gates are applied using **element-wise multiplication**.

- **Signals** (e.g. candidate values): [0.5, 0.6, 0.3]
- **Gate** (0 = block, 1 = pass): [0, 0, 1]

**Element-wise result:**

```
Signals ⊙ Gate = [0.5, 0.6, 0.3] ⊙ [0, 0, 1]
                = [0, 0, 0.3]
```

Only the third dimension passes; the first two are "forgotten" (zeroed out).

**Concept:**

- **Forget gate:** Element-wise multiply with previous cell state → decides what to forget (values near 0) or keep (values near 1).
- **Input gate:** Element-wise multiply with new candidate values → decides what new information to add.

```
LSTM-style gate (simplified):

  Previous state:  [h1, h2, h3]
  Gate:            [0,  0,  1 ]   (forget first two, keep third)
                       ⊙
  Result:          [0,  0,  h3]   (only third dimension remains)

  Same idea for "input gate": new info ⊙ gate = what actually gets added.
```

This is how RNNs (LSTM/GRU) **selectively remember or forget** information across time steps — all via element-wise multiplication with gate vectors.

---

## 3. Scalar Multiplication

### Definition

**Scalar multiplication** multiplies **every element** of a vector by a **single scalar** value. The result is a new vector of the same dimension; direction stays the same, length (magnitude) is scaled.

```
If c is a scalar and a = [a1, a2, a3]

then c * a = [c*a1, c*a2, c*a3]
```

### Example

```
c = 4
a = [3, 5, 7]

c * a = [4*3, 4*5, 4*7]
      = [12, 20, 28]
```

### Coordinate System Visualization

Scalar multiplication **scales the vector** — same direction, length multiplied by the scalar.

```
Vector [2, 2] scaled by 2 → [4, 4]

  y
  4│         • (4, 4)   ← 2 * [2, 2]
  3│       ╱
  2│     • (2, 2)       ← original
  1│   ╱
  0├─╱────────────────── x
   0  1  2  3  4  5

Same direction (45°), doubled length.
```

**ASCII diagram:**

```
Original:  [2, 2]  ------>  arrow from (0,0) to (2,2)
Scalar 2:  [4, 4]  =======> longer arrow from (0,0) to (4,4)
                           (same direction)
```

### Application 1: Unit Conversion

Convert heights from centimeters to meters by multiplying by 0.01.

- **Height in cm:** [161, 171, 180]
- **Scaling factor:** 0.01 (1 cm = 0.01 m)

```
Height in meters = 0.01 * [161, 171, 180]
                 = [1.61, 1.71, 1.80]
```

One scalar (0.01) applied to every element.

### Application 2: Normalization (Image Processing)

In image processing and deep learning, pixel values (0–255) are often **normalized** to [0, 1] by dividing by 255 (i.e. multiplying by 1/255).

- **Pixel values:** e.g. [0, 128, 255]
- **Scale factor:** 1/255

```
Normalized = (1/255) * [0, 128, 255]
           = [0, 0.502, 1.0]
```

**Why:** Smaller values (0–1) lead to **faster and more stable optimization** in neural networks; many activation functions and loss functions behave better in this range.

---

## 4. Comparison Table

| Operation        | Inputs           | Output   | Notation | Key Use                          |
|-----------------|------------------|----------|----------|-----------------------------------|
| Dot Product     | Two vectors      | Scalar   | a · b    | Similarity, attention, scores     |
| Element-wise    | Two vectors      | Vector   | a ⊙ b    | Discounts, gates, masking         |
| Scalar mult     | Scalar + vector  | Vector   | c * a    | Unit conversion, normalization    |

---

## 5. Key Takeaways

| Concept | One-Line Summary |
|--------|-------------------|
| Element-wise (Hadamard) | Multiply corresponding elements; result is a vector of same size |
| Notation ⊙ | Circle-dot denotes element-wise product |
| E-commerce use | Prices ⊙ discount rates = discount amounts; then subtract for final price |
| LSTM/GRU gates | Gate vector ⊙ signal = what to keep (1) or forget (0); core of RNN memory |
| Scalar multiplication | One number × every element; same direction, scaled length |
| Unit conversion | Multiply vector by conversion factor (e.g. 0.01 for cm → m) |
| Normalization | Multiply by 1/255 to scale pixels [0,255] → [0,1] for ML |

---

## 6. Python Quick Check

```python
import numpy as np

# --- Element-wise (Hadamard) multiplication ---
a = np.array([1, 2, 3])
b = np.array([3, 4, 5])
element_wise = a * b   # numpy * is element-wise for arrays
print("Element-wise a ⊙ b:", element_wise)   # [3, 8, 15]

# E-commerce example
prices = np.array([1000, 500, 200])
discounts = np.array([0.10, 0.20, 0.15])
discount_amount = prices * discounts
final_prices = prices - discount_amount
print("Discount amount:", discount_amount)   # [100, 100, 30]
print("Final prices:", final_prices)         # [900, 400, 170]

# LSTM-style gate
signals = np.array([0.5, 0.6, 0.3])
gate = np.array([0, 0, 1])
gated = signals * gate
print("Gated result:", gated)                # [0, 0, 0.3]

# --- Scalar multiplication ---
c = 4
v = np.array([3, 5, 7])
scaled = c * v
print("Scalar 4 * v:", scaled)               # [12, 20, 28]

# Unit conversion (cm to m)
height_cm = np.array([161, 171, 180])
height_m = 0.01 * height_cm
print("Height in m:", height_m)              # [1.61, 1.71, 1.80]

# Normalization (pixels 0-255 to 0-1)
pixels = np.array([0, 128, 255])
normalized = pixels / 255.0   # same as (1/255) * pixels
print("Normalized pixels:", normalized)      # [0, 0.502, 1.0]
```

---

**Previous:** [← Vector Operations (Dot Product, Cosine Similarity)](./03-vector-operations.md)  
**Next:** [Matrices & Matrix Operations →](./05-matrices-and-matrix-operations.md)
