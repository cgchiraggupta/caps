"""Job status and download routes."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.jobs import job_manager
from api.schemas import JobStatusResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the current status of a batch job."""
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job.get("progress", 0),
        total=job.get("total", 1),
        result_zip=job.get("result_zip"),
        result_file=job.get("result_file"),
        result_filename=job.get("result_filename"),
        status_html=job.get("status_html"),
        error=job.get("error"),
    )


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Cancel and clean up a job."""
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_manager.cleanup_job(job_id)
    return {"status": "deleted", "job_id": job_id}


DOWNLOAD_ROUTER = APIRouter(prefix="/api/download", tags=["downloads"])


@DOWNLOAD_ROUTER.get("/{job_id}/{filename:path}")
async def download_job_file(job_id: str, filename: str):
    """Download a result file from a completed job."""
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result_path = job.get("result_zip") or job.get("result_file")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file not found")

    is_zip = bool(job.get("result_zip"))
    default_filename = (
        "hinglishcaps_batch.zip"
        if is_zip
        else (job.get("result_filename") or "captions.srt")
    )

    return FileResponse(
        result_path,
        media_type="application/zip" if is_zip else "application/x-subrip",
        filename=default_filename,
    )
