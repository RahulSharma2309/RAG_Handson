# 04 — Preprocessing for Embedding Quality

## Why Preprocessing Is Not Optional

Many teams skip this step because the pipeline "works."  
But bad preprocessing does not produce errors — it produces bad vectors quietly.

If your chunk contains OCR garbage, repeated headers, broken hyphenation, or noise tokens, the embedding model will represent that noise as part of the meaning. It will then retrieve based on that noise. Queries that should match will miss. Queries that should not match will hit.

Preprocessing is not about cleaning for aesthetic reasons. It is about ensuring the signal-to-noise ratio of the embedding input is as high as possible.

---

## Mental Model: What You Feed Is What Gets Embedded

The embedding model cannot distinguish useful text from noise.  
It represents whatever tokens it receives.

Example:

**Bad chunk input (unpreprocessed PDF text):**
```
Page 4 of 24 | CONFIDENTIAL | Kubernetes Deployment Guide

To  deploy  on  AWS,  use   Amazon  EKS  for   all  production
workloads. Make sure  the IAM  role has  EKS:CreateCluster per-
mission before beginning deployment.
```

What gets embedded:
- page number noise
- extra whitespace as tokens
- confidentiality header
- broken word: `per-\nmission`

**Good chunk input (after preprocessing):**
```
To deploy on AWS, use Amazon EKS for all production workloads. Make sure the IAM role has EKS:CreateCluster permission before beginning deployment.
```

The second version produces a vector that represents the actual meaning. The first produces a polluted vector that partially represents metadata noise.

---

## Categories of Preprocessing

There are five categories of preprocessing decisions, each with different impact on embedding quality:

### Category 1: Text Normalization (Always Do)
### Category 2: Content-Specific Cleaning (Do Per Document Type)
### Category 3: Semantic Preservation Rules (Know When Not to Clean)
### Category 4: PII and Compliance Handling (Policy Decision)
### Category 5: Versioning and Reproducibility (Operational Discipline)

---

## Category 1: Text Normalization

These rules apply to almost every corpus. They remove noise that adds tokens without adding meaning.

### 1a) Whitespace Normalization

Problem: extra spaces, tabs, or multiple newlines inflate token count and pollute vectors.

```python
import re

def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\t', ' ', text)           # tabs -> single space
    text = re.sub(r' {2,}', ' ', text)        # 2+ spaces -> single space
    text = re.sub(r'\n{3,}', '\n\n', text)    # 3+ newlines -> double newline
    return text.strip()
```

### 1b) Hyphenated Line Break Repair

Problem: PDFs extract hyphenated words split across lines (e.g. `auto-\nmatically`).

```python
def fix_hyphenated_breaks(text: str) -> str:
    return re.sub(r'-\n(\s*)', '', text)
```

Result: `automatically` instead of `auto-matically`.

### 1c) Unicode Ligature Normalization

Problem: PDFs often produce ligatures that are single Unicode characters but look like two letters.

Examples:
- `ﬁ` (fi ligature) → `fi`
- `ﬂ` (fl ligature) → `fl`
- `ﬀ` (ff ligature) → `ff`

```python
LIGATURES = {
    'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
    '\u2019': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2014': '--',
}

def fix_ligatures(text: str) -> str:
    for ligature, replacement in LIGATURES.items():
        text = text.replace(ligature, replacement)
    return text
```

### 1d) Null Byte and Control Character Removal

Some document extractors produce null bytes or control characters.

```python
def remove_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
```

---

## Category 2: Content-Specific Cleaning

Different document types produce different noise patterns.

### 2a) PDF-Specific: Remove Page Headers and Footers

Problem: headers/footers repeat on every page and dominate embeddings for short chunks.

```python
def remove_pdf_boilerplate(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()

# Example patterns:
PDF_BOILERPLATE = [
    r'Page \d+ of \d+',
    r'CONFIDENTIAL',
    r'Kubernetes Deployment Guide',  # specific doc title repeated in header
    r'\d{4}-\d{2}-\d{2}',           # repeated date stamps
]
```

Key insight: boilerplate detection is document-specific. You cannot write one universal regex for all PDFs. Profile your documents and define patterns per corpus.

### 2b) Markdown-Specific: Remove Render-Only Syntax

In Markdown, some syntax adds no semantic meaning to embeddings:

Remove:
- raw HTML tags inside Markdown
- image paths: `![alt](path/to/image.png)` → keep alt text, remove path
- raw anchor links

Keep:
- heading text (critical context)
- list content
- code blocks (they carry meaning for technical docs)

```python
def clean_markdown(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)               # HTML tags
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)  # image: keep alt
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)   # links: keep label
    return text
```

### 2c) CSV Row Text: Consistent Field Labeling

When converting CSV rows to text for embedding, always include field labels.

**Bad (no labels):**
```
John Smith, 28, Engineering, Senior Engineer, Remote
```

**Good (labelled):**
```
name: John Smith
age: 28
department: Engineering
title: Senior Engineer
work_mode: Remote
```

The labelled version embeds semantically richer representations. A query for "senior engineers who work remotely" will match the second version far more reliably.

### 2d) Code and JSON: Decide What to Preserve

For code files being embedded:

- Preserve function signatures, class names, docstrings
- Consider whether comments are signal or noise for your query type
- Do not remove type hints — they carry semantic meaning for code search

For JSON payloads:

- Preserve key names alongside values
- Remove system-generated IDs that users never query by
- Convert nested structures to readable key-value text

---

## Category 3: Semantic Preservation Rules (When NOT to Clean)

Over-cleaning damages embeddings just like under-cleaning.

### Do Not Remove Domain Terminology

