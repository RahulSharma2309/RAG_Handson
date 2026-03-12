# Vector Store vs Vector Database — What Is the Difference?

> One of the most confusing things when learning RAG is that people use these terms interchangeably — but they are not the same thing.
> This document explains every layer, when to use each, and what this project uses.

---

## First: Why does "vector storage" exist at all?

Traditional databases (like MySQL, PostgreSQL, MongoDB) store text, numbers, and structured data. They are excellent at finding exact matches:

```sql
SELECT * FROM docs WHERE topic = 'kubernetes';
```

But they cannot answer: *"Find the 5 documents most semantically similar to this query vector."*

That requires a completely different kind of search — called **Approximate Nearest Neighbor (ANN) search** — and it needs special data structures optimised for high-dimensional floating point numbers.

This is why vector-specific storage exists.

---

## The three layers — from simplest to most powerful

Think of it as three levels, each building on the previous:

```
Level 1: Vector Library      (just the search algorithm — no storage)
Level 2: Vector Store        (search + local storage + metadata)
Level 3: Vector Database     (search + cloud/scalable storage + full DB features)
```

---

## Level 1: Vector Library — FAISS

**What it is:** A pure search algorithm library. No storage management. No metadata. No persistence by default. Just extremely fast math.

**Analogy:** A pocket calculator. It does the calculation perfectly but does not remember anything after you turn it off. You must save and load manually.

**Key characteristics:**
- Written in C++ by Meta AI Research, with Python bindings
- Fastest option for nearest-neighbor search at any scale
- Does not store your text — only the raw number vectors
- Does not store metadata — you manage that yourself (the `metadata.jsonl` file)
- Not persistent by default — you call `faiss.write_index()` manually to save
- No query language, no HTTP API, no filtering built-in
- Runs entirely in memory during search

**What this project uses it for:**
- ✅ The main production index in `rag_artifacts/vectorstore/minilm_l6/faiss_index.bin`
- Search is done in `search_local_embeddings.py` and `ask_rag.py`
- Metadata filtering is done manually in Python after FAISS returns raw indices

**When to use FAISS:**
- You want maximum performance and full control
- Your dataset is static or changes infrequently
- You are comfortable managing metadata separately
- You want zero infrastructure — just a binary file
- You are building a learning project or a focused internal tool

**When NOT to use FAISS:**
- You need multi-user concurrent access
- Your data changes frequently and you want incremental updates without rebuilding
- You need complex metadata filtering at the database level
- You need high availability or replication

---

## Level 2: Vector Store — ChromaDB (local)

**What it is:** A full local vector database that handles vectors + text + metadata together in one system. Persists automatically to disk. Has a clean Python API.

**Analogy:** A proper filing cabinet. It stores the document, its label, and its location all together. You do not manage them separately.

**Key characteristics:**
- Stores vectors, raw text, and metadata in one collection
- Automatically persists to disk (SQLite + parquet under the hood)
- Python API handles embedding automatically if you provide an embedding function
- Built-in filtering (you can filter by metadata inside the query, not after)
- Runs locally — no server, no cloud
- Has a simple client-server mode for multi-user access

**What this project uses it for:**
- ✅ The hands-on learning notebook (`Handson Learning/2-VectorStore/1-CromaDb.ipynb`)
- Demonstrates a higher-level abstraction than FAISS

**ChromaDB vs FAISS side by side:**

```python
# FAISS — raw search (you manage everything)
scores, indices = faiss_index.search(query_vector, k=5)
for score, idx in zip(scores[0], indices[0]):
    m = metadata[idx]           # you look this up separately
    text = text_map[m["chunk_id"]]  # you look this up separately

# ChromaDB — managed search (everything together)
results = chroma_collection.query(
    query_texts=["your question"],
    n_results=5,
    where={"folder_profile": "operations_docs"}  # metadata filter built-in
)
# results already contains text + metadata + distances
```

**When to use ChromaDB:**
- Prototyping or learning
- Small to medium datasets (up to a few million vectors on a single machine)
- You want a simpler API without managing metadata separately
- You want persistence without setting up a server

**When NOT to use ChromaDB:**
- Very large scale (hundreds of millions of vectors)
- Distributed / multi-machine setups
- You need enterprise features (access control, audit logs, SLAs)

---

## Level 3: Vector Database — Cloud/Production options

**What it is:** A fully managed database service built specifically for vectors. Cloud-hosted (or self-hosted), scales horizontally, has enterprise features, REST APIs, SDKs for every language.

**Analogy:** A commercial library system with staff, cataloguing software, borrowing history, access rules, and the ability to add a new branch whenever you need more space.

### The major players

#### Pinecone
- Cloud-only, fully managed
- Free tier: 1 index, up to 100K vectors
- Paid: from $70/month for production
- Pros: Zero ops, very easy to start, stable and fast
- Cons: Vendor lock-in, data leaves your machine, expensive at scale
- Best for: Startups that want zero infrastructure, production apps quickly

```python
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
index = pc.Index("my-index")
index.upsert(vectors=[{"id": "chunk1", "values": [0.1, 0.2, ...], "metadata": {...}}])
results = index.query(vector=[0.1, 0.2, ...], top_k=5, include_metadata=True)
```

