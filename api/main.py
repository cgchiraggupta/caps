"""FastAPI application entry point for HinglishCaps."""

from __future__ import annotations

import os
import shutil
import tempfile

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.jobs import job_manager
from api.routes.captions import router as captions_router
from api.routes.jobs import DOWNLOAD_ROUTER, router as jobs_router
from api.routes.presets import router as presets_router

app = FastAPI(
    title="HinglishCaps",
    description="Video caption generation API",
    version="1.0.0",
)

# CORS — allow the Vite dev server and production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(captions_router)
app.include_router(jobs_router)
app.include_router(DOWNLOAD_ROUTER)
app.include_router(presets_router)


@app.on_event("startup")
async def startup():
    """Clean up any stale temp dirs on startup."""
    temp_dir = tempfile.gettempdir()
    for item in os.listdir(temp_dir):
        if item.startswith("hinglishcaps_"):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                pass


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve built frontend last so API routes always take priority.
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
