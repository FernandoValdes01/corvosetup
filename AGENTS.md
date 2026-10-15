# Working on CorvoSetup

This repository restores public CachyOS configuration and agent tooling. It is not a backup of the user's HOME directory.

- Keep changes grouped by component. Preserve unrelated local edits and create separate commits when requested.
- Never import authentication, environment secrets, OAuth state, databases, sessions, history, attachments or backup files. Use explicit file allowlists when capturing live configuration. Review skill reference files for private project context as well as credentials.
- Store user paths as `@HOME@` in agent/skill templates. The restorer renders them for the destination user. Do not commit machine usernames, trusted project lists, monitor identifiers or disk identities.
- Maintain one skill library in `skills/`. Restore client links through `scripts/restore_agents.py`; do not create three independent copies. Keep legacy `quality-agents` disabled unless the user explicitly changes that policy.
- Every installation module must require `CORVOSETUP_AUTHORIZED` and honor `CORVOSETUP_DRY_RUN`. Test with a temporary HOME. Never run an installer against the real desktop to verify a repository change.
- Preserve existing local credentials while merging public preferences. Reject symlinked destination parents and keep credential-bearing configuration private with mode `0600`.
- Check shell syntax, run `bash tests/static-checks.sh`, and run `bash scripts/check-secrets.sh` before committing. The MCP tests need dependencies from `config/mcp/jflap-requirements.txt` and `PYTHONPATH=apps/jflap-mcp`.
- Before publishing, scan the complete Git history with `bash scripts/check-secrets.sh --history`. Never print matching secret values in reports. Git hooks are versioned in `.githooks`; activate them with `git config core.hooksPath .githooks` on each clone.
- Keep README and the restore, agents and security guides aligned with the actual modules, prerequisites and verified limitations. Separate a successful isolated restore from a full installation on another computer.
