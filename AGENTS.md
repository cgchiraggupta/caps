# HinglishCapsV3 Smart Safety Rules

Use this file as the migration guardrail for replacing Gradio with a normal FastAPI plus React/Vite app. Preserve behavior first, improve architecture second, and keep every change reviewable.

## Product Contracts
- Single video mode still returns exactly one caption file.
- Batch mode still returns exactly one ZIP file.
- Missing single upload still shows a clear upload-needed validation state.
- Missing batch upload still shows a clear upload-needed validation state.
- Word-level timestamps still reveal preset and caption settings in both modes.
- Custom phrase dictionary still reveals the JSON path input in both modes.
- Preset save, load, delete, and fallback behavior must remain compatible with the current preset JSON format.
- Existing transcription engine labels and backend IDs must remain compatible.
- Existing caption settings must keep the same meanings: format, stream, style, max characters, minimum duration, gap frames, lines, and subtitle offset.

## UI And Design Rules
- Use plain CSS using the existing Pyko tokens and visual language.
- Match `code.html` for colors, spacing, typography, card radius, glass panels, motion, and remote graphics.
- Do not use Gradio for the final UI.
- Do not allow generated framework chrome to appear in the final workflow UI.
- Keep the site light Pyko style unless a design file explicitly changes the direction.
- Use Playfair Display for major brand headings and Inter or the selected interface font for controls.
- Use pill buttons for primary actions and rounded glass cards for grouped controls.
- Make upload, settings, and export areas visually distinct.
- Keep the workflow responsive with no horizontal overflow on desktop or mobile.
- Do not add decorative elements that conflict with `code.html`.

## Backend Safety Rules
- Keep `batch.py` as the transcription source of truth during migration.
- Extract backend logic before deleting Gradio.
- Add tests before moving or rewriting behavior.
- Mock heavy model calls in tests.
- Keep temp file handling explicit and Windows-safe.
- Keep user-facing status messages friendly and specific.
- Do not load transcription models during app import or test import.
- Do not delete the Gradio fallback until FastAPI and React pass parity checks.

## API Rules
- Use FastAPI for the replacement backend.
- Keep API routes under `/api`.
- Use multipart `FormData` for uploads.
- Single caption submission accepts one video file.
- Batch caption submission accepts multiple video files.
- Caption submission returns a job ID.
- Job status returns state, title, message, and optional download URL.
- Download routes must return the final caption file or ZIP without changing output content.

## Frontend Rules
- Use React plus Vite for the replacement frontend.
- Build custom upload controls with normal file inputs.
- Use custom tabs for Single Video and Batch Processing.
- Keep frontend state mapped exactly to backend API field names.
- Poll job status first. Add WebSockets only after the polling version is stable.
- Keep the final user flow simple: upload, settings, generate, status, download.

## Review And Rollout Rules
- Split migration work into small independent tasks.
- Keep each task easy to review and easy to revert.
- Run backend tests after service extraction and API changes.
- Run browser checks after frontend changes.
- Verify desktop and mobile widths before marking UI work complete.
- Remove `gradio` from requirements only after feature parity passes.
- Preserve unrelated dirty git changes.
- Never use destructive git commands unless the user explicitly asks.

## Acceptance Checklist
- `python -m py_compile app_full.py` passes or the new launcher compiles.
- Backend unit tests pass.
- Single missing-upload validation works.
- Batch missing-upload validation works.
- Word-level toggle works in both modes.
- Custom dictionary toggle works in both modes.
- Preset operations work.
- Single download returns one caption file.
- Batch download returns one ZIP file.
- The final UI has no Gradio wrappers visible to the user.
- The final UI visually follows the Pyko reference.
- The app starts from one clear local command.
