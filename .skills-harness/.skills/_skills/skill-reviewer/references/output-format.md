# Output format

> Load when posting the final review report on the **Output** workflow step.

Post one review comment (PR, MR, or inline in chat). Structure:

```
### skill-reviewer findings

**Summary:** <N> finding(s) — <H> HIGH, <M> MEDIUM, <L> LOW
**Risk tier indicators:** <comma-separated list from the heuristic table, or "none">

#### <relative-path>:<line-or-section>

- [<severity>] <short title>
  Evidence: <quoted snippet>
  Why it matters: <1-2 sentences>
  Recommendation: <concrete fix; cite agentskills.io or harness docs when relevant>
  Caveat: <only when applicable>

(repeat per finding)
```

End with exactly one of:

- `LGTM from skill-reviewer. No blocking concerns.` when no HIGH findings remain.
- `Requesting maintainer review for the HIGH findings above.` when HIGH findings are present and the project requires security sign-off.

When HIGH findings are present in a hosted review tool, request changes rather than approving.
