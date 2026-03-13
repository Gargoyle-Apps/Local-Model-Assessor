#!/usr/bin/env python3
"""
Insert models from YAML output directly into model-assessor.db.
Used by LLM-prompts/model-assessment-prompt.yaml: LLM outputs YAML → pipe to this script.

Usage:
  python scripts/add-model-from-yaml.py model-data/new-models.yaml
  python scripts/add-model-from-yaml.py --assessor gpt-oss:20b --assessor-type local model-data/new-models.yaml
  python scripts/add-model-from-yaml.py   # defaults to model-data/new-models.yaml if it exists
  python scripts/add-model-from-yaml.py < assessment-output.yaml
  # Script extracts from ```yaml ... ``` blocks if present

Provenance (optional):
  --assessor NAME        Model or person that performed the assessment
  --assessor-type TYPE   One of: local, cloud, human
  Also via env: LMA_ASSESSOR, LMA_ASSESSOR_TYPE
"""

import argparse
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


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _has_column(c, table, col) -> bool:
    c.execute(f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='{col}'")
    return c.fetchone()[0] > 0


def load_yaml(content: str) -> dict:
    """Parse YAML, optionally extracting from markdown code block."""
    content = content.strip()
    match = re.search(r"^```yaml\s*\n(.*?)```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    return yaml.safe_load(content) or {}


def insert_model(c, model_id: str, m: dict, assessor: str, assessor_type: str) -> None:
    now = _now()
    has_provenance = _has_column(c, "models", "created_at")

    base_cols = (
        "model_id, vram, ctx, class, tps, url, install, "
        "vision, tools, reasoning, moe, fim, structured, creative, "
        "multilingual, rag, no_corun, latency, assessed_at"
    )
    base_vals = (
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
        now,
    )

    if has_provenance:
        cols = base_cols + ", created_at, created_by, created_by_type, updated_at, updated_by, updated_by_type"
        placeholders = ", ".join(["?"] * 25)
        vals = base_vals + (now, assessor, assessor_type, now, assessor, assessor_type)
        update_set = (
            "vram=excluded.vram, ctx=excluded.ctx, class=excluded.class, "
            "tps=excluded.tps, url=excluded.url, install=excluded.install, "
            "vision=excluded.vision, tools=excluded.tools, reasoning=excluded.reasoning, "
            "moe=excluded.moe, fim=excluded.fim, structured=excluded.structured, "
            "creative=excluded.creative, multilingual=excluded.multilingual, "
            "rag=excluded.rag, no_corun=excluded.no_corun, latency=excluded.latency, "
            "assessed_at=excluded.assessed_at, "
            "updated_at=excluded.updated_at, updated_by=excluded.updated_by, "
            "updated_by_type=excluded.updated_by_type"
        )
        c.execute(
            f"INSERT INTO models ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(model_id) DO UPDATE SET {update_set}",
            vals,
        )
    else:
        placeholders = ", ".join(["?"] * 19)
        c.execute(
            f"INSERT OR REPLACE INTO models ({base_cols}) VALUES ({placeholders})",
            base_vals,
        )


def insert_role(c, role: str, variant: str, model_id: str, notes: str,
                assessor: str, assessor_type: str) -> None:
    now = _now()
    if _has_column(c, "role_model", "created_at"):
        c.execute(
            "INSERT INTO role_model "
            "(role, variant, model_id, notes, created_at, created_by, created_by_type, "
            " updated_at, updated_by, updated_by_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(role, variant) DO UPDATE SET "
            "model_id=excluded.model_id, notes=excluded.notes, "
            "updated_at=excluded.updated_at, updated_by=excluded.updated_by, "
            "updated_by_type=excluded.updated_by_type",
            (role, variant, model_id, notes, now, assessor, assessor_type,
             now, assessor, assessor_type),
        )
    else:
        c.execute(
            "INSERT OR REPLACE INTO role_model (role, variant, model_id, notes) VALUES (?, ?, ?, ?)",
            (role, variant, model_id, notes),
        )


def insert_constraint(c, constraint_name: str, model_id: str, sort_order: int,
                      assessor: str, assessor_type: str) -> None:
    now = _now()
    if _has_column(c, "constraint_model", "created_at"):
        c.execute(
            "INSERT INTO constraint_model "
            "(constraint_name, model_id, sort_order, created_at, created_by, created_by_type, "
            " updated_at, updated_by, updated_by_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(constraint_name, model_id) DO UPDATE SET "
            "sort_order=excluded.sort_order, "
            "updated_at=excluded.updated_at, updated_by=excluded.updated_by, "
            "updated_by_type=excluded.updated_by_type",
            (constraint_name, model_id, sort_order, now, assessor, assessor_type,
             now, assessor, assessor_type),
        )
    else:
        c.execute(
            "INSERT OR IGNORE INTO constraint_model (constraint_name, model_id, sort_order) VALUES (?, ?, ?)",
            (constraint_name, model_id, sort_order),
        )


def insert_doc(c, model_id: str, doc: dict, assessor: str, assessor_type: str) -> None:
    now = _now()
    base_vals = (
        model_id,
        doc.get("spec_table") or "",
        doc.get("description") or "",
        doc.get("best_for") or "",
        doc.get("caveats") or "",
        doc.get("creative_tier"),
    )
    if _has_column(c, "model_docs", "created_at"):
        c.execute(
            "INSERT INTO model_docs "
            "(model_id, spec_table, description, best_for, caveats, creative_tier, "
            " created_at, created_by, created_by_type, updated_at, updated_by, updated_by_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(model_id) DO UPDATE SET "
            "spec_table=excluded.spec_table, description=excluded.description, "
            "best_for=excluded.best_for, caveats=excluded.caveats, "
            "creative_tier=excluded.creative_tier, "
            "updated_at=excluded.updated_at, updated_by=excluded.updated_by, "
            "updated_by_type=excluded.updated_by_type",
            base_vals + (now, assessor, assessor_type, now, assessor, assessor_type),
        )
    else:
        c.execute(
            "INSERT OR REPLACE INTO model_docs "
            "(model_id, spec_table, description, best_for, caveats, creative_tier) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            base_vals,
        )


def main():
    parser = argparse.ArgumentParser(description="Insert models from YAML into model-assessor.db")
    parser.add_argument("yaml_file", nargs="?", help="Path to YAML file (default: model-data/new-models.yaml or stdin)")
    parser.add_argument("--assessor", default=os.environ.get("LMA_ASSESSOR"),
                        help="Model or person that performed the assessment")
    parser.add_argument("--assessor-type", default=os.environ.get("LMA_ASSESSOR_TYPE"),
                        choices=["local", "cloud", "human"],
                        help="One of: local, cloud, human")
    args = parser.parse_args()

    if args.yaml_file:
        content = Path(args.yaml_file).read_text()
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

    assessor = args.assessor
    assessor_type = args.assessor_type

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        for model_id, m in (data.get("models") or {}).items():
            if str(model_id).startswith("_"):
                continue
            if not isinstance(m, dict):
                continue
            insert_model(c, model_id, m, assessor, assessor_type)
            print(f"Added/updated model: {model_id}")

        for role, variants in (data.get("by_role") or {}).items():
            for variant, val in (variants or {}).items():
                model_id = val.get("primary", val) if isinstance(val, dict) else val
                notes = val.get("notes") if isinstance(val, dict) else None
                if model_id and not str(model_id).startswith("_"):
                    insert_role(c, role, variant, str(model_id), notes, assessor, assessor_type)

        for constraint_name, model_ids in (data.get("by_constraint") or {}).items():
            for i, model_id in enumerate(model_ids or []):
                if model_id:
                    insert_constraint(c, constraint_name, model_id, i, assessor, assessor_type)

        for model_id, doc in (data.get("model_docs") or {}).items():
            if str(model_id).startswith("_"):
                continue
            if not isinstance(doc, dict):
                continue
            insert_doc(c, model_id, doc, assessor, assessor_type)

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
