"""Word timings and neural voice synthesis using Edge-TTS with WordBoundary events."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Optional


def probe_duration(path: Path | str) -> float:
    """Measure exact audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def _run_async(coro):
    """Run an async coroutine safely across different event loop contexts."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


async def _synthesize_scene_async(
    text: str,
    mp3_path: Path,
    voice: str = "es-AR-ElenaNeural",
    rate: str = "-2%",
    pitch: str = "+0Hz",
    volume: str = "+0%",
    emit_word_boundaries: bool = True,
) -> list[dict[str, Any]]:
    import edge_tts

    boundary_type = "WordBoundary" if emit_word_boundaries else "SentenceBoundary"
    comm = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
        boundary=boundary_type,
    )

    word_timings: list[dict[str, Any]] = []
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mp3_path, "wb") as f_audio:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f_audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Convert 100ns units to seconds
                offset_sec = round(chunk.get("offset", 0) / 10_000_000, 3)
                duration_sec = round(chunk.get("duration", 0) / 10_000_000, 3)
                word_timings.append({
                    "text": chunk.get("text", ""),
                    "start": offset_sec,
                    "duration": duration_sec,
                    "end": round(offset_sec + duration_sec, 3),
                })

    return word_timings


def synthesize_scenes_speech(
    scenes: list[dict[str, Any]],
    output_dir: Path | str,
    *,
    voice: str = "es-AR-ElenaNeural",
    rate: str = "-2%",
    pitch: str = "+0Hz",
    volume: str = "+0%",
    inter_scene_pause: float = 0.55,
    emit_word_boundaries: bool = True,
) -> dict[str, Any]:
    """Synthesize speech for a batch of educational scenes, capturing word timings and timeline."""
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    timeline_scenes: list[dict[str, Any]] = []
    all_word_timings: dict[str, list[dict[str, Any]]] = {}

    current_offset = 0.0

    for idx, sc in enumerate(scenes, 1):
        scene_id = sc.get("id") or f"scene_{idx:02d}"
        narration = (sc.get("narration") or sc.get("script") or sc.get("text") or "").strip()
        if not narration:
            continue

        mp3_name = f"{scene_id}.mp3"
        mp3_path = out_dir / mp3_name

        words = _run_async(
            _synthesize_scene_async(
                narration,
                mp3_path,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume,
                emit_word_boundaries=emit_word_boundaries,
            )
        )

        dur = probe_duration(mp3_path)
        if dur == 0.0 and words:
            dur = words[-1]["end"]

        sc_entry = {
            "scene_id": scene_id,
            "scene_index": idx,
            "title": sc.get("title", f"Escena {idx}"),
            "audio_file": mp3_name,
            "start": round(current_offset, 3),
            "duration": round(dur, 3),
            "end": round(current_offset + dur, 3),
        }
        timeline_scenes.append(sc_entry)
        all_word_timings[scene_id] = words

        current_offset += dur + inter_scene_pause

    total_duration = round(current_offset - inter_scene_pause if current_offset > 0 else 0.0, 3)

    timeline_data = {
        "voice": voice,
        "rate": rate,
        "inter_scene_pause": inter_scene_pause,
        "total_duration": total_duration,
        "scenes": timeline_scenes,
    }

    # Save metadata files
    timeline_path = out_dir / "audio_timeline.json"
    timeline_path.write_text(json.dumps(timeline_data, indent=2, ensure_ascii=False), encoding="utf-8")

    word_timings_path = out_dir / "word_timings.json"
    word_timings_path.write_text(json.dumps(all_word_timings, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "success": True,
        "total_duration": total_duration,
        "scenes": timeline_scenes,
        "timeline_path": str(timeline_path),
        "word_timings_path": str(word_timings_path),
    }
