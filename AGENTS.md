# Project Rules for AI Coding Agents

> **Cursor users:** Create a local `.cursorrules` that references this file and adds `required_permissions: ["all"]` for git operations. (`.cursorrules` is gitignored.)

This project is designed for **tool-calling AI agents with shell access** (Cursor, Cline, Continue, Claude Code, etc.). Query the database and run scripts directly — do not ask the user to paste data or run commands manually.

**Full setup:** See [README.md](README.md).

---

## Data Flow

| Script / Prompt | Inputs | Outputs |
|-----------------|--------|---------|
| `init-db.sh` | `scripts/schema.sql` | `model-data/model-assessor.db` |
| `import-profiles.py` | `computer-profile/*.yaml` | DB (`hardware_profile`, `software_profile`) |
| `add-model-from-yaml.py` | `model-data/new-models.yaml` | DB (`models`, `role_model`, `constraint_model`, `model_docs`, `provisioned_models`); writes `model-data/modelfile/*.mf` |
| `export-assessed-models.py` | DB | `model-data/assessed-models.md` |
| `generate-ide-config.py` | DB (`provisioned_models`, `models`) | `IDE-model-management/<app>/` config files with role-appropriate timeouts |
| `ollama-search.md` → `model-assessment-prompt.yaml` → `add-model-from-yaml.py` | Ollama popular page, `hardware-profile.yaml` | DB, `assessed-models.md` |

---

## Architecture

**Source of truth:** `model-data/model-assessor.db` (SQLite)

**Key scripts:**
- `./scripts/query-db.sh "SQL"` — run any query (**no args = interactive session; always pass a SQL string**)
- `./scripts/init-db.sh` — create empty DB
- `./scripts/migrate-schema.sh` — add schema columns (e.g. `assessed_at`, provenance) and **`provisioned_models`** if missing
- `python3 scripts/add-model-from-yaml.py --assessor NAME --assessor-type local|cloud|human model-data/new-models.yaml` — insert models with provenance (or no args to use default path; provenance also via `LMA_ASSESSOR` / `LMA_ASSESSOR_TYPE` env vars)
- `python3 scripts/export-assessed-models.py [output.md]` — regenerate `assessed-models.md` (optional path overrides default)
- `python3 scripts/import-profiles.py [db_path]` — import hardware/software YAML into DB (optional DB path overrides default)
- `python3 scripts/generate-ide-config.py [--target continue|cline] [--active-only] [--dry-run]` — emit IDE configs with role-appropriate timeouts from `provisioned_models`

**Env var overrides:** `LMA_DB` overrides the DB path in all Python scripts. `LMA_ASSESSOR` / `LMA_ASSESSOR_TYPE` set provenance defaults for `add-model-from-yaml.py`.

**Discover new models:** Follow `LLM-prompts/ollama-search.md`.

---

## Local vs Tracked Files

| Type | Files |
|------|-------|
| **Tracked** | Templates (`.template.yaml`), prompts (`LLM-prompts/`), scripts, `AGENTS.md`, `IDE-model-management/` (setup docs + config references) |
| **Gitignored** | `model-assessor.db`, `hardware-profile.yaml`, `software-profile.yaml`, `assessed-models.md`, `model-data/new-models.yaml`, `model-data/modelfile/*` (except `.gitkeep`), `.cursorrules`, `.continue/`, `.opencode/`, `opencode.json`, local config copies (`IDE-model-management/*/config.*`, `cline/provider-settings.json`), `ref/` |

Create local files from templates: `cp computer-profile/hardware-profile.template.yaml computer-profile/hardware-profile.yaml` (or use setup in `model-assessment-prompt.yaml`). For assessment output: `cp model-data/new-models.template.yaml model-data/new-models.yaml`.

---

## Task Routing

