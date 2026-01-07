# Assessed Models — Mac Mini M4 Pro (64GB)

A human-readable reference for all evaluated Ollama models. For machine-readable data, see [`model-lookup.json`](./model-lookup.json).

---

## Hardware Classes

| Class | VRAM | Speed | Co-run? | Use Case |
|-------|------|-------|---------|----------|
| **Utility** | 1-4GB | 100-1000 t/s | Always | Embedding, OCR |
| **Speedster** | <8GB | 80-120 t/s | Always | Autocomplete, quick tasks |
| **Middleweight** | 8-12GB | 45-50 t/s | Yes | Daily driver, interactive |
| **Daily Driver** | 12-24GB | 25-40 t/s | Yes | Reasoning, coding |
| **Heavy Lifter** | 30-48GB | ~15 t/s | **No** | Quality-critical |

**Concurrency Rule:** 1 Utility + 1 Speedster + 1 larger model can run simultaneously. Heavy Lifters run solo.

---

## Creative Quality Tiers

For writing and creative tasks, choose based on stage:

| Stage | Model | Speed | When to Use |
|-------|-------|-------|-------------|
| 🎨 **Draft** | gemma3:12b | ~50 t/s | Brainstorming, iteration |
| 🎨 **Quality** | gemma3:27b | ~25 t/s | Substantive drafts |
| 🎨 **Polish** | qwen3:72b | ~15 t/s | Publication-ready |

---

## Utility Models

### Embedding Models

#### embeddinggemma:latest
| Spec | Value |
|------|-------|
| VRAM | 1.5GB |
| Context | 8K |
| Speed | ~1000 t/s |
| Quantization | fp16 |

A distilled embedding model from Google's Gemma architecture. Optimized for English semantic retrieval with high MTEB scores.

**Best for:** Indexing local documents, semantic search, English RAG pipelines

**Caveats:** English-only. Do not chat with this model—it only generates vectors.

---

#### qwen3-embedding:large
| Spec | Value |
|------|-------|
| VRAM | 2GB |
| Context | 32K |
| Speed | ~800 t/s |
| Quantization | fp16 |

Massive multilingual embedding model supporting 100+ languages. Matches the Qwen3 tokenizer for perfect compatibility.

**Best for:** Multilingual document search, codebase indexing, non-English RAG

**Caveats:** Slightly heavier than Gemma. Do not chat with this model.

---

### OCR Models

#### deepseek-ocr:3b
| Spec | Value |
|------|-------|
| VRAM | 4GB |
| Context | 4K |
| Speed | ~100 t/s |
| Quantization | q8_0 |

A specialized vision-only model for OCR and converting screenshots to HTML/Markdown. Pure transcription, no reasoning.

**Best for:** Reading screenshots, digitizing handwritten notes, PDF extraction, image-to-HTML

**Caveats:** Cannot reason about images—only transcribes. Use qwen3-vl for understanding.

---

## Speedster Class Models (<8GB)

### granite4:350m
| Spec | Value |
|------|-------|
| VRAM | 0.7GB |
| Context | 32K |
| Speed | ~200 t/s |
| Quantization | q8_0 |
| Special | **FIM native** |

IBM's tiniest Granite 4. 350M parameters with native Fill-In-the-Middle support for code completions.

**Best for:** Code autocomplete (FIM), inline suggestions, ultra-low-latency responses

**Caveats:** Limited reasoning. Use only for quick completions, not complex generation.

---

### granite4:3b
| Spec | Value |
|------|-------|
| VRAM | 2.1GB |
| Context | 128K |
| Speed | ~120 t/s |
| Quantization | q4_k_m |
| Special | FIM, Tools |

IBM Granite 4 "Micro" with FIM support, tool calling, and 128K context. Multilingual (12 languages).

**Best for:** Code autocomplete with long context, lightweight function calling, JSON output

**Caveats:** Enterprise-focused; can feel "dry" for creative tasks.

---

### granite4:1b
| Spec | Value |
|------|-------|
| VRAM | 3.3GB |
| Context | 128K |
| Speed | ~100 t/s |
| Quantization | fp16 |
| Special | FIM |

IBM Granite 4 at 1B parameters. Higher precision (fp16) for precision-sensitive tasks.

