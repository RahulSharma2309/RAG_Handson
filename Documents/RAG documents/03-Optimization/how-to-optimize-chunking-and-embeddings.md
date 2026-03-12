# How to Optimize Chunking and Embeddings

This guide explains practical optimization in plain language.

## 1) Chunking optimization

### What to tune

- chunk size
- chunk overlap
- split boundaries (headings vs paragraph vs sentence)
- profile mapping by doc family

### How to decide if chunking is good

Use real questions and inspect top-k retrieval:

- Are results relevant?
- Are citations from expected docs?
- Is answer context complete in single chunk?
- Are duplicates/noise too high?

### Common tuning patterns

- Too much noise:
  - decrease chunk size
  - reduce overlap
  - improve profile mapping

- Missing context:
  - increase chunk size
  - increase overlap a bit
  - keep heading + bullet context together

- Wrong domain results:
  - use metadata filters (`folder_profile`, `source_contains`)

## 2) Embedding optimization

### Free model options

- Fast baseline: `sentence-transformers/all-MiniLM-L6-v2`
- Better quality option: `BAAI/bge-small-en-v1.5`

### What to compare

- retrieval relevance on same query set
- latency
- memory footprint
- index size

### Suggested process

1. keep same chunks
2. build index with model A
3. run fixed benchmark queries
4. build index with model B
5. compare top-k relevance and speed

## 3) Retrieval optimization

- increase `pool-size` before applying metadata filters
- keep `top-k` reasonable (5 to 10 for experiments)
- use metadata filters for domain-specific tasks
- add reranking later if needed

## 4) Data quality optimization

- remove boilerplate sections from source docs if repetitive
- keep section headings in chunk text
- avoid mixing unrelated topics in same chunk
- fix broken markdown structure in source when possible

## 5) Practical optimization checklist

- [ ] Evaluate 20 representative questions
- [ ] Record hit quality at top-3 and top-5
- [ ] Tune one variable at a time
- [ ] Save run summaries for each experiment
- [ ] Keep best configuration as default profile settings
