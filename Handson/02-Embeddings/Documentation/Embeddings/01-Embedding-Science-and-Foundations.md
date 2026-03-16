# 01 — Embedding Science and Foundations

## Why This Document Matters

Chunking decides *what* gets represented.  
Embeddings decide *how* that meaning is represented for retrieval.

In RAG, this is the quality chain:

`source quality -> chunk quality -> embedding quality -> retrieval quality -> answer quality`

If embedding representation is weak, nearest-neighbor search returns "close-looking but wrong" chunks.

---

## What an Embedding Is

An embedding is a dense numeric vector that places text in a semantic space.

- Similar meaning should map to nearby vectors.
- Dissimilar meaning should map to distant vectors.
- Retrieval works by finding nearest vectors to the query vector.

Think of embeddings as coordinates for meaning.

---

## Core Concepts You Must Know

### 1) Vector Dimension

Dimension = number of values in the vector (for example 384, 768, 1024, 1536, 3072).

- Higher dimension can capture richer nuance.
- Higher dimension also increases storage and compute cost.
- Bigger is not automatically better; benchmark on your query set.

### 2) Context Length (Input Token Limit)

Embedding models have max input tokens. Exceeding limits can truncate input or fail.

- Truncation silently removes tail context in some pipelines.
- Always track `token_count` in metadata before embedding.

### 3) Similarity Metric

A metric defines "closeness":

- cosine similarity
- dot product (inner product)
- Euclidean distance (L2)

Choosing metric incorrectly can hurt ranking quality.

### 4) Normalization

Normalization scales vector magnitude to 1 (unit vectors).

- With normalized vectors, cosine and dot become equivalent for ranking.
- Without normalization, magnitude influences dot product scores.

This single detail explains most cosine vs dot confusion.

---

## Cosine vs Dot Product vs L2 (Deep Practical Guide)

## Cosine Similarity

Formula:

`cos(a, b) = (a · b) / (||a|| ||b||)`

Interpretation:

- Measures angle alignment, not vector length.
- Focuses on directional similarity (semantic direction).

When to use:

- Default for most text retrieval.
- Best when vector magnitude should not affect relevance.
- Safe for mixed chunk lengths.

Pros:

- Stable semantic ranking
- Robust across varying vector norms

Cons:

- Requires normalization conceptually (or implicit handling by engine)

## Dot Product (Inner Product)

Formula:

`dot(a, b) = a · b`

Interpretation:

- Combines direction + magnitude.
- Large norms can increase score even when angles are similar.

When to use:

- If your pipeline/model is explicitly designed for inner-product retrieval.
- If vectors are normalized (then dot ~= cosine ranking).

Pros:

- Efficient in many ANN implementations
- Great when normalized and engine optimized for IP

Cons:

- Without normalization, magnitude can bias ranking

## Euclidean Distance (L2)

Formula:

`L2(a, b) = ||a - b||`

Interpretation:

- Measures geometric distance between points.

When to use:

- If your index/store is configured for L2 and model workflow expects it.
- Works well when vector scale behavior is consistent.

Pros:

- Simple geometric interpretation

Cons:

- Scale-sensitive; not always ideal for text semantics unless setup is aligned

---

## Which Metric Is "Best"?

There is no universal best metric. Best depends on:

1. How the embedding model was trained
2. Whether vectors are normalized
3. What metric your vector store/index is optimized for
4. Your benchmark results (Recall@k/MRR/nDCG)

Practical default:

- **Use cosine for text retrieval unless model/store docs strongly recommend otherwise.**

---

## "Which Model Uses Which Metric?" (What Actually Matters)

Important clarification:  
Most embedding models output vectors only. The retrieval metric is usually applied by your vector store/retriever configuration.

Use this rule table:

| Scenario | Recommended Metric | Why |
|---|---|---|
| Vectors normalized (or normalized at index time) | Cosine or Dot | Equivalent ranking behavior |
| Vectors not normalized, text retrieval | Cosine (or normalize first) | Avoid norm bias |
| Engine/index optimized for IP and normalized vectors | Dot (IP) | Fast and correct |
| Engine configured only with L2 | L2 (or normalize first then L2) | Keep store + pipeline consistent |

If unsure: normalize vectors and use cosine/IP consistently.

---

## Why Magnitude Can Mislead Dot Product

Suppose two chunks point in similar direction, but one has larger norm because of training/data artifacts.  
Dot product can rank it higher because norm is larger, not because meaning is closer.

This is why many text systems either:

- use cosine directly, or
- normalize vectors then use dot product.

---

## ANN Index and Metric Compatibility

Metric choice is not theory only; it affects indexing.

Common examples:

- FAISS: `IndexFlatIP` (dot), `IndexFlatL2` (L2), HNSW variants
- HNSW-based stores: often support cosine/L2/IP
- Managed vector DBs: expose metric at collection/index creation time

Rule:

- Pick metric once per index/collection.
- Re-index if changing metric strategy significantly.

---

## Embedding Quality Failure Modes

1. **Semantic miss**: same meaning, different wording not matched  
2. **Noise dominance**: boilerplate/headers overwhelm signal  
3. **Truncation loss**: chunk tail removed before embedding  
4. **Domain mismatch**: model not suited for corpus terminology  
5. **Language mismatch**: multilingual query/doc gap  
6. **Metric mismatch**: model/store metric combo misconfigured  
7. **Version drift**: mixed model versions in one index

---

## Practical Baseline Setup (Recommended)

Start with this baseline before advanced tuning:

1. Clean chunks (remove extraction noise, preserve key structure)
2. Track `token_count`, `chunk_id`, `source`, `doc_type`
3. Use one strong baseline embedding model
4. Normalize vectors (if your chosen strategy expects it)
5. Use cosine (or equivalent normalized IP)
6. Benchmark on real production-like queries
7. Version everything (`model_version`, `preprocessing_version`, `index_version`)

---

## Significance for RAG Retrieval

Why this matters for answer quality:

- Better embedding geometry -> better top-k candidate set
- Better candidate set -> less hallucination and fewer missed facts
- Correct metric + normalization -> stable ranking behavior

If chunking is "document segmentation science," embeddings are "retrieval representation science."  
Both must be tuned together.

---

## Quick Decision Checklist

Before generating embeddings, answer these:

- Did I validate token limits for this model?
- Are vectors normalized or not?
- Is metric aligned with normalization and index config?
- Do I know embedding dimension and index dimension match?
- Do I have a benchmark query set ready?
- Can I reproduce results with versions and manifests?

If any answer is "no", fix that first.
