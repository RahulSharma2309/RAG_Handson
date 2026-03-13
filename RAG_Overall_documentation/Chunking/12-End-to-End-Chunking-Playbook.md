# End-to-End Chunking Playbook

> This is the complete implementation SOP for taking raw documents through to retrieval-ready indexed chunks. It is not a list of concepts — it is the sequence of decisions and actions you execute, in order, every time you set up or update a RAG chunking pipeline. Every phase is explained with the reasoning behind it and what goes wrong if you skip it.

---

## Why a Playbook, Not Just Code

A chunking playbook is a repeatable, documented process that produces consistent results regardless of who runs it or when.

Without a playbook:
- Different team members chunk the same documents differently
- Parameter changes are not tracked, so improvements cannot be reproduced
- When retrieval quality degrades (it will), there is no baseline to return to
- When new documents are added, no one knows which profile to use

With a playbook:
- Every ingestion run is reproducible
- Every parameter change is an experiment with before/after evidence
- New team members can onboard the chunking system in hours, not weeks
- Quality regressions are caught and diagnosed with specific, actionable information

---

## Phase 0 — Document Analysis and Profile Definition

**This phase happens before you write a single line of code.**

### Step 0.1 — Inventory your document types

Collect a representative sample (5–10 docs) of each document type you will ingest. Answer these questions for each type:

```
For each document type:
1. What format is it in? (PDF, DOCX, Markdown, CSV, JSON, SQL)
2. What is the typical length? (pages, word count, rows)
3. What structural markers does it have? (headings, numbered lists, tables, code blocks)
4. What types of questions will users ask about it?
5. What is the typical length of a complete answer? (one sentence? one paragraph? multiple steps?)
6. What context is required for each answer to be complete? (just the fact? fact + condition? fact + exception?)
```

### Step 0.2 — Define chunk profiles

Based on your analysis, define a profile for each document family:

```python
CHUNK_PROFILES = {
    "functional": {
        "description": "HR policies, PRDs, SOPs, process documents",
        "loader": "TextLoader or Docx2txtLoader",
        "cleaning": ["normalize_whitespace", "strip_boilerplate_headers"],
        "chunk_size": 700,
        "chunk_overlap": 120,
        "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        "metadata_required": [
            "source", "doc_type", "section_title",
            "version", "effective_date", "owner_team"
        ]
    },
    "technical": {
        "description": "Architecture docs, runbooks, API references, deployment guides",
        "loader": "TextLoader",
        "cleaning": ["normalize_whitespace"],
        "chunk_size": 500,
        "chunk_overlap": 90,
        "separators": ["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""],
        "metadata_required": [
            "source", "doc_type", "service_name",
            "environment", "system_area", "contains_code"
        ]
    },
    "tabular": {
        "description": "CSV exports, database records",
        "loader": "custom_pandas",
        "cleaning": ["strip_empty_rows"],
        "chunk_strategy": "row_plus_group",
        "metadata_required": [
            "source", "doc_type", "row_index", "layer"
        ]
    },
    "general": {
        "description": "Default for unclassified documents",
        "loader": "TextLoader",
        "cleaning": ["normalize_whitespace"],
        "chunk_size": 600,
        "chunk_overlap": 100,
        "separators": ["\n\n", "\n", ". ", " ", ""],
        "metadata_required": ["source", "doc_type", "chunk_index"]
    }
}
```

**Do not skip this step.** The entire pipeline flows from these profile definitions. If they are wrong, everything downstream is wrong.

### Step 0.3 — Document the routing logic

Define which documents go to which profile. Make this explicit in code — do not leave it implicit.

```python
import os
from pathlib import Path

def assign_profile(file_path: str) -> str:
    """
    Assign a chunk profile based on file path and name conventions.
    Customize this for your actual folder structure.
    """
    path_str = str(file_path).lower()

    # Folder-based routing
    if "/hr/" in path_str or "/policies/" in path_str:
        return "functional"
    if "/runbooks/" in path_str or "/architecture/" in path_str or "/api-docs/" in path_str:
        return "technical"
    if path_str.endswith(".csv"):
        return "tabular"

    # Name-based routing
    name = Path(file_path).stem.lower()
    if any(kw in name for kw in ["policy", "prd", "sop", "process", "procedure"]):
        return "functional"
    if any(kw in name for kw in ["runbook", "deploy", "architecture", "api"]):
        return "technical"

    return "general"   # safe default
```

---

## Phase 1 — Ingestion and Normalization

**Goal:** Load every document and produce clean, standardized text with base metadata.

### Step 1.1 — Load documents by type

