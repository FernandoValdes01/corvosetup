#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' 'ADVERTENCIA: enrolar claves incorrectamente puede impedir el arranque.'
printf '%s\n' 'Este script crea claves nuevas para esta maquina; nunca las copia al repo.'
[[ -d /sys/firmware/efi ]] || { printf 'El sistema no arranco en modo UEFI.\n' >&2; exit 1; }
[[ "$(findmnt -no FSTYPE /boot 2>/dev/null || true)" == vfat ]] || {
    printf '/boot no es una ESP vfat montada; revisa el sistema manualmente.\n' >&2
    exit 1
}
for command in sbctl limine-install limine-enroll-config limine-update; do
    command -v "$command" >/dev/null 2>&1 || { printf 'Falta %s.\n' "$command" >&2; exit 1; }
done
sbctl status
read -r -p 'Escribe ENROLAR para continuar: ' answer
[[ "$answer" == "ENROLAR" ]] || { printf 'Cancelado.\n'; exit 1; }

sudo sbctl create-keys
sudo limine-install --fallback
sudo sbctl sign -s /boot/EFI/BOOT/BOOTX64.EFI
sudo limine-enroll-config
sudo limine-update
sudo sbctl verify
printf 'Todo esta preparado y firmado. El siguiente paso modifica las claves del firmware.\n'
read -r -p 'Escribe FIRMWARE para enrolarlas: ' firmware_answer
[[ "$firmware_answer" == "FIRMWARE" ]] || { printf 'Claves creadas pero no enroladas.\n'; exit 1; }
sudo sbctl enroll-keys --microsoft --firmware-builtin
