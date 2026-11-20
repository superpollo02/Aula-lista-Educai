---
name: educational-video-producer
description: Orquestador integral para la creación de videos educativos deterministas en EducAI distinguiendo entre Caso A (Video Común Lineal MP4) y Caso B (Video-Cuestionario SCORM 1.2 para Moodle). Guía el diálogo pedagógico con el docente, activa subtítulos CapCut por defecto y aplica las 5 invariantes de producción.
---

# Educational Video Producer (Flujo Dual: Lineal vs. SCORM)

Esta habilidad orquesta de principio a fin la creación de videos educativos deterministas a partir de documentos de cátedra (`.pptx`, `.docx`, `.pdf`), distinguiendo entre dos modalidades de entrega:

1. **Caso A — Video Común (Lineal MP4):** Video explicativo continuo en Full HD (1080p), con locución neuronal argentina (`es-AR-ElenaNeural`), subtítulos dinámicos estilo CapCut por defecto y outro institucional.
2. **Caso B — Video-Cuestionario SCORM (Interactivo para Moodle):** Recurso didáctico interactivo bajo la norma SCORM 1.2. El video se pausa al finalizar conceptos clave para desplegar preguntas evaluativas y calificar automáticamente en el campus virtual.

---

## 📌 Las 5 Invariantes Obligatorias de Producción

Toda producción ejecutada bajo esta habilidad debe respetar sin excepción las reglas de [AGENTS.md](file:///f:/proyectos%20antigrtavity/maquina%20de%20videos/AGENTS.md):

1. **Sincronía de Preguntas (Invariante 1):**  
   Todo checkpoint evaluativo debe posicionarse en:
   $$\text{timestamp} = \text{fin de la alocución de la escena} + 0.05\text{s}$$
   **Prohibido cortar la voz del docente a mitad de una frase o concepto.** La ventana de detección en el reproductor es tolerante (`curT >= cp.timestamp && curT <= cp.timestamp + 1.2`).
2. **Pantalla Completa Segura para Moodle (Invariante 2):**  
   El `<video>` debe incluir `controlsList="nofullscreen"` y delegar la pantalla completa al contenedor general `#player-container`. Maximizar el elemento video en HTML5 oculta los formularios de preguntas detrás del stream visual.
3. **Reanudación de Renders Inconclusos (Invariante 3):**  
   Si el proceso se interrumpe y la carpeta `frames/` o `video_raw.mp4` ya existen, se retoma desde el ensamble y multiplexado sin recalcular cuadros.
4. **Gates de Calidad Obligatorios (Invariante 4):**  
   Ningún entregable se entrega sin superar `validate_pre_render` (verificación de consola JS y assets en Chromium headless) y `validate_post_render` (`ffprobe` de streams H.264/AAC y descarte de pantallas negras).
5. **Subtítulos Dinámicos Estilo CapCut por Defecto (Invariante 5 - Opt-Out):**  
   Todo video incluye subtítulos animados palabra por palabra a partir de `word_timings.json` generados con la habilidad `tiktok-word-captions`. Solo se desactivan si el usuario solicita explícitamente *"sin subtítulos"* o pasa `--no-captions`.

---

## 🎨 Menú Obligatorio de Preferencias de Estilo Visual

Durante la etapa de briefing inicial, si el usuario no especificó el estilo gráfico, se debe presentar este menú de 5 opciones para su elección:

1. **(Recomendado) Pizarra Didáctica / Whiteboard Explainer (`canvas`):** Trazos progresivos a mano alzada, notas visuales y diagramas vectoriales limpios (ideal para conceptos paso a paso, ciencias y clases magistrales).
2. **Motion Graphics & Tarjetas Modernas (`hyperframes`):** Tipografía editorial, tarjetas dinámicas, fondos con atmósfera de marca y transiciones fluidas (ideal para tecnología, gestión y cursos ejecutivos).
3. **Infografía Técnica & Blueprint (`blueprint`):** Esquemas en azul técnico, diagramas de flujo, despiece de procesos y arquitectura (ideal para ingeniería, sistemas y protocolos).
4. **Visual Sketchnote & Ilustración Editorial (`sketchnote`):** Estilo cuaderno de notas ilustrado con marcadores, texturas orgánicas y viñetas (ideal para humanidades y storytelling).
5. **Títeres Vectoriales Mocap (`ink_theater`):** Personajes vectoriales expresivos animados con captura de movimiento para dramatizaciones y casos prácticos.

---

## 🚀 Caminos Críticos y Errores Resueltos (Golden Path)

* **Rutas en Windows para libass:**  
  En Windows, pasar `ass=C:\path\to\captions.ass` a FFmpeg falla por los dos puntos (`:`) de la unidad de disco. Se debe normalizar la ruta:
  ```python
  ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
  # Queda: ass='C\:/path/to/captions.ass'
  ```
* **Renderizado Rápido vs. Saturación de Memoria:**  
  Renderizar miles de cuadros individuales en Chromium headless con `page.screenshot()` para videos de 60-90s demora varios minutos y puede saturar memoria. El generador vectorial determinista `core.orchestrator.video_render` construye tarjetas por escena (`drawbox`, `drawtext`) y quema los subtítulos en una sola pasada de FFmpeg en menos de 5 segundos.
* **Pausas Naturales entre Escenas:**  
  Concatenar directamente archivos MP3 elimina los silencios pedagógicos. Se debe usar `adelay` para intercalar `0.55s` de silencio natural entre cada escena.
* **Cuotas Estrictas de Moodle:**  
  Para campus virtuales limitados a 10–20 MB por archivo, siempre se emite la arquitectura **Dual ZIP**: el paquete completo y el paquete ultraliviano Zero-Weight ($< 400\text{ KB}$) que apunta al video en streaming externo.

---

## 🛠️ Comandos de Ejecución Rápida

### Producción de Video Común (Caso A):
```powershell
python -m core.orchestrator `
  --project-dir "films/mi-leccion" `
  --doc "apunte.docx" `
  --theme-image "sello educai.jpg" `
  --title "Mi Leccion" `
  --voice "es-AR-ElenaNeural"
```

### Producción de Video-Cuestionario SCORM (Caso B):
```powershell
python -m core.orchestrator `
  --project-dir "films/mi-leccion-scorm" `
  --doc "apunte.docx" `
  --theme-image "sello educai.jpg" `
  --title "Mi Leccion SCORM" `
  --voice "es-AR-ElenaNeural"
```
*(Si existe `checkpoints.json` en el directorio, los alinea automáticamente al final de cada escena).*
