# Chunk Size and Parameter Tuning Guide

> Chunk size is the parameter everyone changes first and understands last. Most people pick 512, run the system, notice something is off, change it to 256 or 1000, and hope for better results. That is not tuning — that is guessing. This guide gives you the science behind every parameter, shows you exactly what happens when you change each one, and gives you a structured process for finding the right values with evidence rather than intuition.

---

## The Three Parameters That Control Everything

Chunking has three core parameters. They interact with each other. Changing one without understanding the others produces unpredictable results.

### Parameter 1 — Chunk Size

`chunk_size` in LangChain is measured in **characters** by default, not tokens.

This is the most important thing to internalize:

```
LangChain chunk_size = 500  →  approximately 100–130 tokens
LangChain chunk_size = 2000 →  approximately 400–520 tokens

The exact token count depends on:
- How many words are in the text
- How technical the vocabulary is (technical words split into more tokens)
- Whether the text contains code (code often tokens differently)
```

**Why this matters:** embedding models have limits in tokens, not characters. If you set `chunk_size=2000` characters and your embedding model has a 256-token limit, every chunk will be silently truncated. The model will only embed the first 256 tokens and throw away the rest — no error, no warning.

**Always verify with tiktoken:**
```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # OpenAI tokenizer, close to most models

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# Check your chunks BEFORE embedding
for chunk in chunks:
    tokens = count_tokens(chunk.page_content)
    chars = len(chunk.page_content)
    print(f"Chars: {chars} | Tokens: {tokens} | Ratio: {chars/tokens:.1f} chars/token")
```

**Typical character-to-token ratios:**
```
Normal English prose      : ~4.5–5.0 chars/token
Technical documentation   : ~4.0–4.5 chars/token (jargon splits into more tokens)
Code (Python, YAML, JSON) : ~3.0–3.5 chars/token
Very short function words : ~3.0 chars/token
```

So `chunk_size=500` characters is approximately:
- 100–110 tokens for normal prose
- 110–125 tokens for technical text
- 140–165 tokens for code-heavy content

---

### Parameter 2 — Chunk Overlap

`chunk_overlap` defines how many characters are shared between consecutive chunks.

**Visualizing overlap:**
```
chunk_size=500, chunk_overlap=100

Document text positions: 0────────────────────────────1500

Chunk 1: positions   0 ──────────────── 500
Chunk 2: positions 400 ──────────────── 900   (100-char overlap with Chunk 1)
Chunk 3: positions 800 ──────────────── 1300  (100-char overlap with Chunk 2)
Chunk 4: positions 1200─────────────── 1500
```

**What happens at a chunk boundary without overlap:**

```
Document text:
"...The deployment command requires the --force flag when overriding existing resources.
This flag bypasses validation and should only be used in emergency scenarios..."

Chunk 3 ends: "...The deployment command requires the --force flag when overriding existing resources."
Chunk 4 starts: "This flag bypasses validation and should only be used in emergency scenarios..."
```

A user asks: "When should the --force flag be used?"

The semantic match for "when should --force be used?" aligns with the second sentence: "should only be used in emergency scenarios." The retriever returns Chunk 4.

But Chunk 4 says: "This flag bypasses validation and should only be used in emergency scenarios."

"This flag" — what flag? The context that "this flag" is `--force` is in Chunk 3, which was not retrieved.

❌ The answer "this flag should only be used in emergency scenarios" is meaningless without knowing which flag.

**With 100-character overlap:**

Chunk 4 starts: "...The deployment command requires the --force flag when overriding existing resources. This flag bypasses validation and should only be used in emergency scenarios..."

Now Chunk 4 contains both the flag name AND the condition. ✅

---

### Parameter 3 — Separators

Separators define the priority order for split points. `RecursiveCharacterTextSplitter` tries each separator in order — using the next one only if the chunk from the previous separator is still too large.

**Default separators:**
```python
separators=["\n\n", "\n", ". ", " ", ""]
```

This means:
1. Try to split at paragraph breaks (`\n\n`) first
2. If the paragraph is still too big, split at line breaks (`\n`)
3. If still too big, split at sentence ends (`. `)
4. If still too big, split at word boundaries (` `)
5. As last resort, split anywhere (`""`)