```python
from langchain_community.document_loaders import (
    TextLoader, PyMuPDFLoader, Docx2txtLoader, DirectoryLoader
)

def load_document(file_path: str, profile: str) -> list:
    """Load a single document using the appropriate loader for its type."""
    ext = Path(file_path).suffix.lower()

    if ext in [".md", ".txt"]:
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == ".pdf":
        loader = PyMuPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    docs = loader.load()

    # Attach base metadata
    for doc in docs:
        doc.metadata["doc_family"] = profile
        doc.metadata["doc_type"] = profile   # will be refined later

    return docs
```

### Step 1.2 — Clean extracted text

```python
import re

def clean_text(text: str, profile: str) -> str:
    """Apply profile-appropriate text cleaning."""

    # Universal cleaning — always applied
    text = re.sub(r'-\n', '', text)           # fix PDF hyphenated line breaks
    text = text.replace("ﬁ", "fi")           # fix ligatures
    text = text.replace("ﬂ", "fl")
    text = re.sub(r'\x00', '', text)          # remove null bytes
    text = re.sub(r'\n{3,}', '\n\n', text)   # normalize excessive newlines

    # Profile-specific cleaning
    if profile == "functional":
        # Remove document footers typical of Word docs
        text = re.sub(r'CONFIDENTIAL\s*\|.*', '', text)
        text = re.sub(r'Version \d+\.\d+ \| \d{4}-\d{2}-\d{2}', '', text)

    if profile == "technical":
        # Remove page number patterns from PDF tech docs
        text = re.sub(r'Page \d+ of \d+', '', text)

    return text.strip()

# Apply to all loaded documents
for doc in loaded_docs:
    doc.page_content = clean_text(doc.page_content, profile=doc.metadata["doc_family"])
```

### Step 1.3 — Skip empty or near-empty documents

```python
MIN_CONTENT_LENGTH = 100   # characters

def is_meaningful(doc) -> bool:
    """Filter out near-empty documents (cover pages, blank pages, TOC-only)."""
    return len(doc.page_content.strip()) >= MIN_CONTENT_LENGTH

loaded_docs = [doc for doc in loaded_docs if is_meaningful(doc)]
print(f"After filtering: {len(loaded_docs)} documents remain")
```

---

## Phase 2 — Semantic-First Splitting

**Goal:** Apply the right splitting strategy for each document family, producing chunks that preserve semantic and logical units.

### Step 2.1 — Apply profile-based splitting

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents_by_profile(docs: list, profile: str) -> list:
    """Split documents using the configured profile parameters."""
    config = CHUNK_PROFILES[profile]

    if profile == "tabular":
        return split_csv_documents(docs)   # handled separately

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=config["separators"]
    )

    return splitter.split_documents(docs)
```

### Step 2.2 — The splitting priority principle

When choosing separators, always follow this mental model:

```
Ask: What is the largest meaningful unit in this document type?

For functional documents:
  Largest unit = policy section (H2 heading)
  → "\n## " must be first separator

For technical documents:
  Largest unit = procedure section (H2 heading) or code block
  → "\n## " and "\n```" must be first separators

For general prose:
  Largest unit = paragraph
  → "\n\n" is the first separator

For code:
  Largest unit = function or class
  → Use from_language() — character splitting does not apply
```

The splitter will always try the first separator before falling back to the next. By putting the right separator first, you guarantee that the right boundaries are honored before any character-level splitting happens.

---

## Phase 3 — Chunk Post-Processing

**Goal:** Enrich every chunk with its complete metadata, assign stable identifiers, and filter garbage chunks.

### Step 3.1 — Extract section title from chunk content

```python
def extract_section_title(chunk_text: str) -> str:
    """Extract the section heading from the chunk text if present."""
    lines = chunk_text.strip().split("\n")
    first_line = lines[0].strip()

    if first_line.startswith("### "):
        return first_line.replace("### ", "").strip()
    elif first_line.startswith("## "):
        return first_line.replace("## ", "").strip()
    elif first_line.startswith("# "):
        return first_line.replace("# ", "").strip()

    # No heading — use first 50 chars as approximate title
    return first_line[:50].strip() if first_line else "body"
```

### Step 3.2 — Enrich all chunk metadata

```python
import hashlib
from datetime import datetime

