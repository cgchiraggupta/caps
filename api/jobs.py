"""Background job manager for caption processing."""

from __future__ import annotations

import os
import shutil
import tempfile
import threading
import zipfile
import uuid

from backend.caption_service import generate_captions, generate_captions_batch


class JobManager:
    """In-memory job tracker for batch caption tasks."""

    def __init__(self):
        self._lock = threading.Lock()
        self._jobs: dict[str, dict] = {}

    def create_job(self) -> str:
        """Create a new job and return its id."""
        job_id = uuid.uuid4().hex[:12]
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "pending",
                "progress": 0,
                "total": 0,
                "result_zip": None,
                "result_file": None,
                "result_filename": None,
                "status_html": None,
                "error": None,
            }
        return job_id

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(kwargs)

    def start_single_job(
        self,
        job_id: str,
        video_path: str,
        params: dict,
        upload_dir: str | None = None,
    ):
        """Run single-video caption generation in a background thread."""
        self.update_job(job_id, status="running", total=1)

        def _run():
            try:
                output_path, status_html = generate_captions(
                    video_path=video_path,
                    word_level=params.get("word_level", False),
                    transcription_engine=params.get(
                        "transcription_engine", "Whisper Large v3 (Recommended Quality)"
                    ),
                    enable_custom_replacements=params.get("enable_custom_replacements", False),
                    custom_replacements_file=params.get("custom_replacements_file", ""),
                    caption_preset=params.get("caption_preset", "Subtitle default"),
                    format_name=params.get("format_name", "Subtitle"),
                    stream=params.get("stream", "None"),
                    style=params.get("style", "None"),
                    max_chars=params.get("max_chars", 42),
                    min_duration=params.get("min_duration", 3.0),
                    gap_frames=params.get("gap_frames", 0),
                    lines=params.get("lines", "Double"),
                    offset_seconds=params.get("offset_seconds", -0.18),
                )

                if output_path and os.path.exists(output_path):
                    self.update_job(
                        job_id,
                        status="done",
                        result_file=output_path,
                        result_filename=os.path.basename(output_path),
                        status_html=status_html,
                        progress=1,
                    )
                else:
                    self.update_job(
                        job_id,
                        status="error",
                        status_html=status_html,
                        error="Caption generation produced no output",
                        progress=1,
                    )
            except Exception as e:
                self.update_job(
                    job_id,
                    status="error",
                    error=str(e),
                    status_html=f'<div class="status-shell"><div class="status-card status-error"><div class="status-title">Error</div><div class="status-message">{e}</div></div></div>',
                )
            finally:
                if upload_dir:
                    shutil.rmtree(upload_dir, ignore_errors=True)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def start_job(
        self,
        job_id: str,
        video_paths: list[str],
        params: dict,
        upload_dir: str | None = None,
    ):
        """Run batch caption generation in a background thread."""
        total = len(video_paths)
        self.update_job(job_id, status="running", total=total)

        def _run():
            temp_dir = tempfile.mkdtemp(prefix="hinglishcaps_batch_")
            try:
                saved_paths = []
                try:
                    for src_path in video_paths:
                        dest = os.path.join(temp_dir, os.path.basename(src_path))
                        shutil.copy2(src_path, dest)
                        saved_paths.append(dest)

                    # Use a wrapper to track progress
                    class ProgressTracker:
                        def __init__(self, jm, jid, total_count):
                            self.jm = jm
                            self.jid = jid
                            self.total = total_count
                            self.done = 0

                        def __iter__(self):
                            return self

                        def __next__(self):
                            raise StopIteration

                    tracker = ProgressTracker(self, job_id, total)

                    # Build file objects compatible with generate_captions_batch
                    # generate_captions_batch expects file objects with .name
                    file_objs = []
                    for p in saved_paths:
                        class _FakeFile:
                            name = p
                        file_objs.append(_FakeFile())

                    zip_path, status_html = generate_captions_batch(
                        video_files=file_objs,
                        word_level=params.get("word_level", False),
                        transcription_engine=params.get(
                            "transcription_engine", "Whisper Large v3 (Recommended Quality)"
                        ),
                        enable_custom_replacements=params.get("enable_custom_replacements", False),
                        custom_replacements_file=params.get("custom_replacements_file", ""),
                        caption_preset=params.get("caption_preset", "Subtitle default"),
                        format_name=params.get("format_name", "Subtitle"),
                        stream=params.get("stream", "None"),
                        style=params.get("style", "None"),
                        max_chars=params.get("max_chars", 42),
                        min_duration=params.get("min_duration", 3.0),
                        gap_frames=params.get("gap_frames", 0),
                        lines=params.get("lines", "Double"),
                        offset_seconds=params.get("offset_seconds", -0.18),
                    )

                    if zip_path and os.path.exists(zip_path):
                        self.update_job(
                            job_id,
                            status="done",
                            result_zip=zip_path,
                            status_html=status_html,
                            progress=total,
                        )
                    else:
                        self.update_job(
                            job_id,
                            status="error",
                            status_html=status_html,
                            error="Batch processing produced no output",
                            progress=total,
                        )

                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if upload_dir:
                        shutil.rmtree(upload_dir, ignore_errors=True)

            except Exception as e:
                self.update_job(
                    job_id,
                    status="error",
                    error=str(e),
                    status_html=f'<div class="status-shell"><div class="status-card status-error"><div class="status-title">Error</div><div class="status-message">{e}</div></div></div>',
                )

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def cleanup_job(self, job_id: str):
        """Remove job data and cleanup its temp files."""
        job = self.get_job(job_id)
        if job and job.get("result_zip"):
            zip_dir = os.path.dirname(job["result_zip"])
            shutil.rmtree(zip_dir, ignore_errors=True)
        if job and job.get("result_file"):
            file_dir = os.path.dirname(job["result_file"])
            shutil.rmtree(file_dir, ignore_errors=True)
        with self._lock:
            self._jobs.pop(job_id, None)


# Singleton
job_manager = JobManager()
