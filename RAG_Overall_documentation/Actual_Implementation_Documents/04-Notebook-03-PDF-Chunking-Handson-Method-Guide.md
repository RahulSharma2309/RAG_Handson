# 04 - Notebook 03 Technical Method Guide (`03_pdf_chunking_handson.ipynb`)

> This document explains the implementation details of `Handson/01-Chunking/notebooks/03_pdf_chunking_handson.ipynb`, which chunks all PDFs inside `Documents/PDF Dummy Documents` using profile-based strategies and produces production-ready chunk artifacts plus quality reports.

---

## What This Notebook Implements

Input corpus:
- `Documents/PDF Dummy Documents/AI Interview PDFs`
- `Documents/PDF Dummy Documents/Different Types Example`

Output artifacts:
- `Handson/01-Chunking/data/pdf/ai_interview_pdfs/*.jsonl`
- `Handson/01-Chunking/data/pdf/different_types_example/*.jsonl`
- `Handson/01-Chunking/data/pdf/quality_reports/*.csv|*.json`

Notebook objective:
- Use **different chunking profiles** for interview-report PDFs vs mixed-type PDFs
- Clean extraction artifacts before chunking
- Attach robust metadata for filtering and traceability
- Detect no-text PDFs and mark them for OCR

---

## Core Building-Block Methods

### 1) `clean_pdf_text(text: str) -> str`

```python
def clean_pdf_text(text: str) -> str:
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'Page\s*\d+\s*(of|/)\s*\d+', '', text, flags=re.IGNORECASE)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    text = text.replace('\x00', '')
    text = ' '.join(text.split())
    return text.strip()
```

**What it does**
- Fixes hyphenated line breaks (`auto-\nmatically -> automatically`)
- Removes page numbering patterns
- Normalizes ligatures and whitespace
- Produces cleaner text for embedding

**Why this method is critical**
- PDF extraction quality determines chunk quality
- Without cleaning, repeated boilerplate and broken words pollute embeddings

---

### 2) `pick_pdf_profile(pdf_path: Path) -> str`

```python
def pick_pdf_profile(pdf_path: Path) -> str:
    folder = pdf_path.parent.name.lower()
    if 'ai interview' in folder:
        return 'ai_interview'
    return 'mixed_pdf'
```

**What it does**
- Routes each PDF to a chunking profile by source folder.

**Why this matters**
- AI interview reports and mixed-type PDFs have different structure and chunking needs.
- This is profile-based chunking in practice (not one global config).

---

### 3) `PROFILE_CONFIG` (profile-level splitter defaults)

```python
PROFILE_CONFIG = {
    'ai_interview': {
        'chunk_size': 850,
        'chunk_overlap': 140,
        'separators': ['\n\n', '\n', '. ', ' ', ''],
        'doc_type': 'pdf_ai_interview',
    },
    'mixed_pdf': {
        'chunk_size': 900,
        'chunk_overlap': 120,
        'separators': ['\n\n', '\n', '. ', ' ', ''],
        'doc_type': 'pdf_mixed',
    },
}
```

**What it does**
- Defines chunk behavior per profile.

**Why this matters**
- Interview reports are compact and repetitive: moderate chunk size with stronger overlap.
- Mixed PDFs (invoice/resume/scanned) need robust but general defaults.

---

### 4) `extract_pdf_pages(pdf_path) -> (pages, summary)`

**What it does**
- Reads each page via PyMuPDF (`fitz`)
- Stores cleaned text per page
- Calculates quality stats:
  - page count
  - non-empty pages
  - avg/max extracted chars
  - `ocr_needed` flag if no text layer exists

**Why this matters**
- Separates extraction quality diagnosis from chunking.
- Prevents silently indexing empty/scanned PDFs as if they were healthy text inputs.

---

### 5) `chunk_single_pdf(pdf_path) -> (chunks, summary)`

Core method in this notebook.

**What it does**
1. Selects profile (`ai_interview` or `mixed_pdf`)
2. Extracts and cleans pages
3. If no text layer exists: returns no chunks + `ocr_needed=True`
4. Splits page text with `RecursiveCharacterTextSplitter`
5. Adds metadata per chunk:
   - source/file/page
   - profile/doc_type
   - extraction method
   - `chunk_id`, `chunk_index`
   - char/token counts
6. Returns both chunk list and quality summary row

**Why this method is a building block**
- It is the per-file engine used by batch processing.
- It combines extraction, split, metadata enrichment, and quality accounting in one controlled unit.

---

### 6) `save_jsonl(chunks, out_path)` + per-source splitting

**What it does**
- Saves chunk artifacts as JSONL:
  - `page_content`
  - `metadata`
- Writes both:
  - per-file artifacts
  - consolidated artifacts per folder

**Why this matters**
- Makes chunking reproducible and inspectable.
- Decouples chunking from embedding/indexing stage.

---

### 7) Quality reports and OCR manifest

Generated outputs:
- `pdf_chunking_quality_report_<run_id>.csv`
- `pdf_chunking_quality_report_<run_id>.json`
- `pdf_ocr_needed_manifest_<run_id>.json`

**What they contain**
- file-wise extraction and chunk metrics
- `ocr_needed` flags for problematic files

**Why this matters**
- Gives immediate operational visibility.
- Ensures no-text files are explicitly handled, not silently ignored.

---

## Real Run Outcome (Current Corpus)

From the executed pipeline:
- PDFs processed: **9**
- Total chunks created: **79**
- AI interview chunks: **70**
- Mixed-type chunks: **9**
- OCR-needed files: **1** (`1-2RAG.pdf`)

This is expected based on extraction profiling:
- AI interview PDFs have good text layers and chunk well
- `1-2RAG.pdf` appears scanned/no-text and correctly gets routed to OCR-needed manifest

---

## Folder Outputs Produced

### Chunk artifacts
- `Handson/01-Chunking/data/pdf/ai_interview_pdfs/`
  - per-file JSONL chunks
  - `all_ai_interview_pdfs_chunks.jsonl`

- `Handson/01-Chunking/data/pdf/different_types_example/`
  - per-file JSONL chunks for text-extractable PDFs
  - `all_different_types_example_chunks.jsonl`

### Reports
- `Handson/01-Chunking/data/pdf/quality_reports/`
  - quality report CSV/JSON
  - OCR-needed manifest JSON

---

## Why This Notebook Matters in the Learning Path

Notebook `01` taught text chunking basics.  
Notebook `02` taught structured CSV chunking.  
Notebook `03` adds the hardest real-world source: PDF.

This notebook introduces the production pattern:
- source profiling
- profile-based strategy
- extraction-quality awareness
- chunk + metadata + reporting as one pipeline

---

## Next Recommended Step

Create a follow-up notebook for embedding/indexing these PDF chunks:
- Load JSONL artifacts
- Embed with local model (`sentence-transformers`)
- Build vector store
- Evaluate retrieval quality with PDF-focused benchmark queries

