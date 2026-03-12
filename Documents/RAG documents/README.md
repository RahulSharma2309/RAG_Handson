# RAG Documents Hub

> Start here if you are new to RAG, or returning after a break.
> This folder is your complete, self-contained guide — from "I've never heard of RAG" to a fully working system with hands-on code.

---

## What is this project?

You built a complete RAG (Retrieval-Augmented Generation) system from scratch using 89 real Markdown documents as the knowledge base. The system can answer questions about your documents using a local AI model — no cloud, no API cost, no data leaving your machine.

**What is running:**
- 979 text chunks, each embedded as a 384-number vector
- A FAISS index for millisecond semantic search
- A CLI tool to ask questions from the terminal
- A browser-based chat UI at `http://localhost:7860`

---

## Reading Journey — Start Here

Read in order if you are new. Jump to any doc if you know what you need.

### Foundation Series (read first — no prior knowledge needed)

| # | Document | What you will learn |
|---|---|---|
| 1 | `01-Foundations/what-is-rag-complete-beginners-guide.md` | What RAG is, why it exists, the 5-step pipeline explained with analogies |
| 2 | `01-Foundations/why-rag-matters-and-augmentation-explained.md` | Business impact with real numbers (JP Morgan, Microsoft), what the "A" in RAG actually does |
| 3 | `01-Foundations/prompt-engineering-vs-finetuning-vs-rag.md` | The three approaches compared — when to use each, pros/cons, the chef analogy |
| 4 | `01-Foundations/tools-and-options-at-every-step.md` | Every tool at every step — free vs paid, when to use which |
| 5 | `01-Foundations/vector-store-vs-vector-database.md` | FAISS vs ChromaDB vs Pinecone — the full comparison |
| 6 | `01-Foundations/chunking-and-embedding-in-layman-terms.md` | Deep dive on chunking, embeddings, and cosine similarity with the Iron Man analogy |

### Implementation Guide (how this system was built)

| # | Document | What you will learn |
|---|---|---|
| 7 | `02-Implementation-Guide/files-created-and-why-they-matter.md` | Complete inventory of every file and script |
| 8 | `02-Implementation-Guide/faiss-vector-store-deep-dive.md` | The FAISS index — how it was built, what each file stores, how search works |
| 9 | `02-Implementation-Guide/vector-store-chromadb-hands-on.md` | The ChromaDB notebook — cell by cell walkthrough with every error explained |
| 10 | `02-Implementation-Guide/rag-answer-generation-and-ui.md` | Ollama LLM + ask_rag.py + Gradio chat UI — the complete generation layer |

### Optimization (improve quality)

| # | Document | What you will learn |
|---|---|---|
| 11 | `03-Optimization/how-to-optimize-chunking-and-embeddings.md` | How to tune chunking, embeddings, and retrieval for better answers |

### Roadmap (what was done, what is next)

| # | Document | What you will learn |
|---|---|---|
| 12 | `04-Roadmap/rag-hands-on-roadmap.md` | Full journey so far + the phases ahead + why each step matters |

---

## Quick Commands (if you just want to run something)

**Start the chat UI:**
```powershell
docker start ollama
.venv\Scripts\python.exe rag_system_workspace\app.py
# Open: http://localhost:7860
```

**Ask a question from terminal:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "How does the CI/CD pipeline work?" --show-chunks
```

**List available knowledge domains:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --list-profiles
```

**Rebuild everything after updating docs:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\chunk_markdown_docs.py
.venv\Scripts\python.exe rag_system_workspace\scripts\build_local_embeddings.py --normalize --output-name minilm_l6
```

---

## Folder Structure

```
RAG documents/
├── README.md                          ← You are here
│
├── 00-Start-Here/
│   └── README.md                      ← All quick commands in one place
│
├── 01-Foundations/                    ← Start here if new to RAG
│   ├── what-is-rag-complete-beginners-guide.md
│   ├── why-rag-matters-and-augmentation-explained.md  ← NEW
│   ├── prompt-engineering-vs-finetuning-vs-rag.md     ← NEW
│   ├── tools-and-options-at-every-step.md
│   ├── vector-store-vs-vector-database.md
│   └── chunking-and-embedding-in-layman-terms.md
│
├── 02-Implementation-Guide/           ← How this specific system was built
│   ├── files-created-and-why-they-matter.md
│   ├── faiss-vector-store-deep-dive.md
│   ├── vector-store-chromadb-hands-on.md
│   └── rag-answer-generation-and-ui.md
│
├── 03-Optimization/
│   └── how-to-optimize-chunking-and-embeddings.md
│
└── 04-Roadmap/
    └── rag-hands-on-roadmap.md
```

---

## Core Workspace Paths

```
rag_system_workspace/
├── app.py                             ← Gradio chat UI
├── rag/
│   └── input_docs/                   ← Source Markdown documents (89 files)
├── rag_artifacts/
│   ├── chunks/                       ← 979 chunk JSONL files
│   └── vectorstore/
│       └── minilm_l6/                ← FAISS index + metadata + embeddings
└── scripts/
    ├── chunk_markdown_docs.py        ← Chunking pipeline
    ├── build_local_embeddings.py     ← Embedding + FAISS build
    ├── search_local_embeddings.py    ← Retrieval only
    └── ask_rag.py                    ← Full RAG (retrieve + generate)
```
