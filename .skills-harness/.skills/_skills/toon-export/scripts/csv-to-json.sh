#!/usr/bin/env bash
# csv-to-json.sh — CSV header row → JSON array of objects (empty cells → null)
# Usage: csv-to-json.sh <input.csv> [output.json]
# If output omitted, writes alongside input with .json extension.
# Exit 0 on success.

set -euo pipefail

IN="${1:-}"
OUT="${2:-}"

if [[ -z "$IN" || ! -f "$IN" ]]; then
  echo "usage: csv-to-json.sh <input.csv> [output.json]" >&2
  exit 1
fi

if [[ -z "$OUT" ]]; then
  OUT="${IN%.csv}.json"
fi

python3 - "$IN" "$OUT" <<'PY'
import csv
import json
import sys
from pathlib import Path

src, dst = sys.argv[1], sys.argv[2]
with Path(src).open(newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    rows = [{k: (v if v != "" else None) for k, v in row.items()} for row in reader]
Path(dst).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
PY

echo "wrote $OUT" >&2
