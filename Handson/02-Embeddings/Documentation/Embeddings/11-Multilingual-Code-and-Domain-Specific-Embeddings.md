# 11 — Multilingual, Code, and Domain-Specific Embeddings

## Why General-Purpose Models Are Not Always Enough

A general-purpose English embedding model is trained primarily on English text, mostly prose, across general web/book/Wikipedia content.

When you throw it at:
- code repositories with function names and type signatures
- documents in Hindi, Arabic, French, or Spanish
- legal contracts with dense Latin terminology
- biomedical papers with gene names and drug identifiers

...the model may miss retrieval opportunities that domain-specific or multilingual models would catch.

This document tells you when and why to go beyond general models, and how to make that decision with evidence.

---

## Part 1: Multilingual Embeddings

### The Core Problem

A general English-only model embeds Hindi and English in separate spaces.

Query in Hindi: "रेट लिमिटिंग कैसे काम करता है?"  
(Meaning: "How does rate limiting work?")

Document in English: "Rate limiting uses a token bucket algorithm..."

English-only model: low similarity score — treats Hindi query as unrelated.  
Multilingual model: high similarity score — maps both to similar semantic region.

### When You Need Multilingual Embeddings

1. Users query in a language different from document language
2. Documents themselves span multiple languages in the same corpus
3. Names, product terms, and places use non-English characters

### What Multilingual Models Do Differently

They are trained on text in 50–100+ languages simultaneously, using cross-lingual examples so that semantically equivalent sentences across languages get embedded nearby.

### Key Considerations for Multilingual Systems

#### Tokenization
Multilingual models use SentencePiece or BPE with large multilingual vocabularies.  
Token counts for non-Latin scripts (e.g. Arabic, Chinese, Devanagari) will be higher per character than English.  
Recalibrate your token budget for each script.

#### Benchmark Cross-Lingually
Your gold query set must include cross-lingual pairs:
- Query in Language A, expected chunk in Language B
- Query and chunk both in Language A
- Query and chunk both in Language B

All three scenarios must be validated.

#### Metadata for Language Awareness
```json
{
  "language": "hi",
  "query_language_support": true
}
```

This lets you debug which language combinations fail and enables language-based routing later.

#### When Cross-Lingual Retrieval Fails
Common causes:
- model supports the language but was not trained on your domain vocabulary in that language
- named entities differ across languages (product names, service names)
- very low-resource language with limited training data in the model

Fix: evaluate per language pair. Consider language-aware hybrid retrieval (BM25 per language).

---

## Part 2: Code Embeddings

### Why Code Is Different From Prose

When a user asks "How does the payment validation work?", the answer might be in:

- a prose description in architecture docs
- a function signature and docstring in source code
- a comment in a configuration file

General text models are trained on prose. Code has fundamentally different structure:

- identifiers: `validate_card`, `PaymentService`, `CARD_NUMBER`
- syntax: brackets, semicolons, type annotations
- semantics carried by naming conventions, not word order

### The Two Retrieval Modes for Code

#### Mode 1: Documentation-to-Code
User asks in natural language. Wants to find the relevant code section.

Example:
- Query: "How is card validation implemented?"
- Expected: function `validate_card` in `PaymentValidator` class

General model might retrieve this if documentation is embedded alongside code.  
Code-aware model performs better at matching natural language intent to code structure.

#### Mode 2: Code-to-Code
User gives a code snippet or symbol. Wants related code.

Example:
- Query: `from services.auth import verify_token`
- Expected: `verify_token` implementation and related tests

For this, code-aware models are significantly better. General models struggle with identifier-heavy inputs.

### Code Chunk Structure That Helps Any Model

Include orientation context in every code chunk:

```python
# File: services/payment_service.py
# Class: PaymentValidator
# Method: validate_card
# Purpose: validates card format and expiry

def validate_card(self, card_number: str, expiry: str) -> bool:
    """Validates card number using Luhn algorithm and checks expiry date."""
    if not self._luhn_check(card_number):
        return False
    return self._check_expiry(expiry)
```

This comment block ensures even a general model embeds meaningful semantics, not just syntax tokens.

### When to Use a Code-Aware Model

Do this test:

1. Build gold query set with 20-30 code-specific queries
2. Test general model vs code-aware model
3. If code-aware model improves Recall@5 by > 10 percentage points → switch
4. If improvement is < 5% → stay with general model for simplicity

Do not switch models without evidence. Maintaining two models adds operational complexity.

### Code Metadata

```json
{
  "doc_type": "source_code",
  "language": "python",
  "repo": "fresh-harvest-backend",
  "file_path": "services/payment_service.py",
  "symbol_type": "method",
  "symbol_name": "validate_card",
  "class_name": "PaymentValidator",
  "line_start": 42,
  "line_end": 58
}
```

`line_start` / `line_end` enables direct navigation from RAG answer to source file.

---

## Part 3: Domain-Specific Embeddings

### What "Domain-Specific" Means

A domain-specific model is trained on text from a particular industry or technical domain.

Domains with strong dedicated models:
- Legal (contracts, statutes, case law)
- Biomedical (papers, clinical notes, drug interactions)
- Finance (SEC filings, earning reports, risk analysis)
- Security / cybersecurity
- Scientific / academic papers

### Why Domain Models Sometimes Win

Domain-specific terminology is often rare in general training data.

Examples:
- Legal: `res judicata`, `indemnification clause`, `force majeure`
- Biomedical: `CRISPR-Cas9`, `mRNA expression`, `p53 tumor suppressor`
- Finance: `EBITDA`, `derivative instrument`, `mark-to-market`

General models may not associate these terms correctly with related concepts because they appear infrequently in general training data.

Domain-specific models have seen thousands of domain documents during training and map these terms correctly.

### When Domain Models Are Worth It

1. Your corpus is deeply domain-specific (90%+ domain vocabulary)
2. Your gold query set reveals consistent failure on domain term queries
3. General model Recall@5 on domain-specific queries is < 0.65

If your corpus is a mix (some policy, some technical, some domain-specific), start with a strong general model. Only route to a domain model if benchmark proves it necessary.

### The Compliance Factor

Hosted domain-specific models (e.g. medical or financial APIs) may require:
- data processing agreements
- HIPAA compliance (healthcare data)
- financial data handling policies

Self-hosted domain models avoid this but require infra to operate.

---

## Query Routing: Using Multiple Models Together

When you have confirmed through benchmarking that different query types need different models, implement query routing.

### Architecture

```
User Query
    │
    ▼
Query Classifier (lightweight model or rule-based)
    │
    ├── "code"          → embed with code-aware model → code index
    ├── "multilingual"  → embed with multilingual model → multilingual index
    ├── "legal"         → embed with legal model → legal index
    └── "general"       → embed with general model → general index
```

### When Not to Route

Routing adds complexity:
- multiple models to maintain and version
- multiple indexes to manage
- query classifier that can misroute

Only add routing if:
- benchmark proves material quality gain for specific query class
- operational complexity is worth the quality improvement

Start with one model. Route later if evidence demands it.

### Rule-Based vs Model-Based Routing

**Rule-based** (simpler):
- If query contains code keywords (imports, function calls, `def`, `class`) → code model
- If query is non-English characters → multilingual model

**Model-based** (more accurate):
- Fine-tune a lightweight classifier
- Route based on predicted query class

Start with rules. Move to model-based only if rules miss important cases.

---

## Practical Decision Tree

```
Is your corpus multilingual OR are users querying in non-English?
├── Yes → Use multilingual model (verify with cross-lingual benchmark)
└── No ↓

Is > 30% of your corpus source code?
├── Yes → Benchmark code-aware model, adopt if Recall@5 improves > 10pp
└── No ↓

Is your corpus 90%+ domain-specific (legal/biomedical/financial)?
├── Yes → Benchmark domain model against general, adopt if better
└── No → Use strong general text model as default
```

---

## Summary

| Corpus Type | Starting Model | Switch If |
|---|---|---|
| English prose/docs | General text model | Never (unless benchmark forces it) |
| Mixed English + multilingual | Multilingual model | Cross-lingual Recall@5 < 0.65 with general |
| Code-heavy | General text first | Code Recall@5 improves > 10pp with code model |
| Legal / biomedical / finance | General text first | Domain Recall@5 consistently < 0.65 |

---

*Part of Handson Phase 2: Embeddings | March 2026*
