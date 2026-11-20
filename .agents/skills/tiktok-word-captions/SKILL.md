---
name: tiktok-word-captions
description: Genera subtítulos dinámicos a nivel de palabra con resaltado activo estilo CapCut/TikTok/Reels sincronizados con la locución TTS para videos en Canvas 2D/HTML5 o quemado directo FFmpeg (.ass). Activos por defecto bajo la Invariante 5 (Opt-Out).
---

# CapCut / TikTok Word-Level Captions

Esta habilidad genera subtítulos de alto impacto con **sincronía palabra por palabra** y resaltado visual activo (estilo karaoke/CapCut/TikTok) para el motor determinista `render(t)` o quemado directo con FFmpeg (`libass`).

## 📌 Regla de Producción por Defecto (Invariante 5)

> [!IMPORTANT]
> **Subtítulos activos por defecto:**  
> En EducAI, todo video producido (común o SCORM) genera e incluye subtítulos estilo CapCut de forma predeterminada a partir de `word_timings.json`.  
> **Regla Opt-Out:** Solo se desactivan si el usuario solicita expresamente *"sin subtítulos"*, *"no pongas subtítulos"* o mediante el flag CLI `--no-captions`.

## 📌 Principios de Diseño y Sincronía

1. **Extracción de Marcas de Tiempo por Palabra:**
   - Captura eventos `WordBoundary` directamente desde `edge-tts` (o alineación forzada/Whisper cuando el audio es pregrabado) guardando `[{ word, start, end }]` en `word_timings.json`.
   - Escala los tiempos respecto a `audio_dur` real medido con `ffprobe` para evitar desfasajes en videos largos.

2. **Agrupación en Bloques Cortos (Chunks):**
   - Agrupa de **3 a 5 palabras por bloque** (máximo 1–2 líneas, sin cortar frases en conectores débiles).
   - Cada bloque permanece visible únicamente entre `chunk[0].start` y `chunk[-1].end`.

3. **Estilo Visual (Alto Contraste y Legibilidad):**
   - Tipografía sans-serif gruesa (`Arial Black`, `Montserrat 900` o `Segoe UI Bold`), borde oscuro grueso (`outline=6`) + sombra (`shadow=3`).
   - **Palabra inactiva:** blanco puro (`#ffffff` / `&H00FFFFFF&`).
   - **Palabra activa (`t >= w.start && t <= w.end`):** color de acento de marca (ej. Amarillo `#facc15` / `&H0015CCFA&` o Cian `#38bdf8`) con formato bold/escala sin provocar saltos de línea (*layout shift*).

---

## 🚀 Generador Determinista Integrado (`core.captions.capcut_ass`)

El módulo `core/captions/capcut_ass.py` procesa automáticamente `audio_timeline.json` y `word_timings.json` para generar el archivo de subtítulos:

```python
from core.captions.capcut_ass import build_capcut_ass

ass_file = build_capcut_ass(
    timeline_path="films/mi-leccion/audio_timeline.json",
    word_timings_path="films/mi-leccion/word_timings.json",
    output_ass_path="films/mi-leccion/captions.ass",
    chunk_size=4,
    accent_color_bgr="&H0015CCFA&",  # Amarillo EducAI en BGR
)
```

### Quemado Rápido con FFmpeg (`libass` en Windows)
Para quemar el `.ass` en el video sin errores de escape de rutas en Windows:

```python
# Escapar backslashes y dos puntos de unidad de disco (C:)
ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")

cmd = [
    "ffmpeg", "-y",
    "-i", "video_raw.mp4",
    "-vf", f"ass='{ass_escaped}'",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
    "video_subtitulado.mp4"
]
```