def enrich_chunk_metadata(
    chunks: list,
    profile: str,
    domain_metadata: dict   # e.g. {"version": "v5", "owner_team": "HR"}
) -> list:
    """
    Add complete metadata to every chunk.
    domain_metadata contains document-level fields specific to this file.
    """
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        # Stable chunk ID (deterministic, based on content)
        content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()[:12]
        chunk_id = f"{profile}-{content_hash}"

        # Section title from content
        section = extract_section_title(chunk.page_content)

        chunk.metadata.update({
            # Stable identity
            "chunk_id": chunk_id,
            "chunk_index": i,
            "total_chunks": total,

            # Content metrics
            "char_count": len(chunk.page_content),
            "word_count": len(chunk.page_content.split()),
            "contains_code": "```" in chunk.page_content,
            "section_title": section,

            # Profile and family
            "doc_family": profile,
            "chunk_method": "recursive",

            # Pipeline metadata
            "indexed_at": datetime.utcnow().isoformat() + "Z",
        })

        # Apply domain-specific metadata
        chunk.metadata.update(domain_metadata)

    return chunks
```

### Step 3.3 — Filter garbage chunks

```python
def is_valid_chunk(chunk, min_words: int = 15) -> bool:
    """
    Filter out chunks that are too short or are boilerplate noise.
    """
    text = chunk.page_content.strip()
    word_count = len(text.split())

    # Too short to be meaningful
    if word_count < min_words:
        return False

    # All-caps header/footer boilerplate
    if text.isupper() and len(text) < 100:
        return False

    # Page number only
    if re.match(r'^Page \d+ of \d+$', text):
        return False

    return True

chunks = [c for c in chunks if is_valid_chunk(c)]
print(f"After filtering garbage chunks: {len(chunks)} remain")
```

### Step 3.4 — Save chunk artifacts to JSONL

**Always save chunks before indexing.** This creates a versioned artifact you can reuse, audit, and roll back to.

```python
import json
import os
from pathlib import Path

