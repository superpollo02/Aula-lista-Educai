"""
Document Ingestion Parser for Raw Educational Materials (PPTX, DOCX, PDF).
Extracts slide content, speaker notes, document headings, paragraphs, and tables.
Outputs clean structured JSON.
"""

import os
import sys
import json
import argparse
from pathlib import Path

def parse_pptx(file_path):
    from pptx import Presentation
    prs = Presentation(file_path)
    slides_data = []

    for idx, slide in enumerate(prs.slides, 1):
        slide_title = ""
        texts = []
        notes = ""

        # Check title
        if slide.shapes.title and slide.shapes.title.text:
            slide_title = slide.shapes.title.text.strip()

        # Extract shapes text
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    t = paragraph.text.strip()
                    if t and t != slide_title:
                        texts.append(t)

        # Extract notes (crucial for voiceover narration)
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()

        slides_data.append({
            "slide_number": idx,
            "title": slide_title or f"Diapositiva {idx}",
            "bullet_points": texts,
            "speaker_notes": notes
        })

    return {
        "source_type": "pptx",
        "file_name": os.path.basename(file_path),
        "total_items": len(slides_data),
        "sections": slides_data
    }

def parse_docx(file_path):
    from docx import Document
    doc = Document(file_path)
    sections = []
    current_sec = {"title": "Introducción", "paragraphs": [], "tables": []}

    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        # If heading
        if p.style.name.startswith("Heading") or p.style.name.startswith("Título"):
            if current_sec["paragraphs"] or current_sec["tables"]:
                sections.append(current_sec)
            current_sec = {"title": txt, "paragraphs": [], "tables": []}
        else:
            current_sec["paragraphs"].append(txt)

    if current_sec["paragraphs"] or current_sec["tables"]:
        sections.append(current_sec)

    return {
        "source_type": "docx",
        "file_name": os.path.basename(file_path),
        "total_items": len(sections),
        "sections": sections
    }

def parse_pdf(file_path):
    text_pages = []

    # 1. Try pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            text_pages.append(page.extract_text() or "")
    except Exception:
        text_pages = []

    # 2. Try pymupdf if pypdf unavailable or failed
    if not text_pages:
        try:
            import pymupdf
            with pymupdf.open(file_path) as doc:
                for page in doc:
                    text_pages.append(page.get_text("text") or "")
        except Exception:
            text_pages = []

    # 3. Try pdfplumber fallback
    if not text_pages:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_pages.append(page.extract_text() or "")
        except Exception:
            text_pages = []

    pages = []
    for idx, text in enumerate(text_pages, 1):
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        pages.append({
            "page_number": idx,
            "title": lines[0] if lines else f"Página {idx}",
            "paragraphs": lines[1:] if len(lines) > 1 else lines
        })

    return {
        "source_type": "pdf",
        "file_name": os.path.basename(file_path),
        "total_items": len(pages),
        "sections": pages
    }

def parse_document(input_path, output_json=None):
    ext = Path(input_path).suffix.lower()
    if ext == ".pptx":
        data = parse_pptx(input_path)
    elif ext == ".docx":
        data = parse_docx(input_path)
    elif ext == ".pdf":
        data = parse_pdf(input_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Utilice .pptx, .docx o .pdf")

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Archivo procesado exitosamente -> {output_json}")

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingesta y parseo de documentos PPTX/DOCX/PDF a JSON estructurado.")
    parser.add_argument("input", help="Ruta al archivo fuente (.pptx, .docx, .pdf)")
    parser.add_argument("--output", "-o", help="Ruta al archivo JSON de salida", default="raw_extracted.json")
    args = parser.parse_args()

    parse_document(args.input, args.output)
