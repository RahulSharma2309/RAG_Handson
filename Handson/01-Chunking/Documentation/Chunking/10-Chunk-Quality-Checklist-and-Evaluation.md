# Chunk Quality Checklist and Evaluation

> "Chunking is done when I have X chunks." This statement is wrong and dangerous. Chunk count tells you nothing about retrieval quality. You could have 2,000 perfectly structured chunks that produce excellent answers, or 2,000 broken chunks that produce confident wrong answers. This document gives you a complete, measurable evaluation framework — so you know when chunking is actually done and when it needs fixing.

---

## The Fundamental Evaluation Principle

Chunking quality is measured by **retrieval quality**, not by chunk structure.

You do not evaluate chunking by:
- ❌ Number of chunks created
- ❌ Average chunk size
- ❌ Whether the chunks look clean when printed
- ❌ Whether the splitter ran without errors

You evaluate chunking by:
- ✅ Does the right chunk appear in top-3 results for real user queries?
- ✅ Does the retrieved chunk contain enough context for a complete answer?
- ✅ Are citations accurate and traceable?
- ✅ Is the noise level (irrelevant results) acceptably low?

If you cannot answer yes to all four, your chunking needs work — regardless of what the chunks look like.

---

## Why Retrieval Evaluation Reveals What Visual Inspection Cannot

You can look at a chunk and think it looks good. Here is a chunk that looks fine:

```
Chunk #47:
"Employees are entitled to 20 days of annual leave per calendar year.
Leave requests must be submitted at least 14 days in advance.
Metadata: {source: hr-policy.docx, doc_type: policy}"
```

It looks complete. It has metadata. It seems fine.

But what you cannot see by looking at it:
- The exception clause for contract employees is in Chunk #48 — never retrieved alongside this
- The `version` and `effective_date` metadata is missing — users may get outdated policy
- The query "how many leave days for a contractor?" does not retrieve Chunk #47 at all — it retrieves Chunk #48 with the exception, but Chunk #48 has no general entitlement context

The only way to discover these problems is to **run the actual retrieval** and inspect results.

---

## Phase 1 — Build a Benchmark Query Set

The benchmark query set is the foundation of all evaluation. Without it, you are flying blind.

### What makes a good benchmark query

A good benchmark query:
1. Comes from the actual use case (not made up by the developer)
2. Has a clearly identifiable expected answer location
3. Represents a full distribution of query types (not just easy ones)
4. Is phrased the way real users would phrase it (not like the document is worded)

**Bad benchmark queries (developer phrases, not user phrases):**
```
- "What does the 'Annual Leave Entitlement' section state?"
- "Summarize the 'Rollback Procedure' runbook section"
```
These are essentially retrieval shortcuts — they use the exact section heading. Real users do not ask this way.

**Good benchmark queries (real user phrases):**
```
- "Can a contractor take 20 days leave?"
- "I need to rollback the API server urgently — what do I do?"
- "Who approves expenses over £2000?"
- "What happens if I don't submit my leave request 14 days in advance?"
- "What's the difference between staging and production deployment?"
```

### Query type distribution

Build your 20–40 queries across these types:

| Type | Description | Example |
|---|---|---|
| Specific lookup | Single factual answer | "What is the reimbursement limit for taxis?" |
| Policy with exception | Rule + condition | "Are contractors eligible for the bonus?" |
| Procedure | How-to steps | "How do I deploy a new version to production?" |
| Troubleshooting | Symptom → solution | "The pod is in CrashLoopBackOff. What do I check?" |
| Comparative | A vs B | "What's the difference between EKS and self-managed K8s?" |
| Analytical | Aggregate insight | "What is the average salary in the Engineering team?" |
| Cross-document | Needs multiple sources | "How does the leave policy interact with the performance review cycle?" |

Each query should have:
```python
benchmark_item = {
    "id": "Q003",
    "query": "Can a contractor take 20 days annual leave?",
    "expected_source": "hr-policy-v5.docx",
    "expected_section": "Annual Leave Entitlement",
    "must_contain": ["contractor", "10 days"],    # answer validation
    "must_not_contain": ["20 days"],               # wrong answer detection
}
```

---

## Phase 2 — Run Retrieval and Score Each Query

### The scoring rubric

Score each query on three dimensions:

