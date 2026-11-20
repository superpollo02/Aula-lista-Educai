#!/usr/bin/env python3
"""
voces.py - Menú de selección y sintetizador de voz neural para Explainers.

Uso:
  python voces.py --listar [es-AR|es-ES|es-MX|todos]
  python voces.py --probar <voz> [--texto "Texto de prueba"]
  python voces.py --generar <ruta/index.html> [--voz <nombre>] [--rate -4%] [--pausa 0.6] [--menu]
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys

try:
    import edge_tts
except ImportError:
    print("Error: falta 'edge-tts'. Instálalo con: pip install edge-tts")
    sys.exit(1)

DEFAULT_VOICE = "es-AR-TomasNeural"
DEFAULT_PAUSE = 0.6
DEFAULT_RATE = "-4%"
DEFAULT_PITCH = "+0Hz"

def check_ffmpeg():
    for cmd in ["ffmpeg", "ffprobe"]:
        try:
            subprocess.run([cmd, "-version"], capture_output=True, check=True)
        except Exception:
            print(f"Error: falta '{cmd}' en el PATH del sistema.")
            sys.exit(1)

async def get_spanish_voices(filter_locale=None):
    voices = await edge_tts.list_voices()
    es_voices = [v for v in voices if v["Locale"].startswith("es-")]
    if filter_locale and filter_locale != "todos":
        es_voices = [v for v in es_voices if v["Locale"].lower() == filter_locale.lower() or filter_locale.lower() in v["Locale"].lower()]
    return sorted(es_voices, key=lambda x: (x["Locale"], x["Gender"], x["ShortName"]))

async def cmd_list(filter_locale):
    voices = await get_spanish_voices(filter_locale)
    print(f"\nVoces en español disponibles ({len(voices)}):")
    print("-" * 65)
    print(f"{'Identificador':<26} {'Género':<8} {'Región/Idioma':<25}")
    print("-" * 65)
    for v in voices:
        print(f"{v['ShortName']:<26} {v['Gender']:<8} {v['Locale']:<25}")
    print("-" * 65)
    print("\nEjemplo de uso:")
    print("  python voces.py --generar explainer-campus/index.html --voz es-AR-TomasNeural\n")

async def cmd_test(voice, text):
    text = text or f"Hola, esta es una prueba de la voz {voice} para explainers animados."
    out_file = "test_voz.mp3"
    print(f"Sintetizando prueba con voz '{voice}'...")
    comm = edge_tts.Communicate(text, voice)
    await comm.save(out_file)
    print(f"Audio de prueba guardado en: {os.path.abspath(out_file)}")

def interactive_menu(voices):
    print("\n--- MENÚ INTERACTIVO DE VOCES ---")
    popular = [
        ("es-AR-TomasNeural", "Español Argentina (Masculino - Recomendado)"),
        ("es-AR-ElenaNeural", "Español Argentina (Femenino)"),
        ("es-ES-AlvaroNeural", "Español España (Masculino)"),
        ("es-ES-ElviraNeural", "Español España (Femenino)"),
        ("es-MX-JorgeNeural", "Español México (Masculino)"),
        ("es-MX-DaliaNeural", "Español México (Femenino)"),
        ("es-CO-GonzaloNeural", "Español Colombia (Masculino)"),
        ("es-CL-LorenzoNeural", "Español Chile (Masculino)")
    ]
    for i, (v, desc) in enumerate(popular, 1):
        print(f"[{i}] {v} - {desc}")
    print("[9] Ver todas las voces")
    print("[0] Ingresar nombre manualmente")

    choice = input("\nSelecciona una opción (default 1): ").strip() or "1"
    if choice.isdigit() and 1 <= int(choice) <= len(popular):
        return popular[int(choice) - 1][0]
    elif choice == "9":
        for i, v in enumerate(voices, 1):
            print(f"[{i:2d}] {v['ShortName']} ({v['Gender']}, {v['Locale']})")
        idx = input("Número de voz: ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(voices):
            return voices[int(idx) - 1]["ShortName"]
    elif choice == "0":
        manual = input("Escribe el nombre de la voz: ").strip()
        if manual:
            return manual
    return DEFAULT_VOICE

def extract_script_and_say(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraer SCRIPT
    m_script = re.search(r"const\s+SCRIPT\s*=\s*\[([\s\S]*?)\];", content)
    if not m_script:
        raise ValueError("No se encontró el array 'const SCRIPT = [...]' en el archivo HTML.")
    raw_script = m_script.group(1)
    
    # Extraer cadenas
    sentences = re.findall(r"['\"](.*?)['\"](?:\s*,|\s*\]|\s*$)", raw_script)
    if not sentences:
        # Fallback a split por comas
        sentences = [s.strip().strip("'\"") for s in raw_script.split(",") if s.strip()]

    # Extraer SAY si existe
    say_dict = {}
    m_say = re.search(r"const\s+SAY\s*=\s*(\{[\s\S]*?\});", content)
    if m_say:
        try:
            # Parse simple JS object
            raw_say = m_say.group(1)
            pairs = re.findall(r"['\"]?([\w\.\*\/\-]+)['\"]?\s*:\s*['\"](.*?)['\"]", raw_say)
            say_dict = {k: v for k, v in pairs}
        except Exception:
            pass

    return sentences, say_dict, content

def build_spoken_text(sentence, say_dict):
    spoken = sentence
    for key, val in say_dict.items():
        spoken = spoken.replace(key, val)
    return spoken

async def cmd_generate(html_path, voice=None, rate=DEFAULT_RATE, pitch=DEFAULT_PITCH, pause=DEFAULT_PAUSE, use_menu=False):
    check_ffmpeg()
    html_abs = os.path.abspath(html_path)
    if not os.path.isfile(html_abs):
        print(f"Error: no existe el archivo {html_abs}")
        sys.exit(1)

    all_voices = await get_spanish_voices()
    if use_menu:
        voice = interactive_menu(all_voices)
    elif not voice:
        voice = DEFAULT_VOICE

    print(f"\n--- GENERACIÓN DE VOZ EN OFF ---")
    print(f"Archivo: {html_abs}")
    print(f"Voz: {voice} | Velocidad: {rate} | Pausa: {pause}s")

    sentences, say_dict, html_content = extract_script_and_say(html_abs)
    print(f"Escenas detectadas: {len(sentences)}")

    work_dir = os.path.dirname(html_abs)
    parts_dir = os.path.join(work_dir, "audio_parts")
    os.makedirs(parts_dir, exist_ok=True)

    concat_list = []
    audio_meta = []
    total_time = 0.0

    for i, text in enumerate(sentences):
        spoken = build_spoken_text(text, say_dict)
        part_mp3 = os.path.join(parts_dir, f"scene_{i}.mp3")
        pause_mp3 = os.path.join(parts_dir, f"pause_{i}.mp3")

        print(f"[{i+1}/{len(sentences)}] Sintetizando escena {i+1}...")
        comm = edge_tts.Communicate(spoken, voice, rate=rate, pitch=pitch)
        await comm.save(part_mp3)

        # Duración real
        cmd_ff = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            part_mp3
        ]
        res = subprocess.run(cmd_ff, capture_output=True, text=True, check=True)
        raw_dur = float(res.stdout.strip())

        # Silencio buffer
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", str(pause), "-q:a", "9", pause_mp3
        ], capture_output=True, check=True)

        concat_list.append(f"file '{os.path.abspath(part_mp3).replace(os.sep, '/')}'")
        concat_list.append(f"file '{os.path.abspath(pause_mp3).replace(os.sep, '/')}'")

        scene_dur = raw_dur + pause
        audio_meta.append({
            "start": round(total_time, 3),
            "dur": round(scene_dur, 3),
            "audio_dur": round(raw_dur, 3)
        })
        total_time += scene_dur

    # Concatenar audio
    concat_txt = os.path.join(parts_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_list))

    final_mp3 = os.path.join(work_dir, "voz.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c:a", "libmp3lame", "-b:a", "128k", final_mp3
    ], capture_output=True, check=True)

    print(f"\nAudio consolidado guardado en: {final_mp3}")
    print(f"Duración total calculada: {total_time:.2f} s")

    # Inyectar o actualizar AUDIO_META en el archivo HTML
    meta_json = json.dumps(audio_meta, indent=4)
    meta_code = f"  const AUDIO_META = {meta_json};\n"

    # Revisar si ya tiene AUDIO_META
    if "const AUDIO_META =" in html_content:
        updated_html = re.sub(r"const\s+AUDIO_META\s*=\s*\[[\s\S]*?\];", f"const AUDIO_META = {meta_json};", html_content)
    else:
        plantilla_loop = "SCENES.forEach((s, i) => { const e = estimate(SCRIPT[i]); s.words = e.words; s.dur = e.dur; s.start = acc; acc += s.dur; });"
        scaled_loop = (
            f"{meta_code}\n  SCENES.forEach((s, i) => {{\n"
            "    const e = estimate(SCRIPT[i]);\n"
            "    const estSpeech = Math.max(0.1, e.dur - CONFIG.cola);\n"
            "    const realSpeech = Math.max(0.1, AUDIO_META[i].audio_dur || (AUDIO_META[i].dur - 0.5));\n"
            "    const scale = realSpeech / estSpeech;\n"
            "    s.words = e.words.map(w => ({ w: w.w, s: +(w.s * scale).toFixed(3), e: +(w.e * scale).toFixed(3) }));\n"
            "    s.dur = AUDIO_META[i].dur;\n"
            "    s.start = AUDIO_META[i].start;\n"
            "  });"
        )
        if plantilla_loop in html_content:
            updated_html = html_content.replace(plantilla_loop, scaled_loop)
        else:
            target = "let acc = 0;\n  SCENES.forEach((s, i) => {"
            replacement = (
                f"{meta_code}\n  let acc = 0;\n  SCENES.forEach((s, i) => {{\n"
                "    const realSpeech = AUDIO_META[i].audio_dur || (AUDIO_META[i].dur - 0.5);\n"
                "    const estSpeech = Math.max(0.1, s.dur - (CONFIG.cola || 0));\n"
                "    const scale = realSpeech / estSpeech;\n"
                "    if (Array.isArray(s.words)) s.words = s.words.map(w => ({ w: w.w, s: +(w.s * scale).toFixed(3), e: +(w.e * scale).toFixed(3) }));\n"
                "    s.dur = AUDIO_META[i].dur;\n"
                "    s.start = AUDIO_META[i].start;"
            )
            updated_html = html_content.replace(target, replacement) if target in html_content else html_content

    with open(html_abs, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"HTML sincronizado con AUDIO_META: {html_abs}")
    print("\nListo para exportar video final:")
    print(f"  node scripts/render.mjs \"{html_path}\"")
    print(f"  ffmpeg -y -i out/index.mp4 -i \"{final_mp3}\" -c:v copy -c:a aac -b:a 192k -shortest out/final-con-voz.mp4\n")

def main():
    parser = argparse.ArgumentParser(description="Gestión de voces neurales y sincronización para Explainers.")
    parser.add_argument("--listar", nargs="?", const="es-AR", help="Listar voces (ej. es-AR, es-ES, es-MX, todos)")
    parser.add_argument("--probar", help="Nombre de voz para probar")
    parser.add_argument("--texto", help="Texto personalizado para probar")
    parser.add_argument("--generar", help="Ruta al archivo HTML del explainer")
    parser.add_argument("--voz", help=f"Nombre de la voz (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Velocidad (ej. -4%%, +5%%)")
    parser.add_argument("--pitch", default=DEFAULT_PITCH, help="Tono (ej. +0Hz, -2Hz)")
    parser.add_argument("--pausa", type=float, default=DEFAULT_PAUSE, help="Pausa entre escenas en segundos")
    parser.add_argument("--menu", action="store_true", help="Abrir menú interactivo de selección de voces")

    args = parser.parse_args()

    if args.listar is not None:
        asyncio.run(cmd_list(args.listar))
    elif args.probar:
        asyncio.run(cmd_test(args.probar, args.texto))
    elif args.generar:
        asyncio.run(cmd_generate(args.generar, args.voz, args.rate, args.pitch, args.pausa, args.menu))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
