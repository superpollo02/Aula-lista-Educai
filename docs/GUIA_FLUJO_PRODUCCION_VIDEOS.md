# Guía Operativa de Producción de Videos · EducAI
## Flujo de Trabajo con Agentes: Video Común vs. Video-Cuestionario SCORM

Esta guía describe cómo interactuar con el ecosistema de agentes inteligentes de **Máquina de Videos · EducAI** para producir dos tipos de entregables educativos:

1. **Video Común (Lineal):** Video explicativo continuo en formato `.mp4` (Full HD 1080p), con locución neuronal sincronizada, subtítulos dinámicos estilo CapCut y outro institucional, ideal para YouTube, WhatsApp, clases invertidas o streaming.
2. **Video-Cuestionario SCORM (Interactivo):** Recurso didáctico interactivo empaquetado bajo el estándar **SCORM 1.2** para **Moodle LMS**. El video se pausa automáticamente al finalizar conceptos clave para plantear preguntas evaluativas que califican directamente en el libro de calificaciones del campus virtual.

---

## 1. El Elenco de Agentes y Cómo Interactúan

El sistema opera bajo una arquitectura de **Agente Principal y Subagentes Especialistas**:

```
                              [Docente / Usuario]
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │  Antigravity Coordinator  │  <-- Interfaz en lenguaje natural
                        └─────────────┬─────────────┘
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
┌──────────────┐              ┌──────────────┐              ┌────────────────┐
│ Doc Parser & │              │ Brand & Theme│              │ Voice & Timings│
│ Scriptwriter │              │  Architect   │              │   Specialist   │
└──────┬───────┘              └──────┬───────┘              └───────┬────────┘
       │                             │                              │
       └─────────────────────────────┼──────────────────────────────┘
                                     ▼
                        ┌───────────────────────────┐
                        │  Pre-Render QA Gatekeeper │  <-- Invariante 1 (No cortar voz)
                        └─────────────┬─────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │ Visual Render & Stitcher  │  <-- Invariante 3 (Reanudación)
                        └─────────────┬─────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │ Post-Render QA Gatekeeper │  <-- Invariante 4 (ffprobe / visual)
                        └─────────────┬─────────────┘
                                      │
       ┌──────────────────────────────┴──────────────────────────────┐
       ▼ (Si es Video Común)                                        ▼ (Si es Video SCORM)
┌───────────────────────────┐                        ┌───────────────────────────┐
│     Entrega Final MP4     │                        │  SCORM Packager Specialist│
│    (*_EducAI_Final.mp4)   │                        └─────────────┬─────────────┘
└───────────────────────────┘                                      ▼
                                                     ┌───────────────────────────┐
                                                     │ Empaquetado Dual ZIP SCORM│
                                                     │ (Completo + Zero-Weight)  │
                                                     └───────────────────────────┘
```

---

## 2. Menú de Preferencias de Estilo Visual (Briefing Interactivo)

Cuando el docente o usuario no especifica el estilo gráfico en su solicitud inicial, el **Antigravity Coordinator** debe presentar el menú de **5 familias de estilos gráficos** para su elección:

1. **(Recomendado) Pizarra Didáctica / Whiteboard Explainer (`canvas`):** Dibujo progresivo a mano alzada, notas visuales y diagramas vectoriales limpios sobre pizarra. Ideal para conceptos paso a paso, ciencias y clases magistrales.
2. **Motion Graphics & Tarjetas Modernas (`hyperframes`):** Tarjetas dinámicas con transiciones fluidas, tipografía editorial moderna, diseño oscuro o claro con paleta institucional. Ideal para tecnología, gestión y cursos ejecutivos.
3. **Infografía Técnica & Blueprint (`blueprint`):** Esquemas en azul técnico, diagramas de flujo, despiece de procesos y arquitectura. Ideal para ingeniería, sistemas y protocolos.
4. **Visual Sketchnote & Ilustración Editorial (`sketchnote`):** Estilo cuaderno de notas ilustrado con marcadores, texturas orgánicas y viñetas. Ideal para humanidades y storytelling.
5. **Títeres Vectoriales Mocap (`ink_theater`):** Personajes vectoriales expresivos animados con captura de movimiento para dramatizaciones y casos prácticos.

---

## 3. Política de Subtítulos Dinámicos Estilo CapCut (Por Defecto)

