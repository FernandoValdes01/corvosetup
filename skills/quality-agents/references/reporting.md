# Reporting

Finish every relevant run with:

```text
QUALITY AGENTS REPORT

STATUS:
COMPLETED | PARTIAL | BLOCKED

SUMMARY:
...

CHANGES:
- ...

AGENTS USED:
1. <role>
   model: <exact ID>
   reasoning: <variant>
   purpose: ...
   result: ...

QUALITY GATE:
PASS | FAIL | NOT REQUIRED

VERIFICATIONS:
- tests: ...
- lint: ...
- typecheck: ...
- build: ...
- runtime: ...
- visual: ...

FILES CHANGED:
- ...

REUSED EXISTING CODE:
- ...

NEW ABSTRACTIONS:
NONE | ...

KNOWN LIMITATIONS:
- ...

REMAINING ISSUES:
- ...

FINAL RESULT:
...
```

Omit no verification category; use `not run`, `not applicable`, or `not available` honestly. Include tokens/cost only when captured from real OpenCode output.

For an actual blocker, use:

```text
STATUS: BLOCKED

COMPLETED:
...

MISSING:
...

WHY IT BLOCKS COMPLETION:
...

WHAT IS REQUIRED:
...
```
