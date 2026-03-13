# Common Chunking Mistakes and Production Lessons

> These are the mistakes that actually appear in real RAG systems — the things tutorials do not warn you about.

---

## Top 10 Chunking Mistakes

---

### Mistake 1: One global chunk size for everything

**What people do:**
```python
# Applied to all documents regardless of type
splitter = RecursiveCharacterTextSplitter(chunk_size=500)
```

**Why it fails:**
- A 500-token chunk is great for an article but terrible for a policy document
- A 500-token chunk is fine for narrative text but wrong for code
- Different content types have different optimal sizes

**The fix:**
Define chunk profiles per document family:
```python
profiles = {
    "functional": {"chunk_size": 700, "chunk_overlap": 120},
    "technical":  {"chunk_size": 500, "chunk_overlap": 90},
    "csv_rows":   {"chunk_size": 200, "chunk_overlap": 0},
    "code":       {"chunk_size": 1000, "chunk_overlap": 0}
}
```

---

### Mistake 2: Ignoring the embedding model's context window

**What people do:**
Set chunk_size=1000 with `all-MiniLM-L6-v2` (256 token max limit).

**Why it fails:**
- The model silently truncates to 256 tokens
- The remaining 744 tokens are thrown away
- Embeddings are corrupted without any error message

**The fix:**
Always check your embedding model's context window first.  
Set chunk_size at least 15% below the model's max.

---

### Mistake 3: No chunk overlap at all

**What people do:**
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
```

**Why it fails:**
A key sentence sits at the boundary between chunk 456 and chunk 457.  
Neither chunk contains it completely.  
Retrieval misses it entirely.

**The fix:**
Always set at least 10% overlap:
- chunk_size=500 → overlap=50 (minimum)
- chunk_size=500 → overlap=80–100 (recommended)

Exception: code chunking by function. No overlap needed there.

---

### Mistake 4: No metadata

**What people do:**
```python
Document(page_content=text)  # No metadata at all
```

**Why it fails:**
- Cannot filter by document type
- Cannot cite the source
- Cannot debug why wrong chunks are retrieved
- Cannot do date-aware retrieval

**The fix:**
Minimum metadata for every chunk:
```python
Document(
    page_content=text,
    metadata={
        "source": "policy.pdf",
        "doc_type": "policy",
        "section": "Leave Rules",
        "chunk_index": 4
    }
)
```

---

### Mistake 5: Not cleaning extracted text before chunking

**What people do:**
Chunk raw PDF extraction directly.

**Why it fails:**
Raw PDF text often contains:
- Extra whitespace and line breaks from column layouts
- Broken words from hyphenation
- Headers and footers repeated on every page
- Encoded characters like `ﬁ` instead of `fi`

These pollute embeddings and hurt retrieval.

**The fix:**
```python
import re

def clean_text(text: str) -> str:
    text = " ".join(text.split())              # normalize whitespace
    text = text.replace("ﬁ", "fi")            # fix ligatures
    text = text.replace("ﬂ", "fl")
    text = re.sub(r'\s{2,}', ' ', text)       # remove double spaces
    return text.strip()

# Apply before chunking
cleaned_text = clean_text(raw_pdf_text)
```

---

### Mistake 6: Splitting rules from their exceptions

**What people do:**
Chunk policy documents purely by character count.

**Why it fails:**
```
Chunk 7: "Employees are eligible for 20 days of annual leave provided they..."
Chunk 8: "...have completed their probation period. 
          Exception: Contract employees are not eligible."
```

A query about leave policy retrieves Chunk 7.  
The LLM confidently says everyone gets 20 days — missing the exception entirely.

**The fix:**
Use heading-first, semantic-aware splitting for policy/functional documents.  
Prefer section splits over character splits.

---

### Mistake 7: Evaluating chunking by chunk count — not retrieval quality

**What people do:**
"We now have 1,843 chunks — chunking is done!"

**Why it fails:**
Chunk count tells you nothing about retrieval quality.  
2,000 good chunks outperform 500 bad ones.

**The fix:**
Evaluate by running real benchmark queries and checking top-k retrieval.  
If the right answer is not in top-3, chunking (or metadata) needs fixing.

---

### Mistake 8: Splitting code at arbitrary character positions

**What people do:**
Use a generic text splitter on code files.

**Why it fails:**
```python
# Chunk 1 ends here:
def calculate_total(items):
    total = 0
    for item in items:
        total +=

