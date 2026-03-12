# Tools and Options at Every RAG Step

> At every single step in a RAG pipeline, you have multiple choices.
> This document maps out every option at every step — free vs paid, simple vs advanced, and which one to use when.
> The choices made in THIS project are highlighted with ✅.

---

## Step 1: Document Loading

You need to get text out of your source files and into Python.

### Options

| Tool | Formats supported | Free? | Complexity | Used in project? |
|---|---|---|---|---|
| `langchain_community.document_loaders.TextLoader` | `.txt` | Free | Simplest | ✅ Used in ChromaDB notebook |
| `langchain_community.document_loaders.DirectoryLoader` | Folder of files | Free | Simple | ✅ Used in ChromaDB notebook |
| `langchain_community.document_loaders.PyPDFLoader` | PDF | Free | Simple | In `0-DataIngestParsing` notebook |
| `langchain_community.document_loaders.PyMuPDFLoader` | PDF (better quality) | Free | Simple | In `0-DataIngestParsing` notebook |
| `langchain_community.document_loaders.UnstructuredMarkdownLoader` | Markdown with structure | Free | Moderate | — |
| `langchain_community.document_loaders.WebBaseLoader` | Web pages (URL) | Free | Simple | — |
| `langchain_community.document_loaders.YoutubeLoader` | YouTube transcripts | Free | Simple | — |
| `langchain_community.document_loaders.GoogleDriveLoader` | Google Drive | Free (needs OAuth) | Complex | — |
| Custom Python (`open()`) | Any text format | Free | DIY | ✅ Used in `chunk_markdown_docs.py` |
| LlamaParse | PDF, complex layouts | Paid ($0.003/page) | Managed | — |
| Azure Document Intelligence | Any document type | Paid | Managed API | — |

### When to use what

- **Simple text or markdown files:** Use `TextLoader` or `DirectoryLoader` — done in 3 lines
- **PDFs with basic text:** `PyPDFLoader` works well
- **PDFs with tables, images, complex layout:** `PyMuPDFLoader` is better, or pay for LlamaParse for best quality
- **Your own custom format:** Write a simple Python `open()` loop — most transparent and controllable
- **Enterprise scale with many formats:** Look at Unstructured.io (open-source library with cloud option)

### What this project does

The RAG system workspace uses custom Python to read Markdown files directly (no LangChain loader dependency). The learning notebooks use LangChain loaders to demonstrate the standard approach.

---

## Step 2: Chunking

How you split your documents is the single biggest factor in retrieval quality.

### Splitting strategies

#### Strategy 1: Fixed character size (CharacterTextSplitter)
```python
from langchain_text_splitters import CharacterTextSplitter
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
```
- Splits at exactly N characters
- Simple and predictable
- **Problem:** Can cut mid-sentence or mid-paragraph, losing context
- **Use when:** Documents have no clear structure, you want simplicity

#### Strategy 2: Recursive character splitting (RecursiveCharacterTextSplitter)
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
```
- Tries to split at paragraph breaks first, then line breaks, then spaces, then characters
- Much smarter than fixed character split
- **Best general-purpose splitter for unstructured text**
- ✅ **Used in the ChromaDB notebook**

#### Strategy 3: Token-based splitting (TokenTextSplitter)
```python
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=256, chunk_overlap=32)
```
- Splits by tokens (the unit LLMs actually count) rather than characters
- More accurate when you care about fitting within a context window
- ~4 characters = 1 token (rough rule of thumb)
- **Use when:** You need precise control over context window usage

#### Strategy 4: Markdown-aware heading split (custom or MarkdownHeaderTextSplitter)
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("##", "section")])
```
- Splits at heading boundaries, preserving document structure
- Each chunk stays within its section
- Heading becomes metadata — very useful for filtering
- ✅ **Used in `chunk_markdown_docs.py`** (custom implementation)
- **Best for structured Markdown documentation**

#### Strategy 5: Semantic chunking
```python
from langchain_experimental.text_splitter import SemanticChunker
splitter = SemanticChunker(embeddings=embedding_model)
```
- Embeds sentences, then groups sentences with similar meaning into one chunk
- No arbitrary size limit — chunks follow natural topic boundaries
- **Slow** (needs to embed every sentence) and requires an embedding model upfront
- **Use when:** Document quality is high and you want maximum semantic precision
- Not used in this project (too slow for 89 files on CPU)

