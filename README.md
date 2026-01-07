# Model Assessment System

A structured system for evaluating, selecting, and deploying AI models on a **Mac Mini M4 Pro (64GB Unified RAM)** via Ollama.

---

## For Humans: How to Use This System

### Option 1: Quick Install (Core Fleet)
```bash
# Install the recommended core models
ollama pull embeddinggemma:latest
ollama pull deepseek-ocr:3b
ollama pull granite4:3b
ollama pull qwen3-vl:8b
ollama pull gemma3:12b
ollama pull gpt-oss:20b
ollama pull qwen3-coder:30b
```

Or look up any model in `model-data/model-lookup.json` → find the `install` field.

### Option 2: Ask Your LLM to Help You Choose
**Copy-paste this to your LLM:**
```
I need help selecting a local Ollama model. Here is my model assessment system:

[Paste the contents of model-data/model-lookup.json here]

My task is: [describe your task]
My constraints are: [VRAM limit, speed needs, etc.]
```

### Option 3: Full Context Mode (Best Results)
For the most accurate recommendations, give your LLM multiple files:

1. **System prompt:** Copy contents of `model-selector-prompt.yaml`
2. **Context:** Copy contents of `model-data/model-lookup.json`
3. **Reference (optional):** Copy relevant sections from `model-data/assessed-models.md`

**Example prompt:**
```
[System: Use the model-selector-prompt.yaml content]

Here is my model database:
[Paste model-data/model-lookup.json]

I need to: analyze screenshots of code and then refactor the code I see.
What models should I use?
```

### Option 4: Assess a New Model
When a new model appears on Ollama that you want to evaluate:

1. Copy contents of `model-assessment-prompt.yaml`
2. Replace `[INSERT LIST OF URLS/MODELS HERE]` with the Ollama URL(s)
3. Send to a capable LLM (Claude, GPT-4, or locally: qwen3-coder:30b)
4. Review the JSON output
5. **First:** Merge into `model-data/model-lookup.json` (source of truth — includes URL and install command)
6. **Then:** Update `model-data/assessed-models.md` (human-readable documentation)

---

## File Reference

| File | What It's For | When to Use It |
|------|---------------|----------------|
| `README.md` | This guide | Start here |
| `model-data/model-lookup.json` | **Source of truth** — specs, URLs, install commands | Give to LLM for model selection |
| `model-data/assessed-models.md` | Human-readable documentation | Deep dive on specific models |
| `model-selector-prompt.yaml` | Makes LLM a model advisor | Use as system prompt |
| `model-assessment-prompt.yaml` | Evaluate new models | When new models release |

---

## Hardware Quick Reference

| Class | VRAM | Speed | Best For |
|------|------|-------|----------|
| Utility | 1-4GB | 100-1000 t/s | Embedding, OCR |
| Speedster | <8GB | 80-120 t/s | Autocomplete, Vision |
| Middleweight | 8-12GB | 45-50 t/s | Daily Driver |
| Daily Driver | 12-24GB | 25-40 t/s | Reasoning, Coding |
| Heavy Lifter | 30-48GB | ~15 t/s | Quality-Critical |

**Concurrency Rule:** You can run 1 Utility + 1 Speedster + 1 Middleweight/Daily Driver model simultaneously. Heavy Lifters run solo.

---

<!-- 
╔══════════════════════════════════════════════════════════════════════════════╗
║                           LLM ROUTING INSTRUCTIONS                           ║
║                                                                              ║
║  The section below contains instructions for AI assistants.                  ║
║  Humans can ignore this section - it's metadata for LLMs.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

## LLM Instructions

> **Note for humans:** This section tells LLMs how to behave when they encounter these files. You can skip this unless you're curious about how the routing works.

---

### @LLM: If you are reading this file

You are in a **Model Assessment System** for a Mac Mini M4 Pro with 64GB RAM running Ollama.

**Identify your task:**

| If the user wants to... | Load these files | Your role |
|-------------------------|------------------|-----------|
| Select a model for a task | `model-data/model-lookup.json` | Query by_role and by_constraint, return recommendation |
| Get full details on a model | `model-data/assessed-models.md` | Find the model entry, summarize specs and caveats |
| Assess a new model | `model-assessment-prompt.yaml` | Follow the prompt to generate JSON, then update docs |
| Install models | `model-data/model-lookup.json` | Look up model.install field for commands |