# Chunk 2 starts here:
        item.price * item.quantity
    return total
```

Both chunks are broken and unembeddable as meaningful units.

**The fix:**
Use language-aware code splitters:
```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=0
)
```

---

### Mistake 9: Not chunking at all for "long-context" LLMs

**What people do:**
"GPT-4 Turbo has 128k tokens. I'll just dump the whole document in context."

**Why it fails:**
- Cost: 128k tokens per query = very expensive
- Latency: huge context = slow response
- Lost in the middle: relevant info buried mid-context is missed
- No citation: can't point to which part was used

**The fix:**
Even with 128k+ context windows, use chunking + retrieval.  
Use the large context as a ceiling for edge cases, not as a standard strategy.

---

### Mistake 10: Changing multiple parameters simultaneously

**What people do:**
"The results were bad, so I changed chunk_size AND overlap AND the splitter all at once."

**Why it fails:**
You cannot tell which change helped.  
Your "improved" config may actually have two changes helping and one hurting — and you'll never know.

**The fix:**
Change one variable at a time.  
Run same benchmark.  
Record result.  
Then change the next variable.

---

## Industry Lessons from Production Systems

---

### Lesson 1: Profile-based chunking is enterprise standard

Major production RAG systems (JP Morgan, Salesforce, enterprise deployments) do not use one chunk size.

They define **document families** with separate profiles:
- Customer-facing docs: different from internal ops docs
- Legal docs: different from engineering docs
- Real-time data: different from archive docs

Your chunking strategy should reflect how your users query, not just how your docs are structured.

---

### Lesson 2: Metadata quality directly impacts retrieval control

The teams that build the best RAG systems invest heavily in metadata design.

Good metadata enables:
- Filter by document type → only search policy docs when answering policy questions
- Filter by date → always prefer newest version
- Filter by team/department → scope queries to relevant domain
- Filter by environment → dev vs production docs separately

You cannot add useful metadata after the fact at query time.  
Design it upfront.

---

### Lesson 3: Test with real user questions — not hypothetical ones

The benchmark query set must use **actual questions real users ask**.

If your users ask:
- "How do I rollback the deployment?"
- "What changed in this sprint?"
- "Is contractor X eligible for leave?"

Your benchmark must have those. Not textbook questions like "What is Kubernetes?"

---

### Lesson 4: Chunk quality degrades over time if not maintained

As documents are updated, your chunks become stale.

Production systems need:
- Document change detection
- Selective re-chunking (not full reprocessing)
- Version tracking in metadata

---

### Lesson 5: The best chunk strategy is the one your retrieval metrics prove

No blog post, tutorial, or this document tells you the definitive best chunk size.

Only your data + your queries + your evaluation tell you that.

Use this as a starting point. Measure. Adjust. Repeat.

---

## Quick Reference: Chunking Anti-Pattern Summary

| Anti-Pattern | Impact | Fix |
|---|---|---|
| One chunk size for all docs | Poor retrieval across doc types | Use profiles per doc family |
| Chunk size > embedding model limit | Silent embedding truncation | Match chunk size to model limit |
| Zero overlap | Context lost at boundaries | Add 10–20% overlap |
| No metadata | No filtering, no citation, no debugging | Define metadata schema upfront |
| No text cleaning | Polluted embeddings | Clean before chunking |
| Rule split from exception | Wrong/incomplete answers | Use semantic or structure-aware splits |
| Evaluate by chunk count only | False confidence | Evaluate by top-k retrieval quality |
| Generic splitter on code | Broken code chunks | Use language-aware code splitter |
| Skip chunking for large LLMs | High cost, lost in middle | Always chunk + retrieve |
| Change multiple params at once | Can't isolate what helped | Change one variable at a time |
