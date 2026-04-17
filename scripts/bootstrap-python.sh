#!/usr/bin/env bash
# Create/update repo-local .venv and install requirements.txt (PEP 668-safe).
# Run from repo root or any cwd; idempotent. See lma-python-env skill.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
  echo "Error: Python >= 3.9 is required (found $(python3 --version 2>&1 || echo 'none'))." >&2
  exit 1
fi
REQ="$ROOT/requirements.txt"
VENV="$ROOT/.venv"
STAMP="$VENV/.lma-reqs-stamp"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Local Model Assessor: creating .venv (gitignored) ..." >&2
  python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install -U pip >/dev/null
"$VENV/bin/pip" install -r "$REQ"
touch "$STAMP"
echo "Python deps ready. Use: ./scripts/py scripts/<script>.py ..." >&2
