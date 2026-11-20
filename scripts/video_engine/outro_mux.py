"""Multiplexing and outro concatenation with audio normalization for EducAI."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DEFAULT_OUTRO_PATH = _ASSETS_DIR / "ending. educai.mp4"


def mux_audio_video(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    *,
    force_stereo: bool = True,
) -> Path:
    """Mux video and audio into a single MP4, enforcing AAC 44.1kHz stereo audio."""
    v_path = Path(video_path).resolve()
    a_path = Path(audio_path).resolve()
    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(v_path),
        "-i", str(a_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
    ]
    if force_stereo:
        cmd.extend(["-ac", "2", "-ar", "44100"])

    cmd.extend(["-shortest", str(out_path)])

    subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return out_path


def concat_with_outro(
    main_video_path: str | Path,
    output_final_path: str | Path,
    outro_path: Optional[str | Path] = None,
) -> Path:
    """Concatenate main video with ending outro, normalizing resolution and audio rate."""
    main_path = Path(main_video_path).resolve()
    final_path = Path(output_final_path).resolve()
    final_path.parent.mkdir(parents=True, exist_ok=True)

    actual_outro = Path(outro_path).resolve() if outro_path else DEFAULT_OUTRO_PATH
    if not actual_outro.is_file():
        # Fallback to copy main video directly if outro doesn't exist
        import shutil
        shutil.copy2(str(main_path), str(final_path))
        return final_path

    # Normalize streams: scale outro to 1080p and resample audio to 44.1kHz stereo to avoid clock drift
    cmd_filter = [
        "ffmpeg", "-y",
        "-i", str(main_path),
        "-i", str(actual_outro),
        "-filter_complex",
        "[0:v]setsar=1[v0];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
        "[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];"
        "[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(final_path),
    ]

    subprocess.run(
        cmd_filter,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return final_path
