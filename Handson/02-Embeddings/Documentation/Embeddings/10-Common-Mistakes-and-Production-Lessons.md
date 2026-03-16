# 10 — Common Mistakes and Production Lessons

## Why This Document Exists

Most embedding pipeline issues are not novel.  
The same mistakes recur across teams, companies, and projects.

This document captures them in full detail: what happened, why it's a problem, how to detect it, and how to fix it.

Reading this before building saves you weeks of debugging.

---

## Mistake 1: Choosing the Model Before Benchmarking

### What it looks like
Team picks `text-embedding-3-small` because it's popular, or picks a model from a leaderboard without running any evaluation on their own data.

### Why it's a problem
MTEB leaderboard scores are computed on standard benchmark datasets that may be completely different from your corpus and query distribution.

A model that ranks #1 on MTEB may rank #3 on your internal knowledge base.

### Real example
A team building a RAG system for Kubernetes operational docs chose a general-purpose model that ranked well on Wikipedia-style questions. Their corpus was dense technical runbooks with commands and identifiers. The model retrieved semantically similar but operationally wrong chunks consistently.

### How to detect
Run your gold query set. If Recall@5 < 0.70, the model is the first thing to investigate.

### How to fix
Build a gold query set from your corpus before selecting a model. Run at least 2 candidate models through the same evaluation. Choose by your metrics, not external rankings.

---

## Mistake 2: Silent Truncation Goes Undetected

### What it looks like
Large chunks (or code/JSON with high token density) silently get truncated by the embedding model. No error is raised. Embeddings are returned but represent only partial content.

### Why it's a problem
Retrieval for queries about tail content of the chunk will fail unpredictably — sometimes returning results, sometimes not. This looks like random retrieval behavior.

### How to detect
```python
chunks_at_risk = [
    c for c in all_chunks
    if c.metadata['token_count'] > operational_token_limit
]
print(f"Chunks at risk of truncation: {len(chunks_at_risk)}")
```

### How to fix
- Set `operational_limit = 0.80 * model_max_tokens`
- Validate every chunk before embedding
- Handle over-limit chunks: split, trim at sentence boundary, or reject + log

---

## Mistake 3: No Versioning for Model or Preprocessing

### What it looks like
Team updates their preprocessing logic (e.g. fixes PDF boilerplate removal) or upgrades the embedding model, but does not re-embed the affected documents. Old and new vectors now coexist in the index.

### Why it's a problem
Old vectors were computed with different preprocessing or different model weights. Vector space is inconsistent. Retrieval quality becomes unpredictable — some documents retrieve well, others poorly, with no clear pattern.

### How to detect
Ask: "If we changed preprocessing rules last month, what is the `preprocessing_version` of every chunk in our index?" If you cannot answer this, you have a versioning problem.

### How to fix
- Tag every chunk with `preprocessing_version` and `embedding_model`
- When either changes, identify affected chunks and re-embed them
- Use blue/green index pattern for major changes

---

## Mistake 4: Embedding Raw Noisy Text

### What it looks like
PDF chunks that still contain "Page 4 of 24 | CONFIDENTIAL | Document Title" at the top of every chunk. CSV chunks embedded as raw comma-separated strings. HTML tags embedded alongside content.

### Why it's a problem
The noise tokens dilute the semantic meaning of the vector.

A chunk about "JWT authentication rate limiting" that starts with three lines of boilerplate embeds a vector that partially represents the boilerplate. It will be retrieved by other boilerplate-heavy chunks, not by queries about JWT rate limiting.

### How to detect
Read 5-10 random chunks from your embedding input and ask: "Does every token in this text contribute to meaning?"

### How to fix
Apply preprocessing per document type before embedding. See doc 04 for the full preprocessing pipeline.

---

## Mistake 5: No Metadata on Chunks

### What it looks like
Vectors are stored with only the text and a numeric ID. No `source`, no `doc_type`, no `version`.

