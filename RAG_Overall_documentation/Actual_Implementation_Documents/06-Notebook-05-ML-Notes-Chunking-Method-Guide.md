# 06 - Notebook 05 Method Guide (`05_ml_notes_chunking_handson.ipynb`)

This notebook is dedicated only to `Documents/ML-Notes`.

## Why this notebook exists
- ML notes are conceptual, hierarchical, and heading-heavy.
- Heading-first chunking produces cleaner learning units than plain fixed splitting.

## Core methods
- `split_ml_notes(...)`
  - first pass: markdown heading split (`#`, `##`, `###`)
  - second pass: recursive split for oversized sections
- `clean_text(...)`
  - normalizes text artifacts before splitting
- metadata enrichment
  - `chunk_id`, `chunk_index`, `token_count`, `char_count`, `doc_type`

## Output
- `data/ml_notes/chunk_artifacts/all_ml_notes_chunks.jsonl`
- per-file chunk JSONL files
- quality report CSV/JSON in `data/ml_notes/quality_reports`

## Practical value
- Gives a clean educational chunk base that supports topic-level retrieval and progression by section.

