"""Unified EducAI Video Studio Orchestrator.

Orchestrates end-to-end video production for Moodle and LMS courses:
Document Ingestion -> Scriptwriting -> Voice & Timings -> Pre-Render QA ->
Multi-Engine Rendering -> Audio Mux & Outro -> Post-Render QA -> Interactive SCORM 1.2 Packaging.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path for direct CLI execution
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from typing import Any, Optional

from scripts.video_engine.captions.word_timings import synthesize_scenes_speech, probe_duration
from scripts.video_engine.engines.explainer_bridge import (
    compile_explainer_project,
    scenes_to_explainer_spec,
    simulate_explainer,
)
from scripts.video_engine.engines.video_render import render_motion_graphics_video
from scripts.video_engine.outro_mux import concat_with_outro, mux_audio_video
from scripts.video_engine.parsers.brand_theme import extract_brand_theme
from scripts.video_engine.qa.post_render import validate_post_render
from scripts.video_engine.qa.pre_render import validate_pre_render
from scripts.video_engine.scene_builder import (
    align_checkpoints_to_timeline,
    build_scenes_from_document,
    generate_style_artifacts,
)
from scripts.video_engine.scorm.scorm_packager import build_scorm_package


class EducAIPipeline:
    """End-to-end educational video production pipeline."""

    def __init__(self, project_dir: str | Path) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        *,
        doc_path: Optional[str | Path] = None,
        scenes: Optional[list[dict[str, Any]]] = None,
        theme_image: Optional[str | Path] = None,
        engine: str = "motion_graphics",
        title: Optional[str] = None,
        voice: str = "es-AR-ElenaNeural",
        captions: bool = True,
        linear_only: bool = False,
        outro_path: Optional[str | Path] = None,
        skip_render: bool = False,
        aspect_ratio: str = "16:9",
    ) -> dict[str, Any]:
        """Execute the full EducAI production workflow."""
        start_time = time.time()
        clean_title = title or self.project_dir.stem.replace("-", " ").title()
        print(f"\n=======================================================")
        print(f"🎬 EducAI Video Studio: {clean_title}")
        print(f"📁 Directorio del proyecto: {self.project_dir}")
        print(f"⚙️  Motor: {engine} | Voz: {voice} | Formato: {aspect_ratio}")
        print(f"💬 Subtítulos: {'ON (Estilo CapCut Dinámico)' if captions else 'OFF'}")
        print(f"📦 Modo: {'Video Común (Lineal MP4)' if linear_only else 'Video-Cuestionario SCORM 1.2 Interactivo'}")
        print(f"=======================================================\n")

        # --- Stage 1: Ingestion & Branding ---
        brand_theme: dict[str, Any] = {}
        if theme_image and Path(theme_image).is_file():
            print(f"[Etapa 1] Extrayendo paleta institucional de marca desde: {theme_image}...")
            theme_out = self.project_dir / "theme_config.json"
            brand_theme = extract_brand_theme(str(theme_image), output_json=str(theme_out))

        if not scenes:
            if doc_path and Path(doc_path).is_file():
                print(f"[Etapa 1] Ingestando documento docente: {doc_path}...")
                scenes = build_scenes_from_document(doc_path, brand_theme)
            else:
                scenes_json = self.project_dir / "scenes.json"
                if scenes_json.is_file():
                    scenes = json.loads(scenes_json.read_text(encoding="utf-8"))
                else:
                    # Minimal default scene if nothing exists
                    scenes = [{
                        "id": "scene_01",
                        "title": clean_title,
                        "narration": f"Bienvenidos a esta clase sobre {clean_title}.",
                        "screen_elements": {"title": clean_title, "bullets": ["Introducción general", "Conceptos fundamentales"]},
                        "checkpoints": [{
                            "checkpoint_id": "cp_01",
                            "question": f"¿Cuál es el tema central abordado en esta clase?",
                            "options": [clean_title, "Otro tema alternativo", "Ninguno de los anteriores"],
                            "correct_index": 0,
                            "explanation": f"Efectivamente, la clase aborda los fundamentos de {clean_title}."
                        }]
                    }]

        scenes_path = self.project_dir / "scenes.json"
        scenes_path.write_text(json.dumps(scenes, indent=2, ensure_ascii=False), encoding="utf-8")

        # Generate style artifacts
        css_vars, design_md = generate_style_artifacts(brand_theme)
        (self.project_dir / "DESIGN.md").write_text(design_md, encoding="utf-8")

        # --- Stage 2: Voice & Timings ---
        print(f"[Etapa 2] Sintetizando locución neural ({voice}) con captura de marcas de tiempo...")
        tts_res = synthesize_scenes_speech(
            scenes=scenes,
            output_dir=self.project_dir,
            voice=voice,
            rate="-2%",
            emit_word_boundaries=captions,
        )
        timeline = tts_res.get("scenes", [])
        total_audio_duration = float(tts_res.get("total_duration", 0.0))

        # Re-align checkpoints strictly to scene end
        raw_checkpoints = []
        for sc in scenes:
            raw_checkpoints.extend(sc.get("checkpoints", []))
        if not raw_checkpoints:
            local_cp = self.project_dir / "checkpoints.json"
            if local_cp.is_file():
                try:
                    raw_checkpoints = json.loads(local_cp.read_text(encoding="utf-8"))
                except Exception:
                    raw_checkpoints = []

        if raw_checkpoints:
            aligned_cps = align_checkpoints_to_timeline(raw_checkpoints, timeline)
            cp_path = self.project_dir / "scorm_checkpoints.json"
            cp_path.write_text(json.dumps(aligned_cps, indent=2, ensure_ascii=False), encoding="utf-8")

        # --- Stage 3: Stereo Audio Mix ---
        print("[Etapa 3] Mezclando audio estéreo normalizado AAC...")
        audio_mixed_path = self.project_dir / "audio_mixed.m4a"
        self._mix_audio_timeline(timeline, audio_mixed_path)

        # --- Stage 4: Pre-Render QA Gate ---
        print("[Etapa 4] Ejecutando compuerta de calidad Pre-Render (Invariantes 1 y 5)...")
        pre_qa = validate_pre_render(
            self.project_dir,
            render_mode="canvas" if engine in ("explainer", "canvas") else "ffmpeg",
            audio_file="audio_mixed.m4a",
            timeline_file="audio_timeline.json",
        )
        if not pre_qa["passed"]:
            print(f"⚠️  [QA Gate Warning] Observaciones detectadas: {pre_qa['issues']}")
        else:
            print("✅ [QA Gate] Pre-Render aprobado: Sincronía y duraciones conformes.")

        # --- Stage 5: Visual Render ---
        video_raw_path = self.project_dir / "video_raw.mp4"
        if not skip_render or not video_raw_path.is_file():
            print(f"[Etapa 5] Renderizando visuales con motor '{engine}'...")
            self._render_visuals(engine, total_audio_duration, video_raw_path, captions=captions, aspect_ratio=aspect_ratio)
        else:
            print(f"[Etapa 5] Reanudando render previo existente ({video_raw_path})")

        # --- Stage 6: Mux + Outro Concatenation ---
        print("[Etapa 6] Multiplexando video + audio y ensamblando cierre institucional...")
        final_video_name = f"{clean_title.replace(' ', '_')}_EducAI_Final.mp4"
        final_video_path = self.project_dir / final_video_name

        muxed_main_temp = self.project_dir / "main_with_audio.mp4"
        mux_audio_video(video_raw_path, audio_mixed_path, muxed_main_temp, force_stereo=True)
        concat_with_outro(muxed_main_temp, final_video_path, outro_path=outro_path)

        if muxed_main_temp.is_file():
            try:
                muxed_main_temp.unlink()
            except OSError:
                pass

        # --- Stage 7: Post-Render QA Gate ---
        print("[Etapa 7] Ejecutando compuerta de calidad Post-Render...")
        outro_dur = 0.0
        target_outro = Path(outro_path).resolve() if outro_path else (Path(__file__).resolve().parent / "assets" / "ending. educai.mp4")
        if target_outro.is_file():
            try:
                outro_dur = probe_duration(target_outro)
            except Exception:
                outro_dur = 0.0
        expected_total_duration = total_audio_duration + outro_dur

        post_qa = validate_post_render(final_video_path, expected_duration=expected_total_duration)
        if not post_qa["passed"]:
            print(f"⚠️  [QA Gate Warning] Observaciones detectadas: {post_qa['issues']}")
        else:
            print("✅ [QA Gate] Post-Render aprobado: Video H.264 + Audio AAC estéreo verificado.")

        # --- Stage 8: Delivery & SCORM Packaging ---
        results: dict[str, Any] = {
            "success": True,
            "final_video": str(final_video_path),
            "pre_qa": pre_qa,
            "post_qa": post_qa,
        }

        if not linear_only:
            print("[Etapa 8] Empaquetando SCORM 1.2 interactivo con checkpoints para Moodle...")
            checkpoints_for_scorm = []
            cp_file = self.project_dir / "scorm_checkpoints.json"
            if cp_file.is_file():
                checkpoints_for_scorm = json.loads(cp_file.read_text(encoding="utf-8"))

            scorm_full_zip = self.project_dir / f"{clean_title.replace(' ', '_')}_SCORM_Completo.zip"
            build_scorm_package(
                title=clean_title,
                video_url=final_video_name,
                checkpoints=checkpoints_for_scorm,
                output_zip=str(scorm_full_zip),
                include_video_file=str(final_video_path),
                audio_timeline_path=str(self.project_dir / "audio_timeline.json"),
                strict_sync=True,
                also_build_zero_weight=True,
            )
            results["scorm_full"] = str(scorm_full_zip)
            results["scorm_zero"] = str(scorm_full_zip.with_name(f"{clean_title.replace(' ', '_')}_SCORM.zip"))

        total_elapsed = round(time.time() - start_time, 2)
        print(f"\n=======================================================")
        print(f"🎉 ¡Producción finalizada exitosamente en {total_elapsed}s!")
        print(f"📹 Video Final MP4: {final_video_path}")
        if "scorm_full" in results:
            print(f"📦 Paquete SCORM Completo: {results['scorm_full']}")
            print(f"🪶 Paquete SCORM Zero-Weight: {results['scorm_zero']}")
        print(f"=======================================================\n")

        results["elapsed_seconds"] = total_elapsed
        return results

    def _mix_audio_timeline(self, timeline: list[dict[str, Any]], output_path: Path) -> None:
        """Concatenate scene MP3 files with accurate pauses into normalized AAC stereo."""
        if output_path.is_file() and output_path.stat().st_size > 0:
            return

        mp3_files = [self.project_dir / sc["audio_file"] for sc in timeline if (self.project_dir / sc["audio_file"]).is_file()]
        if not mp3_files:
            return

        pause_sec = 0.55
        tl_path = self.project_dir / "audio_timeline.json"
        if tl_path.is_file():
            try:
                pause_sec = float(json.loads(tl_path.read_text(encoding="utf-8")).get("inter_scene_pause", 0.55))
            except Exception:
                pause_sec = 0.55

        silence_file = self.project_dir / "_inter_pause.m4a"
        if pause_sec > 0 and len(mp3_files) > 1:
            cmd_silence = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=stereo",
                "-t", f"{pause_sec:.3f}",
                "-c:a", "aac",
                "-b:a", "192k",
                str(silence_file),
            ]
            subprocess.run(cmd_silence, capture_output=True, check=True)

        concat_list = self.project_dir / "audio_concat.txt"
        with open(concat_list, "w", encoding="utf-8") as f:
            for idx, mp3 in enumerate(mp3_files):
                f.write(f"file '{mp3.as_posix()}'\n")
                if pause_sec > 0 and silence_file.is_file() and idx < len(mp3_files) - 1:
                    f.write(f"file '{silence_file.as_posix()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c:a", "aac",
            "-b:a", "192k",
            "-ac", "2",
            "-ar", "44100",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        for tmp in (concat_list, silence_file):
            if tmp.is_file():
                try:
                    tmp.unlink()
                except OSError:
                    pass

    def _render_visuals(
        self,
        engine: str,
        total_duration: float,
        output_raw: Path,
        captions: bool = True,
        aspect_ratio: str = "16:9",
    ) -> None:
        """Dispatch rendering to the requested visual engine."""
        width = 1920 if aspect_ratio == "16:9" else 1080
        height = 1080 if aspect_ratio == "16:9" else 1920

        if engine == "explainer":
            # Explainer Bridge: compile explainer.json and check simulation
            spec = scenes_to_explainer_spec(
                json.loads((self.project_dir / "scenes.json").read_text(encoding="utf-8")),
                formato=aspect_ratio,
            )
            html_path = compile_explainer_project(self.project_dir, spec=spec, formato=aspect_ratio)
            simulate_explainer(html_path)
            # Render motion graphics video with matching scene card timings
            render_motion_graphics_video(
                self.project_dir,
                total_duration,
                output_raw,
                captions=captions,
                width=width,
                height=height,
            )
        else:
            # Default Motion Graphics engine with scene cards & dynamic CapCut ASS subtitles
            render_motion_graphics_video(
                self.project_dir,
                total_duration,
                output_raw,
                captions=captions,
                width=width,
                height=height,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="EducAI Unified Video Studio Orchestrator")
    parser.add_argument("project_dir", nargs="?", default="films/demo-produccion", help="Directorio del proyecto")
    parser.add_argument("--doc", "-d", help="Documento de cátedra de origen (.pptx, .docx, .pdf)")
    parser.add_argument("--engine", "-e", default="motion_graphics", choices=["motion_graphics", "explainer", "canvas", "hyperframes", "lemo"], help="Motor visual")
    parser.add_argument("--voice", "-v", default="es-AR-ElenaNeural", help="Voz neural EdgeTTS")
    parser.add_argument("--title", "-t", help="Título del curso o clase")
    parser.add_argument("--logo", "-l", help="Imagen del logotipo institucional para paleta de marca")
    parser.add_argument("--aspect", "-a", default="16:9", choices=["16:9", "9:16", "1:1"], help="Relación de aspecto")
    parser.add_argument("--no-captions", action="store_true", help="Desactivar subtítulos dinámicos estilo CapCut")
    parser.add_argument("--linear", action="store_true", help="Generar solo Video Común (sin empaquetado SCORM)")
    parser.add_argument("--skip-render", action="store_true", help="Reanudar render existente sin regenerar video_raw.mp4")

    args = parser.parse_args()

    pipeline = EducAIPipeline(args.project_dir)
    pipeline.run(
        doc_path=args.doc,
        theme_image=args.logo,
        engine=args.engine,
        title=args.title,
        voice=args.voice,
        captions=not args.no_captions,
        linear_only=args.linear,
        skip_render=args.skip_render,
        aspect_ratio=args.aspect,
    )


if __name__ == "__main__":
    main()
