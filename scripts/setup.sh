#!/usr/bin/env bash
# One-command setup for macOS / Linux / WSL / Git-Bash.   Run:  bash scripts/setup.sh
set -e
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
$PY -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
[ -d .venv ] || $PY -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
[ -f .env ] || { cp .env.example .env; echo "created .env (keys stay blank = demo mode)"; }
python scripts/doctor.py || true
python -m pytest -q
echo
echo "READY.  Start the app with:   source .venv/bin/activate && streamlit run app.py"
