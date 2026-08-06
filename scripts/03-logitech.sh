#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install
app="$ROOT_DIR/apps/logitech-light-manager"

for file in app.py hardware.py settings.py; do
    install_user_file "$app/$file" "$HOME/.local/lib/logitech-light-manager/$file"
done
install_user_file "$app/logitech-light-manager" "$HOME/.local/bin/logitech-light-manager" 0755
install_user_file "$app/logitech-light-manager.service" "$HOME/.config/systemd/user/logitech-light-manager.service"
install_user_file "$app/logitech-light-manager.desktop" "$HOME/.local/share/applications/logitech-light-manager.desktop"
install_user_file "$app/logitech-light-manager.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/logitech-light-manager.svg"
install_root_file "$app/90-logitech-light-manager.rules" /etc/udev/rules.d/90-logitech-light-manager.rules

if [[ ! -e "$HOME/.config/logitech-light-manager/settings.json" ]]; then
    install_user_file "$app/settings.json" "$HOME/.config/logitech-light-manager/settings.json"
fi

run sudo udevadm control --reload-rules
run sudo udevadm trigger --subsystem-match=hidraw
run systemctl --user daemon-reload
run systemctl --user enable --now logitech-light-manager.service