**Best for:** Quick Q&A, simple text formatting, precision-sensitive small tasks

**Caveats:** Larger file size than 3B due to less aggressive quantization.

---

### gemma3:4b
| Spec | Value |
|------|-------|
| VRAM | 3.3GB |
| Context | 128K |
| Speed | ~100 t/s |
| Quantization | q4_k_m |
| Special | Vision |

Google's Gemma 3 compact model. Supports text and image input with 128K context.

**Best for:** Quick image descriptions, fast chat, vision + text autocomplete

**Caveats:** No native FIM support. Use Granite for pure code autocomplete.

---

### ministral-3:3b
| Spec | Value |
|------|-------|
| VRAM | 3GB |
| Context | 256K |
| Speed | ~120 t/s |
| Quantization | q4_k_m |
| Special | Vision, Tools |

Mistral's edge-optimized 3B model with vision and native function calling. 256K context is exceptional for this size.

**Best for:** Lightweight function calling, edge automation, mobile/embedded use

**Caveats:** Requires Ollama 0.13.1+. Quality ceiling is lower than 8B variants.

---

### qwen3-vl:8b
| Spec | Value |
|------|-------|
| VRAM | 6.1GB |
| Context | 128K |
| Speed | ~80 t/s |
| Quantization | q4_k_m |
| Special | Vision |

The most powerful vision-language model at a runnable size. Supports image analysis, GUI understanding, and visual coding.

**Best for:** Screenshot-to-code, UI/UX analysis, visual debugging, document understanding

**Caveats:** Heavier than deepseek-ocr for pure extraction. Use OCR for transcription, this for understanding.

---

### qwen3-vl:8b-thinking
| Spec | Value |
|------|-------|
| VRAM | 6.1GB |
| Context | 128K |
| Speed | ~70 t/s |
| Quantization | q4_k_m |
| Special | Vision, Reasoning |

Qwen3-VL with thinking/reasoning capabilities. Adds step-by-step reasoning traces for complex visual tasks. Improved OCR across 32 languages.

**Best for:** Visual reasoning with step-by-step analysis, complex screenshot debugging, multilingual OCR (32 languages)

**Caveats:** Reasoning traces add latency. Use standard qwen3-vl:8b when speed matters more. Requires Ollama 0.12.7+.

---

### ministral-3:8b
| Spec | Value |
|------|-------|
| VRAM | 6GB |
| Context | 256K |
| Speed | ~80 t/s |
| Quantization | q4_k_m |
| Special | Vision, Tools |

Mistral's 8B edge model with vision, native function calling, and 256K context. Apache 2.0 licensed.

**Best for:** Visual agent tasks, agentic workflows with images, multilingual vision

**Caveats:** Requires Ollama 0.13.1+. Slightly less visual reasoning depth than Qwen3-VL.

---

## Middleweight Class Models (8-12GB)

### gemma3:12b
| Spec | Value |
|------|-------|
| VRAM | 8.1GB |
| Context | 128K |
| Speed | ~50 t/s |
| Quantization | q4_k_m |
| Special | Vision |
| Creative | Draft tier |

Google's Gemma 3 at 12B. The "Goldilocks" model—fast enough for interactive use, capable enough for most tasks.

**Best for:** General purpose assistant, code review with screenshots, document Q&A

**Caveats:** May struggle with highly complex reasoning. Step up to Daily Driver/Heavy Lifter for those cases.

---

### granite4:14b
| Spec | Value |
|------|-------|
| VRAM | 10GB |
| Context | 32K |
| Speed | ~45 t/s |
| Quantization | q5_k_m |
| Special | Tools, Structured output |

IBM's 4th generation Granite at 14B. Enterprise-focused with strict instruction adherence and no "safety refusals."

**Best for:** JSON/XML formatting, SQL generation, legal text summarization, structured output

**Caveats:** Not a conversationalist. Lacks personality. Don't use for creative writing.

---

### ministral-3:14b
| Spec | Value |
|------|-------|
| VRAM | 9.1GB |
| Context | 256K |
| Speed | ~45 t/s |
| Quantization | q4_k_m |
| Special | Vision, Tools |

Mistral's largest Ministral 3 variant. Vision-enabled with 256K context and native function calling.

