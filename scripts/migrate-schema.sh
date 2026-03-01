#!/usr/bin/env bash
# Add schema columns introduced after initial release (assessed_at, etc.)
# Run from repo root: ./scripts/migrate-schema.sh
# Safe to run multiple times; skips if column already exists.

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${REPO_ROOT}/model-data/model-assessor.db"

if [ ! -f "$DB_PATH" ]; then
  echo "No database at $DB_PATH — nothing to migrate."
  exit 0
fi

add_col_if_missing() {
  local table="$1"
  local col="$2"
  local def="$3"
  if sqlite3 "$DB_PATH" "PRAGMA table_info($table)" | grep -q "^[0-9]*|${col}|"; then
    echo "  $table.$col already exists"
  else
    echo "  Adding $table.$col"
    sqlite3 "$DB_PATH" "ALTER TABLE $table ADD COLUMN $col $def"
  fi
}

echo "Migrating schema..."
add_col_if_missing "models" "assessed_at" "TEXT"
echo "Done."
