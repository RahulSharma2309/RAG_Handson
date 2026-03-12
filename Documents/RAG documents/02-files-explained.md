# File-by-File Explanation (Environment and Setup)

This page explains the important files related to project environment setup.

## Core setup files

| File | Why it exists | Should you edit it? |
|---|---|---|
| `pyproject.toml` | Main project config: project name, Python version requirement, and dependencies managed by `uv`. | Yes, when adding/removing dependencies or metadata. |
| `uv.lock` | Exact locked versions of all direct + transitive dependencies. Ensures reproducible installs. | Usually no manual edits; regenerate via `uv add`, `uv remove`, `uv sync`. |
| `requirement.txt` | Starter dependency list used to bootstrap packages quickly. | Yes, if you still want pip-style dependency file workflow. |
| `.python-version` | Preferred Python version for local tooling (`3.13`). | Rarely; edit only when upgrading/downgrading Python baseline. |
| `.vscode/settings.json` | Workspace editor settings: default interpreter path and local Jupyter server preference. | Yes, for local IDE behavior. |

## Runtime and notebook files

| File | Why it exists | Should you edit it? |
|---|---|---|
| `0-DataIngestParsing/1-DataIngestion.ipynb` | Notebook for ingestion/parsing experiments and learning workflows. | Yes, this is your working notebook. |
| `main.py` | Minimal Python entry point created during initialization. Useful for quick script testing. | Optional; keep or repurpose later. |
| `.venv/` | Local virtual environment containing installed packages and scripts. | No manual edits. Recreate when needed using `uv venv`. |

## Why both `requirement.txt` and `pyproject.toml`?

Both can define dependencies, but they serve different habits:

- `requirement.txt` is simple and common in older workflows.
- `pyproject.toml` + `uv.lock` is modern and reproducible for project-level management.

Current project state uses `pyproject.toml` and `uv.lock` as the primary source of truth, with `requirement.txt` as a convenience starter list.

## Kernel-related config locations (important)

| Location | Purpose |
|---|---|
| `C:\Users\Lenovo\AppData\Roaming\jupyter\kernels\ragudemy\kernel.json` | User-level Jupyter kernel registration used by notebook clients. |
| `.venv\Scripts\python.exe` | Interpreter that must be used by the notebook kernel for project packages. |
| `.vscode/settings.json` | Forces Cursor to prefer project `.venv` interpreter. |

If notebook cells do not execute, these are the first three places to validate.
