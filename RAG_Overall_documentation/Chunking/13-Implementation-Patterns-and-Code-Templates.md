# Implementation Patterns and Code Templates

> This document is the code reference for everything covered in documents 01–12. Every pattern here is production-ready — copy it, adapt the parameters to your use case, and use it directly. Each pattern includes the context for when to use it, what it produces, and what to watch out for.

---

## Setup — Imports and Installation

### Install everything you need

```bash
# Install with uv (recommended)
uv add langchain langchain-community langchain-text-splitters langchain-core \
       langchain-experimental sentence-transformers tiktoken \
       pymupdf pypdf docx2txt unstructured pandas python-dotenv

# Or with pip
pip install langchain langchain-community langchain-text-splitters langchain-core \
            langchain-experimental sentence-transformers tiktoken \
            pymupdf pypdf docx2txt unstructured pandas python-dotenv
```

### Core imports used across all patterns

```python
# LangChain splitters (langchain v1.x — always use langchain_text_splitters)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
    Language,
)

# Document loaders
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyMuPDFLoader,
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    JSONLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
)

# Core document type
from langchain_core.documents import Document

# Utilities
import pandas as pd
import json
import re
import os
import hashlib
import tiktoken
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
```

---

## Pattern 1 — Plain Text and Markdown Chunking

**When to use:** Knowledge base notes, README files, architecture docs, process documents in plain text or Markdown format.

**What it produces:** One Document per chunk, with source metadata. Heading structure is respected by separator priority.

```python
def chunk_text_documents(
    directory: str,
    chunk_size: int = 600,
    overlap: int = 100,
    glob_pattern: str = "**/*.md"
) -> List[Document]:
    """
    Load all text/markdown files from a directory and chunk them.

    chunk_size: target character count per chunk
    overlap: character overlap between consecutive chunks
    glob_pattern: which files to load ("**/*.md" for markdown, "**/*.txt" for text)
    """
    loader = DirectoryLoader(
        directory,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=True
    )
    docs = loader.load()
    print(f"Loaded {len(docs)} documents from {directory}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    # Add chunk tracking metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["doc_family"] = "general"

    print(f"Produced {len(chunks)} chunks")
    return chunks
```

**Example output:**
```python
chunks = chunk_text_documents("docs/", chunk_size=600, overlap=100)
# chunks[0].page_content → "## Kubernetes Overview\n\nKubernetes manages..."
# chunks[0].metadata    → {"source": "docs/kubernetes.md", "chunk_index": 0, "doc_family": "general"}
```

---

## Pattern 2 — Markdown with Header Metadata

**When to use:** Markdown documents where you want heading hierarchy tracked in metadata for each chunk.

**What it produces:** One Document per heading section, with `h1_title`, `h2_section`, `h3_subsection` in metadata.

```python
def chunk_markdown_with_headers(
    markdown_text: str,
    source_path: str,
    max_section_size: int = 800,
    section_overlap: int = 100
) -> List[Document]:
    """
    Split markdown by heading hierarchy.
    Each chunk carries its heading context in metadata.
    Large sections are further split while retaining heading metadata.
    """
    headers_to_split_on = [
        ("#",   "h1_title"),
        ("##",  "h2_section"),
        ("###", "h3_subsection"),
    ]

    # Step 1: Split by headers — each section becomes a Document with heading metadata
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False    # keep heading text in chunk body
    )
    header_chunks = header_splitter.split_text(markdown_text)

    # Attach source to header chunks
    for chunk in header_chunks:
        chunk.metadata["source"] = source_path

    # Step 2: Further split sections that are too large
    secondary_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_section_size,
        chunk_overlap=section_overlap
    )
    final_chunks = secondary_splitter.split_documents(header_chunks)

    return final_chunks

# Usage
with open("architecture.md", "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_markdown_with_headers(text, source_path="architecture.md")

# Each chunk now has:
# metadata["h1_title"]      → "Kubernetes Overview"
# metadata["h2_section"]    → "Core Components"
# metadata["h3_subsection"] → "API Server"   (if applicable)
```

