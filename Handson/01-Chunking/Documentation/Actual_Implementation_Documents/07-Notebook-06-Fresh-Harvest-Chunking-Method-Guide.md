# 07 - Notebook 06 Method Guide (`06_fresh_harvest_chunking_handson.ipynb`)

This notebook is dedicated only to `Documents/Fresh_Harvest_Documents`.

## Why this notebook exists
- Fresh Harvest corpus is technical and mixed-format (`.md`, `.mmd`, `.txt`, scripts, csv notes).
- Needs a technical profile with stronger overlap and code-aware separators.

## Core methods
- `split_technical(...)`
  - recursive splitting with `\n##`, `\n###`, and code-block-aware separators
- `clean_text(...)`
  - removes formatting noise before chunking
- metadata enrichment
  - corpus/source/doc_type + per-chunk ids and token counts

## Output
- `data/fresh_harvest_documents/chunk_artifacts/all_fresh_harvest_documents_chunks.jsonl`
- per-file chunk JSONL files
- quality report CSV/JSON in `data/fresh_harvest_documents/quality_reports`

## Practical value
- Produces retrieval-ready chunks for product, architecture, and engineering process documents without mixing unrelated sections.

