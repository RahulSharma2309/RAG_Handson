# 02 - Notebook 01 Technical Method Guide (`01_chunking_handson.ipynb`)

> This document explains the core methods and building blocks used in `Handson/01-Chunking/notebooks/01_chunking_handson.ipynb`. It focuses on what each method does, why it exists, and where it fits in the end-to-end chunking pipeline.

---

## Notebook Goal

`01_chunking_handson.ipynb` teaches chunking fundamentals through direct experimentation:

1. Start with plain text and the `Document` object
2. Compare fixed-size splitting vs recursive splitting
3. Measure chunk sizes in tokens (not just characters)
4. Split `Document` objects while preserving metadata
5. Enrich chunk metadata for downstream retrieval and debugging

---

## Core Building Blocks in This Notebook

### 1) `Document(...)` from `langchain_core.documents`

```python
doc = Document(
    page_content="Kubernetes is an open-source container orchestration platform...",
    metadata={
        "source": "kubernetes_intro.txt",
        "section": "Introduction",
        "page": 1,
        "doc_type": "technical"
    }
)
```

**What it does**
- Wraps text (`page_content`) + context (`metadata`) into one retrievable unit.

**Why it matters**
- This is the canonical unit in LangChain RAG.
- Every chunk sent to vector DB should eventually be a `Document`.
- Metadata powers filtering, citations, debugging, and provenance.

---

### 2) `CharacterTextSplitter(...)` + `.split_text(...)` (Fixed chunking baseline)

```python
fixed_splitter = CharacterTextSplitter(
    separator="",
    chunk_size=300,
    chunk_overlap=50,
)
fixed_chunks = fixed_splitter.split_text(SAMPLE_TEXT)
```

**What it does**
- Splits by raw character count, mostly ignoring semantic boundaries.

**Why it is included**
- Gives a baseline to compare against smarter methods.
- Shows the classic failure mode: sentence/word fragmentation at chunk boundaries.

**Key learning**
- Useful as a simple baseline, but usually weaker for semantic retrieval quality.

---

### 3) `RecursiveCharacterTextSplitter(...)` + `.split_text(...)`

```python
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
recursive_chunks = recursive_splitter.split_text(SAMPLE_TEXT)
```

**What it does**
- Tries high-quality boundaries first (paragraphs), then weaker ones (lines, sentences, words, characters) only if needed.

**Why it matters**
- This is the default production splitter for many text-heavy RAG systems.
- Better semantic integrity than fixed chunking.

**Important nuance**
- Overlap is best-effort in recursive splitting.
- If semantic pieces already fit exactly into `chunk_size`, requested overlap may be less than configured (or zero).

---

### 4) `count_tokens(text: str) -> int` using `tiktoken`

```python
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))
```

**What it does**
- Measures token count per chunk using OpenAI tokenizer (`cl100k_base`) as a practical approximation.

**Why it matters**
- `chunk_size` in these splitters is usually character-based, but embedding models enforce token limits.
- Without token checking, chunks can exceed embedding context limits and get silently truncated.

**Practical outcome in notebook**
- Token safety checks are shown against a mini model limit (example: 256 tokens for local MiniLM workflows).

---

### 5) `TokenTextSplitter(...)` + `.split_text(...)`

```python
token_splitter = TokenTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
)
token_chunks = token_splitter.split_text(SAMPLE_TEXT)
```

**What it does**
- Splits directly by token count instead of characters.

**Why it matters**
- Useful when strict token budgets are required.
- Helps avoid accidental truncation by design.

**Tradeoff**
- Can be less semantically clean than recursive splitting unless carefully tuned.

---

### 6) `.split_documents(...)` (critical production pattern)

```python
source_documents = [Document(page_content=SAMPLE_TEXT, metadata={...})]
doc_chunks = splitter.split_documents(source_documents)
```

**What it does**
- Splits full `Document` inputs and carries metadata into child chunks.

**Why this is a building block**
- Real pipelines load files as `Document` objects, then split them.
- `.split_text(...)` is great for learning; `.split_documents(...)` is the production pattern.

---

### 7) `enrich_chunk_metadata(chunks: list) -> list`

```python
def enrich_chunk_metadata(chunks: list) -> list:
    enriched = []
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = len(chunks)
        chunk.metadata["char_count"] = len(chunk.page_content)
        chunk.metadata["token_count"] = count_tokens(chunk.page_content)
        enriched.append(chunk)
    return enriched
```

**What it does**
- Adds operational metadata to each chunk after splitting.

**Why it matters**
- `chunk_index` / `total_chunks` support ordering and neighborhood expansion.
- `char_count` / `token_count` support validation and diagnostics.
- Makes retrieval behavior explainable and measurable.

---

## Method Relationships (How They Work Together)

1. Start with raw text or loaded documents.
2. Use splitters to produce candidate chunks.
3. Validate chunk boundaries qualitatively (preview outputs).
4. Validate token counts quantitatively (`count_tokens`).
5. Attach/enrich metadata (`enrich_chunk_metadata`).
6. Save/index chunks for retrieval.

This notebook intentionally teaches that chunking is not one method call - it is a mini pipeline.

---

## Typical Questions This Notebook Helps You Answer

- Why do two splitters with same `chunk_size` produce very different retrieval quality?
- Why can `chunk_overlap=50` still produce little/no overlap in recursive mode?
- Why must token count checks happen before embedding?
- Why is metadata not optional in production chunking?

---

## Recommended Next Step

After understanding this notebook's methods, continue with:

- `Handson/01-Chunking/notebooks/02_csv_chunking_handson.ipynb`

It extends these ideas to structured tabular data and introduces row chunks + grouped summary chunks.

