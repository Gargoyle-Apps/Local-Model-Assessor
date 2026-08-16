---
name: skill-template
description: "Documents the canonical SKILL.md layout and refactor guide for converting rules or docs into skills. Load when the user needs format guidance, reformatting, or conversion — not when authoring a new skill from scratch."
triggers:
  - skill format
  - reformat skill
  - convert rule
  - skill layout
  - refactor to skill
dependencies: []
version: "1.3.1"
---

# Skill Template

Use this as a starting point for any new skill.
Copy this file to `.skills/_skills/<your-skill-name>/SKILL.md` and fill it in.
Pair with **skill-author** for registration, index sync, and review.

## When to use this skill

Load when the user needs the canonical skill layout, is creating a new skill, or is converting an existing rule or doc into the standard format.

## Skill directory layout

Every skill is a directory. `SKILL.md` is required; optional subfolders follow the [agentskills.io specification](https://agentskills.io/specification) for bundled resources (Level 3 — loaded only when referenced). Cursor and other IDEs may document the same layout ([Cursor skills docs](https://cursor.com/docs/skills) — optional).

```text
.skills/_skills/<name>/
├── SKILL.md          ← required: frontmatter + agent instructions
├── scripts/          ← optional: executable helpers the agent runs via shell
├── references/       ← optional: extra markdown/docs loaded on demand
└── assets/           ← optional: templates, schemas, images, data files
```

**Progressive disclosure:** keep `SKILL.md` focused. Move long reference material to `references/`, deterministic steps to `scripts/`, and static files to `assets/`. Reference them from `SKILL.md` with relative paths (e.g. `scripts/<name>.sh`, `references/<name>.md`). The agent (and native IDE discovery) loads these only when the task needs them — not at trigger time.

Do **not** place scripts or extra markdown loose at the skill root; `check.sh` warns on that layout.

## Instructions

1. Copy this file to `.skills/_skills/<name>/SKILL.md`.
2. Set `name` to match the directory name exactly — kebab-case, 1–64 characters, lowercase alphanumeric and hyphens only, no leading/trailing/consecutive hyphens ([agentskills.io](https://agentskills.io/specification) `name` rules).
3. Write `description` as one sentence, 1–1024 characters — used by the harness index and native IDE skill matching ([agentskills.io](https://agentskills.io/specification) `description` rules).
4. List natural-language `triggers` users might say.
5. Put only unconditional runtime companions in `dependencies`; load branch-specific companions from the body step that needs them.
6. Fill **When to use**, **Instructions**, and **Examples** for the agent.
7. If the skill needs bundled files, add `scripts/`, `references/`, and/or `assets/` and link to them from `SKILL.md` with relative paths. Optional trigger evals: `references/trigger-evals.json`.

## Body scaffolds (copy into your skill)

Use these sections as needed — delete unused headings rather than leaving them empty:

```markdown
## When to use this skill

- Concrete trigger one.
- Concrete trigger two.

## Prerequisites

Skip if none.

## Instructions

1. First step.
2. Verification step.

## Examples

**Scenario name** — input / expected outcome.

## Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
|         |              |     |

## What not to do

- Scope foot-gun specific to this skill.
```

## Examples

- "Add a skill for our deploy checklist" → use this template, then register via **skill-author** (`build-index.sh --write`).
- "Skill with a validation script" → put `scripts/<name>.sh` in the skill dir and tell the agent to run it from **Instructions**.

---

<!--
REFACTOR GUIDE

Use this section when converting an existing file (Cursor rule, plain markdown
instructions, AGENTS.md section, etc.) into a standard SKILL.md.

Steps:
1. Identify the core capability the existing file describes
2. Extract it into a new directory: .skills/_skills/<name>/SKILL.md
3. Add YAML frontmatter (name, description, triggers, dependencies, version)
4. Rewrite the body as agent-facing instructions (not human docs)
5. Run .skills/_harness/build-index.sh --write to regenerate .skills/_index.md
6. Remove or replace the original content with a one-liner pointing to the skill

Common sources to refactor:
- Cursor .mdc rules → extract procedural ones as skills, keep declarative ones as rules
- AGENTS.md sections → any multi-step workflow becomes a skill
- Inline comments or README instructions → if an agent needs to follow them, they're a skill

What stays in AGENTS.md / harness files (not skills):
- Project-level conventions (naming, structure)
- Always-on constraints
- Pointers to the index

What becomes a skill:
- Any multi-step workflow
- Domain-specific knowledge (how to use a particular tool or API)
- Anything the agent should only load when relevant
-->