**Best for:** Complex automation workflows, multi-step tool use, long-context agent tasks

**Caveats:** Requires Ollama 0.13.1+. Not the strongest at creative writing.

---

## Daily Driver Class Models (12-24GB)

### deepseek-v3.1:16b
| Spec | Value |
|------|-------|
| VRAM | 12GB |
| Context | 32K |
| Speed | ~40 t/s |
| Quantization | q4_k_m |
| Special | Reasoning, RAG |

Updated "Lite" version of DeepSeek V3. MoE architecture tailored for dense information synthesis and math.

**Best for:** Summarizing 10+ documents, math and step-by-step logic, RAG synthesis

**Caveats:** Can be dry/robotic in tone. Context limited to 32K to maintain stability.

---

### gpt-oss:20b
| Spec | Value |
|------|-------|
| VRAM | 14GB |
| Context | 128K |
| Speed | ~35 t/s |
| Quantization | mxfp4 |
| Special | Reasoning, Tools |

OpenAI's open-weight reasoning model. 20B MoE with native chain-of-thought and configurable reasoning effort. Apache 2.0.

**Best for:** Complex problem solving, code debugging with explanation, multi-step reasoning, agentic tool orchestration

**Caveats:** No vision. Pair with qwen3-vl for visual tasks. Reasoning effort increases latency.

---

### nemotron-3-nano:30b
| Spec | Value |
|------|-------|
| VRAM | 24GB |
| Context | 256K |
| Speed | ~30 t/s |
| Quantization | q4_k_m |
| Special | Reasoning, Tools, MoE |

NVIDIA's hybrid MoE architecture with 3.5B active parameters. 38.8% on SWE-Bench (highest in comparison). Supports 1M context natively.

**Best for:** Agentic coding (SWE-Bench style), long-context synthesis (up to 1M), repository-scale code understanding

**Caveats:** At 24GB, upper bound of Daily Driver Class. Reasoning traces can be disabled for speed. Requires NVIDIA Open Model License.

---

### gemma3:27b
| Spec | Value |
|------|-------|
| VRAM | 17GB |
| Context | 64K |
| Speed | ~25 t/s |
| Quantization | q4_k_m |
| Special | Vision |
| Creative | Quality tier |

Google's flagship Gemma 3. "Most capable model that runs on a single GPU." Vision-enabled with 128K native context.

**Best for:** High-quality general assistant, complex document analysis with images, creative writing

**Caveats:** Not quite Heavy Lifter quality for the most nuanced tasks.

---

### qwen3-coder:30b
| Spec | Value |
|------|-------|
| VRAM | 19GB |
| Context | 64K |
| Speed | ~25 t/s |
| Quantization | q4_k_m |
| Special | Tools, MoE |

Alibaba's flagship coding model. 30B total with 3.3B activated (MoE). Trained via RL on SWE-Bench. Native 256K context.

**Best for:** Repository-scale code understanding, complex refactoring, agentic coding, multi-file generation

**Caveats:** Cap at 64K for stability. For simple edits, use granite4:3b for speed.

---

## Heavy Lifter Class Models (30-48GB)

### qwen3:72b
| Spec | Value |
|------|-------|
| VRAM | 38GB |
| Context | 4K |
| Speed | ~15 t/s |
| Quantization | q3_k_m |
| Creative | Polish tier |

The flagship dense model of the Qwen3 family. 72B parameters rivaling proprietary frontier models.

**Best for:** Writing novels, nuanced roleplay, final polish of important text, quality-critical generation

**Caveats:** Context strictly limited to 4K-8K. Speed ~15 t/s. **Cannot co-run with other models.**

---

## Role Architecture

This section maps roles to their assigned models and explains how they interact in workflows.

### Utility Roles

| Role | Model | Class | Responsibility |
|------|-------|-------|----------------|
| Embedding Engine | embeddinggemma:latest | Utility | Vector search. Converting queries/files to vectors. |
| OCR Engine | deepseek-ocr:3b | Utility | Visual transcription. Converting pixels to text. |

### Technical Roles

