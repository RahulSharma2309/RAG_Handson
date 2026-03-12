# Environment Setup (Windows + uv)

This document explains the exact setup flow used in this project.

## 1) What is `uv`?

`uv` is a fast Python package and project manager from Astral.

It can:
- create and manage virtual environments,
- install dependencies,
- manage `pyproject.toml` + `uv.lock`,
- run Python tools with better speed than traditional `pip` workflows.

Think of it as a modern replacement for "pip + venv + pip-tools" for many projects.

## 2) Prerequisites

- Windows with PowerShell
- Python installed (project currently uses Python 3.13)
- Project path: `C:\Users\Lenovo\source\repos\AIML\RAG_Handson`

## 3) Install `uv`

PowerShell command:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 4) Initialize project (already done here)

```powershell
uv init
```

This creates base project metadata (including `pyproject.toml`).

## 5) Create virtual environment

```powershell
uv venv
```

This creates `.venv` in project root.

Activate it:

```powershell
.venv\Scripts\activate
```

## 6) Install dependencies

From requirements file:

```powershell
uv add -r requirement.txt
```

Also install Jupyter kernel package:

```powershell
uv add "ipykernel<7"
```

Why `<7`?
- In this setup, notebook execution became more stable with `ipykernel 6.x`.

## 7) Register Jupyter kernel

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name ragudemy --display-name "Rag Kernel (.venv)"
```

Check installed kernels:

```powershell
.\.venv\Scripts\python.exe -m jupyter kernelspec list
```

## 8) Configure Cursor/VS Code workspace

File: `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true,
  "jupyter.jupyterServerType": "local"
}
```

This ensures notebooks and terminal use the local `.venv`.

## 9) Verify notebook execution

Test cell:

```python
import sys
print("OK")
print(sys.executable)
```

Success means:
- cell shows execution count like `[1]`,
- output prints `.venv\Scripts\python.exe`.

## 10) If kernel still does not run

1. `Ctrl + Shift + P` -> `Developer: Reload Window`
2. Re-select kernel (`Rag Kernel (.venv)` or `.venv` Python interpreter)
3. Restart notebook kernel once
4. Run test cell again

For deeper debugging, see `03-jupyter-kernel-troubleshooting.md`.
