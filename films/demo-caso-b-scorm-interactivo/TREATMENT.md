# Treatment — Instructivo Caso B: Video-Cuestionario SCORM (Moodle)

**Proyecto:** `films/instructivo-caso-b-video-scorm/`  
**Director:** Antigravity Coordinator (Lemo-Opuscar & Humanizer Studio)  
**Duración objetivo:** ~70–75 segundos (+ ~4s outro institucional = ~78s total)  
**Voz:** `es-AR-ElenaNeural` a `-2%` de velocidad (locución pedagógica argentina)  
**Estilo Visual:** Canvas / Whiteboard EducAI con paleta de 8 colores institucionales (`sello educai.jpg`)  
**Interactividad:** SCORM 1.2 Dual ZIP para Moodle LMS con pausas evaluativas (`checkpoints`)

---

## 1. Premisa y Enfoque

Explicar y demostrar el flujo completo para crear un **video interactivo SCORM 1.2** para Moodle (Caso B de la Tabla 2), mostrando cómo se insertan preguntas formativas que pausan el video al finalizar la alocución docente y cómo se califica automáticamente al estudiante en el libro de notas del campus.

---

## 2. Tres Candidatos de Estructura Narrativa

* **Opción 1: Recorrido por el Aula Virtual Moodle:** Centrada en la vista del alumno respondiendo preguntas. *(Descartada: omite las etapas de producción y QA de la máquina).*
* **Opción 2: Flujo Paso a Paso con Invariantes Pedagógicas (Elegida):** Muestra la ingesta del apunte $\to$ la regla de sincronía (no cortar la voz) $\to$ la pantalla completa segura $\to$ el empaquetado Dual ZIP $\to$ la nota automática en el libro de calificaciones.
* **Opción 3: Entrevista Técnica a Desarrolladores:** *(Descartada por sonar excesivamente técnica).*

---

## 3. Desglose de Escenas y Sincronía

### Escena 1: Introducción y Título (0.0s – ~4.5s)
* **Visual:** Placa inicial con sello EducAI y título: *"Instructivo Caso B: Video-Cuestionario SCORM para Moodle"*.
* **Voz:** *"Instructivo Caso B: Video-Cuestionario SCORM para Moodle."*

### Escena 2: Lección Interactiva para Moodle (~4.5s – ~21.5s)
* **Visual:** Documento de cátedra (`modulo2.docx`) con marcas de checkpoints. Formulario de preguntas de opción múltiple con 3 opciones.
* **Voz:** *"Cuando necesitás evaluar la comprensión de tus alumnos dentro de Moodle, el camino es el video-cuestionario interactivo. Le entregás tu apunte y le pedís que formule preguntas de opción múltiple al cerrar cada concepto importante."*

### Escena 3: Sincronía Invariante y Pantalla Segura (~21.5s – ~41.5s)
* **Visual:** Línea de tiempo de audio mostrando la forma de onda de la voz, con el marcador de pausa situado exactamente en `fin_alocucion + 0.05s` (Invariante 1). Animación de la ventana de video con el overlay de preguntas visible en pantalla completa segura (Invariante 2: `controlsList="nofullscreen"`).
* **Voz:** *"La regla de oro del sistema es no cortar jamás la voz del docente. Cada pregunta aparece medio segundo después de que termina la frase. Además, el botón de pantalla completa se ajusta al contenedor para que el cuestionario nunca quede escondido detrás del reproductor."*

### Escena 4: Empaquetado Dual SCORM 1.2 (~41.5s – ~59.5s)
* **Visual:** Comparativa visual de los dos paquetes ZIP generados:
  1. `_SCORM_Completo.zip` (Autocontenido con video adentro para servidores normales).
  2. `_SCORM.zip` (Zero-Weight shell < 400 KB para límites de 10 MB en campus universitarios).
* **Voz:** *"Para que no tengas problemas de cuota en el campus, el empaquetador genera dos archivos zip: el paquete completo con el video adentro, y la versión liviana de menos de cuatrocientos kilobytes que reproduce el video desde la nube sin ocupar espacio en el servidor."*

### Escena 5: Registro Automático en Moodle (~59.5s – ~75.0s)
* **Visual:** Pantalla de Moodle con la actividad SCORM abierta, el alumno respondiendo la trivia y la nota registrándose automáticamente en el calificador (`cmi.core.score.raw = 100`, estado `passed`).
* **Voz:** *"Subís el paquete como actividad SCORM a tu curso y definís la nota de aprobación. A medida que los estudiantes miran la clase y responden las preguntas, Moodle registra los intentos y asienta la calificación directamente en el libro de notas."*

---

## 4. Cierre y Salida
* **Outro Institucional:** Concatenación con `ending_norm.mp4` (+3.8s).
* **Entregables:**
  - `films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_EducAI_Final.mp4`.
  - `films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_SCORM_Completo.zip`.
  - `films/instructivo-caso-b-video-scorm/Instructivo_Caso_B_SCORM.zip`.
