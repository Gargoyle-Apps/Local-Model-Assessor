"""End-to-end ingestion: seed YAML → add-model-from-yaml.py → verify DB rows."""

import importlib.util
import sqlite3
import subprocess
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


mod = _load_script("add-model-from-yaml.py")

SEED_YAML = """\
models:
  test-model:7b:
    vram: 8
    ctx: 32768
    class: Middleweight
    tps: 45
    url: https://example.com
    install: ollama pull test-model:7b
    provisioning:
      - alias: "test-model:7b_coding_8k"
        role: coding
        variant: primary
        num_ctx: 8192
        temperature: 0.2

by_role:
  coding:
    primary: test-model:7b

by_constraint:
  has_tools: [test-model:7b]

model_docs:
  test-model:7b:
    description: "Test model."
    best_for: "Testing"
    caveats: "None"

by_task_category:
  writing:
    - creative
    - generalist
  analysis:
    - reasoning

decision_tree:
  need_vision: "vision → generalist"
  need_speed: "autocomplete → coding"

rag_pipeline:
  default:
    embedding_model: "test-embed:latest"
    generation_model: "test-model:7b"
    notes: "Test pipeline"
"""


@pytest.fixture
def seeded_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL.read_text())
    conn.close()
    return db_path


def _run_ingestion(db_path: Path, yaml_content: str = SEED_YAML):
    yaml_file = db_path.parent / "seed.yaml"
    yaml_file.write_text(yaml_content)

    import os
    old_env = os.environ.get("LMA_DB")
    os.environ["LMA_DB"] = str(db_path)
    try:
        sys.argv = ["add-model-from-yaml.py", str(yaml_file)]
        mod.main()
    finally:
        if old_env is None:
            os.environ.pop("LMA_DB", None)
        else:
            os.environ["LMA_DB"] = old_env


def test_models_inserted(seeded_db):
    _run_ingestion(seeded_db)
    conn = sqlite3.connect(str(seeded_db))
    c = conn.cursor()
    c.execute("SELECT model_id, vram, class FROM models WHERE model_id='test-model:7b'")
    row = c.fetchone()
    assert row is not None
    assert row[1] == 8.0
    assert row[2] == "Middleweight"
    conn.close()


def test_role_model_inserted(seeded_db):
    _run_ingestion(seeded_db)
    conn = sqlite3.connect(str(seeded_db))
    c = conn.cursor()
    c.execute("SELECT model_id FROM role_model WHERE role='coding' AND variant='primary'")
    row = c.fetchone()
    assert row is not None
    assert row[0] == "test-model:7b"
    conn.close()


def test_task_category_inserted(seeded_db):
    _run_ingestion(seeded_db)
    conn = sqlite3.connect(str(seeded_db))
    c = conn.cursor()
    c.execute("SELECT role_name FROM task_category WHERE category='writing' ORDER BY sort_order")
    rows = [r[0] for r in c.fetchall()]
    assert rows == ["creative", "generalist"]
    conn.close()


def test_decision_tree_inserted(seeded_db):
    _run_ingestion(seeded_db)
    conn = sqlite3.connect(str(seeded_db))
    c = conn.cursor()
    c.execute("SELECT chain_text FROM decision_tree WHERE need_key='need_vision'")
    row = c.fetchone()
    assert row is not None
    assert "vision" in row[0]
    conn.close()


def test_rag_pipeline_inserted(seeded_db):
    _run_ingestion(seeded_db)
    conn = sqlite3.connect(str(seeded_db))
    c = conn.cursor()
    c.execute("SELECT embedding_model, generation_model FROM rag_pipeline WHERE pipeline_name='default'")
    row = c.fetchone()
    assert row is not None
    assert row[0] == "test-embed:latest"
    assert row[1] == "test-model:7b"
    conn.close()


def test_triple_quote_rejection_via_subprocess(seeded_db, tmp_path):
    """Triple-quote in system_prompt should cause failure."""
    bad_yaml = """\
models:
  bad:model:
    vram: 4
    ctx: 4096
    class: Speedster
    tps: 100
    url: https://example.com
    install: ollama pull bad:model
    provisioning:
      - alias: "bad:model_coding_4k"
        role: coding
        variant: primary
        num_ctx: 4096
        system_prompt: |
          Line one
          Contains triple \"\"\" quotes
          Line three
"""
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(bad_yaml)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "add-model-from-yaml.py"), str(yaml_file)],
        capture_output=True, text=True,
        env={**subprocess.os.environ, "LMA_DB": str(seeded_db)},
    )
    assert result.returncode != 0
