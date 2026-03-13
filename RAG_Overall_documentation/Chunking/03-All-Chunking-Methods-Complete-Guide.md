# All Chunking Methods — Complete Guide

> This is the complete reference for every chunking method. Each method is explained with a real document example, a clear before/after comparison, working code, and an honest trade-off assessment. By the end of this document you should be able to pick the right method for any document you encounter — and explain why.

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

### What problem it solves

You have a document. You need to split it. You want the simplest possible approach that works well enough to get started and build a baseline.

Fixed-size chunking is exactly that — split every N characters (or tokens), no matter what the content says.

---

### How it works — step by step

You define two numbers:
- `chunk_size`: how large each chunk can be (in characters or tokens)
- `chunk_overlap`: how many characters/tokens are shared between consecutive chunks

```
Document: "Kubernetes is a container orchestration platform.
           It was developed by Google. It automates deployment,
           scaling, and management of containerized applications.
           The scheduler assigns pods to nodes based on resources.
           etcd stores all cluster state as key-value pairs."

chunk_size = 100 characters, overlap = 20 characters

Chunk 1: characters 0–100
"Kubernetes is a container orchestration platform. It was developed by Google. It automates deploymen"

Chunk 2: characters 80–180  (20 character overlap)
"t automates deployment, scaling, and management of containerized applications. The scheduler assigns"

Chunk 3: characters 160–260
"s pods to nodes based on resources. etcd stores all cluster state as key-value pairs."
```

Notice what happened in Chunk 1: the word "deployment" was split to "deploymen" — because the chunk ended exactly at that character. Chunk 2 starts with "t automates" — which is the remainder of that word.

This is the core weakness of fixed-size chunking. It does not know what a word is, what a sentence is, or what a paragraph is. It just counts characters.

---

### The overlap in action — why it matters

Without overlap, Chunk 1 ends at "deploymen" and Chunk 2 starts with "t automates deployment". A query about "deployment" that retrieves only Chunk 2 would see "t automates deployment" at the very start — broken context.

With overlap, the same 20 characters appear at the end of Chunk 1 AND the start of Chunk 2. Both chunks contain the complete word "deployment" in some form.

**Overlap is a safety net for fixed-size chunking. Always use it.**

---

### Real example: what fixed chunking produces on a policy document

Original text:
```
Employees are eligible for 20 days of annual leave per year.
Leave must be applied at least 2 weeks in advance.
Unused leave can be carried forward up to a maximum of 10 days.
```

Fixed chunking at 80 characters with no overlap:
```
Chunk 1: "Employees are eligible for 20 days of annual leave per year.\nLeave must be"
Chunk 2: " applied at least 2 weeks in advance.\nUnused leave can be carried forward up"
Chunk 3: " to a maximum of 10 days."
```

A user asks: *"How much leave can be carried forward?"*

The answer is in Chunk 3: "to a maximum of 10 days." — but there is no subject in this chunk. The retriever may not return it because "carried forward" is in Chunk 2, and the actual number is in Chunk 3.

This shows exactly why fixed-size chunking, while useful as a starting point, needs overlap and careful size selection.

---

### Code

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Character-based (default in LangChain)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 500 characters per chunk
    chunk_overlap=50     # 50 character overlap (10%)
)
chunks = splitter.split_text(text)

# Or split Document objects (preserves metadata)
chunks = splitter.split_documents(docs)

# Print result
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1} ({len(chunk.page_content)} chars):")
    print(chunk.page_content[:100])
    print("---")
```

---

### Pros
- Simplest to implement — 3 lines of code
- Fast and completely predictable
- Easy to reproduce — same document always produces same chunks
- Good baseline — gives you a score to beat with better strategies

### Cons
- Ignores all document structure (paragraphs, sentences, headings)
- Can split mid-sentence, mid-word, or mid-list
- Overlap helps but does not fully prevent context loss
- Not suitable as final strategy for important documents

### When to use
- First experiment when starting a new RAG project
- When you need a quick baseline to measure improvements against
- Short, simple documents (emails, meeting notes, product descriptions) where perfect boundaries matter less
- Documents with no clear structure to exploit

### Rule of thumb
Always set overlap to at least 10% of chunk_size. For important documents, 15–20%.

---

## Method 2: Recursive Chunking

### What problem it solves

Fixed chunking does not care about sentence or paragraph boundaries. Recursive chunking does.

It tries to split at paragraph boundaries first. If the paragraph is still too large, it tries sentence boundaries. If that is still too large, it tries words. This way chunks stay as semantically intact as possible.

This is the **default recommended method** for most RAG systems.

---

### How the algorithm works — step by step

The splitter has a priority-ordered list of separators:

```
Priority 1: "\n\n"  → paragraph break (strongest semantic boundary)
Priority 2: "\n"    → line break
Priority 3: ". "    → sentence end
Priority 4: " "     → word boundary
Priority 5: ""      → character (last resort)
```

For each section of text:
1. Try splitting by `\n\n` — does each resulting piece fit in chunk_size?
2. If yes → done. These are the chunks.
3. If no (some piece is still too large) → try `\n` on that piece
4. Still too large? → try `. `
5. Still too large? → try ` `
6. Still too large? → split by character

---

### Real example: walking through the algorithm

Document:
```
Kubernetes is an open-source container orchestration platform.
It was originally developed by Google.

