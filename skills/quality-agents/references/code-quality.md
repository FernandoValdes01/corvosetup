# Code quality policy

Apply in order:

1. Correctness over cleverness.
2. Existing conventions over invented patterns.
3. Reuse over duplication.
4. Clarity over unnecessary abstraction.
5. Small focused changes over broad rewrites.
6. Verification over assumptions.

Before creating a helper, hook, component, service, utility, type, or abstraction, search for an existing equivalent. Inspect call sites and tests before changing behavior.

Implement the minimum complexity required for a high-quality solution, not the minimum line count. Add an abstraction only when it removes concrete present complexity; state what complexity it removes. Avoid speculative factories, repositories, adapters, providers, managers, and generic layers.

Respect acceptance criteria. Do not add features, unrelated refactors, cosmetic changes, library replacements, or architecture redesigns. Report important out-of-scope problems without modifying them.

For debugging, require: root cause, evidence connecting cause to symptom, minimal scoped fix, and a verification that would fail without the fix. Do not accept a symptom-only patch.
