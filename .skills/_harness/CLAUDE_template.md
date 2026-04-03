<!-- SETUP — remove this entire section after setup is complete -->

## Setup instructions (Claude Code)

1. Copy the **Skills Harness** section below (from `# Skills Harness` through **Rules**) into a new file at the repository root named `CLAUDE.md`, **or** append to an existing `CLAUDE.md` under a `## Skills Harness` heading.
2. Delete this SETUP block from `CLAUDE.md` when done.
3. **Project `AGENTS.md`:** append a pointer to `CLAUDE.md`. If `AGENTS.md` does not exist, create it with the block below. If `AGENTS.md` already exists, **append** the pointer under a `## Skills Harness` heading — do not erase existing project content.

```markdown
## Skills Harness

Skills: see [CLAUDE.md](./CLAUDE.md).
```

4. Delete **`AGENTS_skills.md`** from the repository root.

**Verify:** `CLAUDE.md` contains the Skills Harness section; `AGENTS.md` has the pointer; this SETUP block is gone; `AGENTS_skills.md` is removed.

<!-- END SETUP -->

---

# Skills Harness

Skills are in `.skills/_skills/`. The index is at `.skills/_index.md`.

## Rules

- Read `.skills/_index.md` at the start of any non-trivial task.
- Load a skill's full `SKILL.md` only when the task matches its triggers in the index.
- Never load skills preemptively.
- If a skill lists `dependencies`, load those skills before proceeding.
- Add new skills to the index when you create them.
- If `.skills/` is missing from the repo, warn the user and do not invent skill content.
- **Temporary bootstrap only:** While `AGENTS_skills.md` exists at the repository root (skills-harness bootstrap not finished), do not create or refactor skills or change `.skills/_index.md` for new skills — complete Path A or B in that file. Once it is removed, this rule does not apply. Path B repos may record ongoing policy in root `AGENTS.md` instead.
