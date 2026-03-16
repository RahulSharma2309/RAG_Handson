# 05 — Embedding Strategies by Dataset Type

## Why Strategy Varies by Dataset Type

A chunk of policy text and a chunk of CSV row data look completely different to an embedding model.

- Policy text: rich natural language, paragraphs, semantic coherence
- CSV row: structured fields, labels and values, minimal prose

If you apply the same chunking, preprocessing, and embedding strategy to both, you will get mediocre retrieval for both.

The core idea is: **match your embedding strategy to how the data is structured and how users will query it.**

This document walks through every major content type with real examples, failure patterns, and proven strategies.

---

## Dataset Type 1: Policy and Functional Documents

### What They Are

Policy documents, PRDs, process guides, SOPs, onboarding guides, HR documents, compliance documents.

Examples:
- "Leave policy for remote employees"
- "Product Requirements Document for Checkout v2"
- "User onboarding flow for Fresh Harvest"

### How Users Query Them

- "What is the refund policy for damaged goods?"
- "What are the steps in the signup flow?"
- "Who approves a purchase over $5000?"

These are natural language questions expecting natural language answers.

### What Works

- Recursive splitting with moderate chunk_size (400–600 tokens)
- Preserve section headings in chunk text — they carry orientation context
- A chunk containing a heading + its content retrieves much better than a chunk with just body text
- General-purpose embedding models work well here

### What Fails

- Stripping headings from chunks → query "what is the approval process" misses a chunk because it no longer has heading context
- Over-chunking (too small) → answer requires 3-4 adjacent chunks none of which are individually sufficient
- Under-chunking (too large) → one chunk covers too many policies, retrieval precision drops

### Concrete Example

**Good chunk:**
```
## Purchase Approval Process

All purchase requests above $5,000 require approval from the Finance Director.
Requests must be submitted via the procurement portal with three competitive quotes.
Approval SLA is 5 business days.
```

**Bad chunk (heading stripped):**
```
All purchase requests above $5,000 require approval from the Finance Director.
Requests must be submitted via the procurement portal with three competitive quotes.
Approval SLA is 5 business days.
```

Query: "Who approves large purchases?"
Result: Good chunk retrieved. Bad chunk sometimes missed because the semantic context of "approval process" is weakened.

### Metadata to Add

```json
{
  "doc_type": "policy",
  "owner_team": "finance",
  "version": "v3.1",
  "effective_date": "2026-01-01",
  "section": "procurement"
}
```

---

## Dataset Type 2: Technical Documents

### What They Are

Architecture diagrams (as text), API docs, runbooks, deployment guides, troubleshooting playbooks, system design documents.

Examples:
- "AUTH_SERVICE.md" describing the authentication architecture
- Kubernetes deployment runbook
- "How to roll back a failed deployment"

### How Users Query Them

- "What is the retry policy for the payment service?"
- "Which port does the auth service expose?"
- "How do I roll back a Helm release?"

Technical queries often contain exact identifiers, port numbers, service names, command names.

### What Works

- Recursive splitting with slightly larger chunks (500–700 tokens) — technical context needs more room
- Keep code blocks, commands, and config snippets inside chunks — they are often the most specific part
- Include service/module name in metadata for filtering
- Hybrid retrieval (semantic + keyword) works best here because users often query by exact terms

### What Fails

- Separating a description from its code block → "how to configure rate limiting" lands in a chunk without the config example
- Small chunk_size cuts code blocks mid-function → chunk is syntactically broken and embeds poorly
- Embedding only prose, stripping all commands → retrieval fails for operational queries

### Concrete Example

**Good chunk (description + code kept together):**
```
## Rate Limiting Configuration

The auth service applies rate limiting using the token bucket algorithm.
Configure it in `appsettings.json`:

```json
{
  "RateLimiting": {
    "PermitLimit": 100,
    "Window": "00:01:00",
    "QueueLimit": 50
  }
}
```
```

**Bad chunk (code stripped):**
```
The auth service applies rate limiting using the token bucket algorithm.
Configure it in appsettings.json.
```

