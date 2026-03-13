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
  local exists
  exists=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM pragma_table_info('$table') WHERE name='$col'")
  if [ "$exists" -gt 0 ]; then
    echo "  $table.$col already exists"
  else
    echo "  Adding $table.$col"
    sqlite3 "$DB_PATH" "ALTER TABLE $table ADD COLUMN $col $def"
  fi
}

add_provenance() {
  local table="$1"
  echo "  Provenance columns for $table..."
  add_col_if_missing "$table" "created_at" "TEXT"
  add_col_if_missing "$table" "created_by" "TEXT"
  add_col_if_missing "$table" "created_by_type" "TEXT"
  add_col_if_missing "$table" "updated_at" "TEXT"
  add_col_if_missing "$table" "updated_by" "TEXT"
  add_col_if_missing "$table" "updated_by_type" "TEXT"
}

echo "Migrating schema..."
add_col_if_missing "models" "assessed_at" "TEXT"

add_provenance "models"
add_provenance "role_model"
add_provenance "constraint_model"
add_provenance "task_category"
add_provenance "model_docs"
echo "Done."
