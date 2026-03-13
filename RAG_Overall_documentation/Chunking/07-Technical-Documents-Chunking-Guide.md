# Technical Documents Chunking Guide

> Technical documents — architecture designs, API references, deployment guides, runbooks, CI/CD documentation — have one failure mode that is categorically worse than most: they guide people through operational actions. When a runbook is chunked incorrectly, the user gets an incomplete command, a missing prerequisite, or a wrong environment instruction. In a production incident, that is not just a bad answer — it is an answer that can cause downtime. This guide explains exactly how to chunk technical documents so that retrieval is operationally safe.

---

## What Counts as a Technical Document

Technical documents include:
- **Architecture design docs** — system components, data flows, decision rationale
- **API references** — endpoints, request/response schemas, authentication, error codes
- **Deployment guides** — environment setup, infrastructure provisioning, service startup
- **Runbooks** — incident response procedures, operational step-by-step guides
- **Troubleshooting guides** — symptoms, root causes, resolution steps, rollback procedures
- **CI/CD documentation** — pipeline stages, environment variables, deployment triggers
- **Configuration references** — environment settings, flags, service parameters

What they all share: **information is bound to dependencies.** A command depends on its prerequisites. An error code depends on its resolution steps. An API endpoint depends on its authentication context. Separate any of these and the retrieved answer becomes operationally unsafe.

---

## The Core Problem: Dependency Chain Separation

The most dangerous chunking failure in technical documents is splitting a prerequisite from its dependent command.

### A real runbook — deployment rollback procedure

```
## Production Rollback — API Server

### Prerequisites (verify before proceeding)

Before executing any rollback command, confirm ALL of the following:

1. Database snapshot `snap-prod-2024-0315-api` is available and healthy
   Verify: aws rds describe-db-snapshots --db-snapshot-identifier snap-prod-2024-0315-api
   Expected: Status = "available"

2. Minimum 2 healthy nodes remain in the cluster
   Verify: kubectl get nodes
   Expected: STATUS = "Ready" for at least 2 nodes

3. Rollback has been approved by the on-call engineer
   Required: Approval logged in incident ticket #INC-XXXXX

4. Confirm current revision number
   Run: kubectl rollout history deployment/api-server
   Note the revision you are rolling back FROM

### Rollback Command

kubectl rollout undo deployment/api-server --to-revision=3

### Post-Rollback Verification

Wait 90 seconds then verify:
kubectl get pods -l app=api-server
Expected: All pods STATUS = "Running"

Check health endpoint:
curl https://api.prod.internal/health
Expected: {"status": "ok", "version": "3.2.1"}
```

---

### Case 1 — Bad chunking (RecursiveCharacterTextSplitter, 300 tokens, no structure awareness)

```
Chunk 1 (284 chars):
"Before executing any rollback command, confirm ALL of the following:
1. Database snapshot snap-prod-2024-0315-api is available and healthy
   Verify: aws rds describe-db-snapshots --db-snapshot-identifier snap-prod-2024-0315-api"

Chunk 2 (302 chars):
"Expected: Status = "available"
2. Minimum 2 healthy nodes remain in the cluster
   Verify: kubectl get nodes
   Expected: STATUS = "Ready" for at least 2 nodes
3. Rollback has been approved by the on-call engineer"

Chunk 3 (289 chars):
"Required: Approval logged in incident ticket #INC-XXXXX
4. Confirm current revision number
   Run: kubectl rollout history deployment/api-server
   Note the revision you are rolling back FROM

Rollback Command:
kubectl rollout undo deployment/api-server --to-revision=3"

Chunk 4 (201 chars):
"Post-Rollback Verification:
kubectl get pods -l app=api-server
Expected: All pods STATUS = "Running"
curl https://api.prod.internal/health
Expected: {"status": "ok", "version": "3.2.1"}"
```

**User query (during a production incident):** "How do I rollback the API server deployment?"

The retriever finds the highest similarity match. The query contains "rollback" and "deployment" — Chunk 3 has both. The retriever returns Chunk 3.

The on-call engineer reads Chunk 3:
- They see the rollback command ✅
- They do NOT see: verify the database snapshot ❌
- They do NOT see: verify healthy node count ❌
- They do NOT see: confirm on-call approval ❌

**Engineer executes the rollback command without verifying the database snapshot.**

The snapshot was actually in a degraded state. The rollback runs but data consistency is compromised. The incident escalates from a service restart to a partial data loss event.

❌ The chunking directly caused an escalated incident.

---

### Case 2 — Good chunking (section-first, 600 tokens, code-block aware)

