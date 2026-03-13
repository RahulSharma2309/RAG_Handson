# Pre-Chunking vs Post-Chunking and Context Windows

> This document builds directly on the foundations. You now know what chunking is, why boundaries matter, and what tokens are. Here you will understand the two strategies for when chunking happens in the pipeline — and everything you need to know about context windows so that you never accidentally lose data silently.

---

## Part 1: Pre-Chunking vs Post-Chunking

Most people only know one way to chunk. There are actually two fundamentally different approaches — and understanding both helps you design smarter RAG systems.

---

### The Core Difference in One Line

**Pre-chunking:** Split documents first, then store the chunks.  
**Post-chunking:** Store documents first, then split only when someone actually asks a question.

---

### Pre-Chunking — The Standard Approach

This is what almost every RAG tutorial shows you. It is what LangChain assumes by default.

**How it works — step by step:**

```
INGEST TIME (happens once, before any user queries):

Raw Document
     ↓
Split into Chunks  ← chunking happens HERE
     ↓
Embed each chunk
     ↓
Store vectors + chunks in Vector DB (fully indexed and ready)

─────────────────────────────────────────────────────────────

QUERY TIME (happens every time a user asks a question):

User Query
     ↓
Embed the query
     ↓
Search Vector DB (index already built → very fast)
     ↓
Return top-k matching chunks
     ↓
LLM generates answer
```

**Real example:**

You have 10,000 company policy documents. You ingest them all once:
- Each document is split into chunks
- Each chunk is embedded
- 50,000 chunks are now stored and indexed in your vector database

When an employee asks *"What is the leave policy for contract employees?"* — the retriever searches those 50,000 pre-built vectors in milliseconds and returns the right 3–5 chunks.

The entire search happens fast because all the heavy processing (chunking + embedding) was done upfront at ingest time, not at query time.

---

**Pros:**

- Fast query-time retrieval — all vectors are pre-built and indexed
- Predictable — index size and structure are known before deployment
- Simple to implement — works with every vector database
- Suitable for production — used by almost all enterprise RAG systems

**Cons:**

- Chunking decisions are locked in at ingest time
- If your chunk boundaries are wrong, you must reprocess all documents to fix them
- Static — the same chunk is returned regardless of what kind of question was asked
- Not efficient if you have millions of documents but only a tiny fraction are ever queried

---

### Post-Chunking — The Advanced Alternative

Post-chunking flips the order. Documents are stored whole first. Chunking only happens at query time, for documents that are actually retrieved.

**How it works — step by step:**

```
INGEST TIME (happens once):

Raw Document
     ↓
Embed the WHOLE document (no chunking yet)
     ↓
Store whole-document vector in Vector DB

─────────────────────────────────────────────────────────────

QUERY TIME — First Access (slow):

User Query
     ↓
Embed the query
     ↓
Search Vector DB → Find relevant DOCUMENTS (not chunks yet)
     ↓
Retrieve those documents
     ↓
Chunk them NOW (on the fly)  ← chunking happens HERE
     ↓
Embed and return the relevant chunks
     ↓
Cache the chunks for future queries

─────────────────────────────────────────────────────────────

QUERY TIME — Subsequent Access (fast, served from cache):

User Query
     ↓
Search Vector DB
     ↓
Retrieve cached chunks
     ↓
Return to LLM
```

**Real example:**

Imagine a law firm with 100,000 contracts. Most contracts are never retrieved — only the active ones matter. With pre-chunking, you would chunk and embed all 100,000 contracts upfront — a massive, expensive operation.

With post-chunking:
- Store document-level vectors for all 100,000 contracts (fast, cheap)
- When a lawyer asks about a specific contract, retrieve that document
- Chunk it on the fly for that specific query
- Cache those chunks
- Next time someone asks about the same contract → serve from cache instantly

You only paid the chunking cost for contracts that were actually queried.

---

**Pros:**

- Only processes documents that are actually used — saves compute and cost
- Chunking strategy can adapt per query — different question types can trigger different chunking approaches
- Good for very large document sets with sparse query patterns

**Cons:**

- First query on any document is slow (chunking + embedding happens live)
- Requires a caching layer — more infrastructure to build and maintain
- More complex to implement correctly
- Not suitable when fast first-response latency is critical

**Used by:** Weaviate's Elysia agentic RAG framework, advanced production agent systems.

---

### Side-by-Side Comparison

```
                  Pre-Chunking          Post-Chunking
─────────────────────────────────────────────────────
Chunking happens  At ingest time        At query time
Query speed       Always fast           Slow first, fast after cache
Complexity        Low                   High
Flexibility       Fixed strategy        Adaptive per query
Best for          Most RAG systems      Large sparse document sets
Infra needed      Vector DB only        Vector DB + cache layer
Fixing bad chunks Reprocess all docs    Can change strategy anytime
```

