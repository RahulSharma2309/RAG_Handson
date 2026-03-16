# 01 — Environment Setup: Chunking Phase

> This document explains every step taken to set up the Python environment for the chunking hands-on phase. Every command is documented with an explanation of what it does and why it is done that way.

---

## What Was Set Up

A clean Python project with `uv` as the package manager, containing only the libraries needed for the chunking phase. No LLM, no vector database, no UI framework — just the tools required to load documents, split them into chunks, and inspect the results.

---

## Folder Structure Created

```
RAG_Handson/
├── Documents/                             ← existing reference docs
├── RAG_Overall_documentation/             ← existing theory docs
│   ├── Chunking/                          ← chunking theory guides
│   └── Actual_Implementation_Documents/   ← this folder (implementation docs)
│       ├── README.md
│       └── 01-Environment-Setup-Chunking-Phase.md  ← this file
│
└── Handson/                               ← ALL hands-on code lives here
    ├── 01-Chunking/                       ← first practice module
    │   ├── notebooks/                     ← Jupyter notebooks go here
    │   └── data/                          ← sample documents for testing
    ├── .python-version                    ← locks Python version to 3.13
    ├── .env.example                       ← template for API keys
    ├── .gitignore                         ← what NOT to commit to GitHub
    ├── pyproject.toml                     ← project config + dependencies
    └── main.py                            ← uv creates this by default (can ignore)
```

**Why keep Handson at root level?**  
So you can open it directly in VS Code as its own folder and the Python interpreter, kernel, and imports all work from the correct base path. Keeping code and documentation separate also makes the repo easier to navigate.

---

## Tool: Why uv?

`uv` is a modern, very fast Python package manager written in Rust. It replaces `pip` + `virtualenv` + `pip-tools` in one tool.

Why use it instead of pip:
- Creates a virtual environment automatically
- Locks exact package versions in `uv.lock` (reproducible installs)
- 10–100x faster than pip for installs
- `pyproject.toml` is the single source of truth for all dependencies
- Adding a new package: `uv add package-name` — it updates `pyproject.toml` automatically

---

## Step 1: Create the Folder Structure

```powershell
# Run from RAG_Handson root
mkdir Handson
mkdir Handson\01-Chunking
mkdir Handson\01-Chunking\notebooks
mkdir Handson\01-Chunking\data
```

**What this creates:**
- `Handson/` — the root of all hands-on work
- `01-Chunking/` — first module, numbered so modules stay in order
- `notebooks/` — Jupyter notebooks for practice
- `data/` — sample files (PDFs, CSVs, etc.) used as chunking input

---

## Step 2: Initialize the uv Project

```powershell
# Navigate into the Handson folder
cd Handson

# Initialize a new uv project (creates pyproject.toml, .python-version, main.py)
uv init --no-workspace

# Pin Python version to 3.13
uv python pin 3.13
```

**What `uv init --no-workspace` does:**
- Creates `pyproject.toml` — the project configuration file
- Creates `.python-version` — tells uv and VS Code which Python to use
- Creates an empty `main.py`
- `--no-workspace` means this project stands alone (not nested inside a uv workspace)

**What `uv python pin 3.13` does:**
- Writes `3.13` into `.python-version`
- Now every `uv` command in this folder will use Python 3.13
- VS Code will also pick this up when you select the interpreter

**After this step, `.python-version` contains:**
```
3.13
```

---

## Step 3: Define Chunking-Only Dependencies

The `pyproject.toml` was updated with exactly the libraries needed for chunking — nothing more.

**Why not install everything at once?**  
Installing the full RAG stack (LLMs, vector DBs, UI frameworks) would:
- Take much longer to install
- Make it harder to understand which library does what
- Add confusion when learning one thing at a time

Learning in phases: chunking → embeddings → vector DB → retrieval → generation.  
Each phase adds only what it needs.

**Libraries installed and why each one is needed:**

| Library | Why It Is Needed |
|---|---|
| `langchain` | Contains all the text splitters: `RecursiveCharacterTextSplitter`, `CharacterTextSplitter`, `TokenTextSplitter`, `MarkdownHeaderTextSplitter` |
| `langchain-community` | Contains all document loaders: `PyMuPDFLoader`, `CSVLoader`, `JSONLoader`, `Docx2txtLoader`, `DirectoryLoader` |
| `langchain-huggingface` | LangChain wrapper that lets you use HuggingFace models inside LangChain code — needed for `SemanticChunker` |
| `sentence-transformers` | Provides free, local embedding models like `all-MiniLM-L6-v2` — required to run semantic chunking without paying for an API |
| `tiktoken` | OpenAI's tokenizer — counts tokens accurately so you can verify chunks are within model context limits |
| `pymupdf` | Fast, high-quality PDF text extraction. Used by `PyMuPDFLoader`. Better than pypdf for most PDFs |
| `pypdf` | Fallback PDF loader. More compatible with some PDF formats. Used by `PyPDFLoader` |
| `docx2txt` | Extracts text from `.docx` Word files. Used by `Docx2txtLoader` |
| `pandas` | Reads CSV and Excel files. Used for custom CSV chunking patterns |
| `openpyxl` | Excel format support (`.xlsx`). pandas needs this to read Excel files |
| `jq` | JSON query language. Required by LangChain's `JSONLoader` for extracting specific fields from JSON |
| `ipykernel` | Allows Jupyter notebooks to run inside VS Code using the project's virtual environment |
| `ipywidgets` | Notebook widgets (progress bars, interactive elements) |
| `python-dotenv` | Reads `.env` files. Loads API keys as environment variables without hardcoding them |

