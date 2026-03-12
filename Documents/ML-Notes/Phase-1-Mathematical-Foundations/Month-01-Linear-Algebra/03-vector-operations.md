# Vector Operations — Addition, Dot Product & Cosine Similarity

> **Source:** Math Foundation Bootcamp — Krish Naik (Udemy)  
> **Lectures:** Addition of Two Vectors + Multiplication of Vectors (Dot Product)

---

## 1. Overview of Vector Operations

There are several mathematical operations we perform on vectors in data science:

| Operation | Inputs | Output | Used In |
|-----------|--------|--------|---------|
| **Vector Addition** | Two vectors | A new vector | Feature engineering, NLP embeddings, image processing |
| **Dot Product** (inner product) | Two vectors | A scalar | Cosine similarity, attention mechanism, neural networks |
| **Element-wise Multiplication** | Two vectors | A new vector | Feature weighting, masking |
| **Scalar Multiplication** | A scalar + a vector | A new vector | Scaling, learning rate application |

This document covers **addition** and **dot product** in depth with data science applications.

---

## 2. Vector Addition

### Definition

Adding two vectors means adding their **corresponding components**.

```
If   a = [a₁, a₂, a₃]
and  b = [b₁, b₂, b₃]

then a + b = [a₁ + b₁,  a₂ + b₂,  a₃ + b₃]
```

### Worked Example

```
p₁ = [-4, 3]
p₂ = [ 5, 3]

p₁ + p₂ = [-4 + 5,  3 + 3] = [1, 6]
```

### Visualizing in a Coordinate System

Vector addition is like **traversing from one vector's endpoint in the direction of the second vector**.

```
  y
  9│
  8│
  7│
  6│                    • (1, 6)  ← Result of p₁ + p₂
  5│                  ╱
  4│                ╱  (add p₂ from the tip of p₁)
  3│  • (-4, 3)  ╱─ ─ ─ ─ ─ ─ ─ • (5, 3)
  2│   ╲       ╱
  1│    ╲    ╱
  0├─────╲─╱────────────────── x
  -5 -4 -3 -2 -1  0  1  2  3  4  5
```

**How to read this geometrically:**

1. Start at the origin. Go to p₁ = (-4, 3).
2. From that point, move by p₂ = (5, 3): move 5 units right on x-axis, 3 units up on y-axis.
3. You arrive at (1, 6) — the result vector.

> **Intuition:** Vector addition = "follow the first path, then follow the second path." The result is where you end up.

### Generalizing to Any Dimension

```
3D Example:
  a = [x₁, y₁, z₁]
  b = [x₂, y₂, z₂]

  a + b = [x₁ + x₂,  y₁ + y₂,  z₁ + z₂]
```

Works the same for 4D, 100D, 5000D — just add corresponding components.

### Another Example (Negative Vectors)

```
a = [-2, -2]
b = [-1, -1]

a + b = [-2 + (-1), -2 + (-1)] = [-3, -3]
```

```
  y
  0├────────── x
 -1│ ╲
 -2│   • (-2,-2)
 -3│     ╲ • (-3,-3)  ← Result moves further into the negative quadrant
```

---

## 3. Applications of Vector Addition in Data Science

### 3.1 Sensor Data Aggregation

When multiple sensors measure the same environment, their readings are vectors that need to be combined.

```
Sensor 1 readings (3D): [3, 5, 7]    ← humidity, temp, pressure
Sensor 2 readings (3D): [2, 4, 6]

Combined reading = [3+2, 5+4, 7+6] = [5, 9, 13]
```

In real-world IoT/data engineering, you might have **100+ sensors** each producing **120-dimensional** vectors. Adding them gives an aggregated view — this is a core **feature engineering** task.

### 3.2 NLP — Word Embeddings

In Natural Language Processing, words are converted to numerical vectors (called **word embeddings**). These vectors capture meaning.

```
"data"    → [0.2, 0.1, 0.4]
"science" → [0.3, 0.7, 0.2]

"data science" (combined meaning) → [0.2+0.3, 0.1+0.7, 0.4+0.2]
                                   = [0.5, 0.8, 0.6]
```

The resulting vector **captures the combined semantic meaning** of "data science."

Common word embedding techniques:

| Technique | Description |
|-----------|-------------|
| **One-Hot Encoding** | Binary vector — only one position is 1 (sparse, loses meaning) |
| **Bag of Words** | Counts word frequencies (loses order) |
| **TF-IDF** | Weighted word frequency (considers document-level importance) |
| **Word2Vec** | Dense vectors from neural networks (captures semantic similarity) |
| **Transformer Embeddings** | Contextual vectors from models like BERT/GPT |

### 3.3 Image Processing — RGB to Grayscale

