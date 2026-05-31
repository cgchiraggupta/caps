"""Caption preset CRUD — built-in + user-saved presets."""

import json
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

PRESET_STORAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "caption_presets.json",
)

CAPTION_FORMAT_OPTIONS = ["Subtitle"]
CAPTION_STREAM_OPTIONS = ["None"]
CAPTION_STYLE_OPTIONS = ["None"]
CAPTION_LINE_OPTIONS = ["Single", "Double"]

TRANSCRIPTION_ENGINE_LABEL_TO_ID = {
    "Whisper Large v3 (Recommended Quality)": "whisper-large-v3",
    "Whisper Large v3 Turbo (Fastest)": "whisper-large-v3-turbo",
    "Whisper Medium (Lighter)": "whisper-medium",
    "Whisper Small (Lightest)": "whisper-small",
    "Whisper Base (Smallest)": "whisper-base",
    "Apex Hinglish (Legacy)": "apex",
}
DEFAULT_TRANSCRIPTION_ENGINE_LABEL = "Whisper Large v3 (Recommended Quality)"

BUILTIN_CAPTION_PRESETS = {
    "Subtitle default": {
        "format_name": "Subtitle",
        "stream": "None",
        "style": "None",
        "max_chars": 42,
        "min_duration": 3.0,
        "gap_frames": 0,
        "lines": "Double",
    },
    "YouTube standard": {
        "format_name": "Subtitle",
        "stream": "None",
        "style": "None",
        "max_chars": 42,
        "min_duration": 2.0,
        "gap_frames": 0,
        "lines": "Double",
    },
    "Shorts single line": {
        "format_name": "Subtitle",
        "stream": "None",
        "style": "None",
        "max_chars": 18,
        "min_duration": 0.8,
        "gap_frames": 1,
        "lines": "Single",
    },
    "Reels punchy": {
        "format_name": "Subtitle",
        "stream": "None",
        "style": "None",
        "max_chars": 14,
        "min_duration": 0.6,
        "gap_frames": 2,
        "lines": "Single",
    },
}


def caption_settings_to_dict(settings):
    """Normalize raw preset values into the backend caption settings shape."""
    try:
        from batch import normalize_caption_settings
    except ImportError:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from batch import normalize_caption_settings  # type: ignore[import-untyped]

    normalized = normalize_caption_settings(settings)
    return {
        "format_name": normalized.format_name,
        "stream": normalized.stream,
        "style": normalized.style,
        "max_chars": normalized.max_chars,
        "min_duration": normalized.min_duration,
        "gap_frames": normalized.gap_frames,
        "lines": normalized.lines,
    }


def load_custom_presets():
    """Read user-saved caption presets from disk."""
    if not os.path.exists(PRESET_STORAGE_PATH):
        return {}

    try:
        with open(PRESET_STORAGE_PATH, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}

    presets = {}
    for name, settings in raw_data.items():
        presets[str(name)] = caption_settings_to_dict(settings)
    return presets


def save_custom_presets(presets):
    """Persist user-saved presets to disk."""
    with open(PRESET_STORAGE_PATH, "w", encoding="utf-8") as handle:
        json.dump(presets, handle, indent=2, ensure_ascii=True)


def get_caption_presets():
    """Return built-in presets plus any user-saved presets."""
    presets = {
        name: caption_settings_to_dict(settings)
        for name, settings in BUILTIN_CAPTION_PRESETS.items()
    }
    presets.update(load_custom_presets())
    return presets


def get_preset_choices():
    """Return preset dropdown choices in stable order."""
    return list(get_caption_presets().keys())


def get_preset_settings(preset_name):
    """Return settings for a preset name, falling back to the default preset."""
    presets = get_caption_presets()
    if preset_name in presets:
        return presets[preset_name]
    return presets["Subtitle default"]


def build_caption_settings(
    format_name,
    stream,
    style,
    max_chars,
    min_duration,
    gap_frames,
    lines,
):
    """Build the caption settings payload passed to the backend."""
    return caption_settings_to_dict(
        {
            "format_name": format_name,
            "stream": stream,
            "style": style,
            "max_chars": max_chars,
            "min_duration": min_duration,
            "gap_frames": gap_frames,
            "lines": lines,
        }
    )


def resolve_transcription_backend(engine_label):
    """Map UI engine label to backend id understood by batch.py."""
    return TRANSCRIPTION_ENGINE_LABEL_TO_ID.get(
        str(engine_label or "").strip(),
        TRANSCRIPTION_ENGINE_LABEL_TO_ID[DEFAULT_TRANSCRIPTION_ENGINE_LABEL],
    )
