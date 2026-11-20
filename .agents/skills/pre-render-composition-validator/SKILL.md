---
name: pre-render-composition-validator
description: Gate de validación previo al renderizado de videos. Verifica archivos y assets requeridos, consistencia de duración entre audio_timeline.json y el renderizador, errores de consola en headless Chrome y sincronía de checkpoints SCORM.
---

# Pre-Render Composition Validator

Ejecutar **siempre antes de lanzar el renderizado cuadro a cuadro** (`render_frames.js` / Playwright) para evitar horas de render sobre una composición rota o desfasada.

## 📌 Checklist Obligatorio Pre-Render

1. **Integridad de Archivos y Assets:**
   - Verificar existencia y tamaño > 0 de: `index.html`, `audio_mixed.m4a`, `audio_timeline.json`, `scenes.json` (si es modular), `ending_norm.mp4` y fuentes/imágenes locales referenciadas en `index.html`.
   - Comprobar que no existan recursos externos rotos (HTTP 404) ni rutas relativas inválidas.

2. **Consistencia Audio ↔ Video (`audio_timeline.json` vs `render_frames.js`):**
   - Medir la duración real de `audio_mixed.m4a` con `ffprobe`:
     ```powershell
     ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio_mixed.m4a
     ```
   - Verificar que `dur` en `render_frames.js` y la última escena en `audio_timeline.json` coincidan con la duración real del audio (tolerancia `<= 0.5s`). Si `dur < audio_dur`, la narración final quedará cortada.

3. **Contrato Determinista y Cero Errores JS:**
   - Abrir `index.html` en Chromium headless (Playwright) y probar `window.render(t)` en `t = 0`, `t = dur * 0.25`, `t = dur * 0.5`, `t = dur * 0.75` y `t = dur - 0.1`.
   - Confirmar **0 `pageerror`** y **0 errores de consola**, y validar que `window.render(t)` no dependa de `Date.now()` ni `Math.random()`.

4. **Sincronía de Checkpoints SCORM (si aplica):**
   - Verificar que todo `timestamp` en `scorm_checkpoints.json` coincida con el `end` de una escena en `audio_timeline.json` (`+0.05s` a `+0.1s`), nunca en medio de una locución.

## 🤖 Ejecución Programática (`core.qa.pre_render`)

Este gate se ejecuta automáticamente en el orquestador y puede invocarse directamente en Python:

```python
from core.qa import validate_pre_render

report = validate_pre_render(
    project_dir="films/mi-leccion",
    render_mode="canvas",  # o "hyperframes"
    timeline_file="audio_timeline.json",
    audio_file="audio_mixed.m4a",
)

if not report["passed"]:
    print("Bloqueado por QA:", report["issues"])
```

Para proyectos largos, delegar este checklist a un subagente de validación antes de iniciar el renderizado pesado. Si falla cualquier punto, **bloquear el render** y corregir la fuente primero.
