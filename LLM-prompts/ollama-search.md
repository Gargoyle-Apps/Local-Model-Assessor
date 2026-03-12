# Ollama Popular Models Search & Assessment Pipeline

A guidance document for tool-calling AI agents to discover new Ollama models worth assessing, pre-filter by hardware/software criteria, and add only models that improve the local fleet.

---

## Overview

1. **Fetch** the Ollama popular models page
2. **Parse** entries into structured data (template below)
3. **Pre-filter** using hardware and software profiles (redundant with full assessment, but narrows the funnel)
4. **Prioritize** models that are new-to-DB or newly updated on Ollama since last scan
5. **Filter** Cloud-only models — we want local models only
6. **Cap** at 7 candidate models for full assessment
7. **Compare** candidates to existing DB models — only assess if they "beat" in size, performance, or unmet need
8. **Assess** accepted candidates using `LLM-prompts/model-assessment-prompt.yaml` and insert into DB
9. **Update** last scan timestamp in the database

---

## 1. Data Source

**URL:** `https://ollama.com/search?o=popular`

Default sort is popular. The `o=popular` parameter may not be officially documented but reflects intent. Avoid `o=newest` — too many niche models.

**Fetch:** Use `curl`, `fetch`, or equivalent. The page is client-rendered; expect a mix of HTML and possibly limited structure. Parse what you can from the rendered content.

---

## 2. Entry Structure (Expected)

Use this JSON shape as a template for what to extract from each Ollama listing. Adjust parsing if the page structure differs.

```json
{
  "name": "olmo-3",
  "url": "https://ollama.com/library/olmo-3",
  "description": "Olmo is a series of Open language models designed to enable the science of language models.",
  "categories": ["vision", "tools", "thinking", "cloud"],
  "size_variants": ["7b", "32b"],
  "pulls": "169.7K",
  "tag_count": 15,
  "updated": "2 months ago"
}
```

| Field | Example | Notes |
|-------|---------|-------|
| `name` | `olmo-3` | Model name (from URL or heading) |
| `url` | `https://ollama.com/library/olmo-3` | Link to model page |
| `description` | Text | First sentence(s) before size/pulls |
| `categories` | `["vision","tools","cloud"]` | Capability tags; **exclude if only `cloud`** |
| `size_variants` | `["7b","32b"]` | Parameter sizes |
| `pulls` | `169.7K` | Download count |
| `tag_count` | 15 | Number of tags |
| `updated` | `2 months ago` | Relative timestamp from page |

**Cloud-only:** If `categories` is `["cloud"]` or the only category is `cloud` (no vision/tools/embedding/etc.), skip. We want models that run locally.

---

## 3. Prioritization

**Highest priority:**
- Models at the **top of the popular list** (higher rank = more interest)
- Models **updated on Ollama since last DB scan** (`updated` parsed from page vs. `meta.last_ollama_scan` in DB)
- Models **not yet in the database** (`models.model_id`)

**Query last scan:**
```bash
./scripts/query-db.sh "SELECT value FROM meta WHERE key='last_ollama_scan'"
```

If empty, treat all models as candidates. When `updated` is relative (e.g. "5 days ago", "2 months ago"), use heuristics: "X hours ago" or "X days ago" with X small = recently updated; "X months ago" = older.

---

## 4. Pre-Filter by Profiles

Before full assessment, apply a quick filter using:

- **`computer-profile/hardware-profile.template.yaml`** (or local `hardware-profile.yaml` if present)
  - `vram_budget.total_available` — can this model fit? (rough check from `size_variants`)
  - `hardware_classes` — which class would it fall into?
  - `context_strategy` — any constraints?

- **`computer-profile/software-profile.template.yaml`** (or local `software-profile.yaml`)
  - `model_runtime: Ollama` — we assume Ollama; no change needed for local.

Skip models that clearly exceed VRAM or don't fit your hardware class strategy.

---

## 5. "Beat" Criterion

A candidate **beats** existing models if it improves at least one of:

| Dimension | Beat means |
|-----------|------------|
| **Size** | Larger capable variant (e.g. 32b vs 24b) or fills a missing size tier |
| **Performance** | Higher expected t/s for the same VRAM class |
| **Need** | Fills an unmet role/constraint (e.g. no vision model, no tools model, no embedding) |

**Query current fleet:**
```bash
./scripts/query-db.sh "SELECT model_id, vram, class, tps, vision, tools, reasoning FROM models"
./scripts/query-db.sh "SELECT role, variant, model_id FROM role_model"
./scripts/query-db.sh "SELECT constraint_name, model_id FROM constraint_model"
```

A candidate that doesn't beat any existing model on size, performance, or need should be **skipped**.

---

## 6. Cap and Select

- **Maximum 7** candidate models for full assessment per run.
- If fewer than 7 qualify after prioritization, pre-filter, and beat logic, assess only those.
- If **no models** meet criteria, return a clear explanation (e.g. "All popular models are either Cloud-only, already in DB, or don't beat existing models on size/performance/need").

---

## 7. Full Assessment (Accepted Candidates)

For each accepted candidate, follow **`LLM-prompts/model-assessment-prompt.yaml`**:

1. Read `computer-profile/hardware-profile.yaml` (or template)
2. For each model URL/name, produce YAML output per the prompt. Use `model-data/new-models.template.yaml` as the schema reference; write to `model-data/new-models.yaml` (gitignored).
3. Run:
   ```bash
   python3 scripts/add-model-from-yaml.py model-data/new-models.yaml
   python3 scripts/export-assessed-models.py
   ```

New models get `assessed_at` set automatically when inserted.

---

## 8. Update Last Scan Timestamp

After completing a scan (whether or not any models were added), update the DB:

```bash
./scripts/query-db.sh "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_ollama_scan', datetime('now'))"
```

---

## Summary Checklist

- [ ] Fetch `https://ollama.com/search?o=popular`
- [ ] Parse entries into JSON template (name, url, description, categories, size_variants, pulls, updated)
- [ ] Exclude Cloud-only models (`categories` = only `cloud`)
- [ ] Check `meta.last_ollama_scan` and prioritize new/recently-updated
- [ ] Pre-filter with hardware/software profiles
- [ ] Compare to current fleet — only keep candidates that "beat" on size, performance, or need
- [ ] Cap at 7 candidates
- [ ] If none qualify: return explanation and stop
- [ ] Otherwise: assess each via `LLM-prompts/model-assessment-prompt.yaml`, run `add-model-from-yaml.py`, `export-assessed-models.py`
- [ ] Update `meta.last_ollama_scan` with `datetime('now')`

---

## Database: Last Modified Fields

| Location | Field | Purpose |
|----------|-------|---------|
| `meta` | `key='last_ollama_scan'`, `value=datetime` | When we last scanned the Ollama popular page |
| `models` | `assessed_at` | When this model was assessed/added locally |

Run `./scripts/migrate-schema.sh` if your DB was created before these fields existed.
