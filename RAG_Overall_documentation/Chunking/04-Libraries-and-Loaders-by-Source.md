# Libraries and Loaders by Source

This file answers: **which library should I use for which source?**

---

## 1) Core stack for chunking workflows

- `langchain` / `langchain-community` for loaders and splitters
- `sentence-transformers` for local embeddings
- `tiktoken` (or tokenizer-specific libs) for token-aware sizing
- `unstructured` for complex formats where plain extraction fails

---

## 2) Source-wise library guide

## A. Plain text / Markdown

Recommended:
- `TextLoader`
- `DirectoryLoader`
- `RecursiveCharacterTextSplitter`

Why:
- simple, fast, reliable
- markdown headings allow semantic splitting

Use cases:
- knowledge base notes
- process docs
- architecture markdown

---

## B. PDF documents

Recommended extraction options:
- `PyPDFLoader` (default for normal text PDFs)
- `PyMuPDFLoader` (faster, often better extraction quality)
- `UnstructuredPDFLoader` (complex layouts/tables, but heavier)

Important:
- run text cleaning after extraction
- preserve page metadata
- validate weird characters and broken lines

---

## C. DOCX / Word documents

Recommended:
- `Docx2txtLoader` for straightforward extraction
- `UnstructuredWordDocumentLoader` for richer element-level extraction

Important:
- preserve section/title relationships
- detect and handle tables separately if needed

---

## D. CSV / tabular files

Recommended:
- `CSVLoader` for quick row-based chunks
- custom pandas-based processor for richer context chunking

Important:
- row-level chunks alone are often not enough
- also create grouped/summary chunks (by category/team/date)

---

## E. JSON / nested JSON

Recommended:
- `JSONLoader` with `jq_schema` for targeted extraction
- custom parser for deeply nested domain structures

Important:
- flatten important nested fields
- preserve entity relationships in metadata

---

## F. SQL / database content

Recommended:
- `SQLDatabase` + `SQLDatabaseLoader`
- custom query-to-document conversion for relational context

Important:
- include table source and join context in metadata
- create both record-level and relationship-level chunks

---

## 3) Splitter choice guide

Default recommended splitter:
- `RecursiveCharacterTextSplitter`

When to use alternatives:
- `CharacterTextSplitter`: strict delimiter-based docs
- `TokenTextSplitter`: hard token budget requirements
- custom heading-aware splitter: markdown-heavy technical/functional docs

---

## 4) Suggested "starter stack" for your project

For your mixed-source RAG learning repo:

- Markdown/text docs: `DirectoryLoader` + `RecursiveCharacterTextSplitter`
- PDFs: `PyMuPDFLoader` first, fallback to `UnstructuredPDFLoader`
- CSV: custom pandas chunking (row + grouped summaries)
- Functional docs: heading-first + paragraph-aware splitting
- Technical docs: heading-first + command/code block preservation

---

## 5) Production note

Do not standardize only the library.  
Standardize the **chunk profile per document family**:

- functional profile
- technical profile
- operations profile
- tabular profile

That is more impactful than switching libraries frequently.

