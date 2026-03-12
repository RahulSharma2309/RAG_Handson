# RAG Core Components — Query Processing and Generation

> Source notes from your RAG lecture transcript, expanded into practical architecture notes.

---

## Why This Stage Matters

In a RAG system, document ingestion prepares knowledge, but **query processing** decides whether your answer will be relevant or not.

If retrieval is weak, even a strong LLM gives weak output.

---

## RAG in 3 Phases (High-Level)

```text
Phase 1: Document Ingestion
  Source Data -> Chunking -> Embeddings -> Vector DB

Phase 2: Query Processing
  User Query -> Query Embedding -> Similarity Search -> Top-K Chunks

Phase 3: Generation
  (Original Query + Retrieved Context) -> LLM -> Final Answer
```

---

## Phase 1 Recap — Document Ingestion and Preprocessing

Before query processing starts, your knowledge base should already be built:

1. Collect sources (PDF, DOCX, website, JSON, DB records, APIs)
2. Parse and clean text
3. Split into chunks
4. Convert chunks to vectors using embedding model
5. Store vectors + metadata in vector database

Metadata examples:
- `source_file`
- `page_number`
- `section_title`
- `timestamp`
- `product_category`
- `tenant_id`

---

## Phase 2 — Query Processing (Main Topic)

### Step-by-step Flow

```text
User Query
   |
   v
Text -> Embedding Model -> Query Vector
   |
   v
Vector DB Similarity Search
   |
   v
Top-K Retrieved Chunks
   |
   v
Context Assembly / Augmentation
   |
   v
Send to Generation Phase
```

### Step 1: Input Query

Example query:
- "What is RAG?"

### Step 2: Convert Query Text to Vector

Use the same or compatible embedding model used during ingestion.

Why:
- Query and stored chunks must be in the same vector space.

### Step 3: Search Relevant Chunks in Vector DB

Common similarity methods:
- Cosine similarity
- Dot product
- Euclidean distance

Typical behavior:
- Find top-k chunks closest to query vector
- Return chunk text + metadata + similarity scores

### Step 4: Retrieve and Rank

Retrieved output might look like:
- `doc_chunk_17` (score 0.92)
- `doc_chunk_05` (score 0.89)
- `doc_chunk_31` (score 0.86)

### Step 5: Build Enriched Context

You combine:
- original query
- retrieved chunks
- useful metadata
- optional guardrails/business instructions

This enriched context is passed to LLM in generation phase.

---

## Phase 3 — Generation

Generation phase input:
- user query
- enriched retrieved context

Generation phase output:
- final answer in natural language
- often summarized and formatted for user readability

Model options:
- OpenAI models
- Llama family
- Grok-hosted/open models
- Gemini models

---

## Practical Architecture View

```text
                +----------------------+
                |  Source Data         |
                |  PDF / DOC / Web     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Chunk + Embed        |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Vector Database      |
                +----------+-----------+
                           ^
                           |
                 Query Vector Search
                           ^
                           |
                +----------+-----------+
                | User Query           |
                | "What is RAG?"       |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Retrieved Chunks     |
                | + Metadata           |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | LLM Generation       |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Final Response       |
                +----------------------+
```

---

## What "Augmentation" Means in RAG

Augmentation is not random extra text. It is structured enrichment that improves answer quality.

Examples:
- Add source citation info
- Add product/tenant/business constraints
- Add retrieval score thresholds
- Add "answer only from context" instruction

Good augmentation reduces hallucination risk and improves trust.

---

## Design Guidelines for Better Query Processing

### 1) Use consistent embedding strategy
- Avoid mixing incompatible embedding models unless intentional migration logic exists.

### 2) Keep chunk quality high
- Poor chunk boundaries produce poor retrieval.
- Use semantic chunking where needed.

### 3) Use metadata filters
- Filter by language, region, product line, date range, tenant.

### 4) Tune top-k retrieval
- Too low: may miss context
- Too high: adds noise and token cost

### 5) Add reranking (optional but useful)
- First retrieve candidates with vector search
- Then rerank with cross-encoder/re-ranker

### 6) Log retrieval traces
- Store query, retrieved chunks, scores, final answer.
- Essential for debugging wrong answers.

---

## Common Failure Cases (and Fixes)

| Problem | Why It Happens | Fix |
|---|---|---|
| Irrelevant chunk returned | weak chunking or embedding mismatch | improve chunking, retrain/tune embeddings |
| Correct chunk exists but not retrieved | top-k too small, poor indexing | increase top-k, hybrid retrieval |
| Hallucinated final answer | weak grounding prompt | enforce context-only generation + citations |
| Old/outdated answers | stale documents in vector DB | re-index with freshness policy |
| Cross-tenant data leakage | missing metadata filters | strict filter at retrieval layer |

---

## Implementation Checklist

- [ ] Ingestion pipeline completed
- [ ] Embeddings generated and stored
- [ ] Metadata schema finalized
- [ ] Query embedding model configured
- [ ] Similarity metric selected
- [ ] Top-k tuned
- [ ] Context builder implemented
- [ ] Generation prompt grounded
- [ ] Trace logging enabled
- [ ] Evaluation set created

---

## Minimal Pseudocode (Conceptual)

```python
def rag_answer(user_query):
    query_vec = embed(user_query)
    results = vector_db.search(query_vec, top_k=5, filters={"tenant_id": "freshharvest"})
    context = build_context(user_query, results)
    answer = llm.generate(context)
    return answer
```

---

## FreshHarvest Example

User query:
- "What is the refund policy for perishable products?"

Query processing:
1. Convert query to vector
2. Search policy chunks in vector DB
3. Retrieve top matching policy paragraphs
4. Attach metadata (policy version/date)
5. Pass to LLM for final response

Output:
- clear policy summary
- optionally include policy section references

---

## Key Takeaways

- RAG quality depends heavily on retrieval quality.
- Query processing is the bridge between user intent and stored knowledge.
- Retrieval + metadata + context assembly decide the final answer quality.
- Generation should be grounded, traceable, and auditable.

---

## Next Notes to Create

Recommended next files in this folder:
- `02-rag-generation-phase-prompting-and-grounding.md`
- `03-rag-evaluation-and-metrics.md`
- `04-rag-failure-modes-and-debugging.md`
- `05-rag-implementation-patterns-langchain-langgraph.md`