Terms that look unusual to a general cleaning tool may be high-value domain signals.

Examples:
- `RBAC`, `EKS`, `kubectl` in a Kubernetes corpus
- `ICC`, `IFRS`, `GAAP` in a finance corpus
- `p53`, `mRNA`, `CRISPR` in a biomedical corpus

If you strip these because they look like "noise" or "abbreviations," you destroy the very signal that makes domain-specific retrieval work.

### Do Not Collapse Ordered Lists Into Prose

```
Prerequisites:
1. Install AWS CLI 2.x
2. Configure kubectl 1.27+
3. Create IAM role with EKS:CreateCluster
```

If flattened to a single sentence, the list structure (numbered steps, individual items) contributes to the embedding. Keep it.

### Do Not Aggressively Stem or Lemmatize

Stemming and lemmatization reduce words to root forms (`running` → `run`).

Modern embedding models already handle morphological variation naturally through training.  
Adding stemming on top can reduce nuance — for example distinguishing `running a cluster` vs `a runner service`.

Unless your domain-specific benchmark shows improvement, do not stem.

### Do Not Strip Code From Technical Docs

If your corpus includes architecture docs that contain code blocks:

```yaml
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
```

This code block carries meaning for queries like "what are the memory limits for this service?"  
Removing code blocks from technical docs destroys one of their most specific parts.

---

## Category 4: PII and Compliance Handling

Embedding personal data creates legal and operational risk.

### Common PII in Business Corpora

- Full names in HR/employee records
- Email addresses
- Phone numbers
- Credit card / bank account numbers
- National ID numbers
- Home addresses

### Approach 1: Redact Before Embedding

Replace PII with typed placeholders:

```python
import re

def redact_pii(text: str) -> str:
    text = re.sub(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
                  '[EMAIL]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
                  '[CARD_NUMBER]', text)
    text = re.sub(r'\b\+?[\d\s\-\(\)]{10,15}\b',
                  '[PHONE]', text)
    return text
```

### Approach 2: Hash Sensitive IDs

For employee IDs or system IDs that need to be traceable but not exposed:

```python
import hashlib

def hash_id(raw_id: str, salt: str = 'your-secret-salt') -> str:
    return hashlib.sha256((salt + raw_id).encode()).hexdigest()[:16]
```

Store `hashed_id` in metadata. Never embed raw PII.

### Approach 3: Policy Tagging

Add compliance metadata to every record:

```python
meta['pii_redacted'] = True
meta['policy_version'] = 'v2.1'
meta['redaction_date'] = '2026-03-12'
```

This makes it auditable. If policy changes, you know which index version to re-process.

---

## Category 5: Preprocessing Versioning (Production Essential)

Every time you change a preprocessing rule, your vectors change for the affected text.

If you mix vectors from different preprocessing versions in one index, retrieval becomes inconsistent.

### Rules

1. Every chunk must carry `preprocessing_version` in metadata
2. When any cleaning rule changes: increment version, re-embed affected documents, re-index
3. Never silently overwrite old vectors with new ones — track the version transition

### Version Scheme

```
preprocessing_v1.0 - initial release, basic whitespace only
preprocessing_v1.1 - added PDF boilerplate removal
preprocessing_v2.0 - changed ligature handling + PII redaction added
```

Store in metadata:

```json
{
  "preprocessing_version": "v2.0",
  "embedding_model": "text-embedding-3-small",
  "index_version": "idx_20260312"
}
```

---

## Preprocessing Pipeline in Order

Apply preprocessing steps in this order:

1. Remove control characters
2. Fix ligatures
3. Fix hyphenated line breaks (PDF specific)
4. Normalize whitespace
5. Remove page headers/footers (PDF specific) / HTML tags (Markdown) / raw IDs (JSON)
6. Apply PII redaction
7. Add field labels (CSV/tabular text)
8. Final whitespace pass
9. Validate: reject if result is empty or under minimum length (e.g. 30 chars)

### Minimum Length Guard

```python
def is_embeddable(text: str, min_chars: int = 40) -> bool:
    return len(text.strip()) >= min_chars
```

A chunk that is 5 characters after cleaning carries no semantic value and should be excluded.

---

## Concrete Example: Before and After Full Preprocessing

**Input from PDF extraction:**
```
Page 7 of 24  |  CONFIDENTIAL  |  Fresh Harvest Architecture Guide

Auth Service  Overview

The  auth  service  manages  all  user  authen-
tication and  session  management  for  the  Fresh
Harvest  platform.  It  uses  JWT  tokens  with  RS256
signing  and  implements  reﬁned  rate  limiting  on
login  endpoints.
```

**After preprocessing:**
```
Auth Service Overview

The auth service manages all user authentication and session management for the Fresh Harvest platform. It uses JWT tokens with RS256 signing and implements refined rate limiting on login endpoints.
```

Tokens before: approximately 88 (including noise)  
Tokens after: approximately 42 (pure signal)

The embedding of the second version accurately represents: auth, session management, JWT, RS256, rate limiting.  
The first version's embedding is polluted by the page header, broken words, and spacing artifacts.

---

## Quick Checklist Before Embedding

Before running your embedding pipeline, verify preprocessing has:

- Removed all known boilerplate for this corpus (headers, footers, dates)
- Fixed encoding issues (ligatures, control chars, null bytes)
- Repaired hyphenated line breaks for PDF content
- Applied PII redaction if corpus contains personal data
- Normalized whitespace
- Tagged metadata with `preprocessing_version`
- Rejected empty or near-empty chunks (< 40 chars)
- Preserved domain terminology and structural meaning

---

*Part of Handson Phase 2: Embeddings | March 2026*