Query: "What is the permit limit for auth service rate limiting?"
Good chunk: retrieved correctly.
Bad chunk: retrieved, but answer cannot be answered — value is not present.

### Metadata to Add

```json
{
  "doc_type": "technical_doc",
  "service": "auth-service",
  "environment": "production",
  "section": "rate-limiting",
  "contains_code": true
}
```

---

## Dataset Type 3: CSV / Tabular Data

### What They Are

Structured rows of data, often representing records: employees, orders, products, incidents, transactions.

### How Users Query Them

Two very different query types:

1. **Precise lookup**: "What is the order status for order ID ORD-2291?"
2. **Aggregate/analytical**: "What are the common issues reported by senior engineers?"

These need different embedding representations.

### Two Required Embedding Strategies

#### Strategy A: Row-Level Embedding (for precise lookup)

Convert each row to labelled natural language text:

```
employee_id: EMP-0042
name: Priya Mehta
department: Platform Engineering
title: Senior Site Reliability Engineer
location: Bangalore
employment_type: Full-time
manager: Arjun Nair
```

Embed each row separately. This allows very precise per-record retrieval.

Query "who is the SRE in Bangalore" → matches this chunk directly.

#### Strategy B: Group Summary Embedding (for analytical queries)

Build one summary document per group (e.g. per department):

```
Platform Engineering Department Summary:
12 employees, 3 Senior SREs, 4 backend engineers, 2 DevOps, 1 manager, 2 interns.
Locations: Bangalore (8), Remote (4).
Average tenure: 2.3 years.
Common skills: Kubernetes, Python, Terraform.
```

Query "what skills are common in platform engineering" → matches this summary.

### What Fails

- Embedding raw CSV rows without field labels → "Priya Mehta, Bangalore, Senior SRE" is ambiguous to the model
- Only row-level embedding without summaries → analytical queries fail
- Embedding column headers as part of each row → inflates token count and adds noise

### Metadata to Add

```json
{
  "doc_type": "tabular_record",
  "chunk_type": "row",
  "primary_id": "EMP-0042",
  "source_file": "employee_workforce_data.csv",
  "row_index": 42,
  "total_rows": 300
}
```

---

## Dataset Type 4: JSON / API Payloads

### What They Are

API responses, configuration files, event logs, webhook payloads.

### How Users Query Them

- "What was the delivery address for order 8823?"
- "What error code does the payment service return for insufficient funds?"

These queries reference specific fields. Users do not ask about JSON structure.

### What Works

Convert selected fields to natural language:

**Raw JSON:**
```json
{
  "order_id": "ORD-8823",
  "customer_name": "Rahul Sharma",
  "delivery_address": "42 MG Road, Bangalore",
  "status": "delivered",
  "payment_method": "UPI",
  "total_amount": 1240.50
}
```

**Embedded text:**
```
Order ORD-8823 placed by Rahul Sharma.
Delivery address: 42 MG Road, Bangalore.
Status: delivered.
Payment method: UPI. Total: 1240.50.
```

### What Fails

- Embedding raw JSON string → the model sees brackets, quotes, colons as tokens and the semantic meaning is diluted
- Embedding every field including system-generated noise fields (timestamps, trace IDs, internal flags) → vector represents system noise
- Schema version drift without re-embedding → new fields not captured in old index

### Metadata to Add

```json
{
  "doc_type": "api_payload",
  "schema_version": "v2",
  "entity_type": "order",
  "primary_id": "ORD-8823"
}
```

---

## Dataset Type 5: PDF Documents

### What They Are

Reports, invoices, contracts, research papers, interview analyses, technical manuals.

PDF is the hardest type because it is a visual format, not a semantic one. Extraction quality varies enormously.

### How Users Query Them

- "What are the deployment prerequisites in the AWS guide?"
- "What score did the candidate receive for problem-solving?"
- "What is the refund clause in contract section 4?"

### The Special Problems With PDF Embedding

#### Problem 1: Column Interleaving
Multi-column PDFs produce interleaved text:

```
Kubernetes is an open-source Docker is a containerization
container orchestration platform that packages
```

These two columns are mixed. The embedding represents gibberish.

**Solution**: detect and skip interleaved pages, or use layout-aware extraction.

