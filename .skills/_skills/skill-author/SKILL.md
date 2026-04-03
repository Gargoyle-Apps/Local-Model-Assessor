---
name: skill-author
description: "How to write a new SKILL.md from scratch and register it in the index."
triggers:
  - write a skill
  - author a skill
  - new skill
  - add a skill
dependencies:
  - skill-template
version: "1.0.1"
---

# Skill Author

## Prerequisites

Follow root **`AGENTS.md`** — **Skills (agnostic / multi-ecosystem)** for Path B policy and any project-specific gate (this repo records policy there after bootstrap).

Load `skill-template` first if you need the canonical layout and refactor notes.

## Steps

1. Create directory: `.skills/_skills/<name>/`
2. Copy `.skills/_skills/skill-template/SKILL.md` as your starting point
3. Fill in frontmatter — `name` must match directory name exactly
4. Write the body as agent-facing instructions, not human documentation
5. Choose triggers carefully — these are what cause the skill to be loaded
6. Add a row to `.skills/_index.md`
7. If this skill depends on another, list it in `dependencies`

## Frontmatter checklist

- [ ] `name` matches directory name
- [ ] `description` is one sentence, suitable for an index
- [ ] `triggers` covers the natural language phrases that should invoke this skill
- [ ] `dependencies` is present (empty list `[]` if none)
- [ ] `version` is set

## Body structure

Use these sections as needed — not all are required:

- **When to use this skill** — conditions for loading
- **Instructions** — step-by-step agent directions
- **Examples** — concrete usage examples
- **Notes** — edge cases, caveats, or references

## What makes a good trigger

Triggers should match how a user would naturally ask for the task, not internal
jargon. Prefer phrases over single words. Think about what someone would type
before they knew this skill existed.

## Circular dependencies

Avoid cycles in `dependencies`. If you detect a cycle, load skills in alphabetical order by `name` and stop after one full pass — then tell the user to fix the dependency graph.
