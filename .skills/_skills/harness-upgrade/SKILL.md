---
name: harness-upgrade
description: "Upgrade a skills-harness install to the latest version with native IDE discovery."
triggers:
  - upgrade harness
  - update harness
  - migrate harness
  - add native discovery
  - enable IDE symlinks
  - update skills system
dependencies: []
version: "1.2.0"
---

# Harness Upgrade

## When to use this skill

Load when upgrading a repo's skills-harness from an older version (pre-0.4.0) to the current version, or when enabling native IDE skill discovery on an existing installation.

**If the repo has a `.skills-harness/` directory** at the root, the kit is vendored as a git subtree — load **harness-subtree** instead. This skill is for repos installed by file copy.

## Prerequisites

- The repo has `.skills/` with a working harness (Single-Tool or Tool-Neutral setup completed, `AGENTS_skills.md` removed).
- You know which IDE the repo targets (or which cross-agent discovery path to use).

## Upgrade steps

### 1. Check current version

Read `.skills/_meta.yml` and note `kit_version`. If it is already 0.4.0 or later, skip to step 3 (enable native discovery only).

### 2. Update harness files

Copy these from the latest [skills-harness](https://github.com/Gargoyle-Apps/skills-harness) repo into the target repo:

| Source | Destination | Notes |
|--------|-------------|-------|
| `.skills/_harness/link.sh` | `.skills/_harness/link.sh` | New — symlink helper |
| `.skills/_harness/check.sh` | `.skills/_harness/check.sh` | Updated — adds symlink validation |
| `.skills/_harness/*_template.md` | `.skills/_harness/*_template.md` | Updated — SETUP now includes native discovery step |
| `.skills/_meta.yml` | `.skills/_meta.yml` | Merge `kit_version`, `repo_url`, and `native_targets`; preserve consumer fields |

Do **not** replace `.skills/_index.md` or the entire `.skills/_skills/` directory — those contain consumer-owned content. To pick up **new** bundled skills from upstream (e.g. `harness-upgrade`), copy the specific skill directory into `.skills/_skills/` and add its row to `.skills/_index.md`.

### 3. Enable native discovery

Run the link script with the target for your IDE. The helper records the selected path under `native_targets:` in `.skills/_meta.yml`, making native discovery a validated repository intention rather than optional local state:

| IDE | Command |
|-----|---------|
| Cursor, Codex, Copilot, Windsurf, Gemini CLI, Roo Code, OpenCode | `.skills/_harness/link.sh .agents/skills` |
| Claude Code, Cline | `.skills/_harness/link.sh .claude/skills` |

You can run both commands if the repo is used with multiple IDEs — both sets of symlinks coexist safely.

### 4. Update `.gitignore`

Add entries for the symlink directories (they are generated, not committed):

```text
# Native IDE skill discovery (symlinks)
.agents/skills/
.claude/skills/
```

### 5. Verify

Run `.skills/_harness/check.sh --link`. It creates or repairs every declared native target, then validates its complete symlink set. A plain `check.sh` reports a declared-but-missing target as an error.

### 6. Update kit version

Set `kit_version` in `.skills/_meta.yml` to the version you upgraded to.

## Swapping IDEs

If switching from one IDE to another (e.g. Cursor to Claude Code):

1. Follow the new IDE's template in `.skills/_harness/` to install or update harness rules.
2. Run `link.sh` with the new target if it differs from the current one; this adds it to `native_targets`.
3. Both `.agents/skills/` and `.claude/skills/` symlinks can coexist. No need to remove old ones.

Skills stay in `.skills/_skills/` regardless of IDE — the same files, just different ways to discover them.

## What changed in 0.4.0

| Change | Detail |
|--------|--------|
| `link.sh` added | Creates symlinks from `.agents/skills/` or `.claude/skills/` into `.skills/_skills/` for native IDE auto-discovery |
| Templates updated | Each SETUP now includes a "Native discovery" step calling `link.sh` |
| New templates | `ROO_template.md` (Roo Code), `OPENCODE_template.md` (OpenCode) |
| `check.sh` updated | Validates declared native targets; `check.sh --link` creates missing targets and repairs their links; also warns on dependency and context-budget health |
| `skill-author` updated | Reminds authors to re-run `link.sh` after adding skills |
| Frontmatter | `name` + `description` documented as [agentskills.io](https://agentskills.io/specification)-compatible; harness extensions (`triggers`, `dependencies`, `version`) unchanged |

## Notes

- Trigger eval cases: `references/trigger-evals.json` (file-copy upgrade and native discovery vs **harness-subtree** and skill-author near-misses).
