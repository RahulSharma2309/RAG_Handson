# Common Chunking Mistakes and Production Lessons

> These are not hypothetical mistakes. They are the actual failure modes that appear when RAG systems are built by people who understand the concepts but miss the practice. Some of them produce subtly wrong answers. Some produce confidently wrong answers. A few of them have caused real operational incidents. Every mistake here is explained with the exact scenario that triggers it, the failure mode it produces, and the correct fix.

---

## Mistake 1 — One Global Chunk Size for All Document Types

### What it looks like

```python
# Applied to every document in the corpus, regardless of type
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

for doc in all_documents:   # policies, runbooks, CSVs, architecture docs
    chunks.extend(splitter.split_documents([doc]))
```

### The exact failure

Imagine a corpus with two document types:

**Document A — HR Leave Policy:**
```
## Annual Leave Entitlement

Full-time employees who have completed probation are entitled to 20 days per year.
Leave must be requested at least 14 days in advance via the HR portal.
Manager approval is required before confirmation.

Exceptions: Contract employees receive 10 days. PIP employees require HR Director approval.
```
This section is about 650 characters. At `chunk_size=500`, it splits mid-section:

```
Chunk 1 (500 chars): "Full-time employees who have completed probation are entitled...Manager approval is required before confirmation."
Chunk 2 (150 chars): "Exceptions: Contract employees receive 10 days. PIP employees require HR Director approval."
```

Rules are separated from exceptions. Retrieval for a contractor's leave question returns Chunk 1 only — the general entitlement — not the contractor exception. ❌

**Document B — Kubernetes Runbook Step:**
```
Step 4: Verify node health before applying patch.
Run: kubectl get nodes
Expected: All nodes STATUS=Ready
If any node is NotReady, abort the patch procedure.
```
This step is about 175 characters. At `chunk_size=500`, Step 4, Step 5, and Step 6 all land in the same chunk:

```
Chunk: "Step 4: Verify node health... Step 5: Apply the patch manifest: kubectl apply -f patch.yaml Step 6: Monitor pod restarts for 5 minutes..."
```

Three separate procedures are merged. A user asking about Step 6 retrieves context polluted with Steps 4 and 5 content. ❌

### The fix

```python
PROFILES = {
    "functional": {"chunk_size": 700, "chunk_overlap": 120},
    "technical":  {"chunk_size": 500, "chunk_overlap": 90},
    "csv_row":    {"chunk_size": 200, "chunk_overlap": 0},
    "code":       {"chunk_size": 1200, "chunk_overlap": 0},
}

def chunk_by_profile(doc, profile: str) -> list:
    config = PROFILES[profile]
    splitter = RecursiveCharacterTextSplitter(**config)
    chunks = splitter.split_documents([doc])
    for chunk in chunks:
        chunk.metadata["doc_family"] = profile
    return chunks
```

Different document families → different profiles. This is non-negotiable for mixed-source corpora.

---

## Mistake 2 — Ignoring the Embedding Model's Token Limit

### What it looks like

Setting `chunk_size=2000` characters and using `all-MiniLM-L6-v2` as the embedding model.

`all-MiniLM-L6-v2` has a 256-token maximum input length.

2000 characters ≈ 400–500 tokens.

### The exact failure

The embedding model receives a 450-token chunk. Silently, it processes only the first 256 tokens and discards the remaining 194 tokens. No error. No warning. No log entry.

The embedding vector represents only the first half of the chunk.

**Before truncation (full chunk):**
```
"The API Server is the front-end of the Kubernetes control plane. It exposes the Kubernetes API.
The Scheduler is responsible for watching newly created pods and assigning them to nodes.
The Controller Manager runs controller processes that regulate the state of the cluster.
etcd is a consistent and highly-available key-value store used as Kubernetes' backing store."
```

**What actually gets embedded (first 256 tokens only):**
```
"The API Server is the front-end of the Kubernetes control plane. It exposes the Kubernetes API.
The Scheduler is responsible for watching newly created pods and assigning them to nodes."
```

Now a query about "etcd" or the "Controller Manager" will not match this chunk — even though both are in it. The embedding has no idea those words exist in the chunk.

**What makes this particularly dangerous:** retrieval still "works" — it returns results, finds matches. The quality degradation is silent and invisible until you notice that certain queries consistently miss relevant content.

