@echo off
setlocal

cd /d "%~dp0"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

if exist ".venv\Scripts\python.exe" (
  set "PYTHON_BIN=.venv\Scripts\python.exe"
) else (
  set "PYTHON_BIN=python"
)

echo Starting HinglishCapsV3...
echo App: http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs

"%PYTHON_BIN%" -m uvicorn api.main:app --host 127.0.0.1 --port 8000
