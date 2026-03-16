# 06 — Metadata and Hybrid Retrieval Design

## Why Metadata Is Not an Afterthought

Most teams design their embedding pipeline, then add metadata as an afterthought.  
This is the wrong order.

Metadata should be designed **before** chunking, because metadata shapes:

- which chunks can be filtered at query time
- which chunks are cited in answers
- how you debug retrieval failures
- how you version and roll back your index

Without well-designed metadata, you have a vector index you cannot operate.

---

## What Metadata Does in a RAG System

Metadata serves four distinct jobs:

### Job 1: Retrieval Filtering

Narrow the candidate pool before or after vector search.

Example: User asks "What is the refund policy for premium customers?"

Without metadata filtering:
- query hits ALL documents in the index
- retrieval might return refund policy for a different product line

With metadata filtering:
- `doc_type = "policy"` AND `domain = "premium_customers"`
- query only searches policy docs in the right domain

### Job 2: Answer Attribution (Citation)

When the LLM generates an answer, the user needs to know where it came from.

Without `source` and `page`: "According to the documentation..."  
With metadata: "According to `PAYMENT_SERVICE.md`, section Rate Limiting, page 7..."

This is the difference between a useful answer and a trustworthy answer.

### Job 3: Debugging and Quality Analysis

When retrieval fails, metadata tells you why.

Was the document chunked from the right source? Is the version correct? Was the section heading preserved?

Without metadata, you are guessing.

### Job 4: Versioning and Lifecycle Management

When you update a document, which chunks in the index need to be replaced?

Without `source` + `version` + `chunk_id`, you cannot do incremental updates. You must re-embed everything every time.

---

## Core Metadata Schema

This is the minimum recommended schema for any RAG system.

```json
{
  "chunk_id": "fh_3f7a91bc22d1",
  "source": "Documents/Fresh_Harvest_Documents/PAYMENT_SERVICE.md",
  "doc_type": "technical_doc",
  "corpus": "fresh_harvest",
  "section": "rate-limiting",
  "version": "v2.3",
  "effective_date": "2026-02-01",
  "language": "en",
  "char_count": 847,
  "token_count": 193,
  "chunk_index": 4,
  "chunk_profile": "technical_docs",
  "preprocessing_version": "v1.2",
  "embedding_model": "text-embedding-3-small",
  "index_version": "idx_20260312"
}
```

Extended fields for specific corpus types:

```json
{
  "owner_team": "platform-engineering",
  "service": "payment-service",
  "environment": "production",
  "contains_code": true,
  "page": 7,
  "ocr_needed": false,
  "pii_redacted": false
}
```

---

## Designing Metadata for Your Query Patterns

Before finalising metadata schema, write down the top 10-20 queries your users will ask.

For each query, ask: "What would I need to filter on to find the right chunk?"

Example query analysis:

| User Query | Likely Filter Needed |
|---|---|
| "What is the refund policy?" | `doc_type = policy`, `domain = payments` |
| "How do I deploy to production?" | `doc_type = runbook`, `environment = production` |
| "Who is the SRE for auth service?" | `corpus = hr`, `role = SRE`, `team = auth` |
| "What changed in version 3?" | `version = v3`, `doc_type = changelog` |
| "Show me Python code for JWT validation" | `language = python`, `contains_code = true`, `topic = jwt` |

Each filter dimension needs a metadata field.

---

## Metadata Field Design Principles

### Principle 1: Use Controlled Vocabularies

`doc_type` should be one of a fixed set of values, not free text.

Bad: `doc_type = "This is a technical architecture document"`  
Good: `doc_type = "technical_doc"`

Controlled vocabularies enable reliable filter queries.

### Principle 2: Flat Is Better Than Nested

Most vector stores support flat key-value metadata.

Bad: `{"category": {"type": "policy", "sub": "HR"}}`  
Good: `{"doc_type": "policy", "category": "HR"}`

### Principle 3: Keep it Queryable

Every field should be something you'd actually filter on.

`char_count` is useful for debugging. You probably won't filter by exact char count at query time.  
`doc_type`, `service`, `version` are directly filterable.

---

## Hybrid Retrieval Design

### The Problem Pure Vector Search Has

Vector search finds semantically similar content.  
But some queries are not semantic — they are lexical.

Examples where pure vector fails:
- "Order ID ORD-8823" — a specific ID
- "Error code E-4029" — an exact code
- "kubectl rollout undo deployment" — an exact command
- "RBAC policy v1.3" — exact version reference

For these, vector search returns "conceptually similar" content. But the user needs the exact match.

### Lexical Retrieval: BM25

BM25 is a keyword scoring algorithm (the basis of most search engines).

