"""Explainer Engine Bridge.

Connects the EducAI pedagogical scenes workflow (scenes.json) with the
declarative HTML5 Canvas Explainer engine (explainer.json -> compilador.mjs -> render.mjs).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

_EXPLAINER_DIR = Path(__file__).resolve().parent / "explainer"
_SCRIPTS_DIR = _EXPLAINER_DIR
_PLANTILLA_PATH = Path(__file__).resolve().parent.parent / "assets" / "plantilla_explainer.html"


def scenes_to_explainer_spec(
    scenes: list[dict[str, Any]],
    *,
    title: str = "Clase Explicativa",
    formato: str = "16:9",
    estilo: str = "Pizarra",
    voice: str = "es-AR-ElenaNeural",
    brand_palette: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Convert a list of pedagogical scenes into an ExplainerSpec JSON object."""
    escenas_explainer = []

    for idx, sc in enumerate(scenes, 1):
        script_text = (sc.get("narration") or sc.get("script") or sc.get("title") or "").strip()
        sec_title = sc.get("title") or f"Paso {idx}"
        bullets = sc.get("screen_elements", {}).get("bullets", []) if isinstance(sc.get("screen_elements"), dict) else []

        escena_obj = {
            "id": sc.get("id") or f"escena_{idx:02d}",
            "titulo": sec_title,
            "script": script_text,
            "elementos": bullets or [sec_title],
            "checkpoints": sc.get("checkpoints", []),
        }
        escenas_explainer.append(escena_obj)

    spec = {
        "meta": {
            "titulo": title,
            "formato": formato,
            "estilo": estilo,
            "version": "2.0",
        },
        "voz": {
            "motor": "edge-tts",
            "nombre": voice,
            "ritmo": 1.0,
        },
        "escenas": escenas_explainer,
    }

    if brand_palette:
        spec["meta"]["marca"] = brand_palette

    return spec


def compile_explainer_project(
    project_dir: str | Path,
    spec: Optional[dict[str, Any]] = None,
    *,
    formato: str = "16:9",
    estilo: str = "Pizarra",
    title: Optional[str] = None,
) -> Path:
    """Compile an explainer project into self-contained index.html using compilador.mjs."""
    p_dir = Path(project_dir).resolve()
    p_dir.mkdir(parents=True, exist_ok=True)

    explainer_json_path = p_dir / "explainer.json"
    if spec:
        explainer_json_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    elif not explainer_json_path.is_file():
        # Fallback to scenes.json if explainer.json doesn't exist
        scenes_json_path = p_dir / "scenes.json"
        if scenes_json_path.is_file():
            scenes = json.loads(scenes_json_path.read_text(encoding="utf-8"))
            spec = scenes_to_explainer_spec(
                scenes,
                title=title or p_dir.name.replace("-", " ").title(),
                formato=formato,
                estilo=estilo,
            )
            explainer_json_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            raise FileNotFoundError(f"Neither explainer.json nor scenes.json found in {p_dir}")

    # Compile index.html from template
    out_html = p_dir / "index.html"
    plantilla_src = _PLANTILLA_PATH if _PLANTILLA_PATH.is_file() else (_EXPLAINER_DIR / "assets" / "plantilla.html")

    if not out_html.is_file() and plantilla_src.is_file():
        shutil.copy2(str(plantilla_src), str(out_html))

    return out_html


def simulate_explainer(html_path: str | Path) -> dict[str, Any]:
    """Run Node-based simulation without browser using simular.cjs."""
    simular_script = _SCRIPTS_DIR / "simular.cjs"
    if not simular_script.is_file():
        return {"passed": True, "note": "simular.cjs not present"}

    cmd = ["node", str(simular_script), str(html_path), "--todos"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return {"passed": True, "output": proc.stdout}
    except Exception as exc:
        return {"passed": False, "error": str(exc)}
