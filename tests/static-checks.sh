#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

while IFS= read -r script; do
    bash -n "$script"
done < <(printf '%s\n' "$ROOT_DIR/install.sh" "$ROOT_DIR"/scripts/*.sh "$ROOT_DIR/config/noctalia/scripts/codex-usage.sh")

PYTHONDONTWRITEBYTECODE=1 python - <<'PY' "$ROOT_DIR"
import ast
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
for path in (root / "apps" / "logitech-light-manager").glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
PY

PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s "$ROOT_DIR/apps/logitech-light-manager" -p 'test_*.py'

temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT
cp -a /etc/skel/.config/niri/. "$temporary/niri"
patch --silent -d "$temporary/niri" -p1 < "$ROOT_DIR/patches/niri-config.patch"
cp "$ROOT_DIR/config/niri/noctalia.kdl" "$temporary/niri/noctalia.kdl"
niri validate -c "$temporary/niri/config.kdl"

source_repo="$HOME/.local/src/niri-display-settings"
git apply --numstat "$ROOT_DIR/patches/niri-display-settings-spanish.patch" >/dev/null
if [[ -d "$source_repo/.git" ]]; then
    mkdir "$temporary/niri-display-settings"
    git -C "$source_repo" archive 63908ce59632524e0f4545cf3c719c3b2a6b118a | tar -x -C "$temporary/niri-display-settings"
    git -C "$temporary/niri-display-settings" init -q
    git -C "$temporary/niri-display-settings" apply --check "$ROOT_DIR/patches/niri-display-settings-spanish.patch"
fi

printf 'Todas las comprobaciones estaticas pasaron.\n'
