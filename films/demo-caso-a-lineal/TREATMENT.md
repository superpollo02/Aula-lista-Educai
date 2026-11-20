# Treatment — Instructivo Caso A: Video Común (Lineal MP4)

**Proyecto:** `films/instructivo-caso-a-video-comun/`  
**Director:** Antigravity Coordinator (Lemo-Opuscar & Humanizer Studio)  
**Duración objetivo:** ~70–75 segundos (+ ~4s outro institucional = ~78s total)  
**Voz:** `es-AR-ElenaNeural` a `-2%` de velocidad (locución pedagógica argentina)  
**Estilo Visual:** Canvas / Whiteboard EducAI con paleta de 8 colores institucionales (`sello educai.jpg`)  
**Subtítulos:** Dinámicos palabra por palabra estilo CapCut / TikTok (resaltado activo en color de acento)

---

## 1. Premisa y Enfoque

Demostrar en video, de forma clara, amena y 100% libre de clichés de IA, el procedimiento exacto que sigue un docente o creador de contenido para convertir un apunte o presentación en un **video explicativo lineal en alta definición** (Caso A de la Tabla 1).

---

## 2. Tres Candidatos de Estructura Narrativa

* **Opción 1: Problema vs. Solución ("Antes y Después"):** Compara el dolor de editar videos a mano vs la automatización de la máquina. *(Descartada: distrae del instructivo práctico).*
* **Opción 2: Paso a Paso Operativo Secuencial (Elegida):** Recorre cronológicamente las 4 etapas técnicas: Ingesta de archivos $\to$ Guion y subtítulos CapCut $\to$ Pre-QA en Chromium $\to$ Ensamble y entrega MP4. Es directa, honesta y respeta la Tabla 1.
* **Opción 3: Diálogo en Estudio (Two-voice conversation):** Dos docentes conversando sobre el flujo. *(Descartada: excede la duración requerida de 60-90s).*

---

## 3. Desglose de Escenas y Sincronía

### Escena 1: Introducción y Título (0.0s – ~3.5s)
* **Visual:** Placa inicial con sello EducAI y título: *"Instructivo Caso A: Video Común Lineal MP4"*.
* **Voz:** *"Instructivo Caso A: Video Común Lineal MP4."*

### Escena 2: Ingesta y Colores de Marca (~3.5s – ~21.5s)
* **Visual:** Tarjeta de Ingesta con íconos de PowerPoint, Word y PDF. Selector de color extrayendo la paleta armónica de 8 colores desde `sello educai.jpg`.
* **Voz:** *"Para producir un video explicativo lineal con EducAI, empezás enviando tu documento de cátedra en formato PowerPoint, Word o PDF, junto al logo de tu institución. El sistema lee el contenido y extrae una paleta armónica de ocho colores para que todo mantenga identidad institucional."*

### Escena 3: Guion Didáctico y Subtítulos CapCut (~21.5s – ~39.5s)
* **Visual:** Layout de `scenes.json` segmentado en bloques de 60s. En el tercio inferior, demostración visual activa de los subtítulos CapCut resaltando en amarillo `#facc15` con rebote `1.08x`.
* **Voz:** *"A partir de tus textos y notas de orador, el guionista organiza la clase en escenas de un minuto. La narración se graba con voz argentina y activa subtítulos palabra por palabra estilo CapCut, salvo que pidas expresamente dejarlos afuera."*

### Escena 4: Control Técnico Pre-Render (~39.5s – ~57.0s)
* **Visual:** Mockup del navegador Chromium headless ejecutando la auditoría de consola JS (`0 errors`) y verificación de duración de audio (`audio_timeline.json`). Badge verde `Pre-QA: APROBADO`.
* **Voz:** *"Antes de generar los fotogramas, un navegador automatizado revisa que los textos queden bien encuadrados y que los tiempos de voz coincidan con la animación. Si todo pasa la prueba sin errores, el renderizador comienza a dibujar cada cuadro."*

### Escena 5: Ensamble Estéreo y Entrega (~57.0s – ~74.5s)
* **Visual:** Gráfico de ondas de audio estéreo con pausas de `0.55s` (`adelay`), ensamble con `ending_norm.mp4` y badge final *"1080p Full HD Listo"*.
* **Voz:** *"El motor mezcla el audio estéreo con silencios naturales de medio segundo entre temas, suma la placa de cierre y produce el archivo MP4 definitivo. En pocos minutos tenés tu video en alta definición listo para proyectar o subir a la web."*

---

## 4. Cierre y Salida
* **Outro Institucional:** Concatenación con `ending_norm.mp4` (+3.8s).
* **Entregable:** `films/instructivo-caso-a-video-comun/Instructivo_Caso_A_EducAI_Final.mp4`.
