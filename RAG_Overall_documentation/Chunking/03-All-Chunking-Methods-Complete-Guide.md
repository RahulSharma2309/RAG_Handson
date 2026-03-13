# All Chunking Methods — Complete Guide

> This is the complete reference for every chunking method that exists today. Read this to understand what every strategy is, how it works, when to use it, and what its trade-offs are.

---

## Quick Comparison Table

| Method | Complexity | Best For | Latency | Cost |
|---|---|---|---|---|
| Fixed-size | Low | Quick baseline, simple docs | Very Fast | Free |
| Recursive | Medium | Unstructured text, articles | Fast | Free |
| Document-based | Low–Medium | Structured docs (Markdown, HTML, PDF) | Fast | Free |
| Sliding Window | Low | Transcripts, conversations | Fast | Free |
| Semantic | Medium–High | Academic papers, dense narratives | Medium | Free–Paid |
| LLM-based | High | Legal, medical, complex reports | Slow | Paid |
| Agentic | Very High | Complex docs needing custom strategies | Very Slow | High |
| Late | High | Docs with cross-references | Medium–High | Free–Paid |
| Hierarchical | Medium | Books, manuals, large contracts | Medium | Free |
| Adaptive | High | Mixed-structure datasets | Variable | Variable |
| Code | Medium | Source code, scripts | Fast | Free |

---

## Method 1: Fixed-Size Chunking

### What it is
Split text into chunks of a predetermined size — measured in tokens or characters — regardless of the content structure.

### How it works
```
Document text: [word1 word2 word3 ... word5000]
chunk_size = 500, overlap = 50

Chunk 1: word1 → word500
Chunk 2: word451 → word950   (50 word overlap)
Chunk 3: word901 → word1400
...
```

### Code example
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_text(text)
```

### Pros
- Simplest to implement
- Fast and predictable
- Easy to reproduce and compare
- Good as a baseline

### Cons
- Ignores document structure
- Can split mid-sentence or mid-thought
- Overlap helps but does not fully solve context loss

### When to use
- Quick prototyping and first RAG experiments
- Documents without a consistent structure
- When you need a fast, reproducible baseline
- Short docs like meeting notes, emails, product descriptions

### Rule of thumb
Always use 10–20% overlap when using fixed chunking.

---

## Method 2: Recursive Chunking

### What it is
Split text using a **prioritized list of separators** applied in order.  
The splitter tries the highest-priority separator first. If the resulting chunk is still too large, it recurses down to the next separator.

### How it works
Default separator order:
```
["\n\n", "\n", ". ", " ", ""]
```

1. Try splitting by `\n\n` (paragraphs)
2. If still too large → split by `\n` (lines)
3. If still too large → split by `.` (sentences)
4. If still too large → split by space (words)
5. Last resort → split by character

### Code example
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(docs)
```

### Pros
- Respects natural text structure
- Adapts to the document
- Avoids brutal mid-sentence splits
- Great default for most use cases

### Cons
- Slightly more complex than fixed
- Still not aware of semantic meaning

### When to use
- **Best default choice for 80% of use cases**
- Research articles, blog posts, process documents
- Anything that is unstructured narrative text

---

## Method 3: Document-Based / Structure-Based Chunking

### What it is
Use the document's own **format and structural markers** as chunk boundaries.

### How it works by format

#### Markdown
Split by headings: `#`, `##`, `###`  
Each heading becomes the start of a new chunk.

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(markdown_text)
```

#### HTML
Split by tags: `<p>`, `<div>`, `<section>`, `<article>`

```python
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
]
splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(html_text)
```

#### Code
Split by logical units: functions, classes, modules

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=0
)
chunks = splitter.split_text(python_code)
```

### Pros
- Chunks align with logical document structure
- Heading context stays with its content
- Very good for documentation, code, and web content

### Cons
- Requires documents to have consistent formatting
- Poor formatting leads to poor chunks

### When to use
- Markdown knowledge bases
- HTML scraped content
- Technical documentation
- Source code
- Any document with clear structural markers

---

## Method 4: Sliding Window Chunking

### What it is
Fixed-size chunks with significant overlap — window slides across the text.

