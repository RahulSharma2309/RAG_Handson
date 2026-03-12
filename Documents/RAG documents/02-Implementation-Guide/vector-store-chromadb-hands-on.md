# ChromaDB Vector Store — Hands-on Guide

## What is a Vector Store and why do you need one?

Imagine you have hundreds of index cards (chunks) sitting on the floor.
You want to find the three most relevant ones for a question you just asked.
A vector store is like a super-smart filing cabinet. You put all your index cards in once.
Then whenever you ask a question, it instantly hands you back only the relevant ones — not by keyword, but by meaning.

FAISS (used earlier) is a raw search library. ChromaDB is a full vector database — it stores vectors, metadata, and text together in one place and gives you a cleaner API to work with.

---

## What was built in `Handson Learning/2-VectorStore/1-CromaDb.ipynb`

This notebook walks through the complete journey from raw text to a searchable, persistent vector store using ChromaDB as the storage engine and HuggingFace embeddings as the model.

### Step-by-step walkthrough

#### Cell 0 — Load environment variables
```python
import os
from dotenv import load_dotenv
load_dotenv()
```
This loads any API keys stored in a `.env` file. Not strictly needed for local models but good practice — if you swap in an OpenAI or HuggingFace API-based model later, keys are already wired in.

---

#### Cell 1 — Imports
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
import numpy as np
```

**Why these specific packages?**

| Package | What it does | Why it matters |
|---|---|---|
| `langchain_text_splitters` | Splits long text into chunks | LangChain moved splitters to a dedicated package in v0.2 |
| `langchain_community.document_loaders` | Loads text files into Document objects | Standard LangChain way to ingest files |
| `langchain_huggingface` | Wraps HuggingFace models for LangChain | Lets you use any HuggingFace model with 3 lines |
| `langchain_core.documents` | The `Document` data class | Carries `page_content` + `metadata` together |
| `langchain_community.vectorstores` | ChromaDB integration | Handles storage + retrieval via Chroma |

> **Common error you already hit:** `from langchain.text_splitter` — this was the old path. After LangChain v0.2 it moved to `langchain_text_splitters`. Same for `Document` which moved from `langchain.schema` to `langchain_core.documents`.

---

#### Cell 2 — Sample documents (your "library")

Three multi-paragraph documents about:
- **Deep Learning** — neural networks, CNNs, RNNs, frameworks
- **Machine Learning** — supervised/unsupervised/reinforcement, algorithms, bias-variance
- **NLP** — Transformers, BERT/GPT, tasks like classification, translation, QA

These simulate a real knowledge base. The topics are related but distinct — perfect for testing whether the vector store retrieves the *right* document for each question.

---

#### Cell 3 — Write docs to temp files
```python
import tempfile
with open(f"{tempdir}/doc_{i}.txt", "w", encoding="utf-8") as f:
    f.write(doc)
```

**Why `encoding="utf-8"`?**
The documents contain em-dashes (`—`) and other Unicode characters. Without specifying UTF-8 on write, Windows saves in `cp1252` (its default). Then LangChain reads expecting UTF-8 and crashes with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97`.
Always specify encoding on both write and read to prevent this.

---

#### Cell 4 — Load documents using DirectoryLoader
```python
loader = DirectoryLoader(tempdir, glob="*.txt", loader_cls=TextLoader,
                         loader_kwargs={"encoding": "utf-8"})
documents = loader.load()
```

`DirectoryLoader` scans a folder and loads all matching files. Each file becomes a LangChain `Document` object with:
- `page_content` — the raw text
- `metadata["source"]` — file path (auto-set by LangChain)

Think of it as the library intake desk that stamps each new book with its shelf location.

---

#### Cell 5 — Chunk the documents
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)
```

**What this does:**
- 3 documents become 9 chunks (each document splits into ~3 pieces of ~500 characters)
- `chunk_overlap=50` means consecutive chunks share 50 characters — ensures context is not cut off at boundaries
- `separators` hierarchy: tries to split at paragraph breaks first, then line breaks, then spaces, then individual characters as last resort

**Why splitting matters:**
If you fed a 3000-character document directly to an embedding model, the vector would represent the "average" meaning of the whole document. A specific question about CNNs would not score well against a paragraph that also mentions PyTorch and JAX. Smaller, focused chunks make retrieval more precise.

---

#### Cell 6 — Generate embeddings with HuggingFace
```python
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
vectors = embedding_model.embed_documents(chunk_texts)
```

**What happens here:**
Each chunk's text is converted into a 384-number vector. Two chunks that discuss similar ideas will have vectors that point in similar directions in 384-dimensional space. This is what enables meaning-based search.

`normalize_embeddings=True` scales each vector to length 1, which makes dot-product equal to cosine similarity — a standard way to measure how related two texts are.

**Why `all-MiniLM-L6-v2`?**
- Free, runs offline on CPU
- 384 dimensions (small and fast)
- Trained specifically for semantic similarity tasks
- Same model used in the RAG system workspace

---

#### Cell 7 — Inspect similarity
```python
vectors_np = np.array(vectors)
similarities = vectors_np @ vectors_np[0]  # dot product = cosine similarity after normalization
```

This is the raw math behind semantic search:
- Take vector of chunk 0 (Deep Learning intro)
- Compute dot product with every other chunk's vector
- Deep Learning chunks score ~0.9 against each other
- NLP/ML chunks score ~0.5–0.6 against Deep Learning chunks
- This proves the model understands meaning, not just keywords

---

#### Cell 9 — Store in ChromaDB
```python
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name="ml_knowledge_base",
    persist_directory="./chroma_store"
)
```

**What ChromaDB does that raw FAISS does not:**
- Stores the text and metadata alongside the vectors (FAISS only stores vectors)
- Gives you a `collection` concept (like a named table in a database)
- Automatically handles embedding when you add new documents
- `persist_directory` saves to disk — survives kernel restarts

Think of FAISS as a lookup table. ChromaDB is the full filing cabinet.

---

#### Cell 10 — Semantic search
```python
results = vectorstore.similarity_search("What is Deep Learning?", k=3)
```

Returns top-3 most semantically similar chunks to your query. No keyword matching — pure meaning-based retrieval.

---

#### Cell 11 — Search with scores
```python
results_with_scores = vectorstore.similarity_search_with_score(query, k=3)
```

Same as above but each result also shows a **distance score**:
- Score near `0` = very close match (in ChromaDB's default L2 distance, lower is better)
- Score `> 1` = weak or unrelated match

---

## Key lessons from this notebook

| Lesson | What it means in practice |
|---|---|
| Always specify `encoding="utf-8"` | Prevents Unicode errors on Windows with special characters |
| Use `chunk_overlap` | Avoids cutting off sentences at chunk boundaries |
| Use hierarchy separators | Gives the splitter a preference order — paragraph > line > word > char |
| Normalize embeddings | Enables cosine similarity via simple dot product |
| ChromaDB stores text + vectors together | Easier to inspect and debug than raw FAISS |

---

## Files involved

| File | Role |
|---|---|
| `Handson Learning/2-VectorStore/1-CromaDb.ipynb` | The hands-on notebook |
| `chroma_store/` | Persisted ChromaDB on disk (auto-created) |

---

## Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: langchain.text_splitter` | Old import path | Use `from langchain_text_splitters import ...` |
| `UnicodeDecodeError: 0x97` | File written without UTF-8 | Add `encoding="utf-8"` to both write and read |
| `TypeError: chunks_size` | Typo in parameter name | Use `chunk_size` (no `s`) |
| `TypeError: w is not defined` | Missing quotes around mode | Use `"w"` not `w` in `open()` |
