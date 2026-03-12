# Files Created and Why They Matter

This is the practical map of what was created in your RAG workspace.

## Source knowledge base

- `../../rag/input_docs/`
  - all markdown docs that act as your knowledge source
  - this is the "raw library"

## Chunking layer outputs

- `../../rag_artifacts/chunks/**/*.chunks.jsonl`
  - chunked text + metadata records
  - these are your "searchable index cards"

- `../../rag_artifacts/chunks/chunking_run_summary.json`
- `../../rag_artifacts/chunks/chunking_run_summary.md`
  - stats by profile/folder (coverage, chunk counts, avg size)
  - useful to track changes after tuning chunk strategy

## Embedding/vector layer outputs

- `../../rag_artifacts/vectorstore/minilm_l6/faiss_index.bin`
  - FAISS index used for semantic nearest-neighbor search

- `../../rag_artifacts/vectorstore/minilm_l6/metadata.jsonl`
  - metadata aligned by row/index with FAISS vectors

- `../../rag_artifacts/vectorstore/minilm_l6/embeddings.npy`
  - raw embedding matrix (numpy array)
  - useful for analysis/debugging

- `../../rag_artifacts/vectorstore/minilm_l6/build_summary.json`
  - build settings and summary (model, vector dim, total chunks)

## Scripts and purpose

- `../../scripts/chunk_markdown_docs.py`
  - reads source markdown docs
  - applies profile-based chunking
  - writes JSONL chunk artifacts

- `../../scripts/build_local_embeddings.py`
  - reads chunk JSONL
  - creates local embeddings with free model
  - builds FAISS index + metadata outputs

- `../../scripts/search_local_embeddings.py`
  - semantic retrieval from FAISS
  - supports metadata filters (`profile`, `source-contains`, `section-contains`)

- `../../scripts/ask_rag.py`
  - full RAG pipeline: retrieve from FAISS + generate answer with Ollama LLM
  - CLI tool — run from terminal with `--query`, `--profile`, `--show-chunks`
  - uses `qwen2.5-coder:3b` running in Docker via Ollama
  - grounds every answer in retrieved chunks (no hallucination)

## UI layer

- `../../app.py`
  - Gradio browser-based chat UI
  - wraps the same RAG pipeline as `ask_rag.py`
  - domain filter dropdown, source visibility toggle, chunk count slider
  - run with: `.venv\Scripts\python.exe rag_system_workspace\app.py`
  - open at: `http://localhost:7860`

## Hands-on notebooks

- `Handson Learning/2-VectorStore/1-CromaDb.ipynb`
  - end-to-end demonstration: load docs → chunk → embed → store in ChromaDB → search
  - uses `HuggingFaceEmbeddings` (all-MiniLM-L6-v2) + `Chroma` vectorstore
  - shows both plain search and search with similarity scores
  - final cells connect ChromaDB retrieval to Ollama LLM via LangChain RAG chain

## Why this architecture is significant

- clean separation of stages:
  - source → chunk → embed → retrieve → generate
- every stage is independently runnable and swappable
- LLM is pluggable — swap Ollama for OpenAI/Groq by changing one line
- vector store is pluggable — FAISS (scripts) and ChromaDB (notebook) both shown
- UI is separate from logic — `app.py` calls the same functions as `ask_rag.py`
- grounding via prompt constraint prevents hallucination
- better maintainability for future production migration
