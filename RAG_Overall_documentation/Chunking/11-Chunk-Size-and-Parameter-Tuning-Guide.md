# Chunk Size and Parameter Tuning Guide

> Chunking parameters are not arbitrary. This guide gives you the science behind each parameter and a practical process for tuning them with evidence.

---

## 1) The Three Core Parameters

### A. Chunk Size
The maximum size of one chunk, measured in tokens or characters.

**What it controls:**
- Information density per chunk
- Embedding precision
- Retrieval scope

**Effect of increasing chunk size:**
- More context per chunk → better for complex answers
- Less precise embeddings → noisier retrieval
- Fewer chunks in top-k → lower chance of missing relevant content

**Effect of decreasing chunk size:**
- More precise embeddings → better retrieval accuracy
- Less context per chunk → may miss surrounding info
- More chunks needed → higher token budget for LLM context

---

### B. Chunk Overlap
The number of tokens/characters shared between consecutive chunks.

```
chunk_size = 500, overlap = 100

Chunk 1: tokens 0–500
Chunk 2: tokens 400–900    (100 token overlap with chunk 1)
Chunk 3: tokens 800–1300   (100 token overlap with chunk 2)
```

**Why overlap matters:**
Important context is often split at a chunk boundary.  
Without overlap, a sentence that spans two chunks may be incomplete in both.  
With overlap, both chunks contain the sentence.

**Effect of increasing overlap:**
- Better boundary context preservation
- More redundancy in index (same content in multiple chunks)
- Slightly larger index size

**Effect of decreasing overlap:**
- Less redundancy
- Risk of losing context at boundaries
- Smaller index

**Practical range: 10–20% of chunk size**
- chunk_size=500 → overlap=50–100
- chunk_size=1000 → overlap=100–200

---

### C. Separators
The text characters or patterns used to decide where splits happen.

**LangChain RecursiveCharacterTextSplitter default order:**
```python
separators=["\n\n", "\n", ". ", " ", ""]
```

**For technical docs (preserve code):**
```python
separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
```

**For functional/business docs:**
```python
separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
```

**For CSV/structured:**
```python
separators=["\n"]  # one row per split
```

---

## 2) How Chunk Size Affects Embedding Quality

This is the most important thing to understand.

### Short chunks (100–200 tokens)
- Embedding captures a very specific, narrow meaning
- Excellent for lookup queries ("what is X?")
- Poor for contextual queries ("how does X relate to Y?")
- Good for: FAQs, product descriptions, atomic facts

### Medium chunks (300–600 tokens)
- Embedding captures a focused topic
- Balanced retrieval precision and context
- Works for most use cases
- **Best default range**

### Large chunks (800–1500 tokens)
- Embedding captures broad themes
- Good for summaries and high-level answers
- Poor precision for specific detail retrieval
- Good for: executive summaries, chapter-level hierarchical nodes

### Too large (beyond embedding model's limit)
- Content is silently truncated
- Embedding is corrupted
- Retrieval becomes unpredictable

---

## 3) Parameter Decision Framework

Answer these questions to pick your starting parameters:

| Question | Answer → Parameter |
|---|---|
| Are questions specific or broad? | Specific → smaller chunk (300–400 tokens) / Broad → larger chunk (600–1000 tokens) |
| How dense is the content? | Dense (academic) → smaller chunks / Light (narrative) → larger chunks |
| What embedding model are you using? | Must stay within model's context window |
| How much context does the answer need? | More context needed → larger chunk + more overlap |
| How many chunks will you retrieve (top-k)? | Large top-k → can afford smaller chunks / Small top-k → need larger chunks |

---

## 4) Recommended Starting Points by Use Case

These are evidence-based starting parameters. Tune from here.

### Customer support / FAQ
```python
chunk_size=400, chunk_overlap=50
```
Questions are specific. Answers need exact policy wording.

### Research papers / academic
```python
chunk_size=600, chunk_overlap=100
```
Dense content. Arguments span multiple sentences.

### Technical documentation (runbooks, APIs)
```python
chunk_size=500, chunk_overlap=80
```
Moderate precision. Commands need context.

