# Advanced Chunking Techniques — Deep Dive

> The techniques in this document are what separate a functioning RAG prototype from a production-grade RAG system. Recursive chunking gets you to 70% quality. The methods here address the remaining 30% — the cases where recursive splitting fails because the problem is not structure, it is meaning. Every technique is explained with the exact problem it solves, the mechanism that solves it, when to use it, and the real trade-offs involved.

---

## Why Advanced Techniques Exist

Recursive character splitting works well when:
- The document has clear structural boundaries (headings, paragraphs)
- Topics change at predictable text positions
- Every chunk needs the same granularity
- The document can be read linearly without cross-references

It fails when:
- Topics blend gradually with no heading boundaries (academic papers, legal documents)
- A chunk's meaning depends on context from a completely different section
- Users ask both strategic questions ("summarize the deployment process") and precision questions ("what flag do I use for rollback?")
- Pronouns or references in a chunk point to content that was in a different chunk

These failures require fundamentally different solutions — not tuning the same recursive splitter.

---

## Technique 1 — Semantic Chunking

### The problem it solves

Recursive chunking splits at structural positions: `\n\n`, `\n##`, `. `.

It has no concept of **topic continuity**. It will split mid-topic if a paragraph happens to end at the 500-character mark. It will join two completely different topics in one chunk if they both happen to start right after a section heading.

Semantic chunking solves this by detecting **where meaning actually changes** — not where the text structure happens to break.

### How it works — step by step

```
Step 1: Sentence Segmentation
   Break the document into individual sentences.
   "Kubernetes manages containers. It was developed by Google. Docker is a different tool."
   → ["Kubernetes manages containers.", "It was developed by Google.", "Docker is a different tool."]

Step 2: Embed Each Sentence
   Convert each sentence to a vector using an embedding model.
   sentence_1 → [0.23, -0.41, 0.87, ...]
   sentence_2 → [0.21, -0.39, 0.85, ...]   ← similar to sentence_1 (same topic)
   sentence_3 → [-0.15, 0.67, -0.22, ...]  ← different (topic shift to Docker)

Step 3: Compute Similarity Between Adjacent Sentences
   similarity(sentence_1, sentence_2) = 0.94  → same topic, no boundary
   similarity(sentence_2, sentence_3) = 0.31  → topic change detected

Step 4: Identify Breakpoints
   Where similarity drops below threshold → chunk boundary

Step 5: Group Into Chunks
   Sentences between breakpoints → one chunk
   Chunk 1: "Kubernetes manages containers. It was developed by Google."
   Chunk 2: "Docker is a different tool."
```

### Concrete example: where recursive fails, semantic wins

**Document text (no headings, mixed topics):**
```
Machine learning models require large amounts of training data to generalize well.
The quality of training data is often more important than model architecture choices.
Data augmentation techniques can increase effective dataset size without manual labeling.

Neural networks use gradient descent to minimize prediction error.
Backpropagation computes the gradient efficiently across all layers.
Learning rate scheduling improves convergence stability.

Kubernetes is a container orchestration platform originally developed by Google.
It manages the lifecycle of containerized applications across clusters.
Kubernetes uses a declarative configuration model based on YAML manifests.
```

**What recursive splitting gives you at 250 characters:**

```
Chunk 1: "Machine learning models require large amounts of training data to generalize well. The quality of training data is often more"

Chunk 2: "important than model architecture choices. Data augmentation techniques can increase effective dataset size without manual labeling."

Chunk 3: "Neural networks use gradient descent to minimize prediction error. Backpropagation computes the gradient efficiently across all layers. Learning rate"

Chunk 4: "scheduling improves convergence stability. Kubernetes is a container orchestration platform originally developed by Google."
```

**Chunk 4 is a problem.** It contains the end of the ML optimization section AND the beginning of the Kubernetes section. The embedding for Chunk 4 will represent a confusing mixture of concepts — gradient descent, convergence, and Kubernetes. No user query will reliably retrieve this chunk.

**What semantic chunking gives you:**

```
Chunk 1: 
"Machine learning models require large amounts of training data to generalize well.
The quality of training data is often more important than model architecture choices.
Data augmentation techniques can increase effective dataset size without manual labeling."
(Topic: ML training data)

Chunk 2:
"Neural networks use gradient descent to minimize prediction error.
Backpropagation computes the gradient efficiently across all layers.
Learning rate scheduling improves convergence stability."
(Topic: neural network optimization)

Chunk 3:
"Kubernetes is a container orchestration platform originally developed by Google.
It manages the lifecycle of containerized applications across clusters.
Kubernetes uses a declarative configuration model based on YAML manifests."
(Topic: Kubernetes)
```

