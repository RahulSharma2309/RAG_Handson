# 01 — Environment Setup (Embeddings Phase)

## Goal

Prepare a clean, reproducible environment for embedding generation and vector indexing experiments.

## Folder Layout

- `Handson/02-Embeddings/notebooks/`
- `Handson/02-Embeddings/data/`
- `Handson/02-Embeddings/Documentation/Embeddings/`
- `Handson/02-Embeddings/Documentation/Actual_Implementation_Documents/`

## Recommended Python Libraries

- `tiktoken` for token counting
- `sentence-transformers` for local embedding models
- `openai` or provider SDK (if hosted embeddings are used)
- `faiss-cpu` (or chosen vector database client) for indexing experiments
- `pandas` for artifact and quality reporting

## Setup Principles

1. Keep model name/version explicit in code
2. Keep preprocessing version explicit in metadata
3. Keep vector index version explicit in output artifacts
4. Keep raw chunk artifacts immutable once published

## Output Artifacts to Generate

- embedding manifest JSON
- per-batch failure log JSONL
- benchmark report CSV/JSON
- index metadata summary
