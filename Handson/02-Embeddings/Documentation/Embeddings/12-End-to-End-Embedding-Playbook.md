# 12 — End-to-End Embedding Playbook

## What This Playbook Is

This is the standard operating procedure for converting chunk artifacts into a validated, production-ready vector index.

Every step from loading chunks to promoting an index version is covered here.  
Follow this in order. Do not skip steps. Each step feeds the next.

---

## Overview: The Full Pipeline

```
CHUNK ARTIFACTS (JSONL)
        │
        ▼
Step 1: Load and Validate Inputs
        │
        ▼
Step 2: Preprocessing Pass
        │
        ▼
Step 3: Token Budget Validation
        │
        ▼
Step 4: Generate Embeddings (Batch + Retry)
        │
        ▼
Step 5: Validate Embedding Output
        │
        ▼
Step 6: Upsert to Vector Index
        │
        ▼
Step 7: Validate Index Integrity
        │
        ▼
Step 8: Smoke Tests
        │
        ▼
Step 9: Benchmark Evaluation
        │
        ▼
Step 10: Produce Manifest and Reports
        │
        ▼
Step 11: Promote Index Version (Gate)
```

---

## Step 1: Load and Validate Inputs

Load chunk artifacts from JSONL files. Validate every record before continuing.

### What to Validate

Required fields must be present:

```python
REQUIRED_FIELDS = {
    'page_content',
    'metadata.chunk_id',
    'metadata.source',
    'metadata.doc_type',
    'metadata.corpus',
    'metadata.token_count',
    'metadata.preprocessing_version',
}
```

Reject records with:
- empty `page_content`
- missing required metadata fields
- `page_content` under minimum length (e.g. 40 characters)

Write rejected records to a `validation_failures.jsonl` file. Do not fail silently.

### Output Artifacts

- `valid_chunks` — list ready for preprocessing
- `validation_failures.jsonl` — rejected records with reason

---

## Step 2: Preprocessing Pass

Apply your corpus-specific preprocessing rules.

Order:
1. Remove control characters
2. Fix ligatures (PDF)
3. Fix hyphenated line breaks (PDF)
4. Remove boilerplate (PDF headers/footers)
5. Normalize whitespace
6. Apply PII redaction (if required)
7. Apply field labelling (CSV/tabular content)
8. Re-validate minimum length after cleaning

Update `preprocessing_version` in metadata if not already set.

Reject any chunk that is empty or below minimum length after cleaning. Log to `preprocessing_rejections.jsonl`.

---

## Step 3: Token Budget Validation

Count tokens for every chunk using the tokenizer of your embedding model.

```python
for chunk in valid_chunks:
    chunk.metadata['token_count'] = count_tokens(
        chunk.page_content, model=EMBEDDING_MODEL
    )
    chunk.metadata['truncation_risk'] = (
        chunk.metadata['token_count'] > OPERATIONAL_TOKEN_LIMIT
    )
```

Chunks flagged `truncation_risk = True` must be handled before embedding:

Options per chunk profile:
- Split at sentence boundary to stay under limit
- Sub-chunk the overflow
- Reject and log (for compliance-sensitive content)

Produce a `token_budget_report.csv` with distribution summary:
- total chunks
- chunks under limit
- chunks over limit
- min/max/avg/p95 token counts per corpus

---

## Step 4: Generate Embeddings

Process chunks in batches with retry logic.

```python
BATCH_SIZE = 100
MAX_RETRIES = 3

all_vectors = []
failed_chunks = []

for i in range(0, len(ready_chunks), BATCH_SIZE):
    batch = ready_chunks[i : i + BATCH_SIZE]
    texts = [c.page_content for c in batch]

    try:
        vectors = embed_with_retry(texts, model=EMBEDDING_MODEL, max_retries=MAX_RETRIES)
        all_vectors.extend(zip(batch, vectors))
    except Exception as e:
        for chunk in batch:
            failed_chunks.append({
                'chunk_id': chunk.metadata['chunk_id'],
                'source': chunk.metadata['source'],
                'error': str(e),
            })
```

Write `embed_failures.jsonl` for any batch that fails all retries.

Track:
- total chunks attempted
- total succeeded
- total failed
- elapsed time
- throughput (chunks/sec)

---

## Step 5: Validate Embedding Output

Before inserting into the index, validate every vector:

```python
expected_dim = EMBEDDING_DIM  # e.g. 1536

for chunk, vector in all_vectors:
    assert vector.shape[0] == expected_dim, (
        f"Dimension mismatch for {chunk.metadata['chunk_id']}: "
        f"got {vector.shape[0]}, expected {expected_dim}"
    )
    assert not any(np.isnan(vector)), (
        f"NaN values in vector for {chunk.metadata['chunk_id']}"
    )
```

