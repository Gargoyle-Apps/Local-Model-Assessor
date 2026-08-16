# Quality checks (Q1–Q7)

> Load when walking the **Quality** phase. Aligns with [agentskills.io skill creation](https://agentskills.io/skill-creation/best-practices) so reviewers and authors check against the same bar.

## Q1. Description triggering (HIGH when broken, MEDIUM when weak)

The `description` (and harness `triggers`) carry the burden of loading. Apply [optimizing-descriptions](https://agentskills.io/skill-creation/optimizing-descriptions):

| Rule | Check | Severity if violated |
|---|---|---|
| States what + when | Describes user intent and trigger contexts, not internal mechanics only | MEDIUM |
| Harness `triggers` | Phrases match how users ask; not single vague words | MEDIUM |
| Concise, ≤1024 chars | Hard cap on `description` | HIGH if over |

Skills-harness repos also list `triggers` in `.skills/_index.md` — verify overlap between `description` and `triggers` without duplication.

If the user reports false positives or false negatives, recommend a trigger-eval set (~20 queries: 8–10 should-trigger + 8–10 near-miss should-not-trigger). Optionally store cases in `references/<evals>.json`.

## Q2. SKILL.md size and progressive disclosure (MEDIUM)

| Check | Threshold | Severity |
|---|---|---|
| `SKILL.md` line count | > 200 lines, no nested references | MEDIUM |
| `SKILL.md` line count | > 500 lines | MEDIUM (firmer) |
| Reference link without a gate | any | MEDIUM |
| Reference file > 120 lines, no TOC | any | MEDIUM |
| Reference nesting > 1 level deep from SKILL.md | any | MEDIUM |

**Shift-left:** usage context belongs before the file is loaded. A bare `see references/foo.md` without when-to-load context defeats progressive disclosure. Quote the line and propose a gated rewrite.

## Q2b. Scope (MEDIUM if too broad)

Symptoms: description lists 3+ unrelated triggers; parallel unrelated workflows; references organized by unrelated tasks. Recommend splitting into narrower skills with focused descriptions.

## Q3. Eval coverage (MEDIUM if missing)

| Check | Severity |
|---|---|
| New skill with no trigger eval cases | MEDIUM — recommend 2–3 cases |
| Eval set exists but no with-skill vs without-skill run | MEDIUM |
| Cases pass without the skill loaded | MEDIUM — skill may not earn its tokens |

## Q4. Workflow shape (LOW / MEDIUM)

| Check | Severity |
|---|---|
| Wall of prose, no numbered steps | MEDIUM for procedural skills |
| Heavy `ALWAYS` / `NEVER` without rationale | MEDIUM |

## Q5. Frontmatter completeness (LOW / MEDIUM)

Harness skills require: `name`, `description`, `triggers`, `dependencies`, `version`. See checks 1–4 in `references/security-checks.md` for agentskills.io contract.

| Check | Severity |
|---|---|
| Missing harness fields | HIGH in this kit |
| `name` doesn't match parent directory | HIGH |

## Q6. Best-effort / no-ping-pong (LOW)

Recommend skills include: do best-effort work before asking; batch questions into one message.

## Q7. Token-tax awareness (informational)

Estimate happy-path footprint = `SKILL.md` + most likely reference. If > ~3k tokens for the common case, recommend further splintering. Informational, not blocking.