### The fix

```python
import tiktoken

def validate_chunk_sizes(chunks: list, model_limit: int, model_name: str = "cl100k_base"):
    enc = tiktoken.get_encoding(model_name)
    violations = [(i, len(enc.encode(c.page_content))) for i, c in enumerate(chunks)
                  if len(enc.encode(c.page_content)) > model_limit]

    if violations:
        print(f"⚠️  {len(violations)} chunks exceed {model_limit}-token limit:")
        for idx, count in violations[:5]:
            print(f"  Chunk {idx}: {count} tokens")
        print("Reduce chunk_size before indexing.")
    else:
        print(f"✅ All {len(chunks)} chunks within {model_limit}-token limit.")

# all-MiniLM-L6-v2 limit: 256 tokens
validate_chunk_sizes(chunks, model_limit=256)
```

**Reference limits:**
```
all-MiniLM-L6-v2       : 256 tokens → keep chunk_size ≤ 1000 chars
BAAI/bge-small-en-v1.5 : 512 tokens → keep chunk_size ≤ 2000 chars
text-embedding-3-small  : 8191 tokens → practically unlimited for normal text
```

---

## Mistake 3 — Zero Overlap

### What it looks like

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
```

"Overlap just duplicates content. I want a clean, non-redundant index."

### The exact failure

```
Document text (positions shown):
...0─────────────────────────────────────────────────────────1500...

Position 490-510 contains:
"...The rollback requires the --force flag. This flag bypasses validation..."

Chunk 1 ends at position 500:
"...The rollback requires the --force flag."

Chunk 2 starts at position 500:
"This flag bypasses validation and should only be used in emergency scenarios."
```

**Query:** "When should the --force flag be used?"

The semantic match is strongest with "should only be used in emergency scenarios" — which is in Chunk 2.

**Chunk 2:** "This flag bypasses validation and should only be used in emergency scenarios."

"This flag" — what flag? The word "--force" is in Chunk 1, which was not retrieved.

The LLM generates: "This flag should only be used in emergency scenarios." — ambiguous and incomplete. ❌

**With chunk_overlap=100:**

Chunk 2 starts at position 400 (100-char overlap with Chunk 1):
"...The rollback requires the --force flag. This flag bypasses validation and should only be used in emergency scenarios."

Now "the --force flag" and "should only be used in emergencies" are in the same chunk. ✅

### The fix

Always set at minimum 10% overlap:
```python
chunk_size=500   → chunk_overlap=50   (minimum)
chunk_size=500   → chunk_overlap=80   (recommended for technical docs)
chunk_size=700   → chunk_overlap=120  (recommended for functional docs)
```

**The only valid exception:** code chunking by function boundaries. If you split at function/class boundaries, there is no natural overlap — each function is a complete unit.

---

## Mistake 4 — No Metadata on Chunks

### What it looks like

```python
from langchain_core.documents import Document

chunks = [Document(page_content=text) for text in split_texts]
# No metadata at all
```

### The four failure modes this creates

**Failure 1 — No source citation**  
The LLM generates an answer. The user asks: "Where did this come from?"  
Answer: impossible to say. The chunk has no source field. Trust evaporates.

**Failure 2 — No domain filtering**  
A query about the "leave policy" retrieves chunks from policies, technical docs, marketing SOPs — all equally. No way to restrict "search only HR policy documents."

**Failure 3 — No version control**  
An outdated v2 policy and the current v5 policy are both indexed without version metadata. Queries might return v2 answers confidently. No way to filter by `effective_date`.

**Failure 4 — No debugging**  
Retrieval produces wrong results. Where did the wrong chunk come from? What section? Which document? Unknown. Every debugging session becomes a needle-in-haystack hunt.

### The fix — minimum metadata schema

```python
Document(
    page_content=text,
    metadata={
        "source": "hr-policy-v5.docx",      # always — enables citation
        "doc_type": "policy",               # always — enables domain filtering
        "section_title": "Annual Leave",    # strongly recommended — enables debugging
        "chunk_index": 4,                   # recommended — enables position tracking
        "doc_family": "functional",         # recommended — enables profile filtering
    }
)

# For functional documents, add:
#   "version", "effective_date", "owner_team"

# For technical documents, add:
#   "service_name", "environment", "system_area", "contains_code"