The main components of Kubernetes include the API Server, Scheduler,
Controller Manager, and etcd.

The Scheduler assigns pods to nodes based on available resources.
etcd stores all cluster configuration as key-value pairs.
```

chunk_size = 150 characters, chunk_overlap = 20

**Step 1:** Try splitting by `\n\n` (paragraph breaks):
```
Piece 1: "Kubernetes is an open-source container orchestration platform.\nIt was originally developed by Google."
→ 103 characters → fits in 150 ✅ → becomes Chunk 1

Piece 2: "The main components of Kubernetes include the API Server, Scheduler,\nController Manager, and etcd."
→ 98 characters → fits in 150 ✅ → becomes Chunk 2

Piece 3: "The Scheduler assigns pods to nodes based on available resources.\netcd stores all cluster configuration as key-value pairs."
→ 121 characters → fits in 150 ✅ → becomes Chunk 3
```

Result:
```
Chunk 1: "Kubernetes is an open-source container orchestration platform.
           It was originally developed by Google."

Chunk 2: "The main components of Kubernetes include the API Server, Scheduler,
           Controller Manager, and etcd."

Chunk 3: "The Scheduler assigns pods to nodes based on available resources.
           etcd stores all cluster configuration as key-value pairs."
```

Every chunk is a complete paragraph. Every chunk passes the "makes sense alone" test.

---

### What happens when a paragraph is too large

If Piece 2 had been 300 characters (exceeds chunk_size=150), the algorithm recurses:

**Step 2:** Apply `\n` to Piece 2:
```
Sub-piece 2a: "The main components of Kubernetes include the API Server, Scheduler,"
→ 70 characters → fits ✅

Sub-piece 2b: "Controller Manager, and etcd."
→ 29 characters → fits ✅
```

These become sub-chunks. The algorithm keeps recursing until everything fits — always using the highest-priority separator available.

---

### Comparison: Fixed vs Recursive on the same document

Same document, same chunk_size=150:

**Fixed chunking result:**
```
Chunk 1: "Kubernetes is an open-source container orchestration platform.\nIt was originally devel"
Chunk 2: "oped by Google.\n\nThe main components of Kubernetes include the API Server, Scheduler,\nC"
Chunk 3: "ontroller Manager, and etcd.\n\nThe Scheduler assigns pods to nodes based on available res"
```

"devel" is split from "oped". Paragraph breaks are ignored. Chunks cross paragraph boundaries.

**Recursive chunking result:**
```
Chunk 1: "Kubernetes is an open-source container orchestration platform. It was originally developed by Google."
Chunk 2: "The main components of Kubernetes include the API Server, Scheduler, Controller Manager, and etcd."
Chunk 3: "The Scheduler assigns pods to nodes based on available resources. etcd stores all cluster configuration as key-value pairs."
```

Clean boundaries. Complete thoughts. Self-contained chunks.

---

### Code

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""]  # priority order
)

# Split plain text
chunks = splitter.split_text(text)

# Split documents (preserves metadata from loader)
chunks = splitter.split_documents(docs)

print(f"Created {len(chunks)} chunks")
print(f"First chunk preview: {chunks[0].page_content[:200]}")
```

### Pros
- Respects natural language structure — paragraphs and sentences stay intact
- Adapts to the document content
- Avoids mid-sentence and mid-word splits in almost all cases
- Great default — works well for 80% of use cases without tuning

### Cons
- Still not aware of semantic meaning (just structure)
- A paragraph about Kubernetes + Docker can still end up in one chunk if small enough

### When to use
- **Start here for any new RAG project**
- Research articles, blog posts, policy documents, process docs
- Any unstructured narrative text
- When you do not know yet what strategy is best — this is the safe default

---

## Method 3: Document-Based / Structure-Based Chunking

### What problem it solves

Recursive chunking uses generic separators that work for any text. But many documents have their own built-in structure — headings, sections, HTML tags, code blocks.

Document-based chunking uses that existing structure instead of inventing its own. A Markdown heading is a much better split point than a double newline. An HTML `<h2>` tag tells you exactly where a new topic begins.

---

### How it works: Markdown

Markdown documents use `#`, `##`, `###` as headings. Each heading is the start of a new topic. Split there.

**Example document:**
```markdown
# Kubernetes Overview

Kubernetes is an open-source container orchestration platform
used to manage containerized applications at scale.

## Core Components

The main components are the API Server, Scheduler, Controller
Manager, and etcd database.

## Deployment

To deploy an application, you create a Deployment manifest
with the desired number of replicas and container image.
```

