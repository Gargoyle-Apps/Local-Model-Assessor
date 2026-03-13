# IDE Model Management

This folder holds **setup docs and config references** for keeping IDE agent tools in sync with models in `model-data/model-assessor.db`.

**On-demand:** Configs are generated only when the user asks. Do not proactively create config files. Query the DB and follow the instructions below for the requested app.

**Source of truth:** `model-data/model-assessor.db` (SQLite). Query via `./scripts/query-db.sh`.
**Hardware context:** `computer-profile/hardware-profile.yaml`

---

## Folder Structure

Each supported app has a subfolder here containing:

| File | Tracked? | Purpose |
|------|----------|---------|
| `config-location.md` | Yes | Where the app loads config from, format, locations |
| `.gitkeep` | Yes | Ensures folder exists in repo |
| Config file (e.g. `config.yaml`, `opencode.json`) | No (gitignored) | Local reference copy of filled-out config |

---

## Overview: Role Mapping

| This repo (`role_model`) | Typical agent use |
|--------------------------|-------------------|
| `coding.primary`         | Chat, Edit, Apply (main agent) |
| `vision.primary`         | Chat with image input |
| `reasoning.primary`      | Chat, Edit (logic / no tools) |
| `autocomplete.balanced`  | Autocomplete / ghost text |
| `embedding.primary`      | Embed / RAG indexing |

Query the DB for current assignments:
```bash
./scripts/query-db.sh "SELECT role, variant, model_id FROM role_model"
./scripts/query-db.sh "SELECT model_id, ctx, tools, vision, reasoning FROM models"
```

---

## Supported Apps

| App | Config format | Subfolder |
|-----|--------------|-----------|
| Continue | `config.yaml` | [continue/](continue/) |
| OpenCode | `opencode.json` | [opencode/](opencode/) |
| Goose | `config.yaml` | [goose/](goose/) |
| Pi | `settings.json` + `models.json` | [pi/](pi/) |
| Zed | `settings.json` | [zed/](zed/) |

---

## Continue (VS Code)

**Docs:** [Continue config reference](https://docs.continue.dev/reference)
**Config file:** `config.yaml` — see [continue/config-location.md](continue/config-location.md)
**Default location:** `~/.continue/config.yaml`

### Role mapping → Continue

| DB query | Continue config |
|----------|----------------|
| `role='coding', variant='primary'` | `roles: [chat, edit, apply]`, `capabilities: [tool_use]` |
| `role='vision', variant='primary'` | `roles: [chat]`, `capabilities: [image_input]` |
| `role='reasoning', variant='primary'` | `roles: [chat, edit]` (no capabilities) |
| `role='autocomplete', variant='balanced'` | `roles: [autocomplete]` |
| `role='embedding', variant='primary'` | `roles: [embed]` |

### Config block template

```yaml
models:
  - name: "Display Name"
    provider: ollama
    model: "model-name:tag"   # must match model-assessor.db
    roles: [chat, edit, apply]
    capabilities: [tool_use]  # tool_use and/or image_input; omit if neither
    contextLength: 32768      # from models.ctx
```

### Setup steps (on-demand)

1. Query DB for current role assignments
2. Generate `config.yaml` using the role mapping above
3. Write to `~/.continue/config.yaml` (user-level)
4. Optionally save a copy to `IDE-model-management/continue/config.yaml` as local reference

---

## OpenCode

**Docs:** [OpenCode config reference](https://opencode.ai/docs/config/)
**Config file:** `opencode.json` or `opencode.jsonc` — see [opencode/config-location.md](opencode/config-location.md)
**Default location:** `~/.config/opencode/opencode.json` (global) or `opencode.json` (project root)

### Role mapping → OpenCode

| DB query | OpenCode config |
|----------|----------------|
| `role='coding', variant='primary'` | `model` (main model) |
| `role='coding', variant='quick'` | `small_model` (lightweight tasks) |
| `role='embedding', variant='primary'` | Not directly configured; use via MCP or external |

OpenCode uses `provider` + `model` at the top level. For Ollama:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {}
  },
  "model": "ollama/model-name:tag",
  "small_model": "ollama/small-model:tag"
}
```

### Config block template

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {}
  },
  "model": "ollama/qwen3-coder:30b",
  "small_model": "ollama/granite4:3b",
  "tools": {}
}
```

### Setup steps (on-demand)

1. Query DB for current role assignments
2. Generate `opencode.json` using the role mapping above
3. Write to project root (`opencode.json`) or `~/.config/opencode/opencode.json` (global)
4. Optionally save a copy to `IDE-model-management/opencode/opencode.json` as local reference