def save_chunk_artifacts(chunks: list, output_dir: str, run_id: str) -> str:
    """
    Save chunks as JSONL file with run metadata.
    Returns the path to the saved artifact.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    artifact_path = os.path.join(output_dir, f"chunks_{run_id}.jsonl")

    with open(artifact_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            record = {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved {len(chunks)} chunks to: {artifact_path}")
    return artifact_path

# Usage
run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
artifact_path = save_chunk_artifacts(
    chunks=all_chunks,
    output_dir="chunk_artifacts/",
    run_id=run_id
)
```

---

## Phase 4 — Pre-Index Validation

**Goal:** Catch errors before they propagate into the vector index.

### Step 4.1 — Token limit check

```python
import tiktoken

def validate_token_limits(chunks: list, model_limit: int) -> bool:
    enc = tiktoken.get_encoding("cl100k_base")
    violations = []
    for i, chunk in enumerate(chunks):
        count = len(enc.encode(chunk.page_content))
        if count > model_limit:
            violations.append((i, count))

    if violations:
        print(f"❌ {len(violations)} token limit violations (limit: {model_limit}):")
        for idx, count in violations[:5]:
            print(f"   Chunk {idx}: {count} tokens")
        return False

    counts = [len(enc.encode(c.page_content)) for c in chunks]
    print(f"✅ All {len(chunks)} chunks within {model_limit}-token limit")
    print(f"   Max: {max(counts)} | Avg: {sum(counts)/len(counts):.1f}")
    return True
```

### Step 4.2 — Metadata completeness check

```python
def validate_metadata(chunks: list, profile: str) -> bool:
    required = CHUNK_PROFILES[profile]["metadata_required"]
    issues = []
    for i, chunk in enumerate(chunks):
        missing = [f for f in required if not chunk.metadata.get(f)]
        if missing:
            issues.append((i, missing))

    if issues:
        print(f"❌ {len(issues)} chunks with missing metadata:")
        for idx, fields in issues[:5]:
            print(f"   Chunk {idx}: missing {fields}")
        return False

    print(f"✅ All {len(chunks)} chunks have complete metadata")
    return True
```

### Step 4.3 — Chunk count by source

```python
from collections import Counter

def print_chunk_distribution(chunks: list) -> None:
    sources = Counter(c.metadata.get("source", "unknown") for c in chunks)
    print("\nChunk distribution by source:")
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {count:4d} chunks | {Path(source).name}")
    print(f"\nTotal: {len(chunks)} chunks from {len(sources)} sources")
```

**Look for anomalies:**
- A single source with 10× more chunks than others → may indicate PDF boilerplate is not cleaned
- A source with 0 or 1 chunk → may indicate loading or cleaning failure
- Expected sources missing entirely → file routing may have failed

### Step 4.4 — Reject the run on hard failures

```python
def validate_and_gate(chunks: list, profile: str, model_limit: int) -> bool:
    """
    Run all validations. Return False if any hard check fails.
    Hard fail = do NOT proceed to indexing.
    """
    token_ok    = validate_token_limits(chunks, model_limit)
    metadata_ok = validate_metadata(chunks, profile)
    print_chunk_distribution(chunks)

    if not token_ok or not metadata_ok:
        print("\n❌ Validation failed. Do not proceed to indexing. Fix issues and re-run.")
        return False

    print("\n✅ All validations passed. Ready for indexing.")
    return True

# Gate the pipeline
if not validate_and_gate(chunks, profile="functional", model_limit=256):
    raise SystemExit("Chunking pipeline halted: validation failures.")
```

---

## Phase 5 — Retrieval Evaluation Loop

**Goal:** Confirm that the chunked content retrieves correctly for real user queries before declaring the ingestion complete.

### Step 5.1 — Build index and run benchmark

After indexing the validated chunks:

```python
# Build vector index (example with FAISS or ChromaDB)
# ... index creation code ...

# Run benchmark
from benchmark import BENCHMARK_QUERIES   # your pre-built query set (see doc 10)
from evaluator import evaluate_retrieval

results = evaluate_retrieval(retriever, BENCHMARK_QUERIES)
print(f"Avg score   : {results['avg_score']} / 6.0")
print(f"Top-3 rate  : {results['top3_hit_rate']}%")
```

### Step 5.2 — Accept or tune

**If avg_score ≥ 4.0 and top3_rate ≥ 70%:** Accept this configuration. Document the parameters.

**If below threshold:** Use the diagnostics map from document 10 to identify the cause. Change **one parameter**. Re-chunk, re-validate, re-index, re-evaluate.

Repeat until both thresholds are met.

### Step 5.3 — Document the accepted configuration

When the threshold is met, write a configuration file that captures exactly what was used:

```yaml
# chunk_config_functional_v3.yaml
# Accepted: 2024-03-15 | Top-3 rate: 76% | Avg score: 4.6
profile: functional
chunk_size: 700
chunk_overlap: 120
separators:
  - "\n## "
  - "\n### "
  - "\n\n"
  - "\n"
  - ". "
  - " "
  - ""
embedding_model: all-MiniLM-L6-v2
model_token_limit: 256
benchmark_score:
  top3_hit_rate: 76%
  avg_quality_score: 4.6
  evaluated_at: "2024-03-15"
  benchmark_set_version: "v2"
```

This file is your contract: any future change must be justified by evidence that beats these scores.

---

## Phase 6 — Production Readiness Checks

Before moving a chunking configuration to production:

| Check | How |
|---|---|
| Chunk artifacts versioned | JSONL file stored with run_id timestamp |
| Configuration documented | YAML config file committed to repo |
| Benchmark scores recorded | Results logged with date and benchmark set version |
| Rollback plan tested | Can you re-index from JSONL artifacts within 30 min? |
| Update pipeline documented | Is the re-chunking trigger and process written down? |
| Monitoring in place | Do you track top-3 hit rate over time in production? |
| Alert threshold defined | At what score drop does the team get notified? |

---

## Quick First Implementation Checklist

For a new RAG project starting from scratch, use this checklist in order:

```
Phase 0 — Before coding:
  [ ] Inventoried all document types
  [ ] Defined chunk profiles for each type
  [ ] Defined routing logic (which document → which profile)

Phase 1 — Ingestion:
  [ ] Correct loader chosen for each file type
  [ ] Text cleaning applied (especially for PDFs)
  [ ] Near-empty documents filtered
  [ ] Base metadata attached at load time

Phase 2 — Splitting:
  [ ] Profile-appropriate separators used
  [ ] Section-aware splitting for structured documents
  [ ] Code-block aware splitting for technical documents

Phase 3 — Post-processing:
  [ ] All required metadata fields populated
  [ ] Chunk IDs assigned
  [ ] Garbage chunks filtered
  [ ] JSONL artifact saved

Phase 4 — Validation:
  [ ] Token limit check passed (0 violations)
  [ ] Metadata completeness ≥ 95%
  [ ] Chunk distribution looks reasonable
  [ ] Pipeline gated on validation failure

Phase 5 — Evaluation:
  [ ] Benchmark query set built (20-40 real queries)
  [ ] Top-3 hit rate ≥ 70%
  [ ] Average quality score ≥ 4.0 / 6.0
  [ ] Accepted configuration documented

Phase 6 — Production:
  [ ] Artifacts versioned
  [ ] Config committed to repo
  [ ] Update pipeline documented
  [ ] Monitoring and alerts configured
```
