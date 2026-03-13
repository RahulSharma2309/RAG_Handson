# Technical Documents Chunking Guide

Technical documents include:
- architecture docs
- API references
- service-level design docs
- deployment guides
- CI/CD docs
- troubleshooting runbooks

These documents are dependency-heavy and often procedural.

---

## 1) Technical docs: what to optimize for

- preserve dependency chains (prerequisite -> command -> output -> fix)
- keep commands/code with explanation
- support high-precision lookup by identifiers
- avoid splitting diagnostic context

---

## 2) Recommended chunk profile

- target size: 340-480 tokens
- max size: 550 tokens
- overlap: 70-110 tokens
- primary split: heading-based
- secondary split: paragraph/code-block aware

Why:
- technical questions are narrow and precise
- moderate size improves precision while keeping enough context

---

## 3) Technical boundary rules

Do keep together:
- command + required flags
- error message + remediation steps
- API endpoint + auth + response caveats
- architecture component + interactions

Do not split:
- in the middle of YAML/JSON blocks
- in the middle of stack traces
- in the middle of step-by-step deployment procedure

---

## 4) Metadata schema for technical chunks

Minimum metadata:
- `source_file`
- `system_area` (api/deployment/ci-cd/troubleshooting)
- `service_name`
- `environment` (local/dev/staging/prod)
- `section_title`
- `contains_code` (true/false)
- `chunk_index`

This enables high-signal filtering and better debugging.

---

## 5) API docs chunking pattern

Best pattern:
- Endpoint overview chunk
- Request schema chunk
- Response schema chunk
- Error handling chunk
- Auth/permissions chunk

Avoid one giant chunk for entire API page.

---

## 6) Runbook/troubleshooting chunking pattern

Best pattern:
- symptom chunk
- likely causes chunk
- resolution steps chunk
- verification steps chunk
- rollback/safety notes chunk

This structure improves answer reliability during incidents.

---

## 7) Tuning symptoms and fixes

- If retrieval returns broad architecture text for specific CLI question:
  - reduce chunk size
  - improve `system_area` metadata

- If answers miss prerequisites:
  - increase overlap
  - keep heading + first command block together

- If wrong environment instructions appear:
  - add environment metadata filters

---

## 8) Technical chunking checklist

- [ ] commands are not detached from context
- [ ] errors and fixes are in same neighborhood
- [ ] environment metadata exists
- [ ] service/module metadata exists
- [ ] API sections are split semantically, not blindly

