"""
Brand Style Guide Extractor (Theme & Typographic Guide from Image).
Extracts dominant brand colors (Primary, Secondary, Accent/Alert, Neutral)
from an uploaded logo or banner image, and generates a visual palette configuration.
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def luminance(r, g, b):
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

def extract_brand_theme(image_path, output_json=None):
    img = Image.open(image_path).convert('RGB')
    # Resize for fast and clean quantization
    img_small = img.resize((200, 200))
    
    # Quantize to 8 color clusters
    quantized = img_small.quantize(colors=8, method=2)
    palette = quantized.getpalette()[:24]
    
    color_clusters = []
    for i in range(8):
        r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
        lum = luminance(r, g, b)
        color_clusters.append({
            "hex": rgb_to_hex(r, g, b),
            "rgb": [r, g, b],
            "lum": lum
        })

    # Filter out near whites and extreme pure blacks for brand accents
    brand_candidates = [c for c in color_clusters if 0.08 < c["lum"] < 0.90]
    
    # Sort by saturation / distinctiveness
    def saturation(c):
        r, g, b = c["rgb"]
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        return (max_c - min_c) / (max_c or 1.0)

    brand_candidates.sort(key=saturation, reverse=True)

    # Assign roles
    primary = brand_candidates[0]["hex"] if len(brand_candidates) > 0 else "#0284c7"
    secondary = brand_candidates[1]["hex"] if len(brand_candidates) > 1 else "#1e293b"
    
    # Alert / accent color (preferably warm: red, orange, coral)
    alert = "#ea580c"
    for c in brand_candidates:
        r, g, b = c["rgb"]
        if r > g * 1.2 and r > b * 1.2: # reddish/orange
            alert = c["hex"]
            break

    dark_neutral = "#0f172a"
    for c in color_clusters:
        if c["lum"] < 0.20:
            dark_neutral = c["hex"]
            break

    theme = {
        "source_image": str(image_path),
        "palette": {
            "primary": primary,
            "secondary": secondary,
            "alert": alert,
            "dark_neutral": dark_neutral,
            "background": "#ffffff",
            "board_sheen": "rgba(255, 255, 255, 0.45)"
        },
        "typography": {
            "font_family": "Segoe UI, -apple-system, sans-serif",
            "title_weight": "bold",
            "body_weight": "normal",
            "subtitles_bg": "rgba(15, 23, 42, 0.88)",
            "subtitles_text": "#ffffff",
            "subtitles_border": primary
        }
    }

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(theme, f, indent=2)
        print(f"[OK] Guía de estilo y paleta extraída exitosamente -> {output_json}")

    return theme

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae la paleta y guía de estilo desde una imagen de marca/logo.")
    parser.add_argument("image", help="Ruta a la imagen (logo, zócalo o banner)")
    parser.add_argument("--output", "-o", default="theme_config.json", help="Archivo JSON de salida")
    args = parser.parse_args()

    extract_brand_theme(args.image, args.output)
