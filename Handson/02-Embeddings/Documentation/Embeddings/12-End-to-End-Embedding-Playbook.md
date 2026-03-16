# 12 — End-to-End Embedding Playbook

## Objective

Convert chunk artifacts into a validated, query-ready vector index.

## SOP

1. Load chunk artifacts (`page_content` + metadata)
2. Validate required metadata fields
3. Apply preprocessing rules
4. Enforce token budget
5. Generate embeddings with model version tag
6. Upsert vectors into target namespace/index
7. Run smoke-test queries
8. Run benchmark suite and publish report
9. Promote index version after pass criteria

## Required Artifacts

- embedding manifest (input counts, model, timestamp)
- failed record log
- benchmark report
- index version map

## Promotion Gate

Promote only if:

- Recall@k and MRR meet threshold
- no critical retrieval regressions
- latency/cost within target bounds

## Rollback Plan

Always keep previous stable index version active until new version is verified.
