#!/usr/bin/env python3
"""
Insert models from YAML output directly into model-assessor.db.
Used by LLM-prompts/model-assessment-prompt.yaml: LLM outputs YAML → pipe to this script.

Usage:
  python scripts/add-model-from-yaml.py model-data/new-models.yaml
  python scripts/add-model-from-yaml.py   # defaults to model-data/new-models.yaml if it exists
  python scripts/add-model-from-yaml.py < assessment-output.yaml
  # Script extracts from ```yaml ... ``` blocks if present
"""

import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "model-data" / "model-assessor.db"
DEFAULT_YAML = REPO_ROOT / "model-data" / "new-models.yaml"


def _truthy(v):
    return v in (True, 1, "true", "1", "yes")


def load_yaml(content: str) -> dict:
    """Parse YAML, optionally extracting from markdown code block."""
    content = content.strip()
    match = re.search(r"^```yaml\s*\n(.*?)```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    return yaml.safe_load(content) or {}


def _models_has_assessed_at(c) -> bool:
    c.execute("PRAGMA table_info(models)")
    return any(row[1] == "assessed_at" for row in c.fetchall())


def insert_model(c, model_id: str, m: dict) -> None:
    values = (
        model_id,
        float(m.get("vram", 0)),
        int(m.get("ctx", 0)),
        str(m.get("class", "")),
        int(m.get("tps", 0)),
        str(m.get("url", "")),
        str(m.get("install", "")),
        1 if _truthy(m.get("vision")) else 0,
        1 if _truthy(m.get("tools")) else 0,
        1 if _truthy(m.get("reasoning")) else 0,
        1 if _truthy(m.get("moe")) else 0,
        1 if _truthy(m.get("fim")) else 0,
        1 if _truthy(m.get("structured")) else 0,
        m.get("creative"),
        1 if _truthy(m.get("multilingual")) else 0,
        1 if _truthy(m.get("rag")) else 0,
        1 if _truthy(m.get("no_corun")) else 0,
        m.get("latency"),
    )
    if _models_has_assessed_at(c):
        assessed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            """
            INSERT OR REPLACE INTO models
            (model_id, vram, ctx, class, tps, url, install,
             vision, tools, reasoning, moe, fim, structured, creative,
             multilingual, rag, no_corun, latency, assessed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values + (assessed_at,),
        )
    else:
        c.execute(
            """
            INSERT OR REPLACE INTO models
            (model_id, vram, ctx, class, tps, url, install,
             vision, tools, reasoning, moe, fim, structured, creative,
             multilingual, rag, no_corun, latency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )


def insert_role(c, role: str, variant: str, model_id: str, notes: str = None) -> None:
    c.execute(
        "INSERT OR REPLACE INTO role_model (role, variant, model_id, notes) VALUES (?, ?, ?, ?)",
        (role, variant, model_id, notes),
    )


def insert_constraint(c, constraint_name: str, model_id: str, sort_order: int = 0) -> None:
    c.execute(
        "INSERT OR IGNORE INTO constraint_model (constraint_name, model_id, sort_order) VALUES (?, ?, ?)",
        (constraint_name, model_id, sort_order),
    )


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        content = path.read_text()
    elif DEFAULT_YAML.exists():
        content = DEFAULT_YAML.read_text()
    else:
        content = sys.stdin.read()

    data = load_yaml(content)
    if not data:
        print("Error: No YAML data found.", file=sys.stderr)
        sys.exit(1)

    db_path = Path(os.environ.get("LMA_DB", str(DEFAULT_DB)))
    if not db_path.exists():
        print(f"Error: {db_path} not found. Run init-db.sh first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        for model_id, m in (data.get("models") or {}).items():
            if str(model_id).startswith("_"):
                continue
            if not isinstance(m, dict):
                continue
            insert_model(c, model_id, m)
            print(f"Added/updated model: {model_id}")

        for role, variants in (data.get("by_role") or {}).items():
            for variant, val in (variants or {}).items():
                model_id = val.get("primary", val) if isinstance(val, dict) else val
                notes = val.get("notes") if isinstance(val, dict) else None
                if model_id and not str(model_id).startswith("_"):
                    insert_role(c, role, variant, str(model_id), notes)

        for constraint_name, model_ids in (data.get("by_constraint") or {}).items():
            for i, model_id in enumerate(model_ids or []):
                if model_id:
                    insert_constraint(c, constraint_name, model_id, i)

        for model_id, doc in (data.get("model_docs") or {}).items():
            if str(model_id).startswith("_"):
                continue
            if not isinstance(doc, dict):
                continue
            c.execute(
                """
                INSERT OR REPLACE INTO model_docs (model_id, spec_table, description, best_for, caveats, creative_tier)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    model_id,
                    doc.get("spec_table") or "",
                    doc.get("description") or "",
                    doc.get("best_for") or "",
                    doc.get("caveats") or "",
                    doc.get("creative_tier"),
                ),
            )

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

    print("Done. Run: python scripts/export-assessed-models.py  # to update assessed-models.md")


if __name__ == "__main__":
    main()
