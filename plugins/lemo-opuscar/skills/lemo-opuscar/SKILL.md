---
name: lemo-opuscar
description: Direct and produce short films, animations, explainers, or promos made entirely in code, in one of the 99 styles of the Lemo-Opuscar library (e.g. Impasto Oil Painting, Watercolor Brush, Ukiyo-e, Satellite Briefing, Blueprint, Exploded Teardown, Neon Tubes, Whiteboard). Use when the user asks for a video, film, short, promo, explainer, or animation in a specific visual style; when they need data storytelling or architectural walkthroughs in code; or when they ask to explore available film styles.
metadata:
  publisher: lemomo-ai & educai
---

# Lemo-Opuscar Film Studio for Antigravity

Direct and produce a short film made entirely in code across 99 distinctive visual styles.

## Overview
Lemo-Opuscar generates complete video compositions using code:
- **Visuals**: HTML5 Canvas, WebGL, Three.js rendered frame-by-frame via headless Chromium.
- **Audio**: Text-to-speech narration (Kokoro/Edge TTS), sampled and synthesized musical scores, and procedural SFX.
- **Post-Production**: FFmpeg audio/video muxing and encoding.

## Library Location
The global library, core tools, and styles reside at:
`C:\Users\mfischer\.gemini\config\plugins\lemo-opuscar\`

Key guides available in the library:
- [DIRECTOR.md](file:///C:/Users/mfischer/.gemini/config/plugins/lemo-opuscar/DIRECTOR.md): Directing guidelines, pacing, rhythm, camera grammar, and quality checkpoints.
- [TECHNIQUE.md](file:///C:/Users/mfischer/.gemini/config/plugins/lemo-opuscar/TECHNIQUE.md): Frame-by-frame rendering, voice synthesis, musical score, and mixing.
- [AGENTS.md](file:///C:/Users/mfischer/.gemini/config/plugins/lemo-opuscar/rules/AGENTS.md): Full agent workflow and style selection guide.
- [styles/](file:///C:/Users/mfischer/.gemini/config/plugins/lemo-opuscar/styles/): 99 style definitions with individual `STYLE.md` specifications.

## Workflow

### 1. Style Selection & Briefing
When the user requests a film or explainer:
1. **Identify the Style**:
   - Check if the user named a specific style (e.g., `blueprint`, `watercolor`, `whiteboard`, `neon-tubes`, `exploded-teardown`). Look up details in `styles/<slug>/STYLE.md`.
   - If no style is specified, propose 2–3 styles suited to the topic or present categories.
2. **Clarify Requirements** (in a single interactive prompt or message):
   - Specific topic facts, key assets (logos, images, text).
   - Voice preference and audio requirements.
   - Target duration (typically 20s to 60s).
   - Whether a storyboard review is needed before final rendering.

### 2. Treatment & Narrative Design
- Create `TREATMENT.md` in the target film directory (e.g., `<workspace>/films/<project-name>/`).
- Formulate 3 candidate narrative structures and select the best one.
- Define sequence breakdown, timings, and visual composition following `DIRECTOR.md`.

### 3. Verification & Setup
Ensure dependencies are available on the host machine:
- Run the setup utility to verify system tools:
  ```powershell
  python C:\Users\mfischer\.gemini\config\plugins\lemo-opuscar\setup.py check
  ```
- Install dependencies when setting up the environment:
  ```powershell
  python C:\Users\mfischer\.gemini\config\plugins\lemo-opuscar\setup.py deps
  ```

### 4. Production & Rendering
- **Draft & Style Frames**: Render still test frames using `core/render/still.mjs`:
  ```powershell
  node C:\Users\mfischer\.gemini\config\plugins\lemo-opuscar\core\render\still.mjs "<film_dir>" 1.5 3
  ```
- **Voice & Audio**: Synthesize narration track with `core/tts/` and musical beds with `core/audio/`.
- **Full Video Render**: Render animation frames and mux into final `.mp4` using `core/render/movie.mjs`.

## Common Pitfalls
- **Never render directly inside `styles/`**: Always create a dedicated project folder (e.g. `films/<project_name>/`).
- **Path Separation**: On Windows, pass absolute paths or normalize slashes when invoking Node and Python render tools.
- **Invariants**: Keep the visual grammar and rules defined in the chosen `STYLE.md`.
