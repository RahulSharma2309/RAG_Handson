# 05 — Embedding Strategies by Dataset Type

## Functional Documents (Policies, PRDs, Workflows)

- Use general-purpose text embedding model
- Keep section headings in chunk text
- Preserve metadata for filtering by domain/team/version

## Technical Documents (Architecture, APIs, Runbooks)

- Include code terms and config keywords
- Keep medium chunk sizes to preserve technical context
- Add metadata for service/module/environment

## CSV / Tabular

- Embed row-level text for precise lookups
- Also create summary-level embeddings for broad queries
- Keep stable primary key metadata for traceability

## JSON / API Payloads

- Convert selected fields to natural language templates
- Embed only useful fields, not raw payload noise
- Track schema version in metadata

## PDF

- Clean extraction artifacts before embedding
- Separate OCR-needed files from text-layer files
- Include page-level provenance metadata

## Code Repositories

- Use code-aware models when code search is primary
- Keep symbol/path metadata for exact references
- Split by function/class/module boundaries, not fixed text blocks only