Every chunk is semantically coherent. Each one retrieves precisely for the right query.

### Configuration

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

# Free, local — no API key required
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# percentile: split when similarity drops into the bottom X%
splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90  # bottom 10% of similarity scores = boundary
)

# standard_deviation: split when similarity drops more than X std devs below mean
splitter_stddev = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1.5   # 1.5 standard deviations below mean
)

chunks = splitter.split_documents(docs)
```

### Threshold type comparison

| Threshold Type | Behavior | Best For |
|---|---|---|
| `percentile` | Splits at the lowest X% of similarity scores | Consistent chunk count, works well generally |
| `standard_deviation` | Splits when similarity drops > X std deviations | Better for documents with clear topic structure |
| `interquartile` | Uses IQR to detect outlier similarity drops | Robust to noisy embeddings |
| `gradient` | Splits when the rate of similarity change spikes | Fast-changing academic or legal text |

### Real cost: semantic chunking is slow

Semantic chunking embeds every sentence in your document before splitting. For a 100-page PDF with ~2,000 sentences, that is 2,000 embedding API calls (or 2,000 local inference runs).

| Document Size | Recursive Time | Semantic Time (local) | Semantic Time (OpenAI API) |
|---|---|---|---|
| 10 pages | ~0.1 sec | ~8 sec | ~15 sec + API cost |
| 100 pages | ~0.5 sec | ~90 sec | ~3 min + API cost |
| 1,000 pages | ~3 sec | ~15 min | ~30 min + significant cost |

Use semantic chunking for documents where retrieval quality matters most: legal contracts, research papers, compliance documents. Use recursive for everything else.

---

## Technique 2 — LLM-Based Chunking and Contextual Retrieval

### The problem it solves

Both recursive and semantic chunking work bottom-up: they look at the text itself to decide where to split.

But some documents have meaning that only becomes clear when you understand the full document context. A sentence like "Revenue increased by 10%" is ambiguous without knowing: which company? which period? which revenue line?

LLM-based chunking works top-down: it uses the language model to understand the document holistically before making splitting decisions.

### Pattern A — Proposition-Based Chunking

The LLM reads sections of the document and extracts atomic, standalone factual propositions.

**Input section:**
```
Amazon Web Services (AWS) launched EKS (Elastic Kubernetes Service) in 2018.
EKS is a managed Kubernetes service that handles the control plane.
It supports both EC2 and Fargate compute options.
Fargate removes the need to manage EC2 instances directly.
```

**LLM output — propositions:**
```
1. AWS launched EKS in 2018.
2. EKS is a managed Kubernetes service.
3. EKS manages the Kubernetes control plane on behalf of users.
4. EKS supports EC2 compute instances.
5. EKS supports AWS Fargate compute.
6. AWS Fargate eliminates the need to manage EC2 instances directly.
```

Each proposition becomes a chunk. The result is extremely fine-grained, precisely queryable units of information.

**Query: "When did AWS launch EKS?"** → Proposition 1 retrieved directly. ✅  
**Query: "Does EKS support Fargate?"** → Propositions 5 and 6 retrieved directly. ✅  

```python
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def extract_propositions(text: str) -> list:
    prompt = f"""Break the following text into clear, atomic propositions.
Each proposition should be a complete, self-contained, standalone statement.
Do not combine multiple facts. Do not use pronouns — use full names.

Text:
{text}

Return one proposition per line. No numbering, no bullets."""

    response = llm.invoke(prompt)
    propositions = [line.strip() for line in response.content.split("\n") if line.strip()]
    return propositions

# Convert propositions to Documents
props = extract_propositions(section_text)
chunk_docs = [
    Document(page_content=prop, metadata={"source": "aws_guide.md", "doc_type": "proposition"})
    for prop in props
]
```

**Trade-off:** Each document section requires one LLM call. For 100 sections: 100 LLM calls. This is expensive and slow. Use it for high-value knowledge bases where retrieval precision justifies the cost.

---

### Pattern B — Anthropic Contextual Retrieval

This is the most impactful chunking improvement published in recent years (Anthropic, 2024). It addresses a fundamental limitation of all standard chunking approaches.

**The fundamental problem with all standard chunking:**

When you split a document into chunks and embed each chunk independently, **each chunk loses awareness of the broader document context.**

Example:
```
Document: A 40-page quarterly earnings report for Acme Corp, Q3 2024.

