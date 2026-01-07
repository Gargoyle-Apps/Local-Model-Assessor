# Local Model Assessor

A system for selecting and configuring local Ollama models for AI coding agents.

**Prerequisites:**
- [Ollama](https://ollama.com) installed and running
- For model assessment: `ollama pull gpt-oss:20b` (14GB VRAM)

---

## Quick Start

### 1. Add to Your Project

Copy this package into your project's root directory:

```bash
# Clone into your project
git clone https://github.com/your-org/local-model-assessor.git .model-assessor

# Or copy the folder directly
cp -r /path/to/local-model-assessor .model-assessor
```

The package lives alongside your project code. Your coding agents can reference these files for model selection.

```text
your-project/
├── .model-assessor/          # This package
│   ├── computer-profile/
│   ├── model-data/
│   └── *.yaml
├── src/
└── ...
```

### 2. Define Your Environment

Edit the profile files in `.model-assessor/computer-profile/` to match your system:

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

### 3. Model Selection: Configure Your Agents

Give your coding agent the model selector prompt + your hardware profile + the model database:

```text
[System: contents of .model-assessor/model-selector-prompt.yaml]
[Hardware: contents of .model-assessor/computer-profile/hardware-profile.yaml]
[Models: contents of .model-assessor/model-data/model-lookup.json]

I'm setting up Cline for coding tasks. What models should I configure?
```

The selector will recommend models based on your hardware constraints and the agent's needs.

### 4. Install & Configure

Install the recommended models:
```bash
ollama pull <model:tag>
```

Configure your agent's settings file with the recommended models.

### 5. Ad-Hoc Selection

When switching tasks or needing a different capability, invoke the model selector:

```text
What model should I use for [vision tasks / creative writing / RAG / etc.]?
```

---

## Model Hydration

### Using the Existing Model Database

The `model-data/` folder contains pre-assessed models ready to use:
- `model-lookup.json` — Machine-readable specs, install commands, role mappings
- `assessed-models.md` — Human-readable descriptions and caveats

### Adding New Models

When a new model appears on Ollama that might outperform existing options:

1. Use `model-assessment-prompt.yaml` + your hardware profile
2. Provide the Ollama URL(s) for the new model(s)
3. Send to `gpt-oss:20b` (default local assessor) or a capable cloud LLM
4. Merge the JSON output into `model-data/model-lookup.json`
5. Add documentation to `model-data/assessed-models.md`

Your local model database evolves with your needs—add models that work for your hardware and workflows.

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

See `model-data/model-lookup.json` for complete role mappings and `assessed-models.md` for detailed descriptions.

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

| File | Purpose |
|------|---------|
| `computer-profile/hardware-profile.yaml` | Your hardware specs and VRAM constraints |
| `computer-profile/software-profile.yaml` | Your IDE and coding agent setup |
| `model-data/model-lookup.json` | Model database (source of truth) |
| `model-data/assessed-models.md` | Human-readable model documentation |
| `model-selector-prompt.yaml` | System prompt for model selection |
| `model-assessment-prompt.yaml` | System prompt for assessing new models |

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
| Assess new model | `computer-profile/hardware-profile.yaml` + `model-assessment-prompt.yaml` | Generate JSON + Markdown |
| Install a model | `model-data/model-lookup.json` | Return `models.{name}.install` |

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
