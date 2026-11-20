---
name: raw-document-video-parser
description: Ingesta, extracción y estructuración de contenidos didácticos en bruto desde presentaciones PowerPoint (.pptx), documentos Word (.docx) y archivos PDF (.pdf) para la Máquina de Videos.
---

# Raw Document Video Parser

Esta habilidad extrae y normaliza el contenido pedagógico de documentos fuente reales aportados por docentes o instituciones académicas para alimentar al motor de video.

## 📌 Formatos Soportados y Reglas de Extracción

1. **PowerPoint (`.pptx`):**
   - Extrae el título de cada diapositiva.
   - Extrae los puntos clave y viñetas visibles.
   - **Notas del orador (Speaker Notes):** Se extraen de forma prioritaria, ya que representan la base ideal para el guion oral de la voz en off.

2. **Word (`.docx`):**
   - Reconoce la jerarquía de encabezados (`Heading 1`, `Heading 2`, `Título 1`, `Título 2`) para segmentar los módulos temáticos.
   - Agrupa párrafos continuos y tablas asociadas.

3. **PDF (`.pdf`):**
   - Extrae el texto limpio por página identificando posibles encabezados de sección.

## 🚀 Uso del Parser CLI

```powershell
python core/parsers/doc_parser.py "ruta/al/documento.pptx" --output "extracted_content.json"
```

## Formato JSON de Salida

El archivo resultante contiene un array de `sections` con la estructura:
```json
{
  "source_type": "pptx",
  "file_name": "clase_01.pptx",
  "total_items": 12,
  "sections": [
    {
      "slide_number": 1,
      "title": "Introducción a Moodle",
      "bullet_points": ["Objetivo", "Destinatarios"],
      "speaker_notes": "Bienvenidos a la clase. En esta unidad exploraremos..."
    }
  ]
}
```
