"""Diagnostic and environment health check tool for EducAI Video Studio.

Verifies system binaries (FFmpeg, FFprobe, Node.js), Python libraries,
and browser automation dependencies for video rendering and document ingestion.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_command(cmd_name: str, version_arg: str = "-version") -> tuple[bool, str]:
    """Check if a CLI executable exists in PATH and get its version line."""
    exe = shutil.which(cmd_name)
    if not exe:
        return False, "No encontrado en PATH"
    try:
        proc = subprocess.run(
            [exe, version_arg],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        first_line = (proc.stdout or proc.stderr or "").strip().splitlines()
        info = first_line[0] if first_line else "Disponible"
        return True, f"{exe} ({info[:60]})"
    except Exception as exc:
        return True, f"{exe} (Error al consultar versión: {exc})"


def check_python_pkg(pkg_name: str, import_name: str | None = None) -> tuple[bool, str]:
    """Check if a python package can be imported."""
    mod = import_name or pkg_name
    try:
        __import__(mod)
        import importlib.metadata
        try:
            ver = importlib.metadata.version(pkg_name)
            return True, f"v{ver}"
        except Exception:
            return True, "Instalado"
    except ImportError:
        return False, "No instalado"


def run_doctor() -> bool:
    print("\n=======================================================")
    print("🩺 EducAI Video Studio · Diagnóstico del Entorno (Doctor)")
    print("=======================================================\n")

    all_healthy = True

    # 1. System executables
    print("🖥️  1. Herramientas del Sistema (CLI Binaries):")
    commands_to_check = [
        ("ffmpeg", "-version", "Obligatorio para multiplexado de audio, video y subtítulos ASS"),
        ("ffprobe", "-version", "Obligatorio para medición de duraciones exactas de audio y video"),
        ("node", "--version", "Obligatorio para compilador y simulación del motor Explainer Canvas"),
    ]

    for cmd, arg, note in commands_to_check:
        ok, msg = check_command(cmd, arg)
        icon = "✅" if ok else "❌"
        print(f"  {icon} {cmd:10}: {msg}")
        if not ok:
            print(f"     💡 Nota: {note}")
            all_healthy = False

    # 2. Python Core Libraries
    print("\n🐍 2. Librerías de Python para Audio y Video:")
    audio_video_pkgs = [
        ("edge-tts", "edge_tts", "Síntesis de voz neural con eventos de sincronía palabra por palabra"),
        ("Pillow", "PIL", "Cuantización y extracción de paletas de marca desde logotipos"),
        ("jinja2", "jinja2", "Plantillas HTML para empaquetado interactivo SCORM"),
        ("PyYAML", "yaml", "Lectura de especificaciones de configuración y cursos"),
        ("playwright", "playwright", "Renderizado automatizado de fotogramas Canvas y QA en headless Chrome"),
    ]

    for pkg, imp, note in audio_video_pkgs:
        ok, msg = check_python_pkg(pkg, imp)
        icon = "✅" if ok else "⚠️"
        print(f"  {icon} {pkg:15}: {msg}")
        if not ok:
            print(f"     💡 {note}")
            if pkg in ("edge-tts", "Pillow"):
                all_healthy = False

    # 3. Document Ingestion Libraries (Optional for PPTX/DOCX/PDF)
    print("\n📄 3. Librerías de Ingesta Docente (Document Parsers):")
    doc_pkgs = [
        ("python-docx", "docx", "Extracción de texto, títulos y tablas desde archivos Word (.docx)"),
        ("python-pptx", "pptx", "Extracción de diapositivas y notas del orador desde PowerPoint (.pptx)"),
        ("pypdf", "pypdf", "Lectura y extracción de texto de documentos PDF"),
        ("pymupdf", "fitz", "Parser rápido de PDFs y renderizado de páginas a imágenes"),
        ("pdfplumber", "pdfplumber", "Extracción de tablas complejas desde documentos PDF"),
    ]

    for pkg, imp, note in doc_pkgs:
        ok, msg = check_python_pkg(pkg, imp)
        icon = "✅" if ok else "⚪"
        print(f"  {icon} {pkg:15}: {msg}")

    print("\n=======================================================")
    if all_healthy:
        print("🎉 ¡Entorno listo y saludable para producir videos didácticos!")
    else:
        print("⚠️  Existen componentes faltantes. Para instalarlos:")
        print("   pip install -r requirements-video.txt")
        print("   (En Windows, asegúrate de tener FFmpeg instalado vía: winget install Gyan.FFmpeg)")
    print("=======================================================\n")
    return all_healthy


if __name__ == "__main__":
    run_doctor()