---

### @LLM: Routing Rules

```yaml
# ROUTING LOGIC - Parse and follow

task_detection:
  keywords_model_selection:
    - "which model"
    - "what model"
    - "recommend a model"
    - "select a model"
    - "best model for"
  action: Load model-data/model-lookup.json, respond with structured recommendation

  keywords_model_details:
    - "tell me about"
    - "specs for"
    - "what is"
    - "details on"
  action: Load model-data/assessed-models.md, find matching entry

  keywords_new_assessment:
    - "assess this model"
    - "evaluate"
    - "new model"
    - "add to assessment"
  action: Load model-assessment-prompt.yaml, follow its format

  keywords_installation:
    - "install"
    - "pull"
    - "download"
    - "ollama pull"
  action: Load model-data/model-lookup.json, return model.install command

response_format:
  model_selection:
    template: |
      **Recommended:** `{model:tag}`
      **Class:** {class}
      **VRAM:** {vram}GB
      **Speed:** ~{tps} t/s
      **Why:** {reasoning}
      **Alternative:** `{alt_model}` ({alt_reason})
  
  model_details:
    template: |
      ## {model:tag}
      **Class:** {class} | **VRAM:** {vram}GB | **Context:** {ctx} | **Speed:** ~{tps} t/s
      
      {description}
      
      **Best for:** {best_for}
      **Caveats:** {caveats}
```

---

### @LLM: Key Constraints to Enforce

```yaml
hardware_constraints:
  max_vram: 50  # GB safe for Ollama
  system_headroom: 14  # GB reserved for macOS/IDE
  unified_memory: 64  # GB total

concurrency_rules:
  - "Speedster models can always co-run with larger models"
  - "Heavy Lifter models (qwen3:72b) run solo - no co-running"
  - "Rule: If (model_vram + 8) < 50, can co-run with Speedster"

class_definitions:
  Utility: "Embedding/OCR, 1-4GB, always-on"
  Speedster: "<8GB, 80-120 t/s, autocomplete/vision"
  Middleweight: "8-12GB, 45-50 t/s, daily driver"
  Daily_Driver: "12-24GB, 25-40 t/s, reasoning/coding"
  Heavy_Lifter: "30-48GB, ~15 t/s, quality-critical"

special_capabilities:
  fim_support: ["granite4:350m", "granite4:1b", "granite4:3b"]
  vision: ["gemma3:4b", "qwen3-vl:8b", "ministral-3:8b", "gemma3:12b", "gemma3:27b"]
  tools: ["granite4:3b", "ministral-3:*", "gpt-oss:20b", "qwen3-coder:30b"]
  reasoning: ["gpt-oss:20b", "deepseek-v3.1:16b"]
```

---

### @LLM: File Schemas

**When parsing `model-data/model-lookup.json`:**
```
by_role.{role}.primary     → Recommended model for this role
by_role.{role}.{variant}   → Alternative (e.g., "quick", "multilingual")
by_constraint.{constraint} → Array of models meeting this constraint
models.{model:tag}         → Specs object {vram, ctx, class, tps, ...}
decision_tree.{need}       → Fallback chain as string
```

**When reading `model-data/assessed-models.md`:**
```
Human-readable Markdown documentation. Use for:
- Detailed model descriptions and reasoning
- Caveats and best-for use cases
- Role architecture explanations
- Creative tier guidance
```

---

### @LLM: Example Interactions

**User:** "I need to process PDFs and answer questions about them"

**Your reasoning:**
1. PDF processing = OCR (deepseek-ocr:3b) for extraction
2. Q&A = RAG task → needs reasoning (gpt-oss:20b or deepseek-v3.1:16b)
3. Check concurrency: 4GB + 14GB = 18GB < 50GB ✓

**Your response:**
```
**Pipeline Recommendation:**

1. **OCR Stage:** `deepseek-ocr:3b`
   - Class: Utility | VRAM: 4GB | Speed: ~100 t/s
   - Extracts text from PDF pages

2. **Q&A Stage:** `gpt-oss:20b`
   - Class: Daily Driver | VRAM: 14GB | Speed: ~35 t/s
   - Answers questions with chain-of-thought reasoning

**Total VRAM:** 18GB (can run both simultaneously)
**Alternative Q&A:** `deepseek-v3.1:16b` (better for math/structured data)
```

