# Local Model Assessor

A system for selecting, assessing, and configuring local Ollama models — designed for **tool-calling AI agents** (Cursor, Cline, Continue, etc.) running inside IDEs.

> **Important:** This system assumes your LLM has **shell/tool access** (e.g. a coding agent in VS Code or Cursor). The agent queries the SQLite database and runs scripts directly — no copy-pasting JSON into chat windows. If you're using a plain chat LLM without tool access, this isn't the right tool.

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- An IDE with a tool-calling AI agent (Cursor, VS Code + Cline/Continue, etc.)
  - Automated setup: [IDE-model-management/IDE.md](IDE-model-management/IDE.md) — config templates, role mappings, and timeout policy for Continue, Cline/Roo, OpenCode, Goose, Pi, Zed
- Python 3 + PyYAML (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`)
- For model assessment: a capable local model (e.g. `ollama pull gpt-oss:20b`, 14GB VRAM) or a cloud LLM service
- Your machine's hardware specs and IDE/agent info — see [Define Your Environment](#3-define-your-environment)

---

## Repo vs Local

The repo ships **scripts, schema, and templates** — not pre-assessed models. Your local `model-assessor.db` starts empty. Clone → run `./scripts/init-db.sh` → fill in hardware → run assessments. Your agent queries the DB directly. All data stays local.

**Tracked** in `computer-profile/` and `model-data/` include templates (e.g. `*.template.yaml`), `new-models.template.yaml`, `modelfile/.gitkeep`, and scripts/schema. **Gitignored** (local only): `hardware-profile.yaml`, `software-profile.yaml`, `model-assessor.db`, `assessed-models.md`, `new-models.yaml`, generated `model-data/modelfile/*.mf`, IDE reference configs under `IDE-model-management/` (e.g. `continue/config.yaml`, `cline/provider-settings.json`), `embed-retrieval-stack/out/`, and `ref/`.

> **For AI agents:** See [AGENTS.md](AGENTS.md) — task routing, key queries, data flow, provenance, and response format.

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
│   ├── schema.sql
│   ├── init-db.sh
│   ├── migrate-schema.sh
│   ├── add-model-from-yaml.py
│   ├── export-assessed-models.py
│   ├── generate-ide-config.py       # Continue + Cline/Roo config from DB
│   ├── generate-stack-handoff.py    # Postgres/pgvector/AGE + embedding handoff
│   ├── import-profiles.py
│   └── query-db.sh
├── embed-retrieval-stack/           # Docker: Postgres + pgvector + Apache AGE (v1)
│   ├── README.md
│   ├── versions.lock.yaml
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── init/
├── IDE-model-management/
│   ├── IDE.md                       # setup docs, role mappings, timeout policy, templates
│   ├── continue/                    # Continue (VS Code)
│   ├── cline/                       # Cline / Roo Code (JSON provider settings)
│   ├── opencode/                    # OpenCode (CLI/TUI)
│   ├── goose/                       # Goose (CLI/Desktop)
│   ├── pi/                          # Pi coding-agent (Terminal)
│   └── zed/                         # Zed (Editor)
├── ref/                             # local agent config copies (gitignored)
├── LLM-prompts/
│   ├── model-assessment-prompt.yaml
│   ├── model-selector-prompt.yaml
│   └── ollama-search.md
├── AGENTS.md                        # agent rules, data flow, task routing
├── requirements.txt
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

# Import profiles into DB (after editing them)
python3 scripts/import-profiles.py
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

Configure your agent's settings file with the recommended models. After provisioned clones exist in the DB, run `python3 scripts/generate-ide-config.py --dry-run` (add `--active-only` to limit to `is_active=1` rows), then merge outputs into your IDE paths — see [IDE-model-management/IDE.md](IDE-model-management/IDE.md).

### 7. Ad-Hoc Selection

When switching tasks or needing a different capability, invoke the model selector:

```text
What model should I use for [vision tasks / creative writing / RAG / etc.]?
```

---

## Model hydration

Ways to grow what’s in `model-assessor.db` after the first setup.

**HF GGUF (not in Ollama’s library):** Same assessment + import scripts; workflow and two-tier Modelfile rules live in **[AGENTS.md](AGENTS.md)** (Phase 3).

## Assess new models

**Canonical flow** (manual or via `ollama-search.md` pipeline):

1. Use `LLM-prompts/model-assessment-prompt.yaml` + `hardware-profile.yaml` + model URL(s) (Ollama library or HF GGUF per [AGENTS.md](AGENTS.md) Phase 3)
2. Send to `gpt-oss:20b` or a capable cloud LLM
3. Save YAML output to `model-data/new-models.yaml`
4. Run:
   ```bash
   python3 scripts/add-model-from-yaml.py model-data/new-models.yaml
   python3 scripts/export-assessed-models.py
   ```

## Discover new models from Ollama

Follow **`LLM-prompts/ollama-search.md`** to fetch the [Ollama popular](https://ollama.com/search?o=popular) page, parse, pre-filter (exclude Cloud-only), cap at 7 candidates, and run the [assessment flow](#assess-new-models) above. Updates `meta.last_ollama_scan`.

---

## IDE Model Management

[IDE-model-management/IDE.md](IDE-model-management/IDE.md) — setup docs, role mappings, timeout policy, and config templates for Continue, Cline/Roo, OpenCode, Goose, Pi, Zed. Configs are **on-demand** (generated when you ask, or via `scripts/generate-ide-config.py`); see [AGENTS.md](AGENTS.md) task routing. **Continue** uses **`~/.continue/config.yaml`** (YAML); **Cline/Roo Code** use JSON provider settings — both get role-appropriate request timeouts.

---

## Embed + retrieval stack (v1): Postgres + pgvector + Apache AGE

**Prerequisites:**

1. **[Docker](https://docs.docker.com/get-docker/)** + Docker Compose (to run Postgres + extensions).
2. **At least one assessed embedding model** in `model-assessor.db`: a row in `models` for an embedding-capable Ollama model, plus **`role_model`** (`role='embedding'`) and ideally a **provisioned** clone in `provisioned_models` for that role (via `model-assessment-prompt.yaml` → `new-models.yaml` → `add-model-from-yaml.py`). Without this, `generate-stack-handoff.py` has no model to reference. You can still bring up the Docker stack alone for experiments.

[embed-retrieval-stack/README.md](embed-retrieval-stack/README.md) — pinned **PostgreSQL + pgvector + Apache AGE** via Docker (`embed-retrieval-stack/versions.lock.yaml`), sample `documents` table, and short **embedding use-case** bullets (semantic search, RAG, etc.).

**Handoff into your app repo** (requires the embedding assessment above — provisioned clone preferred, or at least `role_model.embedding` pointing at an assessed `model_id`):

```bash
python3 scripts/generate-stack-handoff.py
```

Writes **`embed-retrieval-stack/out/STACK_HANDOFF.md`** and **`embed_sample.py`** (gitignored). Copy those plus the `embed-retrieval-stack/` compose files into your project when you leave this repo. See [AGENTS.md](AGENTS.md) task routing.

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

For personal use. Individual models have their own licenses — check each model's Ollama page.
