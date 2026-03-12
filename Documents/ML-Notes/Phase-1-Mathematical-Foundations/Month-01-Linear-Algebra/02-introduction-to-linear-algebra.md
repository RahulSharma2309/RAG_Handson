# Introduction to Linear Algebra — What, Why, and Where

> **Source:** Math Foundation Bootcamp — Krish Naik (Udemy)  
> **Lecture:** Introduction to Linear Algebra + Scalars and Vectors

---

## 1. What is Linear Algebra?

Linear algebra is a branch of mathematics that focuses on the study of:

- **Vectors** — ordered lists of numbers
- **Vector spaces** (also called linear spaces)
- **Linear transformations** — functions that map vectors to vectors
- **Systems of linear equations**

It provides a framework for understanding the properties and operations of mathematical objects that can be represented using **matrices** and **vectors**.

> **Bottom line:** Linear algebra is the foundational math behind ML, deep learning, NLP, and computer vision. Every model you build — from linear regression to GPT — runs on matrix and vector operations under the hood.

---

## 2. Core Concepts We Will Learn

| Concept | What It Is | Where It Shows Up in ML/AI |
|---------|-----------|---------------------------|
| **Scalars** | A single number (no direction) | Bias terms, learning rate, loss value |
| **Vectors** | An ordered list of numbers | Feature vectors, word embeddings, data points |
| **Matrices** | A 2D array of numbers | Weight matrices in neural networks, datasets |
| **Matrix operations** | Add, multiply, transpose, invert | Forward propagation, solving equations |
| **Linear transformations** | Functions that preserve vector addition and scalar multiplication | PCA (dimensionality reduction) |
| **Eigenvalues & Eigenvectors** | Special scalar-vector pairs of a matrix | PCA, spectral clustering, stability analysis |

---

## 3. Why Linear Algebra Matters for Data Science

### 3.1 Data Representation and Manipulation

Every dataset is a collection of vectors. Every row is a vector. Every feature column is a dimension.

**Example — House Price Prediction:**

```
Dataset:
┌──────────────┬──────────────┬────────────┬────────────┐
│ Area (sq ft) │ Num Rooms    │ Location   │ Price (₹)  │  ← Output
├──────────────┼──────────────┼────────────┼────────────┤
│ 1200         │ 2            │ Bangalore  │ 45,00,000  │
│ 1800         │ 3            │ Mumbai     │ 95,00,000  │
│ 900          │ 1            │ Pune       │ 22,00,000  │
└──────────────┴──────────────┴────────────┴────────────┘

Each row is a vector:
  Row 1 → [1200, 2, Bangalore_encoded, 4500000]
  Row 2 → [1800, 3, Mumbai_encoded, 9500000]
```

The model does not understand "area" or "rooms" — it only sees **numbers in vectors** and learns the **relationships between those numbers**.

**Key insight:** When we say the model "quantifies the relationship" between features, we mean it computes things like **covariance** and **correlation** (covered in statistics) through vector and matrix operations.

### 3.2 Dimensions = Features

| Number of Features | Dimension | Can Humans Visualize? |
|---|---|---|
| 1 feature (e.g., area) | 1D — a point on a number line | Yes |
| 2 features (area + rooms) | 2D — a point on a plane | Yes |
| 3 features (area + rooms + location) | 3D — a point in space | Yes (barely) |
| 4+ features | 4D+ — a point in hyperspace | No — but linear algebra handles it perfectly |

> **This is the power of linear algebra:** It works seamlessly with **any number of dimensions** — even 500, 5000, or 50,000 features — using the same matrix and vector operations.

### 3.3 Dimensionality Reduction (PCA Preview)

When you have 500 features, linear algebra gives you techniques to **reduce them to 2 or 3 dimensions** so you can visualize and understand your data.

```
500 features ──[ PCA (uses eigenvalues + eigenvectors) ]──► 2 features

Now you can plot it on a 2D graph and see patterns!
```

This technique is called **Principal Component Analysis (PCA)** — we'll cover it in detail later.

---

## 4. Applications of Linear Algebra

### Application 1: Data Representation & Manipulation

- Every data point = a vector
- Every dataset = a matrix (rows × columns)
- Feature relationships = computed via matrix operations (covariance, correlation)

```
Data matrix (m rows × n features):

     Feature1  Feature2  Feature3
Row1 [  1200      2        0.8  ]     ← Each row is a vector in n-dimensional space
Row2 [  1800      3        0.6  ]
Row3 [   900      1        0.9  ]
```

### Application 2: Machine Learning & AI — Model Training

Training a model = solving equations and optimizing via matrix arithmetic.

**Example — Linear Regression:**

The equation of a straight line:

```
y = mx + c

where:
  y = predicted output (price)
  x = input feature (area)
  m = slope (coefficient) — how much y changes per unit change in x
  c = intercept — the baseline value when x = 0
```

Training finds the **best values of m and c** such that the line minimizes the error across all data points.

```
        Price (y)
          │        ╱ ← Best fit line (y = mx + c)
          │      ╱  •
          │    ╱ •
          │  ╱•    •
          │╱  •
          └──────────── Area (x)

  The "best fit" line minimizes the total distance
  between the line and all the data points (•).
```

This involves:
- **Matrix multiplication** — computing predictions
- **Linear equations** — the model itself is a linear equation
- **Optimization** — gradient descent minimizes the error

### Application 3: Neural Networks (Forward & Backward Propagation)

A neural network layer is literally a **matrix multiplication + bias addition**.

```
Neural Network: 2 inputs → 3 hidden neurons → 1 output

    Input           Hidden Layer        Output
   ┌────┐           ┌────┐
   │ F1 │──w1──────►│ H1 │
   │    │──w2──┐    │    │──────┐
   └────┘      │    └────┘      │
               │    ┌────┐      │    ┌────┐
               ├───►│ H2 │──────┼───►│ Out│
   ┌────┐      │    │    │      │    └────┘
   │ F2 │──w3──┘    └────┘      │
   │    │──w4──────►┌────┐      │
   │    │──w5──┐    │ H3 │──────┘
   └────┘      │    └────┘
               │
               └──► (w6)
```

**Forward propagation** = Input × Weights matrix:

```
Input vector: [F1, F2]        (1 × 2)

Weight matrix:                (2 × 3)
┌─────────────────┐
│  w1   w2   w3   │
│  w4   w5   w6   │
└─────────────────┘

Result = [F1, F2] × W = [H1, H2, H3]    ← Matrix multiplication!
```

**Backward propagation** updates the weights using the **chain rule** (calculus).

> **GPUs train neural networks fast because they can perform thousands of matrix multiplications in parallel.** This is why NVIDIA GPUs (H100, A100) are so important for training LLMs.

### Application 4: Computer Graphics & Image Processing

Images are matrices of pixel values.

```
RGB Image (4 × 4 pixels):

Red channel:     Green channel:    Blue channel:
┌───┬───┬───┬───┐  ┌───┬───┬───┬───┐  ┌───┬───┬───┬───┐
│255│128│ 0 │ 64│  │128│255│ 0 │ 32│  │ 64│ 64│255│128│
│...│...│...│...│  │...│...│...│...│  │...│...│...│...│
└───┴───┴───┴───┘  └───┴───┴───┴───┘  └───┴───┴───┴───┘

Each pixel value is between 0 and 255.
```

Operations like **scaling, rotation, translation, and color conversion** are all done using matrix operations.

### Application 5: Optimization

Finding the **minimum error** of a model = optimization.

```
Goal: Find m and c in y = mx + c that minimizes error

  Error
    │\
    │ \
    │  \
    │   \___________/    ← We want to find this minimum point
    │               \   /
    │                \_/
    └──────────────────── m (slope)

  This is done using Gradient Descent (covered in Calculus, Month 3).
```

---

## 5. Scalars

### Definition

A **scalar** is a single numerical value. It represents a magnitude or quantity and **has no direction**.

### Examples

| Example | Value | What It Represents |
|---------|-------|--------------------|
| Car speed | 45 km/h | Magnitude only — no direction specified |
| Temperature | 25°C | A single measurement |
| Count of records | 5 | A single number |
| Average age | 32.5 | A single computed value |
| Learning rate | 0.001 | A single hyperparameter in ML |

### Scalars in Data Science

| Where | Example |
|-------|---------|
| **Aggregations** | `count(records) = 5`, `mean(age) = 32.5`, `max(salary) = 150000` |
| **Model parameters** | The **intercept (c)** in `y = mx + c` is a scalar |
| **Loss value** | After computing error across all data points, you get one number: `loss = 0.342` |
| **Learning rate** | `lr = 0.001` — controls step size in gradient descent |

> **Key distinction:** The intercept `c` is a scalar (one number). The slope `m` in multivariate regression becomes a **vector** because it has one component per feature.

---

## 6. Vectors

### Definition (Physics vs Data Science)

| Context | Definition |
|---------|-----------|
| **Physics** | A numerical value with both **magnitude** and **direction** (e.g., velocity = 45 km/h heading East) |
| **Data Science** | An **ordered list of numbers** that can represent a point in space or a quantity with both magnitude and direction |

> In data science, we primarily think of vectors as **ordered lists of numbers** — each number corresponds to a feature/dimension.

### Examples

**Physics:** A car moving at 45 km/h towards the East.