---

### When to Use Which

| Your situation | Use |
|---|---|
| Learning RAG, building first system | Pre-chunking |
| Standard production RAG | Pre-chunking |
| 10M+ docs but only 5% ever queried | Post-chunking |
| Need different chunk sizes per query type | Post-chunking |
| Latency of first response is critical | Pre-chunking |
| Agent memory systems (documents recalled dynamically) | Post-chunking or hybrid |
| Small-medium document set (< 100k docs) | Pre-chunking |

**If you are starting out: always use pre-chunking.** It is simpler, faster to build, and works correctly for 95% of production use cases.

---

## Part 2: Context Windows — Everything You Need to Know

This is where most beginners make silent, hard-to-debug mistakes. Understanding context windows completely prevents an entire class of RAG failures.

---

### There Are Two Separate Context Windows

This is the most important thing to understand first.

**Every model in your RAG system has its own context window limit — and they serve different purposes.**

```
Model 1: Embedding Model
  Context window → limits how large each CHUNK can be
  Example: all-MiniLM-L6-v2 → max 256 tokens per chunk

Model 2: LLM (the answer generator)
  Context window → limits total input: system prompt + query + ALL retrieved chunks combined
  Example: GPT-4 → max 8,192 tokens total
```

You must design for BOTH limits.  
Violating either one causes silent failures or wrong answers.

---

### Context Window 1: The Embedding Model

#### What it is

When you send a chunk of text to an embedding model, it converts that text into a vector.  
The model can only convert a maximum number of tokens into that vector.  
Anything beyond that limit is **silently dropped**.

No error. No warning. The embedding just represents a truncated version of your text.

#### Why This Is Dangerous

Imagine this chunk:

```
Paragraph 1 (50 tokens):  "Kubernetes is an open-source container orchestration platform..."
Paragraph 2 (50 tokens):  "It was originally developed by Google..."
Paragraph 3 (50 tokens):  "Kubernetes automates deployment and scaling..."
Paragraph 4 (50 tokens):  "The scheduler assigns pods to nodes based on resource availability..."
Paragraph 5 (50 tokens):  "Kubernetes was adopted by the CNCF in 2016 and has become the industry standard."
─────────────────────────────────────────────────────────────────────────────────────────
Total: 250 tokens
Model limit (all-MiniLM-L6-v2): 256 tokens → Safe ✅
```

Now imagine you increase your chunk size slightly:

```
Paragraph 1 (60 tokens):  "Kubernetes is an open-source container orchestration platform..."
Paragraph 2 (60 tokens):  "It was originally developed by Google..."
Paragraph 3 (60 tokens):  "Kubernetes automates deployment and scaling..."
Paragraph 4 (60 tokens):  "The scheduler assigns pods to nodes based on resource availability..."
Paragraph 5 (60 tokens):  "Kubernetes was adopted by the CNCF in 2016 and has become the industry standard."
─────────────────────────────────────────────────────────────────────────────────────────
Total: 300 tokens
Model limit: 256 tokens → TRUNCATED ❌
```

What happens:

```
Token 1   ✅ included in embedding
Token 2   ✅ included
...
Token 256 ✅ included  ← embedding model stops HERE
Token 257 ❌ dropped
Token 258 ❌ dropped
...
Token 300 ❌ dropped
```

Paragraph 5 is either partially or fully gone from the vector.  
If a user asks *"When did Kubernetes join the CNCF?"* — the answer was in Paragraph 5.  
The vector does not represent that fact. The retriever will not find this chunk for that query.

**The worst part: you get no warning. The embedding model just silently ignores the extra tokens.**

---

#### Real Numbers — How Much Do You Lose?

If you use `all-MiniLM-L6-v2` (256 token limit) and set `chunk_size=1000` characters:

```
1000 characters ≈ 200 words ≈ 267 tokens (rough estimate)

267 tokens in, 256 token limit → 11 tokens dropped → ~4% loss
```

But if you set `chunk_size=3000` characters:

```
3000 characters ≈ 600 words ≈ 800 tokens

800 tokens in, 256 token limit → 544 tokens dropped → 68% loss
```

You embedded only 32% of your chunk. The vector represents a fragment. Retrieval is broken.

---

#### The Buffer Rule

Always stay 15–20% below the embedding model's maximum:

```
Model limit = 256 tokens
Buffer (20%) = 51 tokens
Safe maximum = 205 tokens

In LangChain character terms:
205 tokens × 0.75 words/token × 5 chars/word ≈ 770 characters

Safe setting: chunk_size ≈ 700–800 characters for all-MiniLM-L6-v2
```

Why the buffer? Because tokenizers are inconsistent. Technical words, URLs, code snippets, and special characters all tokenize to more tokens than regular English prose. The buffer absorbs that variation.

---

