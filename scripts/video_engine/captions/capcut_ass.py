"""CapCut-style ASS (Advanced SubStation Alpha) subtitle generator from word_timings.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def _format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp format H:MM:SS.cs."""
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def build_capcut_ass(
    timeline_path: str | Path,
    word_timings_path: str | Path,
    output_ass_path: str | Path,
    *,
    chunk_size: int = 4,
    accent_color_bgr: str = "&H0015CCFA&",  # Warm Yellow (#facc15) in ASS &HAABBGGRR
    inactive_color_bgr: str = "&H00FFFFFF&",  # Crisp White
    outline_color_bgr: str = "&H00000000&",  # Pitch Black
    font_name: str = "Arial Black",
    font_size: int = 56,
) -> Path:
    """Generate a CapCut-style .ass file with dynamic word-by-word active highlighting."""
    timeline = json.loads(Path(timeline_path).read_text(encoding="utf-8"))
    word_timings = json.loads(Path(word_timings_path).read_text(encoding="utf-8"))

    # Map scenes start offset
    scenes = timeline.get("scenes", [])
    scene_offsets = {sc["scene_id"]: sc.get("start", 0.0) for sc in scenes}

    # Collect all words with global timestamps
    global_words = []
    for sc in scenes:
        sid = sc["scene_id"]
        s_offset = scene_offsets.get(sid, 0.0)
        s_words = word_timings.get(sid, [])
        for w in s_words:
            w_text = w.get("text", "").strip().replace("{", "(").replace("}", ")")
            if not w_text:
                continue
            w_start = s_offset + float(w.get("start", 0.0))
            w_end = s_offset + float(w.get("end", w_start + float(w.get("duration", 0.3))))
            global_words.append({
                "word": w_text,
                "start": round(w_start, 3),
                "end": round(w_end, 3),
            })

    # Sort words by start time
    global_words.sort(key=lambda x: x["start"])

    # Chunk words into groups of chunk_size (3-5 words)
    chunks = []
    for i in range(0, len(global_words), chunk_size):
        chunk = global_words[i : i + chunk_size]
        if chunk:
            chunks.append(chunk)

    # Build ASS dialogues
    dialogue_lines = []
    for chunk in chunks:
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]

        # For each word in the chunk, create a dialogue line when that word is active
        for idx, active_word in enumerate(chunk):
            w_start = active_word["start"]
            # The active interval runs until the next word in the chunk starts or the chunk ends
            if idx + 1 < len(chunk):
                w_end = chunk[idx + 1]["start"]
            else:
                w_end = active_word["end"]

            # Ensure positive duration
            if w_end <= w_start:
                w_end = w_start + 0.15

            # Build line text with active word highlighted
            words_formatted = []
            for j, w in enumerate(chunk):
                if j == idx:
                    # Active word in accent color with bold emphasis
                    words_formatted.append(r"{\c" + accent_color_bgr + r"\b1}" + w["word"] + r"{\b0}")
                else:
                    # Inactive word in crisp white
                    words_formatted.append(r"{\c" + inactive_color_bgr + r"}" + w["word"])

            text_rendered = " ".join(words_formatted)
            t_start_str = _format_ass_time(w_start)
            t_end_str = _format_ass_time(w_end)

            dialogue_lines.append(
                f"Dialogue: 0,{t_start_str},{t_end_str},CapCut,,0,0,0,,{text_rendered}"
            )

    ass_content = f"""[Script Info]
Title: EducAI CapCut Dynamic Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CapCut,{font_name},{font_size},{inactive_color_bgr},&H00000000,{outline_color_bgr},&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,100,100,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(dialogue_lines) + "\n"

    out_p = Path(output_ass_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(ass_content, encoding="utf-8")
    return out_p