Reject any vector that fails these checks. Do not insert corrupted vectors.

---

## Step 6: Upsert to Vector Index

Insert validated vectors with their full metadata payload.

If you are normalizing for cosine:
```python
def normalize(v):
    return v / np.linalg.norm(v)

normalized_vectors = [normalize(v) for _, v in all_vectors]
```

Insert with associated metadata per vector.

Log:
- index namespace / collection used
- vectors inserted count
- index version being populated

---

## Step 7: Validate Index Integrity

After insertion, run integrity checks:

```python
# Check 1: vector count
expected_count = len([v for v in all_vectors])
actual_count = index.ntotal  # FAISS example
assert actual_count == expected_count

# Check 2: no duplicate chunk IDs
inserted_ids = [c.metadata['chunk_id'] for c, _ in all_vectors]
assert len(inserted_ids) == len(set(inserted_ids)), "Duplicate chunk IDs"
```

Log result as `index_integrity_report.json`.

---

## Step 8: Smoke Tests

Run 3-5 simple, high-confidence queries against the new index.

For each smoke test query, verify that the expected chunk (by `source` and `chunk_id`) appears in the top-5 results.

```python
SMOKE_TESTS = [
    {
        'query': 'How does the payment service handle rate limiting?',
        'expected_source': 'PAYMENT_SERVICE.md',
    },
    {
        'query': 'What are the Kubernetes deployment prerequisites?',
        'expected_source': 'k8s-deployment.md',
    },
]

smoke_pass = True
for test in SMOKE_TESTS:
    results = retrieve(test['query'], k=5)
    sources = [r.metadata['source'] for r in results]
    if test['expected_source'] not in sources:
        print(f"SMOKE FAIL: {test['query']}")
        smoke_pass = False

assert smoke_pass, "Smoke tests failed. Do not promote this index."
```

---

## Step 9: Benchmark Evaluation

Run the full gold query set evaluation.

```python
report = evaluate(
    queries=gold_query_set,
    retriever=retriever,
    k=5,
)
print(report)
```

Compare metrics against minimum thresholds and previous run.

Fail the pipeline if:
- Recall@5 drops more than 5 percentage points from previous benchmark
- No-hit rate exceeds 15%

Produce `benchmark_report.json` with full metrics.

---

## Step 10: Produce Manifest and Reports

Write an embedding manifest for this run:

```json
{
  "run_id": "embed_20260312_001",
  "timestamp": "2026-03-12T11:30:00Z",
  "embedding_model": "text-embedding-3-small",
  "embedding_dim": 1536,
  "preprocessing_version": "v1.2",
  "corpus": "fresh_harvest",
  "index_version": "idx_20260312",
  "chunks_attempted": 12480,
  "chunks_embedded": 12451,
  "chunks_failed": 29,
  "chunks_rejected_validation": 8,
  "smoke_tests_passed": true,
  "benchmark_Recall@5": 0.84,
  "benchmark_MRR": 0.76,
  "benchmark_NoHitRate": 0.04,
  "promoted": true
}
```

Keep this manifest in `embedding_artifacts/manifests/`.

---

## Step 11: Promote Index Version

Index version is promoted when:
- all integrity checks passed
- smoke tests passed
- benchmark metrics meet thresholds
- no regression vs previous run

Promotion means: traffic switches to new index version.

Keep previous version active for 24-48 hours as rollback insurance.

After validation period, decommission old version and clean up artifacts.

---

## Rollback Plan

If production issues are detected after promotion:

1. Switch traffic back to previous index version (already kept active)
2. Investigate what changed between versions
3. Fix the issue
4. Re-run full pipeline
5. Re-promote after fix is verified

The rollback is only possible if you kept the previous index version and its manifest.  
Never delete the previous version immediately after promotion.

---

## Playbook Summary Checklist

| Step | Artifact Produced |
|---|---|
| Load + validate inputs | `validation_failures.jsonl` |
| Preprocessing | `preprocessing_rejections.jsonl` |
| Token budget validation | `token_budget_report.csv` |
| Embedding generation | `embed_failures.jsonl` |
| Embedding validation | Log / assertion report |
| Index upsert | Index populated |
| Index integrity | `index_integrity_report.json` |
| Smoke tests | Pass/fail log |
| Benchmark evaluation | `benchmark_report.json` |
| Manifest | `embed_manifest.json` |
| Promotion | `promoted = true` in manifest |

---

*Part of Handson Phase 2: Embeddings | March 2026*
