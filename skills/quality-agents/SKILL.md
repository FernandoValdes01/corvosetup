---
name: quality-agents
description: Orchestrate cost-aware OpenCode workers for high-quality software implementation, debugging, frontend/UI work, verification, and strict review. Use when Codex should implement or fix software with explicit acceptance criteria, choose the cheapest capable Spark/Luna worker, keep delegated context small, verify real behavior, require an independent quality gate for relevant changes, or report an honest blocked state.
---

# Quality Agents

Act as the Sol orchestrator. Own interpretation, acceptance criteria, routing, integration, correction loops, final verification, and reporting. Never delegate merely to appear multi-agent.

## Workflow

1. Inspect the repository, instructions, working tree, and relevant code before deciding to delegate.
2. Translate the request into concrete acceptance criteria and classify it as `trivial`, `normal`, `complex`, or `very-complex`.
3. Solve locally when delegation costs more than the task. Otherwise select one focused worker; use at most 1–3 concurrent workers, only for independent work.
4. Read [routing.md](references/routing.md), then build a small task contract with only:

   ```text
   ROLE:
   TASK:
   ACCEPTANCE CRITERIA:
   RELEVANT CONTEXT:
   CONSTRAINTS:
   OUTPUT EXPECTED:
   ```

5. Delegate through `scripts/delegate.py`. Never paste the full conversation. Never select Sol for a worker.
6. Inspect the worker's actual changes and outputs. Do not trust its completion claim.
7. Run relevant verification. Read [code-quality.md](references/code-quality.md) for implementation or debugging. For UI, also read [frontend-quality.md](references/frontend-quality.md) and [design-taste.md](references/design-taste.md), then perform real visual inspection when tools permit.
8. For relevant changes, run `scripts/review.py` after verification. Give the reviewer the original request, acceptance criteria, real diff, relevant files, and verification results—not only the implementer's summary. Read [review-policy.md](references/review-policy.md).
9. On `FAIL`, return only `REQUIRED FIXES` to the implementer, re-verify, and review again. Allow at most two automatic correction rounds; then diagnose and escalate to the user.
10. Read [reporting.md](references/reporting.md) and finish with the required report. Never invent usage, cost, runtime, or visual verification.

## Role selection

- `explorer`: locate relevant code and patterns; read-only.
- `implementer`: make the smallest correct scoped change.
- `debugger`: establish root cause, evidence, minimal fix, and verification.
- `ui-engineer`: implement important visual work after learning the existing product language.
- `verifier`: try to falsify correctness with tests and runtime checks; no feature work.
- `strict-reviewer`: independent read-only quality gate; always Luna XHIGH.

Workers must not delegate. The installed OpenCode agents deny `task`. Use `explorer` only when it saves meaningful orchestration context; do not require an exploration hop for obvious changes.

## Commands

Preview routing without inference:

```bash
python3 ~/.codex/skills/quality-agents/scripts/delegate.py \
  --role implementer --difficulty normal --dir "$PWD" --dry-run < contract.txt
```

Run a worker:

```bash
python3 ~/.codex/skills/quality-agents/scripts/delegate.py \
  --role implementer --difficulty normal --dir "$PWD" < contract.txt
```

Run the mandatory gate:

```bash
python3 ~/.codex/skills/quality-agents/scripts/review.py \
  --dir "$PWD" < review-contract.txt
```

If a required dependency or fact cannot be obtained, stop honestly with `STATUS: BLOCKED` using [reporting.md](references/reporting.md).
