"""Pre-render composition validator gate for EducAI."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional


def _probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return float(res.stdout.strip())


def validate_pre_render(
    project_dir: str | Path,
    *,
    render_mode: str = "canvas",
    html_entry: str = "index.html",
    timeline_file: str = "audio_timeline.json",
    audio_file: str = "audio_mixed.m4a",
    checkpoints_file: Optional[str] = "scorm_checkpoints.json",
) -> dict[str, Any]:
    """Execute pre-render quality checks enforcing EducAI standards.

    Checks:
    - Asset existence and non-zero sizes.
    - Synchrony between audio_mixed duration and audio_timeline total_duration (<= 0.5s).
    - SCORM checkpoint synchronization (checkpoint must NOT cut voiceover before scene end).
    - Canvas determinism & zero console/page errors across 5 timestamps via Playwright (if installed).
    """
    pdir = Path(project_dir).resolve()
    issues: list[str] = []
    details: dict[str, Any] = {
        "project_dir": str(pdir),
        "render_mode": render_mode,
        "checks_passed": [],
    }

    # 1. Timeline check
    timeline_path = pdir / timeline_file
    timeline_data: dict[str, Any] = {}
    if not timeline_path.is_file() or timeline_path.stat().st_size == 0:
        issues.append(f"Missing or empty audio timeline: {timeline_file}")
    else:
        try:
            timeline_data = json.loads(timeline_path.read_text(encoding="utf-8"))
            details["checks_passed"].append("timeline_valid_json")
        except Exception as exc:
            issues.append(f"Invalid JSON in {timeline_file}: {exc}")

    # 2. Audio file check & duration matching
    audio_path = pdir / audio_file
    if not audio_path.is_file() or audio_path.stat().st_size == 0:
        issues.append(f"Missing or empty audio file: {audio_file}")
    elif timeline_data and "total_duration" in timeline_data:
        try:
            real_audio_dur = _probe_duration(audio_path)
            expected_dur = float(timeline_data["total_duration"])
            details["audio_duration"] = real_audio_dur
            details["timeline_duration"] = expected_dur
            diff = abs(real_audio_dur - expected_dur)
            if diff > 0.5:
                issues.append(
                    f"Audio duration mismatch: {audio_file} is {real_audio_dur:.2f}s, "
                    f"timeline expected {expected_dur:.2f}s (difference {diff:.2f}s > 0.5s)"
                )
            else:
                details["checks_passed"].append("audio_duration_sync")
        except Exception as exc:
            issues.append(f"Failed to probe duration of {audio_file}: {exc}")

    # 3. Checkpoint alignment verification (Invariante 1: No cortar voz)
    checkpoints: list[dict[str, Any]] = []
    if checkpoints_file:
        cp_path = pdir / checkpoints_file
        if cp_path.is_file() and cp_path.stat().st_size > 0:
            try:
                checkpoints = json.loads(cp_path.read_text(encoding="utf-8"))
            except Exception as exc:
                issues.append(f"Invalid JSON in {checkpoints_file}: {exc}")

    if not checkpoints and timeline_data.get("scenes"):
        for sc in timeline_data["scenes"]:
            for cp in sc.get("checkpoints", []):
                cp_copy = dict(cp)
                cp_copy.setdefault("scene_id", sc.get("scene_id"))
                checkpoints.append(cp_copy)

    if checkpoints and timeline_data.get("scenes"):
        scenes_map = {s["scene_id"]: s for s in timeline_data["scenes"]}
        for idx, cp in enumerate(checkpoints):
            ts = float(cp.get("timestamp", 0))
            sid = cp.get("scene_id")
            if sid and sid in scenes_map:
                sc = scenes_map[sid]
                sc_end = float(sc.get("end", 0))
                if ts < (sc_end - 0.05):
                    issues.append(
                        f"Checkpoint #{idx+1} at {ts:.2f}s cuts scene '{sid}' speech "
                        f"before end ({sc_end:.2f}s). Must be >= {sc_end:.2f}s."
                    )
            elif idx < len(timeline_data["scenes"]):
                sc = timeline_data["scenes"][idx]
                sc_end = float(sc.get("end", 0))
                if ts < (sc_end - 0.05):
                    issues.append(
                        f"Checkpoint #{idx+1} at {ts:.2f}s cuts scene #{idx+1} speech "
                        f"before end ({sc_end:.2f}s)."
                    )
        if not any("cuts scene" in isue for isue in issues):
            details["checks_passed"].append("scorm_checkpoints_strictly_aligned")

    # 4. Canvas mode checks
    if render_mode == "canvas":
        entry_file = pdir / html_entry
        if not entry_file.is_file():
            issues.append(f"Missing canvas entry file: {html_entry}")
        else:
            html_content = entry_file.read_text(encoding="utf-8", errors="replace")
            if "Math.random(" in html_content and "seed" not in html_content.lower():
                issues.append("Unseeded Math.random() detected in canvas HTML (non-deterministic render risk)")
            if "Date.now(" in html_content:
                issues.append("Date.now() detected in canvas HTML (non-deterministic render risk)")

            # Optional Playwright check if available
            try:
                from playwright.sync_api import sync_playwright

                total_dur = details.get("audio_duration") or timeline_data.get("total_duration") or 5.0
                timestamps = [
                    0.0,
                    round(total_dur * 0.25, 2),
                    round(total_dur * 0.50, 2),
                    round(total_dur * 0.75, 2),
                    round(max(0.0, total_dur - 0.1), 2),
                ]
                page_errors: list[str] = []
                console_errors: list[str] = []

                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page(viewport={"width": 1920, "height": 1080})
                    page.on("pageerror", lambda err: page_errors.append(str(err)))
                    page.on(
                        "console",
                        lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
                    )

                    file_url = entry_file.as_uri()
                    page.goto(file_url, wait_until="networkidle", timeout=10000)

                    for t in timestamps:
                        page.evaluate(f"if (window.render) window.render({t});")

                    browser.close()

                if page_errors:
                    issues.append(f"Playwright detected {len(page_errors)} page errors: {page_errors[:2]}")
                if console_errors:
                    issues.append(f"Playwright detected {len(console_errors)} console errors: {console_errors[:2]}")

                if not page_errors and not console_errors:
                    details["checks_passed"].append("playwright_5pt_evaluation_clean")
            except ImportError:
                details["playwright_note"] = "Playwright not installed; skipped headless 5-point evaluation."
            except Exception as exc:
                issues.append(f"Playwright 5-point evaluation failed: {exc}")

    passed = len(issues) == 0
    return {
        "passed": passed,
        "issues": issues,
        "details": details,
    }
