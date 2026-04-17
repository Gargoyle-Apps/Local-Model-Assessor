"""Test that migrate-schema.sh is idempotent: running it twice produces identical schema."""

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATE_SCRIPT = REPO_ROOT / "scripts" / "migrate-schema.sh"


def _schema_snapshot(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")
    rows = [row[0] for row in c.fetchall()]
    conn.close()
    return "\n".join(rows)


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "model-data" / "model-assessor.db"
    path.parent.mkdir(parents=True)
    schema = REPO_ROOT / "scripts" / "schema.sql"
    conn = sqlite3.connect(str(path))
    conn.executescript(schema.read_text())
    conn.close()
    return path


def test_migrate_idempotent(db_path):
    """Migrate must target LMA_DB only — never the repo default DB under test."""
    env = {
        **subprocess.os.environ,
        "PATH": subprocess.os.environ.get("PATH", ""),
        "LMA_DB": str(db_path.resolve()),
    }

    def run_migrate():
        return subprocess.run(
            ["bash", str(MIGRATE_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
        )

    snap_before = _schema_snapshot(db_path)
    r1 = run_migrate()
    assert r1.returncode == 0, f"migrate stderr:\n{r1.stderr}\nstdout:\n{r1.stdout}"
    snap_after_1 = _schema_snapshot(db_path)
    r2 = run_migrate()
    assert r2.returncode == 0, f"migrate stderr:\n{r2.stderr}\nstdout:\n{r2.stdout}"
    snap_after_2 = _schema_snapshot(db_path)

    assert snap_after_1 == snap_after_2, "Schema changed between first and second migrate run"
    # Full schema from schema.sql + migrate should be stable (migrate is no-op or additive idempotent).
    assert snap_before == snap_after_1, "First migrate run changed schema.sql baseline unexpectedly"
