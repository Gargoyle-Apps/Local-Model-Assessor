# Encode / decode cheatsheet

Package: `@toon-format/cli` · Spec: [toonformat.dev](https://toonformat.dev)

**Hub model:** any structured source → **JSON** → encode → strict-decode.

## Encode JSON → TOON

```bash
pnpm dlx @toon-format/cli data.json -o data.toon
pnpm dlx @toon-format/cli data.json              # stdout
pnpm dlx @toon-format/cli -e --stats data.json   # with token stats
```

Helper:

```bash
.skills/_skills/toon-export/scripts/encode-from-json.sh data.json data.toon
```

## Decode TOON → JSON (strict)

```bash
pnpm dlx @toon-format/cli -d --strict data.toon
pnpm dlx @toon-format/cli -d --strict data.toon -o data.json
```

Always use `--strict` in agent-facing workflows.

## Shapes the encoder chooses

| JSON | TOON |
|------|------|
| Uniform array of objects | `key[N]{f1,f2}:` + CSV rows |
| Array of primitives | `key[N]: a,b,c` (inline) |
| Nested object | Indentation under `key:` |
| Mixed / non-uniform array | List form with `- ` items |
| `null` | bare `null` |

## Delimiters

Default comma. Pipe/tab need explicit header markers (`[N|]`, `[N\t]`). Default: **comma**.

## Comments

Do **not** rely on `#` comments in committed `.toon` files. `@toon-format/cli` 2.3.x fails decode on comment-only first lines. Keep commentary in markdown or stderr.

## Token efficiency tips

- Tab delimiters often beat comma for uniform tables: `--delimiter $'\t'`
- Show TOON in fenced ` ```toon ` blocks when feeding LLMs
- Provide the expected header template when asking models to generate TOON output
