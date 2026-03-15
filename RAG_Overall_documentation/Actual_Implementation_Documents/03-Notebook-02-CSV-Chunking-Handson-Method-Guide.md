# 03 - Notebook 02 Technical Method Guide (`02_csv_chunking_handson.ipynb`)

> This document explains the core methods and building blocks in `Handson/01-Chunking/notebooks/02_csv_chunking_handson.ipynb`. The notebook focuses on structured-data chunking for CSV, where row precision and analytics context need different chunk representations.

---

## Notebook Goal

`02_csv_chunking_handson.ipynb` teaches practical CSV chunking for RAG with two complementary chunk layers:

1. Row-level chunks for exact record lookup
2. Group-summary chunks for comparative and analytical questions

It also covers token checks, metadata strategy, quick retrieval sanity checks, and JSONL export.

---

## Core Building-Block Methods

### 1) `count_tokens(text: str) -> int`

```python
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))
```

**What it does**
- Computes token count per chunk.

**Why it matters**
- CSV summary chunks can become unexpectedly long.
- Token checks prevent silent truncation during embedding.

---

### 2) `stable_chunk_id(text: str, prefix: str) -> str`

```python
def stable_chunk_id(text: str, prefix: str) -> str:
    h = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    return f'{prefix}_{h}'
```

**What it does**
- Generates deterministic IDs from chunk content.

**Why it matters**
- Helps deduplication and re-index stability.
- Useful when re-running chunk pipelines and comparing outputs across runs.

---

### 3) `print_chunk_preview(chunks: list[Document], n: int = 3) -> None`

**What it does**
- Prints chunk content + key metadata + char/token counts for quick inspection.

**Why it matters**
- Fast qualitative QA before indexing.
- Helps spot malformed chunks (wrong field formatting, missing metadata, excessive length).

---

### 4) `build_row_chunks(df, source_name, id_column=None) -> list[Document]`

User-selected example from notebook:

```python
def build_row_chunks(df: pd.DataFrame, source_name: str, id_column: str | None = None) -> list[Document]:
    chunks: list[Document] = []
    total = len(df)

    for row_idx, row in df.iterrows():
        lines = [f'{col}: {row[col]}' for col in df.columns]
        text = '\n'.join(lines)

        primary_id = str(row[id_column]) if id_column and id_column in df.columns else str(row_idx)

        meta = {
            'source': source_name,
            'chunk_type': 'row',
            'row_index': int(row_idx),
            'primary_id': primary_id,
            'total_rows': total,
        }
        meta['chunk_id'] = stable_chunk_id(text, prefix='row')
        meta['char_count'] = len(text)
        meta['token_count'] = count_tokens(text)

        chunks.append(Document(page_content=text, metadata=meta))

    return chunks
```

**What it does**
- Converts each dataframe row into one `Document`.
- Formats each row as `key: value` lines (instead of raw comma text).
- Attaches row-level metadata (`row_index`, `primary_id`, counts).

**Why this is a core method**
- Row chunks are the precision layer for lookup questions:
  - "What is salary of employee E012?"
  - "Which order had issue type 'Defective Item'?"

**Important design choices**
- `id_column` creates human-meaningful identifiers (`employee_id`, `record_id`) instead of only positional index.
- Token/character metadata is attached early so validation is easy later.

---

### 5) `build_group_summary_chunks(...) -> list[Document]`

```python
def build_group_summary_chunks(
    df: pd.DataFrame,
    source_name: str,
    group_by: str,
    include_numeric_stats: bool = True,
) -> list[Document]:
    ...
```

**What it does**
- Creates one summary chunk per group (for example by `department`, `location`, `customer_segment`, `issue_type`).
- Each chunk includes:
  - group identity
  - record count
  - numeric min/max/mean stats
  - sample rows

**Why this is a core method**
- Summary chunks are the analytics layer for questions like:
  - "Average salary by department?"
  - "Which segment gets highest discount?"
  - "How do issue types differ by resolution hours?"

Without this method, row-only chunking is weak for comparative questions.

---

### 6) `summary_splitter = RecursiveCharacterTextSplitter(...)`

```python
summary_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=120,
    separators=['\n\n', '\n', '. ', ' ', '']
)
split_emp_group_chunks = summary_splitter.split_documents(emp_group_by_dept)
```

**What it does**
- Second-pass splitting for large summary chunks.

**Why it matters**
- Group summaries can grow large if groups are big or sample rows are verbose.
- This keeps summaries within safer token windows while preserving readability.

---

### 7) `token_stats(chunks, model_limit=256) -> pd.DataFrame`

```python
def token_stats(chunks: list[Document], model_limit: int = 256) -> pd.DataFrame:
    ...
```

**What it does**
- Builds a dataframe with per-chunk stats:
  - source
  - chunk_type
  - char_count
  - token_count
  - within_limit

**Why it matters**
- Gives an immediate operational dashboard before embedding.
- Makes limit violations explicit and fixable.

---

### 8) `keyword_search(...)` (light sanity retrieval)

```python
def keyword_search(chunks: list[Document], query_terms: list[str], top_n: int = 5) -> list[Document]:
    ...
```

**What it does**
- Basic lexical scoring to quickly validate whether chunk content/metadata design supports expected query terms.

**Why it matters**
- Cheap first-level verification before full semantic retrieval setup.
- Helps catch design issues early (for example field names not represented in text).

---

### 9) `save_jsonl(chunks, path)` (artifact export)

```python
def save_jsonl(chunks: list[Document], path: Path) -> None:
    with path.open('w', encoding='utf-8') as f:
        for c in chunks:
            rec = {'page_content': c.page_content, 'metadata': c.metadata}
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
```

**What it does**
- Saves chunks in JSONL artifact format.

**Why it matters**
- Decouples chunking from indexing.
- Supports reproducibility, versioning, and re-indexing without re-chunking.

---

## Method Flow (How the CSV Notebook Pipeline Works)

1. Load CSV into dataframes.
2. Build row chunks (`build_row_chunks`) for precision retrieval.
3. Build group summary chunks (`build_group_summary_chunks`) for analytical retrieval.
4. Optionally split long summaries recursively.
5. Combine chunk sets.
6. Validate token limits (`token_stats`).
7. Run quick sanity retrieval (`keyword_search`).
8. Export to JSONL (`save_jsonl`) for indexing.

This is a complete structured-data chunking pipeline.

---

## Why This Notebook Is Important

Many RAG tutorials only demonstrate paragraph chunking on text files. Real systems often include CSV/tabular sources, where:

- row chunks alone are not enough
- summaries alone are not enough
- metadata strategy determines whether filtering and diagnostics are possible

This notebook gives the implementation pattern that closes that gap.

---

## Suggested Enhancements (Next Iteration)

1. Add embedding + vector store retrieval notebook (`03_csv_retrieval_handson.ipynb`)
2. Add metadata filters by `chunk_type` (`row` vs `group_summary`)
3. Add unit tests for chunk schema consistency
4. Add chunk dedup validation by `chunk_id`

