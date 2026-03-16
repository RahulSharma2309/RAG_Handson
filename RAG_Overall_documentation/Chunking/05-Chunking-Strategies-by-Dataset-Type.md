# Chunking Strategies by Dataset Type

> Different data types require completely different chunking logic. A strategy that works perfectly for a PDF technical manual will produce garbage results on a CSV employee table. This document walks through each dataset type, explains why it needs a different approach, and shows exactly what good and bad chunking looks like for each one — with real before/after examples throughout.

---

## The Core Insight: Content Type Determines Chunk Shape

Before writing a single line of chunking code, you need to answer one question:

**What kind of questions will users ask about this data?**

That answer determines everything:
- How big each chunk should be
- Where chunk boundaries belong
- What metadata each chunk must carry
- Whether one chunk layer is enough or you need multiple layers

Let's walk through every major dataset type and prove this with real examples.

---

## Dataset Type 1 — CSV and Tabular Datasets

### What makes CSV chunking unique

A CSV is not a narrative. It is a structured set of records. Every row is an independent, complete fact.

This changes the chunking goal entirely:

- **For narrative documents**: preserve semantic flow and context across sentences
- **For CSV rows**: preserve the integrity and label context of each record

Consider this CSV:

```
employee_id,name,department,salary,location,start_date
E001,Sarah Chen,Engineering,95000,New York,2021-03-15
E002,James Park,Marketing,72000,Austin,2020-08-22
E003,Priya Sharma,Engineering,98000,San Francisco,2019-11-10
```

**Bad chunking — raw rows with no labels:**

```
Chunk 1: "E001,Sarah Chen,Engineering,95000,New York,2021-03-15"
Chunk 2: "E002,James Park,Marketing,72000,Austin,2020-08-22"
```

Query: "Where does Sarah Chen work?"

The embedding for `"E001,Sarah Chen,Engineering,95000,New York,2021-03-15"` is ambiguous. It contains positional data but the model does not know that the 5th comma-separated value means "location." The query "where does Sarah Chen work?" will not reliably match this chunk.

❌ Result: wrong or no answer.

---

**Good chunking — labeled key-value text blocks:**

```
Chunk 1:
employee_id: E001
name: Sarah Chen
department: Engineering
salary: 95000
location: New York
start_date: 2021-03-15
```

Query: "Where does Sarah Chen work?"

The embedding for this chunk contains "name: Sarah Chen" and "location: New York" in natural language context. The similarity between the query and this chunk is high and direct.

✅ Result: "Sarah Chen works in New York."

---

### The two-layer problem

Now consider these questions:
1. "Where does Sarah Chen work?" → answered by a single row chunk ✅
2. "How many engineers do we have?" → answered by how many? Counting row chunks? ❌
3. "What is the average engineering salary?" → single row chunks cannot answer this ❌

Row-level chunks support specific lookup queries. They cannot support analytical or comparative queries.

The solution is **two-layer chunking** — build both row chunks and group summary chunks from the same CSV.

```python
import pandas as pd
from langchain_core.documents import Document
import os

def chunk_csv_two_layer(csv_path: str, group_by: str = None) -> list:
    df = pd.read_csv(csv_path)
    source = os.path.basename(csv_path)
    docs = []

    # Layer 1 — one chunk per row
    for idx, row in df.iterrows():
        text = "\n".join([f"{col}: {row[col]}" for col in df.columns])
        docs.append(Document(
            page_content=text,
            metadata={
                "source": source,
                "doc_type": "csv_row",
                "row_index": int(idx),
                "layer": "row"
            }
        ))

    # Layer 2 — one chunk per group (if group_by is specified)
    if group_by and group_by in df.columns:
        for group_val, gdf in df.groupby(group_by):
            numeric_cols = gdf.select_dtypes(include="number").columns
            lines = [
                f"Summary for {group_by}: {group_val}",
                f"Total records: {len(gdf)}"
            ]
            for col in numeric_cols:
                lines.append(f"Average {col}: {gdf[col].mean():.2f}")
                lines.append(f"Max {col}: {gdf[col].max()}")
                lines.append(f"Min {col}: {gdf[col].min()}")
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

docs = chunk_csv_two_layer("employees.csv", group_by="department")
```

