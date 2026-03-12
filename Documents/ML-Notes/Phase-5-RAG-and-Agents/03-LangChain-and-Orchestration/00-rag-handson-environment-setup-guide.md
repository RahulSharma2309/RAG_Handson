# RAG_Handson Environment Setup Guide (Windows + uv)

This note is the ML-Notes landing page for the practical environment setup used in the `RAG_Handson` project.

## Why this note exists

In Phase 5, reproducible local setup is critical before building retrieval pipelines, chains, and agents.  
This document points to the full beginner-friendly setup docs created in the project itself.

## Project docs location

- `RAG_Handson/doc/README.md`
- `RAG_Handson/doc/01-environment-setup-windows-uv.md`
- `RAG_Handson/doc/02-files-explained.md`
- `RAG_Handson/doc/03-jupyter-kernel-troubleshooting.md`

## What is covered there

- What `uv` is and why it is used
- Virtual environment setup (`.venv`)
- Dependency installation (`pyproject.toml`, `uv.lock`, `requirement.txt`)
- Jupyter kernel registration and selection
- Kernel execution troubleshooting and stable `ipykernel` version choice
- File-by-file explanation of environment and notebook setup

## Recommended workflow for new contributors

1. Read the docs in `RAG_Handson/doc`.
2. Follow setup commands in order.
3. Verify notebook kernel with a small test cell.
4. Start Phase-5 practical notebooks and projects.