### How it works
```
chunk_size = 200, overlap = 100

Chunk 1: tokens 0–200
Chunk 2: tokens 100–300
Chunk 3: tokens 200–400
Chunk 4: tokens 300–500
```

Each chunk shares a large portion with its neighbors.

### Pros
- Preserves context continuity
- No information loss at boundaries

### Cons
- High redundancy — same content in multiple chunks
- Larger index size
- More embedding cost

### When to use
- Transcripts (video, meeting, podcast)
- Chat logs and conversation threads
- Continuous narrative text
- Any content where context flows from sentence to sentence

---

## Method 5: Semantic Chunking

### What it is
Split text at **meaning change boundaries** rather than by size or structure.  
Uses embeddings to detect where topics shift.

### How it works
1. Break text into individual sentences
2. Embed each sentence (convert to vector)
3. Compare consecutive sentence vectors using cosine similarity
4. Identify where similarity drops significantly = topic change = chunk boundary
5. Group sentences between boundaries into chunks

```python
# Using LangChain's SemanticChunker (requires OpenAI embeddings)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
chunks = splitter.split_documents(docs)
```

### Example
Document sections:
- Section 1: Kubernetes architecture
- Section 2: Docker containers  
- Section 3: CI/CD pipeline

Semantic chunker detects meaning shifts and creates:
- Chunk 1 → Kubernetes content only
- Chunk 2 → Docker content only
- Chunk 3 → CI/CD content only

Not random character limits — actual topic changes.

### Pros
- Most semantically coherent chunks
- Does not require structured formatting
- Captures meaning rather than structure

### Cons
- Requires embedding model at chunking time (slow and costly)
- Variable chunk sizes — harder to predict
- Experimental — results vary by domain

### When to use
- Dense, unstructured narrative text
- Academic papers and research
- Legal documents
- Long articles where topics blend into each other
- When structure-based splitting gives poor results

---

## Method 6: LLM-Based Chunking

### What it is
Use an LLM itself to decide how to split the document — and optionally enrich each chunk with a context summary.

### How it works
Feed the document (or sections) to an LLM with a prompt like:
> "Given this document, split it into the most meaningful chunks. Each chunk should represent one complete idea or argument."

Anthropic's **Contextual Retrieval** (2024) is the most famous implementation:
1. Send entire document + chunk to Claude
2. Claude generates a short contextual description for each chunk
3. Prepend the description to the chunk before embedding
4. This gives every chunk awareness of the broader document context

```python
# Conceptual pattern (simplified)
def create_contextual_chunk(document_text, chunk_text, llm):
    prompt = f"""
    Document context:
    {document_text}
    
    Chunk to contextualize:
    {chunk_text}
    
    Write a brief context description (2-3 sentences) explaining 
    how this chunk fits into the broader document.
    """
    context = llm.invoke(prompt)
    return f"{context}\n\n{chunk_text}"
```

### Pros
- Highest quality chunks
- Chunks can include summaries and context descriptions
- Handles complex documents that confuse rule-based methods

### Cons
- Very slow — requires LLM call per chunk
- Very expensive — LLM API costs multiply with document volume
- Not practical for large document sets without caching

### When to use
- High-stakes documents where quality is critical
- Legal contracts, medical records, regulatory filings
- Enterprise knowledge bases with small doc count
- When retrieval quality must be maximized regardless of cost

---

## Method 7: Agentic Chunking

### What it is
An AI agent analyses the entire document, decides which chunking strategy is best for each section, and applies that strategy dynamically.

### How it works
The agent acts as a supervisor that:
1. Reads the document's structure and content
2. Decides: "this section needs semantic chunking; this table needs row chunking; this code block needs code chunking"
3. Applies different strategies per section
4. Enriches chunks with metadata tags for advanced retrieval

### Pros
- Highest possible chunk quality
- Tailored per document type and per section
- Can add rich metadata automatically

### Cons
- Most complex to implement
- Very expensive — many LLM calls per document
- Requires robust agent infrastructure

### When to use
- High-stakes RAG systems where cost is secondary to quality
- Complex multi-format documents (part narrative, part table, part code)
- When you need custom strategies tailored to each document's unique characteristics

---

## Method 8: Late Chunking

### What it is
Embed the **entire document first**, then derive chunk embeddings from the full-document token embeddings.

