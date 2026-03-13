# Chunk Quality Checklist and Evaluation

Chunking is done only when retrieval quality is validated.

This file gives a measurable evaluation framework.

---

## 1) Evaluation principle

Do not judge chunking by chunk count.  
Judge it by question-answer retrieval performance.

---

## 2) Build a benchmark query set

Create 20-40 representative questions from real use cases:
- lookup questions (specific fact)
- policy questions (rule + exception)
- procedural questions (steps)
- comparative questions (A vs B)
- troubleshooting questions

Label expected source docs/sections.

---

## 3) Retrieval quality checks (top-k)

For each query, inspect top-3 and top-5:

- relevance: are chunks on-topic?
- completeness: does retrieved context contain enough info?
- citation quality: from expected source?
- duplication: too many near-duplicates?
- noise: unrelated boilerplate chunks present?

---

## 4) Scoring template

Use simple scoring (0-2):

- 0 = bad
- 1 = partial
- 2 = good

Metrics:
- `top3_relevance`
- `top3_completeness`
- `top5_noise_control`
- `citation_correctness`

Track average score before/after tuning.

---

## 5) Chunking diagnostics map

If issue = mostly irrelevant chunks:
- decrease chunk size
- improve semantic splitting
- reduce overlap if too high

If issue = incomplete answers:
- increase chunk size a bit
- increase overlap
- preserve heading + detail together

If issue = wrong document family retrieved:
- use metadata filters (`doc_type`, `folder_profile`, `service_name`)

If issue = repetitive results:
- reduce overlap
- deduplicate near-identical boilerplate chunks

---

## 6) High-value metadata checks

Verify every chunk has:
- source file
- section title
- document family/profile
- chunk index
- token or char count

For business docs add:
- version/effective date

For technical docs add:
- service/environment/system_area

---

## 7) Regression discipline

When changing chunk config:
- change one variable at a time
- run same benchmark set
- compare score deltas
- keep run summary artifacts

This prevents random tuning.

---

## 8) Final acceptance criteria

Chunk strategy is accepted when:
- top-3 retrieval is consistently relevant
- critical questions get complete context
- citations are traceable
- noise is controlled
- behavior is stable across doc families

