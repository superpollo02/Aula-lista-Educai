---
name: post-render-video-qa
description: Auditoría automática posterior al renderizado del MP4 final. Extrae fotogramas clave para detectar fondos incorrectos, texto cortado o subtítulos rotos, y verifica con ffprobe/silencedetect que no haya narración cortada ni desincronía audio-video.
---

# Post-Render Video QA

Ejecutar **después de generar el MP4 final** y **antes de entregarlo al usuario** o empaquetarlo en SCORM. El objetivo es detectar fallos visuales o de audio que pasaron desapercibidos durante el código.

## 📌 Checklist Obligatorio Post-Render

1. **Integridad de Streams (`ffprobe`):**
   - Verificar que el archivo final tiene exactamente 1 stream de video (`h264`, `1920x1080` o `1080x1920`, `yuv420p`) y 1 stream de audio (`aac`).
   - Confirmar que la duración del video final equivale a `dur_contenido + dur_ending` y que el audio no termina abruptamente antes del cierre de escena.

2. **Detección de Cortes de Narración y Silencios Anómalos:**
   - Comparar la duración del stream de audio (`ffprobe -select_streams a:0`) contra `audio_mixed.m4a` + `ending_norm.mp4`.
   - Ejecutar detección de picos/silencios al final de cada escena para asegurar que la voz cerró con respiro natural:
     ```powershell
     ffmpeg -i video_final.mp4 -af silencedetect=noise=-35dB:d=0.4 -f null -
     ```

3. **Inspección Visual de Fotogramas Clave:**
   - Extraer capturas al inicio, mitad y cierre de cada escena (más 1 captura del outro) en una carpeta temporal `_qa_frames/`:
     ```powershell
     ffmpeg -y -i video_final.mp4 -vf "fps=1/30" _qa_frames/qa_%03d.png
     ```
   - Inspeccionar visualmente las imágenes extraídas (usando `read_file` sobre las capturas) verificando:
     - **Fondo correcto:** sin pantallas negras, blancas vacías o gradientes rotos.
     - **Subtítulos íntegros:** sin texto cortado fuera del lienzo, sin superposición sobre gráficos clave y con contraste legible.
     - **Elementos de escena:** diagramas, íconos y tarjetas visibles dentro del área segura.
   - Eliminar `_qa_frames/` al aprobar la revisión.

## 🤖 Ejecución Programática (`core.qa.post_render`)

Este gate se ejecuta automáticamente en el orquestador y puede invocarse directamente en Python:

```python
from core.qa import validate_post_render

report = validate_post_render(
    video_path="films/mi-leccion/Leccion_EducAI_Final.mp4",
    check_silence=True,
    spotcheck_frames=True,
)

if not report["passed"]:
    print("Fallos en post-render QA:", report["issues"])
```

## 🤖 Ejecución con Subagente
Conviene delegar esta auditoría a un subagente independiente (que no escribió el `index.html`) para obtener una revisión objetiva de las capturas extraídas y el reporte de `ffprobe` antes de dar la tarea por terminada.
