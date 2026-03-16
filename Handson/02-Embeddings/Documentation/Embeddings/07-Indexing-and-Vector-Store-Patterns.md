# 07 — Indexing and Vector Store Patterns

## What Is a Vector Index?

A vector index is a data structure that allows efficient nearest-neighbor search over a set of high-dimensional vectors.

When you embed 100,000 chunks and store them, you cannot brute-force compare your query vector against all 100,000 stored vectors at query time — that would be too slow.

An index organises vectors so that nearest neighbors can be found much faster, with some acceptable trade-off between speed and recall.

---

## Two Index Types You Must Understand

### Exact Search (Brute-Force)

Compare query vector against every stored vector. Returns the exact nearest neighbors.

- **Guarantee**: 100% recall — never misses the true nearest neighbors
- **Cost**: `O(n * d)` per query (n = number of vectors, d = dimension)
- **When to use**: small corpora (< 100K vectors), benchmarking, development, regression testing

`FAISS IndexFlatL2` and `IndexFlatIP` are exact search indexes.

### Approximate Nearest Neighbor (ANN)

Uses data structures like HNSW, IVF, or ANNOY to find approximate nearest neighbors faster.

- **Guarantee**: finds *most* true nearest neighbors — miss rate depends on configuration
- **Cost**: `O(log n)` or sub-linear per query
- **When to use**: production systems with large corpora and latency requirements

ANN is the default for most production vector stores.

---

## ANN Index Algorithms

### HNSW (Hierarchical Navigable Small World)

How it works:
- builds a multi-layer graph of vectors
- upper layers are sparse (long-range connections)
- lower layers are dense (close-range connections)
- search starts at top layer and navigates down

Key parameters:
- `M`: number of connections per node. Higher M → better recall, more memory
- `ef_construction`: effort at build time. Higher → better index quality, slower build
- `ef_search`: effort at query time. Higher → better recall, slower query

When to use:
- general-purpose production retrieval
- when you need high recall with fast query time
- when index build time is acceptable (HNSW builds slower than IVF)

### IVF (Inverted File Index)

How it works:
- clusters vectors into `nlist` cells using k-means
- at query time, searches only the nearest `nprobe` cells

Key parameters:
- `nlist`: number of clusters. Larger → more precise partitioning but more memory
- `nprobe`: how many clusters to search at query time. Higher → better recall, slower search

When to use:
- very large corpora (10M+ vectors) where HNSW memory is too large
- when build speed matters (IVF builds faster than HNSW)

### PQ (Product Quantization)

Compresses vectors for storage. Often combined with IVF (`IVFPQ`).

Trade-off: reduced memory at the cost of some recall accuracy.

When to use:
- memory is constrained
- recall loss is acceptable and validated by benchmark

---

## Choosing the Right Index

| Corpus Size | Recommended Index | Notes |
|---|---|---|
| < 50K vectors | `IndexFlatIP` / `IndexFlatL2` (exact) | Perfect for learning/dev |
| 50K – 5M vectors | HNSW | Good recall + fast queries |
| 5M – 100M vectors | IVF or HNSW with PQ | Memory-aware choice |
| > 100M vectors | IVF + PQ + sharding | Distributed architecture needed |

---

## Metric and Index Alignment (Critical)

The index algorithm must match your similarity metric.

Do not use `IndexFlatL2` if your model and workflow expect cosine similarity.  
Do not use `IndexFlatIP` if you have not normalized your vectors.

### FAISS Index Selection by Metric

| Metric | Normalized Vectors? | FAISS Index |
|---|---|---|
| Cosine | Yes (pre-normalize) | `IndexFlatIP` |
| Dot Product | Yes (if IP semantics) | `IndexFlatIP` |
| L2 / Euclidean | Not required | `IndexFlatL2` |

For cosine similarity with FAISS: normalize all vectors to unit length before inserting and before querying. Then `IndexFlatIP` gives correct cosine ranking.

```python
import numpy as np
import faiss

def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

# Normalize before add and search
index = faiss.IndexFlatIP(dim)
index.add(normalize(all_vectors))
scores, ids = index.search(normalize(query_vector), k=10)
```

---

## Index Namespace Design

A namespace (or collection) is a logical partition of your index.

### Why Use Namespaces

- isolate corpora: `ml_notes`, `fresh_harvest`, `rag_documents`
- isolate environments: `dev`, `staging`, `prod`
- isolate index versions: `v1`, `v2`

Without namespaces, a query about "auth service" might retrieve chunks from an unrelated project that also mentions authentication.

### Namespace Strategy

