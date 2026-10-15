#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command git
require_command niri

snapshot="$ROOT_DIR/config/niri"
niri validate -c "$snapshot/config.kdl"

source_dir="$HOME/.local/src/niri-display-settings"
if [[ ! -d "$source_dir/.git" ]]; then
    run git clone https://github.com/SHORiN-KiWATA/niri-display-settings.git "$source_dir"
fi
run git -C "$source_dir" fetch --tags origin
run git -C "$source_dir" checkout --detach 63908ce59632524e0f4545cf3c719c3b2a6b118a
if ! git -C "$source_dir" apply --reverse --check "$ROOT_DIR/patches/niri-display-settings-spanish.patch" >/dev/null 2>&1; then
    run git -C "$source_dir" apply "$ROOT_DIR/patches/niri-display-settings-spanish.patch"
fi

backup_file "$HOME/.config/niri"
run mkdir -p -- "$HOME/.config/niri"
for file in "$snapshot"/*.kdl "$snapshot"/cfg/*.kdl; do
    relative="${file#"$snapshot/"}"
    destination="$HOME/.config/niri/$relative"
    [[ "$relative" != cfg/display.kdl || ! -e "$destination" ]] || continue
    install_user_file "$file" "$destination"
done

install_user_file <(printf '%s\n' \
    '#!/usr/bin/env sh' \
    'exec /usr/bin/python "$HOME/.local/src/niri-display-settings/niri-display-settings" "$@"') \
    "$HOME/.local/bin/niri-display-settings" 0755
install_user_file "$ROOT_DIR/scripts/screenshot.sh" "$HOME/.local/bin/corvosetup-screenshot" 0755
install_user_file "$source_dir/io.github.shorin_kiwata.NiriDisplaySettings.desktop" "$HOME/.local/share/applications/io.github.shorin_kiwata.NiriDisplaySettings.desktop"
install_user_file "$source_dir/icons/niri-display-settings.png" "$HOME/.local/share/icons/hicolor/512x512/apps/niri-display-settings.png"

run niri validate -c "$HOME/.config/niri/config.kdl"
