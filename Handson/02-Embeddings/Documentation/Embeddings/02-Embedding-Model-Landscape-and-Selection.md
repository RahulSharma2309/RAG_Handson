# 02 — Embedding Model Landscape and Selection

## Model Families

- **Open-source local models**: full control, lower API cost, infra responsibility
- **Hosted API models**: strong quality and convenience, usage-based cost
- **Domain-specific models**: tuned for legal, biomedical, finance, or code text

## Selection Criteria

1. Retrieval quality on your benchmark queries
2. Latency (single + batch)
3. Cost per 1K tokens / per request
4. Context length (max input tokens)
5. Multilingual support
6. Operational constraints (self-host vs managed)

## Common Trade-offs

- Higher quality models often cost more and run slower
- Smaller models reduce cost/latency but may hurt recall
- Long-context models reduce truncation risk for larger chunks

## Baseline-to-Advanced Model Strategy

- **Phase A**: one robust general text model
- **Phase B**: compare 2-3 candidates using same evaluation set
- **Phase C**: adopt hybrid strategy if needed (for example code model + doc model)

## Model Registry (Recommended)

Track this for every experiment:

- `model_name`
- `provider`
- `embedding_dim`
- `max_input_tokens`
- `preprocessing_version`
- `index_version`
- `evaluation_report_id`

Without a model registry, reproducibility breaks quickly.
