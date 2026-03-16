# 09 — Cost, Latency, and Scaling Guide

## Why This Matters at Every Stage

Even at prototype scale, decisions you make now about batching, caching, and model choice compound into serious cost and performance problems when you reach production volume.

A team that embeds 10K chunks in development without batching will hit rate limits and timeouts when they try to embed 1M chunks at launch.

This document gives you the mental models, formulas, and practical patterns to plan and operate your embedding pipeline sustainably.

---

## Understanding the Two Cost Phases

### Phase 1: Initial Ingestion Cost

One-time (or infrequent) cost to embed your entire corpus.

Factors:
- total number of chunks
- average tokens per chunk
- embedding model's cost per token or per request
- parallelism achievable (rate limits, hardware)

Formula (API pricing):

```
ingestion_cost = total_chunks * avg_tokens_per_chunk / 1_000_000 * price_per_M_tokens
```

Example:
- 200,000 chunks
- average 200 tokens per chunk
- model priced at $0.02 per 1M tokens

```
= 200,000 * 200 / 1,000,000 * 0.02
= 40,000,000 / 1,000,000 * 0.02
= 40 * 0.02
= $0.80
```

Note: initial ingestion cost is often small. The real cost is in re-embedding.

### Phase 2: Ongoing Maintenance Cost

This is where cost compounds:

- documents are updated → affected chunks re-embedded
- new documents added → new chunks embedded
- model upgraded → full re-embed of entire corpus
- preprocessing change → full re-embed of affected documents

A team that upgrades their embedding model twice a year and re-embeds a 500K chunk corpus each time pays the ingestion cost twice — plus operational engineering time.

**Rule**: reduce re-embedding frequency through good change detection and versioning.

---

## Cost Reduction Strategies

### Strategy 1: Deduplication Before Embedding

Remove exact or near-exact duplicate chunks before embedding.

```python
seen = set()
unique_chunks = []
for chunk in all_chunks:
    h = hashlib.md5(chunk.page_content.strip().encode()).hexdigest()
    if h not in seen:
        seen.add(h)
        unique_chunks.append(chunk)
```

In practice, large corpora often have 5-15% duplicate chunks from repeated content, shared headers, or copied documents. Removing them before embedding saves money and improves retrieval quality.

### Strategy 2: Skip Already-Embedded Chunks

Use a persistent cache keyed on `(chunk_id, preprocessing_version, model_version)`.

Before embedding:
- check if chunk_id + versions already in cache
- skip embedding if found
- only embed new or changed chunks

```python
def should_embed(chunk_id, preprocessing_version, model_version, cache) -> bool:
    key = f"{chunk_id}|{preprocessing_version}|{model_version}"
    return key not in cache
```

This makes incremental runs cheap even for large corpora.

### Strategy 3: Avoid Embedding Low-Value Chunks

Do not embed:
- chunks under minimum length threshold (< 40 chars)
- pure boilerplate chunks (page numbers, confidentiality footers that slipped through)
- duplicate metadata-only chunks

Every token you do not embed saves cost and keeps the index clean.

### Strategy 4: Right-Size Your Model

If a smaller model gives Recall@5 = 0.81 and a larger model gives Recall@5 = 0.84, the 3-point gain may not justify 2x the cost.

Always benchmark first. Choose the smallest model that meets your quality threshold.

---

## Latency: Two Distinct Workloads

### Ingestion Latency

How long does it take to embed your corpus?

This affects: time to first deployment, re-indexing windows, CI/CD pipeline speed.

Factors:
- batch size
- number of parallel workers
- API rate limits (requests/min, tokens/min)
- network latency (for API models)
- inference speed (for local models)

### Query Latency

How long from user query to retrieved chunks?

This is the latency your users feel. Measured as:
- `p50`: median experience
- `p95`: 95th percentile (most users)
- `p99`: 99th percentile (tail experience)

Typical targets:
- p95 < 200ms for retrieval step in conversational RAG
- p95 < 100ms for real-time autocomplete-style retrieval

Query latency components:
- query embedding time (model inference)
- ANN search time
- metadata filter time
- reranking time (if used)

---

## Batching: The Most Important Ingestion Optimization

Sending one chunk at a time to an embedding API is extremely inefficient.

Without batching:
- 1 API call per chunk
- network overhead per call
- likely to hit requests-per-minute limits quickly

With batching (e.g. batch_size=32):
- 32 chunks per API call
- 32x fewer API calls
- far better throughput

