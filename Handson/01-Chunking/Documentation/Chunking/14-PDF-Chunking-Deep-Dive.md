# PDF Chunking Deep Dive

> PDF chunking is one of the hardest parts of practical RAG. PDFs are designed for rendering, not semantic reading. They can contain flowing text, tables, headers/footers, scanned pages, diagrams, code blocks, and mixed layouts in the same file. This guide covers the full depth: extraction strategy, cleaning, layout-aware processing, table handling, OCR paths, metadata design, chunking patterns, evaluation, and production pitfalls.

---

## 1) Why PDF Is Fundamentally Hard

A PDF page is basically positioned glyph instructions, not a semantic document tree.

That means:
- No native concept of paragraph/sentence in many files
- Multi-column text can interleave
- Table cells can collapse into broken line streams
- Headers/footers repeat and pollute every chunk
- Scanned pages have no text layer at all (OCR required)
- Diagrams/UML have meaning with little/no text content

For this reason, PDF chunking is not one function call. It is a pipeline.

---

## 2) PDF Taxonomy Before You Chunk

Before processing, classify the PDF type. The correct pipeline depends on this.

| PDF Type | Signal | Recommended Path |
|---|---|---|
| Native digital text | text selection works | `PyMuPDFLoader` + cleaning + recursive splitting |
| Scanned/image PDF | cannot select text | OCR pipeline first, then split |
| Mixed text + tables | table-heavy pages | Layout-aware extraction (`unstructured`/table tools) |
| Mixed text + diagrams/UML | many figures, little text | hybrid approach: text chunks + figure metadata |
| Forms/invoices | key-value fields | field extraction first, then chunk normalized records |

If you skip classification and apply one generic path, quality drops fast.

---

## 3) Core Failure Modes (And Why Retrieval Breaks)

### Failure A: Column interleaving

Two-column page:
```
Left column text ...      Right column text ...
Left line 2 ...           Right line 2 ...
```

Naive extraction can produce:
```
"Left column text ... Right column text ...
 Left line 2 ... Right line 2 ..."
```

This creates semantically invalid chunks and noisy embeddings.

### Failure B: Hyphenated line breaks

```
orches-
tration
```
becomes `orches-\ntration`, breaking tokenization and retrieval matches.

### Failure C: Boilerplate repetition

Footer/header text repeated on every page (document title, confidentiality stamp, page numbers) dominates embedding space if not removed.

### Failure D: Table flattening

Rows/columns collapse into sequence text. Query like "price for SKU-123" may fail because row structure was lost.

### Failure E: Scanned pages without OCR

If there is no text layer, loader returns little/no content. You index blank/noisy chunks.

---

## 4) Loader Strategy by Complexity

### Default path (80% cases)

Use `PyMuPDFLoader` first:
- fast
- good extraction quality
- useful page metadata

```python
from langchain_community.document_loaders import PyMuPDFLoader

loader = PyMuPDFLoader("guide.pdf")
pages = loader.load()   # one Document per page
```

### Fallback for difficult layout

Use `UnstructuredPDFLoader` for element-level extraction:

```python
from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader("complex_report.pdf", mode="elements")
elements = loader.load()
```

Best for:
- complex tables
- multi-column reports
- section/title/list element categorization

Tradeoff: slower and heavier dependencies.

---

## 5) Cleaning Layer (Mandatory for PDFs)

Use cleaning before chunking. Do not skip.

```python
import re

def clean_pdf_text(text: str) -> str:
    # Fix split words from line-wrap hyphenation
    text = re.sub(r"-\n", "", text)

    # Normalize excessive new lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common page number boilerplate
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

    # Fix common ligature artifacts
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")

    # Normalize whitespace
    text = " ".join(text.split())
    return text.strip()
```

Also consider project-specific boilerplate regexes:
- confidentiality banners
- legal disclaimers repeated on each page
- company signature blocks

---

## 6) Chunking Patterns for Different PDF Content

### Pattern 1: Narrative technical PDF

Use recursive splitting with paragraph-first separators:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,          # char-based in this splitter
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

### Pattern 2: Procedure/runbook PDF

