"""Motion graphics video generator with dynamic scene cards and CapCut-style ASS subtitles."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from scripts.video_engine.captions.capcut_ass import build_capcut_ass


def _clean_text_for_drawtext(text: str) -> str:
    """Clean and escape text for FFmpeg drawtext filter."""
    t = text.replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
    # Remove control characters
    t = re.sub(r"[\r\n\t]+", " ", t).strip()
    return t


def render_motion_graphics_video(
    project_dir: str | Path,
    total_duration: float,
    output_raw: str | Path,
    *,
    captions: bool = True,
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
) -> Path:
    """Render a high-fidelity 1080p motion graphics video with scene cards and CapCut subtitles."""
    p_dir = Path(project_dir).resolve()
    out_file = Path(output_raw).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    timeline_file = p_dir / "audio_timeline.json"
    timeline_data = {}
    if timeline_file.is_file():
        timeline_data = json.loads(timeline_file.read_text(encoding="utf-8"))

    scenes = timeline_data.get("scenes", [])
    total_scenes = len(scenes)

    # Theme palette
    theme_file = p_dir / "theme_config.json"
    bg_color = "0x0F172A"
    card_bg = "0x1E293B"
    accent_color = "0xFACC15"
    primary_color = "0x0284C7"
    text_color = "0xFFFFFF"

    if theme_file.is_file():
        theme_cfg = json.loads(theme_file.read_text(encoding="utf-8"))
        pal = theme_cfg.get("palette", {})
        if pal.get("primary"):
            primary_color = "0x" + pal["primary"].lstrip("#")
        if pal.get("accent"):
            accent_color = "0x" + pal["accent"].lstrip("#")

    # Fonts
    font_bold = "C\\:/Windows/Fonts/arialbd.ttf"
    font_regular = "C\\:/Windows/Fonts/segoeui.ttf"

    # Base filter chain
    vf_filters = []

    # 1. Top banner
    vf_filters.append(f"drawbox=x=0:y=0:w={width}:h=90:color={card_bg}@0.95:t=fill")
    vf_filters.append(
        f"drawtext=fontfile='{font_bold}':text='EducAI · Estudio de Video Determinista':fontcolor=0x94A3B8:fontsize=26:x=80:y=30"
    )

    # 2. Progress bar at bottom
    vf_filters.append(
        f"drawbox=x=0:y={height-10}:w={width}*t/{total_duration:.2f}:h=10:color={accent_color}@1:t=fill"
    )

    # 3. Scene cards
    for idx, sc in enumerate(scenes, 1):
        sc_start = float(sc.get("start", 0.0))
        sc_end = float(sc.get("end", sc_start + float(sc.get("duration", 5.0))))
        enable_expr = f"between(t\\,{sc_start:.2f}\\,{sc_end:.2f})"

        # Main Card Box
        vf_filters.append(
            f"drawbox=x=160:y=150:w=1600:h=600:color={card_bg}@0.92:t=fill:enable='{enable_expr}'"
        )
        vf_filters.append(
            f"drawbox=x=160:y=150:w=1600:h=600:color={primary_color}@0.6:t=3:enable='{enable_expr}'"
        )

        # Stage Badge
        vf_filters.append(
            f"drawbox=x=220:y=200:w=260:h=46:color={primary_color}@1:t=fill:enable='{enable_expr}'"
        )
        vf_filters.append(
            f"drawtext=fontfile='{font_bold}':text='ETAPA {idx} DE {total_scenes}':fontcolor=white:fontsize=22:x=240:y=212:enable='{enable_expr}'"
        )

        # Title
        raw_title = sc.get("title", f"Escena {idx}")
        clean_title = _clean_text_for_drawtext(raw_title)
        vf_filters.append(
            f"drawtext=fontfile='{font_bold}':text='{clean_title}':fontcolor={text_color}:fontsize=46:x=220:y=280:enable='{enable_expr}'"
        )

        # Bullets or description
        screen_elem = sc.get("screen_elements", {})
        bullets = screen_elem.get("bullets", [])
        if not bullets and sc.get("voiceover_script"):
            # Break voiceover into 2-3 readable summary phrases
            words = sc["voiceover_script"].split()
            chunk_len = 12
            bullets = [" ".join(words[i : i + chunk_len]) for i in range(0, min(len(words), chunk_len * 3), chunk_len)]

        y_offset = 360
        for b_idx, bullet in enumerate(bullets[:3]):
            clean_b = _clean_text_for_drawtext(bullet)
            if len(clean_b) > 85:
                clean_b = clean_b[:82] + "..."
            vf_filters.append(
                f"drawtext=fontfile='{font_regular}':text='• {clean_b}':fontcolor=0xE2E8F0:fontsize=30:x=230:y={y_offset}:enable='{enable_expr}'"
            )
            y_offset += 65

    # 4. Burn CapCut-style ASS Subtitles if enabled
    words_file = p_dir / "word_timings.json"
    if captions and words_file.is_file():
        ass_file = p_dir / "captions.ass"
        build_capcut_ass(timeline_file, words_file, ass_file)
        ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
        vf_filters.append(f"ass='{ass_escaped}'")

    vf_string = ",".join(vf_filters)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s={width}x{height}:d={total_duration:.2f}:r={fps}",
        "-vf", vf_string,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        str(out_file),
    ]

    print(f"[VideoRender] Rendering motion graphics video ({total_duration:.2f}s, {fps}fps)...")
    subprocess.run(cmd, capture_output=True, check=True)
    return out_file
