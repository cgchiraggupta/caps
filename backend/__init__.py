"""HinglishCaps backend — caption generation, preset management, status messages."""

from .caption_service import (
    build_caption_content,
    generate_captions,
    generate_captions_batch,
    reserve_output_dir,
    resolve_path,
)
from .preset_store import (
    CAPTION_FORMAT_OPTIONS,
    CAPTION_LINE_OPTIONS,
    CAPTION_STREAM_OPTIONS,
    CAPTION_STYLE_OPTIONS,
    DEFAULT_TRANSCRIPTION_ENGINE_LABEL,
    TRANSCRIPTION_ENGINE_LABEL_TO_ID,
    build_caption_settings,
    caption_settings_to_dict,
    get_caption_presets,
    get_preset_choices,
    get_preset_settings,
    load_custom_presets,
    resolve_transcription_backend,
    save_custom_presets,
)
from .status_messages import render_status

__all__ = [
    "CAPTION_FORMAT_OPTIONS",
    "CAPTION_LINE_OPTIONS",
    "CAPTION_STREAM_OPTIONS",
    "CAPTION_STYLE_OPTIONS",
    "DEFAULT_TRANSCRIPTION_ENGINE_LABEL",
    "TRANSCRIPTION_ENGINE_LABEL_TO_ID",
    "build_caption_content",
    "build_caption_settings",
    "caption_settings_to_dict",
    "generate_captions",
    "generate_captions_batch",
    "get_caption_presets",
    "get_preset_choices",
    "get_preset_settings",
    "load_custom_presets",
    "render_status",
    "reserve_output_dir",
    "resolve_path",
    "resolve_transcription_backend",
    "save_custom_presets",
]
