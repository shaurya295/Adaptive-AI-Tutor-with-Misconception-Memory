"""
doctor.py
---------
Checks that this machine is ready to run the tutor, and says what to do about
anything that is not. Standard library only, so it works before (and after)
the virtualenv exists.

    python3 backend/tools/doctor.py          # full check
    python3 backend/tools/doctor.py --dev    # also check the tools only developers need
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "dotenv", "langgraph", "langchain_core", "langchain_ollama", "langchain_chroma"]
MODEL_VARS = ["TUTOR_MODEL", "TUTOR_PLANNER_MODEL"]

OK, WARN, BAD = "ok", "warn", "bad"
MARK = {OK: "✓", WARN: "!", BAD: "✗"}
results: list[tuple[str, str, str]] = []


def report(level: str, what: str, fix: str = "") -> None:
    results.append((level, what, fix))
    print(f" {MARK[level]} {what}" + (f"\n     → {fix}" if fix and level != OK else ""))


def read_env() -> dict[str, str]:
    env = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def meminfo_mb() -> dict[str, int]:
    out = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            out[k] = int(v.split()[0]) // 1024
    except OSError:
        pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Check this machine is ready to run the tutor.")
    ap.add_argument("--dev", action="store_true", help="also check Node.js and Chrome (needed only to change the gamified UI or run visual tests)")
    args = ap.parse_args()
    env = read_env()
    print(f"Project: {ROOT}\n")

    # Python and virtualenv
    v = sys.version_info
    report(OK if v >= (3, 11) else BAD, f"Python {v.major}.{v.minor}.{v.micro}", "Python 3.11 or newer is required.")
    in_venv = sys.prefix != sys.base_prefix
    venv_dir = ROOT / ".venv"
    if in_venv:
        report(OK, "Running inside a virtualenv")
    elif venv_dir.exists():
        report(WARN, "A virtualenv exists but is not active", "Run: source .venv/bin/activate   (or use ./run.sh, which does it for you)")
    else:
        report(BAD, "No virtualenv yet", "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   (needs: sudo apt install -y python3-venv)")

    missing = [p for p in PACKAGES if importlib.util.find_spec(p) is None]
    if not missing:
        report(OK, "Python packages installed")
    else:
        report(BAD if in_venv else WARN, "Missing Python packages: " + ", ".join(missing), "Run: .venv/bin/pip install -r requirements.txt")

    # Configuration
    has_env = (ROOT / ".env").exists()
    report(OK if has_env else WARN, ".env file " + ("present" if has_env else "missing"), "Run: cp .env.example .env   (the defaults work for a local Ollama)")

    # Ollama and models
    base = os.environ.get("OLLAMA_BASE_URL") or env.get("OLLAMA_BASE_URL") or "http://localhost:11434"
    wanted = {os.environ.get(k) or env.get(k) for k in MODEL_VARS} - {None, ""}
    embed = os.environ.get("EMBED_MODEL") or env.get("EMBED_MODEL") or "nomic-embed-text"
    try:
        tags = json.load(urllib.request.urlopen(base + "/api/tags", timeout=5))
        have = {m["name"] for m in tags.get("models", [])}
        report(OK, f"Ollama is running at {base} ({len(have)} model(s) installed)")
        for name in sorted(wanted | {embed}):
            present = name in have or f"{name}:latest" in have
            report(OK if present else BAD, f"Model {name}", f"Run: ollama pull {name}")
        if not wanted:
            report(WARN, "No tutor model named in .env", "Set TUTOR_MODEL in .env (for example gemma4:e2b).")
    except Exception as exc:  # noqa: BLE001
        report(BAD, f"Ollama is not reachable at {base} ({type(exc).__name__})", "Start it with: sudo systemctl start ollama   (demo mode works without it)")

    # Memory
    mem = meminfo_mb()
    if mem:
        avail, swap = mem.get("MemAvailable", 0), mem.get("SwapFree", 0)
        level = OK if avail >= 5500 else WARN
        report(level, f"Memory: {avail} MB free of {mem.get('MemTotal', 0)} MB, {swap} MB swap free", "Close other apps before using a real model; a 4B model needs about 5.5 GB.")

    # Port and data folder
    with socket.socket() as s:
        busy = s.connect_ex(("127.0.0.1", 8000)) == 0
    report(WARN if busy else OK, "Port 8000 is " + ("already in use" if busy else "free"), "Another server is running on port 8000; stop it or use: ./run.sh real --port 8010")
    data = ROOT / "backend" / "data"
    try:
        data.mkdir(parents=True, exist_ok=True)
        probe = data / ".write-test"
        probe.write_text("ok")
        probe.unlink()
        report(OK, "Data folder is writable (backend/data)")
    except OSError as exc:
        report(BAD, f"Cannot write to backend/data ({exc})", "Check folder permissions.")

    if args.dev:
        node = shutil.which("node")
        if node:
            ver = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
            nums = tuple(int(x) for x in ver.lstrip("v").split(".")[:2])
            report(OK if nums >= (22, 12) else BAD, f"Node.js {ver}", "Vite needs Node 22.12 or newer: sudo snap install node --classic --channel=24/stable")
        else:
            report(WARN, "Node.js not installed", "Only needed to change the gamified UI: sudo snap install node --classic --channel=24/stable")
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        report(OK if chrome else WARN, "Chrome for visual tests" + (f" ({chrome})" if chrome else " not found"), "Install Google Chrome to run the screenshot comparison.")

    bad = sum(1 for r in results if r[0] == BAD)
    warn = sum(1 for r in results if r[0] == WARN)
    print(f"\n{'Ready.' if not bad else 'Not ready yet.'}  {bad} problem(s), {warn} warning(s).")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
