# Model Assessment System

A structured system for evaluating, selecting, and deploying AI models on a **Mac Mini M4 Pro (64GB Unified RAM)** via Ollama.

---

## For Humans: How to Use This System

### Option 1: Quick Lookup (No LLM Needed)
1. Open `ollama model URLs.md`
2. Find the **Quick Reference** table
3. Pick a model based on your role (coding, vision, etc.)
4. Copy the install command from the **Installation Commands** section

### Option 2: Ask Your LLM to Help You Choose
**Copy-paste this to your LLM:**
```
I need help selecting a local Ollama model. Here is my model assessment system:

[Paste the contents of model-lookup.json here]

My task is: [describe your task]
My constraints are: [VRAM limit, speed needs, etc.]
```

### Option 3: Full Context Mode (Best Results)
For the most accurate recommendations, give your LLM multiple files:

1. **System prompt:** Copy contents of `model-selector-prompt.yaml`
2. **Context:** Copy contents of `model-lookup.json`
3. **Reference (optional):** Copy relevant sections from `Assessed models.md`

**Example prompt:**
```
[System: Use the model-selector-prompt.yaml content]

Here is my model database:
[Paste model-lookup.json]

I need to: analyze screenshots of code and then refactor the code I see.
What models should I use?
```

### Option 4: Assess a New Model
When a new model appears on Ollama that you want to evaluate:

1. Copy contents of `Model assessment prompt.yaml`
2. Replace `[INSERT LIST OF URLS/MODELS HERE]` with the Ollama URL(s)
3. Send to a capable LLM (Claude, GPT-4, or locally: qwen3-coder:30b)
4. Review the JSON output
5. **First:** Merge into `model-lookup.json` (the machine-readable source of truth)
6. **Then:** Update `Assessed models.md` (human-readable documentation)
7. Update `ollama model URLs.md` tables and install commands

---

## File Reference

| File | What It's For | When to Use It |
|------|---------------|----------------|
| `README.md` | This guide | Start here |
| `model-lookup.json` | **Source of truth** (machine-readable) | Give to LLM for model selection |
| `model-selector-prompt.yaml` | Makes LLM a model advisor | Use as system prompt |
| `Assessed models.md` | Human-readable documentation | Deep dive on specific models |
| `Model assessment prompt.yaml` | Evaluate new models | When new models release |
| `ollama model URLs.md` | Install commands + tables | Quick human reference |

---

## Hardware Quick Reference

| Class | VRAM | Speed | Best For |
|------|------|-------|----------|
| Utility | 1-4GB | 100-1000 t/s | Embedding, OCR |
| Speedster Class | <8GB | 80-120 t/s | Autocomplete, Vision |
| Middleweight Class | 8-12GB | 40-80 t/s | Daily Driver |
| Daily Driver Class | 12-24GB | 20-40 t/s | Reasoning, Coding |
| Heavy Lifter Class | 30-48GB | 10-20 t/s | Quality-Critical |

**Concurrency Rule:** You can run 1 Utility + 1 Speedster Class + 1 Middleweight/Daily Driver Class model simultaneously. Heavy Lifter Class runs solo.

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
| Select a model for a task | `model-lookup.json` | Query by_role and by_constraint, return recommendation |
| Get full details on a model | `Assessed models.md` | Find the model entry, summarize specs and caveats |
| Assess a new model | `Model assessment prompt.yaml` | Follow the prompt to generate JSON, then update docs |
| Install models | `ollama model URLs.md` | Provide the `ollama pull` commands |

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
  action: Load model-lookup.json, respond with structured recommendation

  keywords_model_details:
    - "tell me about"
    - "specs for"
    - "what is"
    - "details on"
  action: Load Assessed models.md, find matching entry

  keywords_new_assessment:
    - "assess this model"
    - "evaluate"
    - "new model"
    - "add to assessment"
  action: Load Model assessment prompt.yaml, follow its format

  keywords_installation:
    - "install"
    - "pull"
    - "download"
    - "ollama pull"
  action: Load ollama model URLs.md, provide commands

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
  - "Speedster Class models can always co-run with larger models"
  - "Heavy Lifter Class models (qwen3:72b) run solo - no co-running"
  - "Rule: If (model_vram + 8) < 50, can co-run with Speedster Class"

class_definitions:
  Utility: "Embedding/OCR, 1-4GB, always-on"
  Speedster_Class: "<8GB, 80-120 t/s, autocomplete/vision"
  Middleweight_Class: "8-12GB, 40-80 t/s, daily driver"
  Daily_Driver_Class: "12-24GB, 20-40 t/s, reasoning/coding"
  Heavy_Lifter_Class: "30-48GB, 10-20 t/s, quality-critical"

special_capabilities:
  fim_support: ["granite4:350m", "granite4:1b", "granite4:3b"]
  vision: ["gemma3:4b", "qwen3-vl:8b", "ministral-3:8b", "gemma3:12b", "gemma3:27b"]
  tools: ["granite4:3b", "ministral-3:*", "gpt-oss:20b", "qwen3-coder:30b"]
  reasoning: ["gpt-oss:20b", "deepseek-v3.1:16b"]
```

---

### @LLM: File Schemas

**When parsing `model-lookup.json`:**
```
by_role.{role}.primary     → Recommended model for this role
by_role.{role}.{variant}   → Alternative (e.g., "quick", "multilingual")
by_constraint.{constraint} → Array of models meeting this constraint
models.{model:tag}         → Specs object {vram, ctx, class, tps, ...}
decision_tree.{need}       → Fallback chain as string
```

**When reading `Assessed models.md`:**
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
   - Class: Daily Driver Class | VRAM: 14GB | Speed: ~35 t/s
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
1. Use `Model assessment prompt.yaml` to generate assessment
2. **First:** Add to `model-lookup.json` (the source of truth):
   - `models` object (specs)
   - `by_role` (if it fills a role)
   - `by_constraint` (all applicable constraints)
3. **Then:** Add to `Assessed models.md` in the appropriate class section
4. Add to `ollama model URLs.md` class table
5. Update install commands if it's a recommended model

### Files to Update Together
When you change one file, check if others need updates:
- `model-lookup.json` (source of truth) → `Assessed models.md` (human docs)
- `model-lookup.json` ↔ `model-selector-prompt.yaml` (decision logic)
- Any model change → `ollama model URLs.md` tables

---

## License

This assessment system is for personal use. Individual models have their own licenses — check each model's Ollama page.