**Group chunk produced:**
```
Summary for department: Engineering
Total records: 23
Average salary: 92340.87
Max salary: 145000
Min salary: 65000
```

This single chunk now answers: "How many engineers do we have?", "What is the average engineering salary?", "What is the max engineering salary?"

### Required metadata for CSV chunks

Every CSV chunk — whether row or group — must carry:

```python
# Row chunk metadata
{
    "source": "employees.csv",
    "doc_type": "csv_row",
    "row_index": 0,          # original row position in file
    "layer": "row"
}

# Group chunk metadata
{
    "source": "employees.csv",
    "doc_type": "csv_group_summary",
    "group_by": "department",
    "group_value": "Engineering",
    "layer": "group"
}
```

At retrieval time, the `doc_type` metadata lets you filter: "for this analytical question, only search group summaries."

---

## Dataset Type 2 — PDF Documents

### What makes PDF chunking unique

PDFs are a visual format masquerading as text. They were designed for printing, not for machine reading. The challenges are different from any other format.

**The three unavoidable PDF problems:**

**Problem 1 — Line break artifacts from column layouts**

A PDF page with two columns produces this extraction:
```
Kubernetes is an open-source    Docker is a containerization
container orchestration         platform that packages
platform used to manage         applications and their
containerized applications.     dependencies into containers.
```

Extracted as raw text:
```
"Kubernetes is an open-source    Docker is a containerization\ncontainer orchestration         platform that packages\n..."
```

Both columns got merged. The text is now interleaved and will produce wrong embeddings.

**Problem 2 — Hyphenation at line ends**

A PDF might have the word split across lines:
```
The orchestration system auto-
matically manages the lifecycle
of containerized applications.
```

Extracted: `"auto-\nmatically"` — the word "automatically" is now broken.

**Problem 3 — Repeated headers and footers**

Most multi-page PDFs have page numbers and document titles on every page:
```
Page 4 of 24   |   CONFIDENTIAL   |   Kubernetes Deployment Guide

To deploy on AWS, use Amazon EKS...
```

Without cleaning, every chunk from this document will contain "CONFIDENTIAL" and "Kubernetes Deployment Guide" — polluting embeddings with irrelevant repeated text.

### The complete PDF chunking pipeline

```python
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def clean_pdf_text(text: str) -> str:
    text = re.sub(r'-\n', '', text)              # fix hyphenated line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)       # collapse excessive newlines
    text = re.sub(r'Page \d+ of \d+', '', text)  # remove page number text
    text = text.replace("ﬁ", "fi")              # fix ligatures
    text = text.replace("ﬂ", "fl")
    text = " ".join(text.split())                # normalize whitespace
    return text.strip()

def chunk_pdf(pdf_path: str, chunk_size: int = 400, overlap: int = 60) -> list:
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

        chunks = splitter.create_documents(
            texts=[cleaned],
            metadatas=[{
                "source": pdf_path,
                "page": page.metadata.get("page", 0) + 1,  # 1-indexed for humans
                "total_pages": page.metadata.get("total_pages", 0),
                "doc_type": "pdf",
            }]
        )
        all_chunks.extend(chunks)

    return all_chunks
```

### Good vs bad chunking on a real PDF section

**Original PDF content (page 7):**
```
## Deployment Prerequisites

Before deploying Kubernetes on AWS, ensure the following:
- AWS CLI version 2.x or higher is installed
- kubectl version 1.27+ is configured
- IAM role with EKS:CreateCluster permission exists
- VPC with at least 2 subnets in different AZs

If any prerequisite is missing, the deployment will fail at the IAM validation step.
```

**Bad chunking (no cleaning, fixed 200 chars):**
```
Chunk A: "## Deployment Prerequi"
Chunk B: "sites\n\nBefore deploying Kubernetes on AWS, ensure the following:\n- AWS CLI ver"
Chunk C: "sion 2.x or higher is installed\n- kubectl ver"
```

Query: "What are the Kubernetes deployment prerequisites?"  
Retrieval matches Chunk B — which has no heading context and is incomplete.  
❌ Incomplete answer.

