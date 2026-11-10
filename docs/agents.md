# Agentes y skills

El repo conserva 38 skills en `skills/`. El módulo `skills` las instala en `~/.local/share/corvosetup/skills` y crea enlaces en `~/.agents/skills`, `~/.codex/skills`, `~/.config/opencode/skills` y `~/.claude/skills`. Las rutas `@HOME@` de las plantillas se renderizan al restaurar.

Los perfiles Codex viven en `config/codex/agents/` e incluyen roles Luna y Sol. Los perfiles de calidad OpenCode viven en `config/opencode/agents/`. `scripts/restore_agents.py` fusiona las configuraciones gestionadas con `~/.codex/config.toml`, `~/.config/opencode/opencode.jsonc` y `opencode.json`, conservando claves ajenas y credenciales existentes. Para Claude Code solo gestiona `mcpServers` dentro de `~/.claude.json` (el resto del archivo, con su sesión y proyectos, se conserva con modo `0600`) e instala `~/.claude/CLAUDE.md` desde `config/claude/`. Cierra Claude Code antes de restaurar, porque reescribe `~/.claude.json` mientras está abierto. Las definiciones de agentes compartidas se mantienen en `config/codex/` y `config/opencode/`.

El módulo `agents` instala Codex CLI `0.162.1` y OpenCode `1.19.0` desde el lockfile solo cuando falta uno de esos clientes. Si ya están ambos disponibles, mantiene las versiones instaladas. La configuración y los binarios son piezas separadas.

La skill `quality-agents` se conserva como legado y queda desactivada en Codex y denegada en OpenCode; los perfiles de calidad configurados son el camino activo. La skill `brag` se publica sin su música ni efectos de sonido, porque su licencia de redistribución no está verificada; funciona sin ellos o con audio propio. La skill `firefox-local` usa el servidor de `apps/firefox-mcp`. La skill `review-ti2-pr` depende de referencias de contexto propias del proyecto. Comprueba que ese material esté disponible en el equipo destino y no añadas URLs, datos de PR ni credenciales al snapshot público.

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

En Claude Code, autentica Linear con `/mcp`. La configuración MCP de Linear apunta a su endpoint remoto. Este repo no guarda tokens ni concede acceso a tu cuenta; si usas varias cuentas de Linear, agrega sus entradas localmente y el restaurador las conserva.

YouTube Research funciona sin clave para transcripciones; para búsquedas y estadísticas exporta `YOUTUBE_API_KEY` en tu entorno. El repo nunca la guarda.

## Documentación oficial

- [OpenAI Codex MCP](https://developers.openai.com/codex/mcp)
- [OpenCode: configuración](https://opencode.ai/docs/config/)

## Edición de video

La skill `video-editing` se selecciona automáticamente para editar y mejorar videos
con FilmCraft. Usa material del repositorio del video, revisa pausas y limpia audio;
no publica en YouTube. El MCP nativo, su instalación reproducible y sus pruebas
están descritos en [FilmCraft](filmcraft.md). Requiere FFmpeg/FFprobe para análisis.

## Edición de imágenes

La skill auto invocable `photo-editing` usa PhotoCraft para retoque y composición.
Distingue base, objeto y referencia; pide imágenes faltantes cuando afectan el
resultado y permite crear recursos originales con `image_gen` si está disponible.
El setup y las pruebas están en [PhotoCraft](photocraft.md).
