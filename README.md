# HinglishCapsV3

HinglishCapsV3 is a FastAPI plus React caption studio for generating Hinglish subtitle files from videos. It keeps the proven Whisper caption pipeline from the earlier project and serves a custom Pyko-styled dashboard without Gradio UI wrappers.

## What It Does

- Generates one `.srt` caption file for a single video.
- Generates one `.zip` file for batch video processing.
- Supports Whisper Large v3 and Whisper Large v3 Turbo engine choices.
- Uses word-level timestamps, readable chunking, line-length limits, minimum duration rules, and subtitle offset controls.
- Supports optional custom phrase replacement dictionaries.
- Serves the built React frontend from FastAPI at `http://127.0.0.1:8000`.

## Project Structure

```text
api/                       FastAPI app, routes, schemas, job manager
backend/                   Caption service wrapper, presets, status messages
frontend/                  React and Vite frontend
frontend/dist/             Built frontend served by FastAPI
batch.py                   Main transcription and caption pipeline
forced_align_worker.py     Isolated WhisperX alignment worker
requirements_full.txt      Full runtime dependency set
requirements_align.txt     Optional isolated forced-alignment dependencies
start.bat                  Windows startup script
start.sh                   Bash startup script
```

## Quick Start On Windows

```powershell
cd "C:\path\to\HinglishCapsV3"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements_full.txt
.\start.bat
```

Open `http://127.0.0.1:8000`.

## Optional Forced Alignment Runtime

Forced alignment can run in a separate environment so the main app stays stable.

```powershell
py -3.12 -m venv .venv-align
.\.venv-align\Scripts\python.exe -m pip install --upgrade pip
.\.venv-align\Scripts\python.exe -m pip install -r requirements_align.txt
```

The app prefers healthy same-pass Whisper word timings for speed. Set this only when you want to force the older WhisperX alignment path:

```powershell
$env:HINGLISHCAPS_PREFER_SAME_PASS_TIMING="0"
```

## Frontend Development

```powershell
cd frontend
npm install
npm run dev
```

To rebuild the production frontend:

```powershell
cd frontend
npm run build
```

## Launch Command

```powershell
.\start.bat
```

For Bash:

```bash
bash start.sh
```

## Safety Contracts

- Single video mode returns one caption file.
- Batch mode returns one ZIP file.
- Downloaded single captions keep the `.srt` extension.
- Caption chunking respects max characters per line in double-line mode.
- Caption timing rules apply universally across single and batch workflows.
- Local virtual environments, installed node modules, videos, and generated subtitle outputs stay out of Git.
