# Pre-Chunking vs Post-Chunking and Context Windows

---

## Part 1: Pre-Chunking vs Post-Chunking

Most people only know one way to chunk. There are actually two distinct approaches.

---

### Pre-Chunking (Standard Approach)

**How it works:**
1. Documents are chunked **before** being stored in the vector database
2. All chunks are embedded and indexed upfront
3. At query time, the retriever searches the pre-built index
4. Fast retrieval because all work is already done

```
Ingest time:
Document → Chunk → Embed → Store in Vector DB (indexed)

Query time:
Query → Embed query → Search index → Return top-k chunks
```

**Pros:**
- Fast query-time retrieval
- Predictable index size
- Works with any vector database
- Easiest to implement

**Cons:**
- Chunking decisions are baked in upfront
- Wrong chunk boundaries are costly to fix (reprocess all docs)
- Static — can't adapt to different query types

**Used by:** Almost all RAG tutorials, LangChain defaults, most production setups.

---

### Post-Chunking (Advanced Alternative)

**How it works:**
1. Entire documents are embedded first (as-is)
2. At query time: find relevant documents via document-level embedding
3. Only **then** chunk those retrieved documents
4. Chunks are cached for future queries

```
Ingest time:
Document → Embed whole document → Store in Vector DB

Query time:
Query → Find relevant documents → Chunk those documents → Return chunks
First access: slow (chunk on the fly)
Subsequent: fast (cached chunks)
```

**Pros:**
- Only chunks documents that are actually queried
- More dynamic — chunking can adapt to query context
- Avoids processing irrelevant documents
- Chunk strategy can vary per query

**Cons:**
- Higher latency on first access
- Requires additional caching infrastructure
- More complex to build and maintain

**Used by:** Weaviate's Elysia agentic framework, advanced production systems.

---

### When to Use Which

| Scenario | Recommendation |
|---|---|
| Learning and prototyping | Pre-chunking |
| Most production RAG systems | Pre-chunking |
| Large corpus, only small % queried | Post-chunking |
| Need adaptive chunking per query | Post-chunking |
| Latency-critical first response | Pre-chunking |
| Agent memory systems | Post-chunking or hybrid |

---

## Part 2: Context Windows — Everything You Need to Know

---

### What a Context Window Is

A context window is the **maximum number of tokens** an AI model can process in a single input.

Tokens are not the same as words:
- English average: ~1 token per 0.75 words
- "tokenization" = 3 tokens
- 100 words ≈ 133 tokens (rough estimate)

Every model has two separate context window limits:

| Limit | What it constrains |
|---|---|
| **Embedding model context window** | Maximum chunk size you can embed |
| **LLM context window** | Maximum total context (query + retrieved chunks) you can send |

---

### Embedding Model Context Windows

| Embedding Model | Context Window | Notes |
|---|---|---|
| `all-MiniLM-L6-v2` (HuggingFace) | 256 tokens | Fast, free, local |
| `all-mpnet-base-v2` (HuggingFace) | 384 tokens | Better quality |
| `BAAI/bge-small-en-v1.5` | 512 tokens | Good free alternative |
| `text-embedding-ada-002` (OpenAI) | 8191 tokens | Paid, excellent quality |
| `text-embedding-3-small` (OpenAI) | 8191 tokens | Paid, lower cost |
| `text-embedding-3-large` (OpenAI) | 8191 tokens | Paid, highest quality |
| `jina-embeddings-v2-base-en` | 8192 tokens | Supports late chunking |

**Critical rule**: Your chunk size must be smaller than your embedding model's context window.

If you use `all-MiniLM-L6-v2` (256 tokens max) and set chunk_size=1000 → the embedding model truncates to 256 tokens. You lose 74% of the chunk content silently.

---

### LLM Context Windows

| LLM | Context Window | Notes |
|---|---|---|
| GPT-3.5-turbo | 16,385 tokens | Smaller context |
| GPT-4 | 8,192 tokens | Standard |
| GPT-4-turbo | 128,000 tokens | Large context |
| GPT-4o | 128,000 tokens | Large context |
| Claude 3 Haiku | 200,000 tokens | Very large |
| Claude 3.5 Sonnet | 200,000 tokens | Very large |
| Llama 3.1 70B | 128,000 tokens | Open source |
| Gemini 1.5 Pro | 1,000,000 tokens | Experimental |

**What this means for RAG:**
The total tokens you send to the LLM = system prompt + original query + all retrieved chunks.  
Your retrieved chunks must fit within this budget.

If you retrieve top-5 chunks × 500 tokens each = 2,500 tokens for context.  
Plus 500 tokens for system prompt and query = 3,000 tokens total.  
This fits comfortably even in GPT-4 (8,192 tokens).

---

### Aligning Chunk Size with Embedding Model

Practical guidelines:

| Embedding Model | Safe Chunk Size | Why |
|---|---|---|
| `all-MiniLM-L6-v2` | 200–250 tokens | 256 token limit |
| `BAAI/bge-small-en-v1.5` | 350–450 tokens | 512 token limit |
| `text-embedding-3-small` | 500–1500 tokens | 8191 token limit |
| `text-embedding-3-large` | 500–2000 tokens | 8191 token limit |

**Always leave a 10–20% buffer** below the model's max to account for tokenizer variations.

---

### The Lost in the Middle Problem — Explained

Research by Liu et al. (2023) showed a clear pattern in LLM attention:

```
Position in context:
Beginning ████████████ (strong attention)
Middle    ▓▓▓▓         (weak attention — information gets LOST here)
End       ████████████ (strong attention)
```

When you pass a long context to an LLM:
- It reads the beginning well
- It reads the end well
- Content in the middle is often missed or underweighted

**Implication for RAG:**
- Do not pass 20 retrieved chunks hoping the LLM will find the right one
- Pass 3–7 focused, highly relevant chunks
- The most critical chunk should be first or last in your context assembly

**Mitigation strategies:**
1. Retrieve fewer, higher-quality chunks (better chunking helps here)
2. Use reranking to select the best 3–5 from top-10
3. Put the most important chunk first
4. Use models with better long-context handling (Claude, Gemini)

---

### Context Budget Planning

A practical way to plan your RAG context allocation:

```
Total LLM context budget: 8,192 tokens (GPT-4 standard)

Allocation:
- System prompt:        400 tokens
- User query:           100 tokens
- Retrieved context:  5,000 tokens  (your main budget)
- Safety buffer:        500 tokens
- LLM response space: 2,192 tokens

Context budget for chunks: 5,000 tokens
Chunk size: 500 tokens
Maximum chunks to retrieve: 10 (but 5–7 is more practical)
```

**Rule**: Never use more than 60–70% of the LLM's context window for retrieved content. Leave room for the prompt, query, and response.

---

### Do Long-Context LLMs Make Chunking Unnecessary?

Short answer: **No.**

Even with 200k token windows (Claude) or 1M tokens (Gemini):

1. **Cost** — larger context = higher cost per query
2. **Latency** — larger context = slower response
3. **Lost in the middle** — still present, just harder to notice
4. **Precision** — dumping everything in context is less precise than targeted retrieval
5. **Maintainability** — you still need structured, clean chunks for citation and filtering

Chunking remains the right approach even with massive context windows.  
The window size changes the ceiling, not the strategy.
