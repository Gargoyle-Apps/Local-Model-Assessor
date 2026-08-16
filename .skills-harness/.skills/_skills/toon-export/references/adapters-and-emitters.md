# Adapters and emitters

Read the relevant section when ingest is not already JSON, when building an emitter, or when diagnosing an end-to-end workflow.

## Ingest adapters

Adapters belong inside **toon-export**, not in per-format sibling skills. Prefer an existing repo exporter when it already normalizes data to JSON.

| Source | Path to JSON | Constraints |
|--------|--------------|-------------|
| JSON | Use as-is | Preferred hub; matches the TOON data model |
| YAML | `yq -o=json` or `uv run --with pyyaml` | Parsing drops comments; export only the agent slice when nesting is deep |
| CSV | Header row to an array of objects | Require explicit fields; empty cell becomes `null`; choose a named tabular root when needed |
| Emitter | Build JSON, then call or pipe through the CLI | Do not hand-format TOON strings |

CSV helper:

```bash
.skills/_skills/toon-export/scripts/csv-to-json.sh data.csv /tmp/data.json
.skills/_skills/toon-export/scripts/encode-from-json.sh /tmp/data.json data.toon
```

If the CSV schema, null policy, or root name is unclear, stop and ask rather than inventing columns.

## Emitters

| Requirement | Rule |
|-------------|------|
| Stdout | TOON body only |
| Notes | Write to stderr or `*_notes.md` |
| Counts | `[N]` equals the actual row or element count |
| Delimiter | Default comma; quote cells containing the active delimiter |
| Paths | Inner spaces can remain unquoted |
| Hyphens / pipes | Trailing `-` and pipes are valid inside comma-delimited cells |

Prefer building JSON and passing it to `@toon-format/cli`:

```bash
your-emitter --format toon "$REPO" 2>/tmp/notes.txt \
  | pnpm dlx @toon-format/cli -d --strict -
```

## Fit examples

| Use TOON | Keep the source format |
|----------|------------------------|
| Repo scan or registry tables | Authoring YAML or skills Markdown |
| SQL/CSV result sets | Human dashboards or prose docs |
| Uniform API payloads | Public JSON APIs or deeply irregular JSON |

## Conversion examples

```bash
# JSON hub
.skills/_skills/toon-export/scripts/encode-from-json.sh /tmp/users.json exports/users.toon

# YAML agent slice
yq -o=json config/slice.yaml > /tmp/slice.json
.skills/_skills/toon-export/scripts/encode-from-json.sh /tmp/slice.json /tmp/slice.toon

# CSV
.skills/_skills/toon-export/scripts/csv-to-json.sh exports/rows.csv /tmp/rows.json
.skills/_skills/toon-export/scripts/encode-from-json.sh /tmp/rows.json exports/rows.toon
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Top-level document must start with a key-value…` | Comment or prose precedes the first key | Remove it; start with `key:` or an array header |
| Strict decode fails | Count, quoting, or primitive-array shape is wrong | Regenerate from JSON; load `mistakes-checklist.md` |
| CSV columns are ambiguous | Header missing or rows are ragged | Define the schema before ingest |
| `pnpm dlx` is unavailable | Node/pnpm missing | Install through the repo toolchain or use `npx @toon-format/cli` |