Page 12 contains:
"Revenue increased by 10% compared to the previous quarter."
```

After chunking and embedding, this chunk exists in the vector database as:

```
"Revenue increased by 10% compared to the previous quarter."
```

No company name. No time period. No revenue type. The embedding for this text is ambiguous — it could be from any company, any time, any report.

A user asks: "What was Acme Corp's revenue growth in Q3 2024?"

The retriever compares the query embedding to chunk embeddings. The chunk "Revenue increased by 10%..." might not even match strongly because the query specifies "Acme Corp" and "Q3 2024" which are not in the chunk.

❌ The correct information exists in the document but cannot be retrieved reliably.

**The Anthropic solution:**

Before embedding each chunk, prepend a **context sentence** that situates the chunk within the full document:

```python
import anthropic

client = anthropic.Anthropic()

def add_context_to_chunk(full_document: str, chunk: str) -> str:
    """
    Generate a context prefix for the chunk based on the full document.
    This context is prepended before embedding — not shown to the user.
    """
    prompt = f"""<document>
{full_document}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{chunk}
</chunk>

Provide a short (1-2 sentences) context for this chunk that identifies:
- What document this is from
- What topic/section this chunk covers
- Any key entities or time periods that provide disambiguation

Write only the context sentences. Nothing else."""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    context = response.content[0].text.strip()
    return f"{context}\n\n{chunk}"


# Before contextual retrieval — what gets embedded:
original_chunk = "Revenue increased by 10% compared to the previous quarter."

# After contextual retrieval — what gets embedded:
contextualized_chunk = """This chunk is from Acme Corp's Q3 2024 earnings report.
It describes the company's quarterly revenue performance metric.

Revenue increased by 10% compared to the previous quarter."""
```

Now when a user asks "What was Acme Corp's revenue growth in Q3 2024?", the query embedding aligns strongly with the contextualized chunk because it contains "Acme Corp", "Q3 2024", "earnings report", and "revenue growth." ✅

**Reported results (Anthropic, 2024):** 49% reduction in retrieval failures compared to standard RAG when using contextual retrieval.

**Cost optimization — prompt caching:**
The full document is sent once in the API call. With Anthropic's prompt caching, the document portion is cached and you only pay for each chunk's processing — not for re-reading the full document per chunk.

```python
def contextualize_all_chunks(full_document: str, chunks: list) -> list:
    """
    Add context to all chunks. The full_document is in the prompt prefix
    and benefits from prompt caching on repeated calls.
    """
    contextualized = []
    for chunk in chunks:
        new_content = add_context_to_chunk(full_document, chunk.page_content)
        chunk.page_content = new_content
        contextualized.append(chunk)
    return contextualized
```

---

## Technique 3 — Hierarchical Chunking

### The problem it solves

A single chunk size cannot serve two fundamentally different query types simultaneously:

- "Give me an overview of the Kubernetes deployment architecture" → needs a large, broad chunk (~2000 tokens)
- "What exact flag do I pass to kubectl for a rolling update?" → needs a tiny, precise chunk (~100 tokens)

If your chunks are large (2000 tokens), they answer broad questions well but the embeddings are too diffuse to retrieve precisely for specific queries.

If your chunks are small (100 tokens), they retrieve precisely for specific queries but lack context for broad questions.

Hierarchical chunking creates **all levels simultaneously** and retrieves at the appropriate level per query.

### The three-tier structure

```
Level 1 (Large — 2048 tokens):   Chapter or major section summary
    │
    ├── Level 2 (Medium — 512 tokens):   Section or subsection content
    │       │
    │       └── Level 3 (Small — 128 tokens):   Paragraph or detail level
```

Every chunk at Level 3 is linked to its parent at Level 2, which is linked to its parent at Level 1. This parent-child graph is stored in the document store.

### Two retrieval patterns

**Pattern A — Small-to-Big (most common)**

```
1. Retrieve matching Level 3 chunks (small, precise — high retrieval accuracy)
2. Look up each Level 3 chunk's parent (Level 2 chunk)
3. Return the Level 2 parent chunk to the LLM (full section context)
```

Result: precision of small-chunk retrieval + richness of medium-chunk context.

**Pattern B — Top-Down Drill**

```
1. Retrieve matching Level 1 chunks (broad topic match)
2. Within those, retrieve matching Level 2 chunks
3. Return Level 3 for final precise detail
```

Result: broad context alignment + precision for the specific detail.

### LlamaIndex implementation

```python
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore

