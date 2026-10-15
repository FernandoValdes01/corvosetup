local helper = noctalia.expandPath("~/.config/noctalia/scripts/codex-usage.sh")
local loading = false
local lastData = nil
local tick = 0
-- Heurística: tick barato 15s (solo countdown local, 0 forks) + refresh caro
-- cada 6 ticks ≈90s (TTL del .sh). 90s = 0.5% de la ventana de 5h: fresco
-- sin spawnear el binario de 251MB a cada rato.
local refreshEvery = 6

local function renderUsage(data)
    local container = barWidget.isVertical() and ui.column or ui.row
    barWidget.render(container({ gap = 8, align = "center" }, {
        ui.glyph({ name = "brand-openai", size = 14 }),
        ui.label({ text = data.percentageText }),
        ui.button({
            text = data.countdown,
            variant = "ghost",
            controlSize = "sm",
            tooltip = data.tooltip,
        }),
    }))
end

local function showUnavailable()
    if lastData ~= nil then
        renderUsage(lastData)
        return
    end
    renderUsage({
        percentageText = "--",
        countdown = "--",
        tooltip = "No se pudo consultar Codex",
    })
end

local function formatCountdown(resetsAt)
    local ok, now = pcall(os.time)
    if not ok or type(now) ~= "number" or type(resetsAt) ~= "number" then
        return nil
    end
    local remaining = resetsAt - now
    if remaining < 0 then
        remaining = 0
    end
    local minutes = math.floor((remaining + 59) / 60)
    local hours = math.floor(minutes / 60)
    minutes = minutes % 60
    if hours > 0 then
        return hours .. "h " .. minutes .. "m"
    end
    return minutes .. "m"
end

local function fetch()
    if loading then
        return
    end
    loading = true
    local accepted = noctalia.runAsync(helper, function(result)
        loading = false
        if result.exitCode ~= 0 or result.timedOut then
            showUnavailable()
            return
        end

        local data = noctalia.json.decode(result.stdout)
        if type(data) ~= "table"
            or type(data.percentageText) ~= "string"
            or type(data.countdown) ~= "string"
            or type(data.tooltip) ~= "string" then
            showUnavailable()
            return
        end

        lastData = data
        renderUsage(data)
    end, 7000)
    if not accepted then
        loading = false
        showUnavailable()
    end
end

function update()
    noctalia.setUpdateInterval(15000)
    tick = tick + 1

    -- Tick barato: recalcula solo el countdown desde el último dato.
    -- Cero spawns, cero RAM extra. El refresh caro va cada ~90s.
    if lastData ~= nil and (tick % refreshEvery) ~= 0 then
        -- Si el dato ya viene marcado stale o el reset ya pasó, no esperes: refresca.
        if lastData.stale == true then
            fetch()
            return
        end
        local fresh = formatCountdown(lastData.dailyResetsAt)
        if fresh ~= nil then
            renderUsage({
                percentageText = lastData.percentageText,
                countdown = fresh,
                tooltip = lastData.tooltip,
            })
            return
        end
        -- Sin os.time disponible: cae al refresh normal.
    end

    fetch()
end
