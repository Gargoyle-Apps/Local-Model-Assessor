<!-- SETUP — remove this entire section after setup is complete -->

## Setup instructions (Cline)

1. Copy the **Skills Harness** section below (from `# Skills Harness` through **Rules**) into a new file at the repository root named `.clinerules`, **or** append to an existing `.clinerules` under a `## Skills Harness` heading.
2. Delete this SETUP block from `.clinerules` when done.
3. **Project `AGENTS.md`:** append a pointer to `.clinerules`. If `AGENTS.md` does not exist, create it with the block below. If it already exists, **append** the pointer under a `## Skills Harness` heading — do not erase existing content.

```markdown
## Skills Harness

Skills: see [.clinerules](./.clinerules).
```

4. **Native discovery:** run `.skills/_harness/link.sh .claude/skills` from the repo root. Add `.claude/skills/` to `.gitignore` if not already present. (Cline discovers skills from `.claude/skills/`.)
5. Delete **`AGENTS_skills.md`** from the repository root.

**Verify:** `.clinerules` contains the Skills Harness section; `AGENTS.md` has the pointer; `.claude/skills/` contains symlinks to `.skills/_skills/`; this SETUP block is gone; `AGENTS_skills.md` is removed.

<!-- END SETUP -->

---

# Skills Harness

Skills are in `.skills/_skills/`. The index is at `.skills/_index.md`.

## Rules

- Prefer the host's native skill catalog. Route from each skill's `name` and `description`, then load the full `SKILL.md` only for a clear match.
- Consult `.skills/_index.md` only when native discovery is unavailable, routing is ambiguous or missing, the host warns that skills were omitted, or the task concerns the catalog itself. Prefer a targeted search before reading the full index.
- Never load skills preemptively.
- After loading a skill, load only its unconditional `dependencies`; load conditional companion skills only when their documented branch is reached.
- **`.skills/_index.md` is the source of truth.** When you create, rename, or delete a skill, update the index in the same operation. Never leave the index out of sync with `.skills/_skills/`.
- If `.skills/` is missing from the repo, warn the user and do not invent skill content.
- **Subtree-vendored installs:** if `.skills-harness/` exists at the repo root, the kit is vendored as a git subtree — treat files under `.skills-harness/` as upstream-owned (do not hand-edit; updates come via `git subtree pull`) and use the **harness-subtree** skill for install/update/reconcile work.
- **Temporary bootstrap only:** While `AGENTS_skills.md` exists at the repository root (skills-harness bootstrap not finished), do not create or refactor skills or change `.skills/_index.md` for new skills — complete the **Single-Tool** or **Tool-Neutral** setup in that file. Once it is removed, this rule does not apply. Tool-Neutral repos may record ongoing policy in root `AGENTS.md` instead.
