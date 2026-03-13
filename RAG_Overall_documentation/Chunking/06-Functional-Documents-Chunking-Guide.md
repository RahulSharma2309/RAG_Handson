# Functional Documents Chunking Guide

> Functional documents carry business rules, decisions, policies, and workflows. They are the documents that govern how people work — and when they are chunked poorly, your RAG system confidently gives wrong answers about those rules. This guide explains exactly how to chunk functional documents correctly, why the wrong approach causes specific failures, and what every chunk needs to carry to be trustworthy.

---

## What Counts as a Functional Document

Functional documents include:
- **HR policies** — leave, reimbursement, code of conduct, performance management
- **Product Requirements Documents (PRDs)** — features, acceptance criteria, user flows
- **Standard Operating Procedures (SOPs)** — process steps, approval chains
- **Business process docs** — customer journey flows, escalation procedures
- **Contracts and SLAs** — obligations, penalties, conditions, exceptions
- **Compliance documents** — regulatory requirements, audit controls
- **Business roadmaps** — quarterly objectives, milestones, owners

What they all share: **business meaning is carried in complete logical units — not in individual sentences or characters.** A rule without its exception is incomplete. A condition without its outcome is meaningless. A workflow step without its trigger makes no sense.

This is what makes functional document chunking different from technical or narrative chunking — the unit of meaning is the **policy section**, not the paragraph or sentence.

---

## The Core Problem: Rules and Exceptions Get Separated

Let's start with the failure mode that causes the most business damage.

### A real HR policy document

```
## Annual Leave Entitlement

Full-time employees who have completed their probation period are entitled
to 20 working days of paid annual leave per calendar year.

Leave must be requested through the HR portal at least 14 days in advance.
Direct manager approval is required before leave is confirmed.

Accrual: Leave accrues at the rate of 1.67 days per month starting from
the employee's hire date.

Exceptions and Special Cases:

Contract employees: entitled to 10 working days regardless of tenure.

Employees on a Performance Improvement Plan (PIP): entitled to 20 days
but must obtain HR Director approval for any leave request.

Employees hired after October 1st: entitlement is prorated by the
remaining months in the calendar year.

Part-time employees: entitlement is prorated based on contracted hours
relative to a 40-hour standard week.
```

---

### Case 1 — Bad chunking (recursive, default 300 tokens, no section awareness)

```
Chunk 1 (287 chars):
"Full-time employees who have completed their probation period are entitled
to 20 working days of paid annual leave per calendar year. Leave must be
requested through the HR portal at least 14 days in advance."

Chunk 2 (301 chars):
"Direct manager approval is required before leave is confirmed.

Accrual: Leave accrues at the rate of 1.67 days per month starting from
the employee's hire date."

Chunk 3 (298 chars):
"Exceptions and Special Cases:

Contract employees: entitled to 10 working days regardless of tenure.

Employees on a Performance Improvement Plan (PIP): entitled to 20 days
but must obtain HR Director approval for any leave request."

Chunk 4 (201 chars):
"Employees hired after October 1st: entitlement is prorated by the
remaining months in the calendar year.

Part-time employees: entitlement is prorated based on contracted hours."
```

Now observe what happens for four different user queries:

**Query 1:** "How many leave days am I entitled to?"  
Retriever returns Chunk 1 — highest semantic match to "entitled to X days."  
LLM says: "You are entitled to 20 working days of annual leave."  
User is a contract employee. ❌ Wrong answer.

**Query 2:** "I joined on November 15th. How many leave days do I get this year?"  
Retriever might return Chunk 1 (general entitlement) or Chunk 3 (exceptions) depending on embedding similarity.  
Neither contains the October 1st proration rule from Chunk 4.  
LLM answers with general entitlement. ❌ Incomplete answer.

**Query 3:** "I'm on a PIP. Can I take leave?"  
Retriever returns Chunk 3.  
LLM says: "Yes, you are entitled to 20 days but need HR Director approval."  
Partially correct but Chunk 3 didn't retrieve the general request process from Chunk 2.  
The answer is incomplete about how to request it. ⚠️ Partial answer.

