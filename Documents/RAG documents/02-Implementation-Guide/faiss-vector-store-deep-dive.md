# FAISS Vector Store — Deep Dive

## What is FAISS and why is it used here?

FAISS stands for **Facebook AI Similarity Search**. It is an open-source library built by Meta AI Research, designed for one specific job: finding the most similar vectors from a large collection, as fast as possible.

Think of it like this:

> You have 979 GPS coordinates (one per chunk) plotted on a map.
> A user asks a question — that question gets its own GPS coordinate.
> FAISS instantly finds the 5 closest coordinates to where the user is standing.
> Those nearby coordinates are the most relevant chunks.

FAISS does not store text, metadata, or file names. It only stores numbers (the vectors) and gives you back row indices. The metadata is stored separately in `metadata.jsonl` and aligned by index position.

---

## FAISS vs ChromaDB — when to use which

| | FAISS | ChromaDB |
|---|---|---|
| What it stores | Vectors only | Vectors + text + metadata together |
| Speed | Extremely fast | Fast |
| Disk format | Single `.bin` file | Folder with SQLite database |
| Query API | Low-level (index.search) | High-level (similarity_search) |
| Metadata filtering | Manual (you write the filter logic) | Built-in filter support |
| Best for | Production, high performance, custom pipelines | Prototyping, notebooks, simpler queries |
| Used in this project | `rag_artifacts/vectorstore/` (the main system) | `Handson Learning/2-VectorStore/1-CromaDb.ipynb` (learning exercise) |

In this project FAISS is used for the real RAG system because it gives full control and is faster. ChromaDB is used in the notebook to learn the higher-level API. Both produce the same end result.

---

## How the FAISS index was built

### The pipeline

```
Source markdown docs (89 .md files)
          ↓
  chunk_markdown_docs.py
          ↓
979 JSONL chunk records  (text + metadata per chunk)
          ↓
  build_local_embeddings.py
          ↓
  SentenceTransformer (all-MiniLM-L6-v2)
          ↓
979 × 384 float32 matrix
          ↓
  FAISS IndexFlatIP (inner product index)
          ↓
  faiss_index.bin  +  metadata.jsonl  +  embeddings.npy
```

---

## The chunking step — what went in

Before any embeddings are created, the source documents are split into chunks using `chunk_markdown_docs.py`. This is the most important quality driver in the whole pipeline — bad chunks = bad retrieval.

### Profiles used and their stats

| Profile | Files | Chunks | Avg chunk tokens | Target tokens |
|---|---|---|---|---|
| `general_docs` | 28 | 267 | 152 | 380 |
| `operations_docs` | 22 | 298 | 157 | 320 |
| `product_owner_docs` | 25 | 241 | 150 | 450 |
| `technical_docs` | 14 | 140 | 157 | 360 |
| **Total** | **89** | **979** | **~154** | — |

Each profile applies different `target_tokens`, `max_tokens`, and `overlap_tokens` settings suited to the nature of the documents in that domain.

### What a chunk record looks like

Every chunk is a line in a `.chunks.jsonl` file:

```json
{
  "chunk_id": "CI_CD_INTEGRATION-c003",
  "source_file": "rag_system_workspace/rag/input_docs/11-kubernetes/CI_CD_INTEGRATION.md",
  "folder_profile": "operations_docs",
  "section_title": "✅ Summary",
  "section_chunk_index": 1,
  "token_count": 142,
  "text": "## ✅ Summary\n\n**CI/CD Integration provides:**\n- ✅ Automated builds and tests..."
}
```

The `chunk_id` is the primary key that links the FAISS row index → metadata row → chunk text. The position in the FAISS index, the row in `metadata.jsonl`, and the entry in the text map are all aligned by the same insertion order.

---

## The embedding step — turning text into numbers

**Script:** `rag_system_workspace/scripts/build_local_embeddings.py`

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`

### What the model does

Each chunk's text is passed through the MiniLM neural network. The network outputs a 384-number vector that encodes the *meaning* of that text. Chunks about similar topics produce vectors that point in similar directions in 384-dimensional space.

### Why `all-MiniLM-L6-v2`?

| Property | Value |
|---|---|
| Model size | ~90 MB |
| Vector dimensions | 384 |
| Training objective | Semantic similarity (sentence pairs) |
| Hardware required | CPU only — no GPU needed |
| Cost | Free, runs offline |
| Quality | Strong for retrieval tasks on technical/structured text |

### Key setting: `normalize_embeddings=True`

This scales every vector to unit length (length = 1). After normalization:

```
cosine_similarity(A, B) = dot_product(A, B)
```

This simplifies the math — you no longer need a special cosine formula. A simple dot product gives you the similarity score. This is why `IndexFlatIP` (inner product) is used in FAISS rather than `IndexFlatL2` (Euclidean distance).

### What the build script produces

```python
vectors = model.encode(
    texts,
    batch_size=128,
    normalize_embeddings=True,
    convert_to_numpy=True
).astype("float32")