#### Strategy 6: Document-level (no chunking)
If each document is small enough, embed the entire document as one chunk. Works for short blog posts or single-topic notes. Fails for long multi-topic documents.

### Chunking tools comparison

| Tool | Strategy | Free? | Best for |
|---|---|---|---|
| `CharacterTextSplitter` | Fixed size | Free | Simple text, quick prototyping |
| `RecursiveCharacterTextSplitter` | Recursive by separator | Free | ✅ General purpose |
| `TokenTextSplitter` | By LLM tokens | Free | Precise context control |
| `MarkdownHeaderTextSplitter` | By heading | Free | ✅ Structured Markdown |
| `SemanticChunker` | By meaning similarity | Free | High-quality docs, slow |
| LangChain `HTMLHeaderTextSplitter` | By HTML heading | Free | Web pages |
| Custom Python + regex | Any logic you write | Free | ✅ Maximum control |
| LlamaParse + chunking | PDF-aware | Paid | Complex PDFs |
| Unstructured.io | Layout-aware | Free/Paid tiers | Complex docs at scale |

### Key chunk parameters to tune

| Parameter | Typical range | Effect |
|---|---|---|
| `chunk_size` | 200–1000 tokens | Smaller = precise; Larger = more context |
| `chunk_overlap` | 10–20% of chunk size | Too low = cut context; Too high = redundant |
| Split strategy | heading/paragraph/sentence | Affects coherence of each chunk |

---

## Step 3: Embedding Models

The embedding model converts your text into vectors. Quality here directly affects retrieval quality.

### Free models (run locally)

| Model | Dimensions | Size | Speed (CPU) | Quality | Best for |
|---|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | 90 MB | Fast | Good | ✅ **Used in this project** — general semantic similarity |
| `all-MiniLM-L12-v2` | 384 | 130 MB | Moderate | Better | Slightly higher quality than L6 |
| `all-mpnet-base-v2` | 768 | 420 MB | Slower | Very good | Higher quality, needs more RAM |
| `BAAI/bge-small-en-v1.5` | 384 | 130 MB | Fast | Very good | Strong retrieval, competitive with larger models |
| `BAAI/bge-base-en-v1.5` | 768 | 430 MB | Moderate | Excellent | Best free option for English retrieval tasks |
| `nomic-embed-text` | 768 | 274 MB | Fast | Excellent | Available in Ollama Docker — already on your machine |
| `intfloat/e5-small-v2` | 384 | 130 MB | Fast | Good | Strong at passage retrieval |

### Paid / API-based models

| Model | Provider | Dimensions | Cost | Quality |
|---|---|---|---|---|
| `text-embedding-3-small` | OpenAI | 1536 | $0.02 / 1M tokens | Excellent |
| `text-embedding-3-large` | OpenAI | 3072 | $0.13 / 1M tokens | Best-in-class |
| `embed-english-v3.0` | Cohere | 1024 | $0.10 / 1M tokens | Excellent |
| `embed-multilingual-v3.0` | Cohere | 1024 | $0.10 / 1M tokens | Best for non-English |
| Vertex AI Embeddings | Google | 768 | $0.025 / 1M chars | Very good |

### Cost comparison for THIS project (979 chunks, ~154 tokens avg = ~150,000 tokens)

| Model | One-time build cost | Monthly re-embed cost |
|---|---|---|
| MiniLM-L6 (local) | **$0** | **$0** |
| OpenAI text-embedding-3-small | ~$0.003 | ~$0.003 |
| OpenAI text-embedding-3-large | ~$0.02 | ~$0.02 |

For a small corpus like this, even paid APIs are cheap. But for enterprise (millions of chunks, frequent updates), the difference compounds.

### Which to pick?

- **Learning / local / free:** `all-MiniLM-L6-v2` (what this project uses) — perfect starting point
- **Better quality, still free:** `BAAI/bge-small-en-v1.5` — drop-in replacement, measurably better
- **Best free option:** `BAAI/bge-base-en-v1.5` — excellent, worth the extra 300 MB
- **Production with budget:** `text-embedding-3-small` (OpenAI) — minimal cost, top quality
- **Already in your Docker:** `nomic-embed-text` — already pulled, 768 dims, try it!

