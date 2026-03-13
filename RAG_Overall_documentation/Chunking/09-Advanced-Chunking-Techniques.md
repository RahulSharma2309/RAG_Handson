# Advanced Chunking Techniques — Deep Dive

> This file goes deeper on the advanced methods. Once you have the basics, these are the techniques that separate good RAG systems from great ones.

---

## 1) Semantic Chunking — Deep Dive

### The problem it solves
Standard chunkers split by size or structure. They do not know what a "topic change" looks like.

Semantic chunking uses meaning to decide where boundaries belong.

### The algorithm step by step

**Step 1: Sentence segmentation**
Break the document into individual sentences.

**Step 2: Embed each sentence**
Convert each sentence to a vector.

**Step 3: Compute similarity between neighbours**
Compare sentence N with sentence N+1 using cosine similarity.

**Step 4: Detect breakpoints**
Where similarity drops significantly → topic change → chunk boundary.

**Step 5: Group into chunks**
Sentences between breakpoints form one chunk.

### Breakpoint threshold types (LangChain SemanticChunker)

| Type | Meaning |
|---|---|
| `percentile` | Split when similarity drops below the Xth percentile |
| `standard_deviation` | Split when similarity drops > X standard deviations below mean |
| `interquartile` | Use IQR range to identify outliers as breakpoints |
| `gradient` | Split when rate of similarity change spikes |

### Configuration example

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Using OpenAI (paid)
splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95  # top 5% of drops become boundaries
)

# Using HuggingFace (free)
splitter = SemanticChunker(
    embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1.5
)

chunks = splitter.split_documents(docs)
```

### Trade-offs

| Pros | Cons |
|---|---|
| Semantically coherent chunks | Slow — embeds every sentence twice |
| Topic changes define boundaries | Expensive if using paid embedding API |
| Works without document structure | Variable chunk sizes |
| Better retrieval for dense content | Results vary per domain |

### When it clearly outperforms Recursive

- Academic papers where sections do not use headings
- Legal text with long, flowing argument structures
- Narrative documents where topics blend gradually

---

## 2) LLM-Based Chunking and Contextual Retrieval — Deep Dive

### The problem it solves
Some documents are so complex that no rule — not even semantic similarity — captures the true meaning relationships.

An LLM understands language. Let the LLM decide the chunk boundaries.

### Pattern A: Proposition-based chunking

Feed the document to an LLM.  
Ask it to extract clear, atomic propositions — standalone factual statements.

```python
proposition_prompt = """
Break the following text into clear, atomic propositions.
Each proposition should be a complete, standalone statement.
Do not combine multiple facts into one proposition.

Text: {text}

Return each proposition on a new line.
"""
```

Each proposition becomes a chunk.  
Result: extremely precise, queryable units of information.

### Pattern B: Anthropic Contextual Retrieval (2024)

This is the most impactful LLM chunking innovation to date.

**The problem**: When you split a document into chunks and embed them, each chunk loses awareness of the broader document context.

Example:
- Chunk text: "Revenue increased by 10%"
- Without context: which company? which period? what caused it?
- The embedding for this chunk is ambiguous

**The Anthropic solution**: Prepend a context description to every chunk before embedding.

```python
import anthropic

client = anthropic.Anthropic()

def add_context_to_chunk(full_document: str, chunk: str) -> str:
    prompt = f"""
    <document>
    {full_document}
    </document>
    
    Here is the chunk we want to situate within the whole document:
    <chunk>
    {chunk}
    </chunk>
    
    Please give a short succinct context to situate this chunk 
    within the overall document for the purposes of improving 
    search retrieval of the chunk. Answer only with the succinct 
    context and nothing else.
    """
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    context = response.content[0].text
    return f"{context}\n\n{chunk}"  # Prepend context to chunk

# Apply to all chunks
contextualized_chunks = [
    add_context_to_chunk(full_document, chunk.page_content)
    for chunk in chunks
]
```

**Optimization**: Cache the document prompt across all chunk calls. This way the full document is only processed once per document (not once per chunk).

**Results reported by Anthropic**:
- 49% reduction in retrieval failures compared to standard RAG
- Works especially well for long technical and legal documents

### When to use LLM-based chunking

- High-value document sets (legal, medical, compliance)
- Documents where context is critical for interpretation
- Enterprise knowledge bases where retrieval quality directly impacts business outcomes
- When you can afford the cost and latency

---

## 3) Hierarchical Chunking — Deep Dive

### The problem it solves
A single chunk size cannot serve both:
- "Give me a summary of the deployment process" (needs broad context)
- "What exact flag do I use for the rollback command?" (needs granular precision)

Hierarchical chunking creates both simultaneously.

### How the index structure works

```
Level 1 (Large chunks — 2048 tokens): Chapter-level summaries
    └── Level 2 (Medium chunks — 512 tokens): Section-level content
             └── Level 3 (Small chunks — 128 tokens): Paragraph-level detail