How it works:
- counts how often query terms appear in documents
- adjusts for document length and term frequency
- returns documents ranked by keyword relevance

What it's good at:
- exact ID matching
- error code lookup
- command and symbol search
- version string matching

What it misses:
- semantic paraphrasing ("car" vs "automobile")
- conceptual questions
- multilingual queries

### Hybrid Retrieval: Best of Both

Hybrid retrieval runs both vector search and lexical search and combines results.

**Architecture:**

```
User Query
    │
    ├──> Lexical Retrieval (BM25)     → top-k lexical candidates
    │
    └──> Vector Retrieval (ANN)       → top-k semantic candidates
             │
             ▼
         Merge + Deduplicate candidates
             │
             ▼
         Reranking (Cross-encoder or LLM)
             │
             ▼
         Final top-k chunks passed to LLM
```

### Fusion Strategies

#### Reciprocal Rank Fusion (RRF)

Combines ranked lists without needing to normalize scores:

```
RRF_score(chunk) = 1 / (k + rank_lexical) + 1 / (k + rank_vector)
```

Where `k` is a smoothing constant (typically 60).

Chunks that appear high in both lists score highest.

This is simple, effective, and does not require score calibration.

#### Weighted Score Fusion

Normalize scores from both retrieval systems, then combine:

```
final_score = alpha * vector_score + (1 - alpha) * bm25_score
```

Where alpha (0–1) controls how much you weight semantic vs lexical.

Requires calibration per corpus but gives more control.

### When to Use Hybrid Retrieval

| Corpus Characteristic | Use Hybrid? |
|---|---|
| Contains exact IDs, codes, version strings | Yes — strongly |
| Technical docs with commands and symbols | Yes |
| Pure natural language policy docs | Optional — test first |
| Short Q&A style content | Test both and benchmark |
| Multilingual corpus | Yes — multilingual BM25 helps |

---

## Reranking

After merging candidates from vector + lexical retrieval, reranking selects the best ones.

### Cross-Encoder Reranking

A cross-encoder is a model that takes (query, chunk) as a single input and produces a relevance score.

Unlike embedding models (which encode query and chunk separately), cross-encoders see both at once and can model fine-grained interaction.

When to use:
- top-k quality matters greatly (few-shot answer synthesis)
- latency budget allows a reranking step
- vocabulary and semantic precision are both important

Trade-off: cross-encoders are slower than vector similarity. Use on top-N (e.g. 20) candidates, not the full index.

### LLM Reranking

Send top-N retrieved chunks to an LLM with: "Which of these is most relevant to the query?"

Use when:
- cross-encoder is unavailable
- nuanced contextual understanding is required

Trade-off: expensive and slow.

---

## Metadata Filtering Modes

Most vector stores support two modes of metadata filtering:

### Pre-filtering
Apply filter before vector search.  
The ANN search only considers vectors matching the filter.

Pros: precise, deterministic  
Cons: can over-filter and return no results if filter is too strict

### Post-filtering
Apply filter after vector search.  
Retrieve top-k by similarity, then filter the result set.

Pros: always returns candidates from full index  
Cons: may lose relevant results if too many filtered out from top-k

**Practical Rule:**

Use pre-filtering when your filters are broad (e.g. `doc_type = "policy"`).  
Use post-filtering when filters are narrow and you are worried about missing results.

---

## Common Metadata Mistakes

### Mistake 1: Using free-text for categorical fields

`doc_type = "this is the kubernetes architecture guide"` is useless as a filter.  
`doc_type = "architecture_doc"` is a filter.

### Mistake 2: No version or effective_date on policy documents

A user asks about the refund policy. You return an outdated version. The LLM generates an answer from old policy.

### Mistake 3: Over-filtering in production

A filter like `corpus = "legal" AND version = "v3" AND env = "production" AND language = "en"` may return zero candidates if any one field is missing or mismatch.

Test filter combinations with real data before enabling.

### Mistake 4: Not testing hybrid vs vector-only

Teams assume hybrid is always better. Sometimes for short, clean corpora, pure vector is faster and equally good.

Always benchmark your specific corpus.

---

## Example: Metadata-Driven Debugging

A user asks: "What are the deployment steps for auth service?"

Retrieval returns a chunk about `USER_SERVICE` deployment.

Without metadata, you cannot explain why.  
With metadata, you inspect the returned chunk:

```json
"service": "user-service"
```

Diagnosis: the chunks for auth service have `service = "auth_service"` but the query filtered `service = "auth-service"` (hyphen vs underscore mismatch).

Fix: normalize metadata values at ingestion time. Use controlled vocabulary.

---

*Part of Handson Phase 2: Embeddings | March 2026*