# Step 1: Create hierarchical nodes from documents
node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]
)
nodes = node_parser.get_nodes_from_documents(documents)

# Step 2: Separate leaf (smallest) nodes from all nodes
leaf_nodes = [n for n in nodes if len(n.child_nodes or []) == 0]

# Step 3: Store all nodes in docstore (for parent lookup)
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)
storage_context = StorageContext.from_defaults(docstore=docstore)

# Step 4: Index only leaf nodes (small chunks = high precision retrieval)
index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)

# Step 5: AutoMergingRetriever — finds leaf matches, returns parent if enough match
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=12),
    storage_context=storage_context,
    verbose=True
)
```

**What AutoMerging does:**
- Retrieves top-12 small (128-token) chunks
- If 4 or more retrieved chunks share the same 512-token parent → return the parent instead
- If 3 or more 512-token parents share the same 2048-token grandparent → return the grandparent

This automatic promotion up the hierarchy means a broad query gets broad context, and a precise query gets precise detail — from the same index.

### When hierarchical clearly outperforms single-level

| Use Case | Why Hierarchical Wins |
|---|---|
| Textbook or manual (30+ chapters) | Chapter-level summary → section detail → paragraph precision |
| Legal document with cross-references | Article level → clause level → specific condition |
| Large codebase | Module → class → method |
| Enterprise knowledge base with mixed query types | Strategic → operational → reference queries from same index |

---

## Technique 4 — Late Chunking

### The problem it solves precisely

In standard chunking (pre-chunking):
```
Document → Split into chunks → Embed each chunk independently
```

Each chunk is embedded in isolation. It has zero knowledge of what came before or after. This creates specific failures for documents with:

**Forward references:**
```
Chunk 3: "The system uses the authentication protocol described in Section 7."
```
Section 7 is in Chunk 11. The embedding for Chunk 3 has no knowledge of Section 7's content. A query about "how does authentication work?" might retrieve Chunk 3 but the chunk is just a pointer — not the answer.

**Pronouns and co-references:**
```
Chunk 1: "Amazon Web Services launched EKS in 2018."
Chunk 2: "It supports both EC2 and Fargate compute."
```
"It" in Chunk 2 refers to "EKS" in Chunk 1. But Chunk 2 was embedded without knowing what "it" refers to. The embedding for Chunk 2 is "it supports both EC2 and Fargate" — ambiguous. A query about "does EKS support Fargate?" may not retrieve Chunk 2 because "EKS" does not appear in it.

### How late chunking works

```
Document → Embed the ENTIRE document first → Get per-token embeddings → Split later
```

The key insight is in how transformer-based embedding models work: the **attention mechanism** processes all tokens in the input together. Every token's embedding is influenced by every other token in the sequence.

When you embed the full document:
- "It" in sentence 5 attends to "EKS" in sentence 1
- "It"'s embedding vector reflects that it means "EKS"
- When you later average the token embeddings for Chunk 2, the "it" tokens already encode "EKS" meaning

The result: chunks that were split after embedding carry full-document context in their embeddings — even though the chunk text itself is still small and precise.

### Requirements

Late chunking requires a **long-context embedding model** that can fit the entire document in one forward pass:

| Model | Max Context | Notes |
|---|---|---|
| `jina-embeddings-v2-base-en` | 8192 tokens | Native late chunking support |
| `text-embedding-3-large` (OpenAI) | 8191 tokens | Adapts to late chunking approach |
| Standard `all-MiniLM-L6-v2` | 256 tokens | Too small for most documents |

Documents longer than the model's context window cannot use late chunking in a single pass. For longer documents, apply late chunking per section after a primary semantic or heading split.

---

## Technique 5 — Chunk Expansion (Post-Retrieval)

### What it is

This is not a chunking technique applied before indexing — it is applied **after retrieval**, before passing context to the LLM.

After the retriever returns precise small chunks, each retrieved chunk is expanded to include its neighboring chunks.

You retrieve small (precise) → expand to medium (rich context) → pass expanded to LLM.

### Why it matters

Small chunks have high retrieval precision. But the LLM generating an answer may need more than 1–2 sentences to produce a complete response.

Example:
```
Retrieved chunk (128 tokens):
"The rollback command is: kubectl rollout undo deployment/api-server"
```

The LLM needs to answer "how do I rollback?" but this chunk has only the command — no prerequisites, no verification steps.

Without expansion, the LLM answers: "Run: kubectl rollout undo deployment/api-server"  
This is incomplete and potentially dangerous. ⚠️

**With expansion (window = 1 chunk before and after):**
```
Expanded context (3 × 128 = ~384 tokens):
[Previous chunk]: "Before rolling back, verify that the database backup is confirmed healthy."
[Retrieved chunk]: "The rollback command is: kubectl rollout undo deployment/api-server"
[Next chunk]: "After rollback, verify pods are running: kubectl get pods -l app=api-server"
```

The LLM now has the complete context for a safe, complete answer. ✅

### Implementation

```python
def expand_chunks(
    all_chunks: list,
    retrieved_indices: list,
    window: int = 1
) -> list:
    """
    Expand retrieved chunks by including neighboring chunks.

    all_chunks      : The full ordered list of chunks from one document
    retrieved_indices: Indices of retrieved chunks (from retrieval metadata)
    window          : Number of chunks to include before and after each retrieved chunk
    """
    expanded = []
    seen = set()

    for idx in retrieved_indices:
        start = max(0, idx - window)
        end = min(len(all_chunks), idx + window + 1)

        for i in range(start, end):
            if i not in seen:
                expanded.append(all_chunks[i])
                seen.add(i)

    # Sort by original chunk order to preserve reading flow
    expanded.sort(key=lambda c: c.metadata.get("chunk_index", 0))
    return expanded

