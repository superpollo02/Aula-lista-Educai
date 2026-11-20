# CLAUDE.md

Este archivo proporciona pautas para Claude Code / Antigravity cuando trabaja con código en este repositorio.

## Descripción General del Proyecto

Sistema de generación de contenidos de cursos SCORM 1.2 utilizando un flujo de trabajo multi-agente. Crea contenido de e-learning universalmente compatible con todas las plataformas LMS principales (Moodle, Canvas, Blackboard, Google Classroom, TalentLMS, Schoology, D2L Brightspace, etc.).

## Comandos Comunes

```bash
# Generar paquete SCORM a partir de contenido markdown (formato "# Módulo X: Título")
python scripts/scorm_generators/create_scorm_package.py

# Generar paquete SCORM moderno: 1 Lección + 1 Evaluación (quiz) + N Actividades + enlaces
python scripts/scorm_generators/create_scorm_modern_package.py validate <config.yaml>
python scripts/scorm_generators/create_scorm_modern_package.py build <config.yaml>
python scripts/scorm_generators/create_scorm_modern_package.py list <config.yaml>

# Crear paquete SCORM de audio
python scripts/scorm_generators/create_audio_scorm.py <archivo_de_audio> [titulo] [descripcion]

# Generar podcasts pedagógicos de cátedra (motor local gratuito edge-tts con acento rioplatense + ffmpeg)
python -c "from scripts.audio_generators.podcast_engine import generate_podcast_sync; generate_podcast_sync('A: Guion...\nB: Guion...', 'podcast.mp3')"

# Construir aula Moodle completa con podcasts y SCORMs embebidos
python cursos/gestion_personas_talento/generate_moodle_aula.py

# Diagnóstico del entorno de video
python scripts/video_engine/doctor.py

# Producción completa de video con EducAI Video Studio (Orquestador Unificado)
python scripts/video_engine/orchestrator.py films/<proyecto> --doc material.docx --title "Título" --logo logo.jpg
python scripts/video_engine/orchestrator.py films/<proyecto> --engine explainer --aspect 16:9

# Crear paquete SCORM de video pasivo (90% visto)
python scripts/scorm_generators/create_video_scorm.py <archivo_de_video> [titulo] [descripcion]

# Crear paquete SCORM de video interactivo con checkpoints/preguntas
python scripts/scorm_generators/create_video_scorm.py <archivo_de_video> --checkpoints checkpoints.json

# Comprimir archivos de video grandes (CRF recomendado: 23)
ffmpeg -i input.mp4 -vcodec libx264 -crf 23 -preset medium -acodec aac -b:a 128k output.mp4
```

## Estructura de Directorios

```
scripts/
├── video_engine/            # Estudio Unificado EducAI (orquestador, parsers, captions, QA, SCORM interactivo)
│   ├── parsers/             # Ingesta de PPTX, DOCX, PDF y extracción de paleta de marca
│   ├── captions/            # Subtítulos dinámicos estilo CapCut (word_timings.json y .ass)
│   ├── qa/                  # Gates obligatorios Pre-Render y Post-Render (Zero Mocks)
│   ├── scorm/               # Empaquetador SCORM 1.2 interactivo con checkpoints (Dual ZIP)
│   └── engines/             # Motores de renderizado (Explainer Canvas, Motion Graphics, Lemo)
├── scorm_generators/        # Creadores de paquetes SCORM (texto, audio, video, moderno)
├── audio_generators/        # Podcast engine y síntesis de audio
├── content_generation/      # Generación de páginas HTML, edición de contenido
└── legacy/                  # Scripts obsoletos (solo referencia)

films/                       # Proyectos audiovisuales de cátedra (guiones, audios, MP4 y SCORM zips)
├── demo-caso-a-lineal/      # Ejemplo: Video Común Full HD lineal con subtítulos CapCut
├── demo-caso-b-scorm-interactivo/ # Ejemplo: Video-Cuestionario SCORM interactivo con pausas evaluativas
└── demo-explainer-campus/   # Ejemplo: Explainer animado en Canvas (9:16 vertical y 16:9 horizontal)

scorm_modern/                 # Generador moderno: Lección + Evaluación + N Actividades + enlaces
├── scorm_modern/             # Paquete Python (config, parser, renderer, manifest, builder, cli)
├── tests/                    # pytest (30 tests)
├── ejemplo/                  # config.yaml + markdown de ejemplo funcional
└── README.md                 # Formato de config.yaml y del markdown fuente

content/                     # Contenido de los cursos organizado por curso
├── ai-principianti/         # Ejemplo: Curso de IA para principiantes
└── sicurezza-lavoro/        # Ejemplo: Curso de seguridad laboral

.claude/agents/              # Archivos de definición de agentes
output/                      # Paquetes SCORM generados (.zip)
docs/                        # Manual de uso oficial (MANUAL_DE_USO.md), guías de importación y soporte
```

## Flujo de Trabajo de Agentes

El sistema utiliza seis agentes especializados invocados con `subagent_type`:

| Agente | subagent_type | Propósito |
|-------|---------------|-----------|
| Course Outliner | `course-outliner` | Entrevistar al usuario → crear una estructura pedagógica del curso |
| Content Creator | `content-creator` | Generar contenido textual a partir de la estructura |
| Senior Editor | `senior-editor` | Refinar y pulir el contenido escrito |
| Educational Video Producer | `educational-video-producer` | Director integral de video: ingesta docx/pptx, menú de estilos, subtítulos CapCut, QA gates y orquestación |
| Lemo-Opuscar Video Director | `lemo-opuscar-video-director` | Diseñar y producir videos/animaciones por código (99 estilos) para el bloque **La Clase** |
| Multimedia Integrator | `multimedia-integrator` | Crear paquetes SCORM de audio/video (pasivo e interactivo con checkpoints Dual ZIP) y optimizar con FFmpeg |
| SCORM Packager | `moodle-xml-formatter` | Convertir markdown → paquete SCORM .zip |

