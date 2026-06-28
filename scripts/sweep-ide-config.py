#!/usr/bin/env python3
"""
Sync provisioned clone active flags from Ollama, regenerate IDE configs, deploy locally.

Run after adding/removing models, creating clones, or pruning. Agents: see lma-ide-config skill.

Usage:
  ./scripts/py scripts/sweep-ide-config.py
  ./scripts/py scripts/sweep-ide-config.py --dry-run
  ./scripts/py scripts/sweep-ide-config.py --target continue --no-deploy
  ./scripts/py scripts/sweep-ide-config.py --no-sync
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is required (see requirements.txt).\n"
        "  ./scripts/bootstrap-python.sh\n"
        "See lma-python-env skill.",
        file=sys.stderr,
    )
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "model-data" / "model-assessor.db"
SOFTWARE = REPO_ROOT / "computer-profile" / "software-profile.yaml"
SOFTWARE_TEMPLATE = REPO_ROOT / "computer-profile" / "software-profile.template.yaml"

SUPPORTED_TARGETS = ("continue", "cline")

DEPLOY_PATHS = {
    "continue": Path.home() / ".continue" / "config.yaml",
}

GENERATED_PATHS = {
    "continue": REPO_ROOT / "integrations" / "IDE-model-management" / "continue" / "config.yaml",
    "cline": REPO_ROOT / "integrations" / "IDE-model-management" / "cline" / "provider-settings.json",
}


def _load_generate_module():
    path = REPO_ROOT / "scripts" / "generate-ide-config.py"
    spec = importlib.util.spec_from_file_location("generate_ide_config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_software_profile() -> dict:
    src = SOFTWARE if SOFTWARE.exists() else SOFTWARE_TEMPLATE
    if not src.exists():
        return {}
    return yaml.safe_load(src.read_text(encoding="utf-8")) or {}


def _agent_names(profile: dict) -> list[str]:
    names: list[str] = []
    for key in ("primary_agent", "embedded_assistant", "ide"):
        block = profile.get(key)
        if isinstance(block, dict):
            name = str(block.get("name", "")).strip()
            if name:
                names.append(name)
    for block in profile.get("optional_agents") or []:
        if isinstance(block, dict):
            name = str(block.get("name", "")).strip()
            if name:
                names.append(name)
    return names


def detect_targets(profile: dict, explicit: Optional[list[str]] = None) -> list[str]:
    if explicit:
        return explicit
    targets: set[str] = set()
    for name in _agent_names(profile):
        low = name.lower()
        if "continue" in low:
            targets.add("continue")
        if "cline" in low or "roo" in low:
            targets.add("cline")
    if targets:
        return sorted(targets)
    return list(SUPPORTED_TARGETS)


def ollama_aliases() -> Optional[set[str]]:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"Warning: could not run ollama list ({exc}); skipping is_active sync.", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(
            "Warning: ollama list failed; skipping is_active sync.",
            file=sys.stderr,
        )
        return None
    aliases: set[str] = set()
    for line in result.stdout.strip().splitlines()[1:]:
        line = line.strip()
        if line:
            aliases.add(line.split()[0])
    return aliases


def sync_provisioned_active(db_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Set is_active from ollama list: 1 when alias is installed, 0 when missing."""
    installed = ollama_aliases()
    if installed is None:
        return 0, 0

    activated = deactivated = 0
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provisioned_models'")
        if not c.fetchone():
            return 0, 0
        c.execute("SELECT alias, is_active FROM provisioned_models")
        rows = list(c.fetchall())
        for row in rows:
            alias = row["alias"]
            want = 1 if alias in installed else 0
            if row["is_active"] == want:
                continue
            if dry_run:
                state = "active" if want else "inactive"
                print(f"  would mark {alias!r} is_active={want} ({state} in ollama list)")
            else:
                c.execute(
                    "UPDATE provisioned_models SET is_active=? WHERE alias=?",
                    (want, alias),
                )
            if want:
                activated += 1
            else:
                deactivated += 1
        if not dry_run:
            conn.commit()
    return activated, deactivated


def generate_target(
    gen_mod,
    db_path: Path,
    target: str,
    active_only: bool,
    dry_run: bool,
) -> Optional[Path]:
    label, builder, writer = gen_mod.TARGETS[target]
    rows = gen_mod.fetch_provisioned_with_models(db_path, active_only=active_only)
    if not rows:
        print(f"Warning: no provisioned clones for {label}; skipping generation.", file=sys.stderr)
        return None
    config = builder(rows)
    return writer(config, dry_run=dry_run)


def deploy_target(target: str, dry_run: bool = False) -> bool:
    src = GENERATED_PATHS[target]
    if not src.exists():
        print(f"Warning: generated file missing for {target}: {src}", file=sys.stderr)
        return False
    dest = DEPLOY_PATHS.get(target)
    if dest is None:
        print(
            f"Note: {target} config written to {src}. "
            "Import via the extension UI — see integrations/IDE-model-management/cline/config-location.md",
        )
        return True
    if dry_run:
        print(f"  would deploy {src} -> {dest}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"Deployed {target} config to {dest}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Sync Ollama clone flags, regenerate IDE configs, deploy to local paths",
    )
    parser.add_argument(
        "--target",
        choices=list(SUPPORTED_TARGETS),
        action="append",
        default=None,
        help="IDE target(s); default: infer from software-profile.yaml",
    )
    parser.add_argument(
        "--all-provisioned",
        action="store_true",
        help="Include inactive provisioned clones in generated config (default: active only)",
    )
    parser.add_argument("--no-sync", action="store_true", help="Skip is_active sync from ollama list")
    parser.add_argument("--no-deploy", action="store_true", help="Generate repo copies only")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    active_only = not args.all_provisioned
    db_path = Path(os.environ.get("LMA_DB", str(DEFAULT_DB)))
    if not db_path.exists():
        print(f"Error: {db_path} not found. Run init-db.sh first.", file=sys.stderr)
        sys.exit(1)

    profile = _read_software_profile()
    targets = detect_targets(profile, explicit=args.target)
    if not args.target:
        names = _agent_names(profile)
        if names:
            print(f"Targets from software-profile ({', '.join(names)}): {', '.join(targets)}")
        else:
            print(f"No agent names in software-profile; generating all targets: {', '.join(targets)}")

    if not args.no_sync:
        print("Syncing provisioned_models.is_active from ollama list...")
        activated, deactivated = sync_provisioned_active(db_path, dry_run=args.dry_run)
        if activated or deactivated:
            print(f"  activated: {activated}, deactivated: {deactivated}")
        elif ollama_aliases() is not None:
            print("  no is_active changes needed")

    gen_mod = _load_generate_module()
    for target in targets:
        path = generate_target(gen_mod, db_path, target, active_only, args.dry_run)
        if path:
            print(f"Wrote {gen_mod.TARGETS[target][0]} config to {path}")
        elif args.dry_run:
            generate_target(gen_mod, db_path, target, active_only, dry_run=True)

    if not args.no_deploy:
        for target in targets:
            if args.dry_run or GENERATED_PATHS[target].exists():
                deploy_target(target, dry_run=args.dry_run)

    if not args.dry_run and not args.no_deploy and "continue" in targets:
        print("Restart Continue or reload VS Code to pick up config changes.")


if __name__ == "__main__":
    main()