---

## Pattern 3 — PDF Chunking with Cleaning

**When to use:** Any PDF document. Always apply cleaning before splitting.

**What it produces:** One Document per chunk with page number and source metadata.

```python
def clean_pdf_text(text: str) -> str:
    """Remove common PDF extraction artifacts. Always call before chunking."""
    text = re.sub(r'-\n', '', text)              # fix hyphenated line breaks
    text = re.sub(r'Page \d+ of \d+', '', text)  # remove page number patterns
    text = re.sub(r'\n{3,}', '\n\n', text)       # normalize excessive blank lines
    text = text.replace("ﬁ", "fi")              # fix common ligatures
    text = text.replace("ﬂ", "fl")
    text = text.replace("ﬀ", "ff")
    text = text.replace("\x00", "")              # remove null bytes
    return text.strip()


def chunk_pdf(
    pdf_path: str,
    chunk_size: int = 400,
    overlap: int = 60,
    doc_type: str = "pdf"
) -> List[Document]:
    """
    Load a PDF, clean each page, and chunk with metadata.

    Uses PyMuPDFLoader — fastest and most accurate free PDF loader.
    Falls back gracefully to skip near-empty pages.
    """
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()   # one Document per page

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    for page in pages:
        cleaned = clean_pdf_text(page.page_content)
        if len(cleaned.strip()) < 50:
            continue   # skip near-empty pages (cover, blank, diagram-only)

        page_chunks = splitter.create_documents(
            texts=[cleaned],
            metadatas=[{
                "source": pdf_path,
                "page": page.metadata.get("page", 0) + 1,   # 1-indexed
                "total_pages": page.metadata.get("total_pages", 0),
                "doc_type": doc_type,
                "doc_family": "pdf",
            }]
        )
        all_chunks.extend(page_chunks)

    # Add chunk index across all pages
    for i, chunk in enumerate(all_chunks):
        chunk.metadata["chunk_index"] = i

    print(f"PDF: {Path(pdf_path).name} → {len(pages)} pages → {len(all_chunks)} chunks")
    return all_chunks
```

---

## Pattern 4 — CSV Two-Layer Chunking

**When to use:** Any CSV where users will ask both specific lookup questions ("what is Sarah's salary?") and analytical questions ("what is the average salary in Engineering?").

**What it produces:** Two layers — one Document per row AND one Document per group.

```python
def chunk_csv_two_layer(
    csv_path: str,
    group_by: Optional[str] = None
) -> List[Document]:
    """
    Layer 1: One chunk per row (for specific lookup queries)
    Layer 2: One chunk per group (for comparative/analytical queries)

    group_by: column name to group by for Layer 2 (e.g., "department", "category")
    """
    df = pd.read_csv(csv_path)
    source = os.path.basename(csv_path)
    docs = []

    # ── Layer 1: Row-level chunks ─────────────────────────────────
    for idx, row in df.iterrows():
        lines = [f"{col}: {row[col]}" for col in df.columns]
        docs.append(Document(
            page_content="\n".join(lines),
            metadata={
                "source": source,
                "doc_type": "csv_row",
                "row_index": int(idx),
                "layer": "row",
                "doc_family": "tabular"
            }
        ))

    # ── Layer 2: Group-level summary chunks ───────────────────────
    if group_by and group_by in df.columns:
        for group_val, gdf in df.groupby(group_by):
            numeric_cols = gdf.select_dtypes(include="number").columns
            lines = [
                f"Summary for {group_by}: {group_val}",
                f"Total records: {len(gdf)}"
            ]
            for col in numeric_cols:
                lines.extend([
                    f"Average {col}: {gdf[col].mean():.2f}",
                    f"Max {col}: {gdf[col].max()}",
                    f"Min {col}: {gdf[col].min()}"
                ])
            docs.append(Document(
                page_content="\n".join(lines),
                metadata={
                    "source": source,
                    "doc_type": "csv_group_summary",
                    "group_by": group_by,
                    "group_value": str(group_val),
                    "layer": "group",
                    "doc_family": "tabular"
                }
            ))

    row_count   = sum(1 for d in docs if d.metadata["layer"] == "row")
    group_count = sum(1 for d in docs if d.metadata["layer"] == "group")
    print(f"CSV: {source} → {row_count} row chunks + {group_count} group chunks")
    return docs
```