**Good chunking (cleaned, paragraph-aware):**
```
Chunk:
## Deployment Prerequisites
Before deploying Kubernetes on AWS, ensure the following:
- AWS CLI version 2.x or higher is installed
- kubectl version 1.27+ is configured
- IAM role with EKS:CreateCluster permission exists
- VPC with at least 2 subnets in different AZs
If any prerequisite is missing, the deployment will fail at the IAM validation step.

Metadata: {source: guide.pdf, page: 7, doc_type: pdf}
```

Query: "What are the Kubernetes deployment prerequisites?"  
✅ Complete answer including the failure note.

### Suggested PDF defaults

```
chunk_size   : 350–500 tokens (most PDF sections fit within 500 tokens)
chunk_overlap: 50–80 tokens   (one clean sentence overlap)
splitter     : RecursiveCharacterTextSplitter with paragraph-first separators
cleaning     : always required before splitting
```

### Want the full deep-dive for PDF?

If you want full-depth PDF guidance (OCR paths, table strategy, diagram handling, extraction-method decision tree, production anti-patterns, and evaluation checklist), read:

`14-PDF-Chunking-Deep-Dive.md`

---

## Dataset Type 3 — Technical Documents (Architecture, API, Runbooks)

### What makes technical doc chunking unique

Technical documents — architecture designs, API references, runbooks, deployment guides — have a very specific failure mode in RAG:

**The prerequisite-command separation problem.**

Consider this runbook section:
```
## Rollback Procedure

Before executing rollback, confirm the following conditions:
- Backup snapshot is available and verified (snapshot ID: snap-abc123)
- At least 2 healthy nodes exist in the cluster
- Rollback has been approved by on-call engineer

Command to execute rollback:
kubectl rollout undo deployment/api-server --to-revision=3
```

**Bad chunking splits it:**
```
Chunk 1: "Before executing rollback, confirm the following conditions:
- Backup snapshot is available and verified (snapshot ID: snap-abc123)
- At least 2 healthy nodes exist in the cluster"

Chunk 2: "- Rollback has been approved by on-call engineer

Command to execute rollback:
kubectl rollout undo deployment/api-server --to-revision=3"
```

User query: "How do I rollback the API server?"

The retriever returns one or both chunks. Chunk 1 has the prerequisites. Chunk 2 has the command. If only Chunk 2 is retrieved, the LLM gives the rollback command without the critical preconditions.

**Engineer executes command without verifying snapshot → incident escalates.**

❌ The chunking directly caused an operational risk.

**Good chunking keeps the section intact:**
```
Chunk:
## Rollback Procedure
Before executing rollback, confirm the following conditions:
- Backup snapshot is available and verified (snapshot ID: snap-abc123)
- At least 2 healthy nodes exist in the cluster
- Rollback has been approved by on-call engineer

Command to execute rollback:
kubectl rollout undo deployment/api-server --to-revision=3
```

✅ Complete answer with prerequisites and command together.

### The strategy: heading-first, code-block aware

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

technical_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=90,
    separators=[
        "\n## ",     # section break — highest priority
        "\n### ",    # subsection break
        "\n```",     # code block boundary
        "\n\n",      # paragraph break
        "\n",        # line break
        " ",         # word break (last resort)
        ""           # character (emergency fallback)
    ]
)
```

The `"\n```"` separator ensures code blocks stay intact as chunk boundaries. Without it, a multi-line YAML block might be split in the middle:

**Bad split (mid-YAML):**
```
Chunk 1:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3

Chunk 2:
  selector:
    matchLabels:
      app: api-server
```

The second chunk is orphaned — it's a fragment of YAML that means nothing without its parent context.

**With `"\n```"` as separator:**  
The entire YAML block stays in one chunk, correctly bounded by the code fence markers.

### API documentation chunking pattern

Each API endpoint should produce these distinct chunks:

```
Endpoint overview chunk:
  POST /api/v1/orders
  Creates a new order in the system.
  Requires authentication: Bearer token
  Rate limit: 100 requests/minute

Request schema chunk:
  POST /api/v1/orders — Request Body
  {
    "product_id": "string (required)",
    "quantity": "integer (required, min: 1)",
    "customer_id": "string (required)"
  }

