# Libraries and Loaders by Source

> This document answers a question every RAG engineer hits within the first hour of building: **which library do I use to load this file type, and what does it actually give me?** Every loader is explained with what it produces, what it gets wrong, and what to do about it. Every example is concrete. There is no guessing here.

---

## Why Loader Choice Is Not Trivial

The instinct when starting RAG is to focus on embeddings, vector databases, and retrieval. The loader feels like a boring first step that just "opens the file."

That instinct is wrong.

A bad loader produces garbage text, and garbage text produces garbage embeddings, and garbage embeddings produce garbage retrieval. The loader is the first place quality can be destroyed — before you write a single line of chunking or embedding logic.

Let's prove this immediately.

---

### The Same PDF — Two Loaders — Two Very Different Results

**The PDF contains this text:**
```
## Kubernetes Deployment Guide

To deploy on AWS, use Amazon EKS.
Amazon EKS manages the control plane automatically.
It integrates with AWS IAM, VPC, and Route 53.
```

**What PyPDFLoader extracts (default, basic):**
```
Kubernetes Deployment Guide\nTo deploy on AWS, use Amazon EKS.\nAmazon EKS manages
the control plane automa-\ntically. It integrates with AWS IAM, VPC, and Route 53.
```

Notice: "automa-tically" — the hyphenated line break from the PDF column layout was kept.  
The word "automatically" is now broken. It will tokenize and embed incorrectly.

**What PyMuPDFLoader extracts:**
```
Kubernetes Deployment Guide
To deploy on AWS, use Amazon EKS.
Amazon EKS manages the control plane automatically.
It integrates with AWS IAM, VPC, and Route 53.
```

Clean, accurate, no artifacts.

Same file. Different loader. Different text quality. Different embeddings. Different retrieval results.

That is why loader choice matters.

---

## The Core Library Stack

Before diving into source-by-source guidance, here is the complete stack you need installed for a production RAG chunking workflow:

```
langchain                  — Core framework: splitters, chains, document schema
langchain-community        — All document loaders (PDF, CSV, JSON, DOCX, etc.)
langchain-text-splitters   — All text splitter classes (split from core in v1.x)
langchain-core             — Document object, base types
sentence-transformers      — Free local embedding models
tiktoken                   — Token counting for OpenAI tokenizer (cl100k_base)
pymupdf                    — Fast, high-quality PDF extraction (PyMuPDFLoader)
pypdf                      — Fallback PDF loader (PyPDFLoader)
docx2txt                   — Word document text extraction
unstructured               — Complex formats: tables, images, mixed layouts
pandas                     — CSV and Excel processing
python-dotenv              — Environment variable management
```

**Install command (uv):**
```bash
uv add langchain langchain-community langchain-text-splitters langchain-core \
       sentence-transformers tiktoken pymupdf pypdf docx2txt \
       unstructured pandas python-dotenv
```

---

## Source A — Plain Text and Markdown Files

### What these are

Plain text (`.txt`) and Markdown (`.md`) files are the cleanest possible input for RAG.  
No layout artifacts. No encoding issues. No complex structure to decode.

These are your knowledge base notes, architecture docs, process documentation, runbooks written in Markdown, internal wikis, and README files.

### The right loaders

**For a single file:**
```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("docs/architecture.md", encoding="utf-8")
docs = loader.load()

# What you get:
# [Document(page_content="# Architecture Overview\n\nThis document...", metadata={"source": "docs/architecture.md"})]
```

**For an entire directory of files:**
```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    "docs/",
    glob="**/*.md",      # all .md files recursively
    loader_cls=TextLoader,
    show_progress=True,
    use_multithreading=True   # faster for large directories
)
docs = loader.load()

print(f"Loaded {len(docs)} documents")
# Each Document has metadata: {"source": "docs/architecture.md"}
```

### What the loader gives you

Each `Document` object contains:
- `page_content` — the full file text as a single string
- `metadata["source"]` — the file path

