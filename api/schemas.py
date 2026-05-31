"""Pydantic schemas for the HinglishCaps API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# --- Caption Presets ---

class PresetSchema(BaseModel):
    name: str
    format_name: str = "Subtitle"
    stream: str = "None"
    style: str = "None"
    max_chars: int = 42
    min_duration: float = 3.0
    gap_frames: int = 0
    lines: str = "Double"

    class Config:
        frozen = True


class PresetSaveRequest(BaseModel):
    name: str
    format_name: str = "Subtitle"
    stream: str = "None"
    style: str = "None"
    max_chars: int = 42
    min_duration: float = 3.0
    gap_frames: int = 0
    lines: str = "Double"


class PresetSaveResponse(BaseModel):
    name: str
    status_html: str


class PresetDeleteResponse(BaseModel):
    name: str | None = None
    status_html: str


# --- Caption Requests ---

class CaptionRequest(BaseModel):
    word_level: bool = False
    transcription_engine: str = "Whisper Large v3 (Recommended Quality)"
    enable_custom_replacements: bool = False
    custom_replacements_file: str = ""
    caption_preset: str = "Subtitle default"
    format_name: str = "Subtitle"
    stream: str = "None"
    style: str = "None"
    max_chars: int = 42
    min_duration: float = 3.0
    gap_frames: int = 0
    lines: str = "Double"
    offset_seconds: float = -0.18


class CaptionResponse(BaseModel):
    filename: str
    status_html: str


# --- Batch / Job ---

class BatchJobStartRequest(BaseModel):
    word_level: bool = False
    transcription_engine: str = "Whisper Large v3 (Recommended Quality)"
    enable_custom_replacements: bool = False
    custom_replacements_file: str = ""
    caption_preset: str = "Subtitle default"
    format_name: str = "Subtitle"
    stream: str = "None"
    style: str = "None"
    max_chars: int = 42
    min_duration: float = 3.0
    gap_frames: int = 0
    lines: str = "Double"
    offset_seconds: float = -0.18


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending | running | done | error
    progress: int = 0
    total: int = 1
    result_zip: str | None = None
    result_file: str | None = None
    result_filename: str | None = None
    status_html: str | None = None
    error: str | None = None


class JobStartedResponse(BaseModel):
    job_id: str
    status: str = "pending"