**Dimension 1: Source Hit Rate**
```
2 = Expected source is in top-1
1 = Expected source is in top-3 but not top-1
0 = Expected source not found in top-5
```

**Dimension 2: Context Completeness**
```
2 = Retrieved chunk(s) contain all necessary context for a full answer
1 = Retrieved chunk(s) contain partial context — answer will be incomplete
0 = Retrieved chunk(s) do not contain the answer despite correct source
```

**Dimension 3: Noise Level**
```
2 = All top-3 results are relevant to the query
1 = 1-2 top-3 results are irrelevant (noise)
0 = Majority of top-3 results are irrelevant
```

**Total per query: 0–6 points.**  
**Acceptable threshold: ≥ 4 per query, ≥ 4.5 average across all queries.**

### Running the evaluation

```python
from langchain_core.vectorstores import VectorStore
import json

def evaluate_retrieval(
    retriever,
    benchmark: list,
    top_k: int = 5
) -> dict:
    """
    Run all benchmark queries and score results.
    Returns per-query scores and aggregate metrics.
    """
    results = []

    for item in benchmark:
        # Retrieve
        retrieved = retriever.get_relevant_documents(item["query"])[:top_k]

        # Check source hit
        sources = [r.metadata.get("source", "") for r in retrieved]
        if item["expected_source"] in sources[:1]:
            source_score = 2
        elif item["expected_source"] in sources[:3]:
            source_score = 1
        else:
            source_score = 0

        # Check content completeness
        retrieved_text = " ".join([r.page_content for r in retrieved[:3]])
        completeness_score = 2
        for required in item.get("must_contain", []):
            if required.lower() not in retrieved_text.lower():
                completeness_score = max(0, completeness_score - 1)

        # Check noise
        relevant_count = sum(
            1 for r in retrieved[:3]
            if item["expected_source"] in r.metadata.get("source", "")
            or item["expected_section"].lower() in r.page_content.lower()
        )
        noise_score = min(2, relevant_count)

        total = source_score + completeness_score + noise_score
        results.append({
            "id": item["id"],
            "query": item["query"],
            "source_score": source_score,
            "completeness_score": completeness_score,
            "noise_score": noise_score,
            "total": total,
            "top1_source": sources[0] if sources else "none"
        })

    avg_total = sum(r["total"] for r in results) / len(results)
    top3_hit = sum(1 for r in results if r["source_score"] >= 1) / len(results)

    return {
        "per_query": results,
        "avg_score": round(avg_total, 2),
        "top3_hit_rate": round(top3_hit * 100, 1),
        "total_queries": len(results)
    }

# Usage
eval_results = evaluate_retrieval(retriever, benchmark_queries)
print(f"Average score   : {eval_results['avg_score']} / 6.0")
print(f"Top-3 hit rate  : {eval_results['top3_hit_rate']}%")
```

---

## Phase 3 — Diagnostics Map: Symptom → Root Cause → Fix

When your evaluation reveals problems, use this map to diagnose.

### Problem: Retrieved chunks are irrelevant to the query

**What it looks like in evaluation:**
- Noise score = 0 or 1 for multiple queries
- Wrong document family appears in top-3

**Root causes and fixes:**

*Cause A: No metadata filtering*  
A policy question retrieves technical runbook chunks because there is no doc_type filter at retrieval.  
**Fix:** Add `doc_type` metadata to all chunks. Apply filter at retrieval: `{"doc_type": "policy"}` for policy questions.

*Cause B: Chunks too large, embedding unfocused*  
A 1500-character chunk about three different topics produces a diffuse embedding that matches many queries weakly.  
**Fix:** Reduce chunk_size. The embedding of a smaller, focused chunk matches more precisely.

*Cause C: Boilerplate text polluting embeddings*  
Page headers, navigation text, or repeated footers in every chunk dilute the meaningful content.  
**Fix:** Add text cleaning before chunking. Remove repeated boilerplate patterns.

---

### Problem: Retrieved chunks are correct source but incomplete context

**What it looks like in evaluation:**
- Source score = 2 but completeness_score = 1 or 0
- Answer is generated but missing key conditions or steps

**Root causes and fixes:**

*Cause A: Exception clause in next chunk*  
Rule is in Chunk N, exception is in Chunk N+1. Rule is retrieved, exception is not.  
**Fix:** Increase `chunk_overlap` by 50–100 characters. Or use section-aware separators to keep rule + exception in one chunk.

