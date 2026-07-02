# Hugging Face MCP Server

Connect Cursor (or any MCP client) to the [Hugging Face Hub MCP server](https://huggingface.co/docs/hub/en/agents-mcp) for model/dataset/Space search, documentation lookup, and community Gradio tools — useful when assessing local alternatives to cloud-only Ollama models or scouting GGUF/MLX sources.

**Prerequisites:** [Hugging Face account](https://huggingface.co/join). Feature is experimental; tools and settings evolve — see [changelog](https://huggingface.co/changelog/hf-mcp-server).

**Settings UI (canonical):** [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp) — pick your client, enable tools, add community Spaces. The page generates client-specific snippets; use it when upgrading or troubleshooting auth.

---

## Cursor setup (this repo)

This workspace ships a **project-level** config at [`.cursor/mcp.json`](../../.cursor/mcp.json):

```json
{
  "mcpServers": {
    "hf-mcp-server": {
      "url": "https://huggingface.co/mcp?login"
    }
  }
}
```

The `?login` query starts browser OAuth on first connect (HF session must be logged in).

### Activate

1. Ensure `.cursor/mcp.json` exists (tracked on the `mcp` branch).
2. **Reload Cursor** — Command Palette → *Developer: Reload Window*, or restart Cursor.
3. Open **Cursor Settings → MCP** (or the MCP panel). Confirm **hf-mcp-server** / Hugging Face is listed and connected.
4. If auth fails, open [settings/mcp](https://huggingface.co/settings/mcp) while logged in and retry; complete any browser login prompt.

### User-global config (optional)

To use HF MCP in every project, copy the same `mcpServers` block to:

| OS | Path |
|----|------|
| macOS | `~/.cursor/mcp.json` |
| Linux | `~/.cursor/mcp.json` |
| Windows | `%USERPROFILE%\.cursor\mcp.json` |

Project config merges with user config; prefer **one** place to avoid duplicate server entries.

---

## Built-in tools (enable on HF settings page)

| Tool | LMA use |
|------|---------|
| **Model Search** | Find GGUF/local weights when Ollama has only `:cloud` tags |
| **Dataset Search** | Benchmark / eval datasets for assessment notes |
| **Documentation Semantic Search** | PEFT, transformers, quant guides during import (`lma-hf-gguf-ollama`) |
| **Spaces Semantic Search** | Discover MCP Gradio apps (transcription, image gen, etc.) |
| **Papers Semantic Search** | Architecture / capability research |
| **Hub Repository Details** | README + metadata for candidate models (enable README inclusion if offered) |
| **Run and Manage Jobs** | HF Jobs infrastructure (optional; not required for local LMA workflow) |

Toggle tools at [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp). Restart/reload the client after changing enabled tools or Spaces.

---

## Example prompts (with LMA)

- “Search Hugging Face for Qwen3 GGUF quantizations suitable for Ollama import.”
- “Find mlx-community conversions of &lt;model&gt; for Apple Silicon.”
- “How do I use LoRA adapters with PEFT?” (documentation search)
- “Show datasets about code generation benchmarks.”

**Cloud models excluded:** LMA never assesses cloud-only/API proxies. Use HF MCP to find **local** GGUF or MLX weights, then assess via [`lma-hf-mcp`](../../.skills/_skills/lma-hf-mcp/SKILL.md) (discovery) → `lma-hf-gguf-ollama` or `lma-mlx-lm` (import).

---

## Scout folder (local investigation notes)

**Path:** `integrations/mcp/scout/` — tracked as an empty directory (`.gitkeep` only); **contents are gitignored**.

Use during Hub discovery **before** assessment — optional scratch space for agents and humans:

| Put here | Do not put here |
|----------|-----------------|
| MCP search summaries, candidate shortlists | `model-data/new-models.yaml` (assessment contract) |
| Quant / repo comparisons, README excerpts | `assessed-models.md` (DB export) |
| Cloud vs local triage notes | Downloaded `.gguf` / weight files |
| Per-topic files e.g. `qwen3-gguf-candidates.md` | Secrets or API tokens |

Skip writing scout files for one-off chats or when the user already supplied a final model URL. After a candidate is chosen, continue with the normal assess → `new-models.yaml` → import flow.

---

## Community Spaces (optional)

Add MCP-compatible [Gradio Spaces](https://huggingface.co/spaces?search=mcp) in HF MCP settings for extra tools. Enable **Dynamic Spaces (Experimental)** to discover compatible Spaces at runtime. Reload Cursor after adding Spaces.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Server not listed | Reload window; verify JSON in `~/.cursor/mcp.json` or `.cursor/mcp.json` |
| Auth / 401 | Log in at huggingface.co; hit `https://huggingface.co/mcp?login` in browser |
| Tools missing | Enable them on [settings/mcp](https://huggingface.co/settings/mcp); reload client |
| Duplicate servers | Remove duplicate entry from user vs project `mcp.json` |
| MCP unavailable | Agent continues via `lma-hf-mcp` fallbacks (`WebFetch`, Hub browse, user URL) — workflow must not block |

**Without MCP:** assessment and import still work. Agents should suggest connecting once (this doc + reload Cursor) then proceed manually.

---

## References

- [HF MCP docs](https://huggingface.co/docs/hub/en/agents-mcp)
- [MCP settings](https://huggingface.co/settings/mcp)
- [HF MCP endpoint](https://huggingface.co/mcp)
- [Spaces as MCP servers (Gradio)](https://www.gradio.app/guides/building-mcp-server-with-gradio)
