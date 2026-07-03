# Hugging Face Hub REST API (LMA companion)

**Required companion to HF MCP** for Hub discovery in this repo. MCP alone is **not** sufficient: the agentic `hf_hub_query` tool routinely hangs or times out (`MCP -32001`, 8–10+ minutes) even for bounded collection/count asks. The public Hub REST API returns the same list data in **under a second**.

**Skill:** [`lma-hf-mcp`](../../.skills/_skills/lma-hf-mcp/SKILL.md) · **MCP setup:** [huggingface-mcp.md](huggingface-mcp.md) · **Script:** [`scripts/hf-hub-api.py`](../../scripts/hf-hub-api.py)

---

## Hybrid workflow (mandatory when MCP is connected)

| Step | Layer | Use for |
|------|-------|---------|
| 1 | **REST** (`hf-hub-api.py` or `curl`) | Collection lists/counts, org model indexes, pagination, sort-by-date |
| 2 | **MCP** (`hub_repo_details`, `hub_repo_search`, `hf_doc_search`) | Single-repo README/metadata, targeted model search, HF docs |
| 3 | **Assess** | `lma-assess-import-model` / `lma-hf-gguf-ollama` / `lma-mlx-lm` → `new-models.yaml` |

**Health check:** `hf_whoami` (MCP) — confirms transport + OAuth. **Do not** use `hf_whoami` success as proof that `hf_hub_query` will work.

### Avoid `hf_hub_query` (known gap)

| Status | Detail |
|--------|--------|
| **Do not use** | `hf_hub_query` for collections, counts, bulk lists, or discovery |
| **Symptom** | Multi-minute hangs; client timeout `-32001`; user cancel with no server response |
| **Cause** | HF MCP server-side agentic navigator; explicit `limit` / `scan_limit` / `max_pages` in the message does not reliably cap work |
| **Workaround** | This REST script + selective MCP tools (see table above) |
| **Track** | [HF MCP docs](https://huggingface.co/docs/hub/en/agents-mcp) / HF changelog — re-enable only after verified fast bounded queries |

---

## Script commands

From repo root (stdlib only; no extra pip deps):

```bash
# Reachability (~200ms)
./scripts/py scripts/hf-hub-api.py health

# mlx-community collections — total count + 10 most recently updated
./scripts/py scripts/hf-hub-api.py collections --owner mlx-community --recent 10

# JSON for scout notes / agent parsing
./scripts/py scripts/hf-hub-api.py collections --owner mlx-community --recent 10 --json

# Models by org or search (first page; use MCP hub_repo_details for README)
./scripts/py scripts/hf-hub-api.py models --author mlx-community --limit 20
./scripts/py scripts/hf-hub-api.py models --search "qwen3 gguf Q4_K_M" --limit 10 --json
```

### Raw `curl` equivalents

```bash
# One collection page
curl -sS "https://huggingface.co/api/collections?owner=mlx-community&limit=100"

# Single model metadata (MCP hub_repo_details is richer)
curl -sS "https://huggingface.co/api/models/mlx-community/SomeModel-4bit"
```

Follow `Link: rel="next"` headers to paginate (the script does this automatically).

---

## MCP tools to prefer (when connected)

Enable on [huggingface.co/settings/mcp](https://huggingface.co/settings/mcp). **Allowlist** in Cursor MCP settings to skip per-call approval friction:

| MCP tool | LMA use |
|----------|---------|
| `hf_whoami` | Auth / transport probe |
| `hub_repo_details` | README, license, tags for one repo |
| `hub_repo_search` | Targeted model/dataset search |
| `hf_doc_search` / `hf_doc_fetch` | PEFT, quant, transformers how-to |
| `paper_search` | Optional architecture research |
| ~~`hf_hub_query`~~ | **Avoid** — see gap above |

---

## Scout folder

Write multi-step discovery to `integrations/mcp/scout/` (gitignored). Log **both** REST totals and MCP drill-down notes. See [huggingface-mcp.md](huggingface-mcp.md) § Scout folder.

---

## Troubleshooting

| Symptom | Likely layer | Action |
|---------|--------------|--------|
| `hf_whoami` fast, `hf_hub_query` hangs | `hf_hub_query` gap | Use REST script; do not retry `hf_hub_query` |
| All MCP tools slow after idle | Transport wake + OAuth | Run `hf_whoami` once; expect ~30–50s cold start |
| MCP needs approval every call | Cursor allowlist | Allowlist working tools in Settings → MCP |
| REST `health` fails | Network / HF outage | `WebFetch` model URL or user-supplied repo ID |
| MCP disconnected | Client config | [huggingface-mcp.md](huggingface-mcp.md) setup; workflow continues on REST/`WebFetch` |