#### Problem 2: OCR Needed But Not Done
Scanned PDFs or image-only PDFs produce empty or garbage text.

**Solution**: detect OCR-needed files before embedding, route them to OCR pipeline, and do not embed raw garbled text.

#### Problem 3: Repetitive Header/Footer Domination
A 10-token chunk that is entirely page metadata embeds nothing useful and pollutes the index.

**Solution**: always apply PDF boilerplate removal (see doc 04).

### What Works

- PyMuPDF for text extraction (fastest, highest fidelity)
- Always clean before embedding (hyphen repair, header removal, whitespace)
- Skip near-empty pages (< 50 chars after cleaning)
- Keep page number in metadata for citation
- For scanned PDFs: run OCR first, then treat as clean text

### Metadata to Add

```json
{
  "doc_type": "pdf",
  "source": "Documents/ML-Notes/02-confusion-matrix.pdf",
  "page": 4,
  "total_pages": 24,
  "profile": "technical_report",
  "ocr_needed": false,
  "extraction_method": "pymupdf_text_layer"
}
```

---

## Dataset Type 6: Code Repositories

### What They Are

Source code files, scripts, configuration files.

### How Users Query Them

- "Show me the function that handles payment validation"
- "Which file configures retry logic?"
- "How is the database connection pool initialized?"

These queries are symbol-oriented (function names, file names, patterns) and semantic (intent-based).

### What Works

Split by structural boundaries:

- One function or method per chunk
- One class with its methods
- One configuration block

Include file path, function name, class name in chunk text AND metadata:

```python
# File: services/payment_service.py
# Class: PaymentValidator
# Method: validate_card

def validate_card(self, card_number: str, expiry: str) -> bool:
    """Validates card number format and expiry date."""
    if not self._luhn_check(card_number):
        return False
    return self._check_expiry(expiry)
```

The comment header gives the model orientation — it embeds `PaymentValidator.validate_card` as a semantic concept, not just disconnected code.

### General vs Code-Aware Models

For code-heavy corpora, evaluate a code-aware embedding model against your general model.

If your benchmark shows:
- recall on code queries improves significantly → switch to code-aware
- minimal improvement → stay with general model for simplicity

Do not assume code-aware is always better. It depends on query distribution.

### Metadata to Add

```json
{
  "doc_type": "source_code",
  "language": "python",
  "repo": "fresh-harvest-backend",
  "file_path": "services/payment_service.py",
  "symbol_type": "method",
  "symbol_name": "validate_card",
  "class_name": "PaymentValidator"
}
```

---

## Dataset Type 7: Conversational and Support Data

### What They Are

Support tickets, chat transcripts, meeting notes, email threads.

### How Users Query Them

- "What was the most common complaint about checkout last month?"
- "Was there a bug reported about payment failures on Android?"

### What Works

- Per-conversation or per-ticket chunking (not sentence-level)
- Include subject/title at top of each chunk
- Metadata: date, channel, resolution status, tags

### What Fails

- Sentence-level chunking → loses conversational context entirely
- No metadata on date/category → cannot filter by time or issue type

---

## Dataset Type Summary (Quick Reference)

| Dataset Type | Chunk Strategy | Key Preprocessing | Model Preference | Critical Metadata |
|---|---|---|---|---|
| Policy/Functional | Recursive, 400-600 tokens | Whitespace, heading preservation | General text | version, owner_team, section |
| Technical Docs | Recursive, 500-700 tokens | Keep code blocks, service terms | General text (+ hybrid) | service, environment, contains_code |
| CSV / Tabular | Row-level + group summaries | Field labelling | General text | primary_id, chunk_type |
| JSON Payloads | Field-to-text template | Select fields, remove noise | General text | schema_version, entity_type |
| PDF | Page-split + recursive | Boilerplate removal, hyphen repair | General text | page, ocr_needed, profile |
| Code | Function/class boundaries | Path + symbol in chunk text | General or code-aware | language, file_path, symbol_name |
| Conversational | Per-ticket/conversation | Subject header in chunk | General text | date, channel, tags |

---

*Part of Handson Phase 2: Embeddings | March 2026*
