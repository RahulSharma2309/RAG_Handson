# RAG Answer Generation with Ollama + Gradio UI

## The missing half of RAG

Up to the retrieval step, your system could find relevant chunks — but it could not talk back.
A human still had to read the chunks and form an answer.

**RAG = Retrieval + Generation.**

This phase completes the loop:

```
Your question
     ↓
Embed question → search FAISS → get top chunks
     ↓
Pack chunks into a prompt as "context"
     ↓
Send prompt to a Large Language Model (LLM)
     ↓
LLM reads context and writes a human-readable answer
     ↓
You get an answer with sources cited
```

Think of it like hiring a consultant. The retrieval step is the research librarian who finds the right books. The LLM is the consultant who reads those books and writes you a clear summary. You get the best of both: a grounded, specific answer backed by your actual documents.

---

## Why Ollama? Why local?

| Option | Cost | Privacy | Speed | Setup |
|---|---|---|---|---|
| Ollama (local Docker) | Free | Your data never leaves your machine | Fast once loaded | docker start |
| OpenAI GPT-4 | Paid per token | Data sent to OpenAI servers | Fastest | API key |
| Groq (hosted Llama) | Free tier | Data sent to Groq servers | Very fast | API key |
| HuggingFace Inference API | Free tier | Data sent to HF servers | Moderate | API key |

For learning, Ollama is the best choice because:
- Zero cost
- Works offline
- Your documents stay private
- Identical API to cloud models — swap is one line later

---

## The Ollama setup (Docker)

Ollama is an application that hosts LLM models and exposes them via a simple HTTP API on your machine. You interact with it through `localhost:11434`.

```
Docker container "ollama"
  └── Ollama server running
        ├── model: qwen2.5-coder:3b   (1.9 GB, already pulled)
        └── model: nomic-embed-text   (274 MB, for embeddings)
```

**Start the container:**
```powershell
docker start ollama
```

**Check what models are available:**
```powershell
docker exec ollama ollama list
```

**Pull a new model (example):**
```powershell
docker exec -it ollama ollama pull llama3.2
```

---

## `ask_rag.py` — The full RAG pipeline script

**File:** `rag_system_workspace/scripts/ask_rag.py`

This script is the command-line version of the full RAG pipeline. Run it from your terminal to get answers from your knowledge base.

### How it works — step by step

#### Step 1: Load the FAISS index and metadata
```python
index    = faiss.read_index(str(index_path))
metadata = load_metadata(metadata_path)
text_map = load_chunk_texts(CHUNKS_DIR)
```
- `faiss_index.bin` — the vector search engine (979 vectors)
- `metadata.jsonl` — chunk details (source file, section title, profile)
- `*.chunks.jsonl` — the actual text of each chunk

#### Step 2: Embed the query
```python
qv = model.encode([query], normalize_embeddings=True).astype("float32")
```
Your question gets converted into the same 384-dimensional vector space as all the stored chunks.

#### Step 3: Search FAISS
```python
scores, indices = index.search(qv, k_pool)
```
FAISS returns the 200 closest chunks (the pool) instantly. Then metadata filters narrow this down to the top-k that match your profile or source filter.

#### Step 4: Build the prompt
```python
context = "\n\n---\n\n".join(
    f"[Source: {c['source_file']} | Section: {c['section_title']}]\n{c['text']}"
    for c in chunks
)
prompt = PROMPT_TEMPLATE.format(context=context, question=question)
```

The prompt wraps your question with retrieved context. The instruction is explicit:
> "Use ONLY the context below to answer. If it's not there, say so."

This constraint is critical. Without it, the LLM will hallucinate (make up plausible-sounding but wrong answers from its training data). With it, the LLM is forced to stay grounded in your actual documents.

#### Step 5: Ask Ollama
```python
client   = ollama.Client(host="http://localhost:11434")
response = client.chat(model="qwen2.5-coder:3b",
                       messages=[{"role": "user", "content": prompt}])
answer   = response.message.content
```

The Ollama Python client sends the prompt to the Docker container. The LLM generates the answer and returns it. Your documents never leave your machine.

---

### How to run `ask_rag.py`

**From project root:**
```powershell
cd "c:\Users\Lenovo\source\repos\AIML\RAG_Handson"
docker start ollama
```

**Basic question:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "How does the CI/CD pipeline work?"
```

**Show the retrieved chunks (recommended when learning):**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "How does the CI/CD pipeline work?" --show-chunks
```

**Filter by domain:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "Sprint planning process" --profile product_owner_docs
```

**Retrieve more context for broad questions:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --query "Explain the full tech stack" --top-k 6
```