**Result after MarkdownHeaderTextSplitter:**
```
Chunk 1:
  content: "Kubernetes is an open-source container orchestration platform used to manage containerized applications at scale."
  metadata: {"Header 1": "Kubernetes Overview"}

Chunk 2:
  content: "The main components are the API Server, Scheduler, Controller Manager, and etcd database."
  metadata: {"Header 1": "Kubernetes Overview", "Header 2": "Core Components"}

Chunk 3:
  content: "To deploy an application, you create a Deployment manifest with the desired number of replicas and container image."
  metadata: {"Header 1": "Kubernetes Overview", "Header 2": "Deployment"}
```

Notice what happened to the metadata — every chunk automatically knows its heading hierarchy. A retriever can now filter: *"only search chunks under the 'Deployment' heading."*

---

### Code: Markdown

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#",  "h1"),
    ("##", "h2"),
    ("###","h3"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False  # keep headings inside chunk text
)
chunks = splitter.split_text(markdown_text)

# Each chunk now has heading info in metadata
for chunk in chunks:
    print("Heading:", chunk.metadata)
    print("Content:", chunk.page_content[:150])
    print("---")
```

---

### How it works: HTML

HTML pages from scraped websites use tags like `<h1>`, `<h2>`, `<p>`, `<article>`. Split at these logical boundaries.

**Example scraped product page:**
```html
<h1>Kubernetes Documentation</h1>

<h2>Getting Started</h2>
<p>Kubernetes can be installed using kubeadm, minikube, or managed cloud services like EKS.</p>

<h2>Architecture</h2>
<p>The control plane manages the cluster state. Worker nodes run the actual workloads.</p>
```

**Result:**
```
Chunk 1:
  content: "Kubernetes can be installed using kubeadm, minikube, or managed cloud services like EKS."
  metadata: {"h1": "Kubernetes Documentation", "h2": "Getting Started"}

Chunk 2:
  content: "The control plane manages the cluster state. Worker nodes run the actual workloads."
  metadata: {"h1": "Kubernetes Documentation", "h2": "Architecture"}
```

---

### Code: HTML

```python
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "h1"),
    ("h2", "h2"),
    ("h3", "h3"),
]
splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(html_text)
```

---

### Why document-based is better than recursive for structured docs

Recursive chunking on the Kubernetes markdown would produce:

```
Chunk 1: "# Kubernetes Overview\n\nKubernetes is an open-source container orchestration platform..."
Chunk 2: "## Core Components\n\nThe main components are..."
Chunk 3: "## Deployment\n\nTo deploy an application..."
```

It works, but:
- The heading is stuck inside the chunk text, not in metadata
- You cannot filter by heading without text search
- Heading context may split off from its content for long sections

Document-based chunking puts headings in metadata cleanly, keeping the content focused.

---

### Pros
- Chunks align perfectly with the document's logical structure
- Headings automatically populate metadata
- Works extremely well for documentation, wikis, and scraped web content
- HTML and Markdown are the most common formats in enterprise knowledge bases

### Cons
- Requires documents to have consistent, well-formed formatting
- A poorly formatted Markdown file (missing headings) produces poor chunks
- Not useful for PDFs or plain text with no structural markers

### When to use
- Markdown-based knowledge bases and wikis
- Scraped HTML web pages
- Technical documentation written in Markdown
- Any document where sections are clearly marked with headings or tags

---

## Method 4: Sliding Window Chunking

### What problem it solves

In a conversation transcript or meeting recording, context flows continuously. One person's statement only makes sense in the context of what was said before and after it.

Fixed or recursive chunking creates hard boundaries. A question in Chunk 3 may reference an answer in Chunk 2. They get split and context is lost.

Sliding window chunking creates chunks with very high overlap — the "window" slides slowly across the text, ensuring that every boundary region appears in multiple chunks.

---

### How it works

```
Text: [sentence 1][sentence 2][sentence 3][sentence 4][sentence 5][sentence 6]

chunk_size = 3 sentences, overlap = 2 sentences

Chunk 1: [sentence 1][sentence 2][sentence 3]
Chunk 2: [sentence 2][sentence 3][sentence 4]   ← window slides by 1
Chunk 3: [sentence 3][sentence 4][sentence 5]   ← window slides by 1
Chunk 4: [sentence 4][sentence 5][sentence 6]   ← window slides by 1
```

Every sentence appears in multiple chunks. No sentence is ever isolated.

---

### Real example: meeting transcript

Transcript:
```
[00:02] Alice: We need to decide on the deployment timeline.
[00:05] Bob: I think we can ship by end of Q3 if we cut scope.
[00:08] Alice: Which features would you cut?
[00:11] Bob: I would cut the real-time analytics dashboard.
[00:14] Alice: That's fine. The dashboard was a nice-to-have anyway.
[00:17] Bob: Agreed. I'll update the roadmap today.
```

**With hard chunking (chunk_size = 2 lines, no overlap):**
```
Chunk 1: "[00:02] Alice: We need to decide on the deployment timeline.
           [00:05] Bob: I think we can ship by end of Q3 if we cut scope."

Chunk 2: "[00:08] Alice: Which features would you cut?
           [00:11] Bob: I would cut the real-time analytics dashboard."

Chunk 3: "[00:14] Alice: That's fine. The dashboard was a nice-to-have anyway.
           [00:17] Bob: Agreed. I'll update the roadmap today."
