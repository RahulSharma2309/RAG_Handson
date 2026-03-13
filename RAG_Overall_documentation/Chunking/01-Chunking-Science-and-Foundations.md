# Chunking Science and Foundations

> This is where chunking begins. Everything you read here is the foundation for every decision you make later — chunk size, strategy, library, overlap, metadata.

---

## 1) What Chunking Actually Is

Chunking is the process of breaking down large documents into smaller, meaningful units called **chunks** before storing them in a vector database.

In RAG, the retriever does not pull the "whole document". It pulls **chunks**.  
Chunk boundaries directly influence answer quality. This is not a formatting detail — it is a retrieval architecture decision.

---

## 2) Why Chunking Exists: Two Forcing Conditions

There are two hard technical reasons why chunking is non-negotiable:

### Reason 1: Embedding model context windows
Every embedding model has a **context window** — a maximum number of tokens it can process into one vector.

If you exceed this, the excess tokens are truncated (dropped) before embedding.  
This means important context is permanently lost from that chunk's vector representation.

| Embedding Model | Max Context Window |
|---|---|
| `all-MiniLM-L6-v2` | 256 tokens |
| `text-embedding-ada-002` (OpenAI) | 8191 tokens |
| `text-embedding-3-small` (OpenAI) | 8191 tokens |
| `llama-text-embed-v2` | 1024 tokens |
| `BAAI/bge-small-en-v1.5` | 512 tokens |

Your chunks must fit within the model's context window — or content is silently lost.

### Reason 2: Chunks must contain useful, retrievable information
Right-sizing is not enough. The chunk itself must be **semantically useful**.

A chunk that contains unconnected sentences — or half of an argument — may not surface when the retriever compares it to a query vector.  
It must make sense on its own.

---

## 3) The Chunking Sweet Spot

A good chunk is:
- **Large enough** to contain a complete, meaningful idea
- **Small enough** to be precisely retrieved and focused

The most important test:

> If a chunk of text makes sense to a human when read alone — without surrounding context — it will make sense to the LLM too.

If it does not pass that test, it is a bad chunk.

---

## 4) What Happens When Chunks Are Wrong

### Chunks too large
- Multiple ideas mixed together
- Embedding becomes "averaged" meaning — diluted
- Retrieval is noisy, surfaces broad or irrelevant content
- LLM "lost in the middle" problem kicks in

### Chunks too small
- Context is missing
- Embedding captures narrow, isolated meaning
- Answers become incomplete
- Model may hallucinate the missing connections

### Chunk boundaries in wrong places
- Heading in one chunk, explanation in the next
- Rule in one chunk, exception clause in the next
- Command in one chunk, prerequisites in the next
- Retrieval misses the full picture

---

## 5) The "Lost in the Middle" Problem

This is a well-documented LLM failure mode.

When a long context is passed to an LLM, it:
- Handles the beginning well
- Handles the end well
- **Loses track of information buried in the middle**

This has two implications for chunking:

1. Keep chunks focused — do not stuff multiple topics into one giant chunk
2. When you retrieve top-k chunks, the ordering matters

Even modern large-context LLMs (200k token windows like Claude or o1) suffer from this.  
Chunking is still necessary because **relevance filtering matters more than fitting everything into context**.

---

## 6) Relationship Between Chunking and Embeddings

Embeddings represent **semantic meaning** as a vector.

If a chunk contains mixed topics, its embedding is an average of those topics' meanings.  
That average does not strongly represent any single idea.

Example:
- Chunk text: "Leave policy. Expense reimbursement. Holiday calendar."
- Query: "What is the leave policy?"
- Result: Retrieved chunk contains leave policy + unrelated info → noisy answer

Better chunking:
- Chunk 1: Only leave policy rules
- Chunk 2: Only expense reimbursement
- Chunk 3: Holiday calendar

Each embedding now strongly represents one idea → precise retrieval.

---

## 7) The Quality Chain

RAG answer quality flows through this chain:

```
Source quality
     ↓
Chunk quality
     ↓
Embedding quality
     ↓
Retrieval quality
     ↓
Answer quality
```

If chunk quality is weak, even the best embedding model, vector database, and LLM cannot fully fix it.

---

## 8) The Four Levers of Chunk Design

### A. Chunk size
- Unit: characters, tokens, or sentences
- Typical range: 250–600 tokens for most docs
- Smaller = more precise retrieval, less context
- Larger = more context, less precise retrieval
- Choose based on document density and question granularity

### B. Chunk overlap
- Usually 10–20% of chunk size
- Preserves context at chunk boundaries
- Prevents important content from being split at an edge and missed
- Too high overlap → duplicate/noisy chunks

### C. Split boundaries
- **Prefer semantic boundaries first**: headings, paragraphs, sections
- **Use token windows only** when semantic splits are still too large
- Never split blindly mid-sentence or mid-code-block

### D. Metadata
- Source file, section title, page number, document family, version, date
- Enables retrieval filtering, source citation, and debugging
- More metadata = better retrieval control

---

## 9) Does Your Data Even Need Chunking?

This is the first question to ask.

**Data that probably does NOT need chunking:**
- FAQs (each item is already small and complete)
- Product descriptions (short, self-contained)
- Social media posts (sentence-level)
- Pre-structured Q&A pairs

**Data that DOES need chunking:**
- Research papers
- Policy documents
- Technical architecture docs
- Annual reports
- Runbooks and deployment guides
- Books, manuals, regulatory filings

If your documents are already small, focused, and self-contained — chunking can actually hurt retrieval by splitting what is already a good unit.

---

## 10) Chunking's Role in Agentic Applications

In agent-based systems, retrieved chunks function as **agent memory**.

An agent needs to:
- Recall relevant information to make tool calls
- Reason over factual context
- Ground its responses in trusted sources

If chunks are poorly formed:
- The agent gets incomplete context
- It wastes tokens generating hallucinations
- It may call the wrong tools or take wrong actions

Well-formed chunks = reliable agent memory.

---

## 11) Practical Baseline Defaults (Start Here)

These are starting points — not final answers. Tune with retrieval evaluation.

| Document Type | Chunk Size | Overlap |
|---|---|---|
| Narrative / functional docs | 400–550 tokens | 60–90 tokens |
| Technical / operational docs | 320–480 tokens | 70–110 tokens |
| PDFs (clean text) | 300–450 tokens | 50–80 tokens |
| CSV rows | Per-row + grouped summaries | N/A |
| Code files | Per function/class | 10–20 lines |
| Short structured docs | No chunking needed | — |

---

## 12) Final Mental Model

Chunking is not formatting.  
It is the first and most impactful retrieval architecture decision you make.

Get it right, and everything downstream improves.  
Get it wrong, and no amount of model power will fully compensate.
