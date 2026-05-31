# Gradio Removal Migration Plan

## Summary
Replace Gradio with a normal web app architecture: **FastAPI backend + React/Vite frontend**. Preserve the existing transcription backend, preset logic, file outputs, and UI behavior. Execute the migration in independent tasks so each task can be reviewed, tested, and reverted safely.

## Target Architecture
- Backend: FastAPI serves API routes, upload handling, job status, and downloads.
- Frontend: React/Vite renders the Pyko-style website and workflow UI.
- Core transcription: existing `batch.py` remains the source of truth.
- Compatibility: `app_full.py` becomes the new FastAPI launcher at the end.
- Final dependency state: `gradio` removed from `requirements_full.txt`.

## Task Sequence

### Task 1: Add Backend Contract Tests Before Moving Code
**Goal:** Capture current behavior before removing Gradio.

**Files modified:**
- `tests/test_caption_contract.py`
- `tests/test_preset_contract.py`
- `tests/conftest.py`

**Work:**
- Test missing single upload returns the current warning message.
- Test missing batch upload returns the current warning message.
- Test preset load, save, delete, and fallback behavior.
- Test caption settings normalization.
- Mock heavy transcription calls so tests stay fast.

**Architectural risks:**
- Current logic lives inside `app_full.py`, so importing it may also import UI code.
- Tests must mock transcription and model loading to avoid slow runs.

---

### Task 2: Extract Pure Backend Services From `app_full.py`
**Goal:** Separate business logic from UI without changing behavior.

**Files modified:**
- `backend/caption_service.py`
- `backend/preset_store.py`
- `backend/status_messages.py`
- `app_full.py`

**Work:**
- Move preset functions into `backend/preset_store.py`.
- Move caption generation orchestration into `backend/caption_service.py`.
- Move `render_status` message data into `backend/status_messages.py`.
- Keep Gradio UI temporarily calling the extracted functions.
- Keep `batch.py` unchanged.

**Architectural risks:**
- Function signatures must stay compatible with the current Gradio event bindings.
- File path handling must preserve Gradio and future FastAPI upload formats during transition.

---

### Task 3: Create FastAPI Backend Shell
**Goal:** Add a new backend beside the Gradio app.

**Files modified:**
- `api/main.py`
- `api/schemas.py`
- `api/routes/presets.py`
- `api/routes/captions.py`
- `api/routes/downloads.py`
- `requirements_full.txt`

**Work:**
- Add `fastapi`, `uvicorn`, `python-multipart`, and `pydantic`.
- Add `GET /api/health`.
- Add preset routes:
  - `GET /api/presets`
  - `POST /api/presets`
  - `DELETE /api/presets/{name}`
- Add caption routes:
  - `POST /api/captions/single`
  - `POST /api/captions/batch`
- Add download route:
  - `GET /api/downloads/{file_id}`

**Architectural risks:**
- Upload files need explicit temp-file lifecycle handling.
- API schemas must match frontend needs without leaking internal Python objects.

---

### Task 4: Add Job Queue and Status Layer
**Goal:** Prevent long transcription requests from blocking the browser.

**Files modified:**
- `api/jobs.py`
- `api/routes/jobs.py`
- `api/routes/captions.py`

**Work:**
- Add in-memory job registry for local use.
- Return `{ "job_id": "..." }` from single and batch caption routes.
- Add `GET /api/jobs/{job_id}`.
- Track states: `queued`, `running`, `success`, `error`.
- Return user-facing messages and download URLs through job status.

**Architectural risks:**
- In-memory jobs disappear when the server restarts.
- Parallel jobs can compete for RAM during model inference.
- Later production use may need SQLite or a real queue.

---

### Task 5: Build React/Vite Frontend From `code.html`
**Goal:** Replace Gradio-rendered UI with real frontend components.

**Files modified:**
- `frontend/package.json`
- `frontend/index.html`
- `frontend/src/App.tsx`
- `frontend/src/api.ts`
- `frontend/src/styles/pyko.css`
- `frontend/src/components/*`