```

User asks: *"What did they agree to cut and why?"*

The cut decision is in Chunk 2, the reason ("nice-to-have") is in Chunk 3. The retriever likely returns only one of them — incomplete answer.

**With sliding window (chunk_size = 3 lines, overlap = 2 lines):**
```
Chunk 1: "[00:02] We need to decide on deployment...
           [00:05] ship by end of Q3 if we cut scope.
           [00:08] Which features would you cut?"

Chunk 2: "[00:05] ship by end of Q3 if we cut scope.
           [00:08] Which features would you cut?
           [00:11] I would cut the real-time analytics dashboard."

Chunk 3: "[00:08] Which features would you cut?
           [00:11] I would cut the real-time analytics dashboard.
           [00:14] That's fine. The dashboard was a nice-to-have anyway."

Chunk 4: "[00:11] cut the real-time analytics dashboard.
           [00:14] That's fine. The dashboard was a nice-to-have anyway.
           [00:17] Agreed. I'll update the roadmap today."
```

Now Chunk 3 contains both: the decision ("cut the dashboard") AND the reason ("nice-to-have"). One chunk, complete answer.

---

### Code

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# High overlap = sliding window behavior
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=150,   # 50% overlap — high, intentionally
    separators=["\n", ". ", " ", ""]
)
chunks = splitter.split_documents(docs)

print(f"Total chunks: {len(chunks)}")
# Note: will be significantly more chunks than fixed chunking
# This is expected — redundancy is the point
```

### Pros
- Preserves context continuity across all boundaries
- Every important sentence appears in at least 2 chunks
- Works extremely well for transcripts, chats, and conversational text

### Cons
- High redundancy — the same content appears in many chunks
- Larger vector index size
- More embedding API calls = higher cost
- Can produce noisy retrieval if overlap is set too high

### When to use
- Meeting transcripts and recordings
- Chat logs and support conversation histories
- Podcast or video transcripts
- Any text where every sentence is contextually dependent on its neighbors

---

## Method 5: Semantic Chunking

### What problem it solves

Recursive and document-based chunking split by structure (paragraphs, headings). But structure does not always match meaning. A single long paragraph can contain two completely different topics. Splitting at the paragraph boundary keeps them together — producing a noisy, diluted embedding.

Semantic chunking uses the actual meaning of sentences to decide where boundaries belong. If consecutive sentences have very different meanings — that's where to split.

---

### How it works — step by step

**Step 1: Break into sentences**
```
Original text:
"Kubernetes is a container orchestration platform. It was developed by Google.
Docker is a containerization tool that packages applications. Docker Desktop
runs on Windows and Mac. CI/CD pipelines automate build and deployment.
Jenkins and GitHub Actions are popular CI/CD tools."

Sentences:
S1: "Kubernetes is a container orchestration platform."
S2: "It was developed by Google."
S3: "Docker is a containerization tool that packages applications."
S4: "Docker Desktop runs on Windows and Mac."
S5: "CI/CD pipelines automate build and deployment."
S6: "Jenkins and GitHub Actions are popular CI/CD tools."
```

**Step 2: Embed each sentence**
```
Vector(S1) = [0.82, 0.14, 0.33, ...]   ← Kubernetes topic
Vector(S2) = [0.79, 0.16, 0.31, ...]   ← still Kubernetes (very close to S1)
Vector(S3) = [0.21, 0.78, 0.25, ...]   ← Docker topic (very different from S2)
Vector(S4) = [0.19, 0.81, 0.22, ...]   ← still Docker (close to S3)
Vector(S5) = [0.15, 0.23, 0.88, ...]   ← CI/CD topic (very different from S4)
Vector(S6) = [0.13, 0.21, 0.85, ...]   ← still CI/CD (close to S5)
```

**Step 3: Compare consecutive sentence similarity**
```
Similarity(S1, S2) = 0.97  ← very high → same topic → no split
Similarity(S2, S3) = 0.22  ← very low  → topic change → SPLIT HERE
Similarity(S3, S4) = 0.94  ← very high → same topic → no split
Similarity(S4, S5) = 0.19  ← very low  → topic change → SPLIT HERE
Similarity(S5, S6) = 0.96  ← very high → same topic → no split
```

**Step 4: Form chunks at split points**
```
Chunk 1 (Kubernetes): S1 + S2
  "Kubernetes is a container orchestration platform. It was developed by Google."

Chunk 2 (Docker): S3 + S4
  "Docker is a containerization tool that packages applications.
   Docker Desktop runs on Windows and Mac."

Chunk 3 (CI/CD): S5 + S6
  "CI/CD pipelines automate build and deployment.
   Jenkins and GitHub Actions are popular CI/CD tools."
```

Three topics → three clean chunks → three precise embeddings.

---

### Why this beats recursive for mixed-topic text

If this same text was chunked recursively with chunk_size = 400 characters:

```
Chunk 1 (ALL topics together):
  "Kubernetes is a container orchestration platform. It was developed by Google.
   Docker is a containerization tool that packages applications. Docker Desktop
   runs on Windows and Mac. CI/CD pipelines automate build and deployment."
```