**Query 4:** "What is the leave accrual rate?"  
Retriever must find Chunk 2.  
Chunk 2 has the accrual rate but starts with "Direct manager approval..." — the semantic match to "accrual rate" is diluted by the other content.  
Retrieval may miss this. ❌ Unreliable.

---

### Case 2 — Good chunking (section-first, 700 tokens, 120 overlap)

```
Chunk 1:
## Annual Leave Entitlement
Full-time employees who have completed their probation period are entitled
to 20 working days of paid annual leave per calendar year.

Leave must be requested through the HR portal at least 14 days in advance.
Direct manager approval is required before leave is confirmed.

Accrual: Leave accrues at the rate of 1.67 days per month starting from
the employee's hire date.

Exceptions and Special Cases:
Contract employees: entitled to 10 working days regardless of tenure.
Employees on a Performance Improvement Plan (PIP): entitled to 20 days
but must obtain HR Director approval for any leave request.
Employees hired after October 1st: entitlement is prorated by the
remaining months in the calendar year.
Part-time employees: entitlement is prorated based on contracted hours
relative to a 40-hour standard week.

Metadata: {section_title: "Annual Leave Entitlement", doc_type: "policy", version: "v5.1"}
```

This entire section — rule + process + accrual + all four exceptions — fits in one chunk at 700 tokens.

**Query 1:** "How many leave days am I entitled to?"  
LLM has all conditions: full-time gets 20, contract gets 10, PIP needs director approval, proration for late joiners. ✅ Complete answer for any employee type.

**Query 2:** "I joined November 15th. How many days do I get?"  
LLM has the October 1st proration rule and can calculate. ✅

**Query 3:** "I'm on a PIP. Can I take leave?"  
LLM has both the entitlement and the director approval requirement. ✅

**Query 4:** "What is the leave accrual rate?"  
LLM has "1.67 days per month" in context. ✅

---

### Why this works

The section `## Annual Leave Entitlement` is a complete **logical unit** of business information. Every sub-item within it modifies or conditions the main rule. They belong together — semantically and logically.

The 300-token chunking treated the text as words-on-a-page and split at arbitrary positions. The 700-token section-aware chunking treated the text as **structured business logic** and split at meaningful boundaries.

---

## The Five Categories of Content That Must Stay Together

These are the patterns that chunking must preserve in functional documents:

### 1 — Rule and Exception Together

```
❌ SPLIT:
Chunk A: "Employees are entitled to reimbursement for business travel expenses."
Chunk B: "Exception: Personal travel or spouse/family extensions are not reimbursable."

✅ TOGETHER:
"Employees are entitled to reimbursement for business travel expenses.
Exception: Personal travel or spouse/family extensions are not reimbursable."
```

If the exception is in a different chunk, every query about the rule will produce a confidently incomplete answer.

### 2 — Condition and Outcome Together

```
❌ SPLIT:
Chunk A: "If an employee is absent for more than 5 consecutive days without notice..."
Chunk B: "...the absence will be treated as unauthorized leave and may trigger disciplinary action."

✅ TOGETHER:
"If an employee is absent for more than 5 consecutive days without notice,
the absence will be treated as unauthorized leave and may trigger disciplinary action."
```

A condition without its outcome is meaningless. An outcome without its condition is misleading.

### 3 — Multi-Step Workflow Complete

```
❌ SPLIT:
Chunk A: "Step 1: Employee submits leave request in HR portal.
          Step 2: Manager receives notification and reviews request."
Chunk B: "Step 3: Manager approves or rejects within 3 business days.
          Step 4: Employee receives confirmation email.
          Step 5: If rejected, employee may escalate to HR."

✅ TOGETHER (all 5 steps in one chunk):
Complete workflow as a single retrievable unit.
```

Users ask "how do I apply for leave?" They need the complete workflow, not half of it.

### 4 — Approval Chain Complete

