# What is RAG? — A Complete Beginner's Guide

> If you have never heard the word "RAG" before, start here.
> If you have heard it but it still feels fuzzy, start here.
> This document explains everything from zero — no assumptions, no jargon without explanation.

---

## The Problem RAG Solves

Before understanding RAG, you need to understand the problem it fixes.

### What is a Large Language Model (LLM)?

An LLM is an AI that has read an enormous amount of text — books, articles, websites, code — and learned patterns from all of it. When you ask it a question, it generates an answer based on everything it has ever read.

Examples: GPT-4, Llama, Gemini, Claude, Qwen.

### The fundamental limitation of LLMs

An LLM is trained once and then frozen. Its knowledge has a **cutoff date**. It knows nothing that happened after it was trained. More importantly for most businesses:

> **An LLM has never read YOUR documents.**

It does not know:
- Your company's internal processes
- Your product documentation
- Your team's decisions from last sprint
- Your Kubernetes setup
- Your API architecture

If you ask GPT-4 "What is our CI/CD pipeline?", it cannot answer from your actual pipeline — it will either say "I don't know" or worse, make something up that sounds plausible.

This problem of making up plausible-sounding wrong answers is called **hallucination**.

### The naive solution people try first — and why it fails

**Option 1: Paste your documents into the chat**
You could copy-paste your entire documentation into the prompt. This has limits:
- LLMs can only read a certain amount of text at once (called the **context window**)
- Pasting 100 documents exceeds this limit
- Even if it fits, the LLM struggles to find relevant information in a giant wall of text
- Cost: you pay per word sent — sending 100 documents every time is expensive

**Option 2: Fine-tune the LLM on your documents**
Retrain the model to "learn" your documents. Problems:
- Extremely expensive (thousands of dollars of GPU time)
- Takes days or weeks
- Every time docs change, you must retrain
- Still prone to hallucination — the model blends your data with its prior training

---

## What RAG Does — The Core Idea

RAG stands for **Retrieval-Augmented Generation**.

Break that into three words:
- **Retrieval** — find the relevant information
- **Augmented** — add that information to the question
- **Generation** — have the LLM generate an answer using that information

In one sentence:
> **Before asking the LLM your question, first find the relevant pages from your documents, then give the LLM only those pages to read.**

### The open book exam analogy

Think of the difference between:

**Closed book exam (standard LLM):**
The student must answer from memory. Smart students do well on general knowledge. Nobody can answer questions about your specific company policies from memory.

**Open book exam (RAG):**
The student can use the textbook. But there is one rule: the textbook has 10,000 pages and you can only bring 5 pages to the exam. You must first find the right 5 pages (retrieval), then answer using those pages (generation).

RAG is an open book exam system. The retrieval step finds the right pages. The generation step uses them to write the answer.

### The librarian and consultant analogy

Imagine you hire a consultant to answer questions about your company:

**Without RAG:**
The consultant answers from general business knowledge. Accurate for general topics, wrong for your specifics.

**With RAG:**
1. You have a librarian (the retrieval system) who knows your entire document library
2. A user asks a question
3. The librarian instantly finds the 3-5 most relevant documents from your library
4. The consultant reads only those documents and writes the answer
5. The answer is specific, grounded, and traceable to your actual documents

---

## The 5 Steps of a RAG System

Every RAG system — from a basic prototype to a production enterprise deployment — follows these same five steps. The tools and complexity differ, but the steps are universal.

```
Step 1: Document Preparation    →   Load and clean your source documents
Step 2: Chunking                →   Split documents into searchable pieces
Step 3: Embedding               →   Convert pieces into numbers (vectors)
Step 4: Retrieval               →   Find the most relevant pieces for a query
Step 5: Generation              →   Use an LLM to answer using retrieved pieces
```

Let us walk through each step in detail.

---

## Step 1: Document Preparation

### What happens here

You take your raw documents — PDFs, Word files, Markdown files, web pages, databases — and load them into a format your system can process.

In this project: 89 Markdown files in `rag/input_docs/`

### What a "document" looks like in code

After loading, every document becomes a structured object:
```
Document:
  page_content: "This is the full text of the document..."
  metadata:
    source: "path/to/file.md"
    page: 1
```

The `page_content` is the text. The `metadata` is contextual information about where the text came from.

### Why metadata matters

When the system retrieves a chunk and the LLM uses it to answer, you need to know where that answer came from. Metadata provides the citation. Without it, you cannot trust the answer — there is no way to verify it.

---

## Step 2: Chunking

### What happens here

A 10-page document cannot be searched effectively as one unit. You need to break it into smaller, focused pieces so that a specific question finds the specific piece that answers it.

**Chunking** is the process of splitting documents into these smaller pieces.

### Why you cannot skip chunking

Imagine a document with three sections:
- Section A: What is Docker?
- Section B: How to write a Dockerfile?
- Section C: Docker networking?

If you embed the whole document as one vector, the vector represents the average meaning of all three sections. A question about "Dockerfile syntax" would score moderately on this one vector — it is relevant but muddled.

If you split into three chunks, the question about Dockerfile syntax would score very high against Section B and lower against A and C. Precise retrieval.

### The key parameters

**Chunk size:** How big is each piece? Measured in characters or tokens.
- Too small: chunks lose context (a sentence without surrounding paragraphs is ambiguous)
- Too large: chunks are unfocused (the vector represents too many topics)
- Sweet spot: 150–500 tokens for most use cases

**Chunk overlap:** How much do consecutive chunks share?
- Without overlap: important context at a chunk boundary is cut off
- With 50-token overlap: each chunk shares 50 tokens with the previous, preserving boundary context

