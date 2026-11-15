#!/usr/bin/env bash
# One launcher for the tutor. Run it from anywhere:
#
#   ./run.sh real      start the web app with the real AI model (needs Ollama)
#   ./run.sh doctor    check this machine is ready, with a fix for anything that is not
#   ./run.sh bench     measure how fast a model is on this machine (default: the model in .env)
#   ./run.sh setup     create the virtualenv and install the Python packages
#
# Add --port 8010 after "real" to use another port. Windows: see README.
set -euo pipefail
cd "$(dirname "$0")"

PY=".venv/bin/python"
need_venv() {
  if [ ! -x "$PY" ]; then
    echo "No virtualenv yet. Run:  ./run.sh setup" >&2
    exit 1
  fi
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  setup)
    python3 -m venv .venv || { echo "Could not create the virtualenv. On Ubuntu run:  sudo apt install -y python3-venv" >&2; exit 1; }
    "$PY" -m pip install --upgrade pip
    "$PY" -m pip install -r requirements.txt
    [ -f .env ] || cp .env.example .env
    echo "Setup done. Next:  ./run.sh doctor"
    ;;
  real)
    need_venv
    port=8000
    if [ "${1:-}" = "--port" ]; then port="$2"; fi
    echo "Tutor starting at http://127.0.0.1:${port}  (Ctrl+C to stop)"
    exec "$PY" -m uvicorn backend.api.server:app --host 127.0.0.1 --port "$port"
    ;;
  doctor)
    if [ -x "$PY" ]; then exec "$PY" backend/tools/doctor.py "$@"; else exec python3 backend/tools/doctor.py "$@"; fi
    ;;
  bench)
    model="${1:-}"
    if [ -z "$model" ] && [ -f .env ]; then model="$(grep -E '^(TUTOR_MODEL|TUTOR_PLANNER_MODEL)=' .env | head -1 | cut -d= -f2)"; fi
    [ -n "$model" ] || { echo "Usage: ./run.sh bench <model>   e.g. ./run.sh bench gemma4:e2b" >&2; exit 1; }
    exec python3 backend/tools/bench_llm.py --model "$model"
    ;;
  *)
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
    ;;
esac
