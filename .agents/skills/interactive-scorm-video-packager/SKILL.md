---
name: interactive-scorm-video-packager
description: Empaquetador de videos interactivos en paquetes SCORM 1.2 ultra-livianos (< 500 KB) con arquitectura Zero-Weight Shell para Moodle. Integra pausas de video, preguntas formativas en pantalla y calificación automática en el LMS.
---

# Interactive SCORM Video Packager (Zero-Weight Architecture)

Esta habilidad resuelve el problema de las cuotas de subida en Moodle para videos extensos (de 5 a 30+ minutos), encapsulando la interactividad y la calificación en un contenedor ultraliviano.

## 📌 Principio Técnico: Zero-Weight Shell

- **El problema:** Subir un video Full HD de 15 minutos dentro de un ZIP SCORM tradicional pesa >80 MB y falla en la mayoría de los servidores Moodle limitados a 10-20 MB.
- **La solución:** 
  1. El video `.mp4` reside en un servidor de streaming o CDN (o en el repositorio multimedia del campus).
  2. El paquete SCORM (`.zip`) contiene **exclusivamente el reproductor inteligente, el listener de marcas de tiempo y el API Wrapper SCORM 1.2**.
  3. **Peso final del ZIP:** Menor a **400 KB** (subida instantánea garantizada).

## 🚀 Uso del Empaquetador CLI

```powershell
# Modo Dual (genera paquete completo autocontenido + paquete Zero-Weight de streaming)
python -m core.scorm.scorm_packager `
  --title "Protocolo de Relevamiento EducAI" `
  --video-url "Protocolo_Final.mp4" `
  --include-video "films/protocolo/Protocolo_Final.mp4" `
  --checkpoints-json "checkpoints.json" `
  --audio-timeline "audio_timeline.json" `
  --strict-sync `
  --dual-zip `
  --output "Protocolo_SCORM_Completo.zip"
```

## Estructura de Checkpoints JSON

```json
[
  {
    "timestamp": 85.0,
    "question": "¿Cuál es el zoom recomendado para capturar la vista vertical del aula?",
    "options": [
      "120% para ver textos grandes",
      "67% u 80% para registrar la panorámica completa",
      "100% estándar"
    ],
    "correct_index": 1,
    "feedback_ok": "¡Correcto! Maximiza el registro de la secuencia vertical.",
    "feedback_error": "Incorrecto. Se recomienda 67% u 80%."
  }
]
```

## Calificación en Moodle
El reproductor reporta automáticamente a la API SCORM de Moodle:
- `cmi.core.score.raw` (porcentaje acumulado de respuestas correctas 0 a 100).
- `cmi.core.lesson_status` (`passed` si el puntaje >= 60%, de lo contrario `completed` o `incomplete`).

## Reglas de Sincronía, UX y Despliegue en Moodle

1. **Ubicación por Fin de Locución (`audio_timeline.json`):**
   - Nunca ubicar un `timestamp` en medio de una frase narrada. Consultar `audio_timeline.json` y fijar cada checkpoint justo al `end` de la escena correspondiente (`+0.05s` a `+0.1s`, antes del inicio de la escena siguiente).
2. **Pantalla Completa sobre el Contenedor:**
   - Usar `controlsList="nofullscreen"` en `<video>` y maximizar `#player-container` vía JS. Maximizar `<video>` directamente en HTML5 oculta el `#overlay` de preguntas detrás del reproductor.
3. **Visibilidad e Indicador de Checkpoints:**
   - Incluir una barra superior permanente indicando el próximo checkpoint (`Sección (en MM:SS)`) y una ventana de disparo de `1.2s` en `timeupdate`.
4. **Modos de Empaquetado y Coincidencia de Ruta:**
   - Verificar que `<source src="...">` coincida exactamente con el nombre del `.mp4` final.
   - **Zero-Weight (Streaming):** Requiere URL HTTP directa al `.mp4` (CDN, Cloudflare R2, S3, servidor institucional). YouTube no funciona dentro de `<video src>` por CORS (requeriría `YT.Player`).
   - **Autocontenido (`*_SCORM_Completo.zip`):** Incluir el `.mp4` dentro del ZIP y declararlo en `imsmanifest.xml` cuando la cuota de subida de Moodle lo permita.