*Cause B: Chunks too small for complete answer*  
A 200-character chunk has the right fact but no surrounding context.  
**Fix:** Increase `chunk_size` by 100–200. Or implement chunk expansion post-retrieval.

*Cause C: Multi-step procedure split mid-flow*  
Steps 1–3 in one chunk, steps 4–6 in another. Top-3 retrieves only one half.  
**Fix:** Use heading-first separators (`"\n## "`) so complete workflow sections stay in one chunk.

---

### Problem: Correct answer is in document but never retrieved

**What it looks like in evaluation:**
- Source score = 0 despite the answer definitely being in the indexed documents
- Increasing top_k to 20 still does not surface the expected chunk

**Root causes and fixes:**

*Cause A: The chunk text does not match how users phrase the query*  
Document says "Annual Leave Entitlement." User asks "How many vacation days do I get?"  
The embedding distance between "vacation days" and "annual leave" may be high for small models.  
**Fix:** Add semantic synonyms to chunk metadata. Or use a larger/better embedding model. Or implement hybrid search (keyword + semantic).

*Cause B: Query is ambiguous — embedding points to wrong topic*  
"How do I apply for this?" — "this" is ambiguous, the query embedding is diffuse.  
**Fix:** This is a retrieval architecture issue, not chunking. Use query rewriting or clarification before retrieval.

*Cause C: Text cleaning removed the answer*  
Overly aggressive cleaning removed important technical identifiers or section markers.  
**Fix:** Review cleaning pipeline. Only remove confirmed boilerplate, not domain-specific terminology.

---

### Problem: Duplicate or near-duplicate results in top-5

**What it looks like in evaluation:**
- Top-3 returns the same content worded slightly differently
- Noise score low despite chunks being "relevant"

**Root causes and fixes:**

*Cause A: Overlap too high — adjacent chunks share most content*  
With 50% overlap, chunks 1 and 2 share half their content and embed similarly.  
**Fix:** Reduce chunk_overlap. For most use cases, 15–20% overlap (not 50%) is correct.

*Cause B: Same document indexed multiple times*  
Document loaded twice under different file paths, or old and new versions both indexed.  
**Fix:** Implement deduplication by content hash before indexing. Remove old versions when new ones are added.

*Cause C: Boilerplate chunks* 
Repeated page headers or navigation text across many chunks. All match "Document Title" queries equally.  
**Fix:** Filter out chunks where the content length is below a minimum threshold (e.g., less than 50 characters). Remove boilerplate patterns in cleaning.

---

## Phase 4 — Metadata Completeness Check

Run this check on all chunks before indexing:

```python
def check_metadata_completeness(chunks: list, required_fields: list) -> dict:
    """
    Verify all required metadata fields are present in every chunk.
    """
    issues = []
    for i, chunk in enumerate(chunks):
        missing = [f for f in required_fields if f not in chunk.metadata or not chunk.metadata[f]]
        if missing:
            issues.append({
                "chunk_index": i,
                "source": chunk.metadata.get("source", "unknown"),
                "missing_fields": missing,
                "content_preview": chunk.page_content[:80]
            })

    return {
        "total_chunks": len(chunks),
        "chunks_with_issues": len(issues),
        "pass_rate": round((len(chunks) - len(issues)) / len(chunks) * 100, 1),
        "issues": issues[:10]   # show first 10 for review
    }

# Define required fields by document family
REQUIRED_FIELDS = {
    "functional": ["source", "doc_type", "section_title", "version", "effective_date", "owner_team"],
    "technical":  ["source", "doc_type", "service_name", "environment", "system_area"],
    "tabular":    ["source", "doc_type", "row_index"],
    "general":    ["source", "doc_type", "chunk_index"]
}

result = check_metadata_completeness(chunks, REQUIRED_FIELDS["functional"])
print(f"Metadata pass rate: {result['pass_rate']}%")
if result['issues']:
    print(f"Found {result['chunks_with_issues']} chunks with missing metadata:")
    for issue in result['issues'][:3]:
        print(f"  Chunk {issue['chunk_index']}: missing {issue['missing_fields']}")
```

**A metadata pass rate below 90% means your chunking pipeline has a systematic issue** — some document type is not receiving proper metadata enrichment. Fix before indexing.

