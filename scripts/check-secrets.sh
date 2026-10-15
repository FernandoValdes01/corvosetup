#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
command -v gitleaks >/dev/null 2>&1 || {
    printf 'Instala Gitleaks para verificar secretos antes de publicar.\n' >&2
    exit 1
}
case "${1:-}" in
    --staged)
        python scripts/check-security.py --staged
        gitleaks git --staged --redact=100 --no-banner --log-level error .
        ;;
    --history)
        gitleaks git --redact=100 --no-banner --log-level error .
        ;;
    "")
        python scripts/check-security.py
        gitleaks dir --redact=100 --no-banner --log-level error .
        ;;
    *) printf 'Uso: bash scripts/check-secrets.sh [--staged|--history]\n' >&2; exit 2 ;;
esac