### Why it's a problem
1. Cannot filter queries by domain, version, or team
2. Cannot cite sources in answers
3. Cannot debug retrieval failures (you don't know which document the chunk came from)
4. Cannot do incremental updates (no way to identify which vectors belong to a changed document)

### How to detect
Query your index. Look at a returned chunk. Does it have `source`, `doc_type`, `version`, `chunk_id`?

### How to fix
Design metadata schema before chunking. Make it non-negotiable that every chunk carries required fields. Reject chunks without required metadata at ingestion.

---

## Mistake 6: Re-Embedding Everything on Every Run

### What it looks like
Every time a document is added or updated, the team re-embeds and re-indexes the entire corpus. Costs and time scale linearly with corpus size.

### Why it's a problem
At 50K chunks this is manageable. At 2M chunks, a full re-embed might take hours and cost significant money — especially if done daily.

### How to detect
If your embedding pipeline has no concept of "has this chunk already been embedded?", you are re-embedding everything every time.

### How to fix
- Implement change detection (file hash, modification timestamp)
- Track embedded chunk IDs in a persistent cache
- Only embed chunks for new or changed documents
- Checkpoint progress so runs are resumable

---

## Mistake 7: Using Character Count as Token Proxy

### What it looks like
Team uses `len(text) / 4` as a "token estimate" and assumes it's safe.

### Why it's a problem
Dense content types (code, JSON, SQL, URLs) have 2-3 characters per token, not 4-5.

A 2000-character JSON chunk at 2 chars/token = 1000 tokens — double what the proxy estimated.

### How to detect
Run actual tokenizer counts on 100 random chunks from each content type. Compare to character-based estimate. If delta > 20%, your proxy is dangerous.

### How to fix
Use the actual tokenizer for your embedding model. Never use character count as a substitute in production pipelines.

---

## Mistake 8: One Global Strategy for All Content Types

### What it looks like
Same chunk_size, same preprocessing, same embedding profile for policy docs, technical runbooks, CSV records, and PDF reports.

### Why it's a problem
Each content type has different structure, token density, query patterns, and semantic boundaries. A chunk_size of 500 characters is too small for policy docs but too large for CSV row embeddings.

### How to detect
Run your gold query set per content type separately. If one content type has significantly lower Recall@k, your strategy is not suited to it.

### How to fix
Define separate chunk profiles per content type. Apply type-specific preprocessing. Validate each type independently. See doc 05 for per-type strategies.

---

## Mistake 9: No Smoke Tests After Index Build

### What it looks like
After building or updating the index, team immediately promotes to production without testing.

### Why it's a problem
Chunking bugs, embedding failures, or metadata issues can result in an empty or broken index that does not fail loudly.

A missing import, a silent API error, or a dimension mismatch can produce an index with fewer vectors than expected or completely wrong content.

### How to detect
Check vector count after build. Run 3-5 known queries and verify expected chunks are returned.

### How to fix
Always run smoke tests as the last step of any index build or update pipeline. Block promotion if smoke tests fail.

---

## Mistake 10: Evaluating by Cosine Score Alone

### What it looks like
Team prints top-k cosine similarities for a few queries, sees scores > 0.8, and declares retrieval "good."

### Why it's a problem
Cosine similarity between any two chunks of similar-length text in the same domain tends to be high. A score of 0.82 does not mean the chunk is the right answer.

### How to detect
Run the gold query set evaluation. If Recall@5 is low despite high similarity scores, similarity score is not a reliable quality indicator for your corpus.

### How to fix
Always evaluate with Recall@k and MRR on a gold query set with known correct answers. Similarity score is a ranking signal, not a quality guarantee.

---

## Mistake 11: Using a Single Embedding Model for Code + Prose + Multilingual

### What it looks like
One general-purpose English embedding model handles all queries, including code search and non-English content.

### Why it's a problem
General-purpose models are not optimized for:
- code symbol retrieval (function names, variable names, syntax patterns)
- cross-language retrieval

### How to detect
Include code-specific and multilingual queries in your gold query set. If those fail at high rates, the model is not suited for those query types.

### How to fix
Benchmark code-aware and multilingual models for those specific query types. Route specialist queries to specialist models if the benchmark justifies it. See doc 11 for detailed guidance.

---

## Mistake 12: Ignoring the Compound Effect

### What it looks like
Each individual mistake seems minor. Teams fix one issue at a time, each time improving slightly.

### Why it's a problem
Mistakes compound. Noisy text + no metadata + wrong model + no evaluation together produce a retrieval system that is confidently wrong — and you have no way to know which fix to apply first.

### How to fix
Before optimising, run a full baseline evaluation. Categorise failure modes. Fix in order of highest impact on Recall@k. Re-evaluate after each fix.

---

## Production Lessons Summary

| Lesson | Implication |
|---|---|
| Evaluate before choosing | No model selection without your benchmark |
| Track token counts | Silent truncation is the most invisible quality killer |
| Version everything | Model + preprocessing + index version = reproducibility |
| Clean before embedding | Noise in = noise vectors |
| Metadata is required infrastructure | Not optional, not afterthought |
| Change detection saves money | Incremental > full re-embed |
| Test after every index change | Smoke tests + benchmark regression |
| One strategy per content type | Not one strategy for all |
| Similarity score ≠ quality | Recall@k + MRR on gold queries = quality |

---

*Part of Handson Phase 2: Embeddings | March 2026*
