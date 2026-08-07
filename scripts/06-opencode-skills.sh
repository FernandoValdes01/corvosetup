#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$ROOT_DIR/scripts/lib.sh"
require_authorized_install

require_command npx

cli=skills@1.5.22
run npx --yes "$cli" add mattpocock/skills@8b78b531ab965735c5dc74f6f7a219e1e37326df -g -a opencode -y
run npx --yes "$cli" add vercel-labs/skills@c6f69c631292444cc541ac6d91e2226b0ff247da --skill find-skills -g -a opencode -y
run npx --yes "$cli" add shadcn/improve@03369ee6d7cafbfcecc4346539b05b3dc0a603bb --skill improve -g -a opencode -y
