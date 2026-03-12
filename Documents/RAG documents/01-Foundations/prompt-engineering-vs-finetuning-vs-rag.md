# Prompt Engineering vs Fine-Tuning vs RAG

> One of the most common questions when starting with AI: "Why do I need RAG? Can't I just use a better prompt? Or train my own model?"
> This document answers that completely. Each approach has a real use case. Knowing when to use which is what separates someone who builds toy demos from someone who builds real systems.

---

## The three approaches at a glance

| | Prompt Engineering | Fine-Tuning | RAG |
|---|---|---|---|
| What you do | Write better instructions to the LLM | Retrain the LLM on your data | Connect the LLM to your documents at query time |
| Technical expertise needed | None | ML/AI expert | Moderate Python |
| Cost | Free | $1,000s of GPU time | Near zero |
| Time to implement | Minutes | Weeks–months | Days–weeks |
| Model changes | No | Yes (permanently) | No |
| Uses your private data | No | Yes (baked in) | Yes (retrieved live) |
| Data stays fresh | N/A | Only until last training | Always |
| Risk of hallucination | High | Low | Low (with grounding) |

---

## Approach 1: Prompt Engineering

### What it is

You take a standard LLM (GPT-4, Llama, Gemini — whatever) and give it specific, structured instructions in the prompt. The model does not change. You change how you ask.

```
Prompt:  "Act as a senior software architect. Provide answers in bullet points.
          Be concise and cite specific design patterns."

User:    "How do I design a scalable API?"

Output:  Structured, professional response using the architect persona
```

### How it works

```
User question
     ↓
You write a clear, structured prompt with context + instructions
     ↓
Existing LLM reads it
     ↓
Output tailored to your instruction style
```

### Pros

- Zero technical expertise needed — just clear English writing
- Instant results — no setup, no infrastructure
- Works with any LLM — OpenAI, Groq, Claude, local Ollama
- No training cost whatsoever

### Cons

- Limited to what the model already knows — you cannot add new knowledge
- Results are inconsistent — change the wording slightly, get a different answer
- Every LLM has a token limit — complex multi-document prompts hit limits quickly
- Cannot use proprietary company data — the model has never seen it

### When to use it

- Quick prototyping or experimentation
- General-purpose tasks (write an email, summarise this text, explain a concept)
- Small applications where generic answers are acceptable
- You need something working today with zero setup

### When NOT to use it

- Your question requires company-specific knowledge
- The answer must come from a specific document or policy
- You need consistent, reliable, auditable answers

---

## Approach 2: Fine-Tuning

### What it is

You take a pre-trained base LLM and retrain it on your own dataset. The model's internal weights (the billions of parameters that define what it knows) get permanently updated. The result is a new, specialised version of the model that "thinks" like your domain.

```
Base LLM (trained on internet) 
     +
Your company's training data (HR policies, legal docs, product manuals)
     ↓
Fine-tuned LLM (thinks like your company's expert)
```

### How it works

```
Prepare domain-specific training data
     ↓
Run fine-tuning process (GPU training job)
     ↓
Model weights permanently modified
     ↓
Deploy specialised model
```

### Pros

- Deeply specialised knowledge — the model learns your exact domain vocabulary, tone, and facts
- Consistent behaviour — trained to respond in exactly the style you want
- No prompt engineering needed at query time — the persona is already baked in
- Can learn new writing styles, communication patterns, domain-specific reasoning

### Cons

- **Expensive** — GPU rental for fine-tuning can cost thousands of dollars
- Requires ML expertise — not a task for a business analyst
- Data goes stale — as soon as your documents update, the model is out of date
- Retraining is required for every update — and each retraining costs money again
- Not suitable for startups or teams without a dedicated AI budget

### When to use it

- You need a very specific behavioural style (e.g. the chatbot must always introduce itself in a specific way)
- High-volume, consistent tasks where accuracy is critical and documents do not change often
- You have legal, medical, or financial content that requires extreme precision
- Large enterprises with dedicated ML teams and GPU budgets

### When NOT to use it

- Your data changes frequently (weekly, monthly)
- You do not have a GPU budget or ML expertise
- You are building a customer support bot for a company whose policies change regularly

---

## Approach 3: RAG (Retrieval-Augmented Generation)

### What it is

You keep using the same base LLM without changing it. Instead, before the LLM answers a question, you first search your documents for the most relevant pieces. Those pieces are handed to the LLM as context in the prompt. The LLM reads them and answers from them — not from its training memory.