```
Chunk 1 — entire section as one unit:

## Production Rollback — API Server
### Prerequisites (verify before proceeding)
Before executing any rollback command, confirm ALL of the following:
1. Database snapshot snap-prod-2024-0315-api is available...
   Verify: aws rds describe-db-snapshots...
2. Minimum 2 healthy nodes remain in the cluster...
   Verify: kubectl get nodes
3. Rollback has been approved by the on-call engineer...
4. Confirm current revision number...
   Run: kubectl rollout history deployment/api-server

### Rollback Command
kubectl rollout undo deployment/api-server --to-revision=3

### Post-Rollback Verification
kubectl get pods -l app=api-server
curl https://api.prod.internal/health

Metadata: {section_title: "Production Rollback — API Server", system_area: "deployment", environment: "production", contains_code: true}
```

**User query:** "How do I rollback the API server deployment?"

The retriever returns this complete chunk.

The on-call engineer reads it:
- They see the prerequisites ✅
- They verify the snapshot before proceeding ✅
- They verify healthy nodes ✅
- They execute the command safely ✅
- They know how to verify the result ✅

✅ Complete answer. Operationally safe.

---

## The Five Dependency Patterns That Must Stay Together

These are the structural patterns that chunking must preserve in technical documents:

### 1 — Prerequisite and Command

```
❌ SPLIT:
Chunk A: "Before running the database migration, ensure the primary replica is healthy
          and the replica lag is below 100ms."
Chunk B: "Run migration: python manage.py migrate --database=primary --noinput"

✅ TOGETHER:
Full prerequisite check + migration command in one chunk.
```

### 2 — Command and Expected Output

```
❌ SPLIT:
Chunk A: "Check cluster node status: kubectl get nodes"
Chunk B: "Expected output: all nodes should show STATUS=Ready. If any node shows
          NotReady, do not proceed with deployment."

✅ TOGETHER:
Command + expected output + action if output is wrong in one chunk.
```

### 3 — Error and Resolution

```
❌ SPLIT:
Chunk A: "Common error: CrashLoopBackOff on api-server pod."
Chunk B: "This error occurs when the pod cannot access the database secret. Resolution:
          kubectl describe pod <pod-name> to identify the missing secret.
          kubectl create secret generic db-secret --from-literal=password=..."

✅ TOGETHER:
Error symptom + root cause + resolution steps in one chunk.
The user asking "what does CrashLoopBackOff mean and how do I fix it?" needs all of this in one retrieved result.
```

### 4 — API Endpoint and Its Requirements

```
❌ SPLIT:
Chunk A: "POST /api/v1/deployments — Creates a new deployment job."
Chunk B: "Authentication: Requires Bearer token with scope deploy:write.
          Rate limit: 10 requests per minute per user.
          Request body: {service: string, version: string, environment: string}"

✅ TOGETHER:
Endpoint + auth + rate limit + schema in one chunk.
A developer asking "how do I call the deployments API?" needs all of this, not just the endpoint.
```

### 5 — YAML/JSON Blocks and Their Context

```
❌ SPLIT:
Chunk A: "Apply this Kubernetes deployment configuration:"
Chunk B: "apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server"
Chunk C: "  template:
    spec:
      containers:
      - name: api-server
        image: company/api-server:3.2.1
        ports:
        - containerPort: 8080"

✅ TOGETHER:
Introduction + complete YAML block in one chunk.
A split YAML block is broken YAML — it means nothing when retrieved in isolation.
```

---

## Recommended Chunking Profile for Technical Documents

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

technical_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # moderate — most runbook sections fit within 500 chars
    chunk_overlap=90,     # 18% overlap — ensures command context bleeds into next chunk
    separators=[
        "\n## ",          # H2 heading — primary section boundary
        "\n### ",         # H3 subheading — secondary boundary
        "\n```",          # code block boundary — keep code blocks intact
        "\n\n",           # paragraph break
        "\n",             # line break
        " ",              # word boundary
        ""                # character (emergency fallback)
    ]
)
```

### Why `"\n```"` is critical

Without `"\n```"` in the separators, a 40-line YAML block might get split in the middle:

```yaml
# This YAML gets cut — Chunk 1 ends here:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
```

```yaml
# Chunk 2 starts here — orphaned YAML fragment:
  selector:
    matchLabels:
      app: api-server
  template:
    spec:
```

Neither chunk is valid YAML. Neither will embed correctly. Neither will be retrieved when a user asks about the deployment configuration.

With `"\n```"` as a separator, the splitter treats code block boundaries as split points — the complete code block stays together within a chunk.

### When chunks still exceed size with code blocks

Sometimes a code block alone exceeds your `chunk_size`. In this case, accept the large chunk rather than splitting it:

```python
technical_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=90,
    separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""],
    keep_separator=True    # preserve the separator at chunk boundaries
)
```

For very long code blocks (100+ lines), create a dedicated code chunk with a label:

```python
from langchain_core.documents import Document

