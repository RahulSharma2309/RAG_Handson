# 11 — Multilingual, Code, and Domain-Specific Embeddings

## Multilingual Corpora

- Use multilingual embedding models when user queries span languages
- Validate cross-language retrieval explicitly (query in Hindi, doc in English, etc.)
- Tag language metadata for analysis

## Code Retrieval

- Prefer code-aware embeddings when code search is primary
- Preserve identifiers, file paths, and signatures in chunk text
- Add metadata: `repo`, `path`, `language`, `symbol_type`

## Domain-Specific Corpora

For legal, medical, finance, or security:

- benchmark domain-specific models against general models
- include domain terms in test queries
- track compliance constraints for hosted APIs

## Routing Strategy (Advanced)

Use query classification to route:

- policy/business query -> general text model
- code query -> code model
- multilingual query -> multilingual model

Start with one model first, route later if benchmark evidence supports it.
