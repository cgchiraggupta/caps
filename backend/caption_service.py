"""Caption generation service — single and batch processing."""

import os
import sys
import tempfile
import zipfile

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import batch  # type: ignore[import-untyped]

from .preset_store import (
    DEFAULT_TRANSCRIPTION_ENGINE_LABEL,
    build_caption_settings,
    resolve_transcription_backend,
)
from .status_messages import render_status


def reserve_output_dir():
    """Create a temp directory that survives long enough for file downloads."""
    return tempfile.mkdtemp(prefix="hinglishcaps_")


def resolve_path(file_value):
    """Extract a local filesystem path from a file value.

    Supports Gradio file objects (name/path attrs), plain strings, and dicts.
    In FastAPI contexts file_value will typically be a string path.
    """
    if isinstance(file_value, str):
        return file_value
    if hasattr(file_value, "name"):
        return file_value.name
    if isinstance(file_value, dict):
        return file_value.get("path") or file_value.get("name")
    raise ValueError("Unsupported uploaded file format")


def build_caption_content(segments):
    """Build the final SRT subtitle content from transcribed segments."""
    return batch.segments_to_srt(segments)


def generate_captions(
    video_path,
    word_level=False,
    transcription_engine=DEFAULT_TRANSCRIPTION_ENGINE_LABEL,
    enable_custom_replacements=False,
    custom_replacements_file="",
    caption_preset="Subtitle default",
    format_name="Subtitle",
    stream="None",
    style="None",
    max_chars=42,
    min_duration=3.0,
    gap_frames=0,
    lines="Double",
    offset_seconds=0.0,
):
    """Generate captions for a single video.

    Returns (output_path_or_None, status_html).
    """
    if not video_path:
        return None, render_status("Please upload a video first.", "warning", "Upload needed")

    try:
        video_path = resolve_path(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        transcription_backend = resolve_transcription_backend(transcription_engine)
        custom_replacements_path = (custom_replacements_file or "").strip() or None

        # Extract audio
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = batch.extract_audio(video_path, tmp)

            # Transcribe
            if word_level:
                settings = build_caption_settings(
                    format_name, stream, style, max_chars, min_duration, gap_frames, lines,
                )
                segments = batch.transcribe_word_level(
                    audio_path,
                    video_path=video_path,
                    caption_settings=settings,
                    transcription_backend=transcription_backend,
                    enable_custom_replacements=enable_custom_replacements,
                    custom_replacements_file=custom_replacements_path,
                )
            else:
                segments = batch.transcribe(
                    audio_path,
                    transcription_backend=transcription_backend,
                    enable_custom_replacements=enable_custom_replacements,
                    custom_replacements_file=custom_replacements_path,
                )

            if not segments:
                return None, render_status("No speech detected in the video.", "warning", "No speech found")

            if abs(offset_seconds) >= 1e-9:
                segments = batch.shift_segments(segments, float(offset_seconds))

            segments = batch.trim_segments_to_duration(
                segments, batch.get_media_duration(video_path)
            )
            if not segments:
                return None, render_status(
                    "No captions remained after trimming to the video duration.",
                    "warning",
                    "Nothing to export",
                )

            # Generate output
            content = build_caption_content(segments)
            filename = f"{video_name}_captions{batch.OUTPUT_EXTENSION}"

            # Save to temp file
            output_dir = reserve_output_dir()
            output_path = os.path.join(output_dir, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            success_message = "Captions generated successfully and ready to download."
            if word_level:
                success_message = (
                    f"Captions generated successfully with preset '{caption_preset}' "
                    f"using {transcription_engine}."
                )
            if enable_custom_replacements:
                success_message += " Custom replacement dictionary: enabled."
            return output_path, render_status(success_message, "success")

    except Exception as e:
        return None, render_status(str(e), "error")


def generate_captions_batch(
    video_files,
    word_level=False,
    transcription_engine=DEFAULT_TRANSCRIPTION_ENGINE_LABEL,
    enable_custom_replacements=False,
    custom_replacements_file="",
    caption_preset="Subtitle default",
    format_name="Subtitle",
    stream="None",
    style="None",
    max_chars=42,
    min_duration=3.0,
    gap_frames=0,
    lines="Double",
    offset_seconds=0.0,
):
    """Generate captions for multiple videos.

    Returns (zip_path_or_None, status_html).
    """
    if not video_files:
        return None, render_status("Please upload video files first.", "warning", "Upload needed")

    try:
        results = []
        failed = []
        transcription_backend = resolve_transcription_backend(transcription_engine)
        custom_replacements_path = (custom_replacements_file or "").strip() or None

        for video_file in video_files:
            video_label = getattr(video_file, "name", None) or str(video_file)
            try:
                video_path = resolve_path(video_file)
                video_label = os.path.basename(video_path)

                # Extract audio
                with tempfile.TemporaryDirectory() as tmp:
                    audio_path = batch.extract_audio(video_path, tmp)

                    # Transcribe
                    if word_level:
                        settings = build_caption_settings(
                            format_name, stream, style, max_chars, min_duration, gap_frames, lines,
                        )
                        segments = batch.transcribe_word_level(
                            audio_path,
                            video_path=video_path,
                            caption_settings=settings,
                            transcription_backend=transcription_backend,
                            enable_custom_replacements=enable_custom_replacements,
                            custom_replacements_file=custom_replacements_path,
                        )
                    else:
                        segments = batch.transcribe(
                            audio_path,
                            transcription_backend=transcription_backend,
                            enable_custom_replacements=enable_custom_replacements,
                            custom_replacements_file=custom_replacements_path,
                        )

                    if not segments:
                        failed.append(f"{video_label}: No speech detected")
                        continue

                    if abs(offset_seconds) >= 1e-9:
                        segments = batch.shift_segments(segments, float(offset_seconds))

                    segments = batch.trim_segments_to_duration(
                        segments, batch.get_media_duration(video_path)
                    )
                    if not segments:
                        failed.append(
                            f"{video_label}: No captions remained after trimming to the video duration"
                        )
                        continue

                    # Generate output
                    video_name = os.path.splitext(os.path.basename(video_path))[0]
                    content = build_caption_content(segments)
                    filename = f"{video_name}_captions{batch.OUTPUT_EXTENSION}"

                    output_dir = reserve_output_dir()
                    output_path = os.path.join(output_dir, filename)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    results.append((output_path, filename))

            except Exception as e:
                failed.append(f"{video_label}: {str(e)}")
                continue

        if not results:
            return None, render_status(f"All videos failed. {', '.join(failed)}", "error")

        # Create ZIP file
        zip_dir = reserve_output_dir()
        zip_path = os.path.join(zip_dir, "hinglishcaps_batch.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path, filename in results:
                zipf.write(file_path, filename)

        status = f"Processed {len(results)} video(s)"
        status += f" using {transcription_engine}"
        if enable_custom_replacements:
            status += " with custom replacements"
        if word_level:
            status += f" with preset '{caption_preset}'"
        if failed:
            status += f", failed {len(failed)}: {', '.join(failed[:3])}"
            if len(failed) > 3:
                status += f"... (and {len(failed) - 3} more)"

        tone = "warning" if failed else "success"
        title = "Processed with warnings" if failed else "Batch complete"
        return zip_path, render_status(status, tone, title)

    except Exception as e:
        return None, render_status(str(e), "error")
