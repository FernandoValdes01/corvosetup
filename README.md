<div align="center">
  <h1>CorvoSetup</h1>
  <p>Un setup personal de Linux, versionado para restaurarlo con control.</p>
  <p><a href="#inicio-rápido">Inicio rápido</a> · <a href="#módulos">Módulos</a> · <a href="docs/restore.md">Restauración</a> · <a href="docs/agents.md">Agentes y skills</a> · <a href="docs/security.md">Privacidad</a></p>
</div>

## Inicio rápido

Clona el repositorio y prueba primero solo los módulos que necesitas:

```bash
git clone https://github.com/FernandoValdes01/corvosetup.git
cd corvosetup
bash install.sh --only skills --dry-run
bash install.sh --only skills
```

El modo normal presenta un resumen y pide escribir `APLICAR` antes de continuar. No ejecutes `install.sh` como `root` ni con `sudo`. Para una máquina nueva que no necesita cambios de arranque, el orden mínimo recomendado es `skills`, `mcp`, `agents` y después `desktop`, `niri` o `noctalia` según el entorno. El módulo `limine` queda fuera de ese flujo.

La restauración no instala todo el software externo. Revisa los requisitos y pasos de [restauración](docs/restore.md) antes de aplicar más módulos.

## Qué contiene

Snapshots públicos de configuración de escritorio y desarrollo, herramientas locales y scripts por componente. El repo no sincroniza automáticamente cambios desde el HOME. El usuario revisa, valida y decide qué versionar y subir.

### Módulos

Usa `bash install.sh --only MODULO`; añade `--dry-run` para revisar las acciones antes de aplicarlas. Sin `--only`, recorre los módulos en este orden:

| Módulo | Función |
| --- | --- |
| `packages` | Instala paquetes de Arch/CachyOS definidos por el setup. |
| `limine` | Genera configuración con datos del equipo y configura sincronización Snapper. No modifica Secure Boot. |
| `logitech` | Instala Logitech Light Manager, su servicio de usuario y regla udev. |
| `niri` | Restaura el snapshot portable, Niri Display Settings en español y el atajo de capturas. |
| `noctalia` | Instala configuración, plugin Codex local y fuente Monocraft. |
| `desktop` | Restaura Alacritty, Fish, ajustes T3 Code, lanzadores y la unidad de notificaciones T3. |
| `skills` | Copia 33 skills a la biblioteca local y crea enlaces para los clientes compatibles. |
| `agents` | Fusiona perfiles y configuración Codex/OpenCode. Instala CLI fijadas solo si falta alguno de los clientes. |
| `mcp` | Instala servidores MCP Draw.io, JFLAP, Packet Tracer, FilmCraft y PhotoCraft, y sus lanzadores locales. [Video](docs/filmcraft.md) y [fotos con referencias](docs/photocraft.md). |

### Estructura

| Ruta | Contenido |
| --- | --- |
| `apps/` | Logitech Light Manager y código fuente del servidor MCP JFLAP. |
| `config/` | Snapshots `niri`, `alacritty`, `fish`, `noctalia`, `t3code`, `codex`, `opencode`, `agents`, `skills` y `mcp`. |
| `skills/` | Biblioteca común de 33 skills con sus recursos. |
| `scripts/` | Instaladores por módulo, restaurador de agentes, verificaciones y lanzadores MCP. |
| `patches/` | Parche de idioma de Niri Display Settings. |
| `tests/` | Comprobaciones estáticas y pruebas de regresión. |
| `docs/` | Guías de restauración, agentes/skills y seguridad. |

## Qué debes configurar en cada PC

Los perfiles de monitores quedan fuera del snapshot. Niri conserva el `cfg/display.kdl` local existente e instala la plantilla portátil solo si falta. Consulta `niri msg outputs` para configurarlo en ese hardware.

El módulo `desktop` instala el servicio de notificaciones T3, pero no lo activa automáticamente. Para habilitarlo cuando T3 Code esté instalado, ejecuta `systemctl --user daemon-reload && systemctl --user enable --now t3code-notify.service`. El monitor consulta la base local de T3 en modo solo lectura; no copia la base ni el historial.

El vidrio de T3 Code usa opacidad `0.86` y blur Niri, y requiere una versión de Niri compatible con blur. Alacritty usa opacidad `0.7`. Las versiones de paquetes en `packages/current-versions.txt` son referencias del snapshot, no un pin del repositorio rolling.

No se copian credenciales, sesiones, historiales, favoritos/modelos personales, bases SQLite, backups ni rutas a proyectos de confianza. Codex, OpenCode y Linear deben autenticarse otra vez; los conectores/plugins remotos se reactivan en cada equipo. Consulta [privacidad y seguridad](docs/security.md).

## Cambiar el setup

Edita los archivos del repo, revisa `git diff`, prueba el módulo afectado y ejecuta los chequeos de secretos. Crea commits que puedas revisar. El `push` siempre es una decisión explícita; no hay sincronización automática desde el equipo.