---

## Phase 5 — Token Size Verification

Every chunk must stay within your embedding model's token limit. Run this before indexing:

```python
import tiktoken

def verify_token_limits(chunks: list, model_limit: int = 256) -> dict:
    """
    Check all chunks are within the embedding model's token limit.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    violations = []

    for i, chunk in enumerate(chunks):
        token_count = len(enc.encode(chunk.page_content))
        if token_count > model_limit:
            violations.append({
                "chunk_index": i,
                "token_count": token_count,
                "limit": model_limit,
                "overage": token_count - model_limit,
                "source": chunk.metadata.get("source", "unknown"),
                "preview": chunk.page_content[:100]
            })

    all_token_counts = [len(enc.encode(c.page_content)) for c in chunks]
    return {
        "total_chunks": len(chunks),
        "violations": len(violations),
        "max_tokens": max(all_token_counts),
        "avg_tokens": round(sum(all_token_counts) / len(all_token_counts), 1),
        "violation_examples": violations[:5]
    }

# all-MiniLM-L6-v2 limit = 256 tokens
result = verify_token_limits(chunks, model_limit=256)
print(f"Token verification: {result['violations']} violations out of {result['total_chunks']} chunks")
print(f"Max tokens: {result['max_tokens']} | Avg tokens: {result['avg_tokens']}")

if result['violations'] > 0:
    print("⚠️  Some chunks exceed model limit — reduce chunk_size or re-split")
```

---

## Phase 6 — Visual Spot Check Protocol

After automated checks pass, do a manual spot check on 5–10 random chunks per document family:

```python
import random

def spot_check_chunks(chunks: list, n: int = 5, seed: int = 42) -> None:
    """Print a sample of chunks for visual inspection."""
    random.seed(seed)
    sample = random.sample(chunks, min(n, len(chunks)))

    for i, chunk in enumerate(sample):
        print(f"\n{'='*60}")
        print(f"Sample {i+1} of {n}")
        print(f"{'='*60}")
        print(f"Source  : {chunk.metadata.get('source', 'unknown')}")
        print(f"Section : {chunk.metadata.get('section_title', 'unknown')}")
        print(f"Type    : {chunk.metadata.get('doc_type', 'unknown')}")
        print(f"Length  : {len(chunk.page_content)} chars")
        print(f"{'─'*60}")
        print(chunk.page_content)
        print()
```

**During spot check, ask:**
1. Does this chunk make sense when read in isolation?
2. If you received this chunk as context to answer a user query, could you give a complete answer?
3. Are there any dangling references ("this flag...", "as described above...")?
4. Is the metadata accurate — does the section_title match the actual content?

---

## The Acceptance Criteria

Chunking is accepted for indexing when ALL of the following are true:

| Criteria | Threshold | How to Measure |
|---|---|---|
| Top-3 hit rate | ≥ 70% | Benchmark evaluation |
| Average quality score | ≥ 4.0 / 6.0 | Benchmark evaluation |
| Completeness rate | ≥ 65% | Benchmark evaluation |
| Metadata completeness | ≥ 95% | `check_metadata_completeness()` |
| Token limit violations | 0 | `verify_token_limits()` |
| Spot check pass rate | 100% of sample | Visual inspection |

If any criterion fails, diagnose the cause, fix the relevant parameter or pipeline step, and re-run the full evaluation.

---

## Regression Testing — Protect Against Configuration Drift

When you update chunk parameters in the future:
- Save the current benchmark scores as your baseline
- Re-run the full evaluation after any parameter change
- Reject changes that decrease any criterion below threshold
- Accept changes only when they improve without degrading others

```python
def compare_runs(baseline: dict, new_run: dict) -> None:
    """Compare two evaluation runs and show deltas."""
    metrics = ["avg_score", "top3_hit_rate"]
    print("\n=== Evaluation Run Comparison ===")
    for m in metrics:
        b = baseline.get(m, 0)
        n = new_run.get(m, 0)
        delta = n - b
        symbol = "✅" if delta >= 0 else "❌"
        print(f"{m:25s}: {b:.2f} → {n:.2f}  ({delta:+.2f}) {symbol}")
```

This discipline prevents the "whack-a-mole" problem where fixing one query type breaks others — a common trap in RAG tuning without regression tracking.
