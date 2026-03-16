# 09 - Notebook 08 Method Guide (`08_sql_data_chunking_handson.ipynb`)

This notebook is dedicated only to `Documents/SQL Data`.

## Why this notebook exists
- SQL corpora require statement-aware boundaries (`;`) and controlled overlap.
- The folder may be empty at times; pipeline should still produce a valid report.

## Core methods
- `split_sql_or_text(...)`
  - SQL-specific separator priority includes `;` for statement-level boundaries
  - fallback for markdown/text/csv notes
- empty-corpus handling
  - writes a summary row with `no_files_found` instead of failing silently
- metadata enrichment
  - chunk id, token count, char count, source traceability

## Output
- `data/sql_data/chunk_artifacts/all_sql_data_chunks.jsonl`
- per-file chunk JSONL files (when files exist)
- quality report CSV/JSON in `data/sql_data/quality_reports`

## Practical value
- Keeps SQL chunking process reproducible and debuggable even when source availability changes over time.

