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
    """Concatenate main video with ending outro, using copy mode or filter fallback."""
    main_path = Path(main_video_path).resolve()
    final_path = Path(output_final_path).resolve()
    final_path.parent.mkdir(parents=True, exist_ok=True)

    actual_outro = Path(outro_path).resolve() if outro_path else DEFAULT_OUTRO_PATH
    if not actual_outro.is_file():
        # Fallback to copy main video directly if outro doesn't exist
        import shutil
        shutil.copy2(str(main_path), str(final_path))
        return final_path

    # Try fast concat demuxer via temporary text file
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_list:
        list_file = Path(f_list.name)
        f_list.write(f"file '{main_path.as_posix()}'\n")
        f_list.write(f"file '{actual_outro.as_posix()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(final_path),
    ]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.CalledProcessError:
        # Re-encode filter fallback if codecs or timebases differ
        cmd_filter = [
            "ffmpeg", "-y",
            "-i", str(main_path),
            "-i", str(actual_outro),
            "-filter_complex",
            "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[v][a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ac", "2",
            "-ar", "44100",
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
    finally:
        if list_file.is_file():
            try:
                list_file.unlink()
            except OSError:
                pass

    return final_path