| User wants to... | Action |
|------------------|--------|
| Select a model | Follow `LLM-prompts/model-selector-prompt.yaml`: join `role_model` → `provisioned_models` → `models`, run `ollama list` for drift, recommend alias or print `pull_command` / `create_command`. Read `hardware-profile.yaml` for budget. |
| Discover new models | Follow `LLM-prompts/ollama-search.md` — fetch Ollama popular, parse, pre-filter, cap at 7, assess via `model-assessment-prompt.yaml` |
| Get model details | Read `model-data/assessed-models.md` or query `model_docs` |
| Assess new model | Read `model-assessment-prompt.yaml`, generate YAML to `model-data/new-models.yaml`, run `add-model-from-yaml.py`, then `export-assessed-models.py` |
| Install a model | `./scripts/query-db.sh "SELECT install FROM models WHERE model_id='...'"` → run the returned command |
| Configure IDE/agent | Run `python3 scripts/generate-ide-config.py --target <app>` for Continue or Cline/Roo (uses `provisioned_models` + timeout policy from `IDE-model-management/IDE.md`). For other apps (OpenCode, Goose, Pi, Zed): read `IDE-model-management/IDE.md`, find the app section, query DB for role assignments, generate config manually. **Auto-trigger:** after profile import, if `software-profile.yaml` names a supported app, generate its config automatically. |

**If DB missing:** Run `./scripts/init-db.sh`. **If DB lacks `assessed_at`, provenance columns, or `provisioned_models`:** Run `./scripts/migrate-schema.sh`.

---

## Provenance

Content tables (`models`, `role_model`, `constraint_model`, `task_category`, `model_docs`, `provisioned_models`) track who created and last updated each row:

| Column | Set when | Preserved on update? |
|--------|----------|---------------------|
| `created_at` | First insert | Yes |
| `created_by` | First insert (assessor name) | Yes |
| `created_by_type` | First insert (`local`/`cloud`/`human`) | Yes |
| `updated_at` | Every write | No (overwritten) |
| `updated_by` | Every write (assessor name) | No (overwritten) |
| `updated_by_type` | Every write (`local`/`cloud`/`human`) | No (overwritten) |

**How agents provide provenance:**
- `add-model-from-yaml.py --assessor gpt-oss:20b --assessor-type local`
- Or env vars: `LMA_ASSESSOR=gpt-oss:20b LMA_ASSESSOR_TYPE=local`
- Direct SQL: include `created_by`, `created_by_type`, `updated_by`, `updated_by_type` in INSERT

**Query provenance:**
```bash
./scripts/query-db.sh "SELECT model_id, created_at, created_by, created_by_type, updated_at, updated_by FROM models"
```

---

## Key Queries

```bash
./scripts/query-db.sh "SELECT model_id, vram, class, tps FROM models ORDER BY vram"
./scripts/query-db.sh "SELECT model_id FROM role_model WHERE role='coding' AND variant='primary'"
./scripts/query-db.sh "SELECT model_id FROM constraint_model WHERE constraint_name='has_vision'"
./scripts/query-db.sh "SELECT value FROM meta WHERE key='last_ollama_scan'"
./scripts/query-db.sh "SELECT alias, base_model_id, role, num_ctx, is_active FROM provisioned_models ORDER BY role"
./scripts/query-db.sh "SELECT chain_text FROM decision_tree WHERE need_key='need_vision'"
./scripts/query-db.sh "SELECT * FROM rag_pipeline"
./scripts/query-db.sh "SELECT role_name FROM task_category WHERE category='writing'"
```

**Hardware budget:** `grep -A5 vram_budget computer-profile/hardware-profile.yaml` (includes `os_headroom_gb`; effective budget ≈ `total_available - os_headroom_gb`)

**Co-run rule:** `(model_vram + concurrency_reserve) < total_available` → can co-run. Heavy Lifters (30–48GB) run solo.

---

## Response Format (Model Selection)

Prefer a **provisioned alias** when `provisioned_models` has a row for that role (see `model-selector-prompt.yaml`). Fallback when no clone exists:

```markdown
**Recommended:** `model:tag`
**Class:** [class] | **VRAM:** XGB | **Speed:** ~X t/s
**Why:** [reasoning]
**Alternative:** `backup-model` (reason)
**Install:** `ollama pull model:tag`
```

---

## Git Operations

When running git commands (push, pull, commit, fetch, merge, checkout, branch), ensure the agent has write access to `.git` — some sandboxes restrict this.
