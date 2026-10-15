#!/usr/bin/env bash

set -o pipefail

# Heurística RAM vs frescura (características del programa):
# - `codex app-server` es un binario estático de ~251MB que abre SQLite de
#   ~350MB y hace TLS+auth. Cada arranque frío cuesta ~0.9s vivo (antes 6s
#   por sleeps fijos) y un pico transitorio de RAM.
# - La ventana primaria dura 300min (18000s): el % cambia lento salvo uso
#   activo. TTL=90s = 0.5% de la ventana.
# - Balance: 90s TTL + tick barato de 15s en luau => máx 40 arranques/hora
#   x ~0.9s = ~36s/h vivo, vs 12x6s=72s/h antes. Mitad de RAM-tiempo con
#   3x más frescura. Bajar a 60s duplicaría arranques por poca ganancia;
#   subir a 300s vuelve a mentir (bug original).
cache_file="${XDG_CACHE_HOME:-$HOME/.cache}/noctalia-codex-usage.json"
cache_dir="${cache_file%/*}"
cache_ttl_seconds=90
fetch_timeout_seconds=6

valid_limits() {
    jq -e '
        (.dailyRemaining | type == "number")
        and (.weeklyRemaining | type == "number")
        and (.dailyResetsAt | type == "number")
        and (.weeklyResetsAt | type == "number")
    ' >/dev/null 2>&1
}

render_limits() {
    local limits_json="$1" fetched_at="${2:-0}" is_stale="${3:-0}"
    local daily_remaining daily_resets_at weekly_remaining weekly_resets_at
    local now remaining_seconds remaining_minutes remaining_hours countdown
    local daily_reset weekly_reset class tooltip text age_seconds

    read -r daily_remaining daily_resets_at weekly_remaining weekly_resets_at < <(
        printf '%s\n' "$limits_json" |
            jq -r '[.dailyRemaining, .dailyResetsAt, .weeklyRemaining, .weeklyResetsAt] | @tsv'
    )

    if [[ ! "$daily_remaining" =~ ^[0-9]+$ || ! "$daily_resets_at" =~ ^[0-9]+$ ||
        ! "$weekly_remaining" =~ ^[0-9]+$ || ! "$weekly_resets_at" =~ ^[0-9]+$ ]]; then
        return 1
    fi

    now="$(date +%s)" || return 1
    if [[ ! "$fetched_at" =~ ^[0-9]+$ ]] || ((fetched_at <= 0)); then
        fetched_at="$now"
    fi
    age_seconds=$((now - fetched_at))
    if ((age_seconds < 0)); then
        age_seconds=0
    fi
    remaining_seconds=$((daily_resets_at - now))
    if ((remaining_seconds < 0)); then
        remaining_seconds=0
    fi
    remaining_minutes=$(((remaining_seconds + 59) / 60))
    remaining_hours=$((remaining_minutes / 60))
    remaining_minutes=$((remaining_minutes % 60))

    if ((remaining_hours > 0)); then
        countdown="${remaining_hours}h ${remaining_minutes}m"
    else
        countdown="${remaining_minutes}m"
    fi

    daily_reset="$(date -d "@$daily_resets_at" '+%d/%m/%Y %H:%M')" || return 1
    weekly_reset="$(date -d "@$weekly_resets_at" '+%d/%m/%Y %H:%M')" || return 1

    if [[ "$is_stale" == "1" ]]; then
        class="stale"
        text="${daily_remaining}%?"
    elif ((daily_remaining >= 50)); then
        class="good"
        text="${daily_remaining}%"
    elif ((daily_remaining >= 20)); then
        class="warning"
        text="${daily_remaining}%"
    else
        class="critical"
        text="${daily_remaining}%"
    fi

    if [[ "$is_stale" == "1" ]]; then
        tooltip="$(printf 'Uso de GPT [DESACTUALIZADO hace %ss]\nPróximo reset: %s\n\nLímite diario (5 h): %s%% restante\nReset diario: %s\n\nLímite semanal: %s%% restante\nReset semanal: %s\n\nNo fiarse: no se pudo refrescar.' \
            "$age_seconds" "$countdown" "$daily_remaining" "$daily_reset" "$weekly_remaining" "$weekly_reset")"
    else
        tooltip="$(printf 'Uso de GPT (hace %ss)\nPróximo reset: %s\n\nLímite diario (5 h): %s%% restante\nReset diario: %s\n\nLímite semanal: %s%% restante\nReset semanal: %s' \
            "$age_seconds" "$countdown" "$daily_remaining" "$daily_reset" "$weekly_remaining" "$weekly_reset")"
    fi

    local stale_bool="false"
    if [[ "$is_stale" == "1" ]]; then
        stale_bool="true"
    fi
    jq -cn \
        --arg text "$text" \
        --arg percentageText "$text" \
        --arg countdown "$countdown" \
        --arg tooltip "$tooltip" \
        --arg class "$class" \
        --argjson percentage "$daily_remaining" \
        --argjson dailyRemaining "$daily_remaining" \
        --argjson dailyResetsAt "$daily_resets_at" \
        --argjson weeklyRemaining "$weekly_remaining" \
        --argjson weeklyResetsAt "$weekly_resets_at" \
        --argjson fetchedAt "$fetched_at" \
        --argjson ageSeconds "$age_seconds" \
        --argjson stale "$stale_bool" \
        '{text: $text, percentageText: $percentageText, countdown: $countdown, tooltip: $tooltip, class: $class, percentage: $percentage, dailyRemaining: $dailyRemaining, dailyResetsAt: $dailyResetsAt, weeklyRemaining: $weeklyRemaining, weeklyResetsAt: $weeklyResetsAt, fetchedAt: $fetchedAt, ageSeconds: $ageSeconds, stale: $stale}'
}

