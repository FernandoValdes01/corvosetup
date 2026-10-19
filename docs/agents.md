# Agentes y skills

El repo conserva 30 skills en `skills/`. El módulo `skills` las instala en `~/.local/share/corvosetup/skills` y crea enlaces en `~/.agents/skills`, `~/.codex/skills` y `~/.config/opencode/skills`. Las rutas `@HOME@` de las plantillas se renderizan al restaurar.

Los perfiles Codex viven en `config/codex/agents/` e incluyen roles Luna y Sol. Los perfiles de calidad OpenCode viven en `config/opencode/agents/`. `scripts/restore_agents.py` fusiona las configuraciones gestionadas con `~/.codex/config.toml`, `~/.config/opencode/opencode.jsonc` y `opencode.json`, conservando claves ajenas y credenciales existentes. Las definiciones de agentes compartidas se mantienen en `config/codex/` y `config/opencode/`.

El módulo `agents` instala Codex CLI `0.162.1` y OpenCode `1.19.0` desde el lockfile solo cuando falta uno de esos clientes. Si ya están ambos disponibles, mantiene las versiones instaladas. La configuración y los binarios son piezas separadas.

La skill `quality-agents` se conserva como legado y queda desactivada en Codex y denegada en OpenCode; los perfiles de calidad configurados son el camino activo. La skill `review-ti2-pr` depende de referencias de contexto propias del proyecto. Comprueba que ese material esté disponible en el equipo destino y no añadas URLs, datos de PR ni credenciales al snapshot público.

## Restaurar

```bash
bash install.sh --only skills --dry-run
bash install.sh --only agents --dry-run
```

Cuando el resumen corresponda a lo que quieres, repite sin `--dry-run` y confirma en el prompt. La biblioteca queda bajo `.local/share/corvosetup/skills`; edita el repo y vuelve a instalar para actualizarla, en vez de editar los enlaces o copias generadas.

Después de instalar o en un equipo nuevo, autentica cada cliente:

```bash
codex login
opencode auth login
codex mcp login linear
```

La configuración MCP de Linear apunta a su endpoint remoto. Este repo no guarda tokens ni concede acceso a tu cuenta.

## Documentación oficial

- [OpenAI Codex MCP](https://developers.openai.com/codex/mcp)
- [OpenCode: configuración](https://opencode.ai/docs/config/)
