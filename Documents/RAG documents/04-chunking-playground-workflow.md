# Chunking Playground Workflow

This guide explains how to use the generated chunk artifacts as a learning playground for your RAG system.

## What is generated

When you run:

```powershell
.\.venv\Scripts\python.exe rag_system_workspace/scripts/chunk_markdown_docs.py
```

the script reads markdown files from `rag_system_workspace/rag/input_docs/` and writes chunks to:

- `rag_system_workspace/rag_artifacts/chunks/`

This keeps source docs and generated artifacts separated.

## Output structure

The output mirrors source doc folders:

- `rag_system_workspace/rag_artifacts/chunks/0-product-owner-onboarding/*.chunks.jsonl`
- `rag_system_workspace/rag_artifacts/chunks/6-ci-cd/*.chunks.jsonl`
- and all other sections under `rag_system_workspace/rag/input_docs/*`

Each line in a JSONL file is one chunk with metadata.

## Suggested learning path

1. Pick one family first, for example:
   - `0-product-owner-onboarding` for business queries
   - `6-ci-cd` for operational queries
2. Embed only that folder and build retrieval.
3. Expand to all folders and compare retrieval quality.
4. Add metadata filters (by folder profile) in retriever.

## Why this is useful

- You can test chunking and retrieval strategy quickly.
- You can compare folder-specific retrieval behavior.
- You can practice enterprise-style profile chunking on real docs.
