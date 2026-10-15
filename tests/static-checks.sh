#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

while IFS= read -r script; do
    bash -n "$script"
done < <(printf '%s\n' "$ROOT_DIR/install.sh" "$ROOT_DIR"/scripts/*.sh "$ROOT_DIR/config/noctalia/scripts/codex-usage.sh")

for script in "$ROOT_DIR"/scripts/mcp-* "$ROOT_DIR"/scripts/t3code-* "$ROOT_DIR"/.githooks/*; do
    bash -n "$script"
done

bash "$ROOT_DIR/tests/screenshot-lock.sh"

PYTHONDONTWRITEBYTECODE=1 python - <<'PY' "$ROOT_DIR"
import ast
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
for path in (root / "apps" / "logitech-light-manager").glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
PY

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT_DIR/apps/jflap-mcp${PYTHONPATH:+:$PYTHONPATH}"
python -m unittest discover -s "$ROOT_DIR/apps/logitech-light-manager" -p 'test_*.py'
python -m unittest discover -s "$ROOT_DIR/tests" -p 'test_*.py'
python "$ROOT_DIR/scripts/check-security.py"

temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT
if command -v niri >/dev/null 2>&1; then
    niri validate -c "$ROOT_DIR/config/niri/config.kdl"
else
    printf 'Niri no instalado: omiti validacion nativa KDL.\n'
fi

source_repo="$HOME/.local/src/niri-display-settings"
git apply --numstat "$ROOT_DIR/patches/niri-display-settings-spanish.patch" >/dev/null
if [[ -d "$source_repo/.git" ]]; then
    mkdir "$temporary/niri-display-settings"
    git -C "$source_repo" archive 63908ce59632524e0f4545cf3c719c3b2a6b118a | tar -x -C "$temporary/niri-display-settings"
    git -C "$temporary/niri-display-settings" init -q
    git -C "$temporary/niri-display-settings" apply --check "$ROOT_DIR/patches/niri-display-settings-spanish.patch"
fi

printf 'Todas las comprobaciones estaticas pasaron.\n'
