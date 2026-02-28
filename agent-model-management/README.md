# Agent Model Management

This folder holds **reference configs and instructions** for keeping agent/IDE tools in sync with the models in your **local** model data. When you add, remove, or reclassify models in `model-data/model-assessor.db`, update the corresponding agent configs using the instructions below.

**Prerequisite:** You've run `./scripts/init-db.sh` and created local profiles (`model-assessor.db`, `hardware-profile.yaml`). These are gitignored.

**Optional:** The `ref/` folder (gitignored) is for local copies of agent configs before copying into `.continue/config.yaml`.

**Source of truth (local):** `model-data/model-assessor.db` — SQLite DB. Query directly via `./scripts/query-db.sh`.  
**Hardware context (local):** `computer-profile/hardware-profile.yaml` or `SELECT yaml_content FROM hardware_profile` in the DB.

---

## Overview: Role Mapping

| This repo (model-assessor.db) | Typical agent use |
|-------------------------|-------------------|
| `coding.primary`        | Chat, Edit, Apply (main agent) |
| `vision.primary`        | Chat with image input |
| `reasoning.primary`     | Chat, Edit (logic / no tools) |
| `autocomplete.balanced` | Autocomplete / ghost text |
| `embedding.primary`     | Embed / RAG indexing |

Use `role_model` and `models` tables in `model-assessor.db` to pick the right model names and capabilities.

---

## Continue (VS Code)

**Docs:** [Continue config reference](https://docs.continue.dev/reference)  
**Config file:** `config.yaml` (YAML; replaces legacy `config.json`)  
**Default location:** `~/.continue/config.yaml` — see [continue/config-location.md](continue/config-location.md)

Continue uses a single `config.yaml` with `name`, `version`, `schema`, `models`, `context`, and optional `rules`, `prompts`, `docs`, `mcpServers`, `data`.

### Setup (local reference in this repo)

To keep an untracked local copy of your Continue config in this folder, copy from the default location (see [config-location.md](continue/config-location.md)):

```bash
cp ~/.continue/config.yaml agent-model-management/continue/config.yaml
```

The file is gitignored — it never gets committed. Edit your actual config at `~/.continue/config.yaml`; re-copy here when you want to refresh the local reference.

### Where Continue loads config

- **User-level:** `~/.continue/config.yaml` (default)
- **Project-level:** `.continue/config.yaml` in the project root

### How to update `config.yaml` when models change

1. **Check the source of truth**  
   Query `model-assessor.db` directly:
   - `models` — model_id, ctx, tools, vision, etc.
   - `role_model` — which model for coding, vision, reasoning, autocomplete, embedding.

2. **Map roles to Continue**  
   - **Primary agent (chat + edit + apply):** `SELECT model_id FROM role_model WHERE role='coding' AND variant='primary'` (e.g. `qwen3-coder:30b`).  
     - In Continue: `roles: [chat, edit, apply]`, `capabilities: [tool_use]` if the model supports tools.
   - **Vision:** role='vision', variant='primary' (e.g. `qwen3-vl:8b`).  
     - In Continue: `roles: [chat]`, `capabilities: [image_input]`.
   - **Reasoning (no tools):** role='reasoning', variant='primary' (e.g. `gpt-oss:20b`).  
     - In Continue: `roles: [chat, edit]`, no `capabilities` (or omit tool_use) so the UI doesn’t try to use tools.
   - **Autocomplete:** role='autocomplete', variant='balanced' or 'fastest' (e.g. `granite4:3b`).  
     - In Continue: `roles: [autocomplete]` only.
   - **Embeddings:** role='embedding', variant='primary' (e.g. `embeddinggemma:latest`).  
     - In Continue: `roles: [embed]`.

3. **Set context length**  
   Use the `ctx` value from the `models` table for each model (e.g. 32768, 128000). In Continue this is `contextLength` (or under `defaultCompletionOptions.contextLength` depending on schema).

4. **Optional: edit/apply templates**  
   If a model needs a strict “code only” edit template (e.g. to avoid markdown wrappers), keep a `promptTemplates.edit` (and optionally `apply`) in that model’s block. Your local `config.yaml` in this folder (copied from ~/.continue) may include an example for the primary coding model.

5. **Bump version**  
   Update the top-level `version` in `config.yaml` when you change models or roles (e.g. `1.0.5` → `1.0.6`).

### Quick reference: Continue `models` block

```yaml
models:
  - name: "Display Name"
    provider: ollama
    model: "model-name:tag"   # must match Ollama / model-assessor.db
    roles: [chat, edit, apply]  # or [autocomplete], [embed], etc.
    capabilities: [tool_use]    # and/or image_input if supported
    contextLength: 32768        # from models.ctx
```

Only include `capabilities` that the model has in the DB (tools → tool_use, vision → image_input); omit for reasoning-only models.

### Copying into a project

```bash
# From repo root — use your local config (after copying from ~/.continue) or copy directly
mkdir -p .continue
cp agent-model-management/continue/config.yaml .continue/config.yaml
# Or: cp ~/.continue/config.yaml .continue/config.yaml
```

Then adjust `name`/`version` if desired and ensure the listed Ollama models are installed (`ollama pull <model>:<tag>`).

---

## Adding another app

When you add support for another agent/IDE (e.g. Cursor, Windsurf, another tool):

1. Create a subfolder under `agent-model-management/`, e.g. `agent-model-management/other-app/`.
2. Add a **section in this README** (e.g. `## Other App`) with:
   - Link to the app’s config/docs.
   - Config file name and path (where the app loads it).
   - Step-by-step "How to update" using model-assessor.db and role_model.
   - Any app-specific quirks (e.g. role names, capability flags).
3. Put a reference config file in that subfolder (e.g. `config.yaml` or `settings.json`) so the repo keeps a copy that matches your local fleet.

This keeps all “how to update agent configs” in one place and sectioned by app.