### The golden rule

> **The embedding model used at query time must be the same as the one used at build time.** If you rebuild with a different model, you must also rebuild the index. They are not interchangeable.

---

## Step 4: Vector Stores / Vector Databases

This is where the vectors are stored and searched. This step is so important it has its own dedicated document:

→ See `vector-store-vs-vector-database.md` for a complete breakdown.

**Quick summary:**

| Tool | Type | Free? | Persistence | Scale | Used in project? |
|---|---|---|---|---|---|
| FAISS | Library | Free | Manual (save to file) | Millions of vectors | ✅ Main system |
| ChromaDB | Local DB | Free | Automatic | Thousands-millions | ✅ Learning notebook |
| Pinecone | Cloud DB | Free tier / Paid | Cloud | Billions | — |
| Weaviate | Cloud/Self-hosted | Free tier / Paid | Yes | Billions | — |
| Qdrant | Cloud/Self-hosted | Free tier / Paid | Yes | Billions | — |
| pgvector | PostgreSQL extension | Free | Yes (PostgreSQL) | Millions | — |
| Milvus | Self-hosted | Free | Yes | Billions | — |

---

## Step 5: LLM for Generation

The retrieval step finds your chunks. The LLM reads them and writes the answer.

### Free / local options (Ollama)

Run models in Docker. No internet needed. No API key. Data stays local.

| Model | Size | Speed (CPU) | Quality | Best for |
|---|---|---|---|---|
| `qwen2.5-coder:3b` | 1.9 GB | ~30–90s/response | Good | ✅ **Already in your Docker** — technical/code content |
| `llama3.2:3b` | 2.0 GB | ~30–90s/response | Good | General Q&A |
| `phi3:mini` | 2.2 GB | ~30–60s/response | Good | Fast, efficient |
| `mistral:7b` | 4.1 GB | ~2–5 min/response | Very good | Better reasoning |
| `llama3.1:8b` | 4.7 GB | ~2–5 min/response | Excellent | Best free quality |
| `nomic-embed-text` | 274 MB | Fast | N/A | Embeddings only, already pulled |

**Pull a model into your Ollama Docker:**
```powershell
docker exec -it ollama ollama pull llama3.2
docker exec -it ollama ollama pull phi3:mini
```

### Paid / API options

| Model | Provider | Cost (per 1M tokens) | Quality | Context window |
|---|---|---|---|---|
| `gpt-4o-mini` | OpenAI | $0.15 in / $0.60 out | Very good | 128k tokens |
| `gpt-4o` | OpenAI | $2.50 in / $10 out | Excellent | 128k tokens |
| `claude-3-haiku` | Anthropic | $0.25 in / $1.25 out | Very good | 200k tokens |
| `claude-3-5-sonnet` | Anthropic | $3 in / $15 out | Best-in-class | 200k tokens |
| `gemini-1.5-flash` | Google | $0.075 in / $0.30 out | Very good | 1M tokens |
| `llama-3.1-70b` | Groq (hosted) | **Free tier** | Excellent | 128k tokens |
| `mixtral-8x7b` | Groq (hosted) | **Free tier** | Very good | 32k tokens |

### Free tier options worth knowing

**Groq** (groq.com): Hosts open-source models like Llama and Mixtral for free (with rate limits). Extremely fast (hardware-accelerated). Requires signup but no credit card for free tier.

```python
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-70b-versatile", api_key="your-free-key")
```

**Google Gemini free tier**: `gemini-1.5-flash` has a free tier (60 requests/minute).
```python
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key="your-free-key")
```

### Estimated cost for THIS project (queries per day)

Assuming 50 questions/day, each needing ~2000 tokens (4 chunks × 500 tokens) of context:

| Model | Daily cost | Monthly cost |
|---|---|---|
| Ollama local | **$0** | **$0** |
| Groq free tier | **$0** | **$0** |
| GPT-4o-mini | ~$0.01 | ~$0.30 |
| GPT-4o | ~$0.15 | ~$4.50 |
| Claude 3.5 Sonnet | ~$0.30 | ~$9.00 |

For personal learning, local Ollama is the right choice. For a team product, GPT-4o-mini is cheap and high quality.

### How to swap LLMs — LangChain makes this one line