Response schema chunk:
  POST /api/v1/orders — Response
  200 OK: {"order_id": "string", "status": "pending"}
  400 Bad Request: {"error": "invalid_product_id"}
  429 Too Many Requests: {"error": "rate_limit_exceeded"}
```

These three chunks are separately retrievable — a developer asking "what is the orders API request format?" gets the request schema chunk, not a giant page with everything mixed together.

### Suggested technical doc defaults

```
chunk_size   : 400–500 tokens
chunk_overlap: 80–110 tokens (higher than narrative docs — commands need context)
splitter     : RecursiveCharacterTextSplitter with code-aware separators
metadata     : source, section_title, system_area, service_name, environment, contains_code
```

---

## Dataset Type 4 — Functional and Business Documents

### What makes functional doc chunking unique

Functional documents — policies, PRDs, user flows, process docs, SLAs — contain **business logic that is inseparable from its conditions and exceptions**.

The critical failure mode: splitting a rule from its exception.

**A real HR policy section:**
```
## Annual Leave Policy

Employees who have completed their probation period are entitled to 20 days
of annual leave per calendar year.

Leave requests must be submitted at least 2 weeks in advance through the
HR portal. Manager approval is required before leave is confirmed.

Exception: Contract employees and employees on a Performance Improvement
Plan (PIP) are not eligible for the standard 20-day entitlement. Contract
employees receive 10 days. Employees on PIP must obtain HR Director approval.
```

**Bad chunking (character count, 300 tokens):**
```
Chunk 1:
Employees who have completed their probation period are entitled to 20 days
of annual leave per calendar year. Leave requests must be submitted at least
2 weeks in advance through the HR portal. Manager approval is required before
leave is confirmed.

Chunk 2:
Exception: Contract employees and employees on a Performance Improvement
Plan (PIP) are not eligible for the standard 20-day entitlement. Contract
employees receive 10 days. Employees on PIP must obtain HR Director approval.
```

User asks: "How many leave days am I entitled to?"

The retriever returns Chunk 1 — because it has "entitled to 20 days" which matches strongly.

LLM says: "You are entitled to 20 days of annual leave per year."

But the user is a contract employee. The exception in Chunk 2 was never retrieved.

❌ Confidently wrong answer. Potentially a compliance or HR legal issue.

**Good chunking keeps the rule and exception together:**
```
Chunk:
## Annual Leave Policy
Employees who have completed their probation period are entitled to 20 days
of annual leave per calendar year. Leave requests must be submitted at least
2 weeks in advance through the HR portal. Manager approval is required before
leave is confirmed.

Exception: Contract employees and employees on a PIP are not eligible for the
standard 20-day entitlement. Contract employees receive 10 days. Employees on
PIP must obtain HR Director approval.
```

User asks: "How many leave days am I entitled to?"

LLM says: "Full-time employees who have completed probation get 20 days. Contract employees get 10 days. If you are on a PIP, you need HR Director approval."

✅ Complete, accurate answer.

### The strategy: section-first with large chunks and high overlap

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

functional_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # larger — policy context needs more room
    chunk_overlap=120,   # high overlap — exceptions often appear right after rules
    separators=[
        "\n## ",         # section break — primary boundary
        "\n### ",        # subsection break
        "\n\n",          # paragraph break
        "\n",            # line break (but preserve bullets)
        ". ",            # sentence end (last before word)
        " ",
        ""
    ]
)
```

The key differences from technical docs:
- **Larger chunk_size** (700 vs 500) — policies need more context per chunk
- **Higher overlap** (120 vs 90) — ensures exceptions and conditions don't get cut off
- **No code-block separator** — functional docs rarely have code

### Required metadata for functional chunks

```python
{
    "source": "hr_policy_v4.docx",
    "doc_type": "policy",
    "section_title": "Annual Leave Policy",
    "version": "v4.2",
    "effective_date": "2024-01-01",
    "owner_team": "Human Resources",
    "chunk_index": 3
}
```

Why `version` and `effective_date` matter: users often ask about current policy. Without date metadata, you cannot enforce "always retrieve the latest version." An outdated policy retrieved confidently is worse than no answer.

### Suggested functional doc defaults