# For CSV/tabular documents, add:
#   "row_index", "group_by", "group_value"
```

---

## Mistake 5 — Chunking Raw PDF Text Without Cleaning

### What it looks like

```python
loader = PyMuPDFLoader("document.pdf")
pages = loader.load()
chunks = splitter.split_documents(pages)   # no cleaning step
```

### The exact failure

A real PDF of a technical guide contains this content on page 8:
```
## Kubernetes Node Management

To add a new node to the cluster, use the following com-
mand with the appropriate configuration: kubeadm join
192.168.1.100:6443 --token abc123
```

Raw PyMuPDF extraction gives:
```
"## Kubernetes Node Management\n\nTo add a new node to the cluster, use the following com-\nmand with the appropriate configuration: kubeadm join\n192.168.1.100:6443 --token abc123"
```

The word "command" is now "com-\nmand" — split by hyphenation across a line break.

The embedding for this chunk will not strongly match a query for "how to add a node" because:
- "com-\nmand" is not "command" — it tokenizes differently
- The IP address and token are in the embedding but diluted by the broken word

Additionally, most pages of this PDF have a footer: `KUBERNETES ADMINISTRATION GUIDE | INTERNAL | Page 8 of 42`

That footer text appears in every chunk from this document. Every chunk now has "INTERNAL" in its embedding. Queries about anything internal across all document types will weakly match this chunk.

### The fix

```python
import re

def clean_pdf_text(text: str) -> str:
    text = re.sub(r'-\n', '', text)              # fix hyphenated line breaks
    text = re.sub(r'Page \d+ of \d+', '', text)  # remove page numbers
    text = re.sub(r'\n{3,}', '\n\n', text)       # normalize excessive newlines
    text = text.replace("ﬁ", "fi")              # fix ligatures
    text = text.replace("ﬂ", "fl")
    text = re.sub(r'[A-Z ]{20,}\|[A-Z ]+\|[A-Z ]+', '', text)  # remove ALL-CAPS headers/footers
    text = " ".join(text.split())                # normalize whitespace
    return text.strip()

# Always clean before chunking
for page in pages:
    page.page_content = clean_pdf_text(page.page_content)
chunks = splitter.split_documents(pages)
```

---

## Mistake 6 — Splitting Business Rules from Their Exceptions

### What it looks like

Any character-count-based chunking of policy documents without section awareness.

### The exact failure

**HR Reimbursement Policy:**
```
Employees are entitled to reimbursement for all approved business travel expenses
including flights, hotels, and ground transportation. Receipts must be submitted
within 30 days of the travel date via the expense portal. Manager approval is
required for expenses exceeding £500.

Exclusions: Personal travel extensions, companion tickets, first-class upgrades
(unless on flights longer than 6 hours), and entertainment expenses not pre-approved
by the department head are not reimbursable.
```

At 400-character chunks with no section awareness:

```
Chunk A: "Employees are entitled to reimbursement for all approved business travel
expenses including flights, hotels, and ground transportation. Receipts must be
submitted within 30 days of the travel date via the expense portal."

Chunk B: "Manager approval is required for expenses exceeding £500.

Exclusions: Personal travel extensions, companion tickets, first-class upgrades
(unless on flights longer than 6 hours), and entertainment expenses not pre-approved"

