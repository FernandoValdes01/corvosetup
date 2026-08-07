#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command curl
require_command sha256sum

temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT
install_user_file "$ROOT_DIR/config/noctalia/config.toml" "$HOME/.config/noctalia/config.toml"
install_user_file "$ROOT_DIR/config/noctalia/scripts/codex-usage.sh" "$HOME/.config/noctalia/scripts/codex-usage.sh" 0755
install_user_file "$ROOT_DIR/config/noctalia/plugins/corvo-codex-usage/plugin.toml" "$HOME/.local/share/noctalia/plugins/corvo-codex-usage/plugin.toml"
install_user_file "$ROOT_DIR/config/noctalia/plugins/corvo-codex-usage/codex.luau" "$HOME/.local/share/noctalia/plugins/corvo-codex-usage/codex.luau"
run mkdir -p -- "$HOME/Pictures/corvosetup-wallpapers"

font_url=https://github.com/IdreesInc/Monocraft/releases/download/v4.2.1/Monocraft.ttc
font_sha=0ea1aea12f03d552a469fc017f19ea927b53bf9d21e60a41c5c476c3faf3c7f9
if [[ ! -e "$HOME/.local/share/fonts/Monocraft.ttc" ]]; then
    run curl -fL --retry 3 -o "$temporary/Monocraft.ttc" "$font_url"
    if [[ "$CORVOSETUP_DRY_RUN" == 0 ]]; then
        printf '%s  %s\n' "$font_sha" "$temporary/Monocraft.ttc" | sha256sum -c -
    fi
    install_user_file "$temporary/Monocraft.ttc" "$HOME/.local/share/fonts/Monocraft.ttc"
    run fc-cache -f
fi

if command -v noctalia >/dev/null 2>&1; then
    run noctalia msg config-reload
fi