**For technical documents with code:**
```python
separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
```

Adding `"\n```"` before paragraph breaks ensures code block boundaries are respected before character-level splits.

**For functional/policy documents:**
```python
separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
```

Adding section headings at the top ensures `##` sections are always complete chunks before any lower-level split happens.

---

## How Chunk Size Affects Embedding Quality — The Core Insight

This is the most important thing to understand about chunk size, and most tutorials skip it.

**Embedding a chunk produces a single vector.** That vector represents the "meaning" of the entire chunk. The embedding model compresses all the content of the chunk into ~768 or 1536 numbers.

When you retrieve, you compare the query vector to chunk vectors. The closer the vectors, the more relevant the chunk.

**Small chunk (100–200 tokens):**
```
Chunk: "The API Server handles all REST API calls in a Kubernetes cluster."

This chunk has one clear, narrow topic.
Its embedding vector points precisely toward "Kubernetes API Server functionality."

Query: "What does the Kubernetes API Server do?"
→ Very high similarity. Retrieves reliably. ✅
```

**Large chunk (800–1500 tokens):**
```
Chunk: "Kubernetes has several core components.
The API Server handles all REST API calls.
The Scheduler assigns pods to nodes based on available resources and constraints.
The Controller Manager runs controller loops to maintain desired cluster state.
etcd is the backing key-value store for all cluster data.
The kubelet runs on each node and manages pod lifecycle.
The kube-proxy handles network routing rules on each node."

This chunk covers 7 different components.
Its embedding vector points toward "Kubernetes components generally."

Query: "What does the Kubernetes API Server do?"
→ Moderate similarity. The vector also responds to Scheduler queries, etcd queries, kubelet queries. Less precise. ⚠️
```

**The principle:**
- Small chunks → narrow, precise embeddings → high retrieval precision for specific queries
- Large chunks → broad, general embeddings → good for broad questions, poor for specific ones
- The right size is calibrated to the granularity of your users' actual questions

---

## Parameter Decision Framework

Answer these questions in order before picking your initial parameters:

**Question 1: Are user queries specific or broad?**
```
Specific ("What flag do I use for kubectl rollback?")  → smaller chunks (300–400 chars)
Broad ("Explain the deployment process")               → larger chunks (600–1000 chars)
Mixed (both types)                                     → medium chunks (500–700) or hierarchical
```

**Question 2: What is your embedding model's token limit?**
```
all-MiniLM-L6-v2   : 256 tokens → chunk_size ≤ 1000 chars (leaves buffer)
BAAI/bge-small     : 512 tokens → chunk_size ≤ 2000 chars
text-embedding-3   : 8191 tokens → chunk_size up to 35000 chars (impractical for most)
```

**Question 3: How much context does each answer require?**
```
Factual lookup ("what is X?")                  → 100–200 token chunks
Rule + exception ("policy for X?")             → 300–500 token chunks
Process explanation ("how does X work?")       → 400–700 token chunks
Complex reasoning ("why does X cause Y?")      → 500–1000 token chunks
```

**Question 4: How many chunks will you retrieve (top-k)?**
```
top-k=3 → each chunk must be self-sufficient → larger chunks
top-k=10 → multiple chunks provide coverage → smaller chunks acceptable
```

---

## Starting Points by Use Case

These are evidence-based starting parameters. They are starting points — not final answers.

### Customer Support / FAQ System

```python
chunk_size=400, chunk_overlap=60
```
**Why:** Questions are specific ("is product X compatible with Y?"). Answers are short and factual. Small chunks with precise embeddings produce the best top-1 retrieval accuracy.

**Token equivalent:** ~80–90 tokens per chunk.  
**Safe for:** all-MiniLM-L6-v2 (256 token limit), BGE-small (512 token limit).

---

### Technical Documentation (Runbooks, APIs)

```python
chunk_size=500, chunk_overlap=90
```
**Why:** Technical questions are narrow but answers require context (prerequisites + command + verification). 500 characters = ~110 tokens, which fits one complete procedure step with surrounding context.