---

## Goose (CLI / Desktop)

**Docs:** [Goose — Configure LLM Provider](https://block.github.io/goose/docs/getting-started/providers)
**Config file:** `config.yaml` — see [goose/config-location.md](goose/config-location.md)
**Default location:** `~/.config/goose/config.yaml`

### Role mapping → Goose

| DB query | Goose config |
|----------|-------------|
| `role='coding', variant='primary'` | Main model (via `goose configure` or `GOOSE_MODEL`) |

Goose selects one primary model. It supports lead/worker multi-model configs for advanced use.

### Setup steps (on-demand)

1. Query DB for the primary coding model
2. Run `goose configure` → Configure Providers → Ollama → set `OLLAMA_HOST` → select model
3. Or set env: `export OLLAMA_HOST=http://localhost:11434` and `export GOOSE_MODEL=model:tag`
4. Optionally save a copy to `IDE-model-management/goose/config.yaml` as local reference

---

## Pi (Terminal)

**Docs:** [Pi coding-agent docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/docs)
**Config files:** `settings.json` + `models.json` — see [pi/config-location.md](pi/config-location.md)
**Default location:** `~/.pi/agent/settings.json` (global), `.pi/settings.json` (project)

### Role mapping → Pi

| DB query | Pi config |
|----------|----------|
| `role='coding', variant='primary'` | `defaultModel` in `settings.json` |
| All assessed Ollama models | Listed in `models.json` under `providers.ollama.models` |

Pi supports a single active model but can cycle between configured models with Ctrl+P.

### Config block template — `models.json`

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "model:tag", "name": "Display Name", "contextWindow": 32768 }
      ]
    }
  }
}
```

### Config block template — `settings.json`

```json
{
  "defaultProvider": "ollama",
  "defaultModel": "model:tag",
  "defaultThinkingLevel": "medium"
}
```

### Setup steps (on-demand)

1. Query DB for role assignments and all assessed models
2. Generate `models.json` with Ollama provider and model list (use `ctx` from DB for `contextWindow`)
3. Generate `settings.json` with `defaultProvider: "ollama"` and primary coding model as `defaultModel`
4. Write to `~/.pi/agent/models.json` and `~/.pi/agent/settings.json`
5. Optionally save copies to `IDE-model-management/pi/` as local reference

---

## Zed (Editor)

**Docs:** [Zed AI — LLM Providers](https://zed.dev/docs/ai/llm-providers), [Configuration](https://zed.dev/docs/ai/configuration)
**Config file:** `settings.json` — see [zed/config-location.md](zed/config-location.md)
**Default location:** `~/.config/zed/settings.json` (global) or `.zed/settings.json` (project)

Zed auto-discovers pulled Ollama models, but explicit `available_models` lets you set per-model context length, tool support, vision, and thinking capabilities.

### Role mapping → Zed

| DB query | Zed config |
|----------|-----------|
| `role='coding', variant='primary'` | `assistant.default_model` (main agent model) |
| All assessed Ollama models | Listed in `language_models.ollama.available_models` |

Map DB columns to Zed's per-model fields: `tools` → `supports_tools`, `vision` → `supports_images`, `reasoning` → `supports_thinking`, `ctx` → `max_tokens`.

### Config block template

```json
{
  "language_models": {
    "ollama": {
      "api_url": "http://localhost:11434",
      "available_models": [
        {
          "name": "model:tag",
          "display_name": "Display Name",
          "max_tokens": 32768,
          "supports_tools": true,
          "supports_images": false,
          "supports_thinking": false,
          "keep_alive": "5m"
        }
      ]
    }
  },
  "assistant": {
    "default_model": {
      "provider": "ollama",
      "model": "model:tag"
    },
    "version": "2"
  }
}
```

### Setup steps (on-demand)

1. Query DB for all assessed models and role assignments
2. Generate `language_models.ollama.available_models` array (map `ctx` → `max_tokens`, `tools`/`vision`/`reasoning` → `supports_*`)
3. Set `assistant.default_model` to the primary coding model
4. Merge into `~/.config/zed/settings.json` (global) or `.zed/settings.json` (project)
5. Optionally save a copy to `IDE-model-management/zed/settings.json` as local reference

---

## Adding another app

1. Create `IDE-model-management/<app-name>/` with:
   - `config-location.md` — where the app loads config from
   - `.gitkeep`
2. Add a section in this file with:
   - Link to the app's config docs
   - Role mapping table (DB roles → app config)
   - Config block template
   - On-demand setup steps
3. Add gitignore entries for the app's local config files
4. Do NOT pre-create config files — only generate when the user asks
