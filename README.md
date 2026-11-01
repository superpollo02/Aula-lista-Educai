# Aula Lista EDUCAI

Ecosistema multi-agente para la creación, mediación pedagógica, producción audiovisual y gamificación de aulas virtuales en **Moodle 4.5**.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Moodle 4.5](https://img.shields.io/badge/Moodle-4.5-orange.svg)](https://moodle.org/)
[![Bootstrap 4.6.2](https://img.shields.io/badge/Bootstrap-4.6.2-purple.svg)](https://getbootstrap.com/)
[![SCORM 1.2](https://img.shields.io/badge/SCORM-1.2-green.svg)](https://scorm.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Índice

- [Descripción General](#descripción-general)
- [Flujo Autónomo «Genera la Unidad X» (Kit Aula Lista & HyperFrames)](#-flujo-autónomo-genera-la-unidad-x-kit-aula-lista--hyperframes)
- [Matriz de Agentes y Habilidades](#-matriz-de-agentes-y-habilidades)
- [Estructura del Proyecto y Directorio Central de Salidas (`outputs/`)](#-estructura-del-proyecto-y-directorio-central-de-salidas-outputs)
- [Componentes del Aula Tripartita](#-componentes-del-aula-tripartita)
- [Gamificación Interactiva: Conecta Bloques y Gran Trivia SCORM](#-gamificación-interactiva-conecta-bloques-y-gran-trivia-scorm)
- [Centro de Ayuda y Guías Ilustradas](#-centro-de-ayuda-y-guías-ilustradas)
- [Guía Rápida de Comandos](#-guía-rápida-de-comandos)
- [Publicación Segura en Moodle](#-publicación-segura-en-moodle)
- [Estándares de Calidad y Directiva Zero-Missing](#-estándares-de-calidad-y-directiva-zero-missing)
- [Licencia](#-licencia)

---

## Descripción General

**Aula Lista EDUCAI** es una plataforma orientada a docentes e instituciones educativas que transforma programas, documentos de cátedra y apuntes en un **aula virtual completa y homologada para Moodle 4.5**. 

A diferencia de los generadores estáticos lineales, el proyecto implementa la arquitectura pedagógica del **Aula Tripartita** reglamentada por la Circular N° 5 de Educación en Salud:
1. **1. La Clase**: Videoclases magistrales, podcast pedagógico de dos voces con acento rioplatense, cápsulas audiovisuales de microlearning y presentaciones descargables.
2. **2. La Lectura**: Dossier teórico estructurado, infografías vectoriales de síntesis, glosario terminológico y preguntas frecuentes (FAQs).
3. **3. La Práctica**: Desafíos interactivos gamificados (Conecta Bloques y Gran Trivia), consignas situadas de gestión con rúbrica analítica y evaluación final con sistema de Doble Candado.

SCORM 1.2 se utiliza en este ecosistema como **objeto interactivo de aprendizaje embebido**, permitiendo trazabilidad y reporte de calificaciones directo al libro de calificaciones de Moodle.

---

## 🏛️ Flujo Autónomo «Genera la Unidad X» (Kit Aula Lista & HyperFrames)

Al solicitar **«Genera la Unidad X»**, el orquestador activa una cadena en 5 fases continuas:

```text
Usuario: «Genera la Unidad X»
  │
  ├── 0. MENÚ DE DECISIÓN (Copiloto Orquestador + asistente-toma-decisiones)
  │      • 🚀 Modo Turbo Autónomo (1-Click, sin fricción, presets óptimos institucionales).
  │      • 🧭 Modo Guiado Paso a Paso (4 Checkpoints asistidos con opciones cerradas).
  │
  ├── 1. INGESTA COGNITIVA Y DISEÑO CURRICULAR
  │      Conexión a cuadernos de fuentes, extracción de citas verificadas, transcripciones
  │      y estructuración de competencias andragógicas.
  │
  ├── 2. PRODUCCIÓN AUDIOVISUAL Y MULTIMEDIA
  │      • Videos Shorts Microlearning: Render headless MP4 con HyperFrames (16:9 y 9:16).
  │      • Podcasts de Cátedra: Diálogos A/B a dos voces con acento rioplatense (edge-tts + ffmpeg).
  │      • Gráfica Institucional: Banners panorámicos e infografías conceptuales en SVG/PNG.
  │      • Diapositivas: Presentaciones oficiales en formato PDF y PPTX editable.
  │
  ├── 3. MAQUETACIÓN AULA TRIPARTITA (Moodle 4.5 / Bootstrap 4.6.2)
  │      • Encabezado: Banner + Frase de encuadre (2 oraciones) + 3 preguntas andragógicas.
  │      • 1. La Clase: Dual Video (Videoclase magistral + Short HyperFrames + Podcast).
  │      • 2. La Lectura: 3 lecturas didácticas, 2 infografías incrustadas, glosario y FAQs.
  │      • 3. La Práctica: Consigna orientadora obligatoria, desafíos y caso situado con rúbrica.
  │
  └── 4. GAMIFICACIÓN SCORM, AUTO-AUDITORÍA Y PUBLICACIÓN
         • Conecta Bloques SCORM 1.2 (8 pares conceptuales con Web Audio y temporizador).
         • Gran Trivia SCORM 1.2 (sin numeración fija en enunciados para aleatorización anti-trampa).
         • Examen Final Sumativo con restricción condicional (candado de Moodle) si es la unidad de cierre.
         • Auto-auditoría Zero-Missing Gate (verificación física de 10 elementos canónicos) y Self-Healing.
         • Validación de sintaxis HTML limpia con CLI tiza.
```

---

## 🤖 Matriz de Agentes y Habilidades

El ecosistema articula **10 agentes especializados** y **6 habilidades ejecutables (skills)**:

### Agentes Especializados (`agents/` y `.claude/agents/`)

| Agente | Archivo | Rol y Responsabilidad Técnica |
| :--- | :--- | :--- |
| **Copiloto Orquestador** | `copiloto-orquestador.md` | Puerta de entrada. Gestiona la toma de decisiones cerrada (Modo Turbo vs. 4 Checkpoints guiados). |
| **Asistente NotebookLM** | `asistente-notebooklm.md` | Ingesta de fuentes documentales, extracción de citas textuales y elaboración de guiones dialógicos. |
| **Course Outliner** | `course-outliner.md` | Arquitectura didáctica de la unidad, definición de objetivos y encuadre curricular bajo Circular N° 5. |
| **Content Creator** | `content-creator.md` | Redacción integral de marcos teóricos, introducciones andragógicas, glosarios y casos situados. |
| **Senior Editor** | `senior-editor.md` | Control de estilo, cumplimiento de la consigna obligatoria y formulación anti-trampa de preguntas. |
| **Multimedia Integrator** | `multimedia-integrator.md` | Diseño y renderizado de banners panorámicos, infografías vectoriales y diapositivas de cátedra. |
| **EdTech Video Director** | `edtech-video-director.md` | Dirección y renderizado headless de composiciones de video con el motor HyperFrames (1080p y 9:16). |
| **SCORM Architect** | `scorm-architect.md` | Compilación de paquetes interactivos SCORM 1.2 (Trivias Turbo/Turno, Conecta Bloques y bancos GIFT). |
| **Moodle XML Formatter** | `moodle-xml-formatter.md` | Maquetación HTML responsiva (Bootstrap 4.6.2), sanitización offline y preparación de metadatos Tiza. |
| **Auditor Calidad Aula Lista** | `auditor-calidad-aula-lista.md` | Ejecución del checklist físico *Zero-Missing Gate* y protocolo de auto-reparación (*Self-Healing*). |

### Habilidades Ejecutables (`skills/`)

| Habilidad (Skill) | Directorio | Función Principal |
| :--- | :--- | :--- |
| `asistente-toma-decisiones` | `skills/asistente-toma-decisiones/` | Menú interactivo de opciones estrictamente cerradas con previsualizaciones de 3 líneas y salto a Turbo. |
| `diseno-instruccional-aula-tripartita` | `skills/diseno-instruccional-aula-tripartita/` | Estructuración pedagógica: encuadre de 2 oraciones, 3 preguntas andragógicas y consignas orientadoras. |
| `edtech-moodle-video` | `skills/edtech-moodle-video/` | Metodología de captura, sincronización audiovisual y mediación de videoclases para entornos virtuales. |
| `hyperframes-render` | `skills/hyperframes-render/` | Pipeline de renderizado programático HTML5/GSAP hacia MP4 usando Chromium Headless y ffmpeg. |
| `notebooklm-video-shorts` | `skills/notebooklm-video-shorts/` | Conexión e interacción con cuadernos de cátedra para generación de guiones didácticos de síntesis. |
| `scorm-gamification` | `skills/scorm-gamification/` | Motor de gamificación: configuración de estilos (Neón, Clásico), temporizadores y reporte de score LMS. |

---

## 📁 Estructura del Proyecto y Directorio Central de Salidas (`outputs/`)

El repositorio mantiene una estricta separación entre los módulos funcionales de producción y los entregables generados:

```text
aula lista EDUCAI/
│
├── 🤖 NÚCLEO DE PRODUCCIÓN
│   ├── agents/                       # Definiciones canónicas de los 10 agentes
│   ├── .claude/agents/               # Agentes sincronizados para Claude Code / Antigravity
│   ├── skills/                       # Las 6 habilidades ejecutables (SKILL.md)
│   ├── scorm_core/                   # Motor base: manifiesto XML seguro y caché SHA-256
│   ├── scorm_modern/                 # Módulo Python: Clase con Video Adicional, Quizzes y Actividades
│   ├── templates/                    # Plantillas maestras HyperFrames (showcase, tutoriales, verticales)
│   ├── assets/audio/                 # Banco sonoro (BGMs, SFX, locuciones base)
│   ├── content/                      # Documentos de cátedra e insumos (.md, .docx)
│   ├── scripts/                      # Scripts de procesamiento y generación
│   │   ├── audio_generators/         # podcast_engine.py (síntesis rioplatense edge-tts + ffmpeg)
│   │   ├── content_generation/       # Generadores IA de HTML, Conecta Bloques y Trivias
│   │   ├── scorm_generators/         # Compiladores SCORM 1.2 (Conecta Bloques, Trivia, Audio, Video)
│   │   ├── course_builders/          # Constructores de cursos integrales
│   │   ├── legacy/                   # Scripts de referencia histórica
│   │   └── render_all_videotutorials.py # Renderizador masivo de guías ilustradas
│   └── docs/                         # Documentación técnica adicional
│
└── 📦 DIRECTORIO CENTRALIZADO DE ENTREGABLES (outputs/)
    ├── outputs/cursos/               # Aulas virtuales completas y recursos estructurados
    │   └── gestion_personas_talento/ # Unidad 1 y 2 (HTMLs Bootstrap, previews, .tiza, lecturas)
    ├── outputs/scorm/                # Todos los paquetes SCORM 1.2 comprimidos (*-SCORM.zip)
    ├── outputs/articles/             # 9 Guías ilustradas paso a paso (Schema v2) y videotutoriales MP4
    ├── outputs/renders/              # Videos MP4 masterizados con HyperFrames (1080p y 9:16)
    ├── outputs/audio/                # Podcasts y pistas de audio exportadas
    └── outputs/mbz/                  # Respaldos de curso Moodle (.mbz)
```

---

## 🏛️ Componentes del Aula Tripartita

Cada unidad didáctica generada en `outputs/cursos/` incluye los siguientes elementos homologados:

1. **01_encabezado**:
   - `banner_unidad.png`: Banner gráfico de 1200x400 px con estética institucional.
   - `01_etiqueta_encabezado.html`: Frase de encuadre curricular (exactamente 2 oraciones) y 3 preguntas andragógicas disparadoras.
2. **02_la_clase**:
   - Dual Video: Videoclase magistral de 20-30 min + Video Short Microlearning de HyperFrames.
   - Podcast pedagógico de cátedra a dos voces embebido con reproductor HTML5 y botón de descarga.
   - Enlace y descarga de las diapositivas oficiales de clase en PDF y PPTX editable.
3. **03_la_lectura**:
   - Dossier de 3 lecturas didácticas de profundización.
   - 2 Infografías conceptuales de síntesis integradas.
   - Glosario de términos clave y bloque de preguntas frecuentes (FAQs).
4. **04_la_practica**:
   - **Consigna orientadora obligatoria**: *«Esta práctica se resuelve con lo visto en los videos docentes; no necesitás repasar toda la bibliografía obligatoria para completarla»*.
   - Caso situado de gestión asistencial con rúbrica analítica de evaluación.
   - Accesos a los desafíos interactivos SCORM.

---

## 🎮 Gamificación Interactiva: Conecta Bloques y Gran Trivia SCORM

Las actividades formativas interactivas se compilan como paquetes SCORM 1.2 estándar:

### 1. Desafío Conecta Bloques
- **Mecánica**: Asociación de 8 pares de conceptos clave mediante una interfaz synthwave accesible.
- **Técnica**: Motor Web Audio API autónomo, temporizador configurable, barra de precisión y reporte de finalización al LMS.
- **Compilación**:
  ```bash
  python scripts/scorm_generators/build_conectabloques_scorm.py ruta/a/pares.md -o outputs/scorm/conectabloques-SCORM.zip
  ```

### 2. Gran Trivia SCORM
- **Aleatorización Anti-Trampa**: Las preguntas se formulan **sin numeración fija en los enunciados** (sin "Pregunta 1") para permitir la rotación aleatoria en Moodle.
- **4 Modos de Configuración**:
  - **🚀 Modo Turbo 1**: 10 preguntas, 60% de aprobación, 30 min, estilo Neón y retroalimentación inmediata.
  - **🎮 Modo Turno Estándar**: Navegación libre por pasos (`← Anterior` y `Siguiente →`), revisión antes de entregar y 70% de aprobación.
  - **⚡ Modo Turbo 2**: Generación masiva por lotes para todas las unidades existentes.
  - **🎨 Personalización Total**: Selección de tema visual (`neon`, `corporate`, `minimal`), tiempo y momento de feedback.
- **Compilación**:
  ```bash
  python scripts/scorm_generators/build_trivia_scorm.py ruta/a/trivia.md -o outputs/scorm/trivia-SCORM.zip
  ```

---

## 📚 Centro de Ayuda y Guías Ilustradas

El proyecto incluye 9 guías ilustradas paso a paso generadas bajo el estándar Schema v2, acompañadas de sus respectivos videotutoriales MP4 en `outputs/articles/`:

| Guía / Flujo | Descripción Pedagógica y Técnica | Tipo | Video MP4 |
| :--- | :--- | :---: | :---: |
| [**Instructivo: Instalación del repositorio y prompts**](outputs/articles/guia-instalacion-prompts-linea-comandos/article.json) | Clonación, entorno virtual, prompts para agentes IA y comandos de despliegue. | `how-to` | [Ver Video](outputs/articles/guia-instalacion-prompts-linea-comandos/videotutorial.mp4) |
| [**Uso de Aula Lista y conexión con Moodle**](outputs/articles/guia-aula-lista-moodle/article.json) | Ensamblado de aula, previsualización local y conexión autenticada con la CLI `tiza`. | `how-to` | [Ver Video](outputs/articles/guia-aula-lista-moodle/videotutorial.mp4) |
| [**Diseño de unidad didáctica tripartita**](outputs/articles/disenar-unidad-tripartita-moodle/article.json) | Estructuración Circular N° 5: La Clase, La Lectura y La Práctica. | `how-to` | [Ver Video](outputs/articles/disenar-unidad-tripartita-moodle/videotutorial.mp4) |
| [**Creación de trivias y Conecta Bloques**](outputs/articles/crear-trivias-scorm-conecta-bloques/article.json) | Preguntas sin numeración fija para mezcla aleatoria y exportación SCORM 1.2. | `how-to` | [Ver Video](outputs/articles/crear-trivias-scorm-conecta-bloques/videotutorial.mp4) |
| [**Podcasts pedagógicos de dos voces**](outputs/articles/generar-podcasts-pedagogicos-dos-voces/article.json) | Guiones dialógicos (A/B), síntesis con `edge-tts` (Elena y Tomás) y masterización `ffmpeg`. | `how-to` | [Ver Video](outputs/articles/generar-podcasts-pedagogicos-dos-voces/videotutorial.mp4) |
| [**Compresión y empaquetado de video SCORM**](outputs/articles/empaquetar-videos-comprimir-scorm/article.json) | Compresión optimizada (`crf 23`, `libx264`) y rastreo de finalización al 90% visto. | `how-to` | [Ver Video](outputs/articles/empaquetar-videos-comprimir-scorm/videotutorial.mp4) |
| [**Configuración del sistema de Doble Candado**](outputs/articles/configurar-doble-candado-certificacion/article.json) | Encadenamiento: Examen Final (≥ 70%) y Encuesta de Calidad obligatoria. | `how-to` | [Ver Video](outputs/articles/configurar-doble-candado-certificacion/videotutorial.mp4) |
| [**Auditoría de integridad técnica con tiza**](outputs/articles/auditar-integridad-tecnica-tiza/article.json) | Auditoría offline de HTML, validación de recursos y control de calidad. | `troubleshooting` | [Ver Video](outputs/articles/auditar-integridad-tecnica-tiza/videotutorial.mp4) |
| [**Aumento del límite de subida en Moodle**](outputs/articles/aumentar-limite-subida-archivos-moodle/article.json) | Configuración de `php.ini`, Apache/Nginx y administración de campus virtual. | `troubleshooting` | [Ver Video](outputs/articles/aumentar-limite-subida-archivos-moodle/videotutorial.mp4) |

---

## ⚡ Guía Rápida de Comandos

```bash
# 1. Generar podcast pedagógico rioplatense (Elena y Tomás)
python -c "from scripts.audio_generators.podcast_engine import generate_podcast_sync; generate_podcast_sync('A: Hola colega...\nB: Hola, hoy analizamos cultura organizacional.', 'outputs/audio/podcast_demo.mp3')"

# 2. Generar preguntas de trivia interactivas con IA
python scripts/content_generation/generate_trivia_ai.py content/apuntes_unidad.md -o content/trivia_unidad.md

# 3. Compilar Gran Trivia SCORM 1.2
python scripts/scorm_generators/build_trivia_scorm.py content/trivia_unidad.md -o outputs/scorm/trivia_unidad-SCORM.zip

# 4. Compilar Conecta Bloques SCORM 1.2
python scripts/scorm_generators/build_conectabloques_scorm.py content/pares_conceptuales.md -o outputs/scorm/conectabloques_unidad-SCORM.zip

# 5. Compilar lección moderna con video adicional y quiz
python scripts/scorm_generators/create_scorm_modern_package.py build scorm_modern/ejemplo/config.yaml

# 6. Renderizar videotutoriales de guías ilustradas
python scripts/render_all_videotutorials.py
```

---

## 🔒 Publicación Segura en Moodle

La sincronización con el aula virtual Moodle se realiza a través de la CLI oficial **Tiza**, garantizando aislamiento estricto de credenciales:

1. **Auditoría Offline de Calidad**:
   ```bash
   tiza comprobar outputs/cursos/gestion_personas_talento/02_u1_la_clase.html
   ```
2. **Sesión Docente Autenticada**:
   El docente abre la sesión desde su terminal (`tiza empezar`), sin que ningún agente tenga acceso a sus claves.
3. **Publicación Directa**:
   ```bash
   tiza publicar outputs/cursos/gestion_personas_talento/02_u1_la_clase.html --en real
   ```

---

## 🛡️ Estándares de Calidad y Directiva Zero-Missing

El sistema no da por finalizada ninguna unidad hasta que el agente `auditor-calidad-aula-lista` ejecuta la verificación física de los **10 elementos canónicos**:
1. Banner visual panorámico (`banner_unidad.png`) presente y vinculado.
2. Etiqueta de encuadre con síntesis de 2 oraciones y 3 preguntas andragógicas.
3. Video short de microlearning renderizado en MP4.
4. Página de la clase con integración Dual Video y enlace a videoclase magistral.
5. Presentación de clase en formato descargable (`.pdf` o `.pptx`).
6. Módulo teórico estructurado con glosario terminológico y bloque FAQ.
7. Infografía conceptual de síntesis incrustada en la lectura.
8. Tarea de práctica con consigna orientadora obligatoria y caso situado con rúbrica.
9. Paquetes interactivos SCORM 1.2 compilados (Conecta Bloques y Gran Trivia).
10. Aprobación del validador de sintaxis y seguridad HTML (`tiza comprobar`).

Si se detecta la ausencia de cualquiera de ellos, el sistema activa automáticamente su protocolo de auto-reparación (**Self-Healing**) hasta completar el 100% de los requisitos.

---

## 📄 Licencia

Este proyecto está liberado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