Each color channel of an image is a vector of pixel values. Converting RGB to grayscale = averaging the three channel vectors.

```
Red channel:   [255, 128,   0]
Green channel: [128, 255,   0]
Blue channel:  [ 64,  64, 255]

Step 1 — Add channels:
  R + G + B = [255+128+64, 128+255+64, 0+0+255]
            = [447, 447, 255]

Step 2 — Average (divide by 3):
  Grayscale = [149, 149, 85]
```

```
Original RGB pixel          Grayscale pixel
┌─────┬─────┬─────┐        ┌─────┐
│R=255│G=128│B= 64│  ───►  │ 149 │  (single intensity value)
└─────┴─────┴─────┘        └─────┘
```

---

## 4. Vector Multiplication — Dot Product

### 4.1 Definition

The **dot product** (also called **inner product**) of two vectors results in a **scalar**. It is calculated as the **sum of the products of corresponding components**.

```
If   a = [a₁, a₂]
and  b = [b₁, b₂]

then a · b = (a₁ × b₁) + (a₂ × b₂)    ← result is a single number (scalar)
```

### 4.2 Worked Example

```
a = [2, 3]
b = [4, 5]

a · b = (2 × 4) + (3 × 5)
      = 8 + 15
      = 23    ← scalar value
```

### 4.3 Transpose Notation

In many ML contexts (neural networks, linear algebra textbooks), the dot product is written using a **transpose**:

```
a · b = aᵀb

a = [2]    b = [4]
    [3]        [5]

aᵀ = [2, 3]    (row vector — transposed from column)

aᵀb = [2, 3] × [4] = (2×4) + (3×5) = 23
                [5]
```

> This transpose notation is exactly how neural network forward passes are written: **output = Wᵀx + b**

### 4.4 Geometric Interpretation

The dot product measures **how much one vector points in the direction of another**.

**Scenario 1: Vectors pointing in the SAME direction → Positive dot product**

```
  y
  4│
  3│
  2│    • b = (2, 2)
  1│  ╱
  0├╱────•────────── x
   0  1  2  3  4  5
              a = (5, 0)

  Project b onto a:
  
  b projected onto a → lands at x = 2 on the x-axis
  
  a · b = length(projection of b onto a) × length(a)
        = 2 × 5 = 10 ✓
        
  Verification: (5×2) + (0×2) = 10 ✓
```

**Scenario 2: Vectors pointing in OPPOSITE directions → Negative dot product**

```
  y
  4│
  3│
  2│    • b = (2, 2)
  1│  ╱
  0├╱──────────── x
  -5 -4 -3 -2 -1  0
   •
   a = (-5, 0)

  a · b = (-5×2) + (0×2) = -10
  
  Negative because a points LEFT while b's x-component points RIGHT.
```

**Scenario 3: Vectors are PERPENDICULAR → Dot product is ZERO**

```
  y
  2│  • b = (0, 2)
  1│  │
  0├──┼──────────── x
  -5 -4 -3 -2 -1  0
   •
   a = (-5, 0)

  a · b = (-5×0) + (0×2) = 0
  
  Zero because the projection of b onto a has zero length —
  they are at 90° to each other.
```

### 4.5 Summary of Dot Product Sign

| Dot Product | Angle Between Vectors | Meaning |
|-------------|----------------------|---------|
| **Positive** (> 0) | 0° to 90° | Vectors point in roughly the same direction |
| **Zero** (= 0) | Exactly 90° | Vectors are perpendicular (orthogonal) |
| **Negative** (< 0) | 90° to 180° | Vectors point in roughly opposite directions |

---

## 5. Cosine Similarity — The Key Application of Dot Product

### 5.1 Definition

**Cosine similarity** measures how similar two vectors are, regardless of their magnitude. It calculates the cosine of the angle between them.

```
                    a · b
cos(θ) = ─────────────────────
           ‖a‖  ×  ‖b‖

where:
  a · b   = dot product of vectors a and b
  ‖a‖     = magnitude (Euclidean norm) of vector a
  ‖b‖     = magnitude (Euclidean norm) of vector b
```

**Score range:**

```
-1 ◄───────────── 0 ──────────────► +1
Completely       Unrelated          Completely
Opposite                            Similar
(180°)           (90°)              (0°)
```

### 5.2 How to Calculate Magnitude (Euclidean Norm)

The magnitude of a vector = the **distance from the origin** to that point.

```
For a vector a = [a₁, a₂, ..., aₙ]:

‖a‖ = √(a₁² + a₂² + ... + aₙ²)
```

This is just the **Pythagorean theorem** extended to n dimensions.

**Example:**

```
a = [1, 2, 0, 3, 1]

‖a‖ = √(1² + 2² + 0² + 3² + 1²)
     = √(1 + 4 + 0 + 9 + 1)
     = √15
     ≈ 3.873
```