```python
def embed_in_batches(texts: list[str], model, batch_size: int = 32) -> list:
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        vectors = model.encode(batch)  # SentenceTransformers example
        all_vectors.extend(vectors)
    return all_vectors
```

### Choosing Batch Size

- Too small: many API calls, high overhead, rate limit exposure
- Too large: may exceed request payload limits, higher memory per call

Practical starting points:
- OpenAI API: 100–2048 texts per request (check current limits)
- SentenceTransformers local: 32–128 depending on GPU/CPU memory
- Other APIs: check provider docs for max batch size

---

## Throughput Planning

Before a large ingestion run, estimate time:

```
estimated_time = total_chunks / (batch_size * batches_per_second)
```

Example:
- 500,000 chunks
- batch size 100
- 2 batches/second throughput

```
= 500,000 / (100 * 2)
= 500,000 / 200
= 2,500 seconds ≈ 42 minutes
```

With parallel workers (e.g. 4 workers):

```
= 2,500 / 4 ≈ 625 seconds ≈ 10 minutes
```

Plan your re-index windows around this estimate.

---

## Retry and Failure Handling

At scale, some API calls will fail (rate limits, timeouts, transient errors).

Without a retry strategy, a failure at chunk 40,000 out of 500,000 means restarting from scratch.

```python
import time
import random

def embed_with_retry(texts: list[str], model, max_retries: int = 3) -> list:
    for attempt in range(max_retries):
        try:
            return model.encode(texts)
        except RateLimitError:
            wait = 2 ** attempt + random.uniform(0, 1)  # exponential backoff
            print(f"Rate limit hit. Retrying in {wait:.1f}s (attempt {attempt+1})")
            time.sleep(wait)
    raise Exception("Embedding failed after max retries")
```

Also: write successfully embedded chunks to output before they are lost. Do not embed and hold everything in memory until the entire run completes.

---

## Progress Checkpointing

For large ingestion runs, checkpoint progress:

```python
import json
from pathlib import Path

CHECKPOINT_FILE = Path("embed_checkpoint.json")

def load_checkpoint() -> set:
    if CHECKPOINT_FILE.exists():
        data = json.loads(CHECKPOINT_FILE.read_text())
        return set(data["embedded_ids"])
    return set()

def save_checkpoint(embedded_ids: set):
    CHECKPOINT_FILE.write_text(
        json.dumps({"embedded_ids": list(embedded_ids)}, indent=2)
    )
```

Resume logic:
- load checkpoint
- skip already-embedded chunk IDs
- continue from where it left off

This makes a 42-minute run resumable. Without it, every failure restarts from zero.

---

## Quantization for Local Models

If using local models (SentenceTransformers, etc.), model quantization can:

- reduce model size 4x-8x (INT8 or INT4 quantization)
- reduce inference memory significantly
- decrease latency at slight quality cost

When to consider:
- inference memory exceeds your hardware
- latency is too high
- quality loss is acceptable after benchmark validation

---

## Scaling Architecture Patterns

### Single-Worker (Dev/Small Scale)
- sequential embedding loop
- in-memory index
- suitable for < 100K chunks

### Multi-Worker (Medium Scale)
- divide corpus into shards
- parallel workers, each embeds a shard
- merge outputs after all complete
- suitable for 100K – 5M chunks

### Queue-Based Pipeline (Production Scale)
```
Document Sources → Chunking Worker → Message Queue → Embedding Workers (N) → Index Writer
```

- chunking and embedding are decoupled
- embedding workers scale horizontally
- queue absorbs spikes
- dead letter queue for failed items
- suitable for continuously updated large corpora

---

## Dev vs Staging vs Production Index Costs

Keep separate indexes per environment.

Rule of thumb for cost allocation:
- dev: 5-10% of prod corpus (representative sample)
- staging: full corpus (needed for realistic benchmarking)
- prod: full corpus

Do not embed full prod corpus in dev. Waste of cost and noise in development.

---

## Summary: Cost and Latency Quick Reference

| Decision | Impact on Cost | Impact on Latency |
|---|---|---|
| Larger batch size | Reduces cost (fewer API calls) | Reduces ingestion latency |
| Better caching | Reduces cost (skip re-embeds) | No direct query impact |
| Deduplication | Reduces cost (fewer chunks) | Reduces query latency (smaller index) |
| Smaller model | Reduces cost | Reduces query and ingestion latency |
| More parallel workers | No direct cost change | Reduces ingestion time |
| ANN vs exact search | No cost change | Dramatically reduces query latency at scale |
| Cross-encoder reranking | Increases compute cost | Increases query latency |

---

*Part of Handson Phase 2: Embeddings | March 2026*
