#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command git
require_command patch
require_command niri

skel=/etc/skel/.config/niri
[[ -d "$skel" ]] || { printf 'No existe %s; instala cachyos-niri-noctalia.\n' "$skel" >&2; exit 1; }

temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT
cp -a -- "$skel/." "$temporary/"
patch --silent -d "$temporary" -p1 < "$ROOT_DIR/patches/niri-config.patch"
cp -- "$ROOT_DIR/config/niri/noctalia.kdl" "$temporary/noctalia.kdl"
niri validate -c "$temporary/config.kdl"

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
run cp -a -- "$temporary/." "$HOME/.config/niri/"

cat > "$temporary/niri-display-settings" <<'EOF'
#!/usr/bin/env sh
exec /usr/bin/python "$HOME/.local/src/niri-display-settings/niri-display-settings" "$@"
EOF
install_user_file "$temporary/niri-display-settings" "$HOME/.local/bin/niri-display-settings" 0755
install_user_file "$source_dir/io.github.shorin_kiwata.NiriDisplaySettings.desktop" "$HOME/.local/share/applications/io.github.shorin_kiwata.NiriDisplaySettings.desktop"
install_user_file "$source_dir/icons/niri-display-settings.png" "$HOME/.local/share/icons/hicolor/512x512/apps/niri-display-settings.png"

run niri validate -c "$HOME/.config/niri/config.kdl"
