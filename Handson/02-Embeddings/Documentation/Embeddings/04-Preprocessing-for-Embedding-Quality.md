# 04 — Preprocessing for Embedding Quality

## Purpose

Preprocessing removes noise before vectorization so embeddings capture meaning, not artifacts.

## High-Impact Cleanup Steps

- Normalize repeated whitespace/newline noise
- Remove duplicated headers/footers from PDFs
- Fix OCR artifacts where possible
- Standardize unicode and punctuation where needed
- Keep important symbols for code and formulas

## What Not to Over-Clean

- Do not remove domain terms that look uncommon
- Do not flatten structured lists/tables blindly
- Do not aggressively stem/lemmatize unless validated

## PII and Compliance Considerations

Choose policy before embedding:

- redact sensitive fields
- hash IDs if identity linking is required
- tag records with compliance metadata (`pii_redacted`, `policy_version`)

## Preprocessing Versioning

Store a `preprocessing_version` in each chunk metadata.

If preprocessing rules change, re-embed and re-index with a new version.