**Work:**
- Recreate nav, hero, capability cards, testimonials, workflow, and footer.
- Use the same image URLs and visual language from `code.html`.
- Build custom upload controls using normal file inputs.
- Build custom tabs for Single and Batch flows.
- Build custom toggles for word-level timestamps and custom dictionary.
- Build preset controls and settings panels.
- Remove all Gradio DOM from the frontend.

**Architectural risks:**
- React state must map exactly to the backend settings payload.
- Upload UI must support large files without freezing the page.
- Visual parity needs browser screenshot review.

---

### Task 6: Wire Frontend to FastAPI
**Goal:** Connect the new UI to the backend safely.

**Files modified:**
- `frontend/src/api.ts`
- `frontend/src/App.tsx`
- `frontend/src/components/workflow/*`

**Work:**
- Single mode sends `FormData` to `/api/captions/single`.
- Batch mode sends multiple files to `/api/captions/batch`.
- Preset dropdown loads from `/api/presets`.
- Save and delete preset buttons call preset endpoints.
- Generate buttons poll `/api/jobs/{job_id}` until completion.
- Download buttons use `/api/downloads/{file_id}`.

**Architectural risks:**
- Field names must match FastAPI route expectations exactly.
- Polling intervals need a sane default to avoid UI spam.
- Error messages must stay friendly and specific.

---

### Task 7: Serve Frontend Through FastAPI
**Goal:** Make one normal local app command run the full website.

**Files modified:**
- `api/main.py`
- `frontend/vite.config.ts`
- `app_full.py`
- `README.md`

**Work:**
- Configure Vite build output.
- Serve built frontend assets from FastAPI.
- Keep API routes under `/api`.
- Replace `app_full.py` with a FastAPI launcher.
- Keep the local run command simple:
  - `python app_full.py`

**Architectural risks:**
- Static asset paths must work on Windows.
- Dev mode and production build mode need clear commands.
- Existing users may still expect the old Gradio port behavior.

---

### Task 8: Remove Gradio Completely
**Goal:** Finish the migration after parity passes.

**Files modified:**
- `requirements_full.txt`
- `app_full.py`
- `README.md`

**Work:**
- Remove `gradio==6.10.0`.
- Remove all `import gradio as gr`.
- Remove Gradio UI construction.
- Remove Gradio-specific CSS.
- Keep `batch.py` and extracted backend services.
- Update docs with FastAPI and frontend commands.

**Architectural risks:**
- This task should run only after FastAPI and React pass parity tests.
- Removing Gradio too early would remove the fallback UI.

## API Contract Defaults
- `POST /api/captions/single` accepts one video file and caption settings.
- `POST /api/captions/batch` accepts multiple video files and caption settings.
- Both caption routes return `{ "job_id": string }`.
- `GET /api/jobs/{job_id}` returns status, title, message, and optional download URL.
- Single success returns one caption file.
- Batch success returns one ZIP file.
- Preset JSON format stays compatible with the current app.

## Test Plan
- Run backend unit tests after Tasks 1 to 4.
- Run frontend component tests after Tasks 5 and 6.
- Run Playwright checks for desktop and mobile after Task 6.
- Verify missing upload validation in Single and Batch modes.
- Verify word-level toggle reveals preset and caption settings.
- Verify custom dictionary toggle reveals JSON path input.
- Verify preset save, delete, load, and fallback behavior.
- Verify single caption download.
- Verify batch ZIP download.
- Verify `python app_full.py` starts the final app.

## Assumptions
- FastAPI + React/Vite is the chosen replacement for Gradio.
- `batch.py` remains the core transcription engine.
- The current caption output contract stays unchanged.
- Local-first usage stays the priority.
- In-memory jobs are acceptable for the first migration.
- SQLite or a real job queue can come later.

## Confidence And Learning Notes
Confidence: 99%

1. Based on what I know about you, your main gap is planning a rewrite as independent migration slices instead of one large replacement.
2. You should learn next how API contracts protect a frontend rewrite from breaking backend behavior.
