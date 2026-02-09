# Assessed Models

A human-readable reference for all evaluated Ollama models. For machine-readable data, see [`model-lookup.json`](./model-lookup.json).

> **Hardware:** See [`hardware-profile.yaml`](../computer-profile/hardware-profile.yaml) for system specifications, VRAM budgets, and hardware class definitions.

---

## Hardware Classes

> **Source:** `computer-profile/hardware-profile.yaml` — hardware class definitions and VRAM ranges are defined there.

| Class | VRAM | Speed | Co-run? | Use Case |
|-------|------|-------|---------|----------|
| **Utility** | 1-4GB | 100-1000 t/s | Always | Embedding, OCR |
| **Speedster** | <8GB | 80-120 t/s | Always | Autocomplete, quick tasks |
| **Middleweight** | 8-12GB | 45-50 t/s | Yes | Daily driver, interactive |
| **Daily Driver** | 12-24GB | 25-40 t/s | Yes | Reasoning, coding |
| **Heavy Lifter** | 30-48GB | ~15 t/s | **No** | Quality-critical |

**Concurrency Rule:** See `computer-profile/hardware-profile.yaml` for concurrency rules. Generally: 1 Utility + 1 Speedster + 1 larger model can run simultaneously. Heavy Lifters run solo.

---

## Creative Quality Tiers

For writing and creative tasks, choose based on stage:

| Stage | Model | Speed | When to Use |
|-------|-------|-------|-------------|
| Draft | (your draft model) | ~50 t/s | Brainstorming, iteration |
| Quality | (your quality model) | ~25 t/s | Substantive drafts |
| Polish | (your polish model) | ~15 t/s | Publication-ready |

---

## Utility Models

### Embedding Models

<!-- Add assessed embedding models here using the format below -->

### OCR Models

<!-- Add assessed OCR models here using the format below -->

---

## Speedster Class Models (<8GB)

<!-- Add assessed Speedster models here -->

---

## Middleweight Class Models

<!-- Add assessed Middleweight models here -->

---

## Daily Driver Class Models (12-24GB)

<!-- Add assessed Daily Driver models here -->

---

## Heavy Lifter Class Models (30-48GB)

<!-- Add assessed Heavy Lifter models here -->

---

## Model Entry Template

Use this format when adding new models (copy and fill in):

```markdown
### model-name:tag
| Spec | Value |
|------|-------|
| VRAM | XGB |
| Context | XK |
| Speed | ~X t/s |
| Quantization | qX_X_X |
| Special | Vision, Tools, etc. |

[1-2 sentence description of what this model is and its architecture.]

**Best for:** [2-4 specific use cases]

**Caveats:** [Known limitations, requirements, or warnings]
```

---

## Role Architecture

<!-- Add role tables here after populating models -->

---

## RAG Pipelines

<!-- Add RAG pipeline tables here -->

---

## Quick Decision Tree

<!-- Add decision tree here after populating models -->
