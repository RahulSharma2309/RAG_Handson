# Chunking Strategy for RAG Learning

This guide explains how markdown chunking is organized for your RAG playground so the repository stays learner-friendly and production-like.

## Design Goal

- Keep source docs under `rag_system_workspace/rag/input_docs/`.
- Keep generated chunk artifacts outside source docs.
- Support multiple document types with reusable profile-based chunking.

## Where chunk outputs are stored

All generated chunk files now go to:

- `rag_system_workspace/rag_artifacts/chunks/`

This keeps generated data separate from documentation content.

## Coverage scope

The script chunks **all markdown files under `rag_system_workspace/rag/input_docs/`** (recursive).

## Profile-based strategy (document-family approach)

Instead of one global chunk setting for every file, we use a few reusable profiles.

### Profile: `product_owner_docs`

- Target tokens: `450`
- Max tokens: `600`
- Overlap: `60`
- Split levels: `##`

Applied to folders like:
- `input_docs/0-product-owner-onboarding`
- `input_docs/3-product-owner`
- `input_docs/4-epics-and-pbis`
- `input_docs/9-roadmap-and-tracking`

Why:
- These docs are concept-heavy and narrative.
- Larger chunks preserve context for business questions.

### Profile: `operations_docs`

- Target tokens: `320`
- Max tokens: `450`
- Overlap: `50`
- Split levels: `##`

Applied to folders like:
- `input_docs/6-ci-cd`
- `input_docs/8-kubernetes-local-deployment`
- `input_docs/11-kubernetes`

Why:
- Ops docs are procedural and troubleshooting-oriented.
- Smaller chunks improve retrieval precision.

### Profile: `technical_docs`

- Target tokens: `360`
- Max tokens: `520`
- Overlap: `70`
- Split levels: `##`

Applied to folders like:
- `input_docs/6-architecture`
- `input_docs/7-services`

Why:
- Technical docs need moderate chunk size with extra overlap for dependencies.

### Profile: `general_docs` (fallback)

- Target tokens: `380`
- Max tokens: `520`
- Overlap: `60`
- Split levels: `##`

Used for docs that do not match the specific mappings above.

## Hierarchical splitting flow

1. Split by markdown headings (`##`) to preserve semantic sections.
2. Split each section by paragraph blocks.
3. If chunk exceeds `max_tokens`, apply token-window split with overlap.

## Metadata written per chunk

Each chunk record includes:

- `chunk_id`
- `source_file`
- `folder_profile`
- `section_title`
- `section_chunk_index`
- `token_count`
- `text`

This metadata is important for retrieval filtering, source citation, and debugging.

## Output format

Each source markdown file creates a JSONL file:

- `rag_system_workspace/rag_artifacts/chunks/<same-relative-doc-path>/<file>.chunks.jsonl`

Run summaries:

- `rag_system_workspace/rag_artifacts/chunks/chunking_run_summary.json`
- `rag_system_workspace/rag_artifacts/chunks/chunking_run_summary.md`

## How to run

From project root:

```powershell
python rag_system_workspace/scripts/chunk_markdown_docs.py
```

or with your project interpreter:

```powershell
.\.venv\Scripts\python.exe rag_system_workspace/scripts/chunk_markdown_docs.py
```

## RAG learning progression from here

1. Start embeddings on `rag_system_workspace/rag_artifacts/chunks/**/*.jsonl`.
2. Keep metadata during embedding and vector insertion.
3. Evaluate retrieval quality with folder filters (for example, only `operations_docs`).
4. Tune profile settings using retrieval evaluation, not only chunk counts.