```
chunk_size   : 600–750 tokens
chunk_overlap: 100–130 tokens
splitter     : RecursiveCharacterTextSplitter, section-first separators
metadata     : source, section_title, doc_type, version, effective_date, owner_team
```

---

## Dataset Type 5 — Mixed-Source Enterprise Corpus

### What this is

Real enterprise RAG systems don't have one document type. They have:
- HR policy PDFs
- Technical runbooks in Markdown
- Employee CSV exports from HRIS
- Meeting notes in Word documents
- Incident reports in JSON
- Architecture diagrams with text descriptions

Applying a single chunk configuration across this entire corpus is one of the most common and damaging mistakes in RAG development.

### The profile-based chunking approach

The solution is to define **chunk profiles per document family** and route every document to the right profile before processing.

```python
# Define profiles explicitly
CHUNK_PROFILES = {
    "functional": {
        "chunk_size": 700,
        "chunk_overlap": 120,
        "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        "metadata": ["doc_type", "section_title", "version", "effective_date", "owner_team"]
    },
    "technical": {
        "chunk_size": 500,
        "chunk_overlap": 90,
        "separators": ["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""],
        "metadata": ["doc_type", "system_area", "service_name", "environment", "contains_code"]
    },
    "operations": {
        "chunk_size": 380,
        "chunk_overlap": 60,
        "separators": ["\n## ", "\n\n", "\n", ". ", " ", ""],
        "metadata": ["doc_type", "process_name", "team", "priority"]
    },
    "tabular": {
        "strategy": "custom_pandas",
        "layers": ["row", "group"],
        "metadata": ["doc_type", "row_index", "group_by", "group_value"]
    }
}
```

**How document routing works:**

```python
from pathlib import Path

def get_document_profile(file_path: str) -> str:
    """
    Assign a chunk profile based on file location and type.
    In production this would use a config file or database.
    """
    path = Path(file_path)
    path_lower = str(path).lower()

    if "hr/" in path_lower or "policy" in path_lower:
        return "functional"
    elif "runbook" in path_lower or "architecture" in path_lower or "api" in path_lower:
        return "technical"
    elif path.suffix == ".csv":
        return "tabular"
    else:
        return "operations"   # safe default for everything else
```

### What happens without profile routing — a real failure example

Imagine a corpus with two documents:
1. An HR leave policy (narrative, 800 words per section)
2. A Kubernetes runbook (procedural, 150 words per step)

If you apply `chunk_size=300` to both:

**HR policy at 300 tokens:** every chunk covers less than half a policy section. Rules get cut from exceptions. Every chunk is incomplete. ❌

**Runbook at 300 tokens:** each step is about 100-150 tokens. Three steps end up in each chunk. Commands get mixed across contexts. ❌

If you apply `chunk_size=700` to both:

**HR policy at 700 tokens:** most policy sections fit in one chunk. Rules and exceptions stay together. ✅

**Runbook at 700 tokens:** three or four runbook steps land in every chunk. Step 3 and Step 4 are both about different servers. LLM gets confused which steps apply. ❌

**Conclusion:** There is no single chunk size that serves both document types well. Profile-based routing is not optional — it is the only correct approach for a mixed corpus.

---

## Quick Decision Table: Strategy by Dataset Type

| Dataset Type | Chunk Strategy | Chunk Size | Overlap | Layers |
|---|---|---|---|---|
| Plain Text / Markdown | Recursive, paragraph-first | 400–600 | 60–100 | 1 |
| Markdown with headings | Header-split → recursive | 600–900 | 80–120 | 1–2 |
| PDF (standard) | Clean + recursive | 350–500 | 50–80 | 1 |
| PDF (tables/complex) | Unstructured elements | varies | varies | 1–2 |
| Technical docs | Heading + code-block aware | 400–500 | 80–110 | 1 |
| Functional / Policy | Section-first, large chunks | 600–750 | 100–130 | 1 |
| CSV / Tabular | Row chunks + group summaries | small rows | 0 | 2 |
| JSON records | Custom field-to-text conversion | varies | 0 | 1–2 |
| Database records | SQL query → labeled text | varies | 0 | 1–2 |
| Mixed corpus | Profile-based routing | per profile | per profile | per profile |