```
  ─────────────────────►  East
        45 km/h
  (Magnitude = 45, Direction = East)
```

**Data Science:** A student's data as a vector.

```
Dataset:
┌─────┬───────────────┬─────────────┐
│ IQ  │ Study Hours   │ Pass/Fail   │
├─────┼───────────────┼─────────────┤
│  90 │       2       │ Fail (0)    │
│ 100 │       3       │ Pass (1)    │
│ 110 │       4       │ Pass (1)    │
└─────┴───────────────┴─────────────┘

Student 1 as a vector: [90, 2]      ← 2D vector (IQ, Study Hours)
Student 2 as a vector: [100, 3]     ← another point in the same 2D space
```

**Time-series:** A person's weight over months.

```
Weight vector = [70, 72, 75, 73]     ← 4D vector (Jan, Feb, Mar, Apr)
```

### Vectors in a Coordinate System

Every vector can be plotted as a point (and an arrow from the origin).

**2D Vector: a = [1, 2]**

```
  y
  4│
  3│
  2│         • (1, 2)  ← This is the point
  1│       ╱
  0├─────╱──────── x
   0  1  2  3  4

  Arrow goes from origin (0,0) to point (1,2).
  Direction = the angle of the arrow.
  Magnitude = length of the arrow = √(1² + 2²) = √5 ≈ 2.236
```

**3D Vector: c = [x, y, z]**

```
         z
         │   • (x, y, z)
         │  /
         │ /
         │/_________ y
        /
       /
      x
```

> **Key property:** As humans, we can visualize up to 3 dimensions. But linear algebra works identically in **any number of dimensions** — 4D, 500D, 50000D. The same operations (addition, dot product, magnitude) apply.

### Vector Notation and Dimensions

```
1D vector: [1200]                          ← just area
2D vector: [1200, 2]                       ← area + rooms
3D vector: [1200, 2, Bangalore_encoded]    ← area + rooms + location
4D vector: [1200, 2, Bangalore_encoded, 4500000]  ← + price
```

Each additional feature adds one dimension.

### Unit Vectors

A **unit vector** has a magnitude of exactly **1**. It points in a direction but has no length bias.

```
  y
  3│
  2│
  1│    ĵ (0,1)
  0├──î──────── x
   0  1  2  3

  î = unit vector along x-axis = [1, 0]
  ĵ = unit vector along y-axis = [0, 1]
```

Any vector can be expressed using unit vectors:

```
Vector [3, 3] = 3î + 3ĵ

Meaning: move 3 units along x-axis + 3 units along y-axis.
```

### Vectors in Classification (Visual Example)

When we plot data points (vectors) in a coordinate system, a classifier finds a **boundary** to separate classes.

```
  Study Hours
      │
    5 │         ○  ○         ○ = Pass
    4 │      ○  ○  ○         × = Fail
    3 │    ×  ○  ○
    2 │  ×  ×  ╱─────── Decision boundary (y = mx + c)
    1 │  ×  ╱×
    0 ├──╱────────── IQ
      80  90  100  110

  Points ABOVE the line → Pass
  Points BELOW the line → Fail
  
  A new student at (95, 3) → falls above → Predicted: Pass
```

This is the geometric intuition behind **logistic regression** and **SVM** — they find the best boundary line (or hyperplane in higher dimensions).

### Real-World Example: Gaming (GTA)

Vectors are everywhere in game physics:

```
  Lamborghini → [200 km/h, East]     ← velocity vector
  Police car  → [100 km/h, North]    ← velocity vector

  When they collide, the resulting impact vector determines:
  - How the car flips
  - What direction debris flies
  - The explosion animation

  All computed from vector operations!
```

Boat riding through waves — the wave vector determines how much the boat bounces, depending on the relative direction of the boat's velocity vector vs. the wave's direction vector.

---

## 7. Key Takeaways

| Concept | One-Line Summary |
|---------|-----------------|
| **Linear algebra** | The math of vectors and matrices — the language ML models speak |
| **Scalar** | A single number with no direction (e.g., loss = 0.34) |
| **Vector** | An ordered list of numbers representing a point in n-dimensional space |
| **Dimension** | Each feature in your data adds one dimension to the vector |
| **Unit vector** | A vector of length 1 pointing in a specific direction |
| **Data = Vectors** | Every row in a dataset is a vector; every dataset is a matrix |
| **Model training** | Matrix multiplication + linear equations + optimization |
| **PCA** | Uses eigenvalues/eigenvectors to reduce dimensions |
| **GPU acceleration** | Matrix multiplications run in parallel on GPU cores |

---

**Next:** [Vector Operations — Addition, Dot Product & Cosine Similarity →](./03-vector-operations.md)