def create_code_chunk(code: str, language: str, context: str, metadata: dict) -> Document:
    """Create a chunk for a standalone code block with context label."""
    content = f"Code ({language}):\nContext: {context}\n\n```{language}\n{code}\n```"
    return Document(page_content=content, metadata={**metadata, "contains_code": True, "code_language": language})
```

---

## API Documentation — Chunking by Endpoint

API documentation should not be chunked by character count. It should be chunked by endpoint and concern.

### The wrong approach — one giant chunk per page

A full API endpoint page might look like this in a documentation portal:

```
POST /api/v1/orders

Creates a new order in the order management system.

Authentication: Bearer token required, scope: orders:write

Rate Limit: 100 requests per minute per API key

Request Headers:
  Content-Type: application/json
  Authorization: Bearer <token>

Request Body:
{
  "product_id": "string (required)",
  "quantity": "integer (required, min: 1, max: 1000)",
  "customer_id": "string (required)",
  "shipping_address": {
    "street": "string",
    "city": "string",
    "country": "string (ISO 3166-1 alpha-2)"
  },
  "priority": "standard | express | overnight"
}

Response 200 OK:
{"order_id": "string", "status": "pending", "estimated_delivery": "ISO date"}

Response 400 Bad Request:
{"error": "invalid_product_id", "message": "Product not found"}
{"error": "quantity_exceeds_stock", "message": "Available: X units"}

Response 401 Unauthorized:
{"error": "invalid_token", "message": "Token expired or invalid"}

Response 429 Too Many Requests:
{"error": "rate_limit_exceeded", "retry_after": "integer (seconds)"}
```

If you chunk this entire page as one unit, the chunk is too large and semantically diffuse. The embedding will try to represent authentication, request format, error codes, and rate limiting all at once — and will not retrieve precisely for any of them.

### The right approach — chunking by concern

```
Endpoint Overview Chunk:
POST /api/v1/orders — Create Order
Creates a new order in the order management system.
Authentication: Bearer token required, scope: orders:write
Rate Limit: 100 requests per minute per API key
Content-Type: application/json
Metadata: {endpoint: "POST /api/v1/orders", concern: "overview", service: "orders-api"}

Request Schema Chunk:
POST /api/v1/orders — Request Body
{
  "product_id": "string (required)",
  "quantity": "integer (required, min: 1, max: 1000)",
  "customer_id": "string (required)",
  "shipping_address": { street, city, country (ISO 3166-1) },
  "priority": "standard | express | overnight"
}
Metadata: {endpoint: "POST /api/v1/orders", concern: "request_schema", service: "orders-api"}

Response Schema Chunk:
POST /api/v1/orders — Response Codes
200 OK: {"order_id": "string", "status": "pending", "estimated_delivery": "ISO date"}
400: invalid_product_id, quantity_exceeds_stock
401: invalid_token (expired or invalid)
429: rate_limit_exceeded with retry_after seconds
Metadata: {endpoint: "POST /api/v1/orders", concern: "responses_and_errors", service: "orders-api"}
```

Now:
- "How do I authenticate the orders API?" → retrieves Overview chunk ✅
- "What fields are required to create an order?" → retrieves Request Schema chunk ✅
- "What does a 429 error mean on the orders API?" → retrieves Response chunk ✅

---

## Runbook Chunking Pattern — Structured Section Layout

For runbooks and troubleshooting guides, each operational section should be one chunk with this structure preserved:

```
[Section: Symptom]
    What the user observes and what metrics/alerts indicate this issue

[Section: Root Causes]
    Ordered list of likely causes with probability or frequency

[Section: Diagnostic Steps]
    Commands to run to identify the specific cause

[Section: Resolution Steps]
    Step-by-step fix for each possible root cause

[Section: Verification]
    Commands and expected outputs to confirm resolution

[Section: Escalation]
    When to escalate and to whom, with contact information