---

## Pattern 5 — Functional Documents (Policies, PRDs)

**When to use:** HR policies, business SOPs, PRDs, compliance documents — any document where business rules must stay with their exceptions.

**What it produces:** One Document per policy section, with version and owner metadata.

```python
def chunk_functional_docs(
    directory: str,
    doc_type: str = "policy",
    version: str = "unknown",
    effective_date: str = "",
    owner_team: str = ""
) -> List[Document]:
    """
    Chunking profile for functional/business documents.
    Larger chunks and higher overlap to preserve rule + exception context.
    Section headings (## ) are always honored as primary split points.
    """
    loader = DirectoryLoader(
        directory,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    total = len(chunks)
    for i, chunk in enumerate(chunks):
        first_line = chunk.page_content.strip().split("\n")[0]
        section = first_line.lstrip("#").strip() if first_line.startswith("#") else "body"

        chunk.metadata.update({
            "doc_type": doc_type,
            "doc_family": "functional",
            "section_title": section,
            "version": version,
            "effective_date": effective_date,
            "owner_team": owner_team,
            "chunk_index": i,
            "total_chunks": total,
            "char_count": len(chunk.page_content),
        })

    print(f"Functional docs: {total} chunks from {directory}")
    return chunks
```

---

## Pattern 6 — Technical Documents (Runbooks, Architecture, APIs)

**When to use:** Runbooks, architecture docs, API references, deployment guides — documents where commands must stay with their context.

**What it produces:** One Document per procedure section, with service and environment metadata.

```python
def chunk_technical_docs(
    directory: str,
    service_name: str,
    environment: str = "production",
    system_area: str = "general"
) -> List[Document]:
    """
    Chunking profile for technical documentation.
    Code-block aware separators. Higher overlap keeps commands with prerequisites.
    """
    loader = DirectoryLoader(
        directory,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=90,
        separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    total = len(chunks)
    for i, chunk in enumerate(chunks):
        first_line = chunk.page_content.strip().split("\n")[0]
        section = first_line.lstrip("#").strip() if first_line.startswith("#") else "body"

        chunk.metadata.update({
            "doc_type": "technical",
            "doc_family": "technical",
            "service_name": service_name,
            "environment": environment,
            "system_area": system_area,
            "section_title": section,
            "contains_code": "```" in chunk.page_content,
            "chunk_index": i,
            "total_chunks": total,
            "char_count": len(chunk.page_content),
        })

    print(f"Technical docs: {total} chunks from {directory}")
    return chunks