This chunk's embedding represents Kubernetes + Docker + CI/CD all blended together. It is a noisy, averaged representation.

User asks: *"What is Docker?"*  
The Kubernetes+Docker+CI/CD chunk may or may not rank highly.  
The focused Docker chunk from semantic chunking will rank much higher.

---

### Code

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

# Free version using HuggingFace
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # where to draw the cut line
    breakpoint_threshold_amount=90           # top 10% of similarity drops = boundary
)

chunks = splitter.split_documents(docs)

# Using OpenAI (paid, higher quality)
from langchain_openai import OpenAIEmbeddings
splitter_openai = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1.5
)
```

### Pros
- Most semantically coherent chunks of any free method
- Works even when documents have no headings or formal structure
- Topic changes define boundaries — not arbitrary character counts

### Cons
- Requires running embeddings twice (once for chunking, once for indexing) — slower and more expensive
- Produces variable chunk sizes — harder to predict and control
- Results vary by domain — needs tuning per document type
- Experimental — `langchain_experimental` package required

### When to use
- Dense, unstructured academic or research text
- Legal documents where arguments flow without structural markers
- Long news articles and essays where topics blend gradually
- When recursive chunking produces noisy, mixed-topic chunks

---

## Method 6: LLM-Based Chunking

### What problem it solves

All previous methods work with text structure or statistical similarity. None of them truly understand what the content means.

An LLM does. LLM-based chunking uses a language model to understand the document and decide how it should be split — or to add missing context to each chunk.

---

### The Context Loss Problem — What LLM-Based Chunking Fixes

Standard chunking produces:

```
Chunk 7: "Revenue increased by 10% compared to last quarter."
```

A user asks: *"How did Tesla perform in Q3 2024?"*

The retriever searches for chunks matching "Tesla Q3 2024." This chunk does not mention Tesla, Q3, or 2024. It gets a low similarity score and may not be retrieved — even though it is the answer.

The problem: the chunk was extracted from a Tesla Q3 2024 earnings report, but that context was stripped away when the chunk was created.

---

### Anthropic Contextual Retrieval — The Most Important LLM Chunking Method

In 2024, Anthropic published a technique called **Contextual Retrieval** that solves this problem directly.

The idea:
1. Take each chunk you would normally create
2. Send the ENTIRE document + the chunk to Claude
3. Ask Claude to write a short context sentence describing where this chunk fits in the document
4. Prepend that context sentence to the chunk before embedding

**Before (standard chunk):**
```
Chunk: "Revenue increased by 10% compared to last quarter."
Embedding: represents "revenue increased 10%" → vague
```

**After (contextual chunk):**
```
Context added by Claude:
  "This passage from Tesla's Q3 2024 earnings report discusses quarterly
   revenue growth in the automotive segment."

Full chunk sent to embedding:
  "This passage from Tesla's Q3 2024 earnings report discusses quarterly
   revenue growth in the automotive segment.
   
   Revenue increased by 10% compared to last quarter."

Embedding: represents "Tesla Q3 2024 automotive revenue growth 10%" → precise
```

Now when a user asks *"How did Tesla perform in Q3 2024?"* — the retriever finds this chunk immediately because the embedding contains all the relevant context.

**Anthropic reported: 49% reduction in retrieval failures after applying this technique.**

---

### Code

```python
import anthropic

client = anthropic.Anthropic()

def add_context_to_chunk(full_document: str, chunk_text: str) -> str:
    """
    Ask Claude to write a context description for a chunk
    and prepend it before embedding.
    """
    prompt = f"""
    Here is the complete document:
    <document>
    {full_document}
    </document>
    
    Here is the specific chunk from that document:
    <chunk>
    {chunk_text}
    </chunk>
    
    Write 1-2 sentences of context that explain what this chunk is about
    and where it fits within the broader document.
    Answer only with the context — no preamble, no explanation.
    """
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # cheapest Claude model
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    
    context = response.content[0].text.strip()
    return f"{context}\n\n{chunk_text}"


# Apply to all chunks from a document
def create_contextual_chunks(document_text: str, chunks: list) -> list:
    contextual_chunks = []
    for chunk in chunks:
        enriched_text = add_context_to_chunk(document_text, chunk.page_content)
        chunk.page_content = enriched_text
        contextual_chunks.append(chunk)
    return contextual_chunks
