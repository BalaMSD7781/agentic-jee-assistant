@echo off
cd /d "%~dp0"
if exist ".venv-validation\Scripts\python.exe" (
    ".venv-validation\Scripts\python.exe" start_local.py
) else (
    uv run python start_local.py
)
pause
