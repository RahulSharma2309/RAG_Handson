# RAG Hands-on Roadmap (What is Done, What is Next)

This roadmap explains your RAG journey in sequence with "why" and "how".

## Phase 1 - Knowledge Corpus Preparation (Done)

### What was done

- Identified and organized markdown documents as the knowledge source
- Understood the different types of documents present:
  - product/PO-level docs
  - technical architecture docs
  - CI/CD and operations docs
  - learning guides
- Mapped document types to expected query patterns

### Why it was done

- In any RAG system the quality of input docs is the starting point
- Knowing document types upfront allows better chunking strategy
- Real systems have mixed knowledge domains, not just one type

### Tools used

- Markdown as the knowledge format
- Manual classification into document families

## Phase 2 - Chunking Pipeline (Done)

### What was done

- Designed a profile-based chunking strategy (not a single global setting)
- Mapped document types to chunking profiles with different token sizes and overlaps
- Split docs by markdown headings first, then by paragraphs
- Attached metadata to every chunk (source file, section title, doc family, token count)
- Generated JSONL outputs — one file per source markdown file

### Why it was done

- chunk quality and metadata quality drive retrieval quality
- profile-based strategy is closer to real enterprise setups

### Tools used

- Python
- regex/markdown parsing
- JSONL artifact format

## Phase 3 - Embedding and Vector Index (Done)

### What was done

- Understood what an embedding is: converting text into a vector (list of numbers that represent meaning)
- Chose a free local model: `sentence-transformers/all-MiniLM-L6-v2`
- Converted all 979 chunk texts into 384-dimensional vectors
- Built a FAISS flat inner-product index for cosine similarity search
- Saved raw embeddings, FAISS index, and metadata as separate files

### Why it was done

- semantic search needs vector representation
- local model keeps cost near zero for learning

### Tools used

- SentenceTransformers
- FAISS
- NumPy

## Phase 4 - Semantic Retrieval (Done)

### What was done

- Understood how semantic search works: query is embedded and nearest chunks found by vector similarity
- Built top-k retrieval from FAISS index
- Validated real queries returning relevant chunks from correct doc families
- Added `--list-profiles` for discoverability

### Why it was done

- raw retrieval is not enough in mixed corpora
- filters improve relevance and control

### Tools used

- FAISS query
- metadata filter logic

## Phase 5 - Metadata-Filtered Retrieval (Done)

### What was done

- Extended semantic search to support metadata filters on top of vector similarity
- Filters include:
  - `folder_profile` (document family)
  - `source_file` (specific file path substring)
  - `section_title` (topic keyword)
- Introduced candidate pool (retrieve wider, then filter down)

### Why it was done

- A single mixed corpus returns noisy results without domain context
- Metadata filters act like search facets (like "filter by category" in e-commerce)
- Useful for enterprise RAG where you want controlled domain-specific answers

### Tools used

- FAISS candidate pool + Python post-filter
- Metadata stored separately in `metadata.jsonl`

## Phase 6 - Evaluation Layer (Next)

### What should be done

1. Create benchmark query set (20-50 questions)
2. Define relevance scoring rubric
3. Compare chunking profiles and embedding models

### Why this should be done

- optimization without measurement is guesswork

### Tools to use

- simple CSV/JSON benchmark set
- script to run batch queries and save metrics

## Phase 7 - RAG Answer Generation (Next)

### What should be done

1. Add retriever -> context packer -> answer generation flow
2. Add source citation in final answer
3. Add confidence heuristics (basic)

### Why this should be done

- retrieval alone is only half of RAG
- answer quality and trust need citations

### Tools to use

- LangChain (optional)
- Open-source/local LLM or paid API later

## Phase 8 - Production-like Hardening (Later)

### What should be done

- caching
- failure handling
- prompt versioning
- index refresh pipeline
- monitoring logs for retrieval quality

### Why this should be done

- this is what differentiates prototype from robust system

## Suggested execution order from now

1. Build evaluation benchmark
2. Compare MiniLM vs BGE-small
3. Tune chunk profiles using benchmark data
4. Add answer generation with citations
5. Add simple UI/API for querying
6. Add refresh + observability
