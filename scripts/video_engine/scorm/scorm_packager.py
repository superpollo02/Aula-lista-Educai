"""Interactive SCORM 1.2 Video Shell Generator.

Builds compliant SCORM 1.2 packages supporting both Zero-Weight streaming architecture
and full self-contained zip packages for Moodle LMS, enforcing all EducAI production
invariants (safe fullscreen, robust checkpoint trigger windows, and speech synchronization).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Optional

SCORM_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0B0F1A;
      color: #f8fafc;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }}
    #player-container {{
      position: relative;
      width: 100%;
      max-width: 1280px;
      aspect-ratio: 16 / 9;
      background: #000000;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    #player-container:fullscreen {{
      width: 100vw;
      height: 100vh;
      max-width: none;
      border-radius: 0;
    }}
    #player-container:-webkit-full-screen {{
      width: 100vw;
      height: 100vh;
      max-width: none;
      border-radius: 0;
    }}
    video {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}
    #header-bar {{
      position: absolute;
      top: 14px;
      left: 18px;
      right: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 30;
      pointer-events: none;
    }}
    .status-pill {{
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      color: #cbd5e1;
      backdrop-filter: blur(6px);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .status-pill .accent {{
      color: #38bdf8;
      font-weight: 700;
    }}
    .header-actions {{
      display: flex;
      gap: 8px;
      pointer-events: auto;
    }}
    .icon-btn {{
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      transition: all 0.2s;
    }}
    .icon-btn:hover {{
      background: #0284c7;
      border-color: #38bdf8;
    }}
    #overlay {{
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(10, 15, 30, 0.96);
      backdrop-filter: blur(10px);
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      z-index: 100;
      animation: fadeIn 0.25s ease-out;
      overflow-y: auto;
    }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: scale(0.98); }} to {{ opacity: 1; transform: scale(1); }} }}
    .badge {{
      background: #0284c7;
      color: #ffffff;
      padding: 5px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 12px;
      display: inline-block;
    }}
    .question-title {{
      font-size: 22px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 20px;
      max-width: 820px;
      line-height: 1.35;
      color: #ffffff;
    }}
    .options-grid {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 100%;
      max-width: 680px;
    }}
    .option-btn {{
      background: #1e293b;
      border: 2px solid #334155;
      color: #f1f5f9;
      padding: 12px 18px;
      border-radius: 10px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      text-align: left;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .option-btn:hover:not(:disabled) {{
      background: #334155;
      border-color: #38bdf8;
      transform: translateX(4px);
    }}
    .option-btn.correct {{
      background: #14532d !important;
      border-color: #22c55e !important;
      color: #ffffff !important;
    }}
    .option-btn.incorrect {{
      background: #7f1d1d !important;
      border-color: #ef4444 !important;
      color: #ffffff !important;
    }}
    #feedback {{
      margin-top: 18px;
      font-size: 16px;
      font-weight: 600;
      text-align: center;
      min-height: 24px;
      max-width: 680px;
    }}
    .continue-btn {{
      margin-top: 20px;
      background: #0284c7;
      color: #ffffff;
      border: none;
      padding: 11px 32px;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      display: none;
      transition: background 0.2s;
    }}
    .continue-btn:hover {{ background: #0369a1; }}
  </style>
</head>
<body>

<div id="player-container">
  <div id="header-bar">
    <div class="status-pill" id="next-checkpoint-info">
      <span>Próxima Pregunta:</span>
      <span class="accent" id="checkpoint-label">Iniciando lección...</span>
    </div>
    <div class="header-actions">
      <div class="status-pill">Calificación: <span class="accent" id="score-display">100</span>%</div>
      <button class="icon-btn" id="btn-fullscreen" title="Pantalla Completa Segura">⛶ Pantalla Completa</button>
    </div>
  </div>

  <video id="video-elem" controls controlsList="nofullscreen" playsinline>
    <source src="{video_src}" type="video/mp4">
    Tu navegador no soporta video HTML5.
  </video>

  <div id="overlay">
    <div class="badge" id="section-badge">Cierre de Sección</div>
    <div class="question-title" id="q-title">Pregunta</div>
    <div class="options-grid" id="opts-container"></div>
    <div id="feedback"></div>
    <button class="continue-btn" id="btn-continue">Continuar con la clase ▶</button>
  </div>
</div>

<script>
// --- SCORM 1.2 API WRAPPER ---
var scormAPI = null;
function findAPI(win) {{
  var attempts = 0;
  while (win && !win.API && attempts < 10) {{
    if (win.parent && win.parent !== win) win = win.parent;
    else if (win.opener) win = win.opener;
    else break;
    attempts++;
  }}
  return win ? win.API : null;
}}
function initSCORM() {{
  scormAPI = findAPI(window);
  if (scormAPI) {{
    scormAPI.LMSInitialize("");
    scormAPI.LMSSetValue("cmi.core.lesson_status", "incomplete");
    scormAPI.LMSCommit("");
  }}
}}
function finishSCORM(score) {{
  if (scormAPI) {{
    scormAPI.LMSSetValue("cmi.core.score.raw", String(Math.round(score)));
    scormAPI.LMSSetValue("cmi.core.score.min", "0");
    scormAPI.LMSSetValue("cmi.core.score.max", "100");
    var status = score >= 60 ? "passed" : "completed";
    scormAPI.LMSSetValue("cmi.core.lesson_status", status);
    scormAPI.LMSCommit("");
    scormAPI.LMSFinish("");
  }}
}}

// --- INTERACTIVE TIMELINE DATA ---
const checkpoints = {checkpoints_json};
let triggeredTimes = new Set();
let correctAnswers = 0;
let totalQuestions = checkpoints.length;

const playerContainer = document.getElementById('player-container');
const video = document.getElementById('video-elem');
const overlay = document.getElementById('overlay');
const sectionBadge = document.getElementById('section-badge');
const qTitle = document.getElementById('q-title');
const optsContainer = document.getElementById('opts-container');
const feedback = document.getElementById('feedback');
const btnContinue = document.getElementById('btn-continue');
const scoreDisplay = document.getElementById('score-display');
const checkpointLabel = document.getElementById('checkpoint-label');
const btnFullscreen = document.getElementById('btn-fullscreen');

initSCORM();

btnFullscreen.addEventListener('click', () => {{
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {{
    if (playerContainer.requestFullscreen) {{
      playerContainer.requestFullscreen();
    }} else if (playerContainer.webkitRequestFullscreen) {{
      playerContainer.webkitRequestFullscreen();
    }}
    btnFullscreen.textContent = '✕ Salir Pantalla Completa';
  }} else {{
    if (document.exitFullscreen) {{
      document.exitFullscreen();
    }} else if (document.webkitExitFullscreen) {{
      document.webkitExitFullscreen();
    }}
    btnFullscreen.textContent = '⛶ Pantalla Completa';
  }}
}});

video.addEventListener('timeupdate', () => {{
  const curT = video.currentTime;
  
  let nextCpIdx = checkpoints.findIndex((cp, idx) => !triggeredTimes.has(idx));
  if (nextCpIdx !== -1) {{
    const cpNext = checkpoints[nextCpIdx];
    const secTitle = cpNext.section_title || 'Sección';
    const timeStr = cpNext.time_str || (Math.floor(cpNext.timestamp / 60) + ':' + String(Math.floor(cpNext.timestamp % 60)).padStart(2, '0'));
    checkpointLabel.textContent = `${{secTitle}} (en ${{timeStr}})`;
  }} else {{
    checkpointLabel.textContent = 'Todas las preguntas completadas';
  }}

  checkpoints.forEach((cp, idx) => {{
    if (!triggeredTimes.has(idx) && curT >= cp.timestamp && curT <= cp.timestamp + 1.2) {{
      triggeredTimes.add(idx);
      triggerCheckpoint(cp);
    }}
  }});
}});

video.addEventListener('ended', () => {{
  const finalScore = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 100;
  finishSCORM(finalScore);
}});

function triggerCheckpoint(cp) {{
  video.pause();
  overlay.style.display = 'flex';
  sectionBadge.textContent = cp.section_title || 'Cierre de Sección';
  qTitle.textContent = cp.question;
  feedback.textContent = '';
  btnContinue.style.display = 'none';
  optsContainer.innerHTML = '';

  cp.options.forEach((optText, i) => {{
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.textContent = optText;
    btn.onclick = () => selectOption(btn, i, cp);
    optsContainer.appendChild(btn);
  }});
}}

function selectOption(selectedBtn, chosenIdx, cp) {{
  const allBtns = optsContainer.querySelectorAll('.option-btn');
  allBtns.forEach(b => b.disabled = true);

  if (chosenIdx === cp.correct_index) {{
    selectedBtn.classList.add('correct');
    feedback.textContent = cp.feedback_ok || "¡Excelente! Respuesta correcta.";
    feedback.style.color = '#4ade80';
    correctAnswers++;
  }} else {{
    selectedBtn.classList.add('incorrect');
    feedback.textContent = cp.feedback_error || "Respuesta incorrecta.";
    feedback.style.color = '#f87171';
    if (allBtns[cp.correct_index]) {{
      allBtns[cp.correct_index].classList.add('correct');
    }}
  }}

  const scorePct = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 100;
  scoreDisplay.textContent = scorePct;
  if (scormAPI) {{
    scormAPI.LMSSetValue("cmi.core.score.raw", String(scorePct));
    scormAPI.LMSCommit("");
  }}
  btnContinue.style.display = 'inline-block';
}}

btnContinue.onclick = () => {{
  overlay.style.display = 'none';
  video.play();
}};
</script>
</body>
</html>
"""

