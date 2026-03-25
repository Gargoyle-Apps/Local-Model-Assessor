#!/usr/bin/env python3
"""
Import hardware-profile.yaml and software-profile.yaml into model-assessor.db.
Run from repo root: ./scripts/py scripts/import-profiles.py

Reads computer-profile/hardware-profile.yaml and computer-profile/software-profile.yaml
and stores them in the hardware_profile and software_profile tables.
"""

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARDWARE = REPO_ROOT / "computer-profile" / "hardware-profile.yaml"
HARDWARE_TEMPLATE = REPO_ROOT / "computer-profile" / "hardware-profile.template.yaml"
SOFTWARE = REPO_ROOT / "computer-profile" / "software-profile.yaml"
SOFTWARE_TEMPLATE = REPO_ROOT / "computer-profile" / "software-profile.template.yaml"
DB_PATH = REPO_ROOT / "model-data" / "model-assessor.db"


def main():
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        db_path = DB_PATH

    if not db_path.exists():
        print(f"Error: {db_path} not found. Run init-db.sh first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        hw_src = HARDWARE if HARDWARE.exists() else HARDWARE_TEMPLATE
        if hw_src.exists():
            content = hw_src.read_text()
            c.execute(
                "INSERT OR REPLACE INTO hardware_profile (id, yaml_content, updated_at) VALUES (1, ?, datetime('now'))",
                (content,),
            )
            print(f"Imported hardware profile from {hw_src}")
        else:
            print("Skip: no hardware profile found")

        sw_src = SOFTWARE if SOFTWARE.exists() else SOFTWARE_TEMPLATE
        if sw_src.exists():
            content = sw_src.read_text()
            c.execute(
                "INSERT OR REPLACE INTO software_profile (id, yaml_content, updated_at) VALUES (1, ?, datetime('now'))",
                (content,),
            )
            print(f"Imported software profile from {sw_src}")
        else:
            print("Skip: no software profile found")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
