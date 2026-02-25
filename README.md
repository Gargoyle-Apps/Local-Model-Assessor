# Local Model Assessor

A system for selecting, assessing, and configuring local Ollama models — designed for **tool-calling AI agents** (Cursor, Cline, Continue, etc.) running inside IDEs.

> **Important:** This system assumes your LLM has **shell/tool access** (e.g. a coding agent in VS Code or Cursor). The agent queries the SQLite database and runs scripts directly — no copy-pasting JSON into chat windows. If you're using a plain chat LLM without tool access, this isn't the right tool.

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- An IDE with a tool-calling AI agent (Cursor, VS Code + Cline/Continue, etc.)
- Python 3 + PyYAML (`pip install pyyaml` or `pip install -r requirements.txt`)
- For model assessment: `ollama pull gpt-oss:20b` (14GB VRAM)

---

## Repo vs Local: Shell + SQLite DB

**What's in Git (the shell):**
- SQL schema and scripts (`scripts/`) — init DB, import, export, query
- Templates (`.template.yaml`) — starting points for hardware/software profiles
- Prompts (`model-selector-prompt.yaml`, `model-assessment-prompt.yaml`) — system prompts for agents
- Agent config references (`agent-model-management/`)
- `.gitkeep` files so `computer-profile/` and `model-data/` exist when cloned

**What's local-only (gitignored):**
- `computer-profile/hardware-profile.yaml`
- `computer-profile/software-profile.yaml`
- `model-data/model-assessor.db` — **SQLite source of truth** for models, roles, constraints, profiles
- `model-data/assessed-models.md` — human-readable docs (regenerated from DB)

Clone → run `./scripts/init-db.sh` → fill in hardware → run assessments. Your agent queries the DB directly. All data stays local.

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
your-project/
├── .model-assessor/          # This package
│   ├── computer-profile/
│   │   ├── hardware-profile.template.yaml
│   │   ├── software-profile.template.yaml
│   │   └── .gitkeep
│   ├── model-data/
│   │   ├── model-assessor.db     # local SQLite DB (gitignored)
│   │   └── .gitkeep
│   ├── scripts/
│   │   ├── schema.sql
│   │   ├── init-db.sh
│   │   ├── add-model-from-yaml.py
│   │   ├── export-assessed-models.py
│   │   ├── import-profiles.py
│   │   └── query-db.sh
│   ├── agent-model-management/
│   └── *.yaml
├── src/
└── ...
```

### 2. Initialize the Database and Profiles

```bash
cd .model-assessor

# Create empty DB and profile files
./scripts/init-db.sh
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

Use `model-assessment-prompt.yaml` + your hardware profile + Ollama model URLs. Send to `gpt-oss:20b` (or a capable cloud LLM). The prompt outputs YAML — save it and run:
```bash
python3 scripts/add-model-from-yaml.py new-models.yaml
python3 scripts/export-assessed-models.py   # regenerate assessed-models.md
```

### 5. Model Selection: Configure Your Agents

Your coding agent reads the selector prompt and queries the DB directly:

```text
[System: contents of .model-assessor/model-selector-prompt.yaml]

I'm setting up Cline for coding tasks. What models should I configure?
```

The agent will run `./scripts/query-db.sh` or `sqlite3` to look up models, roles, and constraints from `model-assessor.db`. No manual data pasting required.

### 6. Install & Configure

Install the recommended models:
```bash
ollama pull <model:tag>
```

Configure your agent's settings file with the recommended models.

### 7. Ad-Hoc Selection

When switching tasks or needing a different capability, invoke the model selector:

```text
What model should I use for [vision tasks / creative writing / RAG / etc.]?
```

---

## Model Hydration

### Template Shell → SQLite DB → Local Assessments

The repo ships **scripts and schema**, not pre-assessed models. Your local `model-assessor.db` starts empty and is populated by:
- **Assessment:** Your agent runs `model-assessment-prompt.yaml`, outputs YAML, and runs `add-model-from-yaml.py` to insert directly
- **Export:** `export-assessed-models.py` regenerates `assessed-models.md` from the DB

### Adding New Models

When a new model appears on Ollama:

1. Use `model-assessment-prompt.yaml` + your local `hardware-profile.yaml`
2. Provide the Ollama URL(s) for the new model(s)
3. Send to `gpt-oss:20b` (default local assessor) or a capable cloud LLM
4. Save the YAML output and run: `python3 scripts/add-model-from-yaml.py new-models.yaml`
5. Regenerate docs: `python3 scripts/export-assessed-models.py`

Your local DB evolves with your needs. All assessments stay local.

---

## Agent Model Management

The `agent-model-management/` folder holds reference configs and instructions for keeping agent/IDE tools (e.g. Continue) in sync with your local model data.

See [agent-model-management/README.md](agent-model-management/README.md) for:
- How to update Continue's `config.yaml` when models change
- Role mapping from model-assessor.db to agent configs
- Adding support for other apps (Cursor, Windsurf, etc.)

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

## Role Quick Reference

