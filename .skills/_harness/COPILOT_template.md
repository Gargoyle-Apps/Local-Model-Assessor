<!-- SETUP — remove this entire section after setup is complete -->

## Setup instructions (GitHub Copilot)

1. Delete this SETUP section (from the opening comment through `<!-- END SETUP -->` inclusive).
2. Install the harness into root **`AGENTS.md`**:
   - **If `AGENTS.md` does not exist:** create it containing only the harness below.
   - **If `AGENTS.md` already exists** with project content: **append** the harness under a new `## Skills Harness` heading. Do not replace existing project instructions.
3. Delete **`AGENTS_skills.md`** from the repository root (the temporary bootstrap file).

**Verify:** `AGENTS.md` contains the Skills Harness section; this SETUP block is gone; `AGENTS_skills.md` is removed.

<!-- END SETUP -->

---

# Skills Harness (Copilot)

Skills are in `.skills/_skills/`. The index is at `.skills/_index.md`.

## Rules

- Read `.skills/_index.md` at the start of any non-trivial task.
- Load a skill's full `SKILL.md` only when the task matches its triggers in the index.
- Never load skills preemptively.
- If a skill lists `dependencies`, load those skills before proceeding.
- Add new skills to the index when you create them.
- If `.skills/` is missing from the repo, warn the user and do not invent skill content.
- **Temporary bootstrap only:** While `AGENTS_skills.md` exists at the repository root (skills-harness bootstrap not finished), do not create or refactor skills or change `.skills/_index.md` for new skills — complete Path A or B in that file. Once it is removed, this rule does not apply. Path B repos may record ongoing policy in root `AGENTS.md` instead.