### ¿Qué son y cómo se ven?
Inspirados en el estándar visual de CapCut, TikTok e Instagram Reels, los subtítulos dinámicos de EducAI se generan a través de la habilidad `tiktok-word-captions`:
* **Agrupación ágil:** Bloques cortos de 3 a 5 palabras para no saturar la pantalla.
* **Resaltado activo palabra por palabra:** Cada palabra se ilumina en el color de acento de la institución (ej. amarillo `#facc15` o cian `#38bdf8`) con un ligero rebote de escala (`1.08x`) en el milisegundo exacto en que la voz en off la pronuncia.
* **Tipografía de alto impacto:** Fuente gruesa (Black/ExtraBold) con contorno oscuro (`stroke`) y sombra para garantizar lectura perfecta sobre cualquier fondo visual.
* **Zona segura:** Ubicados en el tercio inferior, respetando los controles del reproductor.

### Regla de Inclusión por Defecto (Opt-Out)
> [!IMPORTANT]
> **Los subtítulos estilo CapCut están ACTIVADOS POR DEFECTO.**  
> Se generarán automáticamente en todo video (común o SCORM).  
> **Para desactivarlos**, el usuario debe manifestarlo expresamente en el chat (*"sin subtítulos"*, *"no pongas subtítulos"*, *"desactiva los subtítulos"*) o mediante el flag CLI `--no-captions`.

---

## 3. Flujo 1: Creación de un "Video Común" (Lineal MP4)

### Objetivo
Generar un video MP4 tradicional que se reproduce de principio a fin sin interrupciones, listo para proyectar en aula, subir a YouTube o compartir por mensajería.

### Paso 1: Iniciar la Conversación
Hablas directamente con el **Antigravity Coordinator**.

**Ejemplo de Prompt:**
> *"Hola. Quiero crear un video explicativo común a partir de este archivo `presentacion_ia.pptx`. Usá el logo adjunto `sello educai.jpg` para los colores institucionales y una voz en español argentino. El video debe ser continuo y directo."*

*(Nota: Como no dijiste "sin subtítulos", el video incluirá automáticamente los subtítulos estilo CapCut).*

### Paso 2: Ejecución del Flujo por los Agentes
1. **Doc Parser & Scriptwriter:** Extrae diapositivas y **notas del orador** del PPTX para construir el guion y estructurar `scenes.json`.
2. **Brand & Theme Architect:** Cuantiza el logo, extrayendo 8 colores armónicos en `theme_config.json` y generando las variables CSS en `DESIGN.md`.
3. **Voice & Timings Specialist:** Convierte el guion a voz argentina (`es-AR-ElenaNeural` a `-2%` de velocidad) usando EdgeTTS con `boundary="WordBoundary"`. Genera `audio_timeline.json` y `word_timings.json` (marcas por palabra para los subtítulos).
4. **Pre-Render QA Gatekeeper:** Abre la composición en Chromium headless y verifica que no existan errores de consola ni desajustes entre audio y gráficos.
5. **Visual Render & Stitcher:** Renderiza los fotogramas deterministas a 24 fps con los subtítulos dinámicos integrados, mezcla el audio estéreo con retardos milimétricos (`adelay`) y concatena el cierre institucional `ending_norm.mp4`.
6. **Post-Render QA Gatekeeper:** Audita con `ffprobe` que el video final tenga stream de video H.264 (1080p), audio AAC estéreo a 44.1 kHz y que `silencedetect` no arroje cortes abruptos.

### Resultado Entregado
* Archivo final: `films/mi-leccion/Introduccion_EducAI_Final.mp4`.

### Ejecución equivalente por CLI:
```powershell
# Con subtítulos CapCut por defecto
python -m core.orchestrator `
  --project-dir "films/mi-leccion" `
  --doc "presentacion_ia.pptx" `
  --theme-image "sello educai.jpg" `
  --voice "es-AR-ElenaNeural" `
  --title "Introduccion a la IA"

# Si el usuario pidiera expresamente SIN subtítulos:
python -m core.orchestrator `
  --project-dir "films/mi-leccion" `
  --doc "presentacion_ia.pptx" `
  --no-captions `
  --title "Introduccion a la IA"