```

---

## Pattern 7 — Python Code Chunking

**When to use:** Any source code that needs to be indexed for code search, documentation generation, or developer Q&A.

**What it produces:** One Document per function or class, with no overlap (function boundaries are semantically clean).

```python
def chunk_python_code(file_path: str) -> List[Document]:
    """
    Split Python code by function and class boundaries.
    Uses LangChain's language-aware splitter — never splits mid-function.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=1500,
        chunk_overlap=0   # no overlap — function boundaries are clean units
    )

    chunks = splitter.create_documents(
        texts=[code],
        metadatas=[{
            "source": file_path,
            "doc_type": "source_code",
            "doc_family": "code",
            "language": "python",
            "filename": Path(file_path).name
        }]
    )

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["contains_code"] = True

    print(f"Code: {Path(file_path).name} → {len(chunks)} chunks")
    return chunks

# Supported languages: PYTHON, JS, TS, GO, RUST, JAVA, CPP, RUBY, SCALA, and more
# Usage for other languages:
# RecursiveCharacterTextSplitter.from_language(language=Language.GO, ...)
```

---

## Pattern 8 — Profile-Based Chunking Router

**When to use:** Mixed-source corpora where different document types need different chunking strategies.

**What it produces:** Correctly chunked Documents for each file, routed to the right profile automatically.

```python
PROFILES = {
    "functional": {
        "chunk_size": 700, "chunk_overlap": 120,
        "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
    },
    "technical": {
        "chunk_size": 500, "chunk_overlap": 90,
        "separators": ["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
    },
    "operations": {
        "chunk_size": 400, "chunk_overlap": 60,
        "separators": ["\n## ", "\n\n", "\n", ". ", " ", ""]
    },
    "general": {
        "chunk_size": 600, "chunk_overlap": 100,
        "separators": ["\n\n", "\n", ". ", " ", ""]
    },
}


def assign_profile(file_path: str) -> str:
    """Assign a chunk profile based on file path conventions."""
    path_lower = str(file_path).lower()
    name = Path(file_path).stem.lower()

    if "/hr/" in path_lower or "policy" in name or "prd" in name or "sop" in name:
        return "functional"
    if "/runbooks/" in path_lower or "architecture" in name or "api" in name:
        return "technical"
    if Path(file_path).suffix == ".csv":
        return "tabular"

    return "general"


def chunk_by_profile(file_path: str, extra_metadata: Dict = None) -> List[Document]:
    """
    Route a document to the right chunking profile and split it.
    extra_metadata: additional metadata specific to this document (version, team, etc.)
    """
    profile = assign_profile(file_path)
    config = PROFILES.get(profile, PROFILES["general"])
    extra = extra_metadata or {}

    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(**config)
    chunks = splitter.split_documents(docs)

    total = len(chunks)
    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "doc_family": profile,
            "chunk_index": i,
            "total_chunks": total,
            **extra
        })

    return chunks
```

---

## Pattern 9 — Metadata Schema Builder

**When to use:** Every chunking pipeline — ensures consistent metadata across all document families.

```python
def build_chunk_metadata(
    source_file: str,
    doc_type: str,
    doc_family: str,
    chunk_index: int = 0,
    total_chunks: int = 1,
    section_title: str = "",
    # Functional doc fields
    version: str = "",
    effective_date: str = "",
    owner_team: str = "",
    # Technical doc fields
    service_name: str = "",
    environment: str = "",
    system_area: str = "",
    contains_code: bool = False,
    # Tabular fields
    row_index: int = -1,
    group_by: str = "",
    group_value: str = "",
    **kwargs
) -> Dict[str, Any]:
    """
    Build a complete, standardized metadata dict for any chunk.
    Include only the relevant optional fields for your document type.
    """
    # Base metadata — always present
    meta = {
        "source": source_file,
        "doc_type": doc_type,
        "doc_family": doc_family,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "indexed_at": datetime.utcnow().isoformat() + "Z",
    }

    # Conditional fields — add only if provided
    if section_title:
        meta["section_title"] = section_title
    if version:
        meta["version"] = version
    if effective_date:
        meta["effective_date"] = effective_date
    if owner_team:
        meta["owner_team"] = owner_team
    if service_name:
        meta["service_name"] = service_name
    if environment:
        meta["environment"] = environment
    if system_area:
        meta["system_area"] = system_area
    if contains_code:
        meta["contains_code"] = contains_code
    if row_index >= 0:
        meta["row_index"] = row_index
    if group_by:
        meta["group_by"] = group_by
        meta["group_value"] = group_value

    # Any additional custom fields
    meta.update(kwargs)
    return meta
```

---

## Pattern 10 — Token Verification

**When to use:** Before embedding any chunk set. Catches silent truncation before it corrupts your index.

```python
def verify_token_limits(
    chunks: List[Document],
    model_limit: int = 256,
    tokenizer: str = "cl100k_base"
) -> Dict:
    """
    Verify all chunks are within the embedding model's token limit.
    Returns summary and raises ValueError if violations exist.
    """
    enc = tiktoken.get_encoding(tokenizer)

    counts = [len(enc.encode(c.page_content)) for c in chunks]
    violations = [(i, cnt) for i, cnt in enumerate(counts) if cnt > model_limit]

    summary = {
        "total_chunks": len(chunks),
        "violations": len(violations),
        "max_tokens": max(counts),
        "avg_tokens": round(sum(counts) / len(counts), 1),
        "min_tokens": min(counts),
        "model_limit": model_limit,
        "pass": len(violations) == 0
    }

    if violations:
        print(f"⚠️  Token limit violations: {len(violations)} chunks exceed {model_limit} tokens")
        for idx, cnt in violations[:5]:
            print(f"  Chunk {idx}: {cnt} tokens | {chunks[idx].metadata.get('source', '?')}")
    else:
        print(f"✅ All {len(chunks)} chunks within {model_limit}-token limit")
        print(f"   Max: {summary['max_tokens']} | Avg: {summary['avg_tokens']}")

    return summary
```

---

## Pattern 11 — Chunk Quality Inspector

**When to use:** Spot-check after chunking before embedding. Visual inspection catches issues automated checks miss.

```python
import random

def inspect_chunks(
    chunks: List[Document],
    sample_size: int = 5,
    seed: int = 42
) -> None:
    """
    Print a random sample of chunks for visual inspection.
    Run this after chunking and before indexing.
    """
    total = len(chunks)
    sample = random.sample(chunks, min(sample_size, total))
    random.seed(seed)

    print(f"\n{'='*65}")
    print(f"CHUNK INSPECTION — {sample_size} of {total} chunks (random sample)")
    print(f"{'='*65}")

    for i, chunk in enumerate(sample, 1):
        print(f"\n[Sample {i}/{sample_size}]")
        print(f"  Source    : {chunk.metadata.get('source', 'unknown')}")
        print(f"  Section   : {chunk.metadata.get('section_title', 'unknown')}")
        print(f"  Doc type  : {chunk.metadata.get('doc_type', 'unknown')}")
        print(f"  Char count: {len(chunk.page_content)}")
        print(f"  Has code  : {chunk.metadata.get('contains_code', False)}")
        print(f"  {'─'*55}")
        print(f"  {chunk.page_content[:300].replace(chr(10), chr(10) + '  ')}")
        if len(chunk.page_content) > 300:
            print(f"  ... [{len(chunk.page_content) - 300} more chars]")

    print(f"\n{'='*65}")
    print("Questions to answer during inspection:")
    print("  1. Does each chunk make sense when read in isolation?")
    print("  2. Is any chunk missing its condition or exception?")
    print("  3. Are there dangling references (\"this flag\", \"as above\")?")
    print("  4. Is the section_title accurate for the content?")
```

---

## Pattern 12 — JSONL Chunk Artifact Save/Load

**When to use:** Always. Save chunks to disk before indexing. Load from disk when re-indexing.

```python
def save_chunks(chunks: List[Document], path: str) -> None:
    """Save chunks to a JSONL artifact file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps({
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }, ensure_ascii=False) + "\n")
    print(f"Saved {len(chunks)} chunks → {path}")


