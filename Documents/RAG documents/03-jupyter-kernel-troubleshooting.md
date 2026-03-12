# Jupyter Kernel Troubleshooting (RAGUdemy / Rag Kernel)

This document captures the exact issue and fix from this setup session.

## Problem observed

- Kernel was not visible initially in notebook kernel picker.
- After selection, notebook cells stayed in `[]` or appeared stuck and did not execute.

## What was already correct

- `.venv` was created successfully.
- Dependencies were installed with `uv`.
- `ipykernel` was installed.
- Kernel was registered and visible in Jupyter kernel list.

## Root causes (practical)

1. Cursor workspace was not consistently bound to the project interpreter.
2. Kernel runtime compatibility was unstable with `ipykernel 7.2.0` in this environment.

## Fix applied

### A) Pin workspace interpreter

Created/updated `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true,
  "jupyter.jupyterServerType": "local"
}
```

### B) Re-register kernel

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name ragudemy --display-name "Rag Kernel (.venv)"
```

### C) Use stable ipykernel major version

```powershell
uv add "ipykernel<7"
```

This installed `ipykernel 6.31.0` and reduced startup issues.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m jupyter kernelspec list
.\.venv\Scripts\python.exe -c "import ipykernel; print(ipykernel.__version__)"
```

Expected:
- `ragudemy` appears in kernel list,
- `ipykernel` version is `6.x`.

## Final checks inside notebook UI

1. `Ctrl + Shift + P` -> `Developer: Reload Window`
2. Open notebook
3. `Select Kernel` -> choose `Rag Kernel (.venv)` or project `.venv` interpreter
4. Restart kernel once
5. Run:

```python
import sys
print("OK")
print(sys.executable)
```

If it prints the `.venv` path, setup is correct.

## If issue happens again later

- Recreate environment:
  - delete `.venv`
  - run `uv venv`
  - run `uv sync` (or `uv add -r requirement.txt`)
  - reinstall kernel command above
- Reload Cursor window and reselect kernel.
