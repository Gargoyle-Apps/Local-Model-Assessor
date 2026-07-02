---
name: lma-hf-mcp
description: "Use the Hugging Face MCP server for Hub discovery during LMA assess/import when the client is connected."
triggers:
  - huggingface mcp
  - hf mcp
  - hf-mcp-server
  - search huggingface
  - hub search
  - find gguf
  - mlx-community search
  - hugging face search
dependencies: []
version: "1.2.0"
---

# LMA Hugging Face MCP

## When to use this skill

Load when you need to **discover** Hub resources before or during LMA assessment — model/GGUF/MLX candidates, README metadata, HF library docs, datasets, or papers. Prefer MCP when **`hf-mcp-server`** is connected; otherwise use the fallbacks below and **do not block** the workflow.

**Not a dependency** of import skills — optional accelerator.

> **Cloud models excluded.** MCP may surface API/inference-only models. Only pursue **local weights** (GGUF, safetensors/MLX, downloadable artifacts). After discovery, continue with `lma-assess-import-model`, `lma-hf-gguf-ollama`, or `lma-mlx-lm` as appropriate.

**Setup (humans):** [integrations/mcp/huggingface-mcp.md](../../../integrations/mcp/huggingface-mcp.md) · enable tools at [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp).

## Instructions

### 1. Confirm MCP is usable

Try an HF MCP tool call, or infer from session context (e.g. `hf-mcp-server` in Cursor Settings → MCP).

**If connected:** continue with §2–§3.

**If not connected — graceful fallback (do not stop the task):**

1. **Suggest connect (once per task, brief):** Add `hf-mcp-server` per [integrations/mcp/huggingface-mcp.md](../../../integrations/mcp/huggingface-mcp.md) (`~/.cursor/mcp.json` or project `.cursor/mcp.json`), enable tools at [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp), reload Cursor. Speeds Hub search and README lookup from the IDE.
2. **Proceed without MCP** using the best available path:

| Need | Fallback |
|------|----------|
| Ollama catalog model | `LLM-prompts/ollama-search.md` or [ollama.com/library](https://ollama.com/library) |
| GGUF / HF repo | User-supplied URL; [huggingface.co/models](https://huggingface.co/models) search; `WebFetch` on model card URL |
| MLX conversion | [huggingface.co/mlx-community](https://huggingface.co/mlx-community) browse/search; user repo ID |
| README / license / template | `WebFetch` `https://huggingface.co/<org>/<repo>` |
| HF library how-to | [huggingface.co/docs](https://huggingface.co/docs) or targeted web search |
| Stuck | Ask user for model card URL or local `.gguf` path |

Never fail or refuse assessment/import solely because MCP is offline.

Do **not** assume MCP works from repo files alone — connection is per-machine.

### 2. Pick the right tool

| LMA phase | MCP tool | Example ask |
|-----------|----------|-------------|
| Cloud-only Ollama tag → local alt | **Model Search** | "GGUF quants for &lt;model&gt; suitable for Ollama import" |
| MLX path (no Ollama/GGUF) | **Model Search** | "mlx-community &lt;model&gt; 4-bit Apple Silicon" |
| README, license, arch hints | **Hub Repository Details** | Enable README inclusion on HF settings when offered |
| Quant / PEFT / transformers how-to | **Documentation Semantic Search** | "How do I quantize for GGUF?" / "PEFT LoRA adapters" |
| Benchmark / eval notes | **Dataset Search** | "code generation benchmark datasets" |
| Capability research | **Papers Semantic Search** | "MoE code model architecture" |
| Extra community tools | **Spaces Semantic Search** | Optional; not core LMA loop |

### 3. Discovery → assess handoff

After MCP returns a **local-runnable** candidate:

| Candidate type | Next skill |
|----------------|------------|
| In Ollama library | `lma-assess-import-model` (assess + `ollama pull`) |
| GGUF not in Ollama | `lma-hf-gguf-ollama` |
| MLX safetensors (`mlx-community/…`) | `lma-mlx-lm` |

Pass forward: repo ID, quant tag, README notes (chat template, license), download size estimate. Still run live checks (`ollama show`, benchmarks, capability probes) — MCP does not replace assessment.

**Optional scout notes:** For multi-candidate discovery, write summaries to `integrations/mcp/scout/` (gitignored). Example: `scout/qwen3-gguf-candidates.md`. Folder tracked, contents local — see [huggingface-mcp.md](../../../integrations/mcp/huggingface-mcp.md) § Scout folder. Skip for trivial one-shot lookups.

### 4. What MCP does **not** do

- Write to `model-assessor.db` — use `add-model-from-yaml.py`
- Replace `computer-profile/hardware-profile.yaml` VRAM gating
- Measure `tps`, `moe`, `structured`, `fim` — live Ollama/runtime tests still required
- Configure IDEs — `lma-ide-config` / `sweep-ide-config.py` after import

### 5. Example prompts (agent → MCP)

- "Search Hugging Face for Qwen3 GGUF files with Q4_K_M quant for local Ollama import."
- "Find mlx-community conversions of DeepSeek-R1 for Apple Silicon; prefer 4-bit."
- "Get README and license for `unsloth/Qwen3-30B-GGUF`."
- "How does transformers handle chat templates for custom models?" (documentation search)

## Checklist

- [ ] MCP connected, **or** fallback path chosen and user nudged once to connect (optional)
- [ ] Result is local weights, not cloud/API-only
- [ ] Candidate fits hardware budget (check profile before assess)
- [ ] Handed off to correct import skill with repo URL + quant
- [ ] Live assessment / benchmarks still planned
- [ ] Multi-candidate scout written to `integrations/mcp/scout/` when useful (optional)

## Notes

- HF MCP is experimental; tool names and settings may change — [HF MCP docs](https://huggingface.co/docs/hub/en/agents-mcp).
- Config lives in client MCP settings (`~/.cursor/mcp.json` or project `.cursor/mcp.json`), not in LMA scripts.
