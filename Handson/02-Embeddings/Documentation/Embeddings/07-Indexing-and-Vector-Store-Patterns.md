# 07 — Indexing and Vector Store Patterns

## Index Design Basics

- Keep one index namespace per corpus/environment when possible
- Enforce consistent embedding dimension per index
- Store raw text + metadata alongside vectors

## Upsert and Reindex Patterns

- **Incremental upsert**: add/update changed chunks only
- **Full reindex**: required when model or preprocessing changes
- **Blue/green indexes**: build new index, switch traffic, then retire old

## Operational Patterns

- Track `index_version`
- Track `embedding_model_version`
- Keep ingestion logs with success/fail counts
- Validate vector count equals expected chunk count

## Production Checks

- Vector dimension mismatch guard
- Duplicate chunk ID guard
- Empty/near-empty text rejection
- Latency percentile monitoring (`p50/p95/p99`)
