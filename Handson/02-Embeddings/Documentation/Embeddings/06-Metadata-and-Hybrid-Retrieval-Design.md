# 06 — Metadata and Hybrid Retrieval Design

## Why Metadata Matters

Embeddings capture semantics, but metadata provides control.

Use metadata to:

- filter by product area, team, or date
- enforce tenancy/security boundaries
- reduce false positives in broad corpora

## Recommended Metadata Schema

- `source`
- `chunk_id`
- `doc_type`
- `corpus`
- `version`
- `effective_date`
- `owner_team`
- `language`

## Hybrid Retrieval Pattern

1. Run lexical retrieval (BM25/keyword) and vector retrieval
2. Merge candidates
3. Re-rank with cross-encoder or LLM reranker
4. Return top-k chunks with citations

## When Hybrid Helps Most

- Acronyms and exact IDs
- Error codes and log snippets
- Domains with strict terminology

Hybrid often improves precision without replacing embeddings.
