# Local Model Assessor

A system for selecting and configuring local Ollama models for AI coding agents.

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- For model assessment: `ollama pull gpt-oss:20b` (14GB VRAM)

---

## Repo vs Local: Shell + Templates

**What's in Git (the shell):**
- Templates (`.template.yaml`, `.template.json`, `.template.md`) — empty structures to copy
- Prompts (`model-selector-prompt.yaml`, `model-assessment-prompt.yaml`)
- Agent config references (`agent-model-management/`)
- `.gitkeep` files so `computer-profile/` and `model-data/` exist when cloned

**What's local-only (gitignored):**
- `computer-profile/hardware-profile.yaml`
- `computer-profile/software-profile.yaml`
- `model-data/model-lookup.json`
- `model-data/assessed-models.md`

Clone → copy templates → fill in your hardware → run assessments locally. Your model data and assessments never leave your machine.

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
│   │   ├── model-lookup.template.json
│   │   ├── assessed-models.template.md
│   │   └── .gitkeep
│   ├── agent-model-management/
│   └── *.yaml
├── src/
└── ...
```

### 2. Create Local Files from Templates

Copy templates to create your local (gitignored) files:

```bash
cd .model-assessor

# One-time setup
cp computer-profile/hardware-profile.template.yaml computer-profile/hardware-profile.yaml
cp computer-profile/software-profile.template.yaml computer-profile/software-profile.yaml
cp model-data/model-lookup.template.json model-data/model-lookup.json
cp model-data/assessed-models.template.md model-data/assessed-models.md
```

Or run the setup block from `model-assessment-prompt.yaml` — it copies templates if the target files don't exist.

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

Use `model-assessment-prompt.yaml` + your hardware profile + Ollama model URLs. Send to `gpt-oss:20b` (or a capable cloud LLM). The prompt instructs copying templates if needed, then populates your local `model-lookup.json` and `assessed-models.md`.

### 5. Model Selection: Configure Your Agents

Give your coding agent the model selector prompt + your hardware profile + your local model database:

```text
[System: contents of .model-assessor/model-selector-prompt.yaml]
[Hardware: contents of .model-assessor/computer-profile/hardware-profile.yaml]
[Models: contents of .model-assessor/model-data/model-lookup.json]

I'm setting up Cline for coding tasks. What models should I configure?
```

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

### Template Shell → Local Assessments

The repo ships **templates**, not pre-assessed models. Your local `model-lookup.json` and `assessed-models.md` start empty (or with example placeholders) and are filled by running assessments on your machine.

### Adding New Models

When a new model appears on Ollama that might outperform existing options:

1. Use `model-assessment-prompt.yaml` + your local `hardware-profile.yaml`
2. Provide the Ollama URL(s) for the new model(s)
3. Send to `gpt-oss:20b` (default local assessor) or a capable cloud LLM
4. Merge the JSON output into your local `model-data/model-lookup.json`
5. Add documentation to your local `model-data/assessed-models.md`

Your local model database evolves with your needs—add models that work for your hardware and workflows. All assessments stay local.

---

## Agent Model Management

The `agent-model-management/` folder holds reference configs and instructions for keeping agent/IDE tools (e.g. Continue) in sync with your local model data.

See [agent-model-management/README.md](agent-model-management/README.md) for:
- How to update Continue's `config.yaml` when models change
- Role mapping from `model-lookup.json` to agent configs
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

See your local `model-data/model-lookup.json` for complete role mappings and `assessed-models.md` for detailed descriptions.

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
| `computer-profile/hardware-profile.template.yaml` | ✓ | Template for hardware specs |
| `computer-profile/software-profile.template.yaml` | ✓ | Template for IDE/agent setup |
| `computer-profile/hardware-profile.yaml` | ✗ local | Your hardware specs (gitignored) |
| `computer-profile/software-profile.yaml` | ✗ local | Your IDE/agent config (gitignored) |
| `model-data/model-lookup.template.json` | ✓ | Template for model database |
| `model-data/assessed-models.template.md` | ✓ | Template for model docs |
| `model-data/model-lookup.json` | ✗ local | Your model database (gitignored) |
| `model-data/assessed-models.md` | ✗ local | Your model docs (gitignored) |
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

### @LLM: Task Routing

| User wants to... | Load these files | Action |
|------------------|------------------|--------|
| Select a model | `computer-profile/hardware-profile.yaml` + `model-data/model-lookup.json` | Return structured recommendation |
| Get model details | `model-data/assessed-models.md` | Summarize specs and caveats |
| Assess new model | `computer-profile/hardware-profile.yaml` + `model-assessment-prompt.yaml` | Copy templates if missing, then generate JSON + Markdown |
| Install a model | `model-data/model-lookup.json` | Return `models.{name}.install` |

**Note:** If local files don't exist, copy from `*.template.*` first.

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

### @LLM: Model Database Schema

```text
models.{model:tag}         → {vram, ctx, class, tps, install, url, ...}
by_role.{role}.primary     → default model for role
by_role.{role}.{variant}   → alternative (e.g., "quick", "quality")
by_constraint.{constraint} → array of matching models
decision_tree.{need}       → fallback chain
```

<!-- END LLM INSTRUCTIONS -->

---

## License

For personal use. Individual models have their own licenses — check each model's Ollama page.
