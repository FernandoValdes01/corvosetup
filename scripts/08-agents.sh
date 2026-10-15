#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install
require_command python

restore_args=(agents)
[[ "$CORVOSETUP_DRY_RUN" == 0 ]] || restore_args+=(--dry-run)
python "$ROOT_DIR/scripts/restore_agents.py" "${restore_args[@]}"

if ! command -v codex >/dev/null 2>&1 || ! command -v opencode >/dev/null 2>&1; then
    require_command npm
    cli_dir="$HOME/.local/share/corvosetup/cli"
    install_user_file "$ROOT_DIR/config/agents/package.json" "$cli_dir/package.json"
    install_user_file "$ROOT_DIR/config/agents/package-lock.json" "$cli_dir/package-lock.json"
    run npm ci --prefix "$cli_dir" --ignore-scripts --no-audit --no-fund
    run node "$cli_dir/node_modules/opencode-ai/postinstall.mjs"
    run mkdir -p "$HOME/.local/bin"
    for client in codex opencode; do
        if ! command -v "$client" >/dev/null 2>&1; then
            backup_file "$HOME/.local/bin/$client"
            run ln -sfn "$cli_dir/node_modules/.bin/$client" "$HOME/.local/bin/$client"
        fi
    done
fi

printf 'Agrega ~/.local/bin al PATH si tu shell aun no lo incluye.\n'