| Role | Primary Model | Notes |
|------|---------------|-------|
| `autocomplete` | granite4:3b | FIM support |
| `vision` | qwen3-vl:8b | Screenshot analysis |
| `coding` | qwen3-coder:30b | Repository-scale |
| `reasoning` | gpt-oss:20b | Chain-of-thought |
| `generalist` | gemma3:12b | General assistant |
| `embedding` | embeddinggemma:latest | RAG pipelines |
| `model_assessor` | gpt-oss:20b | Bootstrap for this system |

Query `model-assessor.db` or see `assessed-models.md` for detailed descriptions.

---

## Creative Tiers

For writing tasks, models are tiered by quality/speed tradeoff:

| Tier | Model | Use When |
|------|-------|----------|
| 🎨 Draft | gemma3:12b | Brainstorming, iteration |
| 🎨 Quality | gemma3:27b | Substantive work |
| 🎨 Polish | qwen3:72b | Publication-ready |

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
| `computer-profile/hardware-profile.template.yaml` | ✓ | Template for hardware specs |
| `computer-profile/software-profile.template.yaml` | ✓ | Template for IDE/agent setup |
| `computer-profile/hardware-profile.yaml` | ✗ local | Your hardware specs (gitignored) |
| `computer-profile/software-profile.yaml` | ✗ local | Your IDE/agent config (gitignored) |
| `model-data/model-assessor.db` | ✗ local | **SQLite source of truth** (gitignored) |
| `model-data/assessed-models.md` | ✗ local | Regenerated from DB (gitignored) |
| `model-selector-prompt.yaml` | ✓ | System prompt for model selection |
| `model-assessment-prompt.yaml` | ✓ | System prompt for assessing new models |
| `agent-model-management/` | ✓ | Agent config references and instructions |

---

<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                           LLM ROUTING INSTRUCTIONS                           ║
║                                                                              ║
║  The section below contains instructions for AI assistants.                  ║
║  Humans can skip this section.                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

## LLM Instructions

> **For humans:** This section tells LLMs how to behave when encountering these files. Skip unless curious.

### @LLM: Environment Assumption

**You are running as a tool-calling agent with shell access** (Cursor, Cline, Continue, or similar). You can execute commands directly. Do not ask the user to paste data — query the database yourself.

### @LLM: Task Routing

| User wants to... | Action |
|------------------|--------|
| Select a model | Query `model-assessor.db` via `./scripts/query-db.sh` + read `hardware-profile.yaml`. Return structured recommendation. |
| Get model details | Read `model-data/assessed-models.md` or query `SELECT * FROM model_docs WHERE model_id='...'` |
| Assess new model | Read `model-assessment-prompt.yaml`, generate YAML, run `python3 scripts/add-model-from-yaml.py`, then `python3 scripts/export-assessed-models.py` |
| Install a model | `./scripts/query-db.sh "SELECT install FROM models WHERE model_id='...'"` → run the returned command |

**If DB is missing:** Run `./scripts/init-db.sh`.

### @LLM: Key Queries

```bash
# All models sorted by VRAM
./scripts/query-db.sh "SELECT model_id, vram, class, tps FROM models ORDER BY vram"

# Find model for a role
./scripts/query-db.sh "SELECT model_id FROM role_model WHERE role='coding' AND variant='primary'"

# Models matching a constraint
./scripts/query-db.sh "SELECT model_id FROM constraint_model WHERE constraint_name='has_vision'"

# Decision tree fallback chain
./scripts/query-db.sh "SELECT chain_text FROM decision_tree WHERE need_key='need_coding'"

# Hardware budget
cat computer-profile/hardware-profile.yaml | grep -A2 vram_budget
```

### @LLM: Response Format

**Model Selection:**
```markdown
**Recommended:** `model:tag`
**Class:** [class]
**VRAM:** XGB
**Speed:** ~X t/s
**Why:** [reasoning]
**Alternative:** `backup-model` (reason)
**Install:** `ollama pull model:tag`
```

### @LLM: Constraint Checking

```yaml
# From computer-profile/hardware-profile.yaml:
# vram_budget.total_available     → max VRAM
# vram_budget.concurrency_reserve → headroom for co-running (typically 8GB)
#
# Co-run rule: if (model_vram + concurrency_reserve) < total_available → can co-run
# Heavy Lifters (30-48GB) always run solo
```

### @LLM: Database Schema (SQLite)

```sql
-- model-data/model-assessor.db
SELECT * FROM models;              -- model_id, vram, ctx, class, tps, install, url, vision, tools, ...
SELECT * FROM role_model;          -- role, variant, model_id
SELECT * FROM constraint_model;    -- constraint_name, model_id
SELECT * FROM decision_tree;       -- need_key, chain_text
SELECT * FROM rag_pipeline;        -- pipeline configs
SELECT * FROM model_docs;          -- model_id, description, best_for, caveats
SELECT * FROM hardware_profile;    -- yaml_content (stored profile)
SELECT * FROM software_profile;    -- yaml_content (stored profile)
```

<!-- END LLM INSTRUCTIONS -->

---

## License

For personal use. Individual models have their own licenses — check each model's Ollama page.
