# TOON mistakes checklist

Use before committing any `.toon` file. Prefer regenerating from JSON over patching by eye.

## Gate 0 — Process

| Check | Fail if |
|-------|---------|
| Source of truth | TOON was invented without a JSON hub (YAML/CSV must normalize first) |
| Toolchain | Did not run `@toon-format/cli -d --strict` successfully |
| Audience | File is meant for humans to edit long-term (use YAML/JSON instead) |
| Skill sprawl | You created a sibling `*-to-toon` skill instead of an adapter step in **toon-export** |

## Gate 1 — CLI-fatal

| Mistake | Symptom | Correct |
|---------|---------|---------|
| `#` comment lines | `Top-level document must start with a key-value or array-header line` | No comments in `.toon`; put notes in `.md` or stderr |
| Leading prose / markdown fences | Same / parse errors | File starts with `key:` or `[N]:` / `[N]{fields}:` |
| Notes mixed into emitter stdout | Downstream decode fails | TOON on stdout only |

## Gate 2 — Shape (encode would not produce this)

| Mistake | Incorrect | Correct |
|---------|-----------|---------|
| Multiline primitive array | `tags[3]:` then one item per indented line | `tags[3]: a,b,c` |
| Em dash / placeholder glyphs | `—,unknown,—` | `null` for missing |
| Wrong `[N]` | `fingerprints[5]` but 6 rows | Count must match |
| Field arity | Row has 4 cells; header has 3 fields | Same column count every row |
| Blank-line "sections" | Extra blank lines between root keys for readability | Match encoder (typically no blanks) |
| Over-quoting | `"1.5.0"` when encoder leaves bare | Prefer encoder output |
| List form when tabular applies | `- id: …` for uniform objects | Prefer `items[N]{id,…}:` rows |

## Gate 3 — Quoting (when hand-editing cells)

Quote a string if it:

- Is empty, or has leading/trailing whitespace
- Equals `true` / `false` / `null`
- Looks like a number (`42`, `1e-6`, `05`)
- Contains `,` (active delimiter), `:`, `"`, `\`, brackets/braces, or control chars
- Equals `-` or starts with `-`
- Equals `#` or starts with `#`

**Usually fine unquoted:** inner spaces, Unicode, trailing hyphens (`ph-`), pipes inside comma-delimited tables (`mm-|mc-|server-`).

## Gate 4 — Round-trip sanity

```bash
pnpm dlx @toon-format/cli -d --strict file.toon -o /tmp/out.json
pnpm dlx @toon-format/cli /tmp/out.json | diff -u file.toon - || true
```

Semantic equality matters more than byte-identical whitespace. If decode→encode drifts wildly, regenerate from the JSON source.

## Automated helper

```bash
.skills/_skills/toon-export/scripts/validate-toon.sh path/to/file.toon
```

Exits non-zero on Gate 1 failures and strict-decode errors; prints Gate 2 heuristics as warnings.