```

**Cost optimization:** Claude supports prompt caching. The full document is sent once and cached. Each chunk call only pays for the chunk tokens, not the full document again. This makes the cost manageable.

---

### Pros
- Highest quality chunks — LLM understands the content
- Each chunk carries its own context — no more isolated, out-of-context fragments
- Dramatically improves retrieval accuracy
- Works for any document type including complex nested structures

### Cons
- Requires one LLM API call per chunk — slow for large document sets
- Expensive — cost scales with document volume and chunk count
- Not practical without prompt caching for large corpora
- Adds latency to the ingestion pipeline

### When to use
- High-stakes, low-volume document sets (legal contracts, financial reports, medical records)
- Enterprise knowledge bases where retrieval quality directly affects business decisions
- Documents where chunks frequently need the broader document context to be understood
- When you can afford the cost and ingestion time

---

## Method 7: Agentic Chunking

### What problem it solves

LLM-based chunking improves each chunk with context. But it still applies one strategy to every chunk.

A real enterprise document might contain:
- Narrative prose (needs semantic boundaries)
- Tables (needs row-level chunking)
- Code blocks (needs function-level chunking)
- Bullet lists (needs list-level chunking)

No single strategy works well for all of these at once. Agentic chunking uses an AI agent to inspect each section and decide the best strategy for it.

---

### How it works

```
Document arrives
     ↓
Agent reads the document
     ↓
Agent categorizes each section:
  "Section 1: Narrative text → use semantic chunking"
  "Section 2: Code block → use code chunking (split by function)"
  "Section 3: Data table → use row chunking"
  "Section 4: Policy rules → use larger chunks (keep rule + exception together)"
     ↓
Agent applies different strategy per section
     ↓
Agent enriches each chunk with metadata tags
     ↓
Final chunks sent to embedding
```

---

### Real example: Enterprise Architecture Document

Document structure:
```
Introduction:
  "This document describes the deployment architecture for our production Kubernetes cluster..."
  → Narrative → Semantic chunking (medium size)

Infrastructure Code:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: frontend
  ```
  → Code → Code chunking (full block together)

Resource Table:
  | Service    | CPU   | Memory | Replicas |
  | frontend   | 2 CPU | 4GB    | 3        |
  | backend    | 4 CPU | 8GB    | 5        |
  → Tabular → Row chunking (one row per chunk + summary)

DR Policy:
  "In the event of a region failure, traffic is routed to the secondary region.
   Exception: if both regions are degraded, manual intervention is required."
  → Policy → Large chunk (rule + exception must stay together)
```

Agentic chunking handles each section correctly. A uniform strategy would handle most of them poorly.

---

### Pros
- Highest possible chunk quality across mixed-format documents
- Each section gets the optimal strategy for its content type
- Can automatically add rich, section-specific metadata

### Cons
- Most complex to implement — requires agent infrastructure
- Very expensive — multiple LLM calls per document
- Very slow — not suitable for real-time ingestion
- Overkill for simple, uniform document sets

### When to use
- Complex enterprise documents that mix narrative, code, tables, and policy
- High-stakes knowledge bases where quality is the primary concern
- When you have validated that simpler methods produce unacceptable results
- Projects where ingestion happens offline and latency is not a constraint

---

## Method 8: Late Chunking

### What problem it solves

In standard chunking (split first, then embed), each chunk is embedded in isolation. It has no memory of the rest of the document.

This causes a specific failure: pronouns and cross-references.

---

### The Pronoun Problem

Document:
```
Sentence 1: "Kubernetes is a container orchestration platform."
Sentence 2: "It was originally developed by Google."
Sentence 3: "It automates deployment, scaling, and management."
```

Standard chunking might produce:
```
Chunk 1: "Kubernetes is a container orchestration platform."
Chunk 2: "It was originally developed by Google."
Chunk 3: "It automates deployment, scaling, and management."
```

Chunks 2 and 3 use "It" — but when embedded in isolation, the model does not know "It" refers to Kubernetes. The embeddings for Chunks 2 and 3 are vague — they represent "something developed by Google" and "something that automates" without a subject.

A user asking *"Who developed Kubernetes?"* may not retrieve Chunk 2 because "Kubernetes" is not in Chunk 2, and the isolated embedding of "It was originally developed by Google" does not strongly represent "Kubernetes."

---

### How Late Chunking Fixes This

```
Standard approach (context loss):
  Document → Split into chunks → Embed each chunk independently
  Chunk 2 embedding = "Something was developed by Google" (no Kubernetes context)

Late chunking (context preserved):
  Document → Embed WHOLE document first → Get token-level embeddings
           → Each token's embedding already reflects the full document context
           → Now split the document into chunks
           → Average the token embeddings for each chunk region
  Chunk 2 embedding = "Kubernetes was developed by Google" (subject preserved)
```

The key: when the whole document is embedded, the model's attention mechanism processes every token in relation to every other token. "It" in Sentence 2 gets embedded with full awareness that it refers to "Kubernetes" from Sentence 1.

When you then split and average those embeddings per chunk — each chunk carries the full document's context.

---

### Code

```python
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# jina-embeddings-v2 explicitly supports late chunking
model_name = "jinaai/jina-embeddings-v2-base-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def late_chunk_document(text: str, chunk_boundaries: list) -> list:
    """
    Embed entire document first, then derive chunk embeddings.
    chunk_boundaries: list of (start_char, end_char) tuples
    """
    # Step 1: Tokenize entire document
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    
    # Step 2: Embed entire document (all tokens with full context)
    with torch.no_grad():
        outputs = model(**inputs)
    token_embeddings = outputs.last_hidden_state[0]  # shape: [num_tokens, dim]
    
    # Step 3: Map character boundaries to token positions
    char_to_token = inputs.encodings[0].char_to_token
    
    # Step 4: For each chunk, average the token embeddings in its range
    chunk_embeddings = []
    for start_char, end_char in chunk_boundaries:
        start_tok = char_to_token(start_char)
        end_tok = char_to_token(end_char - 1)
        if start_tok is not None and end_tok is not None:
            chunk_emb = token_embeddings[start_tok:end_tok+1].mean(dim=0)
            chunk_embeddings.append(chunk_emb.numpy())
    
    return chunk_embeddings
```

