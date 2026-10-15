#!/usr/bin/env bash
set -euo pipefail

mode="${1:-select}"
case "$mode" in
    select|annotate) ;;
    *) exit 2 ;;
esac

if [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
    lock_dir="$XDG_RUNTIME_DIR"
else
    lock_dir="${TMPDIR:-/tmp}"
fi
lock_file="$lock_dir/corvosetup-screenshot-$mode.lock"
exec 9>"$lock_file"
flock -n 9 || exit 0

selection="$(slurp)"
[[ -n "$selection" ]] || exit 0

if [[ "$mode" == "annotate" ]]; then
    grim -g "$selection" - | satty --filename - --initial-tool brush --copy-command wl-copy --actions-on-enter save-to-clipboard 9>&-
else
    grim -g "$selection" - | (exec 9>&-; wl-copy)
fi
