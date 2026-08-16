# Rules

- Prefer the host's native skill catalog. Route from each skill's `name` and `description`, then load the full `SKILL.md` only for a clear match.
- Consult `.skills/_index.md` only when native discovery is unavailable, routing is ambiguous or missing, the host warns that skills were omitted, or the task concerns the catalog itself. Prefer a targeted search before reading the full index.
- Never load skills preemptively.
- After loading a skill, load only its unconditional `dependencies`; load conditional companion skills only when their documented branch is reached.
- **`.skills/_index.md` is the source of truth.** When you create, rename, or delete a skill, update the index in the same operation. Never leave the index out of sync with `.skills/_skills/`.
- If `.skills/` is missing from the repo, warn the user and do not invent skill content.
- **Subtree-vendored installs:** if `.skills-harness/` exists at the repo root, the kit is vendored as a git subtree — treat files under `.skills-harness/` as upstream-owned (do not hand-edit; updates come via `git subtree pull`) and use the **harness-subtree** skill for install/update/reconcile work.
- **Temporary bootstrap only:** While `AGENTS_skills.md` exists at the repository root (skills-harness bootstrap not finished), do not create or refactor skills or change `.skills/_index.md` for new skills — complete the **Single-Tool** or **Tool-Neutral** setup in that file. Once it is removed, this rule does not apply. Tool-Neutral repos may record ongoing policy in root `AGENTS.md` instead.