Recommended partitioning:

```
{corpus}_{environment}_{index_version}
e.g.
fresh_harvest_prod_v3
ml_notes_staging_v2
```

For managed vector stores (Pinecone, Weaviate, Qdrant): use their built-in namespace/collection concept.

For self-hosted FAISS: maintain a separate index file per namespace.

---

## Upsert Patterns

### Pattern 1: Full Reindex

Delete everything, re-embed everything, re-insert.

When to use:
- embedding model changed
- preprocessing version changed significantly
- schema/metadata structure changed

Cost: high. Run off-peak.

### Pattern 2: Incremental Upsert

Only update vectors for documents that changed.

Requirements:
- track `chunk_id` per vector
- detect which source documents changed (file hash or modification date)
- delete old vectors for changed documents, insert new ones

```python
# Pseudocode for incremental upsert
for doc in changed_documents:
    old_chunk_ids = get_chunk_ids_by_source(doc.path)
    delete_vectors(old_chunk_ids)
    new_chunks = chunk_document(doc)
    new_vectors = embed(new_chunks)
    insert_vectors(new_chunks, new_vectors)
```

When to use:
- frequently updated knowledge base (daily/weekly updates)
- large corpus where full reindex is expensive

### Pattern 3: Blue/Green Index

Build a new index version (green) while old (blue) serves production.

Steps:
1. Keep blue index active for all queries
2. Build green index in parallel
3. Benchmark green against gold query set
4. If green passes: switch traffic to green
5. Keep blue for 24-48 hours as rollback
6. Decommission blue after validation period

When to use:
- major model or schema upgrades
- zero-downtime requirement
- any change where rollback matters

---

## What to Store With Each Vector

Every vector in your index should be searchable and attributable.

Store alongside each vector:

```json
{
  "chunk_id": "fh_3f7a91bc22d1",
  "page_content": "The payment service handles all financial transactions...",
  "source": "PAYMENT_SERVICE.md",
  "doc_type": "technical_doc",
  "corpus": "fresh_harvest",
  "service": "payment-service",
  "version": "v2.3",
  "token_count": 183,
  "embedding_model": "text-embedding-3-small",
  "index_version": "idx_20260312",
  "preprocessing_version": "v1.2"
}
```

Many vector stores store this as a "payload" or "metadata" alongside the vector.

Do not store only the vector — without metadata, retrieved chunks cannot be cited or filtered.

---

## Validating an Index After Build

After any index operation (build or update), run these checks:

### Check 1: Vector Count Matches Expected Chunk Count

```python
expected = len(all_chunks)
actual = index.ntotal  # FAISS
assert actual == expected, f"Expected {expected}, got {actual}"
```

### Check 2: Dimension Consistency

All vectors must be the same dimension:

```python
assert all(v.shape[0] == DIM for v in all_vectors)
```

### Check 3: No Duplicate chunk_ids

```python
all_ids = [c.metadata["chunk_id"] for c in all_chunks]
assert len(all_ids) == len(set(all_ids)), "Duplicate chunk IDs found"
```

### Check 4: Smoke Test Queries

Run 3-5 known queries against the index and verify expected chunks are retrieved:

```python
for query, expected_source in smoke_tests:
    results = retrieve(query, k=5)
    sources = [r.metadata["source"] for r in results]
    assert expected_source in sources, f"Smoke test failed for: {query}"
```

---

## Production Monitoring

Track these metrics in production:

| Metric | Why It Matters |
|---|---|
| Query latency p50 / p95 / p99 | SLO tracking |
| Index size (vectors) | Capacity planning |
| Vectors added / updated per day | Growth rate |
| Failed embed count | Pipeline health |
| Smoke test pass rate | Index quality signal |
| Retrieval no-hit rate | Query-index mismatch |

A `no-hit rate > 5%` means queries are returning nothing useful — signal for re-evaluation.

---

## Common Indexing Mistakes

### Mistake 1: Mixing metric strategies in one index

Some vectors normalized, some not. Results are inconsistent and unexplainable.

### Mistake 2: No rollback capability

Model update degrades retrieval. Old index is gone. Cannot roll back.

### Mistake 3: Index = only vectors, no metadata

Cannot filter, cannot attribute, cannot debug.

### Mistake 4: Using exact search at scale

IndexFlatIP works for 10K vectors. At 10M vectors, query time is seconds.

### Mistake 5: No smoke tests after index build

Silent failures in chunking or embedding result in an empty or broken index. Without smoke tests, you discover this in production.

---

*Part of Handson Phase 2: Embeddings | March 2026*
