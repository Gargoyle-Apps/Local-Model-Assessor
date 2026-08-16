# Plugin-primitive checks (P1–P8)

> Load when the change touches plugin surfaces beyond skills: hook configs, MCP server definitions, subagent files, or IDE plugin manifests. **Skip this file** when the diff only changes `.skills/_skills/<name>/` content.

## When to apply

| Surface | Examples |
|---|---|
| Hooks | `hooks/hooks.json`, hook scripts referenced from manifests |
| MCP | MCP server config JSON, server references in manifests |
| Subagents | Subagent definition files with tool grants |
| Plugin manifests | `.claude-plugin/plugin.json`, `.cursor-plugin/`, team bundle manifests |

If the repo has no plugin layout, note "plugin checks skipped" and continue with quality + security checks only.

## Primitive risk summary

| Primitive | Default stance |
|---|---|
| Skills under `.skills/_skills/` | Q1–Q7 + security 1–23 |
| Hooks | HIGH — unsandboxed shell on session events without user action |
| MCP server definitions | HIGH — network and credential surface |
| Subagents with broad tool grants | HIGH — delegated execution |
| Channels / monitors (if present) | HIGH — external events without user invocation |

## TOC

| # | Check | Default severity |
|---|---|---|
| P1 | Plugin manifest integrity | HIGH when malformed |
| P2 | Generated catalog hand-edits | HIGH when generator exists |
| P3 | Skill migration into plugin folders | HIGH — full re-review |
| P4 | Disallowed primitives per repo policy | HIGH |
| P5 | Channels and monitors | HIGH if repo forbids them |
| P6 | Subagents | per sub-check |
| P7 | MCP server references | per sub-check |
| P8 | Hooks | HIGH by default |

## P1. Plugin manifest

Generic pattern: a JSON manifest at the plugin root declares identity (`name`, `version` or commit-based versioning per project docs) and optional primitives (hooks, MCP servers, subagents). **HIGH** when malformed.
- **HIGH** on silent `name` renames without migration notes (orphans installed copies).
- **HIGH** when manifest declares hooks, MCP servers, or subagents the repo policy has not approved — route to P4–P8.

## P2. Generated catalogs

When the repo documents a generator for a marketplace/catalog file, **HIGH** when an MR hand-edits the generated output without updating sources. Point authors at the generator script.

## P3. Plugin folder migrations

Moving a skill into an installable plugin folder is elevated scrutiny: re-run Q1–Q7 and checks 1–23 on the **entire** skill body, not just the diff.

## P4. Repo policy gate

If CONTRIBUTING or AGENTS.md forbids certain primitives, any introduction **blocks** until policy is updated deliberately.

## P5. Channels and monitors

If repo policy disallows always-on external listeners, grep the diff for channel/monitor declarations. Any match: **HIGH**, block.

## P6. Subagents

Treat subagent prompt files like `SKILL.md` bodies — apply checks 6, 7, 15, 18, 20. Tool grants follow check 5 logic.

## P7. MCP server references

- Prefer internal or documented hosts. **HIGH** for unexpected external hosts, plain HTTP, or inline credentials.
- **HIGH** for loopback endpoints in shared plugins (`localhost`, `127.0.0.1`) — resolves against the installer's machine, not the author's.

## P8. Hooks

Apply checks 8, 15, 16, 19 to every hook command, defaulting to **HIGH**. Commands should resolve inside the plugin directory; remote fetch at fire time is **HIGH**.