### Pros
- Chunks retain full document context — pronouns, cross-references, progressive arguments all work
- Relationships between distant sections are preserved
- No context loss at chunk boundaries

### Cons
- Requires a long-context embedding model to fit the whole document
- More complex infrastructure than standard chunking
- Higher memory usage during embedding
- Document must fit within the embedding model's context window (use for shorter docs or long-context models)

### When to use
- Research papers that build on earlier sections
- Legal documents where later clauses reference earlier definitions
- Financial reports where tables reference narrative sections
- Technical docs where "the above command" references code from two sections back

---

## Method 9: Hierarchical Chunking

### What problem it solves

Different questions require different levels of detail.

*"Give me an overview of how Kubernetes works"* → needs a broad, high-level summary  
*"What exact flag do I pass to kubectl rollout?"* → needs a precise, detailed chunk

A flat chunk structure (all chunks at the same size) cannot serve both well. If chunks are small for precision, broad questions get too many irrelevant small chunks. If chunks are large for context, specific questions lose precision.

Hierarchical chunking creates multiple layers simultaneously — so both question types get the right level of detail.

---

### How it works

```
Full Document (whole book/manual)
  └── Large chunks / Level 1 (2048 tokens) — Chapter level
       "Chapter 3: Kubernetes Deployment covers deploying applications,
        managing replicas, rolling updates, and rollback procedures."
       
       └── Medium chunks / Level 2 (512 tokens) — Section level
            "Rolling Updates: A rolling update gradually replaces old pod
             versions with new ones, ensuring zero downtime..."
             
             └── Small chunks / Level 3 (128 tokens) — Paragraph level
                  "To trigger a rollout: kubectl rollout restart deployment/frontend"
```

---

### Real example: Two questions, two levels

**Question 1 (broad):** *"What does Chapter 3 cover?"*

Retrieval hits Level 1 chunk:
```
"Chapter 3 covers deploying applications, managing replicas,
 rolling updates, and rollback procedures."
```
✅ Perfect high-level answer.

**Question 2 (specific):** *"How do I restart a deployment?"*

Retrieval hits Level 3 chunk:
```
"kubectl rollout restart deployment/frontend"
```
✅ Perfect specific answer.

A flat single-level structure would struggle with one or the other. Hierarchical handles both.

---

### Code (LlamaIndex)

```python
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core import VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore

# Create three-level hierarchy
node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]  # L1=large, L2=medium, L3=small (leaf)
)
nodes = node_parser.get_nodes_from_documents(documents)

# Build index from leaf nodes (Level 3 — most precise)
leaf_nodes = get_leaf_nodes(nodes)

# Store ALL nodes (needed for auto-merging)
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)

# Build vector index on leaf nodes
index = VectorStoreIndex(leaf_nodes)

# Auto-merging retriever:
# - Finds matching leaf nodes
# - If enough leaf nodes from the same parent match → returns parent instead
# - This "merges up" for broad questions automatically
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=12),
    docstore=docstore,
    verbose=True
)
```

### Pros
- Answers both summary-level and detail-level questions from the same index
- Natural fit for book-length documents
- Auto-merging retriever can dynamically choose the right level

### Cons
- More complex index — multiple representations of the same content
- Higher storage (3x for a 3-level hierarchy)
- More complex retrieval logic to implement correctly

### When to use
- Textbooks, technical manuals, and long guides
- Legal contracts with many cross-referenced articles
- Enterprise knowledge bases where users ask both executive-level and operational questions
- Any document set where "what does this section say about X?" and "explain the detail of X" are both valid query types

---

## Method 10: Adaptive Chunking

### What problem it solves

A document about Kubernetes might have:
- A dense technical reference section with 50 commands per page
- A narrative introduction explaining the philosophy behind the project

Fixed chunking treats both identically. But the dense technical section needs smaller chunks (one command per chunk for precision), while the narrative introduction can handle larger chunks (the story needs room to breathe).

Adaptive chunking adjusts chunk size based on the local content density.

---

### How it works

```
Analyze each section's properties:
  - vocabulary density (unique words per sentence)
  - sentence complexity (average words per sentence)
  - topic concentration (how many distinct topics per paragraph)

Dense section (high density):
  → Use smaller chunk size (200–300 tokens)
  → Higher precision for technical lookups

Light section (low density):
  → Use larger chunk size (600–800 tokens)
  → Better narrative flow for contextual questions
```

**Example document:**