**List available domain profiles:**
```powershell
.venv\Scripts\python.exe rag_system_workspace\scripts\ask_rag.py --list-profiles
```

### All available arguments

| Argument | Default | What it does |
|---|---|---|
| `--query` | (required) | Your question |
| `--top-k` | 4 | How many chunks to send as context |
| `--pool-size` | 200 | FAISS candidates before filtering |
| `--profile` | (none) | Filter results to a specific domain |
| `--source-contains` | (none) | Filter by source filename substring |
| `--show-chunks` | off | Print the retrieved chunks before the answer |
| `--ollama-model` | `qwen2.5-coder:3b` | Which Ollama model to use |
| `--list-profiles` | off | Show all available profiles and exit |

---

## `app.py` — The Gradio Chat UI

**File:** `rag_system_workspace/app.py`

The same RAG pipeline wrapped in a browser-based chat interface. Instead of running commands in a terminal, you type questions in a chat window and get answers back in real time.

### How to start the UI

```powershell
docker start ollama
.venv\Scripts\python.exe rag_system_workspace\app.py
```

Then open your browser at: **http://localhost:7860**

### What the UI gives you

**Chat window** — full conversation history. Each question and answer is kept so you can compare responses.

**Sidebar controls:**

| Control | What it does |
|---|---|
| Chunks to retrieve (slider) | Higher = more context, slower answer |
| Filter by domain (dropdown) | Narrows the search to one knowledge domain |
| Show sources (checkbox) | Each answer shows which files and sections were used |

**Clear chat button** — wipes the conversation history to start fresh.

### How the UI is built

The entire UI is built with Gradio — a Python library that turns functions into browser interfaces with no HTML or CSS needed.

The `chat()` function does the work:
1. Takes `question` + `history` (previous messages)
2. Calls `retrieve()` → FAISS search → top-k chunks
3. Calls `ask_ollama()` → sends to Docker → gets answer
4. Appends both user message and assistant answer to `history`
5. Returns updated history to Gradio (which re-renders the chat)

`@lru_cache` is used on the index loader and embedding model loader so they are only loaded once on first use, not on every question. This makes subsequent questions much faster.

### Why Gradio over other options?

| Option | Pros | Cons |
|---|---|---|
| **Gradio (used)** | 1 file, pure Python, instant | Less customizable |
| Streamlit | Clean UI, more widgets | Version dependency issues (we hit this) |
| Flask + HTML | Fully custom | Requires frontend code |
| FastAPI + React | Production-grade | Complex setup |

For a learning project, Gradio is the right choice. When moving to production, you would replace it with a proper frontend.

---

## The `qwen2.5-coder:3b` model

This is the model already present in your Ollama Docker container.

- **What it is:** Qwen 2.5 Coder, 3 billion parameter version by Alibaba
- **Size:** 1.9 GB
- **Strength:** Good at reasoning about technical content, code, and structured text — exactly what your knowledge base contains
- **Speed on CPU:** ~30–90 seconds per response depending on context length
- **Context window:** Large enough to fit 4–6 chunks comfortably

If you want a faster response and are ok with slightly less quality, pull:
```powershell
docker exec -it ollama ollama pull phi3
```
`phi3` is smaller (~2GB) but faster.

---

## Grounding vs Hallucination — why the prompt matters

The most important part of the RAG prompt is this line:

> "Use ONLY the context below to answer. If the answer is not in the context, say 'I don't have enough information in the knowledge base.'"

**Without this instruction:**
The LLM will mix your document content with knowledge from its training data. The answer sounds confident but may be factually wrong for your specific system.

**With this instruction:**
The LLM is constrained to what is in your documents. When a question falls outside your knowledge base, it says so honestly rather than guessing.

This is the core value of RAG — not just augmented answers, but *grounded, trustworthy* answers.

---

## Files involved

| File | Role |
|---|---|
| `rag_system_workspace/scripts/ask_rag.py` | CLI tool — full RAG pipeline |
| `rag_system_workspace/app.py` | Browser UI — same pipeline, chat interface |
| `rag_artifacts/vectorstore/minilm_l6/` | FAISS index + metadata used for retrieval |
| `rag_artifacts/chunks/` | Source chunk texts |

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `Ollama error: Connection refused` | Docker not running | `docker start ollama` |
| Answer is very slow | Model loading on first use | Wait 30–60s, faster after that |
| Answer ignores your question | top-k too low, wrong chunks retrieved | Use `--show-chunks` to inspect, increase `--top-k` |
| "I don't have enough information" | Question is outside your docs | That is correct behaviour — add docs or rephrase |
| UI shows "Data incompatible with messages format" | Gradio version mismatch | Ensure history uses `{"role": ..., "content": ...}` dicts |
