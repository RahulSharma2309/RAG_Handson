# 01 — Embedding Science and Foundations

## What an Embedding Is

An embedding is a dense numeric vector representing meaning.  
Two texts with similar meaning should map to nearby vectors in embedding space.

## Why Embeddings Matter in RAG

RAG retrieval quality depends on:

`document quality -> chunk quality -> embedding quality -> retrieval quality -> answer quality`

If embeddings are weak, nearest-neighbor search returns irrelevant chunks.

## Core Concepts

- **Vector dimension**: length of the embedding vector (for example 384, 768, 1536)
- **Similarity metric**: cosine, dot-product, or L2 distance
- **Semantic proximity**: closeness in vector space approximates meaning similarity
- **Context length**: max tokens that the model can embed per input

## Similarity Metrics (Practical)

- **Cosine similarity**: most common default for normalized vectors
- **Dot product**: useful when models/stores are tuned for it
- **Euclidean (L2)**: less common for text retrieval but still supported

Use the metric recommended by your vector store + model combination.

## Embedding Failure Modes

- Same topic, different wording not matched
- Boilerplate dominates vectors
- Overly long chunks get truncated before embedding
- Language/domain mismatch between model and corpus

## Practical Foundation Rule

Start simple, then evaluate:

- clean text
- consistent chunk profile
- one strong baseline embedding model
- benchmark on real questions before scaling
