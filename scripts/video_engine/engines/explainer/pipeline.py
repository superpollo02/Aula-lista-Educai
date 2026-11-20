#!/usr/bin/env python3
"""
pipeline.py - Pipeline integral de compilación, generación de voz y verificación
para Explainers animados (Phase 1 Document Model & Compiler).

Pasos:
  1. Valida explainer.json contra schema.mjs
  2. Sintetiza audio neural escena por escena mediante edge-tts (o scripts/voces.py)
     y obtiene duraciones reales con ffprobe y pausas de buffer
  3. Compila explainer.json + duraciones reales de audio en index.html
  4. Ejecuta simular.cjs para verificar que la reproducción funciona en todos los formatos sin errores

Uso:
  python scripts/pipeline.py <ruta/explainer.json> [--skip-voice] [--voz <nombre>] [--rate <rate>] [--simular-todos]
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys

def check_dependencies():
    for cmd in ["node", "ffmpeg", "ffprobe"]:
        try:
            subprocess.run([cmd, "-version" if cmd != "node" else "--version"], capture_output=True, check=True)
        except Exception:
            print(f"[ERROR] Dependencia faltante en el PATH del sistema: '{cmd}'")
            sys.exit(1)

def run_command(cmd_args, cwd=None):
    res = subprocess.run(cmd_args, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Falló comando: {' '.join(cmd_args)}")
        print(res.stdout)
        print(res.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def validate_spec(json_path, script_dir):
    print(f"\n[1/4] Validando especificación: {json_path}...")
    root_dir = os.path.dirname(script_dir)
    json_path_fwd = os.path.abspath(json_path).replace(os.sep, "/")
    node_script = f"""
    import fs from 'fs';
    import {{ validateExplainerSpec }} from './scripts/schema.mjs';
    const raw = fs.readFileSync('{json_path_fwd}', 'utf8');
    const spec = JSON.parse(raw);
    validateExplainerSpec(spec);
    console.log('VALID_SPEC');
    """
    try:
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", node_script],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )
        if "VALID_SPEC" in proc.stdout:
            print("  ✓ Especificación válida según ExplainerSpecSchema.")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Falló la validación del schema:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

def lint_spec(spec):
    emoji_re = re.compile(r"[\U0001F300-\U0001FAFF\u23F0-\u23FA\u2600-\u27BF]")
    for i, sc in enumerate(spec.get("escenas", []), 1):
        draw = sc.get("drawCode") or ""
        found = emoji_re.findall(draw)
        if found:
            uniq = " ".join(dict.fromkeys(found))
            print(
                f"  [LINT] Escena {i} ({sc.get('id', 'sin-id')}): contiene emojis Unicode en drawCode ({uniq}). "
                "Usá íconos vectoriales del motor según references/estilos.md."
            )

async def synthesize_voice_for_spec(spec, spec_dir, voice=None, rate=None, pitch=None, pause=None):
    import edge_tts

    voz_cfg = spec.get("voz", {})
    voice = voice or voz_cfg.get("locutor", "es-AR-TomasNeural")
    rate = rate or voz_cfg.get("rate", "-4%")
    pitch = pitch or voz_cfg.get("pitch", "+0Hz")
    pause = pause if pause is not None else voz_cfg.get("pausa", 0.6)
    say_dict = voz_cfg.get("say", {})

    escenas = spec.get("escenas", [])
    parts_dir = os.path.join(spec_dir, "audio_parts")
    os.makedirs(parts_dir, exist_ok=True)

    print(f"\n[2/4] Sintetizando audio neural para {len(escenas)} escenas...")
    print(f"  Voz: {voice} | Rate: {rate} | Pitch: {pitch} | Pausa: {pause}s")

    concat_list = []
    audio_meta = []
    total_time = 0.0

    for i, sc in enumerate(escenas):
        # Determinar texto hablado
        if sc.get("hablado"):
            spoken = sc["hablado"]
        else:
            spoken = sc["texto"]
            for k, v in say_dict.items():
                spoken = spoken.replace(k, v)

        part_mp3 = os.path.join(parts_dir, f"scene_{i}.mp3")
        pause_mp3 = os.path.join(parts_dir, f"pause_{i}.mp3")

        print(f"  [{i+1}/{len(escenas)}] Sintetizando escena {i+1}...")
        comm = edge_tts.Communicate(spoken, voice, rate=rate, pitch=pitch)
        await comm.save(part_mp3)

        # Duración real con ffprobe
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
            "index": i,
            "text": sc["texto"],
            "spoken": spoken,
            "start": round(total_time, 3),
            "dur": round(scene_dur, 3),
            "audio_dur": round(raw_dur, 3)
        })
        total_time += scene_dur

    # Concatenar archivo final
    concat_txt = os.path.join(parts_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_list))

    final_mp3 = os.path.join(spec_dir, "voz.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c:a", "libmp3lame", "-b:a", "128k", final_mp3
    ], capture_output=True, check=True)

    meta_file = os.path.join(spec_dir, "audio_meta.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({"total": round(total_time, 3), "scenes": audio_meta}, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Audio final consolidado: {final_mp3} ({total_time:.2f} s)")
    print(f"  ✓ Metadatos guardados en: {meta_file}")

    return audio_meta, meta_file

def compile_spec(json_path, output_html, meta_file, script_dir):
    print(f"\n[3/4] Compilando HTML desde {json_path}...")
    compilador_path = os.path.join(script_dir, "compilador.mjs")
    root_dir = os.path.dirname(script_dir)

    node_args = ["node", compilador_path, json_path, output_html]
    if meta_file and os.path.isfile(meta_file):
        node_args.extend(["--audio-meta", meta_file])

    proc = subprocess.run(node_args, cwd=root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        print("[ERROR] Error al compilar HTML:")
        print(proc.stdout)
        print(proc.stderr)
        sys.exit(proc.returncode)

    print(f"  ✓ Compilador generó con éxito: {output_html}")

def simulate_html(output_html, script_dir, all_formats=True):
    print(f"\n[4/4] Verificando ejecución y render en simular.cjs...")
    simular_path = os.path.join(script_dir, "simular.cjs")
    root_dir = os.path.dirname(script_dir)

    sim_args = ["node", simular_path, output_html]
    if all_formats:
        sim_args.append("--todos")

    proc = subprocess.run(sim_args, cwd=root_dir, capture_output=True, text=True)
    print(proc.stdout)
    if proc.returncode != 0:
        print(f"[ERROR] Falló la simulación (código {proc.returncode}):")
        print(proc.stderr)
        sys.exit(proc.returncode)

    print("  ✓ Simulación completada con 0 errores.")

def format_srt_time(seconds):
    ms_total = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(ms_total, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(meta_file, spec_dir):
    with open(meta_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenes = data if isinstance(data, list) else data.get("scenes", [])
    if not scenes:
        return None
    srt_lines = []
    seq_idx = 1
    for sc in scenes:
        text = str(sc.get("text", "")).strip()
        if not text:
            continue
        start = float(sc.get("start", 0.0))
        speech_dur = float(sc.get("audio_dur") or sc.get("dur") or 0.0)
        end = start + max(0.1, speech_dur)
        srt_lines.append(f"{seq_idx}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n")
        seq_idx += 1
    srt_path = os.path.join(spec_dir, "subtitulos.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    print(f"  ✓ Subtítulos SRT generados: {srt_path}")
    return srt_path

def main():
    parser = argparse.ArgumentParser(description="Pipeline integral de compilación y render de Explainers.")
    parser.add_argument("spec", help="Ruta al archivo explainer.json")
    parser.add_argument("--out", help="Ruta de salida del index.html (default: mismo directorio de explainer.json)")
    parser.add_argument("--skip-voice", action="store_true", help="Omitir síntesis de voz y usar audio_meta.json existente o tiempos estimados")
    parser.add_argument("--voz", help="Sobrescribir voz de edge-tts")
    parser.add_argument("--rate", help="Sobrescribir rate de voz")
    parser.add_argument("--pitch", help="Sobrescribir pitch de voz")
    parser.add_argument("--pausa", type=float, help="Sobrescribir pausa entre escenas en segundos")
    parser.add_argument("--solo-formato-base", action="store_true", help="En simulación no correr --todos")

    args = parser.parse_args()

    check_dependencies()

    spec_abs = os.path.abspath(args.spec)
    if not os.path.isfile(spec_abs):
        print(f"[ERROR] Archivo no encontrado: {spec_abs}")
        sys.exit(1)

    spec_dir = os.path.dirname(spec_abs)
    script_dir = os.path.abspath(os.path.dirname(__file__))
    out_html = os.path.abspath(args.out) if args.out else os.path.join(spec_dir, "index.html")

    with open(spec_abs, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # 1. Validación
    validate_spec(spec_abs, script_dir)
    lint_spec(spec)

    # 2. Voz
    meta_file = os.path.join(spec_dir, "audio_meta.json")
    if not args.skip_voice:
        try:
            import edge_tts
            asyncio.run(synthesize_voice_for_spec(spec, spec_dir, voice=args.voz, rate=args.rate, pitch=args.pitch, pause=args.pausa))
        except ImportError:
            print("[WARN] Falta 'edge_tts'. Se omitirá la síntesis y se usará estimación o audio_meta.json existente.")
    else:
        print("\n[2/4] Síntesis de voz omitida por flag (--skip-voice).")

    srt_path = None
    if not os.path.isfile(meta_file):
        meta_file = None
    else:
        srt_path = generate_srt(meta_file, spec_dir)

    # 3. Compilación
    compile_spec(spec_abs, out_html, meta_file, script_dir)

    # 4. Simulación
    simulate_html(out_html, script_dir, all_formats=not args.solo_formato_base)

    print("\n=======================================================")
    print("PIPELINE COMPLETADO EXITOSAMENTE")
    print(f"Spec:  {spec_abs}")
    print(f"HTML:  {out_html}")
    if os.path.isfile(os.path.join(spec_dir, "voz.mp3")):
        print(f"Audio: {os.path.join(spec_dir, 'voz.mp3')}")
    if srt_path and os.path.isfile(srt_path):
        print(f"SRT:   {srt_path}")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
