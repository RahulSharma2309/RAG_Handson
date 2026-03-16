# 08 — Evaluation and Benchmarking Embeddings

## Goal

Select embeddings with evidence, not intuition.

## Build a Gold Query Set

For each query, define:

- expected relevant chunks/documents
- acceptable alternates
- failure examples

Cover easy, medium, and hard queries.

## Metrics to Track

- Recall@k
- Precision@k
- MRR (Mean Reciprocal Rank)
- nDCG
- No-hit rate

## Evaluation Loop

1. Fix chunking profile and metadata schema
2. Compare candidate embedding models
3. Measure metrics on same query set
4. Inspect failure cases manually
5. Adopt winner and log report ID

## Failure Analysis Categories

- semantic miss
- lexical miss
- metadata filter over-restriction
- truncation/long-input failure
- domain terminology mismatch