index = faiss.IndexFlatIP(384)
index.add(vectors)
faiss.write_index(index, "faiss_index.bin")
np.save("embeddings.npy", vectors)
```

---

## The output files — what is in each

All files live at: `rag_system_workspace/rag_artifacts/vectorstore/minilm_l6/`

### `faiss_index.bin` — the search engine (1.4 MB)

This is the FAISS index. It is a binary file — not human-readable. It contains the 979 vectors organized so that FAISS can search them extremely fast.

When you call `index.search(query_vector, k=200)`, FAISS:
1. Computes the dot product of your query vector against all 979 stored vectors
2. Returns the top-200 row indices sorted by score
3. Does this in milliseconds

```python
import faiss
index = faiss.read_index("faiss_index.bin")
print(index.ntotal)   # 979 — number of vectors
print(index.d)        # 384 — number of dimensions
```

### `metadata.jsonl` — the label layer (250 KB)

979 lines, one per chunk. Row `i` in this file corresponds to row `i` in the FAISS index.

```json
{"chunk_id": "CI_CD_INTEGRATION-c001", "source_file": "...", "folder_profile": "operations_docs", "section_title": "...", "section_chunk_index": 1, "token_count": 87}
```

Notice: the text itself is **not** stored here. Only the metadata. The text is kept in the original `.chunks.jsonl` files and loaded into a dictionary (`text_map`) keyed by `chunk_id`. This keeps `metadata.jsonl` small and fast to scan.

### `embeddings.npy` — the raw number matrix (1.4 MB)

The full 979 × 384 float32 numpy array saved to disk.

```python
import numpy as np
emb = np.load("embeddings.npy")
print(emb.shape)   # (979, 384)
print(emb[0])      # the 384-number vector for chunk 0
```

**When would you use this?**
- Debugging: inspect individual vectors
- Analysis: compute similarity between specific chunks manually
- Visualization: compress to 2D with PCA/UMAP to see clusters
- Experimentation: test alternative search approaches without rebuilding FAISS

### `build_summary.json` — the build receipt (tiny)

```json
{
  "model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "batch_size": 128,
  "normalize_embeddings": true,
  "chunks": 979,
  "vector_dim": 384,
  "index_path": "rag_system_workspace/rag_artifacts/vectorstore/minilm_l6/faiss_index.bin"
}
```

Acts as a record of how the index was built. If you rebuild with different settings, you can compare build summaries to understand what changed.

---

## How search works against this index

**Script:** `rag_system_workspace/scripts/search_local_embeddings.py`
**Also used by:** `ask_rag.py` and `app.py`

### Step-by-step

```python
# 1. Embed the query
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
query_vector = model.encode(["How does CI/CD work?"],
                             normalize_embeddings=True).astype("float32")
# shape: (1, 384)

# 2. Search FAISS — get top 200 candidates
scores, indices = index.search(query_vector, k=200)
# scores: similarity scores (higher = better, max = 1.0 after normalization)
# indices: row numbers in the index

# 3. Apply metadata filters manually
for score, idx in zip(scores[0], indices[0]):
    m = metadata[idx]
    if m["folder_profile"] != "operations_docs":
        continue      # skip rows not matching the filter
    # collect this result

# 4. Return top-k after filtering
```

**Why search 200 first, then filter?**
If you ask FAISS for top-5 directly and then filter, you might discard all 5 and get nothing. By searching a wider pool (200) first, you have enough candidates to filter down to a meaningful top-k that passes all conditions.

### Understanding scores

After `normalize_embeddings=True`, scores are cosine similarities:

| Score | Meaning |
|---|---|
| 1.0 | Identical vectors (same text) |
| 0.7 – 0.9 | Very high semantic similarity |
| 0.4 – 0.6 | Moderate match — same topic, different focus |
| < 0.3 | Weak match — likely off-topic |

In the test run on `"What is CI/CD and how does it work?"` the top result scored **0.5685** from `CI_CD_INTEGRATION.md` — a good match for a factual technical question.

---

## How to rebuild the FAISS index

Run when you add new docs, rechunk existing docs, or want to try a different embedding model.

**Step 1 — Rechunk (if source docs changed):**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\chunk_markdown_docs.py
```

**Step 2 — Rebuild embeddings and FAISS index:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\build_local_embeddings.py `
  --model-name sentence-transformers/all-MiniLM-L6-v2 `
  --batch-size 128 `
  --normalize `
  --output-name minilm_l6
```

**To try a different model (saves to a separate folder):**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\build_local_embeddings.py `
  --model-name BAAI/bge-small-en-v1.5 `
  --normalize `
  --output-name bge_small
```

Now `rag_artifacts/vectorstore/bge_small/` contains a parallel index. You can search either by passing `--index-name bge_small` to `ask_rag.py`.

---

## Complete file reference

| File | Size | What it is |
|---|---|---|
| `faiss_index.bin` | 1.4 MB | FAISS binary index (search engine) |
| `metadata.jsonl` | 250 KB | 979 chunk metadata rows, aligned with index |
| `embeddings.npy` | 1.4 MB | Raw 979×384 float32 matrix (numpy) |
| `build_summary.json` | tiny | Build config receipt |
| `rag_artifacts/chunks/**/*.chunks.jsonl` | ~5 MB | Source chunk text + full metadata |
| `rag_artifacts/chunks/chunking_run_summary.json` | tiny | Stats per profile from last chunk run |

---

## Visual summary of how it all connects

```
input_docs/ (89 .md files)
    │
    ▼  chunk_markdown_docs.py
chunks/ (979 .chunks.jsonl records)
    │
    ▼  build_local_embeddings.py → all-MiniLM-L6-v2
vectorstore/minilm_l6/
    ├── faiss_index.bin      ← search engine
    ├── metadata.jsonl       ← chunk labels (aligned by row)
    ├── embeddings.npy       ← raw vectors (for analysis)
    └── build_summary.json   ← build receipt
    │
    ▼  ask_rag.py / app.py / search_local_embeddings.py
User query → embed → FAISS search → metadata filter → top-k chunks
    │
    ▼  Ollama (qwen2.5-coder:3b)
Final answer grounded in your documents
```