```
Origin (0,0,0,0,0)
    │
    │  distance = √15 ≈ 3.873
    │
    ▼
Point (1, 2, 0, 3, 1)
```

### 5.3 Full Worked Example — Movie Recommendation

**Problem:** Should we recommend Movie B to a user who watched Avengers?

Each movie is represented as a 5D vector based on genre scores:

```
                   Action  Comedy  Drama  Romance  Thriller
Avengers (a) =  [   1,      2,      0,     3,       1    ]
Movie B  (b) =  [   2,      0,      1,     1,       1    ]
```

**Step 1: Dot Product**

```
a · b = (1×2) + (2×0) + (0×1) + (3×1) + (1×1)
      = 2 + 0 + 0 + 3 + 1
      = 6
```

**Step 2: Magnitudes**

```
‖a‖ = √(1² + 2² + 0² + 3² + 1²)
     = √(1 + 4 + 0 + 9 + 1)
     = √15
     ≈ 3.873

‖b‖ = √(2² + 0² + 1² + 1² + 1²)
     = √(4 + 0 + 1 + 1 + 1)
     = √7
     ≈ 2.646
```

**Step 3: Cosine Similarity**

```
cos(θ) = 6 / (3.873 × 2.646)
       = 6 / 10.248
       ≈ 0.586
```

**Interpretation:**

```
Similarity score = 0.586 → 58.6% similar

┌─────────────────────────────────────────────────────────────┐
│  -1         0              0.586          1                 │
│   │─────────│────────────────│─────────────│                │
│   Opposite  Unrelated       ▲              Identical        │
│                              │                              │
│                         Avengers vs                         │
│                         Movie B                             │
│                                                             │
│   Verdict: Moderately similar → YES, recommend Movie B      │
└─────────────────────────────────────────────────────────────┘
```

### 5.4 Why Cosine Similarity, Not Just Dot Product?

The raw dot product is affected by **vector magnitude** (length). Two long vectors can have a high dot product even if they point in different directions.

Cosine similarity **normalizes by magnitude**, so it only measures the **angle** (direction), not the length.

```
Example where magnitude misleads:

a = [100, 200]     (very popular action movie — high raw scores)
b = [1, 2]         (indie action movie — low raw scores)

Dot product: (100×1) + (200×2) = 500   ← seems large

But cosine similarity:
  ‖a‖ = √(10000 + 40000) = √50000 ≈ 223.6
  ‖b‖ = √(1 + 4) = √5 ≈ 2.236

  cos(θ) = 500 / (223.6 × 2.236) = 500 / 500 = 1.0

They are PERFECTLY similar in direction — same genre profile,
just different magnitudes (popularity).
```

> **Cosine similarity is the standard similarity metric** in recommendation systems, semantic search, RAG systems, and anywhere you compare embeddings.

### 5.5 Where Cosine Similarity Is Used

| Application | What Vectors Represent | What Similarity Means |
|-------------|----------------------|----------------------|
| **Netflix/Spotify Recommendations** | Movie/song genre scores | Similar taste → recommend |
| **Semantic Search** | Text embeddings (from BERT/GPT) | Similar meaning → relevant result |
| **RAG (Retrieval-Augmented Generation)** | Document chunk embeddings | Similar to query → retrieve for LLM |
| **Plagiarism Detection** | Document embeddings | High similarity → potential plagiarism |
| **Customer Segmentation** | Customer behavior vectors | Similar vectors → same segment |
| **Duplicate Detection** | Product description embeddings | High similarity → likely duplicate |

---

## 6. Quick Reference — Formulas

### Vector Addition

```
[a₁, a₂, ..., aₙ] + [b₁, b₂, ..., bₙ] = [a₁+b₁, a₂+b₂, ..., aₙ+bₙ]
```

### Dot Product

```
a · b = a₁b₁ + a₂b₂ + ... + aₙbₙ = Σᵢ aᵢbᵢ
```

### Euclidean Norm (Magnitude)

```
‖a‖ = √(a₁² + a₂² + ... + aₙ²)
```

### Cosine Similarity

```
cos(θ) = (a · b) / (‖a‖ × ‖b‖)

Range: [-1, +1]
  +1 = identical direction
   0 = perpendicular (unrelated)
  -1 = opposite direction
```

---

## 7. Key Takeaways

