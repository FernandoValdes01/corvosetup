#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT

bin_dir="$temporary/bin"
runtime_dir="$temporary/runtime"
log_file="$temporary/tools.log"
mkdir -p -- "$bin_dir" "$runtime_dir"

# Simulate an annotation session whose clipboard child still owns the
# legacy shared lock. Normal Print captures must remain independent of it.
exec 8>"$runtime_dir/corvosetup-screenshot.lock"
flock -n 8

for command in slurp grim wl-copy satty; do
    ln -s -- "$ROOT_DIR/tests/fixtures/screenshot-tools.sh" "$bin_dir/$command"
done

pids=()
for _ in {1..2}; do
    for _ in {1..5}; do
        PATH="$bin_dir:$PATH" \
            XDG_RUNTIME_DIR="$runtime_dir" \
            SCREENSHOT_TEST_LOG="$log_file" \
            bash "$ROOT_DIR/scripts/screenshot.sh" select &
        pids+=("$!")
    done

    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    pids=()
done

for command in slurp grim wl-copy; do
    count=0
    if [[ -f "$log_file" ]]; then
        count="$(awk -v command="$command" '$0 == command { count++ } END { print count + 0 }' "$log_file")"
    fi
    [[ "$count" == 2 ]] || {
        printf 'Se esperaban dos ejecuciones de %s, pero hubo %s.\n' "$command" "$count" >&2
        exit 1
    }
done

exec 8>&-
for _ in {1..2}; do
    for _ in {1..5}; do
        PATH="$bin_dir:$PATH" \
            XDG_RUNTIME_DIR="$runtime_dir" \
            SCREENSHOT_TEST_LOG="$log_file" \
            bash "$ROOT_DIR/scripts/screenshot.sh" annotate &
        pids+=("$!")
    done

    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    pids=()
done

for command in slurp grim; do
    count="$(awk -v command="$command" '$0 == command { count++ } END { print count + 0 }' "$log_file")"
    [[ "$count" == 4 ]] || {
        printf 'Se esperaban cuatro ejecuciones de %s, pero hubo %s.\n' "$command" "$count" >&2
        exit 1
    }
done

satty_count="$(awk '$0 == "satty" { count++ } END { print count + 0 }' "$log_file")"
[[ "$satty_count" == 2 ]] || {
    printf 'Se esperaban dos ejecuciones de satty, pero hubo %s.\n' "$satty_count" >&2
    exit 1
}