MANIFEST_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{identifier}" version="1.2"
          xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
                              http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="org_default">
    <organization identifier="org_default">
      <title>{title}</title>
      <item identifier="item_01" identifierref="res_01">
        <title>{title}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res_01" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>{extra_files}
    </resource>
  </resources>
</manifest>
"""


def _format_time_str(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def build_scorm_package(
    title: str,
    video_url: str,
    checkpoints: list[dict[str, Any]],
    output_zip: str,
    *,
    include_video_file: Optional[str] = None,
    audio_timeline_path: Optional[str] = None,
    strict_sync: bool = False,
    theme: Optional[dict[str, Any]] = None,
    also_build_zero_weight: bool = False,
) -> str:
    """Build a compliant SCORM 1.2 zip package.

    Maintains 100% backward compatibility with legacy 4-positional signature.
    """
    out_path = Path(output_zip).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Strict sync verification
    if strict_sync and audio_timeline_path:
        tl_path = Path(audio_timeline_path)
        if tl_path.is_file():
            tl_data = json.loads(tl_path.read_text(encoding="utf-8"))
            scenes = tl_data.get("scenes", [])
            scenes_map = {s["scene_id"]: s for s in scenes}
            for idx, cp in enumerate(checkpoints):
                ts = float(cp.get("timestamp", 0))
                sid = cp.get("scene_id")
                sc = scenes_map.get(sid) or (scenes[idx] if idx < len(scenes) else None)
                if sc and ts < (float(sc.get("end", 0)) - 0.05):
                    raise ValueError(
                        f"Checkpoint #{idx+1} at {ts:.2f}s violates strict_sync: "
                        f"cuts scene '{sc.get('scene_id')}' speech before end ({sc.get('end')}s)."
                    )

    # Format time strings on checkpoints
    cps_formatted = []
    for cp in checkpoints:
        cp_copy = dict(cp)
        if "time_str" not in cp_copy and "timestamp" in cp_copy:
            cp_copy["time_str"] = _format_time_str(float(cp_copy["timestamp"]))
        cps_formatted.append(cp_copy)

    identifier = "educai_scorm_" + re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())[:24]

    # Decide primary package contents
    video_basename = Path(include_video_file).name if include_video_file else video_url
    video_src = video_basename if include_video_file else video_url
    extra_files = f'\n      <file href="{video_basename}"/>' if include_video_file else ""

    html_content = (
        SCORM_HTML_TEMPLATE.replace("{title}", title)
        .replace("{video_src}", video_src)
        .replace("{checkpoints_json}", json.dumps(cps_formatted, ensure_ascii=False))
    )

    manifest_content = (
        MANIFEST_XML_TEMPLATE.replace("{identifier}", identifier)
        .replace("{title}", title)
        .replace("{extra_files}", extra_files)
    )

    # Write main package
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", html_content)
        zf.writestr("imsmanifest.xml", manifest_content)
        if include_video_file and Path(include_video_file).is_file():
            zf.write(include_video_file, arcname=video_basename)

    size_kb = out_path.stat().st_size / 1024
    print(f"[OK] Paquete SCORM 1.2 creado: {out_path} ({size_kb:.1f} KB)")

    # Dual packaging: if requested and video was bundled, emit Zero-Weight package as well
    if also_build_zero_weight and include_video_file:
        zero_name = out_path.name
        if "_SCORM_Completo.zip" in zero_name:
            zero_name = zero_name.replace("_SCORM_Completo.zip", "_SCORM.zip")
        else:
            zero_name = out_path.stem + "_ZeroWeight.zip"
        zero_zip_path = out_path.with_name(zero_name)

        zero_html = (
            SCORM_HTML_TEMPLATE.replace("{title}", title)
            .replace("{video_src}", video_url)
            .replace("{checkpoints_json}", json.dumps(cps_formatted, ensure_ascii=False))
        )
        zero_manifest = (
            MANIFEST_XML_TEMPLATE.replace("{identifier}", identifier + "_zw")
            .replace("{title}", title)
            .replace("{extra_files}", "")
        )

        with zipfile.ZipFile(zero_zip_path, "w", zipfile.ZIP_DEFLATED) as zf_zero:
            zf_zero.writestr("index.html", zero_html)
            zf_zero.writestr("imsmanifest.xml", zero_manifest)

        zero_size_kb = zero_zip_path.stat().st_size / 1024
        print(f"[OK] Paquete SCORM 1.2 Zero-Weight creado: {zero_zip_path} ({zero_size_kb:.1f} KB)")

    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generador de paquete SCORM 1.2 interactivo para Moodle (EducAI)."
    )
    parser.add_argument("--title", required=True, help="Título del curso/lección")
    parser.add_argument(
        "--video-url",
        required=True,
        help="URL o nombre de archivo del video MP4",
    )
    parser.add_argument(
        "--checkpoints-json",
        required=True,
        help="Ruta al archivo JSON con las preguntas y timestamps",
    )
    parser.add_argument(
        "--output", "-o", default="paquete_scorm.zip", help="Archivo .zip de salida"
    )
    parser.add_argument(
        "--include-video",
        help="Ruta local al archivo .mp4 para empaquetarlo dentro del ZIP (autocontenido)",
    )
    parser.add_argument(
        "--audio-timeline",
        help="Ruta a audio_timeline.json para verificar sincronía de preguntas",
    )
    parser.add_argument(
        "--strict-sync",
        action="store_true",
        help="Rechaza checkpoints que corten alocuciones antes del final de escena",
    )
    parser.add_argument(
        "--dual-zip",
        action="store_true",
        help="Genera tanto el paquete completo como el Zero-Weight",
    )
    args = parser.parse_args()

    with open(args.checkpoints_json, "r", encoding="utf-8") as f:
        cps = json.load(f)

    build_scorm_package(
        args.title,
        args.video_url,
        cps,
        args.output,
        include_video_file=args.include_video,
        audio_timeline_path=args.audio_timeline,
        strict_sync=args.strict_sync,
        also_build_zero_weight=args.dual_zip,
    )
