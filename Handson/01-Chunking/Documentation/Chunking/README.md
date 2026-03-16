# Chunking — One-Stop Documentation

> Everything about chunking in one place. The science, all strategies, every data type, libraries, parameters, advanced techniques, quality evaluation, production patterns, and common mistakes. After this folder, nothing about chunking should be left unclear.

---

## Who This Is For

- Beginners learning chunking from scratch
- Engineers building RAG with mixed document types
- Teams designing chunking strategy for production systems
- Anyone who wants to go from "I know what chunking is" to "I can design and tune it properly"

---

## Reading Order — Follow This Exactly

The file numbers now match this order. Go from `01` to `13` in sequence.

### Foundation Track — Start Here

| # | File | What You'll Learn |
|---|---|---|
| 01 | `01-Chunking-Science-and-Foundations.md` | What chunking is, why chunk boundaries decide answer quality, tokens explained with examples, context windows, the quality chain, four levers of chunk design with real examples |
| 02 | `02-Pre-vs-Post-Chunking-and-Context-Windows.md` | Pre vs post chunking with real scenarios, embedding model context windows, LLM context windows, truncation walkthrough, context budget planning, why large-context LLMs still need chunking |
| 03 | `03-All-Chunking-Methods-Complete-Guide.md` | All 11 methods with real document examples, before/after comparisons, working code — Fixed, Recursive, Document-based, Sliding Window, Semantic, LLM-based, Agentic, Late, Hierarchical, Adaptive, Code |

### Strategy Track — Once You Know the Basics

| # | File | What You'll Learn |
|---|---|---|
| 04 | `04-Libraries-and-Loaders-by-Source.md` | Which loader/library to use for PDF, CSV, JSON, DOCX, SQL, Markdown |
| 05 | `05-Chunking-Strategies-by-Dataset-Type.md` | Exact chunking strategy per data type: CSV, PDF, technical docs, functional docs, mixed corpus |
| 06 | `06-Functional-Documents-Chunking-Guide.md` | Deep guide for policies, PRDs, user flows, process docs |
| 07 | `07-Technical-Documents-Chunking-Guide.md` | Deep guide for architecture, APIs, runbooks, troubleshooting, code-heavy docs |

### Advanced Track — Production Readiness

| # | File | What You'll Learn |
|---|---|---|
| 08 | `08-Advanced-Chunking-Techniques.md` | Semantic chunking deep dive, Anthropic contextual retrieval, hierarchical, late chunking, chunk expansion, summary chunks |
| 09 | `09-Chunk-Size-and-Parameter-Tuning-Guide.md` | How chunk size affects embeddings, overlap science, parameter tuning process, experiment template |
| 10 | `10-Chunk-Quality-Checklist-and-Evaluation.md` | Evaluation framework, benchmark query sets, scoring, diagnostics map |
| 11 | `11-Common-Mistakes-and-Production-Lessons.md` | Top 10 chunking mistakes, industry lessons, anti-pattern reference |

### Implementation Track — Code and Practice

| # | File | What You'll Learn |
|---|---|---|
| 12 | `12-End-to-End-Chunking-Playbook.md` | Full SOP from raw docs to retrieval-ready chunks |
| 13 | `13-Implementation-Patterns-and-Code-Templates.md` | All code patterns: text, PDF, CSV, JSON, DOCX, code files, profile router, metadata schema |
| 14 | `14-PDF-Chunking-Deep-Dive.md` | Full deep-dive for PDF chunking: OCR, tables, diagrams, extraction strategy, metadata, evaluation |

---

## Core Principles

### 1. Chunking is not formatting — it is retrieval architecture
Every chunk boundary is a retrieval decision. Wrong boundaries = wrong answers.

### 2. The quality chain
```
Source quality → Chunk quality → Embedding quality → Retrieval quality → Answer quality
```
If chunking is broken, nothing downstream fully fixes it.

### 3. One chunk = one focused idea
A chunk should answer one focused question clearly without requiring surrounding context.

### 4. Profile-based, not global
Different document types need different chunk strategies.
One global chunk size is an anti-pattern.

### 5. Evaluate with real queries — not chunk count
Chunk count means nothing. Top-k retrieval accuracy on real user questions means everything.

---

## Quick Method Selector

```
What type of document?
├── Source code                    → 03 (Method 11: Code Chunking)
├── Markdown / HTML               → 03 (Method 3: Document-Based)
├── Transcript / Conversation     → 03 (Method 4: Sliding Window)
├── Large book / manual           → 03 (Method 9: Hierarchical)
├── Dense academic / legal text   → 03 (Method 5: Semantic)
├── Policy / business docs        → 06
├── Technical / architecture docs → 07
├── CSV / tabular                 → 05 + 13
├── JSON / API response           → 04 + 13
└── Everything else               → 03 (Method 2: Recursive) as default
```

---

## Quick Parameter Selector

```
Starting point for most docs:
  chunk_size=512, overlap=50, RecursiveCharacterTextSplitter

Tune based on:
  Answers too generic?     → decrease chunk_size
  Answers incomplete?      → increase chunk_size
  Context lost at edges?   → increase overlap
  Too many duplicate hits? → decrease overlap
  Wrong domain retrieved?  → add metadata filters
```

---

## All Methods at a Glance

| Method | Complexity | Cost | Best For |
|---|---|---|---|
| Fixed-size | Low | Free | Quick baseline |
| Recursive | Medium | Free | Default choice for most text |
| Document-based | Low–Medium | Free | Markdown, HTML, code |
| Sliding Window | Low | Free | Transcripts, conversations |
| Semantic | Medium–High | Free–Paid | Dense academic/legal text |
| LLM-based | High | Paid | Complex, high-value docs |
| Agentic | Very High | High | Max quality, cost no concern |
| Late | High | Free–Paid | Cross-reference heavy docs |
| Hierarchical | Medium | Free | Books, manuals, large docs |
| Adaptive | High | Variable | Mixed-structure datasets |
| Code | Medium | Free | Source code, scripts |

---

*Part of RAG_Overall_documentation series | March 2026*