---

<!-- END LLM INSTRUCTIONS -->

## Role Categories

### Technical Roles
| Role | Primary Model | Description |
|------|---------------|-------------|
| `autocomplete` | granite4:3b | Fast code/text completion (FIM) |
| `vision` | qwen3-vl:8b | Image understanding |
| `coding` | qwen3-coder:30b | Repository-scale code gen |
| `formatting` | granite4:14b | JSON/SQL structured output |

### Writing & Composition
| Role | Draft | Quality | Polish |
|------|-------|---------|--------|
| `creative_writer` | gemma3:12b | gemma3:27b | qwen3:72b |
| `copywriter` | gemma3:12b | gpt-oss:20b | gemma3:27b |
| `technical_writer` | — | granite4:14b | gpt-oss:20b |

### Analysis & Assessment
| Role | Primary Model | Notes |
|------|---------------|-------|
| `document_analyst` | deepseek-v3.1:16b | Requires embedding |
| `writing_critic` | gpt-oss:20b | Shows reasoning |
| `contract_reviewer` | granite4:14b | Precision-focused |
| `research_synthesizer` | deepseek-v3.1:16b | RAG pipeline |
| `fact_checker` | gpt-oss:20b | Visible reasoning chain |

### Creative & Narrative
| Role | Draft | Quality | Polish |
|------|-------|---------|--------|
| `storyteller` | gemma3:12b | gemma3:27b | qwen3:72b |
| `worldbuilder` | — | gemma3:27b | — |
| `character_developer` | gemma3:12b | gemma3:27b | qwen3:72b |
| `dialogue_writer` | gemma3:12b | gemma3:27b | qwen3:72b |
| `game_master` | ministral-3:14b | gemma3:27b | — |

### Business & Professional
| Role | Primary Model | Notes |
|------|---------------|-------|
| `executive_summarizer` | gemma3:12b | Speed-focused |
| `proposal_writer` | gpt-oss:20b | Reasoning for structure |
| `strategy_analyst` | gpt-oss:20b | Chain-of-thought |

### Education
| Role | Primary Model | Notes |
|------|---------------|-------|
| `tutor` | gemma3:12b | gpt-oss for math |
| `quiz_generator` | granite4:14b | Structured output |
| `study_guide` | deepseek-v3.1:16b | Requires embedding |
| `eli5_explainer` | gemma3:12b | Accessible language |

### Utility & General
| Role | Primary Model | Description |
|------|---------------|-------------|
| `embedding` | embeddinggemma:latest | Vector generation |
| `ocr` | deepseek-ocr:3b | Image → text |
| `translator` | gemma3:12b | + qwen3-embedding |
| `daily_driver` | gemma3:12b | General assistant |
| `reasoning` | gpt-oss:20b | Logic tasks |
| `heavy_lifter` | qwen3:72b | Quality-critical |

---

## Creative Quality Classes

For writing and creative tasks, choose based on stage:

| Stage | Speed | Model | Use When |
|-------|-------|-------|----------|
| 🎨 **Draft** | Fast | gemma3:12b | Brainstorming, iteration, exploration |
| 🎨 **Quality** | Medium | gemma3:27b | Substantive drafts, good output |
| 🎨 **Polish** | Slow | qwen3:72b | Final version, publication-ready |

---

## Maintenance Notes

### Adding a New Model
1. Use `model-assessment-prompt.yaml` to generate assessment
2. **First:** Add to `model-data/model-lookup.json` (the source of truth):
   - `models` object (specs, url, install command)
   - `by_role` (if it fills a role)
   - `by_constraint` (all applicable constraints)
3. **Then:** Add to `model-data/assessed-models.md` in the appropriate class section

### Files to Update Together
When you change one file, check if others need updates:
- `model-data/model-lookup.json` (source of truth) → `model-data/assessed-models.md` (human docs)
- `model-data/model-lookup.json` ↔ `model-selector-prompt.yaml` (decision logic)

---

## License

This assessment system is for personal use. Individual models have their own licenses — check each model's Ollama page.
