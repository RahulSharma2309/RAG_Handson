# 03 — Tokenization and the Chunk-to-Embedding Interface

## Why This Document Exists

Most embedding pipeline failures are not model quality problems.  
They are token budget problems. Silent truncation. Wrong tokenizer. Overflow at query time.

This layer — between your chunk text and the embedding model — is where retrieval quality gets damaged invisibly.

Understanding it saves you hours of debugging and prevents silent degradation in production.

---

## What Is a Token?

A token is the basic unit of input that an embedding model sees.  
It is not a word. It is not a character. It is a piece of text determined by the model's tokenizer.

Tokenizers break text into subword units using algorithms like:

- **BPE (Byte Pair Encoding)**: starts with characters, merges common pairs iteratively. Used by OpenAI (tiktoken).
- **WordPiece**: similar to BPE, used by BERT-family models.
- **SentencePiece**: unigram model, handles multilingual text well. Used by many SentenceTransformers.

Because different models use different tokenizers, the same sentence produces different token counts with different tokenizers.

---

## The Real Problem: Same Text, Different Token Counts

Take this sentence:

```
Kubernetes is an open-source container orchestration system for automating deployment.
```

- OpenAI `text-embedding-3-small` tokenizer: approximately 12 tokens
- BERT tokenizer: approximately 14 tokens
- SentencePiece multilingual: approximately 16 tokens

This alone is harmless. But now consider:

- a chunk of 2000 characters of dense technical prose
- another 2000-character chunk of JSON/code with identifiers and brackets

The JSON/code chunk can be 40-60% more tokens for the same character count.

This is why **character count is a dangerous proxy for token count**, especially for:

- code and configuration files
- JSON, YAML, TOML payloads
- URL-heavy text
- text with many punctuation marks and symbols

---

## How Token Limits Work in Embedding Models

Every embedding model has a maximum input token limit.

What happens when input exceeds this limit varies by implementation:

### Behavior 1: Silent Truncation (most dangerous)
The model simply cuts the text at the token limit and embeds only the first N tokens.  
The tail of your chunk — often the most specific, action-oriented content — disappears.  
No error is raised. The embedding is returned. You never know.

### Behavior 2: Explicit Error / Exception
The API or library raises an error: "input too long."  
This is actually better than silent truncation — at least you know.

### Behavior 3: Automatic Chunking by Provider
Some managed APIs will split inputs internally.  
Dangerous because you cannot control the split and the resulting vector may represent a meaningless segment.

**Default assumption**: treat every model as a silent truncator unless documentation explicitly states otherwise.

---

## What Silent Truncation Looks Like in Retrieval

Imagine your chunk is:

```
## Kubernetes Deployment Requirements

Before deploying, ensure:
- AWS CLI 2.x installed
- kubectl 1.27+ configured
- IAM role with EKS:CreateCluster permission
- VPC with 2 subnets in different AZs

If any prerequisite is missing, deployment will fail at IAM validation.
```

If truncated at token limit, the model might only embed:

```
## Kubernetes Deployment Requirements

Before deploying, ensure:
- AWS CLI 2.x installed
- kubectl 1.27+ configured
```

Now query: "What happens if a prerequisite is missing?"  
The answer (IAM validation failure) was in the truncated tail.  
The chunk retrieves sometimes, fails sometimes. Looks random.

---

## The Tokenizer Mismatch Trap

A very common mistake:

1. You count tokens with `tiktoken` (OpenAI's tokenizer)
2. You embed with `sentence-transformers/all-MiniLM-L6-v2`
3. `all-MiniLM-L6-v2` uses its own tokenizer — different from tiktoken

The tiktoken count might say 480 tokens (safe under 512 limit).  
The SentenceTransformer tokenizer counts 530 tokens. Truncated silently.

**Rule**: Always count tokens using the tokenizer of the actual model you are embedding with.

---

## Practical Input Budget Policy

Never use the model's max token limit as your operational target.

| Model Max Tokens | Recommended Operational Limit | Safety Margin |
|---|---|---|
| 512 | 400–450 | ~12-20% |
| 4096 | 3000–3500 | ~15-25% |
| 8192 | 6000–7000 | ~15-25% |
| 32768 | 24000–28000 | ~15-25% |

Why keep a margin:

- Tokenizer counts in chunking vs embedding can differ slightly
- Metadata-enriched queries can push prompt+context over limit
- Safety against model version updates that change tokenization

### The Coupling With Chunking Phase

Your `chunk_size` in chunking is set in characters (LangChain default).  
Your `max_input_tokens` in embedding is in tokens.

These are different units. Your chunking setup must be calibrated so that character-based chunk sizes map safely to token counts under your operational limit.

Typical calibration:

- 1 token ≈ 3-5 characters for English prose
- 1 token ≈ 1-3 characters for code/JSON/URLs

Example:  
A `chunk_size=1500` characters for English prose → roughly 300-500 tokens. Safe under 512.  
The same `chunk_size=1500` for dense JSON → potentially 750-1000 tokens. Dangerous under 512.

---

## Content Types and Their Token Density (Practical Reference)

| Content Type | Chars per Token (Approximate) | Risk Level |
|---|---|---|
| Clean English prose | 4–5 | Low |
| Technical documentation | 3–4 | Medium |
| Markdown with headings | 3–5 | Medium |
| Code (Python, JS, TS) | 2–3 | High |
| JSON / YAML / TOML | 1.5–2.5 | Very High |
| SQL queries | 2–3 | High |
| URLs and paths | 1–2 | Very High |
| Log lines | 2–3 | High |

For high-density content types, reduce chunk_size significantly or set separate chunking profiles.

---

## What Good Metadata Looks Like After Token Validation

Before embedding, each chunk should carry:

```json
{
  "chunk_id": "ml_3f7a91bc22d1",
  "source": "Documents/ML-Notes/02-confusion-matrix.md",
  "char_count": 847,
  "token_count": 193,
  "chunk_index": 4,
  "chunk_profile": "ml_notes",
  "doc_type": "educational_notes",
  "truncation_risk": false,
  "model_token_limit": 512,
  "operational_limit": 450
}
```

`truncation_risk: false` means token_count < operational_limit.  
Anything flagged `true` should be reviewed before embedding.

---

## Token Overflow Handling Strategies

When a chunk exceeds the operational limit:

### Strategy 1: Hard Reject
Reject and log to failure manifest. Do not embed.  
Use when: you cannot afford wrong embeddings (compliance, legal).

### Strategy 2: Truncate at Sentence Boundary
Trim from the tail at the nearest sentence boundary to stay under limit.  
Use when: content is linear prose where tail is lower-priority context.

### Strategy 3: Sub-chunk the Overflow
Split the long chunk into smaller sub-chunks and embed each.  
Use when: all content is equally important and must be preserved.

### Strategy 4: Summarize Before Embedding
Use a lightweight LLM to summarize the chunk to a safe length, then embed.  
Use when: precision is critical and content is dense.

Most practical default: **Strategy 2 or 3 depending on content type**.

---

## Checking Token Limits in Practice

A simple token validation utility for your pipeline:

```python
import tiktoken

def count_tokens_for_openai(text: str, model: str = "text-embedding-3-small") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def check_token_budget(chunks, model_limit=8191, operational_limit=7000):
    at_risk = []
    for c in chunks:
        n = count_tokens_for_openai(c.page_content)
        c.metadata["token_count"] = n
        c.metadata["truncation_risk"] = n > operational_limit
        if n > operational_limit:
            at_risk.append(c.metadata.get("source", "?"))
    return at_risk
```

For SentenceTransformers models, use the model's own tokenizer:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def count_tokens_for_st(text: str, st_model) -> int:
    tokens = st_model.tokenizer.tokenize(text)
    return len(tokens)
```

---

## The Chunk Overlap and Token Budget Interaction

Overlap in chunking increases token counts for edge chunks.

Example:

- chunk_size = 800 chars, overlap = 200 chars
- overlap content = repeated from previous chunk
- actual unique content per chunk = 600 chars
- token count: full 800 chars get tokenized, not just 600

For tight token budgets, calculate effective token budget as:

`operational_limit >= tokens(chunk_size) + tokens(overlap)`

Not just `tokens(chunk_size)`.

---

## Common Questions

### Q: Does longer context window always mean better embedding quality?

No. Longer context window means less truncation risk. Whether the model uses the full context effectively depends on model architecture. Some models embed early tokens with stronger weight.

### Q: What if my chunks are consistently under 100 tokens?

Very short chunks may produce vectors that are too specific. They may fail on slightly rephrased queries. Consider increasing chunk_size for sparse documents, or checking if preprocessing is over-aggressively cleaning content.

### Q: Should I strip metadata from chunk text before embedding?

Yes. Metadata fields like `source`, `doc_type`, and `chunk_id` belong in the metadata dictionary, not in the text you embed. Embedding metadata fields wastes token budget and pollutes the semantic vector.

---

## Quick Checklist Before Embedding

- Are you using the tokenizer that matches your embedding model?
- Is every chunk under your operational token limit (not max limit)?
- Did you account for overlap tokens in your budget?
- Is `token_count` stored in each chunk's metadata?
- Are over-limit chunks flagged and handled by a defined strategy?
- Does your chunking profile use lower `chunk_size` for high-density content types?

If any answer is "no" — fix it before running embedding at scale.

---

*Part of Handson Phase 2: Embeddings | March 2026*
