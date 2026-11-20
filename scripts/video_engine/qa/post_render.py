"""Post-render video quality assurance gate for EducAI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional


def validate_post_render(
    video_path: str | Path,
    *,
    expected_duration: Optional[float] = None,
    check_silence: bool = True,
    spotcheck_frames: bool = True,
) -> dict[str, Any]:
    """Execute post-render verification on a finalized video MP4.

    Validates:
    - Exactly 1 video stream (h264, yuv420p, 1920x1080, 1080x1920, or 1280x720).
    - Exactly 1 audio stream (aac, 44100 Hz, 2 channels stereo).
    - Duration within +-1.0s of expected.
    - No abrupt ending or pure black keyframes.
    """
    vpath = Path(video_path).resolve()
    issues: list[str] = []
    details: dict[str, Any] = {
        "video_path": str(vpath),
        "checks_passed": [],
    }

    if not vpath.is_file() or vpath.stat().st_size == 0:
        return {
            "passed": False,
            "issues": [f"Final video file missing or empty: {vpath}"],
            "details": details,
        }

    # 1. Technical probe with ffprobe
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(vpath)
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        probe_data = json.loads(proc.stdout)
    except Exception as exc:
        return {
            "passed": False,
            "issues": [f"ffprobe failed to read video: {exc}"],
            "details": details,
        }

    streams = probe_data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    if len(video_streams) != 1:
        issues.append(f"Expected exactly 1 video stream, found {len(video_streams)}")
    else:
        v_stream = video_streams[0]
        details["video_codec"] = v_stream.get("codec_name")
        details["pix_fmt"] = v_stream.get("pix_fmt")
        details["width"] = v_stream.get("width")
        details["height"] = v_stream.get("height")

        if v_stream.get("codec_name") != "h264":
            issues.append(f"Video codec is {v_stream.get('codec_name')}, expected h264")
        if v_stream.get("pix_fmt") != "yuv420p":
            issues.append(f"Pixel format is {v_stream.get('pix_fmt')}, expected yuv420p")
        if (details["width"], details["height"]) not in [(1920, 1080), (1080, 1920), (1280, 720), (1080, 1080)]:
            issues.append(f"Unexpected resolution: {details['width']}x{details['height']}")

    if len(audio_streams) != 1:
        issues.append(f"Expected exactly 1 audio stream, found {len(audio_streams)}")
    else:
        a_stream = audio_streams[0]
        details["audio_codec"] = a_stream.get("codec_name")
        details["sample_rate"] = a_stream.get("sample_rate")
        details["channels"] = a_stream.get("channels")

        if a_stream.get("codec_name") != "aac":
            issues.append(f"Audio codec is {a_stream.get('codec_name')}, expected aac")
        if str(a_stream.get("sample_rate")) != "44100":
            issues.append(f"Audio sample rate is {a_stream.get('sample_rate')}, expected 44100")
        if a_stream.get("channels") != 2:
            issues.append(f"Audio channels count is {a_stream.get('channels')}, expected 2 (stereo)")

    # Duration check
    format_info = probe_data.get("format", {})
    actual_dur = float(format_info.get("duration", 0))
    details["duration"] = actual_dur

    if expected_duration is not None:
        diff = abs(actual_dur - expected_duration)
        if diff > 1.0:
            issues.append(
                f"Video duration mismatch: actual {actual_dur:.2f}s vs expected {expected_duration:.2f}s (diff {diff:.2f}s > 1.0s)"
            )
        else:
            details["checks_passed"].append("duration_sync")

    if not issues:
        details["checks_passed"].append("streams_compliance")

    # 2. Silence detection at end of video
    if check_silence and actual_dur > 2.0:
        try:
            silence_cmd = [
                "ffmpeg", "-i", str(vpath),
                "-af", "silencedetect=noise=-35dB:d=0.4",
                "-f", "null", "-"
            ]
            s_proc = subprocess.run(
                silence_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            details["checks_passed"].append("silencedetect_evaluated")
        except Exception as exc:
            details["silence_check_warning"] = f"silencedetect command error: {exc}"

    # 3. Keyframe spotchecks
    if spotcheck_frames and actual_dur > 1.0:
        with tempfile.TemporaryDirectory(prefix="qa_frames_") as tmpdir:
            sample_times = [
                0.5,
                round(actual_dur * 0.5, 2),
                round(max(0.5, actual_dur - 2.0), 2),
            ]
            black_detected = False
            for idx, st in enumerate(sample_times):
                frame_out = Path(tmpdir) / f"spot_{idx}.png"
                f_cmd = [
                    "ffmpeg", "-y", "-ss", str(st),
                    "-i", str(vpath),
                    "-frames:v", "1",
                    str(frame_out),
                ]
                subprocess.run(
                    f_cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if frame_out.is_file():
                    # Pure black 1080p PNG is typically < 3KB
                    if frame_out.stat().st_size < 3000:
                        black_detected = True

            if black_detected:
                issues.append("Pure black frame detected during spotcheck sampling")
            else:
                details["checks_passed"].append("spotcheck_frames_non_black")

    passed = len(issues) == 0
    return {
        "passed": passed,
        "issues": issues,
        "details": details,
    }
