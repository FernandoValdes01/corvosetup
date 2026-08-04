#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command findmnt
require_command sed

esp_path=""
for candidate in /boot /efi /boot/efi; do
    if [[ "$(findmnt -no FSTYPE "$candidate" 2>/dev/null || true)" == vfat ]]; then
        esp_path="$candidate"
        break
    fi
done
[[ -n "$esp_path" ]] || { printf 'No se encontro una ESP vfat montada en /boot, /efi o /boot/efi.\n' >&2; exit 1; }
[[ -r /proc/cmdline ]] || { printf 'No se puede leer /proc/cmdline.\n' >&2; exit 1; }
kernel_cmdline="$(< /proc/cmdline)"
[[ -n "$kernel_cmdline" && "$kernel_cmdline" == *root=* ]] || {
    printf 'La linea del kernel no contiene root=; se cancela por seguridad.\n' >&2
    exit 1
}

snapper_configs="$(snapper list-configs 2>/dev/null || true)"
[[ "$snapper_configs" == *root* ]] || {
    printf 'No existe una configuracion Snapper llamada root; se cancela antes de escribir.\n' >&2
    exit 1
}

escaped_cmdline="${kernel_cmdline//\\/\\\\}"
escaped_cmdline="${escaped_cmdline//\"/\\\"}"

temporary="$(mktemp)"
trap 'rm -f -- "$temporary"' EXIT
sed -e "s|@ESP_PATH@|$esp_path|g" -e "s|@KERNEL_CMDLINE@|$escaped_cmdline|g" "$ROOT_DIR/config/limine/default.template" > "$temporary"

install_root_file "$temporary" /etc/default/limine
install_root_file "$ROOT_DIR/config/limine/limine-snapper-sync.conf" /etc/limine-snapper-sync.conf
install_root_file "$ROOT_DIR/config/limine/10-limine-snapper-sync.conf" /etc/mkinitcpio.conf.d/10-limine-snapper-sync.conf

run sudo systemctl enable limine-snapper-sync.service
run sudo limine-update

printf 'Secure Boot no fue modificado. Revisa scripts/secure-boot.sh.\n'