```
User question
     ↓
Search your document database for the 3-5 most relevant chunks
     ↓
Add those chunks to the prompt as "context"
     ↓
LLM reads context + question and generates answer
     ↓
Answer cites your actual documents
```

### How it works

Three things happen at query time:

1. **Retrieval** — find relevant documents from your knowledge base (vector search)
2. **Augmentation** — enrich the context with metadata (source file, section, author, date)
3. **Generation** — LLM reads the enriched context and writes the answer

### Pros

- Always up to date — add a new document to your knowledge base, it is immediately searchable
- No training required — no GPU, no ML engineer, no retraining cost
- Cost-effective — pay only for LLM API calls (or run free locally with Ollama)
- Handles private and proprietary data — documents stay in your own systems
- Grounded answers — the LLM is forced to answer from your documents, not from imagination
- Very high accuracy for domain-specific questions when retrieval is tuned well

### Cons

- Requires infrastructure — vector database, embedding model, retrieval pipeline
- Retrieval quality directly affects answer quality — bad chunking = bad answers
- Context window limitation — you can only pass so many chunks before the LLM gets confused
- Slightly more complex to build than prompt engineering

### When to use it

- Customer support chatbots that must answer from your specific policies
- Internal knowledge assistants ("what is our leave policy?", "how do we deploy to production?")
- Any domain where documents change regularly
- Legal, medical, compliance use cases where the answer must be traceable to a specific document
- When you cannot share your data with a cloud AI provider (run everything locally)

---

## The chef analogy — hallucination explained

Imagine a restaurant where the chef is an LLM.

**Scenario 1: A customer from another country orders a dish the chef has never cooked.**

The chef has two choices:
- **Guess** — make something up, present it confidently, and hope it tastes right. The food is terrible because the chef is guessing. This is **hallucination** — the LLM making up a plausible-sounding but wrong answer.
- **Say "I don't know"** — honest, but not helpful.

**Scenario 3: The chef has a recipe library.**

The chef looks up the exact recipe, follows it step by step, and produces a great dish. This is **RAG** — instead of guessing, the system looks up the answer from your actual documents.

The library of recipe books = your vector database. The act of looking up the right recipe = retrieval. The chef reading it and cooking = the LLM generating the answer from context.

---

## Customer support example — the clearest business case

### Without RAG

Customer asks: *"What is your return policy for items bought during the Black Friday sale?"*

LLM answer (generic, hallucinated): *"Generally most companies offer a 30-day return policy, but policies may vary."*

Problems: generic, unhelpful, possibly wrong for your specific company, cannot be trusted.

### With RAG

The same LLM, but now it first searches a vector database containing your actual company policy document.

LLM answer (grounded): *"According to our current policy document (Version 3.2, uploaded November 2024), Black Friday purchases have an extended 60-day return window until 31st January."*

This answer is:
- Specific to your company
- Cites the exact document version
- Trustworthy and auditable
- Would update automatically if you upload a new policy document

---

## Decision framework — which to use?

```
Do you need company-specific answers?
├── No → Prompt Engineering is enough
└── Yes
    ├── Does your data change frequently?
    │   ├── Yes → RAG
    │   └── No
    │       ├── Do you have an ML budget and team?
    │       │   ├── Yes → Fine-Tuning (or Fine-Tuning + RAG together)
    │       │   └── No → RAG
    └── Is accuracy absolutely critical (legal, medical)?
        ├── Yes, and data is static → Fine-Tuning
        └── Yes, but data changes → RAG with careful retrieval tuning
```

---

## Can you combine them?

Yes. In enterprise systems you often see:

**Fine-Tuning + RAG:**
- Fine-tune the LLM to have the right communication style and domain vocabulary
- Use RAG to inject the most current, specific document content at query time
- Result: an LLM that speaks like your expert and answers from your latest documents

**Prompt Engineering + RAG:**
- Use RAG for retrieval
- Use a carefully crafted prompt template to control how the LLM formats its answer
- This is exactly what `ask_rag.py` does in this project

---

## Summary table

| When you should... | Use this |
|---|---|
| Need something working in the next hour | Prompt Engineering |
| Want a chatbot that behaves like a specific persona and data rarely changes | Fine-Tuning |
| Need answers from YOUR documents, that update automatically, with low cost | RAG |
| Need both domain expertise and live document answers | Fine-Tuning + RAG |
| More than 80% of business AI use cases | RAG |
