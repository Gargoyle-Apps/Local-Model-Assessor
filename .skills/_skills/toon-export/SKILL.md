---
name: toon-export
description: "Encode or validate agent-facing TOON from JSON, YAML, CSV, or emitter output using a JSON hub, the official CLI, and strict decode."
triggers:
  - export TOON
  - validate TOON
  - JSON to TOON
  - write a .toon file
  - TOON emitter
  - token-efficient structured data
dependencies: []
version: "1.1.1"
---

# toon-export

Produce validated **TOON** ([toonformat.dev](https://toonformat.dev)) for agent-consumed structured data. Treat TOON as a generated view; keep YAML, JSON, Markdown, or CSV authoritative when humans edit the source.

Use one format-agnostic path:

```text
source (YAML | JSON | CSV | emitter) -> JSON -> official encoder -> .toon -> strict decode
```

Do not add per-format sibling skills such as `yaml-to-toon` or `csv-to-toon`.

## Hard rules

1. Normalize to a JSON object or array; never hand-author TOON as the source of truth.
2. Encode with `@toon-format/cli` or the bundled wrapper.
3. Strict-decode every generated or edited `.toon` before commit; fail closed.
4. Keep emitter stdout TOON-only; send notes to stderr or a sidecar Markdown file.
5. Reject `#` comment lines. CLI v2.3.x does not decode them reliably.
6. Represent missing values as `null`, never empty cells or em-dash placeholders.
7. Preserve encoder shapes: inline primitive arrays, accurate `[N]` counts, matching table arity, no decorative blank lines, and no unnecessary quoting.

## Workflow

1. Confirm TOON fits: the primary reader is an agent in the same turn and the data is a uniform table or small nested document. Keep human-edited, prose, public-API, or deeply irregular sources in their native format.
2. Normalize the source to JSON:
   - JSON: use directly.
   - YAML: parse it; export only the needed agent slice when comments or deep structure matter.
   - CSV: require a header and explicit schema; map empty cells to `null`. Stop rather than invent ambiguous columns.
   - Emitter: build JSON in the script instead of formatting TOON strings.
3. Encode:

   ```bash
   .skills/_skills/toon-export/scripts/encode-from-json.sh path/to/data.json path/to/out.toon
   # direct equivalent:
   pnpm dlx @toon-format/cli path/to/data.json -o path/to/out.toon
   ```

4. Validate every output:

   ```bash
   .skills/_skills/toon-export/scripts/validate-toon.sh path/to/out.toon
   ```

5. Fix failures at the JSON source and regenerate. Hand-edit only as a last resort; after two failed manual fixes, regenerate.

## Branch references

Load only what the task needs:

- YAML, CSV, or emitter implementation; fit decisions; examples; troubleshooting: [references/adapters-and-emitters.md](references/adapters-and-emitters.md)
- Direct CLI flags, decode commands, encoder shapes, or delimiters: [references/encode-decode.md](references/encode-decode.md)
- Hand edits or validation failures: [references/mistakes-checklist.md](references/mistakes-checklist.md)

## Finish gate

- [ ] Source normalized to JSON, or emitter output strict-decoded
- [ ] Official CLI or bundled encoder used
- [ ] `pnpm dlx @toon-format/cli -d --strict <file>` exits 0
- [ ] No leading `#` lines or em-dash placeholders
- [ ] Primitive arrays are inline
- [ ] Each table count and row arity matches its header
- [ ] Emitter stdout contains TOON only

Consumer repos may wrap this skill with repo-specific paths or exporters through `dependencies:`. Keep the same JSON hub and single-skill model.
