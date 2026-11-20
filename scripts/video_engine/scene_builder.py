"""Scene generation, brand theming, and SCORM checkpoint alignment for EducAI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.video_engine.parsers.brand_theme import extract_brand_theme
from scripts.video_engine.parsers.doc_parser import parse_document


def build_scenes_from_document(
    doc_path: str | Path,
    brand_theme: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Parse a PPTX, DOCX, or PDF document and map it into structured EducAI scenes."""
    doc_data = parse_document(str(doc_path))
    sections = doc_data.get("sections", [])

    scenes: list[dict[str, Any]] = []
    for idx, sec in enumerate(sections, 1):
        sid = f"scene_{idx:02d}"
        title = sec.get("title") or f"Escena {idx}"
        paragraphs = sec.get("paragraphs") or []
        bullets = sec.get("bullets") or []

        # Script creation: prefer paragraphs or bullets, or fallback to title
        if paragraphs:
            voiceover_script = " ".join(paragraphs)
        elif bullets:
            voiceover_script = f"{title}. " + ". ".join(bullets)
        else:
            voiceover_script = title

        # Build basic screen elements
        screen_elements = {
            "title": title,
            "bullets": bullets or paragraphs[:3],
            "visual_concept": f"Visual conceptual layout for {title}",
        }

        # Checkpoint placeholder
        cp = {
            "checkpoint_id": f"cp_{idx:02d}",
            "question": f"¿Cuál es el concepto clave discutido en '{title}'?",
            "options": [
                f"Definición fundamental de {title}",
                "Un aspecto secundario",
                "Información no relacionada",
            ],
            "correct_index": 0,
            "explanation": f"Se repasa el núcleo temático abordado en {title}.",
        }

        scene_obj = {
            "id": sid,
            "title": title,
            "narration": voiceover_script,
            "screen_elements": screen_elements,
            "checkpoints": [cp],
        }
        scenes.append(scene_obj)

    return scenes


def align_checkpoints_to_timeline(
    raw_checkpoints: list[dict[str, Any]],
    timeline_scenes: list[dict[str, Any]],
    tolerance_buffer: float = 0.08,
) -> list[dict[str, Any]]:
    """Align evaluative checkpoints to scene end timestamps strictly obeying Invariant 1."""
    aligned: list[dict[str, Any]] = []
    scenes_by_id = {s["scene_id"]: s for s in timeline_scenes}
    scenes_list = list(timeline_scenes)

    for idx, cp in enumerate(raw_checkpoints):
        target_sid = cp.get("scene_id")
        target_scene = None
        if target_sid and target_sid in scenes_by_id:
            target_scene = scenes_by_id[target_sid]
        elif idx < len(scenes_list):
            target_scene = scenes_list[idx]

        if target_scene:
            # End of speech plus small buffer
            sc_end = float(target_scene.get("end", 0.0))
            aligned_ts = round(sc_end + tolerance_buffer, 2)
        else:
            aligned_ts = float(cp.get("timestamp", 0.0))

        aligned_cp = dict(cp)
        aligned_cp["timestamp"] = aligned_ts
        aligned_cp.setdefault("scene_id", target_scene.get("scene_id") if target_scene else None)
        aligned.append(aligned_cp)

    return aligned


def generate_style_artifacts(brand_theme: dict[str, Any]) -> tuple[str, str]:
    """Generate CSS root variables and DESIGN.md from brand theme palette."""
    palette = brand_theme.get("palette", {})
    primary = palette.get("primary", "#0284c7")
    secondary = palette.get("secondary", "#0369a1")
    accent = palette.get("accent", "#facc15")
    bg = palette.get("background", "#0f172a")
    surface = palette.get("surface", "#1e293b")
    text = palette.get("text", "#f8fafc")
    text_muted = palette.get("text_muted", "#94a3b8")

    css_root = f""":root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-accent: {accent};
  --color-bg: {bg};
  --color-surface: {surface};
  --color-text: {text};
  --color-text-muted: {text_muted};
}}"""

    design_md = f"""# Design System & Palette · EducAI

## Colors
- **Primary:** `{primary}`
- **Secondary:** `{secondary}`
- **Accent:** `{accent}`
- **Background:** `{bg}`
- **Surface:** `{surface}`
- **Text:** `{text}`
- **Text Muted:** `{text_muted}`

## Typography
- **Headings:** Bold / ExtraBold (Segoe UI / Arial Black)
- **Body:** Regular / SemiBold
- **Subtitles:** CapCut-style active word highlighting
"""

    return css_root, design_md
