# Local Model Assessor

A system for selecting, assessing, and configuring local Ollama models — designed for **tool-calling AI agents** (Cursor, Cline, Continue, etc.) running inside IDEs.

> **Important:** This system assumes your LLM has **shell/tool access** (e.g. a coding agent in VS Code or Cursor). The agent queries the SQLite database and runs scripts directly — no copy-pasting JSON into chat windows. If you're using a plain chat LLM without tool access, this isn't the right tool.

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- An IDE with a tool-calling AI agent (Cursor, VS Code + Cline/Continue, etc.)
  - Automated setup: [IDE-model-management/IDE.md](IDE-model-management/IDE.md) — config templates and role mappings for Continue, OpenCode, Goose, Pi, Zed
- Python 3 + PyYAML (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`)
- For model assessment: a capable local model (e.g. `ollama pull gpt-oss:20b`, 14GB VRAM) or a cloud LLM service
- Your machine's hardware specs and IDE/agent info — see [Define Your Environment](#3-define-your-environment)

---

## Repo vs Local

The repo ships **scripts, schema, and templates** — not pre-assessed models. Your local `model-assessor.db` starts empty. Clone → run `./scripts/init-db.sh` → fill in hardware → run assessments. Your agent queries the DB directly. All data stays local.

See **File Reference** below for what's tracked vs gitignored.

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
│   ├── import-profiles.py
│   └── query-db.sh
├── IDE-model-management/
│   ├── IDE.md                       # setup docs, role mappings, config templates
│   ├── continue/                    # Continue (VS Code)
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

Configure your agent's settings file with the recommended models. See [IDE-model-management/IDE.md](IDE-model-management/IDE.md) for app-specific templates.

### 7. Ad-Hoc Selection

When switching tasks or needing a different capability, invoke the model selector:

```text
What model should I use for [vision tasks / creative writing / RAG / etc.]?
```

---

## Model Hydration

### Assess New Models

**Canonical flow** (manual or via `ollama-search.md` pipeline):

1. Use `LLM-prompts/model-assessment-prompt.yaml` + `hardware-profile.yaml` + Ollama model URL(s)
2. Send to `gpt-oss:20b` or a capable cloud LLM
3. Save YAML output to `model-data/new-models.yaml`
4. Run:
   ```bash
   python3 scripts/add-model-from-yaml.py model-data/new-models.yaml
   python3 scripts/export-assessed-models.py
   ```

### Discover New Models from Ollama

Follow **`LLM-prompts/ollama-search.md`** to fetch the [Ollama popular](https://ollama.com/search?o=popular) page, parse, pre-filter (exclude Cloud-only), cap at 7 candidates, and run the assessment flow above. Updates `meta.last_ollama_scan`.

---

## IDE Model Management

[IDE-model-management/IDE.md](IDE-model-management/IDE.md) — setup docs, role mappings, and config templates for Continue, OpenCode, Goose, Pi, Zed. Configs are **on-demand** (generated when you ask); see [AGENTS.md](AGENTS.md) task routing.

---

## Hardware Classes

Models are categorized by VRAM footprint and performance:

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

## File Reference

| File | In Git? | Purpose |
|------|---------|---------|
| `scripts/schema.sql` | ✓ | SQLite schema for models, roles, profiles |
| `scripts/init-db.sh` | ✓ | Create empty DB |
| `scripts/add-model-from-yaml.py` | ✓ | Insert models from assessment YAML → DB |
| `scripts/export-assessed-models.py` | ✓ | Regenerate assessed-models.md from DB |
| `scripts/import-profiles.py` | ✓ | Import hardware/software YAML → DB |
| `scripts/query-db.sh` | ✓ | Run ad-hoc SQL queries against DB |
| `scripts/migrate-schema.sh` | ✓ | Add columns to existing DB (e.g. assessed_at) |
| `LLM-prompts/ollama-search.md` | ✓ | Pipeline to discover & assess new models from Ollama popular |
| `computer-profile/hardware-profile.template.yaml` | ✓ | Template for hardware specs |
| `computer-profile/software-profile.template.yaml` | ✓ | Template for IDE/agent setup |
| `model-data/new-models.template.yaml` | ✓ | Template for model assessment YAML output |
| `model-data/modelfile/.gitkeep` | ✓ | Placeholder for Ollama Modelfiles; `*.mf` in this dir are gitignored |
| `computer-profile/hardware-profile.yaml` | ✗ local | Your hardware specs (gitignored) |
| `computer-profile/software-profile.yaml` | ✗ local | Your IDE/agent config (gitignored) |
| `model-data/model-assessor.db` | ✗ local | **SQLite source of truth** (gitignored) |
| `model-data/assessed-models.md` | ✗ local | Regenerated from DB (gitignored) |
| `model-data/new-models.yaml` | ✗ local | Assessment output; copy from template (gitignored) |
| `model-data/model-lookup.json` | ✗ legacy | Legacy format (gitignored if present) |
| `requirements.txt` | ✓ | Python deps (PyYAML) |
| `LLM-prompts/model-selector-prompt.yaml` | ✓ | System prompt for model selection |
| `LLM-prompts/model-assessment-prompt.yaml` | ✓ | System prompt for assessing new models |
| `AGENTS.md` | ✓ | Agent rules, data flow, task routing |
| `IDE-model-management/IDE.md` | ✓ | IDE config setup docs, role mappings, config templates |
| `IDE-model-management/*/config-location.md` | ✓ | Per-app config format and locations (Continue, OpenCode, Goose, Pi, Zed) |
| `IDE-model-management/*/config.*` | ✗ local | Local reference copies of filled-out configs (gitignored) |
| `ref/` | ✗ local | Local copies of agent configs (gitignored) |

---

## For AI Agents

**Task routing, key queries, response format:** See [AGENTS.md](AGENTS.md).

---

## Next version

Planned work is split into **three parallel git forks** (separate branches); merge each to `main` when ready. Full checklist: local **`ref/TODO.md`**. **Fork 1 spec:** **`ref/context setting.md`**.

| Fork | Suggested branch | Scope |
|------|------------------|--------|
| **1** | `fork/provisioning-context` | Human-in-the-loop provisioning, Modelfile / `num_ctx` rules, `provisioning_profiles`, DB — per **`ref/context setting.md`**. |
| **2** | `fork/hf-gguf-ollama` | Verify HF GGUF → `Modelfile` → `ollama create` / `ollama run`; gate on **`computer-profile/`**. |
| **3** | `fork/ollama-catalog-automation` | Update **`LLM-prompts/ollama-search.md`** (cloud-only caveat); then LLM + Python automation for the import pipeline (after Fork 2). |

- **Cross-cutting** — Alternate runtimes ([Docker Model Runner](https://docs.docker.com/ai/model-runner/), [vLLM](https://vllm.ai), [vllm-metal](https://github.com/vllm-project/vllm-metal)): shared notes in **`ref/TODO.md`** (not its own fork).

---

## License

For personal use. Individual models have their own licenses — check each model's Ollama page.