```
❌ SPLIT:
Chunk A: "Expenses above £500 require manager approval."
Chunk B: "Expenses above £2,000 require Director approval. Expenses above £10,000
          require CFO sign-off. All reimbursements are processed within 30 days."

✅ TOGETHER:
Full threshold table and approval chain in one chunk.
```

Splitting an approval chain at an arbitrary token position creates chunks that give partial approval authority guidance — potentially misleading.

### 5 — Definition and Application Together

```
❌ SPLIT:
Chunk A: "A 'continuous service period' is defined as uninterrupted employment
          with the organization without a break of more than 7 days."
Chunk B: "Employees with 5 or more years of continuous service are entitled
          to an additional 5 days of annual leave."

✅ TOGETHER:
The definition in Chunk A makes Chunk B interpretable. Without it, users cannot understand what "continuous service" means in the entitlement context.
```

---

## Recommended Chunking Profile for Functional Documents

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

functional_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,       # target size in characters
    chunk_overlap=120,    # 17% overlap — preserves transitions between sections
    separators=[
        "\n## ",          # H2 section heading — primary split point
        "\n### ",         # H3 subsection — secondary split point
        "\n\n",           # paragraph break — tertiary
        "\n",             # line break — but preserves bullet lists
        ". ",             # sentence boundary (only if above fail)
        " ",              # word boundary (emergency)
        ""                # character (last resort)
    ]
)
```

**Why `chunk_size=700`:**
Most functional document sections (rule + conditions + exceptions + procedure) fit within 600–700 characters. Setting the limit at 700 means most sections become exactly one chunk without overflow.

**Why `chunk_overlap=120`:**
When a section does overflow into two chunks, the overlap ensures the second chunk begins with context from the end of the first — preserving the logical transition (e.g., an exception clause that was partially in the first chunk will appear again at the start of the second).

**Why `"\n## "` is first:**
This ensures that `##` section breaks in Markdown are always honored as chunk boundaries before any other rule applies. A policy document's `## Disciplinary Process` section should never bleed into `## Appeal Procedure` within the same chunk.

---

## Metadata Schema for Functional Document Chunks

Every functional document chunk must carry this metadata:

```python
{
    # Where it came from
    "source": "hr-policy-annual-leave-v5.docx",
    "doc_type": "policy",              # policy | prd | sop | contract | sla

    # What section it is
    "section_title": "Annual Leave Entitlement",

    # When this version is valid
    "version": "v5.1",
    "effective_date": "2024-01-01",
    "expiry_date": "2024-12-31",       # if applicable

    # Who owns it
    "owner_team": "Human Resources",
    "document_owner": "Sunita Kapoor",

    # For retrieval control
    "chunk_index": 3,
    "total_chunks": 12,
    "doc_family": "functional"
}
```

### Why each field matters

**`version` and `effective_date`**  
Users ask "what is the current policy?" Without date metadata, there is no way to enforce "return only the latest version" at query time. An outdated policy version retrieved with high confidence is worse than no result — it will produce wrong answers the user trusts.

**`owner_team`**  
Filters retrieval to the right domain. "What is the leave policy?" should only search HR documents, not Marketing SOPs or Finance contracts.

**`section_title`**  
Critical for citation and debugging. When the LLM answer is traced back to source, the user needs to know not just the document but the exact section. "HR Policy, Section: Annual Leave Entitlement" is a trustworthy citation.

**`doc_type`**  
Enables policy-vs-PRD-vs-SLA differentiation at retrieval time. A query about "approval process" should probably search policies and SOPs — not product roadmaps.

---

## Question Patterns That Functional Chunks Must Answer

Before finalizing your chunking strategy for a functional document set, test these question types against your top-3 retrieved chunks:

| Question Pattern | What Retrieval Must Return |
|---|---|
| "What is the policy on X?" | The policy section including all exceptions |
| "Who approves X?" | The approval chain, complete, in one chunk |
| "What are the exceptions to X?" | The exception clause alongside the main rule |
| "What changed in the latest version?" | The section marked with the current `effective_date` |
| "Am I eligible for X?" | Eligibility criteria including all conditions |
| "What is the process for X?" | Complete workflow steps, not partial |
| "What happens if I miss the deadline for X?" | Consequence clause adjacent to the requirement |

