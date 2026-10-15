#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

if [[ "${CORVOSETUP_DRY_RUN:-0}" == 1 ]]; then
    printf '  + install Alacritty, Fish y keybindings en %s/.config y %s/.t3/userdata\n' "$HOME" "$HOME"
    printf '  + fusionar preferencias visuales T3 allowlist en %s/.t3/userdata/client-settings.json\n' "$HOME"
    exit 0
fi

install_user_file "$ROOT_DIR/config/alacritty/alacritty.toml" "$HOME/.config/alacritty/alacritty.toml"
install_user_file "$ROOT_DIR/config/alacritty/themes/noctalia.toml" "$HOME/.config/alacritty/themes/noctalia.toml"
install_user_file "$ROOT_DIR/config/fish/config.fish" "$HOME/.config/fish/config.fish"
install_user_file "$ROOT_DIR/config/t3code/keybindings.json" "$HOME/.t3/userdata/keybindings.json"
install_user_file "$ROOT_DIR/scripts/t3code-notify" "$HOME/.local/bin/t3code-notify" 0755
install_user_file "$ROOT_DIR/scripts/t3code-focus" "$HOME/.local/bin/t3code-focus" 0755
install_user_file "$ROOT_DIR/config/systemd/user/t3code-notify.service" "$HOME/.config/systemd/user/t3code-notify.service"

settings="$HOME/.t3/userdata/client-settings.json"
merged="$(mktemp)"
trap 'rm -f -- "$merged"' EXIT
python3 - "$ROOT_DIR/config/t3code/client-settings.json" "$settings" > "$merged" <<'PY'
import json
import os
import sys

snapshot_path, current_path = sys.argv[1:]
with open(snapshot_path, encoding="utf-8") as stream:
    visual = json.load(stream)
try:
    with open(current_path, encoding="utf-8") as stream:
        current = json.load(stream)
except FileNotFoundError:
    current = {}
if not isinstance(current, dict):
    raise SystemExit(f"Formato JSON inesperado en {current_path}: se esperaba un objeto")
current.update(visual)
json.dump(current, sys.stdout, ensure_ascii=False, indent=2)
sys.stdout.write("\n")
PY
install_user_file "$merged" "$settings" 0600
