# Start Here - RAG Workspace

If you are opening this project fresh, start from this file.

## What this project is

You built a practical RAG playground from real docs.

In simple words:
- You have many markdown knowledge files (your "library")
- You split them into meaningful chunks (your "index cards")
- You convert chunks into vectors/embeddings (your "GPS coordinates for meaning")
- You store them in FAISS to search semantically (your "smart lookup engine")

## What is already done

- Structured source docs kept in `../../rag/input_docs/`
- All docs chunked into JSONL in `../../rag_artifacts/chunks/`
- Local free embeddings generated for all chunks (979 vectors, 384 dimensions)
- FAISS index created in `../../rag_artifacts/vectorstore/minilm_l6/`
- Semantic search script with metadata filtering is ready
- Full RAG pipeline (retrieval + Ollama LLM answer generation) is ready
- ChromaDB vector store hands-on notebook is ready
- Gradio browser chat UI is ready at `http://localhost:7860`

## Where to run from

Run all commands from project root:

`C:\Users\Lenovo\source\repos\AIML\RAG_Handson`

## Quick command list

**1) Start Ollama (required before asking questions):**
```powershell
docker start ollama
```

**2) Launch the chat UI (easiest way to use the system):**
```powershell
.venv\Scripts\python.exe rag_system_workspace\app.py
```
Then open: http://localhost:7860

**3) Ask a question from terminal (no UI):**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "How does CI/CD work?" --show-chunks
```

**4) Rebuild chunks (if you update source docs):**
```powershell
.venv\Scripts\python.exe rag_system_workspace/scripts/chunk_markdown_docs.py
```

**5) Rebuild embeddings (after rechunking):**
```powershell
.venv\Scripts\python.exe rag_system_workspace/scripts/build_local_embeddings.py --model-name sentence-transformers/all-MiniLM-L6-v2 --batch-size 128 --normalize --output-name minilm_l6
```

**6) Raw semantic search (retrieval only, no LLM):**
```powershell
.venv\Scripts\python.exe rag_system_workspace/scripts/search_local_embeddings.py --query "how deployment trigger works" --normalize --profile operations_docs --top-k 5
```

**7) List available knowledge domains:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --list-profiles
```

## Best next read

- `../01-Foundations/chunking-and-embedding-in-layman-terms.md`
- `../02-Implementation-Guide/vector-store-chromadb-hands-on.md`
- `../02-Implementation-Guide/rag-answer-generation-and-ui.md`
- `../02-Implementation-Guide/files-created-and-why-they-matter.md`
- `../04-Roadmap/rag-hands-on-roadmap.md`
