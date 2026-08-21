# Ollama MLX tags (Apple Silicon)

Discrete strategy for **Ollama library tags** whose name ends in `-mlx` (for example `qwen3.8:27b-mlx`). These stay on the Ollama runtime: `ollama pull`, Modelfile clones, `runtime` default `ollama`, and `sweep-ide-config.py`.

This is **not** mlx-lm. HuggingFace `mlx-community/…` safetensors that run via `mlx_lm.generate` belong in [`lma-mlx-lm`](../../lma-mlx-lm/SKILL.md). Do not set `runtime: mlx` on an Ollama `-mlx` tag.

## When it applies

Apply on **Apple Silicon** only. Detect from `computer-profile/hardware-profile.yaml` (`cpu` / `gpu` / `system` mentioning Apple, M1–M5, or Apple Silicon). Skip on Intel Macs, NVIDIA, or non-macOS.

## Tag selection (mandatory on Apple Silicon)

When assessing or pulling an Ollama library model:

1. Open the library tags page (`https://ollama.com/library/<name>/tags`) or `ollama show <name>:<size>-mlx`.
2. Prefer the **same size class** MLX tag over the GGUF default. Example: `qwen3.8:27b-mlx` beats `qwen3.8:27b` (Q4_K_M GGUF).
3. Keep the intended hardware class. Do **not** jump to `*-mlx-bf16`, huge `mxfp8`, or other premium quants just because they are MLX. Those are a separate quality choice if they still fit `vram_budget`.
4. Confirm capabilities with `ollama show` (vision, tools, thinking). If the MLX tag drops a capability the GGUF tag has, keep GGUF and record the gap in `model_docs.caveats`.
5. Do **not** pull both the GGUF default and the same-size `-mlx` tag unless the user asked for an A/B. One local copy.

`model_id` and `install` must use the chosen tag (`ollama pull qwen3.8:27b-mlx`). Clone aliases follow `<base_model_id>_<role>_<ctx>` as usual.

## Comparison ("beat")

On Apple Silicon, a same-size Ollama `-mlx` tag **beats** its GGUF sibling on performance even when VRAM class is equal. Do not skip the MLX tag because the GGUF tag is already in the DB. Treat the GGUF sibling as superseded once the MLX tag is imported (see `lma-model-prune` §A).

If no `-mlx` tag exists at that size, pull the GGUF (or HF GGUF import) as before.

## Anti-triggers

- Cloud-only tags (`:cloud`) — still excluded.
- mlx-lm / `mlx-community` Python workflow — load `lma-mlx-lm`.
- Non-Apple-Silicon hardware — GGUF remains the Ollama default.
