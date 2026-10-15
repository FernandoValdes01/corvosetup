#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' "$(basename "$0")" >> "$SCREENSHOT_TEST_LOG"

case "$(basename "$0")" in
    slurp)
        sleep 0.2
        printf '0,0 100x100\n'
        ;;
    grim)
        printf 'screenshot-data\n'
        ;;
    wl-copy)
        cat >/dev/null
        (sleep 0.2) &
        sleep 0.2
        ;;
    satty)
        cat >/dev/null
        (sleep 0.2) &
        sleep 0.2
        ;;
    *)
        exit 2
        ;;
esac