print_unknown() {
    jq -cn '{text: "--", percentageText: "--", countdown: "--", tooltip: "No se pudo consultar Codex", class: "unknown", percentage: 0, fetchedAt: 0, ageSeconds: 0, stale: false}'
}

print_stale() {
    local cached fetched_at
    if [[ -s "$cache_file" ]]; then
        cached="$(jq -c . "$cache_file" 2>/dev/null)"
        if printf '%s\n' "$cached" | valid_limits; then
            fetched_at="$(printf '%s\n' "$cached" | jq -r '.fetchedAt // 0' 2>/dev/null)"
            if [[ ! "$fetched_at" =~ ^[0-9]+$ ]] || ((fetched_at <= 0)); then
                fetched_at="$(stat -c %Y "$cache_file" 2>/dev/null || date +%s)"
            fi
            render_limits "$cached" "$fetched_at" 1 && return 0
        fi
    fi

    print_unknown
}

cache_is_fresh() {
    # $1=now. Exito 0 si el caché existe, es válido, no expiró por TTL y no cruzó el reset.
    local now="$1" cache_mtime cached cached_reset
    [[ -s "$cache_file" ]] || return 1
    cache_mtime="$(stat -c %Y "$cache_file" 2>/dev/null)" || return 1
    cached="$(jq -c . "$cache_file" 2>/dev/null)" || return 1
    printf '%s\n' "$cached" | valid_limits || return 1
    cached_reset="$(printf '%s\n' "$cached" | jq -r '.dailyResetsAt // 0' 2>/dev/null)"
    [[ "$cache_mtime" =~ ^[0-9]+$ && "$cached_reset" =~ ^[0-9]+$ ]] || return 1
    ((now - cache_mtime < cache_ttl_seconds && cached_reset > now)) || return 1
    return 0
}

cached_fetched_at() {
    local fetched_at
    fetched_at="$(jq -r '.fetchedAt // 0' "$cache_file" 2>/dev/null)"
    if [[ "$fetched_at" =~ ^[0-9]+$ ]] && ((fetched_at > 0)); then
        printf '%s\n' "$fetched_at"
    else
        stat -c %Y "$cache_file" 2>/dev/null || date +%s
    fi
}