#### Embedding Model Reference Table

| Model | Context Window | Safe Chunk Size | Cost |
|---|---|---|---|
| `all-MiniLM-L6-v2` | 256 tokens | 150–200 tokens / ~700 chars | Free |
| `all-mpnet-base-v2` | 384 tokens | 300–330 tokens / ~1200 chars | Free |
| `BAAI/bge-small-en-v1.5` | 512 tokens | 400–440 tokens / ~1600 chars | Free |
| `llama-text-embed-v2` | 1024 tokens | 800–870 tokens / ~3200 chars | Free/Paid |
| `text-embedding-ada-002` (OpenAI) | 8191 tokens | 1000–6000 tokens | Paid |
| `text-embedding-3-small` (OpenAI) | 8191 tokens | 1000–6000 tokens | Paid (cheaper) |
| `text-embedding-3-large` (OpenAI) | 8191 tokens | 1000–6000 tokens | Paid (best quality) |
| `jina-embeddings-v2-base-en` | 8192 tokens | 1000–6000 tokens | Free |

**The free models have much smaller context windows — this is the most common source of silent truncation bugs in beginner RAG projects.**

---

### Context Window 2: The LLM

#### What it is

When you send a request to an LLM (GPT-4, Claude, Llama), the total input has a maximum token limit.

**Total input = system prompt + user query + all retrieved chunks combined**

If this total exceeds the LLM's context window, the model either:
- Refuses to process the request (error)
- Silently truncates the beginning of the input (losing your system prompt or early chunks)

Both outcomes break your RAG system.

---

#### Why This Matters for Chunk Count

Each retrieved chunk consumes tokens from your LLM budget.

Example calculation:

```
You retrieve top-5 chunks
Each chunk = 800 tokens
Total chunk tokens = 5 × 800 = 4,000 tokens

System prompt = 500 tokens
User query = 150 tokens
─────────────────────────
Total sent to LLM = 4,650 tokens
```

GPT-4 limit = 8,192 tokens → 4,650 fits comfortably ✅  
GPT-3.5-turbo limit = 4,096 tokens → 4,650 **does NOT fit** ❌

The model would error or truncate your chunks — and you might not immediately notice because the LLM still generates *something*.

---

#### LLM Context Window Reference Table

| LLM | Context Window | What It Means for RAG |
|---|---|---|
| GPT-3.5-turbo | 16,385 tokens | Can handle ~25 × 500-token chunks |
| GPT-4 | 8,192 tokens | Can handle ~12 × 500-token chunks |
| GPT-4-turbo | 128,000 tokens | Can handle ~200 × 500-token chunks |
| GPT-4o | 128,000 tokens | Same as GPT-4-turbo |
| Claude 3 Haiku | 200,000 tokens | Very large — but cost scales with size |
| Claude 3.5 Sonnet | 200,000 tokens | Most capable Claude model |
| Llama 3.1 70B | 128,000 tokens | Open source, self-hosted |
| Gemini 1.5 Pro | 1,000,000 tokens | Experimental — not practical for most use cases |

---

### Aligning Both Context Windows

Here is how both limits interact in a real RAG system:

```
Step 1: Choose your embedding model
  → This sets your MAXIMUM CHUNK SIZE
  
Step 2: Choose your LLM
  → This sets your MAXIMUM TOTAL CONTEXT (prompt + query + all chunks)
  
Step 3: Choose chunk size
  → Must be below embedding model limit
  → Chunk size × number of chunks retrieved must be below LLM context limit
  
Step 4: Choose how many chunks to retrieve (top-k)
  → chunk_size × top-k + prompt + query ≤ LLM context window
```

**Concrete example — Free tier setup:**

```
Embedding model: all-MiniLM-L6-v2 (256 token limit)
→ Safe chunk size: 200 tokens

LLM: GPT-4 (8,192 token limit)
→ Budget: 8,192 - 500 (prompt) - 150 (query) - 500 (buffer) = 7,042 tokens for chunks
→ Max chunks: 7,042 ÷ 200 = 35 chunks (but 5–7 is the practical sweet spot)
```

**Concrete example — Production setup:**

```
Embedding model: text-embedding-3-small (8,191 token limit)
→ Safe chunk size: 500 tokens

LLM: GPT-4-turbo (128,000 token limit)
→ Budget: 128,000 - 500 (prompt) - 150 (query) - 1,000 (buffer) = 126,350 tokens for chunks
→ Max chunks: 126,350 ÷ 500 = 252 chunks (but still only retrieve 5–10 for quality)
```

Just because the context window allows 252 chunks does not mean you should send 252 chunks.  
Sending too many chunks leads directly to the **Lost in the Middle problem**.

---

### Context Budget Planning — Step by Step

Here is how to plan your context budget before writing any code:

**Step 1:** Know your LLM's context window

