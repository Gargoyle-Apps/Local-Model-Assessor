"""Tests for generate-stack-handoff.py embedding resolution."""

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMA_SQL = SCRIPTS_DIR / "schema.sql"


def _load_script(name: str):
    module_name = name.replace("-", "_").removesuffix(".py")
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_script("generate-stack-handoff.py")


@pytest.fixture
def empty_assessed_db(tmp_path):
    """Schema only — no embedding role or provisioned clone."""
    db_path = tmp_path / "t.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL.read_text())
    conn.execute(
        "INSERT INTO models (model_id, vram, ctx, class, tps, url, install) "
        "VALUES ('llama3:8b', 8, 4096, 'Daily Driver', 40, 'https://example.com', 'ollama pull llama3:8b')"
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_with_embedding_role(tmp_path):
    db_path = tmp_path / "t.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL.read_text())
    conn.execute(
        "INSERT INTO models (model_id, vram, ctx, class, tps, url, install) "
        "VALUES ('nomic-embed-text:latest', 1, 8192, 'Utility', 100, 'https://example.com', "
        "'ollama pull nomic-embed-text:latest')"
    )
    conn.execute(
        "INSERT INTO role_model (role, variant, model_id) VALUES ('embedding', 'primary', 'nomic-embed-text:latest')"
    )
    conn.commit()
    conn.close()
    return db_path


def test_resolve_raises_when_no_embedding(empty_assessed_db):
    with pytest.raises(mod.EmbeddingResolutionError, match="No embedding model"):
        mod.resolve_embedding_model(empty_assessed_db, active_only=False)


def test_resolve_via_role_model(db_with_embedding_role):
    info = mod.resolve_embedding_model(db_with_embedding_role, active_only=False)
    assert info["alias"] == "nomic-embed-text:latest"
    assert info["source"] == "role_model"


def test_active_only_raises_without_active_provisioned(db_with_embedding_role):
    """--active-only requires is_active=1 provisioned_models row; role_model is not used."""
    with pytest.raises(mod.EmbeddingResolutionError, match="No active"):
        mod.resolve_embedding_model(db_with_embedding_role, active_only=True)
