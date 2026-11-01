# CLAUDE.md

Este archivo proporciona pautas para Claude Code / Antigravity cuando trabaja con código en este repositorio.

## Descripción General del Proyecto

**Aula Lista EDUCAI** es un ecosistema multi-agente para la creación, mediación didáctica, producción audiovisual y gamificación de aulas virtuales en **Moodle 4.5**. Implementa la arquitectura pedagógica del **Aula Tripartita** reglamentada por la Circular N° 5 de Educación en Salud (1. La Clase, 2. La Lectura, 3. La Práctica), integrando objetos interactivos SCORM 1.2 (Conecta Bloques y Gran Trivia), podcasts rioplatenses y renderizado audiovisual con HyperFrames.

## Comandos Comunes

```bash
# 1. Generar podcast pedagógico de dos voces (acento rioplatense Elena y Tomás)
python -c "from scripts.audio_generators.podcast_engine import generate_podcast_sync; generate_podcast_sync('A: Hola...\nB: Hola...', 'outputs/audio/podcast.mp3')"

# 2. Generar y compilar Gran Trivia SCORM 1.2 (sin numeración rígida)
python scripts/content_generation/generate_trivia_ai.py content/lecturas.md -o content/trivia.md
python scripts/scorm_generators/build_trivia_scorm.py content/trivia.md -o outputs/scorm/trivia-SCORM.zip

# 3. Compilar Desafío Conecta Bloques SCORM 1.2 (8 pares conceptuales)
python scripts/scorm_generators/build_conectabloques_scorm.py content/pares.md -o outputs/scorm/conectabloques-SCORM.zip

# 4. Validar y construir paquete SCORM moderno con Video Adicional
python scripts/scorm_generators/create_scorm_modern_package.py validate scorm_modern/ejemplo/config.yaml
python scripts/scorm_generators/create_scorm_modern_package.py build scorm_modern/ejemplo/config.yaml

# 5. Auditar archivo HTML para Moodle con Tiza
tiza comprobar outputs/cursos/gestion_personas_talento/02_u1_la_clase.html

# 6. Renderizar videotutoriales de guías ilustradas
python scripts/render_all_videotutorials.py
```

## Estructura de Directorios

```text
aula lista EDUCAI/
├── agents/                       # Definiciones de los 10 agentes especializados
├── .claude/agents/               # Agentes sincronizados para Claude Code / Antigravity
├── skills/                       # Las 6 habilidades ejecutables (SKILL.md)
├── scorm_core/                   # Motor unificado de manifiesto y caché IA SHA-256
├── scorm_modern/                 # Paquete Python: Lección + Video Adicional + Quizzes
├── templates/                    # Plantillas HyperFrames HTML/GSAP para videos MP4
├── assets/audio/                 # Banco de sonido y pistas base
├── content/                      # Documentos de cátedra e insumos (.md, .docx)
├── scripts/
│   ├── audio_generators/         # podcast_engine.py (edge-tts + ffmpeg)
│   ├── content_generation/       # Generadores IA de HTML, Conecta Bloques y Trivias
│   ├── scorm_generators/         # Compiladores SCORM 1.2 interactivos
│   ├── course_builders/          # Constructores de cursos
│   └── render_all_videotutorials.py # Renderizador masivo de guías
└── outputs/                      # SALIDAS Y ENTREGABLES CENTRALIZADOS
    ├── cursos/                   # Aulas virtuales estructuradas
    ├── scorm/                    # Archivos finales *-SCORM.zip
    ├── articles/                 # Guías ilustradas Schema v2 con videotutoriales
    ├── renders/                  # Videos MP4 masterizados en 1080p y 9:16
    ├── audio/                    # Podcasts exportados
    └── mbz/                      # Respaldos Moodle (.mbz)
```

## Flujo de Trabajo de los 10 Agentes

El flujo autónomo **«Genera la Unidad X»** orquesta 10 agentes y 6 habilidades especializadas:

1. **`copiloto-orquestador`** (+ skill `asistente-toma-decisiones`): Puerta de entrada con menú cerrado: Modo Turbo (1-Click) vs. Modo Guiado en 4 Checkpoints.
2. **`asistente-notebooklm`** (+ skill `notebooklm-video-shorts`): Extracción de fuentes, transcripciones y guiones dialógicos.
3. **`course-outliner`**: Diseño de la arquitectura curricular bajo Circular N° 5.
4. **`content-creator`** (+ skill `diseno-instruccional-aula-tripartita`): Redacción de contenidos, encuadre (2 oraciones + 3 preguntas) y rúbricas.
5. **`senior-editor`**: Revisión de estilo, verificación de consigna obligatoria y preguntas anti-trampa.
6. **`multimedia-integrator`**: Generación de banners panorámicos, infografías vectoriales y diapositivas.
7. **`edtech-video-director`** (+ skill `hyperframes-render`): Dirección y render de videos MP4 (1080p / 9:16).
8. **`scorm-architect`** (+ skill `scorm-gamification`): Compilación de Conecta Bloques y Trivias en 4 modos (Turbo 1, Turno, Turbo 2, Personalizado).
9. **`moodle-xml-formatter`** (+ skill `tiza`): Maquetación HTML responsiva (Bootstrap 4.6.2) y verificación.
10. **`auditor-calidad-aula-lista`**: Verificación física de los 10 elementos canónicos (*Zero-Missing Gate*) y auto-reparación (*Self-Healing*).

## Directiva de Calidad Zero-Missing Gate

Antes de dar por concluida la generación de cualquier unidad, el agente auditor debe certificar la existencia física en disco de los 10 componentes:
1. `banner_unidad.png`
2. `01_etiqueta_encabezado.html` (2 oraciones + 3 preguntas andragógicas)
3. `video_short.mp4` (renderizado por HyperFrames)
4. `02_pagina_la_clase.html` (Dual Video + Videoclase magistral + Podcast)
5. `diapositivas.*` (.pdf o .pptx descargable)
6. `03_pagina_la_lectura.html` (Marco teórico, glosario y FAQs)
7. `infografia_unidad.png`
8. `04_tarea_la_practica.html` (Consigna orientadora obligatoria + Caso con rúbrica)
9. `conectabloques-SCORM.zip` y `trivia-SCORM.zip`
10. Auditoría `tiza comprobar` aprobada sin errores.