```
LLM: GPT-4
Context window: 8,192 tokens
```

**Step 2:** Reserve space for the prompt and query

```
System prompt (instructions to the LLM): ~400 tokens
User query (the question): ~100 tokens
─────────────────────────────────────────
Reserved: 500 tokens
```

**Step 3:** Reserve space for the LLM's response

```
Typical answer length: ~500–800 tokens
Reserve: 1,000 tokens (safe buffer)
```

**Step 4:** Calculate remaining budget for retrieved chunks

```
Total budget:           8,192 tokens
- Prompt + query:         500 tokens
- Response space:       1,000 tokens
- Safety buffer:          200 tokens
────────────────────────────────────
Remaining for chunks:   6,492 tokens
```

**Step 5:** Calculate how many chunks you can retrieve

```
Chunk size: 500 tokens
Max chunks: 6,492 ÷ 500 = 12 chunks

Practical recommendation: retrieve top-10, rerank, pass top-5
(Better quality with fewer, more focused chunks)
```

**Final rule:**  
Never use more than 60–70% of the LLM's context window for retrieved content.  
Always leave room for the prompt, the query, and the LLM's response.

---

### What Happens When You Overshoot the LLM Context Window

**Scenario:** You retrieve 20 chunks × 600 tokens = 12,000 tokens of context.  
System prompt = 500 tokens. Query = 100 tokens. Total = 12,600 tokens.  
LLM: GPT-4 with 8,192 token limit.

```
12,600 > 8,192 → OVERFLOW
```

The API throws a `context_length_exceeded` error — your application crashes.

OR — depending on implementation — the model silently truncates the beginning of the input.  
Your system prompt disappears. The LLM no longer knows its role, tone, or instructions.  
It still generates an answer — but now it's answering without its context, behaving unpredictably.

**This is why context budget planning must be done before building, not after debugging.**

---

### Do Long-Context LLMs Make Chunking Unnecessary?

This is a common question when developers discover that Claude supports 200,000 tokens or Gemini supports 1,000,000 tokens.

*"If I can send the entire document in one request — why chunk at all?"*

**Short answer: No. Chunking is still necessary and still the right approach.**

Here is why, with real reasoning:

---

#### Reason 1: Cost scales with context size

LLM API pricing is based on tokens processed.

```
GPT-4-turbo pricing (approximate):
  Input: $0.01 per 1,000 tokens
  Output: $0.03 per 1,000 tokens

Scenario A: Send full 50,000-token document per query
  Cost per query: 50,000 × $0.01 / 1,000 = $0.50 per query
  Cost for 1,000 queries per day: $500/day = $15,000/month

Scenario B: RAG with top-5 chunks × 500 tokens = 2,500 tokens per query
  Cost per query: 2,500 × $0.01 / 1,000 = $0.025 per query
  Cost for 1,000 queries per day: $25/day = $750/month
```

RAG is **20x cheaper** per query in this scenario.

---

#### Reason 2: Latency increases with context size

Larger context = longer processing time = slower response.

```
Approximate latency (rough estimates):
  2,500 token context  → ~1–2 seconds
  50,000 token context → ~10–20 seconds
  200,000 token context → ~60+ seconds
```

Users waiting 60 seconds for an answer is not acceptable in most applications.

---

#### Reason 3: The Lost in the Middle problem is real at any context size

Even with 200,000 token windows, the LLM still pays less attention to content buried in the middle.

Sending a 50,000-token document and asking one question means 49,900 tokens are irrelevant noise.  
The LLM has to sort through all of it. The relevant answer has a much lower chance of being seen clearly.

With RAG: you send only the 3–5 chunks that actually contain the answer.  
The relevant content is right at the front. The LLM has full attention on exactly what it needs.

---

#### Reason 4: Citations and filtering require metadata

If you dump the whole document into context, you lose the ability to:
- Tell the user exactly which section the answer came from
- Filter by document type, date, department, or version
- Debug why the answer is wrong

Chunking with metadata preserves all of this.

---

#### Reason 5: You still need structure for agent memory

In agentic AI systems, chunks become the units of memory that agents recall.  
Agents do not dump entire documents — they retrieve specific, relevant memory units.  
Without chunking, agent memory becomes unstructured and unreliable.

---

#### Summary

```
Large context windows are useful for:
  → Complex multi-step reasoning on a single document
  → Comparing two versions of a contract side by side
  → Edge cases where the full document is truly needed

Small chunks + RAG are better for:
  → Every repeated question-answering workload
  → Multi-document knowledge bases
  → Cost-sensitive production systems
  → Systems that need citations and source traceability
  → Agent memory architectures
```

The window size changes what is *possible*.  
Chunking + retrieval changes what is *practical and cost-effective*.

**These two approaches are complementary, not competing. For most RAG systems you build, chunking remains the right design.**
