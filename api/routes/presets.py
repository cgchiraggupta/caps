"""Preset management routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.preset_store import (
    BUILTIN_CAPTION_PRESETS,
    build_caption_settings,
    get_caption_presets,
    get_preset_choices,
    get_preset_settings,
    load_custom_presets,
    save_custom_presets,
)
from backend.status_messages import render_status
from api.schemas import (
    PresetDeleteResponse,
    PresetSaveRequest,
    PresetSaveResponse,
    PresetSchema,
)

router = APIRouter(prefix="/api/presets", tags=["presets"])


@router.get("", response_model=list[PresetSchema])
async def list_presets():
    """Return all available presets (built-in + user-saved)."""
    presets = get_caption_presets()
    return [
        PresetSchema(name=name, **settings) for name, settings in presets.items()
    ]


@router.get("/choices", response_model=list[str])
async def preset_choices():
    """Return ordered preset names for dropdown."""
    return get_preset_choices()


@router.get("/{preset_name}", response_model=PresetSchema)
async def get_preset(preset_name: str):
    """Get a specific preset's settings."""
    choices = get_preset_choices()
    if preset_name not in choices:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
    presets = get_caption_presets()
    settings = presets[preset_name]
    return PresetSchema(name=preset_name, **settings)


@router.post("", response_model=PresetSaveResponse)
async def save_preset(body: PresetSaveRequest):
    """Save a new user preset."""
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Enter a preset name before saving.")
    if name in BUILTIN_CAPTION_PRESETS:
        raise HTTPException(
            status_code=400,
            detail="Built-in presets are read-only. Save under a new name instead.",
        )

    custom = load_custom_presets()
    custom[name] = build_caption_settings(
        body.format_name,
        body.stream,
        body.style,
        body.max_chars,
        body.min_duration,
        body.gap_frames,
        body.lines,
    )
    save_custom_presets(custom)
    return PresetSaveResponse(
        name=name,
        status_html=render_status(
            f"Saved preset '{name}'.", "success", "Preset saved"
        ),
    )


@router.delete("/{preset_name}", response_model=PresetDeleteResponse)
async def delete_preset(preset_name: str):
    """Delete a user-saved preset."""
    name = (preset_name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Select a preset to delete.")
    if name in BUILTIN_CAPTION_PRESETS:
        raise HTTPException(status_code=400, detail="Built-in presets cannot be deleted.")

    custom = load_custom_presets()
    if name not in custom:
        raise HTTPException(
            status_code=404,
            detail=f"Preset '{name}' was not found.",
        )
    del custom[name]
    save_custom_presets(custom)
    return PresetDeleteResponse(
        name=name,
        status_html=render_status(
            f"Deleted preset '{name}'.", "success", "Preset deleted"
        ),
    )