```

---

## 4. Flujo 2: Creación de un "Video-Cuestionario SCORM" (Interactivo para Moodle)

### Objetivo
Generar un recurso de aprendizaje activo para Moodle LMS. El video se detiene automáticamente en momentos pedagógicos estratégicos y muestra preguntas en pantalla. El estudiante no puede saltear la pregunta sin responder, y su calificación se reporta automáticamente al libro de calificaciones de Moodle.

### Paso 1: Iniciar la Conversación
Hablas directamente con el **Antigravity Coordinator**, solicitando explícitamente la interactividad o evaluación.

**Ejemplo de Prompt:**
> *"Hola. Quiero transformar este documento `modulo1_didactica.docx` en un video-cuestionario interactivo SCORM para Moodle. Necesito que al final de cada sección importante haga una pregunta formativa de opción múltiple para verificar que el alumno comprendió el tema antes de continuar."*

### Paso 2: Detección y Sincronía de Preguntas (Invariante 1)
El subagente **Doc Parser & Scriptwriter** detecta los cierres temáticos y formula las preguntas (`checkpoints`).
* **Regla Invariante No Negociable:**  
  La pausa de la pregunta se posiciona en:
  $$\text{timestamp} = \text{fin de la alocución de la escena} + 0.05\text{s}$$
  **Está estrictamente prohibido cortar la voz del docente a mitad de una frase o concepto.**

### Paso 3: Renderizado y Post-QA
Se produce el video base MP4 (`*_EducAI_Final.mp4`) siguiendo las mismas fases de calidad del video común (incluyendo los subtítulos estilo CapCut).

### Paso 4: Empaquetado Dual SCORM 1.2 (Invariante 2)
El subagente **SCORM Packager Specialist** toma el video auditado y la lista de checkpoints (`scorm_checkpoints.json`) y construye el paquete web SCORM:
1. **Seguridad en Pantalla Completa:** Bloquea la pantalla completa nativa del reproductor (`controlsList="nofullscreen"`) y la redirecciona al contenedor `#player-container`. Esto garantiza que los formularios de preguntas se vean siempre por encima del video.
2. **Generación Dual ZIP:**
   * **`*_SCORM_Completo.zip` (Autocontenido):** Contiene el reproductor HTML, el archivo `imsmanifest.xml` y el archivo `.mp4` adentro. Ideal para plataformas Moodle que permiten subir archivos de 50 a 100 MB.
   * **`*_SCORM.zip` (Zero-Weight Shell < 400 KB):** Contiene el reproductor inteligente y la lógica de preguntas, pero apunta a una URL directa del video alojada en un servidor o CDN. Supera cualquier restricción de cuota de subida (ej. límites estrictos de 10 MB en campus universitarios).

### Paso 5: Despliegue en Moodle LMS por el Docente
1. En el curso de Moodle, hacer clic en **Activar edición**.
2. Seleccionar **Añadir una actividad o un recurso** $\to$ **Paquete SCORM**.
3. Arrastrar el archivo `*_SCORM_Completo.zip` (o `*_SCORM.zip`).
4. En la sección **Calificación**:
   * *Método de calificación:* **Calificación más alta** o **Promedio de intentos**.
   * *Calificación para aprobar:* Ej. `70` (o `7` según la escala).
5. En la sección **Ajustes de visualización**:
   * Abrir en: **Ventana actual** o **Nueva ventana**.
6. Guardar cambios. Al reproducir, Moodle registrará el avance y la nota obtenida en el intento (`cmi.core.lesson_status` y `cmi.core.score.raw`).

### Ejecución equivalente por CLI:
```powershell
python -m core.orchestrator `
  --project-dir "films/modulo1-didactica" `
  --doc "modulo1_didactica.docx" `
  --theme-image "sello educai.jpg" `
  --title "Modulo 1 Didactica" `
  --voice "es-AR-ElenaNeural"
