# 02 — Embedding Model Landscape and Selection

## Why Model Selection Is a System Decision

In RAG, "best model" is not absolute. The right choice depends on:

- corpus type (policy docs vs code vs multilingual content)
- query style (fact lookup vs conceptual questions)
- latency/cost budget
- deployment constraints (cloud API vs local/self-hosted)

Pick model + metric + index together, then validate with benchmark queries.

---

## Model Families

### 1) Hosted API Embedding Models

Best when you want strong quality quickly with low infra effort.

Use when:

- team wants fast iteration
- reliability/SLA from provider matters
- data governance allows external API usage

Trade-offs:

- ongoing API cost
- provider dependency
- compliance review may be needed

### 2) Open-Source Local Embedding Models

Best when cost control, privacy, and infrastructure ownership are priorities.

Use when:

- on-prem or VPC-only requirement
- large volume makes API cost high
- custom fine-tuning may be needed later

Trade-offs:

- infra ops burden (serving, scaling, monitoring)
- model updates and compatibility are your responsibility

### 3) Domain-Specific Models

Best for specialized language (legal, biomedical, security, code-heavy repos).

Use when:

- general models miss terminology
- retrieval failures are domain-wording related

Trade-off:

- sometimes narrower generalization outside target domain

---

## Selection Criteria (Practical Rubric)

Score each candidate from 1-5:

1. Retrieval quality on gold query set (highest weight)
2. Latency p95 for your real batch size
3. Cost per 1K chunks / monthly projection
4. Max input token support
5. Multilingual capability (if needed)
6. Integration simplicity (SDK, rate limits, retries)
7. Compliance/security fit

Do not choose only by benchmark leaderboards; choose by workload fitness.

---

## Model Dimension and Its Impact

- Lower dimensions reduce storage and search cost
- Higher dimensions can improve nuance but increase memory + compute
- Index dimension must match model dimension exactly

Example:

- 10M vectors at 1536 dimensions need much more memory than 384-dim vectors
- If quality gain from 1536 is small in your benchmark, 384/768 may be more efficient

---

## Example Selection Scenarios

### Scenario A: Internal Knowledge Base (English only)

- Corpus: architecture docs + runbooks
- Need: low latency, strong precision
- Recommended path: strong general text model, cosine/IP with normalized vectors, hybrid retrieval enabled

### Scenario B: High-volume Customer Support

- Corpus: FAQ + tickets + policies
- Need: cost-efficient scale
- Recommended path: evaluate smaller local models first, batch embedding pipeline, strict caching

### Scenario C: Code + Docs Assistant

- Corpus: Python/TS repos + markdown docs
- Need: symbol-aware retrieval
- Recommended path: compare general model vs code-aware model; route code queries separately if benchmark proves gain

### Scenario D: Multilingual Enterprise Search

- Corpus: English + Hindi + Spanish docs
- Need: cross-language retrieval
- Recommended path: multilingual model baseline, language-aware benchmark queries, language metadata filters

---

## Model Comparison Framework

For each model candidate, capture:

- `model_name`
- `provider`
- `embedding_dim`
- `max_input_tokens`
- `recommended_metric`
- `normalization_required` (yes/no)
- `avg_embed_latency_ms`
- `cost_estimate_per_1m_chunks`
- `Recall@5`, `Recall@10`, `MRR`, `nDCG`
- `notes_on_failures`

This table becomes your decision artifact.

---

## Common Selection Mistakes

1. Picking model by popularity, not benchmark results
2. Ignoring metric compatibility with vector store
3. Not testing long chunks for truncation behavior
4. Mixing model versions in one index
5. Changing preprocessing without re-evaluating model choice

---

## Baseline-to-Advanced Adoption Plan

### Phase 1: Baseline

- one model
- one index
- one evaluation set

### Phase 2: Controlled Comparison

- evaluate 2-3 models with same chunk set + same retrieval config
- compare metrics + cost + latency

### Phase 3: Specialized Routing (Optional)

- route query classes (code, multilingual, policy) to specialized models only if proven by benchmarks

---

## Final Decision Rule

Choose the model that gives:

- stable top-k quality on real queries
- acceptable p95 latency
- sustainable cost
- operational simplicity

The best embedding model is the one that wins *your* benchmark under *your* constraints.