Chunk C: "by the department head are not reimbursable."
```

**Query:** "Are flight upgrades reimbursable?"

The exclusion about upgrades is split across Chunks B and C. The retriever returns Chunk B (contains "first-class upgrades") but Chunk B has the exclusion clause cut off mid-sentence: "first-class upgrades (unless on flights longer than 6 hours)..."

**LLM answer:** "First-class upgrades are not reimbursable, with an exception for flights longer than 6 hours."

Actually correct! But only because the condition survived in Chunk B. Now try:

**Query:** "What travel expenses are excluded from reimbursement?"

The retriever returns Chunk B. "Not pre-approved by the department head are not reimbursable" is in Chunk C and not retrieved.

**LLM answer:** "Personal travel extensions, companion tickets, and first-class upgrades (with exception) are excluded." — missing the entertainment expense exclusion. ❌

### The fix

Use section-aware splitting with `"\n## "` as primary separator. For documents without Markdown headings, build a section-aware loader using python-docx or by detecting capitalized section headers.

---

## Mistake 7 — Evaluating Chunking by Chunk Count

### What it looks like

"We now have 2,847 chunks. The ingestion pipeline is complete."

### Why it fails

Chunk count is the output of the splitting process. It says nothing about whether the splits are semantically correct, whether metadata is complete, whether retrieval works, or whether the system will produce correct answers.

2,847 chunks with broken boundaries, no metadata, and overlapping content from document families → terrible retrieval.

200 chunks with clean semantic boundaries, full metadata, and appropriate overlap → excellent retrieval.

**The question is never "how many chunks?" The question is always "does retrieval work?"**

### The fix

The only valid completion criterion is passing the benchmark evaluation from document 10:
- Top-3 hit rate ≥ 70%
- Average quality score ≥ 4.0 / 6.0
- Metadata completeness ≥ 95%
- Token limit violations = 0

If these pass: chunking is done.  
If they don't: chunking is not done, regardless of chunk count.

---

## Mistake 8 — Splitting Source Code at Arbitrary Character Positions

### What it looks like

```python
# Generic splitter applied to Python code
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
code_chunks = splitter.split_text(python_file_content)
```

### The exact failure

```python
# Chunk 1 ends here — mid-function:
def calculate_discount(order_value: float, customer_tier: str) -> float:
    """Calculate discount based on order value and customer tier."""
    if customer_tier == "premium":
        if order_value >= 1000:
            return 0.20
        elif order_value >= 500:
            return 0.15

# Chunk 2 starts here:
        else:
            return 0.10
    elif customer_tier == "standard":
        if order_value >= 1000:
            return 0.10
        else:
            return 0.05
    return 0.0
```

Chunk 1 contains an incomplete function — missing the else branch and the standard tier logic.  
Chunk 2 starts with `else:` — which is orphaned Python syntax, meaningless without the if statement.

Neither chunk is valid Python. Neither embeds meaningfully. A query about "discount calculation" might retrieve Chunk 1 and the LLM will describe incomplete logic.

### The fix

```python
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

# Language-aware splitter respects Python function and class boundaries
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1500,
    chunk_overlap=0   # no overlap needed — function boundaries are clean
)

code_chunks = python_splitter.create_documents(
    texts=[code_content],
    metadatas=[{"source": file_path, "doc_type": "python_code", "language": "python"}]
)

# Supported languages: PYTHON, JS, TS, GO, RUST, JAVA, CPP, RUBY, etc.
```

---

## Mistake 9 — "My LLM Has 128k Tokens, I Don't Need Chunking"

### What it looks like

"GPT-4o supports 128k token context. My entire knowledge base is 80k tokens. I'll just dump it all in the prompt."

### The four reasons this is wrong

**Reason 1 — Cost**  
Sending 80k tokens on every user query, regardless of what they're asking:

```
80,000 tokens × $0.000015/token (input) = $1.20 per query
1,000 queries/day = $1,200/day = $36,000/month
```

With chunking and retrieval (top-5 chunks, ~500 tokens each = 2,500 tokens):
```
2,500 tokens × $0.000015 = $0.038 per query
1,000 queries/day = $38/day = $1,140/month
```

**97% cost reduction from chunking + retrieval vs full-context.**

**Reason 2 — The "Lost in the Middle" Phenomenon**  
Research shows LLMs perform significantly worse at recalling information from the middle of a large context window compared to the beginning or end. In an 80k token context, information at position 40k-60k may be effectively invisible to the model.

With chunking, relevant content is retrieved and placed at the beginning of the context — in the model's high-attention zone.

**Reason 3 — Latency**  
Processing 80k tokens takes measurably longer than processing 2,500 tokens. For user-facing applications, this difference (3–10 seconds) is noticeable and impacts user experience.

**Reason 4 — No Citation**  
When the LLM answers using the full document context, there is no way to know which specific section or document contributed to the answer. You cannot cite sources, cannot debug wrong answers, and cannot build user trust.

### The fix

Chunk + retrieve even with large-context LLMs. Use the large context window as a ceiling for edge cases (retrieving more chunks when the query requires it), not as the standard operating mode.

---

## Mistake 10 — Changing Multiple Parameters Simultaneously

### What it looks like

"The retrieval quality was bad. I changed chunk_size from 500 to 300, overlap from 50 to 100, and switched from RecursiveCharacterTextSplitter to SemanticChunker. Now it's better!"

### Why this is a problem

You made three changes. Results improved. But:
- Which change caused the improvement?
- Did one change help while another hurt?
- If you added a new document type tomorrow, which parameter would you adjust?
- What if results are bad on a new query set — what do you roll back?

The answer to all four: you don't know.

### The exact scenario where this burns you

```
Experiment: Changed chunk_size 500→300, overlap 50→100, RecursiveCharacter→Semantic