```

---

## 5. Cuadro Comparativo: Video Común vs. Video-Cuestionario SCORM

| Dimensión | Video Común (Lineal) | Video-Cuestionario SCORM |
| :--- | :--- | :--- |
| **Formato de Entrega** | Archivo único `.mp4` (H.264/AAC). | Paquetes comprimidos `.zip` (SCORM 1.2 Dual). |
| **Interactividad** | Pasiva (reproducción continua de principio a fin). | Activa (pausas obligatorias con preguntas formativas). |
| **Evaluación de Estudiantes** | Sin evaluación ni registro. | Califica automáticamente en el libro de calificaciones de Moodle. |
| **Subtítulos CapCut** | **Sí, por defecto** (Opt-out con `--no-captions`). | **Sí, por defecto** (Opt-out con `--no-captions`). |
| **Outro Institucional** | Concatenado al final (`ending_norm.mp4`). | Concatenado al final (`ending_norm.mp4`). |
| **Reproductor Utilizado** | Cualquier reproductor estándar (VLC, web, móvil). | Reproductor HTML5 seguro con wrapper SCORM 1.2. |
| **Canales de Publicación** | YouTube, WhatsApp, Google Drive, televisión, web. | Moodle, Blackboard, Canvas LMS, Chamilo. |
| **Agente Final Involucrado** | Visual Render & Outro Stitcher. | SCORM Packager Specialist. |

---

## 6. Buenas Prácticas y Resolución de Problemas

1. **Reanudación de Renders (Invariante 3):**
   Si el proceso de render se interrumpió y la carpeta `frames/` ya contiene los cuadros PNG, no vuelvas a renderizar desde cero. Ejecuta el pipeline con `--skip-render` o directamente el multiplexado para ahorrar tiempo y cómputo.
2. **Audio con pausas limpias:**
   Nunca concatenes archivos de audio en bruto; el sistema utiliza `adelay` estéreo para insertar `0.55s` de silencio natural entre escenas, permitiendo que el cerebro del estudiante asimile cada idea.
3. **Validación Previa Obligatoria:**
   Antes de renderizar un video extenso, asegúrate de que el gate `pre_render.py` reporte `passed: true`. Esto evita sorpresas de tipografías faltantes o preguntas superpuestas a la voz.

---

## 7. Instructivo de Uso para Principiantes (Paso a Paso en Tablas de Doble Entrada)

### Tabla 1: Instructivo Paso a Paso — Caso A: Video Común (Lineal MP4)

| Etapa del Flujo | ¿Qué te pregunta o informa la App / Agente? | ¿Qué debes responder o solicitar tú? (Prompt Modelo) | Comando Alternativo por Terminal (CLI) | Configuración / Resultado Obtenido |
| :--- | :--- | :--- | :--- | :--- |
| **1. Ingesta y Briefing Inicial** | *"¡Hola! ¿Qué documento deseas convertir en video? (PPTX, DOCX o PDF). ¿Tienes algún logo o imagen institucional para definir los colores?"* | *"Hola. Quiero crear un **video común explicativo** a partir del archivo adjunto `tema1_historia.pptx`. Usá el logo `sello educai.jpg` para los colores y voz argentina."* | `python -m core.orchestrator --project-dir "films/tema1" --doc "tema1_historia.pptx" --theme-image "sello educai.jpg" --title "Tema 1"` | Se crea la carpeta del proyecto, se extraen las diapositivas y notas del orador, y se calcula la paleta de 8 colores armónicos. |
| **2. Revisión de Guion y Estilo** | *"He estructurado el video en 3 escenas de 60 segundos cada una. Los colores principales serán Azul Noche (#0f172a) y Acento Dorado (#facc15). ¿Deseas modificar alguna frase de la locución antes de grabar la voz?"* | *"El guion está excelente, pero en la escena 2 agregá énfasis en la fecha 1816."* (O simplemente: *"Aprobado, continuá"*). | *(Se puede editar directamente `scenes.json` si se desea)* | Se aprueba `scenes.json` y se genera `DESIGN.md` con las variables CSS del lienzo. |
| **3. Configuración de Subtítulos y Voz** | *"Sintetizaré la voz en tono argentino (`es-AR-ElenaNeural`). Por defecto incluiré **subtítulos animados palabra por palabra estilo CapCut**. ¿Deseas mantenerlos?"* | **Para mantenerlos (por defecto):** *"Sí, dejalos así."*<br><br>**Para quitarlos (Opt-Out):** *"No, hacelo sin subtítulos."* | **Con subtítulos:** *(por defecto)*<br><br>**Sin subtítulos:**<br>`--no-captions` | Se generan `scene_XX.mp3`, `audio_timeline.json` y `word_timings.json` (marcas por palabra al milisegundo). |
| **4. Validación Pre-Render (QA)** | *"Ejecutando auditoría Pre-Render en Chromium headless... Verificando 0 errores de consola y duración sincronizada... [Pre-QA: APROBADO]"* | *(No requiere acción del usuario; el sistema valida automáticamente la integridad de assets y audio).* | `python -m core.qa.pre_render --project-dir "films/tema1"` | El Gate Pre-Render valida que no existan tipografías rotas ni desfasajes antes de renderizar cuadros. |
| **5. Renderizado y Ensamble** | *"Renderizando fotogramas a 24 fps en disco, mezclando audio estéreo con pausas naturales de 0.55s y concatenando el cierre institucional..."* | *(Esperar la finalización del proceso en segundo plano).* | *(Flag opcional para reanudar si se cortó):*<br>`--skip-render` | Se genera `video_raw.mp4`, se mezcla `audio_mixed.m4a` (-16 LUFS) y se une `ending_norm.mp4`. |
| **6. Entrega Final del Archivo** | *"¡Video completado con éxito! Se verificó el flujo H.264/AAC sin saltos. Puedes descargarlo en: `films/tema1/Tema 1_EducAI_Final.mp4`"* | *"Muchas gracias. Lo descargo para proyectarlo en clase y subirlo a YouTube."* | `vlc "films/tema1/Tema 1_EducAI_Final.mp4"` | Archivo `.mp4` Full HD listo para compartir en cualquier plataforma. |

---

### Tabla 2: Instructivo Paso a Paso — Caso B: Video-Cuestionario SCORM (Moodle)

| Etapa del Flujo | ¿Qué te pregunta o informa la App / Agente? | ¿Qué debes responder o solicitar tú? (Prompt Modelo) | Comando Alternativo por Terminal (CLI) | Configuración / Resultado Obtenido |
| :--- | :--- | :--- | :--- | :--- |
| **1. Ingesta y Definición Evaluativa** | *"¡Hola! ¿Qué material pedagógico deseas transformar en **video-cuestionario interactivo**? ¿Cuántas preguntas evaluativas deseas y qué tipo de opciones prefieres?"* | *"Hola. Quiero transformar `modulo2_didactica.docx` en un **video interactivo SCORM para Moodle**. Incluí 3 preguntas de opción múltiple con 3 opciones cada una al finalizar cada sección principal."* | `python -m core.orchestrator --project-dir "films/modulo2" --doc "modulo2_didactica.docx" --theme-image "sello educai.jpg" --title "Modulo 2 Didactica"` | Ingesta del documento docente y segmentación temática con puntos de inserción evaluativa. |
| **2. Revisión de Preguntas y Sincronía (Invariante 1)** | *"Formulé 3 preguntas formativas situadas al finalizar la narración de cada tema (+0.05s). Aquí tienes el borrador: [Pregunta 1, Opciones, Correcta...]. ¿Deseas cambiar alguna pregunta o la respuesta correcta?"* | *"Cambiá la opción A de la pregunta 2 por 'Aprendizaje basado en proyectos' y marcá esa como correcta. El resto está perfecto."* | *(Se valida y guarda en `scorm_checkpoints.json`)* | **Invariante 1 aplicada:** Las pausas quedan fijadas estrictamente en el silencio posterior a la voz docente; **jamás cortan una frase**. |
| **3. Configuración de Subtítulos y Locución** | *"Grabando narración y extrayendo cronograma de palabras para subtítulos CapCut. La pantalla completa se configurará sobre el contenedor para que las preguntas no queden ocultas. ¿Avanzamos?"* | *"Sí, adelante con subtítulos y voz argentina."* (O: *"Sin subtítulos"* si se prefiere). | `--voice "es-AR-ElenaNeural"` *(Subtítulos activos por defecto)* | Locución procesada a `-2%` de velocidad y marcas `WordBoundary` listas. |
| **4. Validación Pre-Render y Render** | *"Auditoría Pre-Render ejecutada en Chromium headless: verificados checkpoints, sincronía de audio y eventos DOM... [Pre-QA: APROBADO]. Renderizando video base..."* | *(El usuario solo observa el avance del agente).* | `python -m pytest tests/e2e/test_orchestrator_e2e.py` | Se verifica que los eventos de pausa `timeupdate` no tengan colisiones ni errores JavaScript. |
| **5. Post-QA y Empaquetado Dual SCORM (Invariante 2)** | *"Video base compilado y auditado con `ffprobe`. Se generaron dos paquetes SCORM 1.2:  1) `*_SCORM_Completo.zip` (Autocontenido con video adentro)  2) `*_SCORM.zip` (Zero-Weight < 400 KB para límites de campus) ¿Cuál es la cuota máxima de subida de tu Moodle?"* | *"Mi campus virtual solo me deja subir archivos de hasta 10 MB, así que usaré el paquete liviano `_SCORM.zip` apuntando al video alojado en el drive institucional."* | `python -m core.scorm.scorm_packager --title "Modulo 2 Didactica" --video-url "Modulo2_EducAI_Final.mp4" --dual-zip` | **Invariante 2:** `controlsList="nofullscreen"` y botón fullscreen en `#player-container`. Emisión de la arquitectura **Dual ZIP**. |
| **6. Despliegue en el Campus Virtual (Moodle)** | *"El paquete SCORM 1.2 está listo. Sigue estos 4 pasos en Moodle:  1. Activar edición en tu curso.  2. Añadir actividad -> Paquete SCORM.  3. Arrastrar el archivo `.zip`.  4. En 'Calificación', definir método 'Calificación más alta' y guardar."* | *"¡Excelente! Acabo de subir el archivo `.zip` a Moodle, probé el cuestionario interactivo y registró la nota en el libro de calificaciones."* | *(Prueba local previa en navegador):*<br>`python -m http.server 8080` $\to$ `localhost:8080` | Los alumnos ven el video, responden las preguntas en pantalla al terminar cada tema y su nota queda asentada en Moodle. |

