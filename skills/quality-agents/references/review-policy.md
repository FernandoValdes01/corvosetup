# Strict review policy

Run the strict reviewer for relevant behavior, logic, UI, multi-file, security, data, API, or regression-sensitive changes. It is always `openai/gpt-5.6-luna` with `xhigh`.

Supply the original request, acceptance criteria, actual diff, relevant source, and verification evidence. The reviewer must not rely on the implementer's summary and must not silently fix issues.

Review exact scope, correctness, duplication, overengineering, readability, maintainability, architectural fit, regressions, tests and test validity, security when relevant, and UI/UX/responsiveness/accessibility/visual evidence when relevant.

Require this exact shape:

```text
QUALITY GATE

VERDICT: PASS | FAIL

REQUIREMENTS:
PASS | FAIL

CORRECTNESS:
PASS | FAIL

CODE QUALITY:
PASS | FAIL

REGRESSIONS:
PASS | FAIL

VERIFICATION:
PASS | FAIL

UI/UX:
PASS | FAIL | N/A

BLOCKERS:
...

REQUIRED FIXES:
...

OPTIONAL IMPROVEMENTS:
...
```

`FAIL` only for unmet requirements, correctness risks, regressions, invalid/missing necessary verification, or material quality/security/UI problems. Keep optional polish separate. Pass genuinely good work; avoid destructive perfectionism.