```

Each of these sections can be its own chunk if the runbook is large. But **Diagnostic Steps + Resolution Steps + Verification must always stay in the same chunk** or overlapping chunks — because a user executing a resolution needs to know if it worked.

---

## Metadata Schema for Technical Document Chunks

```python
{
    # Source identification
    "source": "runbooks/api-server-rollback.md",
    "doc_type": "runbook",              # runbook | architecture | api_reference | deployment_guide | ci_cd

    # Operational context
    "system_area": "deployment",        # deployment | troubleshooting | api | ci_cd | architecture
    "service_name": "api-server",       # which service this applies to
    "environment": "production",        # local | dev | staging | production | all

    # Section context
    "section_title": "Production Rollback — API Server",
    "section_type": "procedure",        # procedure | reference | overview | error_handling

    # Content flags
    "contains_code": True,              # boolean — contains code blocks
    "code_language": "bash",            # if contains_code: what language

    # Position
    "chunk_index": 4,
    "total_chunks": 16,
    "doc_family": "technical"
}
```

### Why `environment` metadata is critical

Many technical documents cover multiple environments. Without environment metadata, a query like "how do I deploy the service?" might retrieve a staging deployment guide when the user needs the production one.

**With metadata filter at retrieval:**
```python
# Only retrieve production runbooks
retriever.search(
    query="how do I rollback the api server?",
    filter={"environment": "production"}
)
```

This is only possible if `environment` is in the metadata. Without it, you have no way to prevent cross-environment confusion in retrieved results.

---

## End-to-End Example: Processing a Technical Document

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_technical_document(
    file_path: str,
    doc_type: str,
    service_name: str,
    environment: str,
    system_area: str
) -> list:
    """
    Load and chunk a technical document with full operational metadata.
    """
    loader = TextLoader(file_path, encoding="utf-8")
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=90,
        separators=["\n## ", "\n### ", "\n```", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(raw_docs)

    total = len(chunks)
    for i, chunk in enumerate(chunks):
        first_line = chunk.page_content.strip().split("\n")[0]
        section = first_line.replace("## ", "").replace("### ", "").strip() \
                  if first_line.startswith("#") else "Body"

        chunk.metadata.update({
            "doc_type": doc_type,
            "service_name": service_name,
            "environment": environment,
            "system_area": system_area,
            "section_title": section,
            "contains_code": "```" in chunk.page_content,
            "chunk_index": i,
            "total_chunks": total,
            "doc_family": "technical",
            "char_count": len(chunk.page_content)
        })

    return chunks

# Usage
chunks = process_technical_document(
    file_path="runbooks/api-server-rollback.md",
    doc_type="runbook",
    service_name="api-server",
    environment="production",
    system_area="deployment"
)

print(f"Total chunks: {len(chunks)}")
for chunk in chunks[:4]:
    code_flag = "⚙️ " if chunk.metadata["contains_code"] else "   "
    print(f"  {code_flag}[{chunk.metadata['section_title']}] {chunk.metadata['char_count']} chars")
```

**Expected output:**
```
Total chunks: 11
  ⚙️ [Production Rollback — API Server] 587 chars
     [Prerequisites (verify before proceeding)] 498 chars
  ⚙️ [Rollback Command] 164 chars
  ⚙️ [Post-Rollback Verification] 203 chars
```

---

## Practical Tuning Guide for Technical Documents

### Symptom: Generic architecture text retrieved for specific CLI question

**Cause:** Architecture overview and CLI reference are in the same chunks. The embedding mixes broad and narrow content.  
**Fix:** Reduce `chunk_size` to 350–400. Use `system_area` metadata ("api", "cli", "architecture") and filter at retrieval.

---

### Symptom: Commands appear without prerequisites in retrieved results

**Cause:** Chunk overlap is insufficient. Prerequisites are in the previous chunk with no bleedover.  
**Fix:** Increase `chunk_overlap` to 120–140. Or restructure the document to always place prerequisites within the same `##` section as the commands.

---

### Symptom: Wrong environment instructions appear (dev instead of prod)

**Cause:** No `environment` metadata filtering at retrieval.  
**Fix:** Add `environment` field to all chunks. Apply metadata filter at query time.

---

### Symptom: YAML/JSON config blocks are split and broken

**Cause:** `"\n```"` is not in the separator list. The splitter treats code blocks as regular text.  
**Fix:** Add `"\n```"` as a separator with high priority (before `"\n\n"`).

---

## Technical Documentation Checklist

Before indexing technical document chunks, verify:

- [ ] Every `##` section heading is a chunk boundary
- [ ] No code block is split mid-content
- [ ] Every command has its prerequisite context reachable (same chunk or high overlap)
- [ ] Error codes are in the same chunk as their resolution steps
- [ ] `environment` metadata is set correctly (production vs staging vs local)
- [ ] `service_name` metadata is set for all service-specific docs
- [ ] `contains_code: true` flag is set for chunks with code blocks
- [ ] API endpoint chunks are split by concern (overview, request, response)
- [ ] Runbook symptom + diagnosis + resolution are in adjacent or overlapping chunks
- [ ] Top-3 retrieval for a sample incident query returns the right runbook section