### Legal / compliance documents
```python
chunk_size=800, chunk_overlap=150
```
Context critical. Rules reference each other.

### Business policies / functional docs
```python
chunk_size=700, chunk_overlap=120
```
Rule completeness matters more than precision.

### Transcripts / conversations
```python
chunk_size=300, chunk_overlap=100
# High overlap for continuous flow
```

### Source code
```python
chunk_size=1000, chunk_overlap=0
# Split by function/class — no overlap needed
```

---

## 5) The Tuning Process

### Step 1: Establish a baseline
```
chunk_size=512, chunk_overlap=50
Splitter: RecursiveCharacterTextSplitter
```
This is the most common production starting point.

### Step 2: Create a benchmark query set
Write 20–40 real questions that represent your actual use case.
Label the expected source documents.

Example:
```
Q: "What is the leave policy for probationary employees?"
Expected source: hr-policy-v3.md, section: Probation Rules
```

### Step 3: Evaluate top-k retrieval
For each query, check:
- Is the right document in top-3?
- Is the right section in top-5?
- Does the chunk contain enough context for a full answer?

### Step 4: Diagnose patterns

| Symptom | Likely cause | Adjustment |
|---|---|---|
| Answers are too generic | Chunks too large | Decrease chunk_size |
| Answers are incomplete | Chunks too small | Increase chunk_size |
| Context lost at boundaries | Not enough overlap | Increase chunk_overlap |
| Too much noise in retrieved chunks | Overlap too high | Decrease chunk_overlap |
| Wrong document retrieved | Semantic ambiguity | Try semantic chunking or metadata filters |
| Right doc, wrong section | Split boundaries wrong | Use structure-aware splitting |

### Step 5: Tune one variable at a time

Do not change chunk_size AND overlap AND separators simultaneously.  
Change one. Re-evaluate. Record results. Then change another.

### Step 6: Compare experiments

| Config | Chunk Count | Top-3 Accuracy | Avg Relevance Score | Notes |
|---|---|---|---|---|
| size=512, overlap=50 | 840 | 65% | 0.72 | Baseline |
| size=300, overlap=50 | 1200 | 70% | 0.78 | Better precision |
| size=300, overlap=100 | 1350 | 75% | 0.81 | Best so far |
| size=400, overlap=80 | 1100 | 73% | 0.79 | Good balance |

---

## 6) Chunk Size for Different Embedding Models

Always calibrate to your embedding model:

| Model | Recommended Chunk Size |
|---|---|
| `all-MiniLM-L6-v2` (256 max) | 150–220 tokens |
| `BAAI/bge-small-en-v1.5` (512 max) | 300–450 tokens |
| `text-embedding-ada-002` (8191 max) | 500–1500 tokens |
| `text-embedding-3-small` (8191 max) | 500–1500 tokens |

Using a larger chunk than the model can process → truncation → silent quality loss.

---

## 7) Retrieval Budget Planning

```
Planning a typical RAG call:

LLM context window: 8,192 tokens
- System prompt:       400 tokens
- User query:          150 tokens  
- Retrieved context: 5,000 tokens  ← your chunk budget
- Response headroom: 2,642 tokens

Chunk size: 500 tokens
Max chunks to pass: 5,000 ÷ 500 = 10 chunks (retrieve top-10)
Practical recommendation: retrieve top-10, rerank, pass top-5
```

Overshooting the context window causes:
- Truncation of retrieved content
- Unpredictable answers
- Higher cost per query

---

## 8) Chunk Size Experiment Template

Use this as your structured experiment log:

```
Experiment: [number]
Date: [date]
Document set: [description]
Embedding model: [model name]
Splitter: [splitter type]

Parameters tested:
  chunk_size: [value]
  chunk_overlap: [value]
  separators: [list]

Results:
  Total chunks created: [number]
  Avg chunk token count: [number]
  Top-3 hit rate: [%]
  Top-5 hit rate: [%]
  Noise level: [low/medium/high]

Observations:
  [what worked / what did not]

Decision:
  Keep / Discard / Use as new baseline
```