# Usage after retrieval
retrieved_chunks = retriever.get_relevant_documents(query)
retrieved_indices = [c.metadata["chunk_index"] for c in retrieved_chunks]

# Get the full ordered chunk list for the source document
source = retrieved_chunks[0].metadata["source"]
source_chunks = [c for c in all_indexed_chunks if c.metadata["source"] == source]

expanded_context = expand_chunks(source_chunks, retrieved_indices, window=1)
```

### When expansion is most valuable

- Retrieved chunks are short (100–200 tokens) and answers need 2–4x that amount
- Procedural documents where context flows across chunk boundaries
- Transcripts and conversations where one turn does not fully explain without context
- Any case where the LLM answer is consistently "incomplete" despite correct retrieval

---

## Technique 6 — Summary Chunks (Dual Representation)

### What it is

For each section of the document, create two representations:
1. A precise chunk (for high-accuracy retrieval)
2. A summary chunk (for high-quality LLM generation)

Store both. Use the precise chunk embedding for retrieval. Return the summary chunk content to the LLM.

### Why this helps

Dense technical or legal text often contains precise language that embeds well but reads poorly when passed directly to the LLM. A legal clause might be technically accurate but require a 500-token interpretation to understand.

By pairing each precise chunk with a summary:
- Retrieval uses the precise chunk → high accuracy
- Generation uses the summary → high quality, complete answers

### Implementation

```python
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def create_dual_representation(chunk: Document) -> tuple:
    """
    Returns (retrieval_doc, generation_doc) pair for one chunk.
    The retrieval doc is embedded. The generation doc is passed to LLM.
    """
    summary_prompt = f"""Summarize the following text into a complete, clear paragraph
that preserves all key facts, conditions, and named entities.

Text:
{chunk.page_content}

Write only the summary. No preamble."""

    summary = llm.invoke(summary_prompt).content.strip()

    # Retrieval doc: original precise text
    retrieval_doc = Document(
        page_content=chunk.page_content,
        metadata={**chunk.metadata, "representation": "precise"}
    )

    # Generation doc: summary (stored but linked)
    generation_doc = Document(
        page_content=summary,
        metadata={**chunk.metadata, "representation": "summary"}
    )

    return retrieval_doc, generation_doc

# Apply to all chunks
for chunk in chunks:
    retrieval_doc, generation_doc = create_dual_representation(chunk)
    # Store retrieval_doc in vector index
    # Store generation_doc in docstore, linked by chunk_id
```

---

## Choosing the Right Advanced Technique

| Situation | Recommended Technique |
|---|---|
| No headings, mixed topics blending gradually | Semantic Chunking |
| Chunks missing document context (company, date, entity) | Contextual Retrieval (Anthropic) |
| Users ask both strategic and detailed questions | Hierarchical Chunking |
| Pronouns / cross-references between chunks | Late Chunking |
| Precise retrieval but incomplete LLM answers | Chunk Expansion |
| Dense text that retrieves well but answers poorly | Summary Chunks |
| High-value documents where precision justifies cost | Proposition-Based (LLM) |

Most production systems combine 2–3 of these techniques:
- Contextual Retrieval + Recursive (most common, biggest bang for buck)
- Hierarchical + Semantic (complex document sets)
- Recursive + Chunk Expansion (pragmatic improvement with minimal cost)
