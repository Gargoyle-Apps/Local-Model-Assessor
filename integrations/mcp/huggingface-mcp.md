# Hugging Face MCP Server

Connect Cursor (or any MCP client) to the [Hugging Face Hub MCP server](https://huggingface.co/docs/hub/en/agents-mcp) for model/dataset/Space search, documentation lookup, and community Gradio tools — useful when assessing local alternatives to cloud-only Ollama models or scouting GGUF/MLX sources.

**Prerequisites:** [Hugging Face account](https://huggingface.co/join). Feature is experimental; tools and settings evolve — see [changelog](https://huggingface.co/changelog/hf-mcp-server).

**Settings UI (canonical):** [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp) — pick your client, enable tools, add community Spaces. The page generates client-specific snippets; use it when upgrading or troubleshooting auth.

> **REST + MCP required:** MCP alone is not enough for reliable Hub discovery. Use [hf-hub-api.md](hf-hub-api.md) + [`scripts/hf-hub-api.py`](../../scripts/hf-hub-api.py) for lists/counts, then MCP for drill-down. **Avoid `hf_hub_query`** — it hangs/timeouts without the REST layer.

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
5. **Allowlist** fast MCP tools (`hf_whoami`, `hub_repo_details`, `hub_repo_search`, `hf_doc_search`) to reduce approval friction. Do **not** rely on `hf_hub_query`.

### User-global config (optional)

To use HF MCP in every project, copy the same `mcpServers` block to:

| OS | Path |
|----|------|
| macOS | `~/.cursor/mcp.json` |
| Linux | `~/.cursor/mcp.json` |
| Windows | `%USERPROFILE%\.cursor\mcp.json` |

Project config merges with user config; prefer **one** place to avoid duplicate server entries.

---

## Hybrid discovery (REST + MCP)

| Step | Layer | Tool |
|------|-------|------|
| Lists, counts, collections, pagination | **Hub REST API** | [`hf-hub-api.py`](../../scripts/hf-hub-api.py) — see [hf-hub-api.md](hf-hub-api.md) |
| Single-repo README, targeted search, docs | **HF MCP** | `hub_repo_details`, `hub_repo_search`, `hf_doc_search` |
| Auth / transport probe | **HF MCP** | `hf_whoami` |

**Agent skill:** [`lma-hf-mcp`](../../.skills/_skills/lma-hf-mcp/SKILL.md) encodes this as mandatory workflow.

### `hf_hub_query` — avoid for now

| | |
|--|--|
| **Problem** | Multi-minute hangs; `MCP -32001` request timeout; bounded `limit`/`scan_limit` in the message does not help |
| **Use instead** | REST script for bulk; MCP tools above for drill-down |
| **Details** | [hf-hub-api.md § Avoid hf_hub_query](hf-hub-api.md) |

---

## Built-in MCP tools (enable on HF settings page)

| Tool | LMA use |
|------|---------|
| **Hub Repository Details** (`hub_repo_details`) | README + metadata for candidate models |
| **Hub Repository Search** (`hub_repo_search`) | Targeted GGUF/MLX model discovery |
| **Documentation Semantic Search** (`hf_doc_search`) | PEFT, transformers, quant guides during import |
| **Papers Semantic Search** (`paper_search`) | Architecture / capability research |
| **Spaces Semantic Search** (`space_search`) | Optional Gradio MCP apps |
| **Model Search** (legacy naming) | Prefer `hub_repo_search` + REST index |
| ~~**hf_hub_query**~~ | **Do not use** for LMA — see gap above |
| **Run and Manage Jobs** | Optional; not core LMA |

Toggle tools at [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp). Restart/reload the client after changing enabled tools or Spaces.

---

## Example prompts (with LMA)

- “List mlx-community collections (REST), then get README for the top candidate via MCP.”
- “Search Hugging Face for Qwen3 GGUF quantizations suitable for Ollama import.” (`hub_repo_search`)
- “Find mlx-community conversions of &lt;model&gt; for Apple Silicon; prefer 4-bit.” (REST index + `hub_repo_details`)
- “How do I use LoRA adapters with PEFT?” (`hf_doc_search`)

**Cloud models excluded:** LMA never assesses cloud-only/API proxies. Use REST + MCP to find **local** GGUF or MLX weights, then assess via [`lma-hf-mcp`](../../.skills/_skills/lma-hf-mcp/SKILL.md) → `lma-hf-gguf-ollama` or `lma-mlx-lm`.

---

## Scout folder (local investigation notes)

**Path:** `integrations/mcp/scout/` — tracked as an empty directory (`.gitkeep` only); **contents are gitignored**.

Use during Hub discovery **before** assessment — optional scratch space for agents and humans:

| Put here | Do not put here |
|----------|-----------------|
| REST collection totals + MCP drill-down notes | `model-data/new-models.yaml` (assessment contract) |
| Quant / repo comparisons, README excerpts | `assessed-models.md` (DB export) |
| `hf_hub_query` gap / timeout observations | Downloaded `.gguf` / weight files |
| Per-topic files e.g. `mlx-community-collections.md` | Secrets or API tokens |

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
| `hf_whoami` OK, queries hang | **Not transport** — avoid `hf_hub_query`; use [hf-hub-api.md](hf-hub-api.md) |
| MCP `-32001` timeout | Same — REST for lists; MCP only for selective tools |
| Cold start ~50s after idle | Dormant transport + OAuth refresh; run `hf_whoami` once |
| MCP unavailable | REST script + `WebFetch` + user URL — workflow must not block |

**Without MCP:** assessment and import still work via REST script and manual paths.

---

## References

- [HF Hub REST + LMA hybrid (this repo)](hf-hub-api.md)
- [HF MCP docs](https://huggingface.co/docs/hub/en/agents-mcp)
- [MCP settings](https://huggingface.co/settings/mcp)
- [HF MCP endpoint](https://huggingface.co/mcp)
- [Spaces as MCP servers (Gradio)](https://www.gradio.app/guides/building-mcp-server-with-gradio)
