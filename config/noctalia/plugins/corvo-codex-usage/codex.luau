local helper = noctalia.expandPath("~/.config/noctalia/scripts/codex-usage.sh")
local loading = false

local function showUnavailable()
    barWidget.setGlyph("brand-openai")
    barWidget.setText("--")
    barWidget.setTooltip("No se pudo consultar Codex")
end

local function showUsage(data)
    barWidget.setGlyph("brand-openai")
    barWidget.setText(data.text)
    barWidget.setTooltip(data.tooltip)
end

function update()
    noctalia.setUpdateInterval(300000)
    if loading then return end
    loading = true
    local accepted = noctalia.runAsync(helper, function(result)
        loading = false
        if result.exitCode ~= 0 or result.timedOut then
            showUnavailable()
            return
        end
        local data = noctalia.json.decode(result.stdout)
        if type(data) ~= "table" or type(data.text) ~= "string" or type(data.tooltip) ~= "string" then
            showUnavailable()
            return
        end
        showUsage(data)
    end, 10000)
    if not accepted then
        loading = false
        showUnavailable()
    end
end
