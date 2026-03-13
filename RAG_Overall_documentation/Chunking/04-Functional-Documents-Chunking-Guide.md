# Functional Documents Chunking Guide

Functional documents include:
- policies
- PRDs
- user flows
- process docs
- business roadmaps
- stakeholder notes

These are usually narrative and rule-driven, so chunking must preserve business meaning.

---

## 1) Functional docs: what to optimize for

- rule completeness (rule + condition + exception)
- workflow continuity (step sequences)
- business context (who/what/when/why)
- traceability (version/effective date/source owner)

---

## 2) Recommended chunk profile

- target size: 450-550 tokens
- max size: 650 tokens
- overlap: 60-90 tokens
- primary split: heading/section-based
- secondary split: paragraph blocks

Why:
- functional answers often need context and policy nuance
- chunks too small lose decision context

---

## 3) Section-aware splitting pattern

Preferred split anchors:
- Scope
- Definitions
- Rules/Policy statements
- Exceptions
- Approval flow
- Responsibilities
- Effective date/version

Do not split in the middle of:
- condition + exception pair
- multi-step decision flow
- eligibility criteria tables

---

## 4) Metadata schema for functional chunks

Minimum metadata:
- `source_file`
- `doc_type` (policy/prd/process)
- `section_title`
- `version`
- `effective_date`
- `owner_team`
- `chunk_index`

Why this matters:
- helps date-aware retrieval ("latest policy")
- helps filter by domain/team
- improves trust via source citation

---

## 5) Example: bad vs good chunking

## Bad chunking
- Chunk 1: "Employees are eligible for leave under conditions..."
- Chunk 2: "Exception: probationary employees are excluded..."

Problem: rule and exception are separated.

## Good chunking
- One chunk includes eligibility rule + exception + applicability date.

Result: retrieval gives complete answer in one shot.

---

## 6) Question patterns functional chunks must support

Your chunks should reliably answer:
- "What is the current policy for X?"
- "Who approves X?"
- "What are the exceptions?"
- "Which version is active?"
- "What changed recently?"

If these fail in top-3 retrieval, retune chunk boundaries and metadata.

---

## 7) Practical tuning tips

- If answers are generic: decrease chunk size slightly
- If answers miss exceptions: increase overlap
- If wrong policy version appears: enforce date/version metadata filter
- If unrelated domain docs appear: add `owner_team` / `doc_type` filters

---

## 8) Functional chunking checklist

- [ ] Rule and exception together
- [ ] Workflow step continuity preserved
- [ ] Version/effective date captured
- [ ] Owner/team metadata present
- [ ] Top-3 retrieval works for policy questions