def load_chunks(path: str) -> List[Document]:
    """Load chunks from a saved JSONL artifact file."""
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunks.append(Document(
                page_content=record["page_content"],
                metadata=record["metadata"]
            ))
    print(f"Loaded {len(chunks)} chunks from {path}")
    return chunks

# Usage
run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
save_chunks(all_chunks, f"artifacts/chunks_{run_id}.jsonl")

# Later, re-index without re-chunking:
all_chunks = load_chunks("artifacts/chunks_20240315_143022.jsonl")
```

---

## Pattern 13 — Full Pipeline: Document to Indexed Chunks

**When to use:** As the entry point for your complete chunking pipeline, combining all patterns above.

```python
def run_chunking_pipeline(
    source_dir: str,
    output_artifact_dir: str,
    embedding_model_limit: int = 256
) -> List[Document]:
    """
    Full end-to-end chunking pipeline:
    Load → Clean → Split → Enrich → Validate → Save → Return

    source_dir          : folder containing all documents to process
    output_artifact_dir : where to save JSONL chunk artifacts
    embedding_model_limit: token limit of your embedding model
    """
    all_chunks = []

    # ── Discover all files ────────────────────────────────────────
    files = list(Path(source_dir).rglob("*"))
    files = [f for f in files if f.is_file() and f.suffix in [".md", ".txt", ".pdf", ".docx", ".csv"]]
    print(f"Found {len(files)} files to process")

    # ── Process each file by its profile ─────────────────────────
    for file_path in files:
        profile = assign_profile(str(file_path))

        if profile == "tabular" and file_path.suffix == ".csv":
            chunks = chunk_csv_two_layer(str(file_path))
        elif file_path.suffix == ".pdf":
            chunks = chunk_pdf(str(file_path), chunk_size=400, overlap=60)
        elif file_path.suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
            docs = loader.load()
            config = PROFILES.get(profile, PROFILES["general"])
            splitter = RecursiveCharacterTextSplitter(**config)
            chunks = splitter.split_documents(docs)
        else:
            chunks = chunk_by_profile(str(file_path))

        all_chunks.extend(chunks)

    print(f"\nTotal chunks before validation: {len(all_chunks)}")

    # ── Validate ──────────────────────────────────────────────────
    token_summary = verify_token_limits(all_chunks, model_limit=embedding_model_limit)
    if not token_summary["pass"]:
        raise ValueError(f"{token_summary['violations']} chunks exceed token limit. Fix before indexing.")

    # ── Spot check ───────────────────────────────────────────────
    inspect_chunks(all_chunks, sample_size=3)

    # ── Save artifact ─────────────────────────────────────────────
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    artifact_path = os.path.join(output_artifact_dir, f"chunks_{run_id}.jsonl")
    save_chunks(all_chunks, artifact_path)

    return all_chunks