---

### Tabla 3: Guía Rápida de Atajos y Modificadores

| Qué deseas configurar | Qué decirle al Agente en el Chat (Prompt) | Parámetro por Línea de Comandos (CLI) |
| :--- | :--- | :--- |
| **Subtítulos Dinámicos (CapCut)** | *"Con subtítulos"* (Activo por defecto) / *"Sin subtítulos"* (Opt-Out) | `--no-captions` (solo para desactivar) |
| **Cambiar la Voz Narradora** | *"Usá la voz de Tomás"* o *"Usá la voz de Ingrid"* | `--voice "es-AR-TomasNeural"` o `--voice "es-CL-CatalinaNeural"` |
| **Velocidad de la Locución** | *"Hacé la voz un poco más pausada/rápida"* | *(Automático: `-2%` para claridad pedagógica)* |
| **Estilo Visual del Lienzo** | *"Estilo pizarra con dibujos"* o *"Estilo diapositivas modernas con tarjetas"* | `--render-mode canvas` o `--render-mode hyperframes` |
| **Reanudar Render Interrumpido** | *"Se cortó el render, retomalo desde los cuadros existentes"* | `--skip-render` (reutiliza `frames/` y salta al multiplexado) |
| **Servidores Moodle Estrictos (< 10 MB)** | *"El aula virtual no me deja subir archivos pesados"* | Usar el paquete `*_SCORM.zip` (Zero-Weight, pesa menos de $400\text{ KB}$) |

