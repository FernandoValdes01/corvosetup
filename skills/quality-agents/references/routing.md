# Routing and delegation

## Decision table

| Difficulty | Model | Variant | Typical work |
|---|---|---|---|
| `trivial` | `opencode/muse-spark-1.2-contributor-free` | `xhigh` | Mechanical, tiny, explicit changes or searches |
| `normal` | `openai/gpt-5.6-luna` | `medium` | Ordinary implementation with bounded reasoning |
| `complex` | `openai/gpt-5.6-luna` | `high` | Multiple related modules, important logic, substantial UI, nontrivial debugging |
| `very-complex` | `openai/gpt-5.6-luna` | `xhigh` | Architecture, ambiguous cross-system behavior, difficult regressions |
| final review | `openai/gpt-5.6-luna` | `xhigh` | Every relevant change |

These IDs were resolved from `opencode models --refresh --verbose`. Change them only in `routing.json`, then run the tests.

## Delegate only when useful

Do not delegate a trivial task if Sol can finish it faster with equal confidence. Delegate when a focused worker reduces expensive Sol implementation time, isolates a specialty, or supplies independent verification.

Classify by the hardest acceptance criterion, not file count alone. Raise difficulty when requirements are ambiguous, failures cross boundaries, security is material, or mistakes are costly. Lower it when the change is mechanical and fully specified.

Run workers concurrently only when they do not edit or reason about the same surface. Prefer 1–3 useful workers. Never create worker chains.

## Contract discipline

Include exact acceptance criteria, relevant paths/symbols already known, project constraints, and the expected response. Omit global policies already present in the selected role. Let the worker inspect nearby files. Do not include other roles' instructions.

The bridge always passes `--agent`, `--model`, and `--variant`; therefore workers never inherit the orchestrator model.

OpenCode declares these CLI-invocable workers as `mode: primary` because `opencode run --agent` rejects `mode: subagent` and falls back to its default agent. They remain leaf workers: every role denies `task`, planning transitions, questions, and skill loading.

The bridge marks worker processes with `QUALITY_AGENTS_LEAF=1` and refuses nested bridge calls. Agents with Bash also deny commands matching `*opencode*` and common mutating Git operations. These controls reinforce the short role instruction; they do not claim to be an OS sandbox.