```

### Two retrieval patterns

**Pattern A: Top-down drill**
1. Retrieve matching Level 1 chunks (broad topic match)
2. From those, retrieve matching Level 2 (section precision)
3. Return Level 3 for the final context

**Pattern B: Small-to-big**
1. Retrieve precise small chunks (high precision)
2. Expand to parent medium/large chunks for full context
3. Return the parent chunk to the LLM

LlamaIndex supports both patterns natively.

```python
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core import VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore

# Create hierarchical nodes
node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]
)
nodes = node_parser.get_nodes_from_documents(documents)

# Build index from leaf nodes (smallest)
leaf_nodes = [n for n in nodes if n.parent_node is not None]
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)

index = VectorStoreIndex(leaf_nodes)

# Auto-merging retriever: finds leaf nodes, returns parent if enough match
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=12),
    storage_context=index.storage_context,
    verbose=True
)
```

### When hierarchical clearly wins

- Textbooks and manuals (30+ chapters)
- Regulatory documents (many cross-referenced articles)
- Large codebases (file → class → method)
- Enterprise knowledge bases where users ask both strategic and operational questions

---

## 4) Late Chunking — Deep Dive

### The problem it solves (precisely)

In standard pre-chunking:
```
Document → Split first → Embed each chunk independently
```

Each chunk is embedded in isolation. It has no awareness of what came before or after.

This creates a serious problem for documents with:
- Pronouns: "It was introduced in 2019..." (what is "it"?)
- Cross-references: "As described in section 3..." (section 3 is a different chunk)
- Progressive arguments: each paragraph builds on the previous

### How late chunking works

```
Document → Embed ENTIRE document → Get token-level embeddings → Split later
```

The key insight: the embedding model's attention mechanism "reads" the entire document when computing each token's embedding.  
Each token's embedding already contains context from the whole document.

When you then split and average token embeddings per chunk:  
→ Each chunk embedding inherently reflects the full document context.

### Requirements

- Requires a **long-context embedding model** (to fit whole document)
- `jina-embeddings-v2-base-en` explicitly supports late chunking
- Other long-context models can also be adapted

### When late chunking matters most

- Research papers with forward/backward references
- Legal contracts where clause N references clause 3
- Technical documentation that assumes cumulative reading
- Financial reports with tables that reference narrative sections

---

## 5) Chunk Expansion (Post-Retrieval Technique)

### What it is

After retrieval, **expand each retrieved chunk** to include its neighboring chunks.

You retrieve precise chunks (small, focused) → but deliver broader context to the LLM.

### Why this matters

Small chunks → high precision retrieval  
But the LLM may need 2–3 paragraphs of context to generate a complete answer.

Chunk expansion gives you both:
1. Precise retrieval (small chunks)
2. Rich context for generation (expanded neighborhood)

### How to implement

```python
def expand_chunk(chunks: list, retrieved_idx: int, window: int = 1) -> str:
    """
    Expand a retrieved chunk by including neighboring chunks.
    window=1 means include 1 chunk before and after.
    """
    start = max(0, retrieved_idx - window)
    end = min(len(chunks), retrieved_idx + window + 1)
    
    expanded = chunks[start:end]
    return "\n\n".join([c.page_content for c in expanded])
```

### When to use

- Retrieved chunks are precise but too short for full answer
- When answers require transition context between ideas
- Transcripts and conversations where one exchange does not fully explain

---

## 6) Summary Chunks (Hybrid Pattern)

### What it is

Create **two representations** of the same content:
1. A small, precise chunk (for retrieval)
2. A larger summary chunk (for generation)

Store both. Retrieve by small chunk. Return summary to LLM.

### Pattern

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def create_summary_chunk(chunk_text: str) -> str:
    prompt = f"Summarize the following into a concise, complete paragraph:\n\n{chunk_text}"
    return llm.invoke(prompt).content

# Create both versions
for chunk in chunks:
    precise_chunk = chunk.page_content
    summary = create_summary_chunk(precise_chunk)
    
    # Store summary as the indexed version, precise as metadata
    chunk.metadata["precise_content"] = precise_chunk
    chunk.page_content = summary  # embed and index this
```

This is useful when your docs contain very dense or verbose content that needs simplification before embedding.