If any of these fail in top-3 retrieval, the chunk boundaries or metadata need adjusting.

---

## Practical Tuning Guide for Functional Documents

### Symptom: Answers are generic — missing specific conditions

**Cause:** Chunks are too large and contain too many topics.  
**Fix:** Reduce `chunk_size` by 100–150 tokens. Each section should have its own chunk.

---

### Symptom: Answers always miss the exception clause

**Cause:** Rules and exceptions are in different chunks.  
**Fix:** Increase `chunk_overlap` to 150–200. Or use section-aware splitting with `## ` as primary separator to keep sections whole.

---

### Symptom: Wrong version of the policy is retrieved

**Cause:** Multiple versions indexed, no date filtering at retrieval.  
**Fix:** Add `effective_date` to metadata. At query time, filter: `metadata["effective_date"] >= "2024-01-01"`. Or remove old versions from the index entirely.

---

### Symptom: Query returns policies from the wrong department

**Cause:** No `owner_team` or `doc_type` filtering.  
**Fix:** Add `owner_team` to metadata. Use metadata filters at retrieval: only search `doc_type=policy` when answering policy questions.

---

### Symptom: Multi-step workflow is answered incompletely

**Cause:** Numbered steps are split across chunks.  
**Fix:** Treat the entire numbered list as one chunk. Use `\n## ` splitting — not paragraph splitting — to keep lists intact.

---

## End-to-End Example: Processing a Policy Document

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_functional_document(
    file_path: str,
    doc_type: str,
    version: str,
    effective_date: str,
    owner_team: str
) -> list:
    """
    Load and chunk a functional document with full metadata.
    """
    # Load
    loader = TextLoader(file_path, encoding="utf-8")
    raw_docs = loader.load()

    # Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(raw_docs)

    # Enrich metadata
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        # Extract section title from chunk if heading present
        first_line = chunk.page_content.strip().split("\n")[0]
        section = first_line.replace("## ", "").replace("### ", "").strip() \
                  if first_line.startswith("#") else "Body"

        chunk.metadata.update({
            "doc_type": doc_type,
            "version": version,
            "effective_date": effective_date,
            "owner_team": owner_team,
            "section_title": section,
            "chunk_index": i,
            "total_chunks": total,
            "doc_family": "functional",
            "char_count": len(chunk.page_content),
        })

    return chunks

# Usage
chunks = process_functional_document(
    file_path="policies/hr-annual-leave-v5.md",
    doc_type="policy",
    version="v5.1",
    effective_date="2024-01-01",
    owner_team="Human Resources"
)

print(f"Total chunks: {len(chunks)}")
for chunk in chunks[:3]:
    print(f"  [{chunk.metadata['section_title']}] {len(chunk.page_content)} chars")
```

**Expected output:**
```
Total chunks: 9
  [Annual Leave Entitlement] 682 chars
  [Public Holidays] 241 chars
  [Sick Leave Policy] 588 chars
```

Each section becomes its own chunk, complete, with full metadata. The annual leave section — with all its exceptions — fits entirely in one 682-character chunk.

---

## Functional Chunking Checklist

Before indexing functional document chunks, verify:

- [ ] Every section heading (`## `) is a chunk boundary, not split mid-section
- [ ] Every rule is in the same chunk as its exception clause
- [ ] Every multi-step workflow is in a single chunk (no partial lists)
- [ ] Every approval threshold table is in one chunk
- [ ] `version` and `effective_date` metadata is present on every chunk
- [ ] `owner_team` and `doc_type` metadata is present for filtering
- [ ] `section_title` is accurate and human-readable in metadata
- [ ] Top-3 retrieval for a sample policy question returns the right section
- [ ] No duplicate old versions are indexed alongside current versions
