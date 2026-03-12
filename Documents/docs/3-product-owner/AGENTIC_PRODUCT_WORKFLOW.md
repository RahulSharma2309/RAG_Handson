# 🤖 Agentic Product Workflow (PM/PO)

This repo already has a detailed engineering roadmap. This document explains how to run **PM/PO planning “agentically”** (with AI agents) while keeping decisions controlled and auditable.

---

## Where Agents Help (High Leverage)

- **Backlog refinement**
  - convert outcome → epics → PBIs with acceptance criteria
- **Documentation upkeep**
  - keep flows and service docs in sync with code changes
- **Risk discovery**
  - identify missing edge cases (validation, security, rollback)
- **Sprint planning support**
  - propose sprint goals and demo scripts mapped to `ITERATION_VIEW_PM_PO.md`

---

## Where Agents Should NOT Decide Alone

- Priority tradeoffs that affect roadmap outcomes
- Security decisions (auth, secrets, threat model)
- Data model decisions with long-term cost (variants/specs schema choices)
- Any decision that changes public API contracts without review

---

## Standard Agent Prompts (Copy/Paste)

### 1) Create/Refine PBIs from a Product Outcome
Use when: PM defines an outcome and PO needs executable backlog items.

Prompt:
“Given this outcome: <text>, propose 5–10 PBIs with acceptance criteria, dependencies, and demo scripts. Map each PBI to the relevant epic in `docs/PROJECT_ROADMAP.md` and to a sprint in `docs/ITERATION_CHECKLIST.md`.”

### 2) Sprint Planning Draft
Use when: preparing sprint planning quickly.

Prompt:
“Propose a sprint goal and a sprint backlog that fits 2 weeks. Include demo script and risks. Reference `docs/product-documents/ITERATION_VIEW_PM_PO.md` and ensure DoD from `docs/product-documents/DEFINITION_OF_DONE.md` is achievable.”

### 3) Release Notes Draft
Use when: end of sprint/release.

Prompt:
“Draft release notes: user-facing changes, known limitations, and what’s next. Keep it readable for non-engineers. Use repo context from docs and the sprint items.”

---

## Guardrails (How PM/PO Keep Control)

- **Every agent output becomes a proposal**, not a decision.
- **PO converts proposals into backlog items** and owns acceptance criteria quality.
- **PM signs off on outcomes and success metrics**.
- **Engineering validates feasibility** and updates estimates.
- **Decisions are recorded** (recommended future doc: `docs/product-documents/DECISION_LOG.md`).