Before: Top-3 hit rate 62%
After:  Top-3 hit rate 74%   ← improvement!

Three weeks later: new document type added, retrieval quality drops.
Which parameter needs adjusting? You have no baseline for any individual change.
```

```
Proper approach:

Experiment 1: chunk_size 500→300 (only)
  Before: 62%
  After:  70%   ← this change helped

Experiment 2: overlap 50→100 (keeping chunk_size=300)
  Before: 70%
  After:  75%   ← this change also helped

Experiment 3: switch to SemanticChunker (keeping size=300, overlap=100)
  Before: 75%
  After:  74%   ← this change didn't help! Actually slightly worse.

Decision: keep RecursiveCharacterTextSplitter (faster, cheaper, same or better results)
```

You learned that semantic chunking, for this document set, was not worth the cost and complexity. That is valuable knowledge — only possible because you changed one thing at a time.

### The fix

Change one parameter per experiment. Run the same benchmark set. Record results in the experiment log from document 09. Never change two things at once unless you have a specific reason.

---

## Industry Lessons from Production Systems

### Lesson 1 — Metadata design decisions cannot be made retroactively

The most expensive error in production RAG is discovering — after you have indexed 50,000 chunks — that you forgot to add a critical metadata field.

Example: you indexed all HR documents without `effective_date`. Six months later, users start getting answers from outdated policies. To fix it, you must re-chunk and re-index everything.

**The lesson:** spend 30 minutes designing your complete metadata schema before writing the first chunking function. Add every field you might ever want to filter on. Adding metadata fields is free at ingestion time and extremely expensive afterward.

### Lesson 2 — Separate chunk artifacts from your index

Always save chunked documents as JSONL files before indexing them. Never rebuild chunks from the raw documents every time you update the index.

```python
import json
from langchain_core.documents import Document

def save_chunks_to_jsonl(chunks: list, output_path: str) -> None:
    with open(output_path, "w") as f:
        for chunk in chunks:
            record = {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata
            }
            f.write(json.dumps(record) + "\n")

def load_chunks_from_jsonl(path: str) -> list:
    chunks = []
    with open(path, "r") as f:
        for line in f:
            record = json.loads(line)
            chunks.append(Document(**record))
    return chunks
```

This lets you:
- Version control your chunk configurations
- Re-embed chunks without re-chunking (when you change embedding models)
- Audit what was indexed for debugging
- Roll back to a previous chunk configuration immediately

### Lesson 3 — Real user questions look nothing like document headings

Developers write benchmark queries like: "What does the Annual Leave policy state?"

Users ask: "Can my intern take a week off next month if she started two months ago?"

The difference in phrasing changes the embedding. A small model might not bridge the semantic gap between "Annual Leave policy" and "intern taking a week off."

**The lesson:** collect actual user queries from your chat logs, tickets, and Slack messages. Use those as your benchmark set. If you don't have user data yet, ask the domain experts what questions they field regularly — not what the document is about.

### Lesson 4 — Chunk quality degrades as documents are updated

When document v2 is published, your index may contain:
- Chunks from v1 (outdated)
- Chunks from v2 (current)

Both indexed simultaneously. Retrieval returns whichever has higher similarity — not whichever is newer.

**The lesson:** build a document update pipeline:
1. When a document is updated, detect the update (file hash, modification date, document version)
2. Delete all chunks from the old version
3. Chunk and index the new version
4. Never allow multiple versions of the same document to coexist in the index unless version filtering is explicitly designed for it

### Lesson 5 — Chunking strategy is a product decision, not a technical one

The best chunk size for your RAG system depends on:
- What questions your users actually ask
- How much context each answer requires
- What citation format builds user trust
- How much latency users will tolerate
- What your cost budget is per query

These are product and business decisions. The developer who owns the chunking pipeline needs input from the team that owns the user experience. Chunking done in isolation, without understanding actual user query patterns, will be wrong.