**Higher overlap** (90 vs 60) ensures commands and their prerequisites overlap when they span chunks.

---

### Business / Functional Documents (Policies, PRDs)

```python
chunk_size=700, chunk_overlap=120
```
**Why:** Policy questions require rule + exception + approval chain to give a complete answer. Smaller chunks split these apart. 700 characters = ~150 tokens, which fits most policy sections.

**Overlap of 120** ensures exception clauses that follow rules are represented in both chunks.

---

### Research Papers / Academic Documents

```python
chunk_size=600, chunk_overlap=100
```
**Why:** Academic arguments span multiple sentences. The claim → evidence → conclusion structure should stay in one chunk when possible. Dense vocabulary means 600 characters ≈ 130–150 tokens.

---

### Legal / Compliance Documents

```python
chunk_size=800, chunk_overlap=150
```
**Why:** Legal clauses reference other clauses. Context is critical. High overlap ensures clause transitions are captured in both neighboring chunks.

---

### Transcripts / Conversations

```python
chunk_size=300, chunk_overlap=120
```
**Why:** Conversation turns are short but meaning builds across exchanges. Very high overlap (40% of chunk size) ensures the conversational thread is preserved across chunk boundaries.

---

### Source Code

```python
chunk_size=1500, chunk_overlap=0
# Use language-aware splitter, not character-based
```
**Why:** Code is split by function or class boundaries — not character count. Each function or class is a complete logical unit. No overlap is needed because code boundaries are semantically clean.

---

## The Systematic Tuning Process

This is the only way to know if your parameters are right. Guessing is not tuning.

### Step 1 — Establish your baseline

Always start from the same baseline so you can measure improvements objectively:
```
chunk_size   : 500 characters
chunk_overlap: 80 characters
splitter     : RecursiveCharacterTextSplitter
separators   : ["\n\n", "\n", ". ", " ", ""]
```

### Step 2 — Build a benchmark query set

Write 20–40 questions that represent the actual queries users will ask. Label the expected source document and section for each.

```
Benchmark set structure:

ID   : Q001
Query: "What is the leave policy for probationary employees?"
Expected source: hr-policy-v4.md
Expected section: Annual Leave — Probation Clause
Expected answer contains: "probation", "not eligible" or equivalent

ID   : Q002
Query: "How do I rollback the API server deployment?"
Expected source: runbook-api-server.md
Expected section: Rollback Procedure
Expected answer contains: rollback command + prerequisites
```

### Step 3 — Measure baseline retrieval quality

For each query in your benchmark set:
- Run the retriever, get top-3 and top-5 results
- Check: is the expected source in top-3?
- Check: is the expected section in top-5?
- Check: does the top-1 chunk contain enough context for a complete answer?

Score each query: 2 (perfect), 1 (partial), 0 (wrong or missing).

Record the average score across all queries.

```
Baseline results:
  Top-3 hit rate  : 62%
  Top-5 hit rate  : 71%
  Avg relevance   : 1.28 / 2.0
  Completeness    : 58% of answers are complete without expansion
```

### Step 4 — Change one variable at a time

Pick the parameter most likely to be causing your observed symptom and change only that.

| Observed Symptom | Most Likely Cause | Change |
|---|---|---|
| Answers are generic and vague | Chunks too large — embeddings unfocused | Decrease chunk_size by 100–200 |
| Answers are consistently incomplete | Chunks too small — context cut off | Increase chunk_size by 100–200 |
| Important context lost at boundaries | Overlap too low | Increase chunk_overlap by 30–50 |
| Too much noise in retrieved chunks | Overlap too high — duplicate content | Decrease chunk_overlap by 20–30 |
| Wrong document family retrieved | No metadata filtering | Add doc_type metadata + filter |
| Right document, wrong section | Split boundaries wrong | Switch to structure-aware separators |

### Step 5 — Re-run same benchmark, compare scores

