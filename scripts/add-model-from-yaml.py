#!/usr/bin/env python3
"""
Insert models from YAML output directly into model-assessor.db.
Used by LLM-prompts/model-assessment-prompt.yaml: LLM outputs YAML → pipe to this script.

Usage:
  ./scripts/py scripts/add-model-from-yaml.py model-data/new-models.yaml
  ./scripts/py scripts/add-model-from-yaml.py --assessor gpt-oss:20b --assessor-type local model-data/new-models.yaml
  ./scripts/py scripts/add-model-from-yaml.py   # defaults to model-data/new-models.yaml if it exists
  ./scripts/py scripts/add-model-from-yaml.py < assessment-output.yaml
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
from typing import Optional

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is required (see requirements.txt).\n"
        "  ./scripts/bootstrap-python.sh\n"
        "  ./scripts/py scripts/add-model-from-yaml.py ...\n"
        "See lma-python-env skill.",
        file=sys.stderr,
    )
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "model-data" / "model-assessor.db"
DEFAULT_YAML = REPO_ROOT / "model-data" / "new-models.yaml"


def _truthy(v):
    return v in (True, 1, "true", "1", "yes")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


_KNOWN_TABLES = frozenset({
    "models", "role_model", "constraint_model", "task_category",
    "model_docs", "provisioned_models",
})


def _has_column(c, table: str, col: str) -> bool:
    if table not in _KNOWN_TABLES:
        raise ValueError(f"_has_column called with unknown table {table!r}")
    c.execute(f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='{col}'")
    return c.fetchone()[0] > 0


def _table_exists(c, name: str) -> bool:
    c.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    )
    return c.fetchone() is not None


def alias_to_modelfile_path(alias: str) -> str:
    return f"model-data/modelfile/{alias.replace(':', '-')}.mf"


def build_modelfile_content(
    base_model_id: str,
    num_ctx: int,
    temperature: Optional[float],
    num_predict: Optional[int],
    system_prompt: Optional[str],
) -> str:
    """Build a deterministic Modelfile body from normalized parameters.

    Callers must pass typed values (float/int/str or None); raw strings are
    not re-parsed here.
    """
    lines = [f"FROM {base_model_id}", f"PARAMETER num_ctx {int(num_ctx)}"]
    if temperature is not None:
        lines.append(f"PARAMETER temperature {float(temperature)}")
    if num_predict is not None:
        lines.append(f"PARAMETER num_predict {int(num_predict)}")
    if system_prompt:
        sp = system_prompt.strip()
        if "\n" in sp:
            lines.append(f'SYSTEM """\n{sp}\n"""')
        else:
            esc = sp.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'SYSTEM "{esc}"')
    return "\n".join(lines) + "\n"


def upsert_provisioned(
    c,
    base_model_id: str,
    install: str,
    entry: dict,
    assessor: str,
    assessor_type: str,
) -> Optional[str]:
    """Insert/update provisioned_models and write .mf file. Returns alias or None if skipped.

    create_command uses a repo-relative -f path; run it from the repository root.
    """
    alias = str(entry.get("alias", "")).strip()
    role = str(entry.get("role", "")).strip()
    if not alias or not role:
        return None
    variant = str(entry.get("variant", "primary")).strip() or "primary"
    try:
        num_ctx = int(entry["num_ctx"])
    except (KeyError, TypeError, ValueError):
        print(f"Warning: skip provisioning for {base_model_id!r}: invalid num_ctx", file=sys.stderr)
        return None

    temperature = entry.get("temperature")
    if temperature == "":
        temperature = None
    elif temperature is not None:
        try:
            temperature = float(temperature)
        except (TypeError, ValueError):
            temperature = None

    num_predict = entry.get("num_predict")
    if num_predict == "" or num_predict is None:
        num_predict = None
    else:
        try:
            num_predict = int(num_predict)
        except (TypeError, ValueError):
            num_predict = None

    system_prompt = entry.get("system_prompt")
    if system_prompt is not None:
        system_prompt = str(system_prompt).strip() or None

    pull_command = (install or "").strip()
    modelfile_path = alias_to_modelfile_path(alias)
    modelfile_content = build_modelfile_content(
        base_model_id, num_ctx, temperature, num_predict, system_prompt
    )
    create_command = f"ollama create {alias} -f {modelfile_path}"
    now = _now()

    c.execute(
        "SELECT base_model_id, role, variant FROM provisioned_models WHERE alias=?",
        (alias,),
    )
    alias_row = c.fetchone()
    if alias_row:
        eb, er, ev = alias_row
        if (eb, er, ev) != (base_model_id, role, variant):
            print(
                f"Error: provisioning alias {alias!r} is already used for "
                f"{eb!r} role={er!r} variant={ev!r}; cannot reuse for "
                f"{base_model_id!r} role={role!r} variant={variant!r}.",
                file=sys.stderr,
            )
            return None

    c.execute(
        "SELECT modelfile_path, is_active, modelfile_content, alias FROM provisioned_models "
        "WHERE base_model_id=? AND role=? AND variant=?",
        (base_model_id, role, variant),
    )
    prior = c.fetchone()
    if prior:
        old_path_str, was_active, old_content, old_alias = prior
        if was_active and (
            old_content != modelfile_content or old_alias != alias
        ):
            print(
                f"Warning: reprovisioning {base_model_id!r} ({role}/{variant}) changed "
                f"Modelfile body or alias; is_active was cleared. Re-verify with `ollama list` "
                f"after rebuilding the clone in Ollama.",
                file=sys.stderr,
            )

    c.execute(
        """
        INSERT INTO provisioned_models (
          alias, base_model_id, role, variant, num_ctx, temperature, num_predict, system_prompt,
          modelfile_content, modelfile_path, create_command, pull_command, is_active,
          created_at, created_by, created_by_type, updated_at, updated_by, updated_by_type
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?,?,?,?,?,?)
        ON CONFLICT(base_model_id, role, variant) DO UPDATE SET
          alias=excluded.alias,
          num_ctx=excluded.num_ctx,
          temperature=excluded.temperature,
          num_predict=excluded.num_predict,
          system_prompt=excluded.system_prompt,
          modelfile_content=excluded.modelfile_content,
          modelfile_path=excluded.modelfile_path,
          create_command=excluded.create_command,
          pull_command=excluded.pull_command,
          is_active=CASE
            WHEN excluded.modelfile_content = provisioned_models.modelfile_content
             AND excluded.alias = provisioned_models.alias
            THEN provisioned_models.is_active
            ELSE 0
          END,
          updated_at=excluded.updated_at,
          updated_by=excluded.updated_by,
          updated_by_type=excluded.updated_by_type
        """,
        (
            alias,
            base_model_id,
            role,
            variant,
            num_ctx,
            temperature,
            num_predict,
            system_prompt,
            modelfile_content,
            modelfile_path,
            create_command,
            pull_command,
            now,
            assessor,
            assessor_type,
            now,
            assessor,
            assessor_type,
        ),
    )

    out_path = REPO_ROOT / modelfile_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        out_path.write_text(modelfile_content, encoding="utf-8")
    except OSError as e:
        print(f"Error: could not write {out_path}: {e}", file=sys.stderr)
        raise

    if prior and prior[0] and prior[0] != modelfile_path:
        stale = REPO_ROOT / prior[0]
        if stale.is_file() and stale.resolve() != out_path.resolve():
            try:
                stale.unlink()
            except OSError as e:
                print(f"Warning: could not remove stale modelfile {stale}: {e}", file=sys.stderr)

    return alias


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

    has_runtime = _has_column(c, "models", "runtime")
    runtime_val = str(m.get("runtime", "ollama")).strip() or "ollama"

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

    if has_runtime:
        base_cols += ", runtime"
        base_vals += (runtime_val,)

    if has_provenance:
        cols = base_cols + ", created_at, created_by, created_by_type, updated_at, updated_by, updated_by_type"
        prov_vals = (now, assessor, assessor_type, now, assessor, assessor_type)
        vals = base_vals + prov_vals
        placeholders = ", ".join(["?"] * len(vals))
        runtime_update = ", runtime=excluded.runtime" if has_runtime else ""
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
            + runtime_update
        )
        c.execute(
            f"INSERT INTO models ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(model_id) DO UPDATE SET {update_set}",
            vals,
        )
    else:
        placeholders = ", ".join(["?"] * len(base_vals))
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

    assessor = args.assessor or "unknown"
    assessor_type = args.assessor_type or "human"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        prov_table = _table_exists(c, "provisioned_models")

        for model_id, m in (data.get("models") or {}).items():
            if str(model_id).startswith("_"):
                continue
            if not isinstance(m, dict):
                continue
            insert_model(c, model_id, m, assessor, assessor_type)
            print(f"Added/updated model: {model_id}")

            raw_prov = m.get("provisioning")
            model_runtime = str(m.get("runtime", "ollama")).strip() or "ollama"
            if raw_prov and model_runtime != "ollama":
                print(f"  Skipping Ollama provisioning for {model_id} (runtime={model_runtime})")
            elif raw_prov and prov_table:
                entries = raw_prov if isinstance(raw_prov, list) else [raw_prov]
                install = str(m.get("install", ""))
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    done_alias = upsert_provisioned(
                        c, str(model_id), install, entry, assessor, assessor_type
                    )
                    if done_alias:
                        print(f"  Provisioned clone: {done_alias}")
            elif raw_prov and not prov_table:
                print(
                    "Warning: YAML has provisioning but provisioned_models table is missing. "
                    "Run ./scripts/migrate-schema.sh",
                    file=sys.stderr,
                )

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
    except (sqlite3.Error, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

    print("Done. Run: ./scripts/py scripts/export-assessed-models.py  # to update assessed-models.md")


if __name__ == "__main__":
    main()
