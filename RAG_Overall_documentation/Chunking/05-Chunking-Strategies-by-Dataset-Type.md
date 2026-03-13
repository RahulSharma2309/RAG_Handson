# Chunking Strategies by Dataset Type

This file gives practical chunking strategy per dataset family.

---

## 1) CSV and tabular datasets

## Goal
Preserve record-level precision and business context.

## Recommended strategy

Use a two-layer approach:

1. **Row chunks**  
   - one chunk per row for exact lookup
   - include column labels in text body

2. **Grouped summary chunks**  
   - group by meaningful dimensions (category, team, month, status)
   - include aggregate insights

## Why this works
- row chunks support specific questions
- grouped chunks support comparative/analytic questions

## Metadata to include
- source file
- row index / primary key
- table name
- category/group fields
- timestamp/version

## Pitfalls
- only row chunks -> poor answers for summary questions
- only summary chunks -> poor answers for specific item lookup

---

## 2) PDF datasets

## Goal
Handle layout noise while preserving semantic continuity.

## Recommended strategy

1. extract text with page metadata  
2. clean extraction artifacts (line breaks, ligatures, repeated headers)  
3. split by headings/sections if detectable  
4. apply token-aware splitting with overlap

## Suggested defaults
- chunk size: 300-450 tokens
- overlap: 50-80 tokens

## Metadata to include
- source PDF
- page number
- section title (if detected)
- extraction method

## Pitfalls
- chunking raw noisy text without cleaning
- losing page references (hurts trust/citation)
- mixing tables and narrative content into one chunk blindly

---

## 3) Technical documents (architecture/API/runbook)

## Goal
Keep operational dependencies and commands together.

## Recommended strategy

1. split by heading level (`##` or equivalent)
2. keep code blocks/commands with nearest explanatory text
3. split long sections into paragraph or token windows
4. preserve technical identifiers in chunk text

## Suggested defaults
- chunk size: 320-520 tokens
- overlap: 70-100 tokens

## Metadata to include
- service/module name
- section type (setup, troubleshooting, API, architecture)
- environment (dev/staging/prod)

## Pitfalls
- separating command from prerequisites
- separating error message from solution steps
- removing identifiers that users search for

---

## 4) Functional/business documents (policy/PRD/process/user flows)

## Goal
Keep business logic and decision context intact.

## Recommended strategy

1. split by business section (scope, rules, workflow, exceptions)
2. preserve bullet-list continuity
3. keep rule + condition + exception in same chunk when possible
4. use moderate overlap to preserve transitions

## Suggested defaults
- chunk size: 420-620 tokens
- overlap: 60-90 tokens

## Metadata to include
- document type (policy/PRD/roadmap)
- team/department
- effective date/version
- owner/author

## Pitfalls
- splitting rules from exception clauses
- splitting workflow steps in the middle
- omitting version/effective-date metadata

---

## 5) Mixed-source corpus (real enterprise scenario)

Use **profile-based chunking**, not one global config.

Example profiles:
- `functional_docs`: larger narrative chunks
- `technical_docs`: medium chunks with higher overlap
- `operations_docs`: smaller procedural chunks
- `tabular_docs`: row + grouped chunks

This pattern aligns with how your existing RAG notes already separate doc families.

