"""Cross-platform environment checker and dependency installer for Lemo-Opuscar.
Replaces Unix setup.sh with full Windows (PowerShell / CMD) and POSIX compatibility.
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent

def check_command(cmd, name, install_hint=""):
    path = shutil.which(cmd)
    if path:
        print(f"[OK] {name}: found at {path}")
        return True
    else:
        print(f"[MISSING] {name}: not found. {install_hint}")
        return False

def check_system():
    print(f"Checking environment for Lemo-Opuscar at: {PLUGIN_ROOT}\n")
    ok = True
    ok &= check_command("node", "Node.js (v20+ recommended)", "Download from https://nodejs.org/")
    ok &= check_command("npm", "npm", "Installed with Node.js")
    ok &= check_command("ffmpeg", "FFmpeg", "Install via `winget install Gyan.FFmpeg` or download from https://ffmpeg.org/")
    
    # Python version check
    py_ver = sys.version_info
    if py_ver >= (3, 11):
        print(f"[OK] Python: {py_ver.major}.{py_ver.minor}.{py_ver.micro} (>= 3.11)")
    else:
        print(f"[WARN] Python: {py_ver.major}.{py_ver.minor}.{py_ver.micro} (Python 3.11+ recommended)")
        ok = False
        
    return ok

def install_deps(tiers=None):
    if tiers is None:
        tiers = ["core"]
    print(f"Installing dependencies for tiers: {', '.join(tiers)}...")
    
    # 1. npm install
    if shutil.which("npm"):
        print("\n--> Running npm install in plugin directory...")
        subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=PLUGIN_ROOT, check=False)
        
        # 2. Playwright chromium headless shell
        playwright_cli = PLUGIN_ROOT / "node_modules" / "playwright-core" / "cli.js"
        if playwright_cli.exists() and shutil.which("node"):
            print("--> Installing Playwright Chromium headless shell...")
            subprocess.run(["node", str(playwright_cli), "install", "chromium-headless-shell"], cwd=PLUGIN_ROOT, check=False)
    else:
        print("[ERROR] npm is required to install core dependencies.")
        return False

    # 3. Python dependencies
    req_file = PLUGIN_ROOT / "requirements.txt"
    if req_file.exists():
        print("--> Installing Python requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)], check=False)

    if "voice" in tiers:
        voice_req = PLUGIN_ROOT / "requirements-voice.txt"
        if voice_req.exists():
            print("--> Installing voice requirements (TTS)...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(voice_req)], check=False)

    if "music" in tiers:
        music_req = PLUGIN_ROOT / "requirements-music.txt"
        if music_req.exists():
            print("--> Installing music requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(music_req)], check=False)

    print("\nDependency installation completed.")
    return True

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    if action == "check":
        check_system()
    elif action == "deps":
        tiers = sys.argv[2:] if len(sys.argv) > 2 else ["core"]
        install_deps(tiers)
    else:
        print("Usage: python setup.py [check | deps [voice] [music]]")
