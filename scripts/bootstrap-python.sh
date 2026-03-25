#!/usr/bin/env bash
# Create/update repo-local .venv and install requirements.txt (PEP 668-safe).
# Run from repo root or any cwd; idempotent. See AGENTS.md "Python environment".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
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