```
Introduction (light narrative):
  "Kubernetes represents a fundamental shift in how we think about
   application deployment. Rather than treating servers as pets that
   must be individually maintained, Kubernetes encourages us to treat
   infrastructure as cattle..."
  → Adaptive assigns: chunk_size=600

API Reference (dense technical):
  kubectl get pods --namespace=production --selector=app=frontend -o wide
  kubectl describe pod frontend-7d9f8b-xk2j9 --namespace=production
  kubectl logs frontend-7d9f8b-xk2j9 --container=app --tail=100
  ...
  → Adaptive assigns: chunk_size=200
```

### Pros
- Best semantic fit across documents with uneven content density
- No single-size compromise — each section gets what it needs

### Cons
- More complex to implement — requires content analysis layer
- Behavior is harder to predict and reproduce
- Needs careful testing to ensure the density analysis works correctly for your domain

### When to use
- Large enterprise documents that alternate between executive summary and technical detail
- Mixed datasets: blogs + PDFs + technical docs + emails in the same index
- When you have tested fixed and recursive chunking and still see significant quality gaps

---

## Method 11: Code Chunking

### What problem it solves

Code is not prose. A sentence boundary (`". "`) means nothing in Python. A paragraph break means nothing in JavaScript.

Code has its own logical units: functions, classes, methods, import blocks. Splitting at these boundaries preserves the meaning of the code. Splitting mid-function destroys it.

---

### Why generic chunking destroys code

Imagine this Python file chunked at 200 characters:

```python
def calculate_total(items):
    """Calculate total price for all items in cart."""
    total = 0
    for item in items:
```
**Chunk boundary here**
```python
        total += item.price * item.quantity
    return total

def apply_discount(total, discount_percent):
```

**Result:**
```
Chunk 1: "def calculate_total(items):\n    total = 0\n    for item in items:"
Chunk 2: "total += item.price * item.quantity\n    return total\n\ndef apply_discount"
```

Chunk 1 is a broken, incomplete function. It cannot be understood alone.  
Chunk 2 starts mid-indentation. It has no function signature.  
Neither chunk is embeddable in a meaningful way.

A user asking *"How is cart total calculated?"* will get garbage.

---

### Good code chunking: function = chunk

```
Chunk 1:
def calculate_total(items):
    """Calculate total price for all items in cart."""
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total

Chunk 2:
def apply_discount(total, discount_percent):
    """Apply percentage discount to total."""
    return total * (1 - discount_percent / 100)
```

Each chunk is one complete, self-contained function.  
Each chunk answers one clear question: "What does this function do?"  
Docstrings stay with their function — the embedding captures both the name and the description.

---

### Code

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

# Python
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1500,
    chunk_overlap=0   # no overlap — function boundaries are clean
)

# JavaScript / TypeScript
js_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size=1500,
    chunk_overlap=0
)

# Other supported languages:
# Language.JAVA, Language.GO, Language.RUST, Language.CPP,
# Language.RUBY, Language.MARKDOWN, Language.HTML, Language.SOLIDITY

chunks = python_splitter.split_text(python_code)

# Inspect what was created
for i, chunk in enumerate(chunks):
    first_line = chunk.strip().split('\n')[0]
    print(f"Chunk {i+1}: {first_line}")
    # Output: "Chunk 1: def calculate_total(items):"
    #         "Chunk 2: def apply_discount(total, discount_percent):"
```

### Pros
- Functions and classes stay intact — no broken logic
- Docstrings stay with their function — embedding captures intent
- Enables code search by function name, class, or behavior
- No overlap needed — function boundaries are natural and clean

### Cons
- Very long functions (500+ lines) may still need splitting
- Closely coupled functions that call each other may lose context when retrieved separately

### When to use
- Code repositories and codebases
- API documentation with embedded code samples
- Technical manuals that include scripts and configuration examples
- Any document where code is a primary content type

---

## Decision Flowchart — How to Choose Your Method

```
Step 1: Does your data need chunking?
├── NO  → FAQs, product descriptions, pre-structured Q&A
│         Embed directly. No chunking.
└── YES → Continue

Step 2: What type is the content?
├── Source code files            → Method 11: Code Chunking
├── Markdown/HTML with headings  → Method 3: Document-Based
├── Meeting/chat transcript      → Method 4: Sliding Window (high overlap)
├── Very large doc (book/manual) → Method 9: Hierarchical
├── Dense academic/legal prose   → Method 5: Semantic
├── Mixed types in one document  → Method 7: Agentic
├── Cross-reference heavy doc    → Method 8: Late Chunking
├── High-value doc, cost no limit→ Method 6: LLM-Based (Contextual Retrieval)
└── Everything else              → Method 2: Recursive (default)

Step 3: If Recursive is not good enough:
├── Answers too broad/noisy      → Reduce chunk size + add metadata filters
├── Answers incomplete           → Increase chunk size + increase overlap
├── Wrong topic retrieved        → Add metadata filters OR try Semantic
└── Cross-document confusion     → Add metadata filters (doc_type, section)
```

**The 80% rule:** Start with Method 2 (Recursive). It handles most cases well.  
Only move to a specialized method after you have measured that Recursive is producing bad retrieval results.
