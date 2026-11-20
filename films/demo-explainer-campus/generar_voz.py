import asyncio
import edge_tts
import json
import os
import subprocess

SCRIPT_SCENES = [
    {
        "text": "Residentes Cohorte 2026/27: tus cursos autogestionados en Campus Esalud ya están listos.",
        "spoken": "Residentes Cohorte dos mil veintiséis dos mil veintisiete: tus cursos autogestionados en Campus Esalud ya están listos."
    },
    {
        "text": "Si ya tenés usuario registrado ingresá directo. Si no recordás tu clave usá recuperación.",
        "spoken": "Si ya tenés usuario registrado ingresá directo. Si no recordás tu clave usá recuperación de contraseña."
    },
    {
        "text": "En el catálogo buscá: Herramientas de Gestión o Economía de la Salud.",
        "spoken": "En el catálogo de cursos buscá: Herramientas de Gestión o Economía de la Salud."
    },
    {
        "text": "Al ingresar usá las claves: Ges.residentes2026* para Gestión y Eco.residentes206* para Economía.",
        "spoken": "Al ingresar usá las claves institucionales: Ges punto residentes dos mil veintiséis asterisco para Gestión, y Eco punto residentes doscientos seis asterisco para Economía."
    },
    {
        "text": "¡Listo! El aula virtual queda habilitada de forma permanente para cursar a tu ritmo.",
        "spoken": "¡Listo! El aula virtual queda habilitada de forma permanente para cursar a tu ritmo."
    },
    {
        "text": "Si no tenés cuenta solicitá el formulario a Residencias. Las altas se procesan los viernes a las doce horas.",
        "spoken": "Si no tenés cuenta solicitá el formulario a Residencias. Las altas masivas se procesan los viernes a las doce horas."
    },
    {
        "text": "¿Consultas o dudas? Escribinos a deptocapacitacionminsalud@mendoza.gov.ar. ¡Buen inicio de cursada!",
        "spoken": "¿Consultas o dudas? Escribinos a depto capacitación min salud arroba mendoza punto gov punto ar. ¡Buen inicio de cursada!"
    }
]

VOICE = "es-AR-TomasNeural"
OUT_DIR = "f:/proyectos antigrtavity/explainer/explainer-campus"
AUDIO_DIR = os.path.join(OUT_DIR, "audio_parts")
os.makedirs(AUDIO_DIR, exist_ok=True)

async def generate():
    concat_list = []
    metadata = []
    total_time = 0.0

    for i, sc in enumerate(SCRIPT_SCENES):
        out_mp3 = os.path.join(AUDIO_DIR, f"scene_{i}.mp3")
        c = edge_tts.Communicate(sc["spoken"], VOICE, rate="-4%")
        await c.save(out_mp3)

        # Get audio duration with ffprobe
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            out_mp3
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        
        # Add pause buffer per scene (0.6s)
        pause_mp3 = os.path.join(AUDIO_DIR, f"pause_{i}.mp3")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", "0.6", "-q:a", "9", pause_mp3
        ], capture_output=True, check=True)

        concat_list.append(f"file '{os.path.abspath(out_mp3).replace(os.sep, '/')}'")
        concat_list.append(f"file '{os.path.abspath(pause_mp3).replace(os.sep, '/')}'")

        scene_dur = dur + 0.6
        metadata.append({
            "index": i,
            "text": sc["text"],
            "spoken": sc["spoken"],
            "start": total_time,
            "dur": scene_dur,
            "audio_dur": dur
        })
        total_time += scene_dur

    list_file = os.path.join(AUDIO_DIR, "concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_list))

    final_audio = os.path.join(OUT_DIR, "voz.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:a", "libmp3lame", "-b:a", "128k", final_audio
    ], capture_output=True, check=True)

    with open(os.path.join(OUT_DIR, "audio_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"total": total_time, "scenes": metadata}, f, indent=2, ensure_ascii=False)

    print(f"SUCCESS: Generated voiceover. Total duration: {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(generate())
