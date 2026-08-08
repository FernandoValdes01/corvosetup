#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export ROOT_DIR

if [[ "$EUID" -eq 0 ]]; then
    printf 'No ejecutes este instalador como root ni mediante sudo. Usa tu usuario normal.\n' >&2
    exit 1
fi

ONLY=""
DRY_RUN=0

usage() {
    printf 'Uso: bash install.sh [--dry-run] [--only MODULO]\n'
    printf 'Modulos: packages, limine, logitech, niri, noctalia, skills\n'
}

while (($#)); do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        --only)
            shift
            [[ $# -gt 0 ]] || { usage >&2; exit 2; }
            ONLY="$1"
            ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Argumento desconocido: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

case "$ONLY" in
    ""|packages|limine|logitech|niri|noctalia|skills) ;;
    *) printf 'Modulo invalido: %s\n' "$ONLY" >&2; usage >&2; exit 2 ;;
esac

export CORVOSETUP_DRY_RUN="$DRY_RUN"
export CORVOSETUP_AUTHORIZED=1
source "$ROOT_DIR/scripts/lib.sh"

if [[ "$DRY_RUN" == 0 ]]; then
    printf 'Se modificaran archivos del sistema y/o del usuario actual.\n'
    read -r -p 'Escribe APLICAR para continuar: ' answer
    [[ "$answer" == "APLICAR" ]] || { printf 'Cancelado.\n'; exit 1; }
fi

modules=(packages limine logitech niri noctalia skills)
for module in "${modules[@]}"; do
    [[ -z "$ONLY" || "$ONLY" == "$module" ]] || continue
    script="$ROOT_DIR/scripts/$(case "$module" in
        packages) printf '01-packages.sh' ;;
        limine) printf '02-limine.sh' ;;
        logitech) printf '03-logitech.sh' ;;
        niri) printf '04-niri.sh' ;;
        noctalia) printf '05-noctalia.sh' ;;
        skills) printf '06-opencode-skills.sh' ;;
    esac)"
    section "$module"
    bash "$script"
done

printf '\nInstalacion terminada. Ejecuta: bash scripts/verify.sh\n'