**Cost for this project's 979 vectors:** Free tier is more than enough.

#### Weaviate
- Cloud or self-hosted (Docker)
- Free tier: Weaviate Cloud (limited), self-hosted is always free
- Pros: Rich filtering, GraphQL API, modular (bring your own embeddings or use built-in)
- Cons: More complex setup, heavier than ChromaDB
- Best for: Teams who want self-hosted + cloud option + complex queries

#### Qdrant
- Cloud or self-hosted (Docker)
- Free tier: 1 GB cloud, self-hosted unlimited
- Pros: Rust-based (very fast), excellent filtering, clean REST API, Docker support
- Cons: Newer, smaller community than Pinecone/Weaviate
- Best for: Performance-focused teams, on-premise requirements, EU data residency

```python
from qdrant_client import QdrantClient
client = QdrantClient("localhost", port=6333)  # or cloud URL
client.search(
    collection_name="knowledge",
    query_vector=[0.1, 0.2, ...],
    limit=5,
    query_filter={"must": [{"key": "folder_profile", "match": {"value": "operations_docs"}}]}
)
```

#### pgvector (PostgreSQL extension)
- Runs inside your existing PostgreSQL database
- Free (open-source)
- Pros: You already have PostgreSQL? Add vectors with one extension. SQL queries with vector search combined.
- Cons: Not as fast as purpose-built vector DBs at very large scale, no ANN (only exact search by default)
- Best for: Teams with existing PostgreSQL infrastructure who want to add semantic search without new systems

```sql
-- After installing pgvector extension
CREATE TABLE chunks (id SERIAL, text TEXT, embedding vector(384));
SELECT text FROM chunks ORDER BY embedding <-> '[0.1, 0.2, ...]' LIMIT 5;
```

#### Milvus
- Self-hosted (Docker/Kubernetes) or cloud (Zilliz)
- Free self-hosted, Zilliz cloud has free tier
- Pros: Designed for billions of vectors, multiple index types, enterprise-grade
- Cons: Complex setup, overkill for small projects
- Best for: Very large scale, enterprises, ML teams with dedicated infra

---

## Complete comparison table

| | FAISS | ChromaDB | Pinecone | Weaviate | Qdrant | pgvector | Milvus |
|---|---|---|---|---|---|---|---|
| **Type** | Library | Local DB | Cloud DB | Cloud/Self | Cloud/Self | PostgreSQL ext | Self/Cloud |
| **Free?** | ✅ Always | ✅ Always | ✅ Free tier | ✅ Self-hosted | ✅ Self-hosted | ✅ Always | ✅ Self-hosted |
| **Persistence** | Manual | Automatic | Cloud | Yes | Yes | Yes (PG) | Yes |
| **Metadata filter** | Manual in Python | Built-in | Built-in | Built-in | Built-in | SQL WHERE | Built-in |
| **Scale** | Millions (1 machine) | Millions (1 machine) | Billions | Billions | Billions | Millions | Billions |
| **Setup complexity** | None | pip install | Sign up | Docker | Docker | psql extension | Docker/K8s |
| **Multi-user** | No | Limited | Yes | Yes | Yes | Yes (PG) | Yes |
| **Used in project** | ✅ Main system | ✅ Notebook | — | — | — | — | — |

---

## Which should you use at each stage of your journey?

### Day 1 — Learning what RAG is
Use FAISS. It forces you to understand every piece because you manage it all yourself. There is no magic. You see exactly what is stored and how search works.

### Week 1 — Building a prototype
Use ChromaDB. Much cleaner API, automatic persistence, built-in metadata filtering. You can move faster and focus on the RAG logic rather than infrastructure.

### Month 1 — Building for a team
Start evaluating Qdrant (self-hosted Docker) or Weaviate. You need multi-user access, incremental updates, better filtering.

### Production at scale
Pinecone if you want zero ops and can afford it. Qdrant or Weaviate self-hosted if you need data control. pgvector if you already have PostgreSQL.

---

## The terminology confusion — cleared up

People use these terms loosely. Here is what they technically mean:

| Term | What it actually means |
|---|---|
| **Vector library** | A search algorithm (FAISS, Annoy, ScaNN) — no storage, just math |
| **Vector store** | Loose term for any system storing vectors (FAISS file, ChromaDB, Pinecone — all called this) |
| **Vector index** | The internal data structure used for fast search (IndexFlatIP, IVF, HNSW) |
| **Vector database** | A full database system with persistence, APIs, filtering, scaling (Pinecone, Qdrant, Weaviate) |
| **Embedding store** | Same as vector store — just emphasising these are embeddings |
| **Knowledge base** | Your source documents before they become vectors — the human-readable layer |

In conversation, "vector store" is used for all of these. This is fine. Just know the technical difference when you need to choose.

---

## What this project uses and why

| Use case | Tool | Reason |
|---|---|---|
| Production RAG system | FAISS | Single binary file, zero infrastructure, max control, teaches the fundamentals |
| Learning exercise | ChromaDB | Shows higher-level API, auto-persistence, better for exploration |
| Future upgrade path | Qdrant (self-hosted Docker) | When multi-user or incremental updates needed — easy Docker deployment |
