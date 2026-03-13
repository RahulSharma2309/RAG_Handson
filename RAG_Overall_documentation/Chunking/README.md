# Chunking — One-Stop Documentation

> Everything about chunking in one place. The science, all strategies, every data type, libraries, parameters, advanced techniques, quality evaluation, production patterns, and common mistakes. After this folder, nothing about chunking should be left unclear.

---

## Who This Is For

- Beginners learning chunking from scratch
- Engineers building RAG with mixed document types
- Teams designing chunking strategy for production systems
- Anyone who wants to go from "I know what chunking is" to "I can design and tune it properly"

---

## Recommended Reading Order

### Foundation Track (Start here if new to chunking)

| # | File | What You'll Learn |
|---|---|---|
| 1 | `01-Chunking-Science-and-Foundations.md` | What chunking is, why it exists, context windows, embedding alignment, the quality chain |
| 2 | `10-Pre-vs-Post-Chunking-and-Context-Windows.md` | Pre vs post chunking, LLM/embedding context windows, lost in the middle, context budget planning |
| 3 | `03-All-Chunking-Methods-Complete-Guide.md` | Every chunking method explained: Fixed, Recursive, Document-based, Sliding Window, Semantic, LLM-based, Agentic, Late, Hierarchical, Adaptive, Code |

### Strategy Track (Once you know the basics)

| # | File | What You'll Learn |
|---|---|---|
| 4 | `02-Libraries-and-Loaders-by-Source.md` | Which loader/library to use for PDF, CSV, JSON, DOCX, SQL, Markdown |
| 5 | `03-Chunking-Strategies-by-Dataset-Type.md` | Exact chunking strategy per data type: CSV, PDF, technical docs, functional docs, mixed corpus |
| 6 | `04-Functional-Documents-Chunking-Guide.md` | Deep guide for policies, PRDs, user flows, process docs |
| 7 | `05-Technical-Documents-Chunking-Guide.md` | Deep guide for architecture, APIs, runbooks, troubleshooting, code-heavy docs |

### Advanced Track (Production readiness)

| # | File | What You'll Learn |
|---|---|---|
| 8 | `09-Advanced-Chunking-Techniques.md` | Semantic chunking deep dive, Anthropic contextual retrieval, hierarchical, late chunking, chunk expansion, summary chunks |
| 9 | `11-Chunk-Size-and-Parameter-Tuning-Guide.md` | How chunk size affects embeddings, overlap science, parameter tuning process, experiment template |
| 10 | `06-Chunk-Quality-Checklist-and-Evaluation.md` | Evaluation framework, benchmark query sets, scoring, diagnostics map |
| 11 | `12-Common-Mistakes-and-Production-Lessons.md` | Top 10 chunking mistakes, industry lessons, anti-pattern reference |

### Implementation Track (Code and practice)

| # | File | What You'll Learn |
|---|---|---|
| 12 | `07-End-to-End-Chunking-Playbook.md` | Full SOP from raw docs to retrieval-ready chunks |
| 13 | `08-Implementation-Patterns-and-Code-Templates.md` | All code patterns: text, PDF, CSV, JSON, DOCX, code files, profile router, metadata schema |

---

## Core Principles (The 5 Things You Must Know)

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
├── Source code                    → Code Chunking (file 03, Method 11)
├── Markdown / HTML               → Document-Based (file 03, Method 3)
├── Transcript / Conversation     → Sliding Window (file 03, Method 4)
├── Large book / manual           → Hierarchical (file 09)
├── Dense academic / legal text   → Semantic (file 09)
├── Policy / business docs        → Recursive large + file 04
├── Technical / architecture docs → Recursive medium + file 05
├── CSV / tabular                 → Row + Summary pattern (file 08)
├── JSON / API response           → JSONLoader + Recursive (file 08)
└── Everything else               → Recursive (file 03, Method 2) as default
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