**Libraries intentionally NOT installed yet:**

| Library | Why Skipped |
|---|---|
| `chromadb`, `faiss-cpu` | Vector databases — needed in embeddings phase, not chunking |
| `langchain-openai`, `langchain-groq` | LLM integrations — needed in generation phase |
| `gradio`, `streamlit` | UI frameworks — needed in application phase |
| `unstructured` | Complex document parser — heavy install, add only if standard loaders fail |

---

## Step 4: Install the Dependencies

```powershell
# From inside the Handson folder
uv sync
```

**What `uv sync` does:**
- Reads `pyproject.toml`
- Creates a `.venv/` virtual environment inside `Handson/`
- Installs all listed dependencies and their dependencies
- Writes exact versions to `uv.lock`

**Result:** 121 packages installed in ~24 seconds.

**What `.venv/` is:**  
A self-contained Python installation for this project only. When you activate it (or VS Code uses it), you get exactly these libraries — nothing from other projects interferes.

---

## Step 5: Create `.env.example`

```
# Copy this file to .env and fill in your keys
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
HUGGINGFACE_API_KEY=your_hf_key_here
```

**Why `.env.example` and not `.env`?**  
- `.env` contains real API keys — must never be committed to GitHub
- `.env.example` is a template showing what keys are needed — safe to commit
- When you start: copy `.env.example` → `.env`, fill in your real keys

For the chunking phase: **no API keys are needed at all**. All chunking and semantic chunking uses free local models. The `.env.example` is preparation for later phases.

---

## Step 6: Create `.gitignore`

```
.venv/         ← never commit — 100MB+ of installed packages
.env           ← never commit — contains real API keys
__pycache__/   ← never commit — Python bytecode cache
*.pyc          ← never commit — compiled Python files
uv.lock        ← optional: commit for exact reproducibility
```

**Why `.venv/` must never be committed:**
- It contains hundreds of megabytes of installed packages
- It is machine-specific — Windows vs Mac vs Linux paths differ
- Anyone else runs `uv sync` and gets the exact same environment from `pyproject.toml`

---

## Step 7: Connect VS Code to the Right Interpreter

After setup, tell VS Code to use the project's virtual environment:

1. Open VS Code in the `Handson/` folder (or the root `RAG_Handson/` folder)
2. Press `Ctrl+Shift+P` → type `Python: Select Interpreter`
3. Choose the interpreter at: `Handson\.venv\Scripts\python.exe`
4. For notebooks: press `Ctrl+Shift+P` → `Notebook: Select Kernel` → choose the same `.venv` Python

**How to verify it is working:**

Open a terminal in VS Code and run:
```python
# Quick verification
python -c "import langchain; import pymupdf; import tiktoken; print('All chunking libraries ready')"
```

Expected output:
```
All chunking libraries ready
```

---

## Step 8: How to Add a New Library Later

When you need a new package (for example, adding `chromadb` in the embeddings phase):

```powershell
# From inside the Handson folder
uv add chromadb
```

This automatically:
- Installs the package into `.venv`
- Adds it to `pyproject.toml` with the correct version
- Updates `uv.lock`

Do NOT use `pip install` — it bypasses uv and breaks version tracking.

---

## Final State After This Setup

```
Handson/
├── 01-Chunking/
│   ├── notebooks/     ← empty, ready for your first notebook
│   └── data/          ← empty, add sample docs here for practice
├── .venv/             ← Python virtual environment (121 packages)
├── .python-version    ← "3.13"
├── .env.example       ← API key template
├── .gitignore         ← protects secrets and large files
├── pyproject.toml     ← project config + 14 chunking dependencies
└── main.py            ← created by uv init (can ignore for now)
```

---

## What Comes Next

With the environment ready, the next step is hands-on chunking practice.

The `01-Chunking/notebooks/` folder is where you will create Jupyter notebooks covering:
1. Loading different document types (PDF, CSV, DOCX, JSON, Markdown)
2. Applying different text splitters and comparing results
3. Inspecting chunks — what they contain, how many tokens, what the overlap looks like
4. Semantic chunking using the local `all-MiniLM-L6-v2` model
5. Adding metadata to chunks

Each notebook will have a corresponding documentation file in `Actual_Implementation_Documents/`.

---

## Troubleshooting

**Problem:** `uv` is not recognized  
**Fix:** Install uv → `pip install uv` or follow https://docs.astral.sh/uv/getting-started/installation/

**Problem:** VS Code does not show `.venv` as an interpreter option  
**Fix:** Open the `Handson/` folder directly in VS Code, then select interpreter. The `.venv` must be inside the folder VS Code has open.

**Problem:** `import langchain` fails in a notebook  
**Fix:** Make sure the notebook kernel is set to `Handson/.venv/Scripts/python.exe` — not the system Python or Anaconda.

**Problem:** `uv sync` fails with network error  
**Fix:** Check internet connection. Try `uv sync --no-cache` to force fresh download.