```
Experiment 1: chunk_size=300 (decreased from 500)
  Top-3 hit rate  : 72%   (improved from 62%)
  Top-5 hit rate  : 79%   (improved from 71%)
  Avg relevance   : 1.48 / 2.0 (improved from 1.28)
  Completeness    : 51% — decreased! Some answers now incomplete.

Decision: better retrieval precision but worse completeness.
Try: chunk_size=300 with chunk_overlap=120 (higher overlap to restore completeness)

Experiment 2: chunk_size=300, chunk_overlap=120
  Top-3 hit rate  : 74%
  Avg relevance   : 1.55
  Completeness    : 68% — restored!

Decision: keep this as new baseline, continue tuning.
```

### Step 6 — Document every experiment

Keep a log. Do not rely on memory.

```
===========================
Experiment: #003
Date: 2024-03-15
Document set: HR policy documents (22 files)
Embedding model: all-MiniLM-L6-v2
Splitter: RecursiveCharacterTextSplitter

Parameters:
  chunk_size   : 300
  chunk_overlap: 120
  separators   : ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]

Results:
  Total chunks created : 847
  Avg token count      : 68
  Max token count      : 119  (within 256-token model limit ✅)
  Top-3 hit rate       : 74%
  Top-5 hit rate       : 82%
  Avg relevance score  : 1.55 / 2.0
  Completeness rate    : 68%

Observations:
  Policy sections mostly complete in single chunks ✅
  Exception clauses sometimes split from rules — increase overlap next experiment

Decision: New baseline. Next test: overlap=150
===========================
```

---

## Embedding Model Token Limits — Do Not Exceed

Never configure chunk_size without knowing your model's limit. Exceeding it causes **silent truncation** — the model embeds only the first N tokens and discards the rest, with no error.

| Embedding Model | Token Limit | Recommended Max Chunk Size |
|---|---|---|
| `all-MiniLM-L6-v2` | 256 tokens | 1000 characters (~200 tokens with buffer) |
| `BAAI/bge-small-en-v1.5` | 512 tokens | 2000 characters (~400 tokens with buffer) |
| `BAAI/bge-large-en-v1.5` | 512 tokens | 2000 characters |
| `text-embedding-3-small` (OpenAI) | 8191 tokens | 30000+ characters (not a practical limit) |
| `text-embedding-3-large` (OpenAI) | 8191 tokens | 30000+ characters |
| `jina-embeddings-v2-base-en` | 8192 tokens | 30000+ characters |

**Always leave a 20% buffer below the model limit.** Content with technical vocabulary uses more tokens per character. A chunk that measures 200 tokens on one document may measure 240 tokens on a more technical document — too close to the 256 limit.

---

## LLM Context Budget Planning

When deciding chunk size, think backward from the LLM context window:

```
Example planning for GPT-4o with 128k context:

Total context budget:          128,000 tokens
System prompt:                 -    800 tokens
User query:                    -    200 tokens
Response headroom:             -  3,000 tokens
Available for retrieved chunks: 124,000 tokens

But: passing 124k tokens to GPT-4o on every query is expensive.
Practical retrieved context: ~6,000 tokens

If chunk_size = 500 characters ≈ 110 tokens:
  Max chunks to pass: 6,000 / 110 = ~54 chunks
  Practical: retrieve top-20, rerank, pass top-5

If chunk_size = 200 characters ≈ 45 tokens:
  Max chunks to pass: 6,000 / 45 = ~133 chunks
  Practical: retrieve top-30, rerank, pass top-10
```

The smaller your chunks, the more you can fit in the LLM context. But very small chunks may not be self-sufficient — the LLM may need chunk expansion to generate complete answers.

---

## Chunk Size Experiment Log Template

Copy this for every experiment you run:

```
===========================
Experiment: #___
Date: 
Document set: 
Embedding model: 

Parameters tested:
  chunk_size   : 
  chunk_overlap: 
  separators   : 

Results:
  Total chunks created : 
  Avg token count      : 
  Max token count      : 
  Top-3 hit rate       : 
  Top-5 hit rate       : 
  Avg relevance score  : 
  Completeness rate    : 

Observations:
  [what worked]
  [what did not work]
  [unexpected behaviors]

Decision:
  Keep / Discard / Use as new baseline
  Next experiment: change ___ to ___
===========================
```
