# Agent Model Management

This folder holds **reference configs and instructions** for keeping agent/IDE tools in sync with the models defined in this repo. When you add, remove, or reclassify models in [`model-data/model-lookup.json`](../model-data/model-lookup.json), update the corresponding agent configs using the instructions below.

**Source of truth:** [`model-data/model-lookup.json`](../model-data/model-lookup.json) and [`model-data/assessed-models.md`](../model-data/assessed-models.md).  
**Hardware context:** [`computer-profile/hardware-profile.yaml`](../computer-profile/hardware-profile.yaml).

---

## Overview: Role Mapping

| This repo (model-lookup) | Typical agent use |
|-------------------------|-------------------|
| `coding.primary`        | Chat, Edit, Apply (main agent) |
| `vision.primary`        | Chat with image input |
| `reasoning.primary`     | Chat, Edit (logic / no tools) |
| `autocomplete.balanced` | Autocomplete / ghost text |
| `embedding.primary`     | Embed / RAG indexing |

Use `by_role` and `models` in `model-lookup.json` to pick the right model names and capabilities when editing agent configs.

---

## Continue (VS Code)

**Docs:** [Continue config reference](https://docs.continue.dev/reference)  
**Config file:** `config.yaml` (YAML; replaces legacy `config.json`)  
**Reference copy in this repo:** [continue/config.yaml](continue/config.yaml)

Continue uses a single `config.yaml` with `name`, `version`, `schema`, `models`, `context`, and optional `rules`, `prompts`, `docs`, `mcpServers`, `data`.

### Where Continue loads config

- **Project-level:** `.continue/config.yaml` in the project root (or `config.json` for legacy).
- **User-level:** Continue settings may also define or override models.

Use the project-level file so this repo can version a reference; you can copy from `agent-model-management/continue/config.yaml` into `.continue/config.yaml` in any project where you want this fleet.

### How to update `config.yaml` when models change

1. **Check the source of truth**  
   In `model-data/model-lookup.json`:
   - `models` — `model-name:tag`, `ctx`, capabilities (`tools` → `tool_use`, `vision` → `image_input`).
   - `by_role` — which model to use for coding, vision, reasoning, autocomplete, embedding.

2. **Map roles to Continue**  
   - **Primary agent (chat + edit + apply):** `by_role.coding.primary` (e.g. `qwen3-coder:30b`).  
     - In Continue: `roles: [chat, edit, apply]`, `capabilities: [tool_use]` if the model supports tools.
   - **Vision:** `by_role.vision.primary` (e.g. `qwen3-vl:8b`).  
     - In Continue: `roles: [chat]`, `capabilities: [image_input]`.
   - **Reasoning (no tools):** `by_role.reasoning.primary` (e.g. `gpt-oss:20b` or `deepseek-r1:14b`).  
     - In Continue: `roles: [chat, edit]`, no `capabilities` (or omit tool_use) so the UI doesn’t try to use tools.
   - **Autocomplete:** `by_role.autocomplete.balanced` or `fastest` (e.g. `granite4:3b`, `granite4:350m`).  
     - In Continue: `roles: [autocomplete]` only.
   - **Embeddings:** `by_role.embedding.primary` (e.g. `embeddinggemma:latest` or `qwen3-embedding:0.6b`).  
     - In Continue: `roles: [embed]`.

3. **Set context length**  
   Use the `ctx` value from `model-lookup.json` for each model (e.g. 32768, 128000). In Continue this is `contextLength` (or under `defaultCompletionOptions.contextLength` depending on schema).

4. **Optional: edit/apply templates**  
   If a model needs a strict “code only” edit template (e.g. to avoid markdown wrappers), keep a `promptTemplates.edit` (and optionally `apply`) in that model’s block. The reference [continue/config.yaml](continue/config.yaml) includes an example for the primary coding model.

5. **Bump version**  
   Update the top-level `version` in `config.yaml` when you change models or roles (e.g. `1.0.5` → `1.0.6`).

### Quick reference: Continue `models` block

```yaml
models:
  - name: "Display Name"
    provider: ollama
    model: "model-name:tag"   # must match Ollama / model-lookup.json
    roles: [chat, edit, apply]  # or [autocomplete], [embed], etc.
    capabilities: [tool_use]    # and/or image_input if supported
    contextLength: 32768        # from model-lookup.json "ctx"
```

Only include `capabilities` that the model actually has in `model-lookup.json`; omit for reasoning-only models to avoid tool errors.

### Copying the reference config into a project

```bash
# From repo root
mkdir -p .continue
cp agent-model-management/continue/config.yaml .continue/config.yaml
```

Then adjust `name`/`version` if desired and ensure the listed Ollama models are installed (`ollama pull <model>:<tag>`).

---

## Adding another app

When you add support for another agent/IDE (e.g. Cursor, Windsurf, another tool):

1. Create a subfolder under `agent-model-management/`, e.g. `agent-model-management/other-app/`.
2. Add a **section in this README** (e.g. `## Other App`) with:
   - Link to the app’s config/docs.
   - Config file name and path (where the app loads it).
   - Step-by-step “How to update …” using `model-lookup.json` and `by_role`.
   - Any app-specific quirks (e.g. role names, capability flags).
3. Put a reference config file in that subfolder (e.g. `config.yaml` or `settings.json`) so the repo keeps a copy that matches our fleet.

This keeps all “how to update agent configs” in one place and sectioned by app.