# Usage
chunks = run_chunking_pipeline(
    source_dir="documents/",
    output_artifact_dir="artifacts/",
    embedding_model_limit=256
)
```

---

## Libraries Quick Reference

| Library | Install Command | Use For |
|---|---|---|
| `langchain` | `uv add langchain` | Core framework |
| `langchain-community` | `uv add langchain-community` | All document loaders |
| `langchain-text-splitters` | `uv add langchain-text-splitters` | All text splitters (LangChain v1.x) |
| `langchain-core` | `uv add langchain-core` | Document type, base classes |
| `langchain-experimental` | `uv add langchain-experimental` | SemanticChunker |
| `pymupdf` | `uv add pymupdf` | Fast, accurate PDF extraction |
| `pypdf` | `uv add pypdf` | Fallback PDF loader |
| `docx2txt` | `uv add docx2txt` | Word document extraction |
| `python-docx` | `uv add python-docx` | Section-aware DOCX parsing |
| `unstructured` | `uv add unstructured` | Complex PDF/DOCX layouts, tables |
| `sentence-transformers` | `uv add sentence-transformers` | Free local embedding models |
| `tiktoken` | `uv add tiktoken` | Token counting (OpenAI tokenizer) |
| `pandas` | `uv add pandas` | CSV/Excel processing |
| `python-dotenv` | `uv add python-dotenv` | Environment variable management |
| `llama-index-core` | `uv add llama-index-core` | Hierarchical chunking |