| Concept | One-Line Summary |
|---------|-----------------|
| **Vector addition** | Add corresponding components — like following one path then another |
| **Dot product** | Multiply corresponding components and sum — gives a scalar |
| **Positive dot product** | Vectors point in roughly the same direction (angle < 90°) |
| **Zero dot product** | Vectors are perpendicular / orthogonal (angle = 90°) |
| **Negative dot product** | Vectors point in roughly opposite directions (angle > 90°) |
| **Euclidean norm** | Distance from origin — uses Pythagorean theorem in n dimensions |
| **Cosine similarity** | Normalized dot product — measures direction similarity, ignores magnitude |
| **Recommendation systems** | Compare movie/product vectors using cosine similarity |
| **RAG / Semantic search** | Compare query embedding to document embeddings using cosine similarity |
| **Transpose dot product** | aᵀb — the notation used in neural network math |

---

## 8. RAG (Retrieval-Augmented Generation) and Vector Databases — Real-World Cosine Similarity

Cosine similarity is the backbone of **RAG** and **vector databases**, which power many modern GenAI applications (chatbots, search, assistants). Here is how it fits in.

### How RAG Works (High-Level Flow)

1. **Book/PDF or any text** is split into chunks (paragraphs, sections).
2. Each chunk is **converted to a vector** (embedding) using an embedding model.
3. These vectors are **stored in a vector database**.
4. When a **user asks a question**, the query is **converted to a vector** (same embedding model).
5. The database performs a **cosine similarity search**: find the stored vectors most similar to the query vector.
6. The **most similar chunks** (their text) are **retrieved** and passed to an LLM.
7. The LLM **generates an answer** using that retrieved context (hence "retrieval-augmented" generation).

```
RAG Pipeline (ASCII):

  [Book/PDF]                    [User Query]
       |                              |
       v                              v
  Split into chunks            Convert to vector
       |                              |
       v                              |
  Convert each chunk  --------> [Embedding Model]
  to vector (embedding)              |
       |                              |
       v                              v
  [Vector Database]  <--cosine similarity search-->
  (store vectors)         (query vector vs stored vectors)
       |
       v
  Return most similar chunks (text)
       |
       v
  [LLM] uses chunks as context --> Generate answer
```

### Vector Databases

These systems store high-dimensional vectors and support fast **similarity search** (often using cosine similarity or related metrics):

| Database    | Notes |
|------------|--------|
| **FAISS**  | Facebook AI Similarity Search — library for similarity search, often used with embeddings |
| **Pinecone** | Managed vector DB, cloud-hosted |
| **Weaviate** | Open-source vector DB with GraphQL API |
| **Qdrant**  | Vector DB optimized for ML embeddings |
| **ChromaDB** | Lightweight, often used for prototyping and local RAG |

### Embedding Techniques

Text is turned into vectors (embeddings) using various methods:

| Technique | Description |
|-----------|-------------|
| **Bag of Words** | Count word frequencies → vector of counts (simple, no order) |
| **TF-IDF** | Weighted word frequency; down-weights common words (good for classic search) |
| **Word2Vec** | Dense vectors from neural nets; captures semantic similarity |
| **Transformer embeddings (BERT/GPT)** | Contextual embeddings; state-of-the-art for semantic similarity and RAG |

For RAG, **transformer-based embeddings** (e.g. sentence-BERT, OpenAI embeddings) are most common because they capture meaning and work well with cosine similarity.

### Why This Matters for GenAI

- **Chatbots & assistants:** RAG lets the model "look up" facts from your docs instead of relying only on training data — fewer hallucinations, more accurate answers.
- **Search:** Semantic search uses query and document embeddings + cosine similarity to find relevant content by meaning, not just keywords.
- **Enterprise apps:** Internal wikis, PDFs, and databases can be turned into queryable knowledge bases using the same pipeline: text → embeddings → vector DB → similarity search → LLM.

Cosine similarity is the operation that answers: *"Which stored vectors are closest in direction to my query vector?"* — and that is exactly what RAG and vector databases use to retrieve the right context for generation.

---

## 9. Python Quick Check

```python
import numpy as np

# Vector Addition
a = np.array([-4, 3])
b = np.array([5, 3])
print("Addition:", a + b)          # [1, 6]

# Dot Product
a = np.array([2, 3])
b = np.array([4, 5])
print("Dot Product:", np.dot(a, b))  # 23

# Cosine Similarity
from numpy.linalg import norm

avengers = np.array([1, 2, 0, 3, 1])
movie_b  = np.array([2, 0, 1, 1, 1])

cosine_sim = np.dot(avengers, movie_b) / (norm(avengers) * norm(movie_b))
print(f"Cosine Similarity: {cosine_sim:.3f}")  # 0.586

# Magnitude (Euclidean Norm)
print("‖avengers‖ =", norm(avengers))   # 3.873
print("‖movie_b‖  =", norm(movie_b))    # 2.646
```

---

**Previous:** [← Introduction to Linear Algebra](./02-introduction-to-linear-algebra.md)  
**Next:** [Element-wise and Scalar Multiplication →](./04-element-wise-and-scalar-multiplication.md)