This solves the context-loss problem in standard chunking: when you split first and then embed, each chunk loses awareness of the rest of the document.

### How it works
Standard chunking (context loss):
```
Document → Split into chunks → Embed each chunk independently
```

Late chunking (context preserved):
```
Document → Embed entire document (token-level) → Split into chunks → 
Average token embeddings for each chunk region
```

Each chunk's embedding was generated with the full document in context.

### Pros
- Chunks retain context of the whole document
- Relationships between sections are preserved
- No context loss for cross-references

### Cons
- Requires a long-context embedding model
- More complex infrastructure
- Higher memory requirements

### When to use
- Technical documents where sections reference each other
- Research papers that build arguments across sections
- Legal documents with cross-clause dependencies
- Any document where understanding one part requires context from another

---

## Method 9: Hierarchical Chunking

### What it is
Create **multiple layers of chunks** at different levels of detail simultaneously.

```
Book
  └── Chapter (large chunk — summary-level)
       └── Section (medium chunk — topic-level)
            └── Paragraph (small chunk — detail-level)
```

### How it works
Using LlamaIndex's HierarchicalNodeParser:

```python
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes

node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]  # large, medium, small
)
nodes = node_parser.get_nodes_from_documents(documents)
leaf_nodes = get_leaf_nodes(nodes)
```

Retrieval can start at any level — find the section, then drill into the paragraph.

### Pros
- Answers both high-level summary questions and granular detail questions
- Natural fit for large, multi-level documents
- Enables multi-granularity retrieval

### Cons
- More complex index structure
- Higher storage (multiple representations of same content)
- More complex retrieval logic

### When to use
- Books, textbooks, and manuals
- Long legal contracts
- Technical documentation with chapters and sub-sections
- Enterprise knowledge bases with both executive summaries and technical detail

---

## Method 10: Adaptive Chunking

### What it is
Dynamically adjust chunk size and overlap **based on the content density** of each section.

Dense, information-rich sections → smaller chunks  
Light, narrative sections → larger chunks

### How it works
Uses ML or heuristics to analyze:
- Vocabulary density
- Sentence complexity
- Topic concentration
Then adjusts chunk parameters accordingly per section.

### Pros
- Best fit for documents with uneven content density
- No one-size-fits-all compromise

### Cons
- Complex to implement
- Requires additional ML/heuristic layer

### When to use
- Mixed datasets: blogs + PDFs + emails + technical docs together
- Documents that alternate between dense technical sections and narrative context
- Large corpora where fixed sizing is clearly suboptimal

---

## Method 11: Code Chunking

### What it is
Split code files by their **logical units**: functions, classes, methods, modules.

### How it works
```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

# For Python
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1500,
    chunk_overlap=0
)

# For JavaScript
js_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size=1500,
    chunk_overlap=0
)
```

LangChain supports: Python, JS, TypeScript, Rust, Go, Java, C, C++, Ruby, Markdown, LaTeX, HTML, Solidity.

### Best chunking boundaries for code
- One function = one chunk (ideal)
- One class = one chunk (or break by methods)
- Import block = separate chunk
- Docstring + function = same chunk

### Pros
- Preserves logical code units
- Docstrings stay with their function
- Enables code search by function/class

### Cons
- Very long functions may still need splitting
- Closely coupled functions may lose context if split

### When to use
- Code repositories
- API documentation with code examples
- Technical manuals with embedded scripts

---

## Decision Flowchart

```
Does your data need chunking?
├── NO  (FAQs, short product descriptions, pre-structured Q&A)
│   └── Skip chunking — embed directly
└── YES

What type of document is it?
├── Code → Code Chunking (Method 11)
├── Markdown / HTML → Document-Based (Method 3)
├── Transcript / Conversation → Sliding Window (Method 4)
├── Large structured doc (book/manual) → Hierarchical (Method 9)
├── Dense academic/legal text → Semantic (Method 5)
├── Mixed-format doc → Agentic (Method 7)
├── Doc with cross-references → Late Chunking (Method 8)
├── High-stakes complex doc, cost not an issue → LLM-Based (Method 6)
└── Everything else → Recursive (Method 2) as default

If Recursive still underperforms:
└── Add overlap → tune size → try semantic → add metadata filters
```
