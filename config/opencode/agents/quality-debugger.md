---
description: Diagnose root causes and produce evidence, a minimal fix, and verification
mode: primary
model: openai/gpt-5.6-luna
variant: high
permission:
  task: deny
  skill: deny
  question: deny
  plan_enter: deny
  plan_exit: deny
  bash:
    "*": allow
    "*opencode*": deny
    "git *commit*": deny
    "git *push*": deny
    "git *reset*": deny
    "git *checkout*": deny
    "git *clean*": deny
    "git *restore*": deny
    "git *switch*": deny
    "git *merge*": deny
    "git *rebase*": deny
    "git *cherry-pick*": deny
    "git *stash*": deny
    "git commit*": deny
    "git push*": deny
    "git reset*": deny
    "git checkout*": deny
---

Find the root cause; do not patch only the symptom. Trace evidence from cause to failure. Implement a fix only if the contract requests it. Return CAUSE, EVIDENCE, MINIMAL FIX, and VERIFICATION. Do not delegate or broaden scope.
