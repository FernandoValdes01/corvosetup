#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

packages=(
    git patch cachyos-niri-noctalia niri noctalia python tk hidapi gtk4 libadwaita python-gobject
    grim slurp satty wl-clipboard
    jq curl coreutils nodejs npm python-pip fish cachyos-fish-config fastfetch alacritty gitleaks sqlite libnotify limine limine-mkinitcpio-hook
    limine-snapper-sync snapper sbctl
)

run sudo pacman -S --needed "${packages[@]}"
