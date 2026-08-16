---
name: skill-export
description: "Exports a skill to another repository by PR, adding target-only upstream lineage without modifying the source repo."
triggers:
  - export skill
  - publish skill
  - share skill to another repo
dependencies: []
version: "1.0.1"
---

# Skill Export

Publish a skill from this repo into another repository. The **target** receives a portable copy with an `upstream:` block pointing back here for refresh via **skill-import**.

## Hard rule — target only

Export must **never** create, edit, or commit files in **this** repo except reading source skill files to assemble the payload. No index changes, version bumps, or changelog updates on the source skill as part of export.

## When to use

- Share a consumer-authored prefixed skill with another team repo
- Re-publish an updated skill downstream (user names the target)

**Not for:** importing (**skill-import**) or creating new skills (**skill-author**).

## Target lineage block

The exported copy in the **target** repo:

```yaml
upstream:
  repo: <this-repo-owner/name>
  ref: main
  path: .skills/_skills/<skill-name>
  imported: 2026-07-21
  imported-commit: <sha at export time>
```

No reciprocal metadata is written on the source skill in this repo.

## Steps

1. **Pick skills and target** — which skill(s), target `owner/repo`, and destination path (usually `.skills/_skills/<name>/` or the target's documented skills root).

2. **Confirm with user** — restate target repo, branch name, and skill list; wait for explicit approval before creating a branch or PR.

3. **Assemble payload** — copy `SKILL.md`, `scripts/`, `references/`, `assets/`. Strip harness-only wiring (index rows, `.skills/_harness` references). Add `upstream:` on the target copy.

4. **Land via PR** — create a branch on the target and open a pull request. Never direct-push to the target's default branch without project policy allowing it.

5. **Stop** — export completes when the target PR is open (or the user asked for a local copy only). Do not modify this repo.

Optional trigger evals: `references/trigger-evals.json`.

## Re-publishing

Re-run export: newer payload from source paths, refresh target `upstream:` dates/commits, open a fresh PR on the target. Still no writes here.

## What not to do

- Don't modify this repo during or after export
- Don't export harness-internal paths without stripping kit-specific references
- Don't echo or commit credentials used to push to the target
