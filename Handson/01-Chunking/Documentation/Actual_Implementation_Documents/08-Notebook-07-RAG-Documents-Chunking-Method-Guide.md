# 08 - Notebook 07 Method Guide (`07_rag_documents_chunking_handson.ipynb`)

This notebook is dedicated only to `Documents/RAG documents`.

## Why this notebook exists
- This corpus is mostly markdown theory/implementation guides.
- Heading-aware chunking is essential to preserve semantic sections.

## Core methods
- `split_rag_docs(...)`
  - heading split first, recursive split second
- `clean_text(...)`
  - normalizes formatting before splitting
- metadata enrichment
  - chunk indexing and token/character counts for evaluation and debugging

## Output
- `data/rag_documents/chunk_artifacts/all_rag_documents_chunks.jsonl`
- per-file chunk JSONL files
- quality report CSV/JSON in `data/rag_documents/quality_reports`

## Practical value
- Creates clean chunks aligned with conceptual headings, which improves retrieval relevance for “what is X” and “compare X vs Y” queries.

