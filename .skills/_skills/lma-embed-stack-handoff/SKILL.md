---
name: lma-embed-stack-handoff
description: "Generate embed-retrieval-stack handoff artifacts for app repos (Postgres + pgvector + AGE)."
triggers:
  - embed stack
  - pgvector
  - embeddings
  - postgres stack
  - vector database
  - AGE
  - graph database
  - stack handoff
dependencies:
  - lma-db-core
version: "1.0.0"
---

# LMA Embed Stack Handoff

## When to use this skill

Load when the user wants to set up or generate handoff artifacts for the **embed-retrieval stack** (Docker Postgres + pgvector + Apache AGE). Requires at least one assessed **embedding** model in the DB with role assignments.

## Instructions

### 1. Prerequisites

Confirm the DB has an embedding model assigned:

```bash
./scripts/query-db.sh "SELECT model_id FROM role_model WHERE role='embedding'"
```

If no rows, assess and import an embedding model first (see `lma-assess-import-model`).

### 2. Generate handoff artifacts

```bash
./scripts/py scripts/generate-stack-handoff.py [--output-dir DIR]
```

Default output: `integrations/embed-retrieval-stack/out/` (gitignored). Generates:
- `STACK_HANDOFF.md` — setup instructions and model config for the target app repo.
- `embed_sample.py` — sample embedding script.

### 3. Copy to app repo

Copy the stack infrastructure and handoff artifacts into the target application repository:
- `integrations/embed-retrieval-stack/` — Docker Compose, Dockerfile, init scripts, `.env.example`.
- `integrations/embed-retrieval-stack/out/*` — generated handoff files.

### 4. Stack documentation

Full setup, architecture, and upgrade instructions: `integrations/embed-retrieval-stack/embed-retrieval-stack.md`.

### 5. Version alignment

For upgrades (Postgres, pgvector, AGE versions), consult:
- `integrations/embed-retrieval-stack/versions.lock.yaml` — pinned versions.
- `integrations/embed-retrieval-stack/embed-retrieval-stack.md` — upgrade procedures.

## Notes

- The `out/` directory is gitignored — artifacts are generated per-machine.
- The stack uses Docker Compose; Docker must be available on the host.
- The Compose file, Dockerfile, init SQL, and docs are **tracked** (committed). Only the `out/` handoff artifacts are local.
