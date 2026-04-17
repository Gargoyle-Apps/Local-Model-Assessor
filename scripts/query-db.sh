#!/usr/bin/env bash
# Run SQL against model-assessor.db. Examples:
#   ./scripts/query-db.sh "SELECT model_id, vram, class FROM models ORDER BY vram"
#   ./scripts/query-db.sh "SELECT role, variant, model_id FROM role_model WHERE role='coding'"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="${REPO_ROOT}/model-data/model-assessor.db"

if [ ! -f "$DB" ]; then
  echo "Error: $DB not found. Run ./scripts/init-db.sh first." >&2
  exit 1
fi

if [ $# -eq 0 ]; then
  sqlite3 -header -column "$DB"
elif [ $# -eq 1 ]; then
  sqlite3 -header -column "$DB" "$1"
else
  echo "Error: pass SQL as a single quoted string." >&2
  echo "  Good: ./scripts/query-db.sh \"SELECT * FROM models\"" >&2
  echo "  Bad:  ./scripts/query-db.sh SELECT * FROM models" >&2
  exit 2
fi
