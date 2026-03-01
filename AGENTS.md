# Project Rules for AI Coding Agents

> **Cursor users:** Create a local `.cursorrules` that references this file and adds `required_permissions: ["all"]` for git operations. (`.cursorrules` is gitignored.)

This project is designed for **tool-calling AI agents with shell access** (Cursor, Cline, Continue, Claude Code, etc.). You can query the database and run scripts directly — do not ask the user to paste data or run commands manually.

## Architecture: SQLite as Source of Truth
The model database is `model-data/model-assessor.db` (SQLite). Query it directly:
- `./scripts/query-db.sh "SQL"` — run any query against the DB
- `./scripts/init-db.sh` — create empty DB
- `python3 scripts/add-model-from-yaml.py file.yaml` — insert models from assessment output
- `python3 scripts/export-assessed-models.py` — regenerate assessed-models.md from DB
- `python3 scripts/import-profiles.py` — import hardware/software YAML into DB
- `./scripts/migrate-schema.sh` — add schema columns (e.g. assessed_at) to existing DB
- For discovering new models from Ollama: follow `LLM-prompts/ollama-search.md`

## Local vs Tracked Files
Prefer editing **gitignored local files** (`model-assessor.db`, hardware-profile.yaml, software-profile.yaml, assessed-models.md). Templates and prompts are tracked. To create local files from templates, use the setup block in `LLM-prompts/model-assessment-prompt.yaml` or run `./scripts/init-db.sh`.

## Git Operations
When running git commands (push, pull, commit, fetch, merge, checkout, branch operations), ensure the agent has write access to `.git` — some sandboxes restrict this.
