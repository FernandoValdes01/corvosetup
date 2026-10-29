#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install
require_command python3

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' || {
    printf 'Se requiere Python 3.11 o superior.\n' >&2
    exit 1
}

share_dir="${HOME:?HOME no está definido}/.local/share/corvosetup/mcp"
bin_dir="$HOME/.local/bin"

install_python_server() {
    local name="$1" manifest="$2" venv_dir="$share_dir/$1"
    run python3 -m venv "$venv_dir"
    run "$venv_dir/bin/python" -m pip install --disable-pip-version-check -r "$ROOT_DIR/config/mcp/$manifest"
    if [[ "$name" == jflap ]]; then
        run "$venv_dir/bin/python" -m pip install --disable-pip-version-check --no-deps "$ROOT_DIR/apps/jflap-mcp"
    fi
}

install_python_server jflap jflap-requirements.txt
install_python_server packet-tracer packet-tracer-requirements.txt

for server in jflap packet-tracer drawio; do
    run install -Dm0755 "$ROOT_DIR/scripts/mcp-$server" "$bin_dir/corvosetup-mcp-$server"
done

run python3 "$ROOT_DIR/scripts/install_filmcraft.py"

run python3 "$ROOT_DIR/scripts/install_photocraft.py"
