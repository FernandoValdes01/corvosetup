#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command python
restore_args=(skills)
[[ "$CORVOSETUP_DRY_RUN" == 0 ]] || restore_args+=(--dry-run)
python "$ROOT_DIR/scripts/restore_agents.py" "${restore_args[@]}"
