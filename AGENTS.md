# Project Rules for AI Coding Agents

> **Cursor:** `.cursorrules` → reference this file; `required_permissions: ["all"]` for git if sandbox blocks `.git`.

**Agents:** shell-capable IDEs only — query DB, run scripts; do not ask users to paste data.

**Scope:** Procedural workflows live in **skills** under [`.skills/_skills/`](.skills/_skills/) (index: [`.skills/_index.md`](.skills/_index.md)). This file is the **spine** — non-negotiable conventions, static reference tables, and pointers. [README.md](README.md) = human quick start + tree.

---

## Skills (agnostic / multi-ecosystem)

This repository uses **Path B** from the bundled skills harness: **portable skills** under [`.skills/`](.skills/) (manifest: [`.skills/_index.md`](.skills/_index.md)), **no** tool-specific runtime harness pasted from [`.skills/_harness/*_template.md`](.skills/_harness/) into this tree. Those templates are **reference** for consumers who clone this repo and may run Path A in their own environment.

**Authoring:** Use bundled `skill-template` / `skill-author` and the index when adding skills. Do **not** paste ecosystem harness blocks into this file for this repository.

**Gate:** Do not create, rename, delete skills under `.skills/_skills/`, change `.skills/_index.md`, or load full `SKILL.md` for skill refactors **unless** the user's task explicitly includes that work. Reading `.skills/_index.md` to describe the system is fine.

---

## Non-negotiables

- **Python:** Always run scripts via `./scripts/py scripts/<name>.py …` from the repo root. See `lma-python-env` skill for venv details.
- **DB path:** `LMA_DB` env var overrides the default `model-data/model-assessor.db` for all Python scripts.
- **Queries:** `./scripts/query-db.sh "SQL"` — always pass SQL as a quoted string argument.
- **If DB missing:** `./scripts/init-db.sh`. **If columns/tables missing:** `./scripts/migrate-schema.sh`.

---

## Local vs Tracked Files

| Type | Files |
|------|-------|
| **Tracked** | Templates (`*.template.yaml`), `LLM-prompts/`, scripts, `Brewfile` (optional `libpq` via `brew bundle`), `AGENTS.md`, `.skills/` (portable skills + `_index.md`; `.skills/_harness/` templates are reference-only here), `integrations/IDE-model-management/`, `integrations/embed-retrieval-stack/` (compose + `embed-retrieval-stack.md` + `versions.lock.yaml`) |
| **Gitignored** | `.venv/`, `model-assessor.db`, `hardware-profile.yaml`, `software-profile.yaml`, `assessed-models.md`, `model-data/new-models.yaml`, `model-data/modelfile/*` (except `.gitkeep`), `.cursorrules`, `.continue/`, `.opencode/`, `opencode.json`, local config copies (`integrations/IDE-model-management/*/config.*`, `integrations/IDE-model-management/cline/provider-settings.json`), `integrations/embed-retrieval-stack/out/`, `ref/` |

Create local files from templates: `cp computer-profile/hardware-profile.template.yaml computer-profile/hardware-profile.yaml` (or use setup in `model-assessment-prompt.yaml`). For assessment output: `cp model-data/new-models.template.yaml model-data/new-models.yaml`.

**Repo development vs using the repo:** End-user agents rely on this section matching **`.gitignore`** and the real tree. When you change ignore rules, add generated artifacts, or new local-only paths, update **this table** and **README.md** ("Repo vs Local") together so agents and humans stay aligned.

---

## Hardware Budget

```bash
grep -A5 vram_budget computer-profile/hardware-profile.yaml
```

Effective budget ≈ `total_available - os_headroom_gb`.

**Co-run rule:** `(model_vram + concurrency_reserve) < total_available` → can co-run. Heavy Lifters (30–48 GB) run solo.
