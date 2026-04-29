---
name: lma-model-prune
description: "Supersede an older model with a newer generation, remove it from Ollama, and clean up clones."
triggers:
  - prune model
  - supersede model
  - replace model
  - remove old model
  - retire model
  - model cleanup
  - drop model
dependencies:
  - lma-db-core
version: "1.0.0"
---

# LMA Model Prune

## When to use this skill

Load when a newer dot release or major release of a model family makes an older entry redundant. The older model stays in the DB for history (marked `superseded_by`) but is removed from Ollama and excluded from selection, export, and IDE config generation.

## Concepts

- **`models.superseded_by`** — stores the `model_id` of the replacement. `NULL` = active; non-NULL = superseded.
- Superseded models are excluded from `export-assessed-models.py` output, from role selection queries, and from `generate-ide-config.py` when `--active-only` is used.
- The row is never deleted — provenance, assessment history, and class/role data are preserved.

## Change-management rules (mandatory)

Every direct SQL write here must update the provenance trio on each touched row:

- `updated_at` → current UTC timestamp (`%Y-%m-%d %H:%M:%S`).
- `updated_by` → assessor name (CLI: model id or person; default `human` if unattributed).
- `updated_by_type` → one of `local` | `cloud` | `human`.

Set them as session vars at the top of each prune run:

```bash
DB=model-data/model-assessor.db
NOW=$(date -u +"%Y-%m-%d %H:%M:%S")
BY="human"            # or the model id that decided the prune
BYT="human"           # human | local | cloud
```

Then include them in every `UPDATE`. Example:

```sql
UPDATE models SET superseded_by='<new>', updated_at='$NOW', updated_by='$BY', updated_by_type='$BYT'
  WHERE model_id='<old>';
```

`created_at` / `created_by` / `created_by_type` are write-once — never overwrite them.

## Instructions

### 1. Identify the pair

Confirm the **old** model and the **new** model that replaces it. They should overlap on:
- Similar parameter count / VRAM footprint.
- Same or superset of capabilities (vision, tools, reasoning).
- Same family lineage or direct successor on the upstream card.

```bash
./scripts/query-db.sh "SELECT model_id, vram, class, vision, tools, reasoning FROM models WHERE superseded_by IS NULL ORDER BY model_id"
```

### 2. Mark superseded

```bash
sqlite3 "$DB" "UPDATE models SET superseded_by='<new_model_id>',
  updated_at='$NOW', updated_by='$BY', updated_by_type='$BYT'
  WHERE model_id='<old_model_id>'"
```

Verify:

```bash
./scripts/query-db.sh "SELECT model_id, superseded_by FROM models WHERE superseded_by IS NOT NULL"
```

### 3. Deactivate and remove provisioned clones

List clones for the old base:

```bash
./scripts/query-db.sh "SELECT alias, role, variant FROM provisioned_models WHERE base_model_id='<old_model_id>'"
```

Remove each clone from Ollama and mark inactive in the DB:

```bash
ollama rm <alias>
sqlite3 "$DB" "UPDATE provisioned_models SET is_active=0,
  updated_at='$NOW', updated_by='$BY', updated_by_type='$BYT'
  WHERE base_model_id='<old_model_id>'"
```

### 4. Clean up role and constraint assignments

If the new model is **not** already assigned to the role the old one held, **reassign first** (don't lose the slot):

```bash
sqlite3 "$DB" "UPDATE role_model SET model_id='<new_model_id>',
  updated_at='$NOW', updated_by='$BY', updated_by_type='$BYT'
  WHERE role='<role>' AND variant='<variant>' AND model_id='<old_model_id>'"
```

If the new model is **already** assigned to the same `(role, variant)` (PK conflict), use `UPDATE` on the existing row instead and `DELETE` the redundant variant pointing at the old model. Then drop any leftover rows for the old model:

```bash
sqlite3 "$DB" "DELETE FROM role_model WHERE model_id='<old_model_id>'"
sqlite3 "$DB" "DELETE FROM constraint_model WHERE model_id='<old_model_id>'"
```

`role_model` PK is `(role, variant)`. If you need to demote (not delete) the old model to a different variant, `INSERT` the new variant row first, then `UPDATE` the original.

### 5. Remove the base model from Ollama

```bash
ollama rm <old_model_id>
```

### 6. Remove stale Modelfiles

Delete `.mf` files for superseded clones from `model-data/modelfile/`:

```bash
rm model-data/modelfile/<old-alias-pattern>*.mf
```

### 7. Regenerate exports

```bash
./scripts/py scripts/export-assessed-models.py
```

The export now prints a summary line listing superseded models that were excluded.

## Checklist

- [ ] Old model confirmed as redundant (same size class, capabilities covered by successor).
- [ ] `models.superseded_by` set to the replacement `model_id`.
- [ ] Provisioned clones deactivated (`is_active=0`) and removed from Ollama.
- [ ] `role_model` / `constraint_model` rows cleaned or reassigned.
- [ ] `ollama rm` run for the base model tag.
- [ ] Stale `.mf` files deleted from `model-data/modelfile/`.
- [ ] `assessed-models.md` regenerated; superseded models excluded.

## Querying superseded history

```bash
./scripts/query-db.sh "SELECT model_id, class, vram, superseded_by, updated_at, updated_by FROM models WHERE superseded_by IS NOT NULL ORDER BY updated_at"
```

## Notes

- Never `DELETE FROM models` — always use `superseded_by` to preserve history.
- If a superseded model needs to come back (e.g. successor regresses), clear the column: `UPDATE models SET superseded_by=NULL, updated_at='$NOW', updated_by='$BY', updated_by_type='$BYT' WHERE model_id='...'`.
- `provisioned_models` rows for superseded bases are kept (with `is_active=0`) for audit; they will not appear in active config generation.
- Pure role reassignments (no supersede) follow the same provenance rules — every `UPDATE role_model` / `INSERT role_model` must stamp `updated_at/by/by_type`.
