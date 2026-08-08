#!/usr/bin/env bash
set -u

failures=0
check() {
    local description="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        printf '[OK] %s\n' "$description"
    else
        printf '[FALLO] %s\n' "$description"
        failures=$((failures + 1))
    fi
}

check 'Configuracion de Niri valida' niri validate -c "$HOME/.config/niri/config.kdl"
check 'Niri Display Settings instalado' test -x "$HOME/.local/bin/niri-display-settings"
check 'Logitech Light Manager instalado' test -x "$HOME/.local/bin/logitech-light-manager"
check 'Servicio Logitech habilitado' systemctl --user is-enabled logitech-light-manager.service
check 'Servicio Logitech activo' systemctl --user is-active logitech-light-manager.service
check 'Regla udev Logitech instalada' test -f /etc/udev/rules.d/90-logitech-light-manager.rules
check 'Configuracion de Noctalia instalada' test -f "$HOME/.config/noctalia/config.toml"
check 'Plugin Codex instalado' test -f "$HOME/.local/share/noctalia/plugins/corvo-codex-usage/plugin.toml"
check 'Fuente Monocraft instalada' test -f "$HOME/.local/share/fonts/Monocraft.ttc"
check 'Skills de Matt Pocock instaladas' test -d "$HOME/.agents/skills/ask-matt"
check 'Skill code-review instalada' test -d "$HOME/.agents/skills/code-review"
check 'Skill codebase-design instalada' test -d "$HOME/.agents/skills/codebase-design"
check 'Skill diagnosing-bugs instalada' test -d "$HOME/.agents/skills/diagnosing-bugs"
check 'Skill domain-modeling instalada' test -d "$HOME/.agents/skills/domain-modeling"
check 'Skill grill-me instalada' test -d "$HOME/.agents/skills/grill-me"
check 'Skill grill-with-docs instalada' test -d "$HOME/.agents/skills/grill-with-docs"
check 'Skill handoff instalada' test -d "$HOME/.agents/skills/handoff"
check 'Skill research instalada' test -d "$HOME/.agents/skills/research"
check 'Skill to-tickets instalada' test -d "$HOME/.agents/skills/to-tickets"
check 'Skill find-skills instalada' test -d "$HOME/.agents/skills/find-skills"
check 'Skill improve instalada' test -d "$HOME/.agents/skills/improve"
check 'Configuracion de Limine instalada' test -f /etc/default/limine

if command -v sbctl >/dev/null 2>&1; then
    check 'Estado de Secure Boot legible' sbctl status
    check 'Firmas de Secure Boot validas' sbctl verify
fi

exit "$failures"
