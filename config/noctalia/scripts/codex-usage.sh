#!/usr/bin/env bash
set -o pipefail

cache_file="${XDG_CACHE_HOME:-$HOME/.cache}/noctalia-codex-usage.json"
cache_dir="${cache_file%/*}"

print_cached_or_error() {
    if [[ -s "$cache_file" ]] && jq -e . "$cache_file" >/dev/null 2>&1; then
        jq -c . "$cache_file"
    else
        jq -cn '{text: "--", tooltip: "No se pudo consultar Codex", class: "unknown", percentage: 0}'
    fi
}

codex_bin="$HOME/.local/bin/codex"
if [[ ! -x "$codex_bin" ]]; then
    codex_bin="$(command -v codex 2>/dev/null)" || { print_cached_or_error; exit 0; }
fi

response="$(
    {
        printf '%s\n' '{"id":1,"method":"initialize","params":{"clientInfo":{"name":"noctalia-codex-usage","version":"1.0"}}}'
        sleep 1
        printf '%s\n' '{"method":"initialized","params":{}}'
        sleep 1
        printf '%s\n' '{"id":2,"method":"account/rateLimits/read","params":{}}'
        sleep 4
    } | timeout --kill-after=1s 8s "$codex_bin" app-server 2>/dev/null
)" || { print_cached_or_error; exit 0; }

weekly="$(printf '%s\n' "$response" | jq -cer '
    select(.id == 2 and (.result.rateLimits | type == "object"))
    | .result.rateLimits | [.primary, .secondary]
    | map(select(type == "object" and (.windowDurationMins | type == "number") and (.usedPercent | type == "number") and (.resetsAt | type == "number")))
    | if length == 0 then error("no rate limit windows") else max_by(.windowDurationMins) end
' 2>/dev/null)" || { print_cached_or_error; exit 0; }

read -r remaining resets_at < <(printf '%s\n' "$weekly" | jq -r '[((100 - .usedPercent) | round | if . < 0 then 0 elif . > 100 then 100 else . end), .resetsAt] | @tsv')
[[ "$remaining" =~ ^[0-9]+$ && "$resets_at" =~ ^[0-9]+$ ]] || { print_cached_or_error; exit 0; }
reset="$(date -d "@$resets_at" '+%d/%m/%Y %H:%M')" || { print_cached_or_error; exit 0; }

if ((remaining >= 50)); then class=good; elif ((remaining >= 20)); then class=warning; else class=critical; fi
tooltip="$(printf 'Codex\n%s%% restante\nReset: %s' "$remaining" "$reset")"
output="$(jq -cn --arg text "${remaining}%" --arg tooltip "$tooltip" --arg class "$class" --argjson percentage "$remaining" --argjson resetsAt "$resets_at" '{text: $text, tooltip: $tooltip, class: $class, percentage: $percentage, resetsAt: $resetsAt}')"

mkdir -p "$cache_dir" 2>/dev/null || true
tmp_file="$(mktemp "${cache_file}.XXXXXX" 2>/dev/null)" || { printf '%s\n' "$output"; exit 0; }
printf '%s\n' "$output" > "$tmp_file" && mv -f "$tmp_file" "$cache_file" || rm -f "$tmp_file"
printf '%s\n' "$output"