There is no page number (it's not a PDF), no section split (the whole file is one document), no heading metadata. All of that comes from your splitter, not your loader.

### Markdown — the structure-aware option

If your Markdown files have headings (`#`, `##`, `###`), you can extract the structure as metadata:

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

markdown_text = """
# Kubernetes Overview

Kubernetes manages containerized applications at scale.
It was originally developed by Google.

## Core Components

The API Server is the entry point for all operations.
The Scheduler assigns pods to nodes.

### Scheduler Details

The Scheduler uses resource constraints and node affinity rules.
"""

headers_to_split_on = [
    ("#",   "h1_title"),
    ("##",  "h2_section"),
    ("###", "h3_subsection"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False   # keep heading text in the chunk body too
)

chunks = splitter.split_text(markdown_text)

for chunk in chunks:
    print("Content :", chunk.page_content[:80])
    print("Metadata:", chunk.metadata)
    print()
```

**Output:**
```
Content : # Kubernetes Overview\nKubernetes manages containerized applications at scale.
Metadata: {'h1_title': 'Kubernetes Overview'}

Content : ## Core Components\nThe API Server is the entry point for all operations.
Metadata: {'h1_title': 'Kubernetes Overview', 'h2_section': 'Core Components'}

Content : ### Scheduler Details\nThe Scheduler uses resource constraints.
Metadata: {'h1_title': 'Kubernetes Overview', 'h2_section': 'Core Components', 'h3_subsection': 'Scheduler Details'}
```

Notice: every chunk now knows its heading hierarchy. When a user asks "what does the Scheduler do?", the retrieved chunk carries the metadata `h2_section: Core Components` — you can cite exactly where the answer came from.

### When to use which

| Scenario | Loader |
|---|---|
| Single file quick load | `TextLoader` |
| Entire folder of docs | `DirectoryLoader` + `TextLoader` |
| Markdown with heading structure | `TextLoader` → then `MarkdownHeaderTextSplitter` |
| Mixed file types in folder | `DirectoryLoader` with `glob="**/*"` |

---

## Source B — PDF Documents

### Why PDFs are the hardest source type

PDFs are a display format, not a content format. A PDF is essentially a set of instructions for placing text at specific pixel coordinates on a page. There is no concept of "paragraph" or "sentence" — only positioned text boxes.

This means:
- Multi-column layouts produce jumbled text when read linearly
- Hyphenated words across line breaks appear as broken fragments
- Headers and footers repeat on every page and pollute chunks
- Tables get extracted as flat text that loses row/column meaning
- Mathematical notation, ligatures (`ﬁ`, `ﬂ`), and special characters often corrupt

**Real example of raw PDF extraction:**

You have a PDF with this actual content:
```
Kubernetes is an open-source container orches-
tration platform used to manage containerized ap-
plications at scale.
```

Raw extraction gives you:
```
Kubernetes is an open-source container orches-\ntration platform used to manage containerized ap-\nplications at scale.
```

Now "orchestration" is "orches-\ntration" and "applications" is "ap-\nplications."  
These fragments will embed differently than the complete words.  
Retrieval for "container orchestration" will miss this chunk.

### The loader options

**Option 1: PyMuPDFLoader — use this first**

```python
from langchain_community.document_loaders import PyMuPDFLoader

loader = PyMuPDFLoader("documents/deployment_guide.pdf")
pages = loader.load()

# What you get: one Document per page
# pages[0].metadata:
# {
#   "source": "documents/deployment_guide.pdf",
#   "page": 0,           ← 0-indexed page number
#   "total_pages": 24,
#   "author": "DevOps Team",
#   "title": "Kubernetes Deployment Guide"
# }
```

PyMuPDF (also called `fitz`) is the fastest and most accurate free PDF extractor. It handles most PDFs cleanly, including rotated text and embedded fonts. Use this as your default.

**Option 2: PyPDFLoader — simple fallback**

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("documents/policy.pdf")
pages = loader.load()

# Similar output to PyMuPDF but slightly less accurate for complex layouts
# Metadata includes: source, page (0-indexed)
```

Use PyPDF when PyMuPDF fails or is unavailable. It's more widely supported but slightly worse extraction quality on complex PDFs.

**Option 3: UnstructuredPDFLoader — for complex layouts**

```python
from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader(
    "documents/annual_report.pdf",
    mode="elements",   # extract as structured elements: Title, NarrativeText, Table, etc.
)
elements = loader.load()

# Each element has:
# element.metadata["category"] = "NarrativeText" | "Title" | "Table" | "ListItem" | ...
```

Use `UnstructuredPDFLoader` when the PDF has tables you need to preserve, multi-column layouts, or mixed content (text + images). It is significantly slower but produces richer structure. It requires the `unstructured` package and its dependencies.

### The cleaning step — always required for PDFs

```python
import re

def clean_pdf_text(text: str) -> str:
    """
    Remove common PDF extraction artifacts.
    Always apply this before chunking PDF content.
    """
    # Fix hyphenated line breaks: "orches-\ntration" → "orchestration"
    text = re.sub(r'-\n', '', text)
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    # Fix common ligature encoding issues
    text = text.replace("ﬁ", "fi")
    text = text.replace("ﬂ", "fl")
    text = text.replace("ﬀ", "ff")
    text = text.replace("ﬃ", "ffi")
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Remove repeated page headers/footers (common pattern: "Page X of Y")
    text = re.sub(r'Page \d+ of \d+', '', text)
    
    return text.strip()

# Usage
for page in pages:
    page.page_content = clean_pdf_text(page.page_content)
```

**Before cleaning:**
```
Kubernetes is an open-source container orches-
tration platform. It integrates with AWS IAM, VPC, 
and Route 53. Page 4 of 24
```

**After cleaning:**
```
Kubernetes is an open-source container orchestration platform. It integrates with AWS IAM, VPC, and Route 53.
```

### PDF metadata you should always preserve

When a PDF is chunked, page metadata is crucial for citation and debugging:

```python
# Every PDF chunk should have at minimum:
{
    "source": "deployment_guide.pdf",
    "page": 4,             # which page this chunk came from
    "total_pages": 24,     # total pages in document
    "doc_type": "pdf",
    "chunk_method": "recursive"
}
```

When retrieval returns a PDF chunk, the user can verify the answer by going to page 4 of that document. Without this, citation is impossible.

---

## Source C — DOCX / Word Documents

### What these are

Word documents (`.docx`) are the standard format for business writing — policies, HR documents, contracts, reports, meeting notes, PRDs.

Unlike PDFs, Word documents have actual semantic structure: paragraphs, headings (with levels), tables, lists, footnotes. The challenge is extracting that structure faithfully.

### The loader options

**Option 1: Docx2txtLoader — fast, clean, simple**

```python
from langchain_community.document_loaders import Docx2txtLoader

loader = Docx2txtLoader("documents/hr_policy.docx")
docs = loader.load()

# Returns: one Document with full document text
# docs[0].metadata: {"source": "documents/hr_policy.docx"}
```

`Docx2txtLoader` extracts all text content cleanly. It strips formatting but preserves paragraph structure. Good for most use cases.

**What you get — example:**
```
Leave Policy

Annual Leave
Employees are entitled to 20 days of annual leave per calendar year.
Leave must be approved by the direct manager.

Probation Period
Employees on probation are not eligible for leave.
```

**Option 2: UnstructuredWordDocumentLoader — structure-aware**

```python
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

loader = UnstructuredWordDocumentLoader(
    "documents/hr_policy.docx",
    mode="elements"
)
elements = loader.load()

# Each element has category: "Title", "NarrativeText", "ListItem", "Table"
# Preserves heading level information
```

Use this when you need to know which text is a heading vs body — for building metadata like `section_title` automatically.

### The section metadata problem

The biggest issue with Word documents in RAG is that after chunking, you lose track of which section a chunk came from.

A 30-page HR policy document becomes 80 chunks. Without section metadata, you cannot tell whether chunk 47 is from "Leave Policy" or "Disciplinary Process."

**The fix — extract section headings manually:**

```python
from docx import Document as DocxDocument

def extract_sections_from_docx(path: str) -> list:
    """
    Extract document text with section heading tracking.
    Returns list of (heading, content) tuples.
    """
    doc = DocxDocument(path)
    sections = []
    current_heading = "Introduction"
    current_content = []

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            if current_content:
                sections.append((current_heading, "\n".join(current_content)))
            current_heading = para.text.strip()
            current_content = []
        else:
            if para.text.strip():
                current_content.append(para.text.strip())

    if current_content:
        sections.append((current_heading, "\n".join(current_content)))

    return sections

# Each section becomes a Document with accurate section metadata
sections = extract_sections_from_docx("hr_policy.docx")
from langchain_core.documents import Document

docs = [
    Document(
        page_content=content,
        metadata={"source": "hr_policy.docx", "section": heading, "doc_type": "policy"}
    )
    for heading, content in sections
]
```

This approach gives every chunk precise `section` metadata — enabling filtered retrieval like "only search within the Leave Policy section."

---

## Source D — CSV and Tabular Files

### Why CSV chunking is fundamentally different

A PDF is a narrative. A Word doc is a document. A CSV is a **table of facts**.

The chunking goal is completely different:
- For PDFs: preserve meaning across text flow
- For CSVs: preserve **every row's data integrity AND enable cross-row analysis**

A single CSV row might look like:
```
employee_id,name,department,salary,start_date
E001,Sarah Chen,Engineering,95000,2021-03-15
```

The correct chunk for this row is:
```
employee_id: E001
name: Sarah Chen
department: Engineering
salary: 95000
start_date: 2021-03-15
```

Not a raw comma-separated line — a labeled, human-readable text block that will embed correctly when a user asks "what is Sarah Chen's salary?"

### Two-layer CSV chunking strategy

Row chunks alone are not enough. If a user asks "what is the average engineering salary?", no single row chunk answers that. You need a second layer: grouped summary chunks.

```python
import pandas as pd
from langchain_core.documents import Document
import os

def chunk_csv_two_layer(csv_path: str, group_by: str = None) -> list:
    """
    Layer 1: One chunk per row (exact lookup)
    Layer 2: One chunk per group (comparative/summary questions)
    """
    df = pd.read_csv(csv_path)
    source = os.path.basename(csv_path)
    docs = []

    # ── Layer 1: Row-level chunks ─────────────────────────────────
    for idx, row in df.iterrows():
        lines = [f"{col}: {row[col]}" for col in df.columns]
        text = "\n".join(lines)
        docs.append(Document(
            page_content=text,
            metadata={
                "source": source,
                "doc_type": "csv_row",
                "row_index": int(idx),
                "layer": "row"
            }
        ))

    # ── Layer 2: Group-level summary chunks ───────────────────────
    if group_by and group_by in df.columns:
        for group_val, group_df in df.groupby(group_by):
            numeric_cols = group_df.select_dtypes(include="number").columns
            lines = [
                f"Group: {group_by} = {group_val}",
                f"Total records: {len(group_df)}",
            ]
            for col in numeric_cols:
                lines.append(f"Average {col}: {group_df[col].mean():.2f}")
                lines.append(f"Max {col}: {group_df[col].max()}")
                lines.append(f"Min {col}: {group_df[col].min()}")

            docs.append(Document(
                page_content="\n".join(lines),
                metadata={
                    "source": source,
                    "doc_type": "csv_group_summary",
                    "group_by": group_by,
                    "group_value": str(group_val),
                    "layer": "group"
                }
            ))

    return docs

# Usage
docs = chunk_csv_two_layer("employees.csv", group_by="department")
print(f"Row chunks   : {sum(1 for d in docs if d.metadata['layer'] == 'row')}")
print(f"Group chunks : {sum(1 for d in docs if d.metadata['layer'] == 'group')}")
```

**What this produces for row chunk:**
```
employee_id: E001
name: Sarah Chen
department: Engineering
salary: 95000
start_date: 2021-03-15
```
→ Answers: "What department is Sarah Chen in?" ✅

**What this produces for group chunk:**
```
Group: department = Engineering
Total records: 47
Average salary: 92450.23
Max salary: 145000
Min salary: 65000
```
→ Answers: "What is the average engineering salary?" ✅

The LangChain `CSVLoader` produces row-level documents but does not build group summaries. For most real use cases, the custom pandas approach above is more powerful.

---

## Source E — JSON and Nested JSON

### The problem with JSON in RAG

JSON files can represent wildly different things:
- A flat list of records (like a CSV but in JSON format)
- A deeply nested object hierarchy
- An API response with metadata wrapping the data
- A configuration file with nested settings

The challenge: you cannot apply one extraction strategy to all JSON files. You need to know the structure first and target the fields that matter.

### The JSONLoader with jq_schema

LangChain's `JSONLoader` uses `jq` syntax to navigate JSON structure:

```python
from langchain_community.document_loaders import JSONLoader

# Example JSON: [{"id": "1", "title": "...", "body": "...", "author": "..."}, ...]

loader = JSONLoader(
    file_path="articles.json",
    jq_schema=".[]",             # iterate over array items
    content_key="body",          # which field becomes page_content
    metadata_func=lambda record, meta: {
        **meta,
        "article_id": record.get("id"),
        "title": record.get("title"),
        "author": record.get("author"),
        "doc_type": "article"
    }
)
docs = loader.load()
```

**For nested JSON:**
```python
# JSON structure:
# {
#   "company": "Acme Corp",
#   "departments": [
#     {"name": "Engineering", "budget": 1000000, "head_count": 47, "projects": [...]}
#   ]
# }

loader = JSONLoader(
    file_path="org_structure.json",
    jq_schema=".departments[]",    # navigate into departments array
    content_key="name",
    text_content=False             # treat entire object as content
)
```

**The `text_content=False` option** — when the field you target is not a simple string but an object or array, this prevents the loader from crashing.

### When JSONLoader is not enough — custom parsing

For deeply nested domain-specific JSON, write a custom parser:

```python
import json
from langchain_core.documents import Document

def parse_api_response_json(path: str) -> list:
    """
    Custom parser for a JSON structure like:
    {
      "incidents": [
        {
          "id": "INC-001",
          "title": "Database timeout",
          "severity": "P1",
          "description": "...",
          "resolution": "..."
        }
      ]
    }
    """
    with open(path, "r") as f:
        data = json.load(f)

    docs = []
    for incident in data.get("incidents", []):
        # Build a human-readable text block for embedding
        text = (
            f"Incident: {incident['id']}\n"
            f"Title: {incident['title']}\n"
            f"Severity: {incident['severity']}\n"
            f"Description: {incident['description']}\n"
            f"Resolution: {incident['resolution']}"
        )
        docs.append(Document(
            page_content=text,
            metadata={
                "source": path,
                "incident_id": incident["id"],
                "severity": incident["severity"],
                "doc_type": "incident_report"
            }
        ))
    return docs
```

The key principle: the `page_content` should read like a natural language description of the record, not like raw JSON. Embeddings are trained on natural language — not on `{"key": "value"}` strings.

**Bad (raw JSON as content):**
```
{"id": "INC-001", "title": "Database timeout", "severity": "P1"}
```

**Good (natural language block):**
```
Incident: INC-001
Title: Database timeout
Severity: P1
Description: The primary database connection pool exhausted during peak hours.
Resolution: Increased pool size from 50 to 200 connections.
```

The second version embeds correctly and retrieves for queries like "what was the database timeout incident?" and "how was the P1 incident resolved?"

---

## Source F — SQL / Database Content

### The approach

SQL database content is not a file — it is rows in tables. You query it, then convert the results to Documents.

```python
from langchain_community.utilities import SQLDatabase
from langchain_core.documents import Document
import sqlite3
import pandas as pd

def load_table_as_documents(db_path: str, table: str, id_col: str) -> list:
    """
    Load a database table as individual record Documents.
    Each row becomes one Document with full field context.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()

    docs = []
    for _, row in df.iterrows():
        lines = [f"{col}: {row[col]}" for col in df.columns]
        text = "\n".join(lines)
        docs.append(Document(
            page_content=text,
            metadata={
                "source": f"{db_path}::{table}",
                "table": table,
                "row_id": str(row.get(id_col, "")),
                "doc_type": "database_record"
            }
        ))
    return docs
```

For relational data, also create join-context chunks — records that include data from related tables:

```python
def load_orders_with_customer_context(conn) -> list:
    """
    Create chunks that include both order and customer data.
    This allows retrieval for: "What did customer X order?"
    """
    query = """
    SELECT o.order_id, o.product, o.amount, o.status,
           c.name AS customer_name, c.tier AS customer_tier
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    """
    df = pd.read_sql(query, conn)
    # ... build Documents as shown above
```

The metadata for database chunks should include `table`, `row_id`, and relevant FK values so you can trace exactly which record produced the answer.

---

## Source G — The Starter Stack Decision Tree

When you start a new RAG project, here is the decision process for choosing loaders:

```
What is your source type?

├── Plain text or Markdown
│   ├── Single file         → TextLoader
│   ├── Directory of files  → DirectoryLoader + TextLoader
│   └── Markdown with headings → TextLoader → MarkdownHeaderTextSplitter
│
├── PDF
│   ├── Normal text PDF     → PyMuPDFLoader  (first choice)
│   ├── Scanned/image PDF   → UnstructuredPDFLoader with OCR
│   └── Tables in PDF       → UnstructuredPDFLoader with mode="elements"
│
├── Word (DOCX)
│   ├── Simple extraction   → Docx2txtLoader
│   └── Section-aware       → python-docx custom parser
│
├── CSV / Excel
│   ├── Row-level lookup    → Custom pandas (row chunks)
│   ├── Analytics questions → Custom pandas (row + group chunks)
│   └── Simple ingestion    → CSVLoader (with understanding of its limits)
│
├── JSON
│   ├── Known schema        → JSONLoader with jq_schema
│   └── Complex nested      → Custom parser
│
└── Database (SQL)
    ├── Single table        → Custom pandas + SQLite/SQLAlchemy
    └── Relational context  → Custom join query → Documents
```

---

## Production Note: Standardize the Profile, Not Just the Library

A mistake teams make is choosing a library once and calling it done.

The real standard is the **chunk profile per document family** — the combination of:
1. Which loader to use for that file type
2. How to clean the extracted text
3. Which metadata fields to extract
4. Which splitter and parameters to apply
5. What the finished chunk looks like

Example profile for your functional documents:

```python
FUNCTIONAL_DOCS_PROFILE = {
    "loader": "Docx2txtLoader or TextLoader",
    "cleaning": "normalize whitespace, strip boilerplate headers",
    "metadata": ["source", "section_title", "doc_type", "version", "effective_date", "owner_team"],
    "splitter": "RecursiveCharacterTextSplitter",
    "chunk_size": 700,
    "chunk_overlap": 120,
    "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
}
```

Standardizing the profile means every document in the "functional" family is loaded, cleaned, chunked, and tagged identically — regardless of who runs the pipeline or when. This reproducibility is what makes production RAG systems maintainable.

---

## Quick Reference: Loader Decision Table

| Source Type | Recommended Loader | Key Metadata | Watch Out For |
|---|---|---|---|
| Markdown / Text | `TextLoader` + `DirectoryLoader` | `source` | No built-in heading metadata |
| Markdown (structured) | `TextLoader` → `MarkdownHeaderTextSplitter` | `source`, `h1`–`h3` | Large sections still need secondary split |
| PDF (standard) | `PyMuPDFLoader` | `source`, `page`, `total_pages` | Hyphenation artifacts, ligatures |
| PDF (tables) | `UnstructuredPDFLoader` (elements mode) | `source`, `page`, `category` | Slow, heavy dependencies |
| Word (DOCX) | `Docx2txtLoader` | `source` | No section metadata automatically |
| Word (sections) | Custom `python-docx` parser | `source`, `section` | Manual coding required |
| CSV | Custom pandas | `source`, `row_index`, `doc_type` | Column headers not in chunk text unless added |
| JSON (known schema) | `JSONLoader` + `jq_schema` | `source`, domain fields | Complex schema needs custom parser |
| SQL | Custom `pandas` + SQL query | `source`, `table`, `row_id` | Relational context lost without joins |