---

## 8. Galería de Producciones Demostrativas Generadas

El repositorio incluye las dos producciones completas que demuestran este flujo de trabajo:

1. **Caso A (Video Común Lineal):**
   * Carpeta: [`films/instructivo-caso-a-video-comun/`](../films/instructivo-caso-a-video-comun/)
   * Video Final MP4: [`Instructivo_Caso_A_Video_Comun_EducAI_Final.mp4`](../films/instructivo-caso-a-video-comun/Instructivo_Caso_A_Video_Comun_EducAI_Final.mp4) (81.5s, Full HD 1080p, subtítulos CapCut quemados).
   * Tratamiento de Dirección: [`TREATMENT.md`](../films/instructivo-caso-a-video-comun/TREATMENT.md)
2. **Caso B (Video-Cuestionario SCORM para Moodle):**
   * Carpeta: [`films/instructivo-caso-b-video-scorm/`](../films/instructivo-caso-b-video-scorm/)
   * Video Base MP4: [`Instructivo_Caso_B_Video_SCORM_EducAI_Final.mp4`](../films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_Video_SCORM_EducAI_Final.mp4) (79.1s, Full HD 1080p).
   * Paquete Autocontenido: [`Instructivo_Caso_B_Video_SCORM_SCORM_Completo.zip`](../films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_Video_SCORM_SCORM_Completo.zip) ($4.33\text{ MB}$).
   * Paquete Zero-Weight: [`Instructivo_Caso_B_Video_SCORM_SCORM.zip`](../films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_Video_SCORM_SCORM.zip) ($4.6\text{ KB}$).
   * Tratamiento y Checkpoints: [`TREATMENT.md`](../films/instructivo-caso-b-video-scorm/TREATMENT.md) y [`scorm_checkpoints.json`](../films/instructivo-caso-b-video-scorm/scorm_checkpoints.json).

