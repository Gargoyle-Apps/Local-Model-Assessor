#!/usr/bin/env bash
# encode-from-json.sh — JSON → TOON via official CLI, then validate
# Usage: encode-from-json.sh <input.json> [output.toon]
# If output omitted, writes alongside input with .toon extension.
# Exit 0 on success.

set -euo pipefail

IN="${1:-}"
OUT="${2:-}"

if [[ -z "$IN" || ! -f "$IN" ]]; then
  echo "usage: encode-from-json.sh <input.json> [output.toon]" >&2
  exit 1
fi

if [[ -z "$OUT" ]]; then
  OUT="${IN%.json}.toon"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "encode: $IN → $OUT" >&2
pnpm dlx @toon-format/cli "$IN" -o "$OUT"
"$SCRIPT_DIR/validate-toon.sh" "$OUT"
echo "wrote $OUT" >&2
