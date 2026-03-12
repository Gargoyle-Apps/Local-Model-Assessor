# Local Model Assessor — Project Rules for Continue

This project manages a local fleet of Ollama models via a SQLite database. You are a tool-calling agent with shell access — query the DB and run scripts directly. Do not ask the user to paste data or run commands manually.

**Full agent rules (data flow, task routing, key queries):** [AGENTS.md](AGENTS.md)

## Source of Truth

The model database is `model-data/model-assessor.db` (SQLite). Use these scripts:

- `./scripts/query-db.sh "SQL"` — run any query
- `./scripts/init-db.sh` — create empty DB
- `python3 scripts/add-model-from-yaml.py model-data/new-models.yaml` — insert models from YAML
- `python3 scripts/export-assessed-models.py` — regenerate assessed-models.md from DB
- `python3 scripts/import-profiles.py` — import hardware/software YAML into DB
- `./scripts/migrate-schema.sh` — add schema columns to existing DB

### Key Tables

- `models` — model specs (vram, ctx, class, tps, vision, tools, reasoning, etc.)
- `role_model` — which model fills which role (coding, vision, reasoning, etc.)
- `constraint_model` — capability tags (has_tools, has_vision, under_8gb, etc.)
- `model_docs` — descriptions, best_for, caveats
- `meta` — metadata like `last_ollama_scan` timestamp

### Useful Queries

```bash
# List all models with specs
./scripts/query-db.sh "SELECT model_id, vram, class, tps, vision, tools, reasoning FROM models"

# Check role assignments
./scripts/query-db.sh "SELECT role, variant, model_id FROM role_model"

# Find models with a capability
./scripts/query-db.sh "SELECT model_id FROM constraint_model WHERE constraint_name='has_tools'"
```

## Local vs Tracked Files

**Gitignored (local-only):** `model-assessor.db`, `hardware-profile.yaml`, `software-profile.yaml`, `assessed-models.md`, `model-data/new-models.yaml`, `.cursorrules`, `agent-model-management/continue/config.yaml`, `ref/`

**Tracked (in git):** Templates (`.template.yaml`), scripts, prompts (`LLM-prompts/`), `AGENTS.md`, this rules file.

Never commit local-only files. When creating new local files, use the corresponding template. For model assessment output, copy `model-data/new-models.template.yaml` to `model-data/new-models.yaml`.

## Hardware Context

Read `computer-profile/hardware-profile.yaml` (or the template) for system specs, VRAM budget, hardware classes, quantization preferences, and context strategy.

## Workflows

### Assess New Models

Follow `LLM-prompts/ollama-search.md` to discover models from Ollama, or use `LLM-prompts/model-assessment-prompt.yaml` to assess specific models. Output goes to `model-data/new-models.yaml`, then:

```bash
python3 scripts/add-model-from-yaml.py model-data/new-models.yaml
python3 scripts/export-assessed-models.py
```

### Update Continue Config

See `agent-model-management/README.md` for mapping DB roles to Continue's `config.yaml` format. The role mapping is:

| DB role (`role_model`) | Continue role |
|---|---|
| `coding.primary` | `roles: [chat, edit, apply]` + `capabilities: [tool_use]` |
| `vision.primary` | `roles: [chat]` + `capabilities: [image_input]` |
| `reasoning.primary` | `roles: [chat, edit]` (no tool_use) |
| `autocomplete.balanced` | `roles: [autocomplete]` |
| `embedding.primary` | `roles: [embed]` |

### Select a Model for a Task

Use `LLM-prompts/model-selector-prompt.yaml` or query the DB directly by role and constraints.

## Documentation Links

- [Continue config.yaml reference](https://docs.continue.dev/reference/config-yaml)
- [Continue rules](https://docs.continue.dev/customize/rules)
- [Ollama model library](https://ollama.com/library)
- [Project README](README.md)
- [Agent rules (all IDEs)](AGENTS.md)
- [Agent model management](agent-model-management/README.md)