**Splitting strategy:** How do you decide where to split?
- At fixed character count (simple but may cut mid-sentence)
- At paragraph/sentence boundaries (smarter, meaning-preserving)
- At document headings (best for structured docs like Markdown)

In this project: We split at heading level 2 (`##`) and then by paragraphs. Each document type (product docs, ops docs, etc.) has its own tuned settings.

---

## Step 3: Embedding

### What happens here

Every chunk of text is converted into a list of numbers called a **vector** or **embedding**. These numbers encode the meaning of the text mathematically.

### The core insight

Two pieces of text with similar meaning will produce vectors that are close together in mathematical space. Two pieces with different meaning will be far apart.

This allows meaning-based search rather than keyword search.

### An analogy — GPS coordinates for meaning

Think of every chunk as a location on a globe. When you embed a chunk, you get its GPS coordinates (latitude + longitude + altitude + 381 more dimensions). When you ask a question, you get the GPS coordinates of that question. Finding relevant chunks = finding the locations closest to your question's coordinates.

### What a vector looks like

```python
"Deep learning uses neural networks"
→ [-0.0604, -0.0673, 0.0254, -0.0268, -0.0300, ... (384 numbers total)]

"Neural networks are the basis of deep learning"
→ [-0.0589, -0.0651, 0.0241, -0.0259, -0.0288, ... (very similar numbers)]

"How to make pasta"
→ [0.1234, 0.5678, -0.2345, ... (very different numbers)]
```

### Where embeddings come from — the embedding model

An embedding model is a neural network trained specifically to map text to vectors. Different models produce different vector sizes (dimensions) and have different quality levels.

In this project: `sentence-transformers/all-MiniLM-L6-v2` — free, runs on CPU, produces 384-dimensional vectors.

---

## Step 4: Retrieval (Vector Search)

### What happens here

A user asks a question. The question is also converted into a vector using the same embedding model. Then you search through all stored chunk vectors to find the ones closest to the question vector.

```
User: "How does the CI/CD pipeline work?"
        ↓ embed
Query vector: [-0.02, 0.15, -0.08, ...]
        ↓ search 979 stored vectors
Top matches: CI_CD_INTEGRATION.md (score: 0.57), DOCKER_COMMANDS.md (score: 0.52)
```

### Why "similarity" is not just keyword matching

Keyword search: finds documents that contain the exact words "CI/CD pipeline"
Vector search: finds documents that are *about* the concept of CI/CD pipelines, even if they use words like "continuous integration", "deployment automation", or "GitHub Actions"

This is why RAG retrieval is semantic — it understands meaning.

### What a vector store is

The place where you store all the chunk vectors so you can search them quickly. This is called a **vector store** or **vector index**.

Think of it as a special kind of database optimised for finding the closest numbers rather than exact matches.

---

## Step 5: Generation

### What happens here

The retrieved chunks are assembled into a **context block** and combined with the user's question into a **prompt**. This prompt is sent to an LLM, which reads the context and generates a human-readable answer.

```
PROMPT =
  "Here is some context from our documentation:
   [chunk 1 text]
   [chunk 2 text]
   [chunk 3 text]

   Using only the above context, answer this question:
   How does the CI/CD pipeline work?"

LLM reads prompt → generates answer → you receive it
```

### The grounding constraint — the most important line

Notice "**using only the above context**". This instruction constrains the LLM to your documents. Without this, the LLM mixes your documents with its own training data, leading to answers that sound right but are actually from a different company's setup.

With this constraint: if the answer is not in the retrieved chunks, the LLM says "I don't have enough information" instead of making something up.

---

## The Full RAG Loop — End to End

```
                 [BUILD PHASE — done once]
Source docs (.md, .pdf, .txt)
       ↓  Document loader
Text in memory
       ↓  Chunker
979 text chunks with metadata
       ↓  Embedding model
979 × 384 number vectors
       ↓  Vector store
faiss_index.bin + metadata.jsonl
                       ↑
               [QUERY PHASE — done on every question]
                       ↑
User question: "How does CI/CD work?"
       ↓  Same embedding model
Query vector (1 × 384 numbers)
       ↓  Vector search
Top 4 most relevant chunks
       ↓  Prompt builder
"Context: [chunks]\nQuestion: [user question]"
       ↓  LLM (Ollama / OpenAI / Groq)
"CI/CD in this system works by..."
       ↓
Answer shown to user (with sources cited)
```

---

## Why RAG beats the alternatives

| Approach | Cost | Accuracy | Freshness | Complexity |
|---|---|---|---|---|
| Ask LLM directly | Low | Low (hallucination) | Outdated | Simple |
| Paste docs in prompt | High (pay per token) | Medium | Fresh | Simple |
| Fine-tune LLM | Very high ($1000s) | Medium | Stale after training | Very complex |
| **RAG** | **Low** | **High (grounded)** | **Always fresh** | **Moderate** |

---

## What This Project Built

By the end of working through this workspace you will have:

1. **89 source documents** covering a real software project (architecture, CI/CD, Kubernetes, product owner guides)
2. **979 chunks** split intelligently by document type
3. **A FAISS vector index** — 979 × 384 vectors, searchable in milliseconds
4. **A CLI tool** (`ask_rag.py`) — ask questions from the terminal, get answers from your docs
5. **A chat UI** (`app.py`) — browser-based chat powered by your own knowledge base
6. **A ChromaDB notebook** — hands-on exploration of vector storage
7. **Full documentation** — this series of guides

All of this runs **100% locally** on your machine. No cloud. No API keys. No cost.

---

## The next documents to read

Now that you understand what RAG is, the next document explains every tool and option available at each step — free vs paid, simple vs advanced:

→ `tools-and-options-at-every-step.md`
