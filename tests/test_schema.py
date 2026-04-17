"""Tests for schema.sql: DDL loads, tables exist, provenance columns present."""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "scripts" / "schema.sql"

CONTENT_TABLES = [
    "models", "role_model", "constraint_model", "task_category", "model_docs",
    "provisioned_models",
]
CONFIG_TABLES = ["meta", "hardware_profile", "software_profile"]
ALL_TABLES = CONTENT_TABLES + CONFIG_TABLES + ["decision_tree", "rag_pipeline"]


def _fresh_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def test_ddl_loads_cleanly():
    conn = _fresh_db()
    conn.close()


def test_expected_tables_exist():
    conn = _fresh_db()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    actual = {row[0] for row in c.fetchall()}
    for t in ALL_TABLES:
        assert t in actual, f"Missing table: {t}"
    conn.close()


def test_content_tables_have_provenance():
    provenance_cols = {"created_at", "created_by", "created_by_type",
                       "updated_at", "updated_by", "updated_by_type"}
    conn = _fresh_db()
    c = conn.cursor()
    for table in CONTENT_TABLES:
        c.execute(f"PRAGMA table_info({table})")
        cols = {row[1] for row in c.fetchall()}
        missing = provenance_cols - cols
        assert not missing, f"{table} missing provenance columns: {missing}"
    conn.close()


def test_config_tables_lack_provenance():
    provenance_cols = {"created_by", "created_by_type"}
    conn = _fresh_db()
    c = conn.cursor()
    for table in CONFIG_TABLES:
        c.execute(f"PRAGMA table_info({table})")
        cols = {row[1] for row in c.fetchall()}
        overlap = provenance_cols & cols
        assert not overlap, f"{table} should not have provenance: {overlap}"
    conn.close()
