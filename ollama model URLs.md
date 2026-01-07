# Ollama Model URLs - Mac Mini M4 Pro (64GB)

## Related Files
| File | Purpose |
|------|---------|
| `README.md` | **Start here.** System overview and usage guide |
| `Assessed models.yaml` | Full model assessments with documentation |
| `model-lookup.json` | Machine-readable lookup table for tool-calling LLMs |
| `model-selector-prompt.yaml` | System prompt for model selection agent |
| `Model assessment prompt.yaml` | Prompt template for assessing new models |

---

## Source URLs (Raw List)

```
https://ollama.com/library/embeddinggemma
https://ollama.com/library/qwen3-embedding
https://ollama.com/library/deepseek-ocr
https://ollama.com/library/granite4
https://ollama.com/library/gemma3
https://ollama.com/library/ministral-3
https://ollama.com/library/qwen3-vl
https://ollama.com/library/qwen3-coder
https://ollama.com/library/qwen3
https://ollama.com/library/gpt-oss
https://ollama.com/library/deepseek-v3.1
https://ollama.com/library/nemotron-3-nano
```

---

## Utility Models (Always Running / Specialized)

### Embedding Models
| Model | Tag | VRAM | Context | Notes |
|-------|-----|------|---------|-------|
| [embeddinggemma](https://ollama.com/library/embeddinggemma) | `:latest` | 1.5GB | 8K | English-only, high MTEB score |
| [qwen3-embedding](https://ollama.com/library/qwen3-embedding) | `:large` | 2GB | 32K | Multilingual (100+ languages) |

### OCR Models
| Model | Tag | VRAM | Context | Notes |
|-------|-----|------|---------|-------|
| [deepseek-ocr](https://ollama.com/library/deepseek-ocr) | `:3b` | 4GB | 4K | Pure transcription, no reasoning |

---

## Generation Models (By Class)

### Speedster Class: Speedsters (<8GB)
| Model | Tag | VRAM | Context | Role |
|-------|-----|------|---------|------|
| [granite4](https://ollama.com/library/granite4) | `:350m` | 0.7GB | 32K | **Autocomplete** (FIM native) |
| [granite4](https://ollama.com/library/granite4) | `:3b` | 2.1GB | 128K | Autocomplete + Tools |
| [granite4](https://ollama.com/library/granite4) | `:1b` | 3.3GB | 128K | Small tasks (fp16) |
| [gemma3](https://ollama.com/library/gemma3) | `:4b` | 3.3GB | 128K | Autocomplete + Vision |
| [ministral-3](https://ollama.com/library/ministral-3) | `:3b` | 3GB | 256K | Edge Agentic |
| [qwen3-vl](https://ollama.com/library/qwen3-vl) | `:8b` | 6.1GB | 128K | **Vision Engine** |
| [qwen3-vl](https://ollama.com/library/qwen3-vl) | `:8b-thinking` | 6.1GB | 128K | Vision + Reasoning |
| [ministral-3](https://ollama.com/library/ministral-3) | `:8b` | 6GB | 256K | Vision + Tools |

### Middleweight Class: Middleweights (8-12GB)
| Model | Tag | VRAM | Context | Role |
|-------|-----|------|---------|------|
| [gemma3](https://ollama.com/library/gemma3) | `:12b` | 8.1GB | 128K | **Daily Driver** |
| [ministral-3](https://ollama.com/library/ministral-3) | `:14b` | 9.1GB | 256K | Agentic Daily Driver |
| [granite4](https://ollama.com/library/granite4) | `:14b` | 10GB | 32K | Enterprise Formatter |

### Daily Driver Class: Daily Drivers (12-24GB)
| Model | Tag | VRAM | Context | Role |
|-------|-----|------|---------|------|
| [deepseek-v3.1](https://ollama.com/library/deepseek-v3.1) | `:16b` | 12GB | 32K | RAG Synthesizer |
| [gpt-oss](https://ollama.com/library/gpt-oss) | `:20b` | 14GB | 128K | **Reasoning Engine** |
| [nemotron-3-nano](https://ollama.com/library/nemotron-3-nano) | `:30b` | 24GB | 256K | MoE Reasoning + Agentic |
| [gemma3](https://ollama.com/library/gemma3) | `:27b` | 17GB | 64K | Quality Daily Driver |
| [qwen3-coder](https://ollama.com/library/qwen3-coder) | `:30b` | 19GB | 64K | **Coding Engine** |

### Heavy Lifter Class: Heavy Lifters (30-48GB)
| Model | Tag | VRAM | Context | Role |
|-------|-----|------|---------|------|
| [qwen3](https://ollama.com/library/qwen3) | `:72b` (q3_k_m) | 38GB | 4K | **Heavy Lifter** |

---

## Not Recommended (Exceed 50GB Budget)
- `gpt-oss:120b` — 65GB, won't fit
- `qwen3-coder:480b` — 290GB, requires cluster
- `qwen3-vl:235b` — 143GB, requires cluster

---

## Quick Reference: Primary Roles

| Role | Model | Class | Speed |
|------|-------|------|-------|
| Embedding | `embeddinggemma:latest` | Utility | ~1000 t/s |
| OCR | `deepseek-ocr:3b` | Utility | ~100 t/s |
| Autocomplete | `granite4:3b` | S | ~120 t/s |
| Vision | `qwen3-vl:8b` | S | ~80 t/s |
| Vision + Reasoning | `qwen3-vl:8b-thinking` | S | ~70 t/s |
| Daily Driver | `gemma3:12b` | M | ~50 t/s |
| Formatter | `granite4:14b` | M | ~45 t/s |
| Reasoning | `gpt-oss:20b` | D | ~35 t/s |
| Reasoning (Long Context) | `nemotron-3-nano:30b` | D | ~30 t/s |
| Coding | `qwen3-coder:30b` | D | ~25 t/s |
| Heavy Lifter | `qwen3:72b` | H | ~15 t/s |

---

## Installation Commands

### Core Fleet (Recommended Minimum)
```bash
# Utility
ollama pull embeddinggemma:latest
ollama pull deepseek-ocr:3b

# Speedster Class - Autocomplete & Vision
ollama pull granite4:3b
ollama pull qwen3-vl:8b

# Middleweight Class - Daily Driver
ollama pull gemma3:12b

# Daily Driver Class - Workhorses
ollama pull gpt-oss:20b
ollama pull qwen3-coder:30b
```

### Full Fleet (All Assessed Models)
```bash
# Utility: Embedding
ollama pull embeddinggemma:latest
ollama pull qwen3-embedding:large

# Utility: OCR
ollama pull deepseek-ocr:3b

# Speedster Class
ollama pull granite4:350m
ollama pull granite4:1b
ollama pull granite4:3b
ollama pull gemma3:4b
ollama pull ministral-3:3b
ollama pull ministral-3:8b
ollama pull qwen3-vl:8b
ollama pull qwen3-vl:8b-thinking

# Middleweight Class
ollama pull gemma3:12b
ollama pull ministral-3:14b
ollama pull granite4:14b

# Daily Driver Class
ollama pull deepseek-v3.1:16b
ollama pull gpt-oss:20b
ollama pull nemotron-3-nano:30b
ollama pull gemma3:27b
ollama pull qwen3-coder:30b

# Heavy Lifter Class (use sparingly - 38GB)
ollama pull qwen3:72b
```

### VRAM Budget Check
```bash
# Total if ALL models loaded (not recommended):
# Utility:     ~7.5GB
# Speedster Class:      ~31GB
# Middleweight Class:      ~27GB
# Daily Driver Class:      ~86GB
# Heavy Lifter Class:      ~38GB

# Recommended concurrent loading:
# - 1 Utility model (embedding OR ocr)
# - 1 Speedster Class model (autocomplete)
# - 1 Middleweight/Daily Driver Class model (active task)
# Example: embeddinggemma (1.5) + granite4:3b (2.1) + gpt-oss:20b (14) = 17.6GB
```
