# 03 — Tokenization and Chunk-to-Embedding Interface

## Why This Interface Is Critical

Embedding models consume tokens, not characters.  
A chunk that looks "small" in characters can still overflow token limits.

## Key Risks

- **Silent truncation**: tail of chunk discarded before embedding
- **Boundary loss**: important context split across chunks
- **Tokenizer mismatch**: counting with one tokenizer, embedding with another

## Practical Rules

- Measure token count before embedding
- Keep a safety margin below model max input tokens
- Use chunk overlap where context continuity matters
- Store `token_count` in metadata for diagnostics

## Input Budget Example

If model limit is 8192 tokens, do not target 8192 exactly.  
Target a lower operational limit (for example 6000-7000) for safer pipelines.

## Metadata Fields to Add

- `chunk_id`
- `char_count`
- `token_count`
- `chunk_profile`
- `source`
- `model_name_used`

This makes truncation and retrieval failures debuggable.