Preserve heading + bullets + command neighborhood:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=850,
    chunk_overlap=140,
    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
)
```

### Pattern 3: Table-heavy PDF

Do not treat tables as plain narrative text.

Better options:
1. Table extraction to structured rows (CSV-like records) and chunk row/group summaries
2. Keep table per chunk with table_id and page metadata
3. Hybrid: narrative chunks + table summary chunks

### Pattern 4: Scanned PDF

Pipeline:
1. OCR page images
2. Clean OCR noise
3. Chunk as text
4. Keep OCR confidence metadata per chunk

---

## 7) Recommended PDF Metadata Schema

Minimum:

```python
{
  "source": "guide.pdf",
  "page": 7,
  "total_pages": 42,
  "doc_type": "pdf",
  "chunk_index": 18
}
```

Recommended (production):

```python
{
  "source": "guide.pdf",
  "page": 7,
  "total_pages": 42,
  "doc_type": "pdf",
  "section_title": "Deployment Prerequisites",
  "extraction_method": "pymupdf",      # pymupdf | unstructured | ocr
  "contains_table": False,
  "contains_code": False,
  "ocr_confidence": None,              # set for OCR paths
  "chunk_index": 18,
  "char_count": 812,
  "token_count": 176
}
```

Why this matters:
- citation trust (page-level traceability)
- debug extraction quality by method
- filtering table/code/ocr-specific chunks

---

## 8) End-to-End PDF Chunking Pipeline (Reference)

```python
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def clean_pdf_text(text: str) -> str:
    text = re.sub(r"-\n", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = " ".join(text.split())
    return text.strip()

def chunk_pdf(pdf_path: str, chunk_size: int = 900, overlap: int = 120) -> list[Document]:
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    for p in pages:
        cleaned = clean_pdf_text(p.page_content)
        if len(cleaned) < 50:
            continue

        page_chunks = splitter.create_documents(
            texts=[cleaned],
            metadatas=[{
                "source": pdf_path,
                "page": p.metadata.get("page", 0) + 1,
                "total_pages": p.metadata.get("total_pages", 0),
                "doc_type": "pdf",
                "extraction_method": "pymupdf"
            }]
        )
        all_chunks.extend(page_chunks)

    # post metadata enrichment
    for i, c in enumerate(all_chunks):
        c.metadata["chunk_index"] = i
        c.metadata["char_count"] = len(c.page_content)

    return all_chunks
```

---

## 9) PDF Parameter Starting Defaults

These are starting points, not universal truths:

| PDF Family | Chunk Size | Overlap | Notes |
|---|---:|---:|---|
| Standard narrative PDF | 800-1000 chars | 100-140 chars | clean first, recursive |
| Technical/procedural PDF | 750-950 chars | 120-160 chars | preserve step continuity |
| Compliance/legal PDF | 1000-1400 chars | 150-220 chars | context-heavy clauses |
| OCR-heavy scanned PDF | 600-900 chars | 120-180 chars | OCR noise needs more overlap tolerance |
| Table-heavy PDF | N/A | N/A | prefer table extraction + structured chunking |

Always validate token counts before embedding.

---

## 10) Evaluation Checklist for PDF Chunk Quality

Before indexing:

- [ ] no obvious column interleaving in sampled chunks
- [ ] hyphenation artifacts removed (`auto-\nmatically` -> `automatically`)
- [ ] page-level metadata present on all chunks
- [ ] repeated headers/footers significantly reduced
- [ ] table-heavy pages handled with explicit strategy
- [ ] token counts within embedding model limits
- [ ] top-3 retrieval returns complete answers for benchmark PDF questions

Benchmark questions to test:
- "What are deployment prerequisites?"
- "What is the rollback command and verification step?"
- "Which page states the IAM requirement?"
- "What is the policy exception for contractors?" (if policy PDF)

---

## 11) Common PDF Anti-Patterns

1. **Chunking raw PDF text directly**
   - leads to polluted embeddings
2. **No page metadata**
   - no citations, hard debugging
3. **Treating tables as paragraph text**
   - destroys row/column meaning
4. **Using one extraction method for all PDFs**
   - fails on scanned/complex layouts
5. **No OCR fallback**
   - scanned docs effectively invisible

---

## 12) Practical Decision Tree

```
Is text selectable in PDF?
├── No → OCR pipeline first
└── Yes
    ├── Mostly narrative/procedure → PyMuPDF + cleaning + recursive
    ├── Table-heavy/complex layout → Unstructured/table extraction path
    └── Mixed content → hybrid (narrative chunks + table chunks + figure metadata)
```

---

## 13) Where This Fits in Your Chunking Set

This deep-dive extends:
- `05-Chunking-Strategies-by-Dataset-Type.md` (high-level strategy by type)
- `04-Libraries-and-Loaders-by-Source.md` (loader selection)
- `13-Implementation-Patterns-and-Code-Templates.md` (code patterns)

Use this document when PDF quality is your bottleneck.

