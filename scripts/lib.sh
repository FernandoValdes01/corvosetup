#!/usr/bin/env bash

: "${ROOT_DIR:?ROOT_DIR no esta definido}"
: "${CORVOSETUP_DRY_RUN:=0}"

section() {
    printf '\n==> %s\n' "$1"
}

run() {
    printf '  +'
    printf ' %q' "$@"
    printf '\n'
    [[ "$CORVOSETUP_DRY_RUN" == 1 ]] || "$@"
}

backup_file() {
    local destination="$1"
    if [[ -e "$destination" && ! -e "${destination}.corvosetup.bak" ]]; then
        run cp -a -- "$destination" "${destination}.corvosetup.bak"
    fi
}

install_user_file() {
    local source="$1" destination="$2" mode="${3:-0644}"
    backup_file "$destination"
    run install -Dm"$mode" -- "$source" "$destination"
}

install_root_file() {
    local source="$1" destination="$2" mode="${3:-0644}"
    if [[ -e "$destination" && ! -e "${destination}.corvosetup.bak" ]]; then
        run sudo cp -a -- "$destination" "${destination}.corvosetup.bak"
    fi
    run sudo install -Dm"$mode" -- "$source" "$destination"
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'Falta el comando requerido: %s\n' "$1" >&2
        exit 1
    }
}

require_authorized_install() {
    [[ "${CORVOSETUP_AUTHORIZED:-0}" == 1 ]] || {
        printf 'Ejecuta este modulo mediante: bash install.sh [--only modulo]\n' >&2
        exit 1
    }
}
