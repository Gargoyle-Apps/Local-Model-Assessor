# Local Model Assessor

For **tool-calling agents** in IDEs (Cursor, Cline, Continue, …): query SQLite and run repo scripts — not for chat-only LLMs without shell access.

**Prerequisites:** [Ollama](https://ollama.com) · Python 3 · `./scripts/bootstrap-python.sh` (creates gitignored `.venv` from [requirements.txt](requirements.txt)) · run scripts with `./scripts/py` — see `lma-python-env` skill in [`.skills/_index.md`](.skills/_index.md) · IDE agent · [profiles](#3-define-your-environment) · optional LLM for assessments · optional [mlx-lm](https://github.com/ml-explore/mlx-lm) for Apple Silicon MLX models · **Docker** only for [integrations/embed-retrieval-stack/embed-retrieval-stack.md](integrations/embed-retrieval-stack/embed-retrieval-stack.md) (`docker compose exec postgres psql …` for checks).

---

## Repo vs Local

Ships **scripts, schema, templates** — empty `model-assessor.db` until you init, profile, assess. **`Brewfile`:** optional `brew bundle` → `libpq` (keg-only; see `brew info libpq`); not needed for Docker stack (`docker compose exec`). **Tracked:** templates under `computer-profile/`, `model-data/` (e.g. `*.template.yaml`, `modelfile/.gitkeep`), `scripts/`, `.skills/` (skills harness; see [Skills harness](#skills-harness-third-party)), `integrations/` (copy-out: IDE + embed stack). **Gitignored:** profiles, DB, `new-models.yaml`, generated modelfiles, `integrations/IDE-model-management/*/config*`, `integrations/embed-retrieval-stack/out/`, `ref/`, `.cursorrules`. Details: [AGENTS.md](AGENTS.md) + `.gitignore`.

---

## Quick Start

### 1. Add to Your Project

```bash
# Clone into your project
git clone https://github.com/Gargoyle-Apps/Local-Model-Assessor.git .model-assessor

# Or copy the folder directly
cp -r /path/to/local-model-assessor .model-assessor
```

```text
.model-assessor/
├── computer-profile/
│   ├── hardware-profile.template.yaml
│   ├── software-profile.template.yaml
│   ├── hardware-profile.yaml        # local (gitignored)
│   ├── software-profile.yaml        # local (gitignored)
│   └── .gitkeep
├── model-data/
│   ├── model-assessor.db            # local SQLite DB (gitignored)
│   ├── assessed-models.md            # regenerated from DB (gitignored)
│   ├── new-models.template.yaml     # schema for assessment output (tracked)
│   ├── new-models.yaml              # assessment output (gitignored; copy from template)
│   ├── modelfile/                   # Ollama Modelfiles (.mf); contents gitignored, .gitkeep only
│   └── .gitkeep
├── scripts/
│   ├── py                       # run Python with .venv (+ sync requirements.txt)
│   ├── bootstrap-python.sh      # create .venv and pip install -r requirements.txt
│   ├── schema.sql
│   ├── init-db.sh
│   ├── migrate-schema.sh
│   ├── add-model-from-yaml.py
│   ├── export-assessed-models.py
│   ├── generate-ide-config.py       # Continue + Cline/Roo config from DB
│   ├── generate-stack-handoff.py    # Postgres/pgvector/AGE + embedding handoff
│   ├── import-profiles.py
│   └── query-db.sh
├── integrations/                    # copy-out kits: IDE configs + Docker data stack
│   ├── embed-retrieval-stack/       # Postgres + pgvector + Apache AGE
│   │   ├── embed-retrieval-stack.md
│   │   ├── versions.lock.yaml
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   └── init/
│   └── IDE-model-management/
│       ├── IDE.md                   # setup docs, role mappings, timeout policy, templates
│       ├── continue/                # Continue (VS Code)
│       ├── cline/                   # Cline / Roo Code (JSON provider settings)
│       ├── opencode/                # OpenCode (CLI/TUI)
│       ├── goose/                   # Goose (CLI/Desktop)
│       ├── pi/                      # Pi coding-agent (Terminal)
│       └── zed/                     # Zed (Editor)
├── ref/                             # local agent config copies (gitignored)
├── LLM-prompts/
│   ├── model-assessment-prompt.yaml
│   ├── model-selector-prompt.yaml
│   └── ollama-search.md
├── .skills/                         # skills harness (third-party; see README)
├── AGENTS.md                        # agent spine: non-negotiables, file layout, hardware budget
├── requirements.txt             # PyYAML for YAML import scripts; install via bootstrap-python.sh
├── Brewfile                         # optional: brew bundle → libpq
├── .gitignore
└── LICENSE
```

### 2. Initialize the Database and Profiles

```bash
cd .model-assessor

# Create empty DB (init-db.sh creates only the database, not profile files)
./scripts/init-db.sh
# Existing DB? Run ./scripts/migrate-schema.sh to add assessed_at and other columns
cp computer-profile/hardware-profile.template.yaml computer-profile/hardware-profile.yaml
cp computer-profile/software-profile.template.yaml computer-profile/software-profile.yaml

# Python deps (PEP 668-safe venv); then import profiles into DB (after editing them)
./scripts/bootstrap-python.sh
./scripts/py scripts/import-profiles.py
```

### 3. Define Your Environment

Edit the **local** profile files in `computer-profile/`:

**`hardware-profile.yaml`** — Your machine's specs and VRAM budget:
```yaml
system:
  name: "Your Machine"
  unified_ram: "64GB"  # or available RAM
vram_budget:
  total_available: 50  # GB safe for Ollama
```

**`software-profile.yaml`** — Your IDE and coding agents:
```yaml
ide:
  name: "VS Code"  # or Cursor, etc.
primary_agent:
  name: "Cline"    # your main coding agent
```

### 4. Run Initial Model Assessments

Use `LLM-prompts/model-assessment-prompt.yaml` + your hardware profile + Ollama model URLs. Send to `gpt-oss:20b` (or a capable cloud LLM). Save the YAML output to `model-data/new-models.yaml`, then run the [assessment flow](#assess-new-models).

### 5. Model Selection: Configure Your Agents

Your coding agent reads the selector prompt and queries the DB directly:

```text
[System: contents of .model-assessor/LLM-prompts/model-selector-prompt.yaml]

I'm setting up Cline for coding tasks. What models should I configure?
```

The agent will run `./scripts/query-db.sh` or `sqlite3` to look up models, roles, and constraints from `model-assessor.db`. No manual data pasting required.

### 6. Install & Configure

Install the recommended models:
```bash
ollama pull <model:tag>
```

Configure your agent's settings file with the recommended models. After provisioned clones exist in the DB, run `./scripts/py scripts/generate-ide-config.py --dry-run` (add `--active-only` to limit to `is_active=1` rows), then merge outputs into your IDE paths — see [integrations/IDE-model-management/IDE.md](integrations/IDE-model-management/IDE.md).

### 7. Ad-Hoc Selection

When switching tasks or needing a different capability, invoke the model selector:

```text
What model should I use for [vision tasks / creative writing / RAG / etc.]?
```

---

## Assess new models

1. `LLM-prompts/model-assessment-prompt.yaml` + `hardware-profile.yaml` + URLs (Ollama, HF GGUF via `lma-hf-gguf-ollama` skill, or MLX via `lma-mlx-lm` skill)
2. LLM → save YAML → `model-data/new-models.yaml`
3. `./scripts/py scripts/add-model-from-yaml.py model-data/new-models.yaml` then `./scripts/py scripts/export-assessed-models.py`

**Discover:** `LLM-prompts/ollama-search.md` → [Ollama popular](https://ollama.com/search?o=popular), cap 7, same import flow; sets `meta.last_ollama_scan`. Cloud-only models are excluded — check [HuggingFace](https://huggingface.co) for local alternatives.

---

## IDE + embed stack

- **IDEs:** [integrations/IDE-model-management/IDE.md](integrations/IDE-model-management/IDE.md) — roles, timeouts, Continue (`~/.continue/config.yaml`) / Cline-Roo (JSON), others; `generate-ide-config.py`; see `lma-ide-config` skill.
- **Postgres + pgvector + AGE:** [integrations/embed-retrieval-stack/embed-retrieval-stack.md](integrations/embed-retrieval-stack/embed-retrieval-stack.md) — pins, compose under `integrations/embed-retrieval-stack/`, use cases, troubleshooting. **Handoff** (`STACK_HANDOFF.md`, `embed_sample.py`): assessed **embedding** in DB → `./scripts/py scripts/generate-stack-handoff.py` → `integrations/embed-retrieval-stack/out/` (gitignored); copy stack + `out/` to your app.

---

## Skills harness (third-party)

This repo vendors a **skills harness** under `.skills/` (portable manifest + authoring helpers). Policy is **agnostic / multi-ecosystem** (Path B): see [AGENTS.md](AGENTS.md) **Skills (agnostic / multi-ecosystem)** — we do not merge tool-specific harness templates from `.skills/_harness/` into this project.

**Credit:** The `.skills/` tree is derived from **[skills-harness](https://github.com/gotalab/skills-harness)** (MIT). To propose changes to shared templates, rules, or bundled skills, contribute upstream in that repository.

---

## Hardware Classes

Models are categorized by VRAM footprint and performance. **Full fields** (budget, `os_headroom_gb`, quantization, concurrency, `context_strategy`, hardware class definitions) live in **`computer-profile/hardware-profile.template.yaml`** — copy to `hardware-profile.yaml` and edit.

| Class | VRAM | Speed | Use Case |
|-------|------|-------|----------|
| **Utility** | 1-4GB | 100-1000 t/s | Embedding, OCR (always-on) |
| **Speedster** | <8GB | 80-120 t/s | Autocomplete, quick vision |
| **Middleweight** | 8-12GB | 45-50 t/s | Interactive assistant |
| **Daily Driver** | 12-24GB | 25-40 t/s | Reasoning, coding |
| **Heavy Lifter** | 30-48GB | ~15 t/s | Quality-critical (runs solo) |

**Concurrency:** 1 Utility + 1 Speedster + 1 larger model can run simultaneously. Heavy Lifters cannot co-run.

---

## Roles & Constraints

Query `model-assessor.db` for current assignments:

```bash
./scripts/query-db.sh "SELECT role, variant, model_id FROM role_model"
./scripts/query-db.sh "SELECT constraint_name, model_id FROM constraint_model"
```

Example roles: `coding`, `vision`, `reasoning`, `autocomplete`, `embedding`, `generalist`. See `model-data/assessed-models.md` for descriptions.

---

## License

[LICENSE](LICENSE) — MIT (ImpureCrumpet; see file for **skills-harness** attribution under `.skills/`). Individual Ollama models have their own licenses — check each model’s page.
