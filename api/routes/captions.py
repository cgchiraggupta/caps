"""Caption generation routes for single video and batch starts."""

from __future__ import annotations

import os
import shutil
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.jobs import job_manager
from api.schemas import JobStartedResponse

router = APIRouter(prefix="/api/captions", tags=["captions"])


@router.post("", response_model=JobStartedResponse)
async def single_caption(
    video: UploadFile = File(...),
    word_level: bool = Form(False),
    transcription_engine: str = Form("Whisper Large v3 (Recommended Quality)"),
    enable_custom_replacements: bool = Form(False),
    custom_replacements_file: str = Form(""),
    caption_preset: str = Form("Subtitle default"),
    format_name: str = Form("Subtitle"),
    stream: str = Form("None"),
    style: str = Form("None"),
    max_chars: int = Form(42),
    min_duration: float = Form(3.0),
    gap_frames: int = Form(0),
    lines: str = Form("Double"),
    offset_seconds: float = Form(-0.18),
):
    """Start a background single-video caption job and return the job_id."""
    temp_dir = tempfile.mkdtemp(prefix="hinglishcaps_uploads_")
    safe_name = os.path.basename(video.filename or "video.mp4") or "video.mp4"
    tmp_path = os.path.join(temp_dir, safe_name)

    try:
        with open(tmp_path, "wb") as handle:
            shutil.copyfileobj(video.file, handle)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Failed to save uploaded file")

    job_id = job_manager.create_job()
    params = {
        "word_level": word_level,
        "transcription_engine": transcription_engine,
        "enable_custom_replacements": enable_custom_replacements,
        "custom_replacements_file": custom_replacements_file,
        "caption_preset": caption_preset,
        "format_name": format_name,
        "stream": stream,
        "style": style,
        "max_chars": max_chars,
        "min_duration": min_duration,
        "gap_frames": gap_frames,
        "lines": lines,
        "offset_seconds": offset_seconds,
    }

    job_manager.start_single_job(job_id, tmp_path, params, upload_dir=temp_dir)
    return JobStartedResponse(job_id=job_id, status="pending")


@router.post("/batch", response_model=JobStartedResponse)
async def start_batch(
    videos: list[UploadFile] = File(...),
    word_level: bool = Form(False),
    transcription_engine: str = Form("Whisper Large v3 (Recommended Quality)"),
    enable_custom_replacements: bool = Form(False),
    custom_replacements_file: str = Form(""),
    caption_preset: str = Form("Subtitle default"),
    format_name: str = Form("Subtitle"),
    stream: str = Form("None"),
    style: str = Form("None"),
    max_chars: int = Form(42),
    min_duration: float = Form(3.0),
    gap_frames: int = Form(0),
    lines: str = Form("Double"),
    offset_seconds: float = Form(-0.18),
):
    """Start a background batch caption job and return the job_id."""
    temp_dir = tempfile.mkdtemp(prefix="hinglishcaps_uploads_")
    saved_paths = []
    try:
        for video in videos:
            safe_name = os.path.basename(video.filename or "video.mp4") or "video.mp4"
            dest = os.path.join(temp_dir, safe_name)
            with open(dest, "wb") as handle:
                shutil.copyfileobj(video.file, handle)
            saved_paths.append(dest)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Failed to save uploaded files")

    job_id = job_manager.create_job()
    params = {
        "word_level": word_level,
        "transcription_engine": transcription_engine,
        "enable_custom_replacements": enable_custom_replacements,
        "custom_replacements_file": custom_replacements_file,
        "caption_preset": caption_preset,
        "format_name": format_name,
        "stream": stream,
        "style": style,
        "max_chars": max_chars,
        "min_duration": min_duration,
        "gap_frames": gap_frames,
        "lines": lines,
        "offset_seconds": offset_seconds,
    }

    job_manager.start_job(job_id, saved_paths, params, upload_dir=temp_dir)
    return JobStartedResponse(job_id=job_id, status="pending")