| Role | Model | Class | Responsibility |
|------|-------|-------|----------------|
| Autocomplete Engine | granite4:3b | Speedster | Fast inline code/text completion (<100ms target) |
| Vision Engine | qwen3-vl:8b | Speedster | Screenshot analysis, UI understanding |
| Visual Reasoning Engine | qwen3-vl:8b-thinking | Speedster | Step-by-step visual analysis with reasoning |
| Coding Engine | qwen3-coder:30b | Daily Driver | Repository-scale code generation |
| Formatter | granite4:14b | Middleweight | Structured output (JSON, SQL) |

### Writing Roles

| Role | Draft | Quality | Polish |
|------|-------|---------|--------|
| Creative Writer | gemma3:12b | gemma3:27b | qwen3:72b |
| Copywriter | gemma3:12b | gpt-oss:20b | gemma3:27b |
| Technical Writer | — | granite4:14b | gpt-oss:20b |
| Storyteller | gemma3:12b | gemma3:27b | qwen3:72b |
| Dialogue Writer | gemma3:12b | gemma3:27b | qwen3:72b |

### Analysis Roles

| Role | Model | Class | Notes |
|------|-------|-------|-------|
| Document Analyst | deepseek-v3.1:16b | Daily Driver | Requires embedding model |
| Writing Critic | gpt-oss:20b | Daily Driver | Shows reasoning |
| Contract Reviewer | granite4:14b | Middleweight | Precision-focused |
| Research Synthesizer | deepseek-v3.1:16b | Daily Driver | RAG pipeline |
| Fact Checker | gpt-oss:20b | Daily Driver | Visible reasoning chain |

### Creative Roles

| Role | Model | Class | Notes |
|------|-------|-------|-------|
| Worldbuilder | gemma3:27b | Daily Driver | Requires embedding for consistency |
| Character Developer | gemma3:27b | Daily Driver | qwen3:72b for complex psychology |
| Game Master | gemma3:27b | Daily Driver | Requires embedding for lore |

### Business & Education Roles

| Role | Model | Class | Notes |
|------|-------|-------|-------|
| Executive Summarizer | gemma3:12b | Middleweight | Speed-focused |
| Proposal Writer | gpt-oss:20b | Daily Driver | Reasoning for structure |
| Strategy Analyst | gpt-oss:20b | Daily Driver | Chain-of-thought |
| Tutor | gemma3:12b | Middleweight | gpt-oss for math |
| Quiz Generator | granite4:14b | Middleweight | Structured output |

### General Roles

| Role | Model | Class | Notes |
|------|-------|-------|-------|
| Daily Driver | gemma3:12b | Middleweight | Default general assistant |
| Reasoning Engine | gpt-oss:20b | Daily Driver | Logic tasks with CoT |
| Heavy Lifter | qwen3:72b | Heavy Lifter | Quality-critical, runs solo |

---

## RAG Pipelines

| Pipeline | Embedding | Synthesis | Notes |
|----------|-----------|-----------|-------|
| Document Analysis | embeddinggemma:latest | deepseek-v3.1:16b | Index docs, retrieve, synthesize |
| Research | qwen3-embedding:large | deepseek-v3.1:16b | Multilingual academic papers |
| Worldbuilding | embeddinggemma:latest | gemma3:27b | Index lore, check consistency |
| Game Mastering | embeddinggemma:latest | gemma3:27b | Campaign notes, characters, world |

---

## Quick Decision Tree

| Need | Model Chain |
|------|-------------|
| Embedding | embeddinggemma:latest (or qwen3-embedding if multilingual) |
| OCR | deepseek-ocr:3b |
| Speed | granite4:350m → granite4:3b → gemma3:4b |
| Vision | qwen3-vl:8b → qwen3-vl:8b-thinking → gemma3:12b |
| Reasoning | gpt-oss:20b → nemotron-3-nano:30b |
| Coding | qwen3-coder:30b → nemotron-3-nano:30b → gpt-oss:20b |
| Quality | qwen3:72b → gemma3:27b → gpt-oss:20b |
| Tools | ministral-3:14b → gpt-oss:20b → granite4:3b |
| Creative Draft | gemma3:12b |
| Creative Quality | gemma3:27b → gpt-oss:20b |
| Creative Polish | qwen3:72b → gemma3:27b |
| Structured Output | granite4:14b → granite4:3b |