fetch_response() {
    # Consulta al app-server sin sleeps fijos: mantiene stdin abierto con
    # coproc y corta en cuanto llega .id==2 (típico <1s, máx fetch_timeout).
    local codex_bin="$1" line resp=""
    coproc _CODEX { timeout --kill-after=1s "${fetch_timeout_seconds}s" "$codex_bin" app-server 2>/dev/null; }
    local wfd="${_CODEX[1]}" rfd="${_CODEX[0]}"
    {
        printf '%s\n' '{"id":1,"method":"initialize","params":{"clientInfo":{"name":"noctalia-codex-usage","version":"1.0"}}}'
        printf '%s\n' '{"method":"initialized","params":{}}'
        printf '%s\n' '{"id":2,"method":"account/rateLimits/read","params":{}}'
    } >&"$wfd" || {
        exec {wfd}>&- 2>/dev/null || true
        wait "$_CODEX_PID" 2>/dev/null || true
        return 1
    }
    while IFS= read -r -t "$fetch_timeout_seconds" line <&"$rfd"; do
        resp+="$line"$'\n'
        if printf '%s\n' "$line" | jq -e 'select(.id == 2 and (.result.rateLimits | type == "object"))' >/dev/null 2>&1; then
            break
        fi
    done
    exec {wfd}>&- 2>/dev/null || true
    wait "$_CODEX_PID" 2>/dev/null || true
    [[ -n "$resp" ]] || return 1
    printf '%s' "$resp"
}

force_refresh=0
if [[ "${1:-}" == "--force" || "${1:-}" == "-f" || "${1:-}" == "refresh" ]]; then
    force_refresh=1
fi

now="$(date +%s)"
if ((force_refresh == 0)) && cache_is_fresh "$now"; then
    cached="$(jq -c . "$cache_file" 2>/dev/null)"
    render_limits "$cached" "$(cached_fetched_at)" 0
    exit $?
fi

codex_bin="$HOME/.local/bin/codex"
if [[ ! -x "$codex_bin" ]]; then
    codex_bin="$(command -v codex 2>/dev/null)" || {
        print_stale
        exit 0
    }
fi

response="$(fetch_response "$codex_bin")" || {
    print_stale
    exit 0
}

limits="$(printf '%s\n' "$response" | jq -cer '
    def valid_window:
        type == "object"
        and (.windowDurationMins | type == "number")
        and (.usedPercent | type == "number")
        and (.resetsAt | type == "number");
    def remaining:
        ((100 - .usedPercent) | round | if . < 0 then 0 elif . > 100 then 100 else . end);

    select(.id == 2 and (.result.rateLimits | type == "object"))
    | .result.rateLimits
    | if (
        (.primary | valid_window)
        and (.secondary | valid_window)
        and .primary.windowDurationMins == 300
        and .secondary.windowDurationMins > .primary.windowDurationMins
    ) then {
        dailyRemaining: (.primary | remaining),
        dailyResetsAt: .primary.resetsAt,
        weeklyRemaining: (.secondary | remaining),
        weeklyResetsAt: .secondary.resetsAt
    } else error("unexpected rate limit windows") end
' 2>/dev/null)" || {
    print_stale
    exit 0
}

fetched_now="$(date +%s)"
output="$(render_limits "$limits" "$fetched_now" 0)" || {
    print_stale
    exit 0
}

mkdir -p "$cache_dir" 2>/dev/null || true
tmp_file="$(mktemp "${cache_file}.XXXXXX" 2>/dev/null)" || {
    printf '%s\n' "$output"
    exit 0
}
printf '%s\n' "$output" >"$tmp_file" && mv -f "$tmp_file" "$cache_file" || rm -f "$tmp_file"
printf '%s\n' "$output"