**Flujo estándar de contenidos:**
1. `course-outliner` → Entrevista y creación de la estructura pedagógica tripartita (*La Clase*, *La Lectura*, *La Práctica*).
2. `content-creator` → Escribir contenido textual de cátedra y actividades.
3. `senior-editor` → Pulir, auditar y editar.
4. **Flujo Audiovisual del Aula Moodle:**
   - **Videos de Introducción Visual de Sección / Banner (< 1 min con HyperFrames):** Micro-videos de apertura (15 a 45 seg) situados en el encabezado de cada sección junto al banner (Bienvenida general, cada Unidad y la sección de Examen Final / Cierre), proporcionando encuadre andragógico de impacto inmediato.
   - **Flujo de Video para "La Clase" (Doble Formato Audiovisual Complementario):**
     - **Video Conceptual Gemini Notebook (NotebookLM):** Síntesis explicativa narrada y estructurada a partir de las fuentes documentales de la cátedra (formato Video Studio / Resumen conceptual).
     - **Video Short Animado Adicional Lemo-Opuscar (`lemo-opuscar-video-director`):** Video adicional de microlearning visual animado por código (99 estilos en Canvas/WebGL/Three.js) para ilustrar esquemas, dinámicas y conceptos clave.
     - `multimedia-integrator` → Optimiza ambos videos con FFmpeg (CRF 23) y genera sus paquetes SCORM interactivos o embeds para la página de **La Clase** (`02_la_clase.html`).
5. `moodle-xml-formatter` → Empaquetar unidades y evaluaciones como SCORM .zip para Moodle.

## Generación de Paquetes SCORM

Hay **dos generadores de texto** disponibles; elegir según la estructura del contenido:

| Generador | Estructura de origen | Cuándo usarlo |
|---|---|---|
| `create_scorm_package.py` | `# Módulo X: Título` (secuencia simple de módulos) | Cursos lineales sin quiz interactivo ni enlaces estructurados. |
| `create_scorm_modern_package.py` (→ paquete `scorm_modern/`) | `# Lección:` + `# Evaluación:` + `# Actividad:`/`# Ejercicio:` + `# Enlaces` | Cursos que necesitan un quiz corregido en el navegador (con seguimiento SCORM de aprobado/reprobado), actividades separadas de la lección, bloques de apoyo (`:::apoyo:::`) con video embebido de YouTube/Drive, y una lista de enlaces (`ENLACES.md`). |

**`create_scorm_package.py`**: convierte markdown a HTML con estilo y botones de navegación, crea `imsmanifest.xml` compatible con SCORM 1.2, y empaqueta todo en un .zip listo para importar en el LMS.

**`create_scorm_modern_package.py`** (`validate` / `build` / `list`): lee un `config.yaml` (con `identificador`, `titulo`, `contenido_md`, `puntaje_minimo`, `enlaces`) y el markdown que referencia, valida ambos, y genera 1 página de lección + 1 de evaluación (quiz autoevaluable) + N páginas de actividad + `ENLACES.md` + `imsmanifest.xml` con título real por objeto, todo empaquetado en `<identificador>-SCORM.zip`. Ver `scorm_modern/README.md` para el formato completo del config y del markdown.

**SCORM de Audio:** Se marca como completado cuando el audio termina. Soporta MP3, WAV, OGG, M4A, AAC.

**SCORM de Video:** Se marca como completado al visualizar el 90%. Soporta MP4, WEBM, MOV, AVI, MKV.

## Pautas de Tamaño de Archivos Multimedia

| Tamaño | Acción |
|------|--------|
| < 10 MB | Usar directamente |
| 10-25 MB | Compresión opcional |
| 25-50 MB | Compresión recomendada |
| 50-100 MB | Compresión obligatoria |
| > 100 MB | Alojamiento externo (YouTube/Vimeo) |

## Directrices para el Idioma Español

- Utilizar de forma consistente el tono informal "tú".
- Acentuación y caracteres correctos: á, é, í, ó, ú, ñ, ü, ¡, ¿.
- Ejemplos adaptados a contextos culturalmente relevantes de habla hispana.

## Estándares de Calidad

- **Pedagógico**: Taxonomía de Bloom, complejidad progresiva.
- **Tablas**: Tablas markdown con separadores `|`, fila de encabezado y separador `|---|---|`.
- **SCORM**: Archivo `imsmanifest.xml` válido en la raíz del zip.
- **Responsivo**: Salida HTML compatible con dispositivos móviles.

## Resolución de Problemas

**Fallo al importar SCORM:** Comprobar que `imsmanifest.xml` esté en la raíz del archivo zip.

**Tablas rotas:** Asegurar fila de cabecera + fila separadora (`|---|---|`) + número consistente de columnas.

**Carga demasiado grande:** Para Moodle/XAMPP, editar php.ini: `upload_max_filesize=100M`, `post_max_size=100M`.

**Los medios no se reproducen:** Volver a codificar a formato H.264/AAC.

Ver `docs/` para guías detalladas: `GUIA_IMPORTAR_MOODLE.md`, `GUIA_AUMENTAR_LIMITE_UPLOAD_MOODLE.md`
