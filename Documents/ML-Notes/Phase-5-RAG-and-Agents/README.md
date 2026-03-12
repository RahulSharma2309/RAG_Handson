# Phase 5 — RAG & Agentic AI (Months 7–9)

**Learner:** Rahul Sharma — 10-year distributed systems architect with **FreshHarvest-Market** e-commerce platform.

---

## Phase Overview

**This is where your career multiplies.** You go from understanding AI to building AI-powered products. RAG and Agents are the two most in-demand skills in 2025–2026. Your distributed systems background—APIs, state, orchestration, failure handling—maps directly onto RAG pipelines and agent loops.

| Attribute | Value |
|-----------|--------|
| **Timeline** | Months 7–9 |
| **Primary courses** | Ultimate RAG Bootcamp (Months 7–8); Complete Agentic AI Bootcamp (Month 9) — Krish Naik, Udemy |
| **Prerequisites** | Phase 2 (NLP/transformers intro); comfort with embeddings and LLM APIs |
| **Target outcome** | Ship RAG apps and agentic workflows; connect them to FreshHarvest-Market |

---

## Folder Structure

```
Phase-5-RAG-and-Agents/
├── README.md                      ← You are here
├── 01-Embeddings-and-Vector-DBs/ # Embedding models, indexing, similarity search
├── 02-RAG-Architecture/           # Chunking, retrieval, reranking, generation
├── 03-LangChain-and-Orchestration/ # Chains, LCEL, tool integration
└── 04-Agentic-AI/                # ReAct, planning, memory, tool schemas
```

---

## Courses & Resources

| Course | Role | Timeline | Notes |
|--------|------|----------|-------|
| **Ultimate RAG Bootcamp Using LangChain, LangGraph & LangSmith** | **PRIMARY** | Months 7–8 | Krish Naik, Udemy — RAG foundations, advanced techniques, agentic RAG, LangSmith, cloud deployment |
| **Complete Agentic AI Bootcamp with LangGraph and LangChain** | **PRIMARY** | Month 9 | Krish Naik, Udemy — single agents, multi-agent collaboration, autonomous workflows, state transitions |
| [RAG_Handson Environment Setup Guide](./03-LangChain-and-Orchestration/00-rag-handson-environment-setup-guide.md) | PRACTICAL NOTE | Phase 5 start | Windows + `uv` + Jupyter kernel setup used in this repo |
| [LangChain Documentation](https://python.langchain.com/docs/) | SUPPLEMENTARY | — | Chains, agents, retrievers, integrations |
| [LlamaIndex Documentation](https://docs.llamaindex.ai/) | SUPPLEMENTARY | — | Alternative RAG/retrieval framework |
| [Pinecone Learning Center](https://www.pinecone.io/learn/) | SUPPLEMENTARY | — | Vector DB concepts |
| [Qdrant Documentation](https://qdrant.tech/documentation/) | SUPPLEMENTARY | — | Vector DB with filtering and hybrid search |

---

## Month 7 — RAG Foundations + Advanced Techniques

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **RAG foundations** | Embeddings, vector DBs, chunking strategies; retrieval and generation |
| **2** | **Advanced RAG** | Hybrid search, reranking; multimodal RAG; self-RAG and adaptive RAG patterns |

---

## Month 8 — Agentic RAG + LangSmith

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **Agentic RAG** | Multi-agent RAG with LangGraph; RAG + agent loops |
| **2** | **LangSmith** | Evaluation, debugging, tracing RAG and agent pipelines |
| **3** | **Deployment** | Cloud deployment of RAG and agent services |

---

## Month 9 — Agentic AI

| Week | Focus | Topics |
|------|--------|--------|
| **1** | **Single agents** | ReAct, tool calling, agent loops, error handling |
| **2** | **Multi-agent collaboration** | Multi-agent systems with LangGraph; state transitions; orchestration |
| **3** | **Autonomous workflows** | Planning, reasoning; memory (short-term, long-term); production patterns |
| **4** | **Projects** | Inventory Agent, Dynamic Pricing Agent, Multi-Agent Research Assistant |

---

## Key Deliverables

| Deliverable | Description |
|-------------|-------------|
| **RAG Product Search** | Semantic search over product catalog and docs; embeddings, vector DB, chunking |
| **AI Shopping Assistant** | RAG + conversation memory; answers product and policy questions for FreshHarvest |
| **Multi-Agent Research Assistant** | Multi-agent system (e.g. LangGraph) for research or product comparison |
| **Inventory Agent** | Agent with tools (inventory API, reorder logic); multi-step reasoning for stock and reorders |
| **Dynamic Pricing Agent** | Agent that uses internal data + LLM to support or suggest pricing decisions |

---

## Architecture Connection: How RAG & Agents Power Production Systems

| Use case | RAG / Agent role |
|----------|-------------------|
| **Customer support bots** | RAG over KB + ticket history; agent for escalation and tool use (create ticket, check order) |
| **Internal knowledge bases** | RAG over docs, runbooks, Slack; agents for summarization and action (e.g. Jira, PagerDuty) |
| **Autonomous operations** | Agents that monitor, reason, and act (e.g. inventory reorder, anomaly response) |

Design these like microservices: clear boundaries, idempotency, observability, and fallbacks when the model is uncertain.

---

## Key Concepts to Master

| Concept | Why it matters |
|---------|----------------|
| **Chunking strategies** | Size and overlap affect recall and cost; semantic chunking vs fixed blocks |
| **Hybrid search** | Combine vector similarity with keyword/BM25; better for product IDs and exact terms |
| **Hallucination detection** | Confidence, citations, NLI-based faithfulness checks |
| **Guardrails** | Input/output validation; PII redaction; topic boundaries; use NeMo Guardrails or similar |
| **Agent loops** | Observe → reason → act → observe; design for timeouts and max steps |
| **Tool schemas** | OpenAPI/JSON Schema for tools; LLMs use these for function calling—same idea as API contracts |

---

## Navigation

- **Previous:** [Phase 4 — Transformers & LLMs](../Phase-4-Transformers-and-LLMs/README.md)
- **Next:** [Phase 6 — MLOps & AI Systems Architecture](../Phase-6-MLOps-and-AI-Architecture/README.md)
- **Root:** [ML-Notes](../README.md)