```python
# Local Ollama (current)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen2.5-coder:3b", base_url="http://localhost:11434")

# Switch to Groq (free, fast)
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-70b-versatile", api_key="gsk_...")

# Switch to OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", api_key="sk-...")

# Everything else stays the same — same chain, same retriever, same prompt
```

This is the power of LangChain's abstraction: every LLM has the same `.invoke()` interface.

---

## Step 6: Orchestration Frameworks

You have retrieved chunks. You need to build the chain: retrieve → format → prompt → LLM → answer. Orchestration frameworks handle this wiring.

### Option 1: Manual Python (no framework)
```python
chunks = retrieve(query)
context = "\n".join(c["text"] for c in chunks)
prompt = f"Context: {context}\nQuestion: {query}"
answer = ollama_client.chat(model="qwen2.5-coder:3b", messages=[{"role":"user","content":prompt}])
```
- ✅ **Used in `ask_rag.py` and `app.py`**
- Maximum transparency — you see every step
- No hidden behaviour
- More code to write
- **Best for: learning what RAG actually does, or production systems needing full control**

### Option 2: LangChain LCEL (pipe syntax)
```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
answer = rag_chain.invoke(question)
```
- ✅ **Used in Cell 12 of the ChromaDB notebook**
- Clean, declarative syntax
- Easy to swap components
- Abstraction hides details (harder to debug)
- **Best for: rapid prototyping, standard RAG patterns**

### Option 3: LangChain chains (older style)
```python
from langchain.chains import RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"   # "stuff" = put all chunks in one prompt
)
answer = qa_chain.run(question)
```
- Older API, still widely used in tutorials
- Less flexible than LCEL
- `chain_type` options: `stuff` (all chunks at once), `map_reduce` (summarize each chunk first), `refine` (iteratively refine answer)
- **Best for: following older tutorials or courses**

### Option 4: LlamaIndex
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("How does CI/CD work?")
```
- Alternative to LangChain with different philosophy
- More opinionated, less flexible
- Better defaults for document Q&A
- Larger community growing
- **Best for: document Q&A systems, knowledge graphs, structured data RAG**

### Option 5: Haystack
- Open-source pipeline framework from deepset
- More enterprise-focused
- Good for production pipelines with multiple nodes
- Steeper learning curve
- **Best for: production, complex pipelines, evaluation built-in**

### Framework comparison

| Framework | Learning curve | Flexibility | Community | Best for |
|---|---|---|---|---|
| Manual Python | Lowest (just Python) | Maximum | — | ✅ Learning, full control |
| LangChain LCEL | Moderate | High | Very large | ✅ Prototyping, most tutorials |
| LlamaIndex | Moderate | High | Large | Document Q&A |
| Haystack | Higher | High | Medium | Enterprise production |
| None (manual) | Lowest | Maximum | — | Full custom systems |

---

## Step 7: The UI Layer

Once your RAG system works, how do users interact with it?

| Option | Complexity | Free? | Best for |
|---|---|---|---|
| Terminal / CLI | Lowest | Free | ✅ Developers, scripting |
| **Gradio** | Low | Free | ✅ **Used in `app.py`** — quick browser UI |
| Streamlit | Low-Medium | Free | Clean dashboards, more widgets |
| Flask API | Moderate | Free | REST API backend |
| FastAPI | Moderate | Free | Production API with docs |
| React / Next.js | High | Free | Production web app |
| Slack / Teams bot | Moderate | Free (bot) | Internal team tool |
| VS Code extension | High | Free | Developer tool |

---

## Summary — What this project uses and why

| Step | Tool chosen | Why chosen |
|---|---|---|
| Document loading | Custom Python | Maximum control, no LangChain dependency for core pipeline |
| Chunking | Custom heading-aware + paragraph split | Best for structured Markdown docs |
| Embedding | `all-MiniLM-L6-v2` | Free, fast on CPU, good quality, 90 MB |
| Vector store | FAISS | Free, fast, lightweight, 1 file output |
| LLM | Ollama `qwen2.5-coder:3b` | Already in Docker, free, local, technical content |
| Orchestration | Manual Python | Learning-first, transparent, no hidden behaviour |
| UI | Gradio | Simplest Python-native browser UI, minimal dependencies |
| Learning notebooks | LangChain + ChromaDB | Industry-standard tools, LCEL chain, widely used in courses |
