# Seguridad y privacidad

CorvoSetup versiona archivos ejecutables y configuraciones. Revisa el diff antes de instalarlos o compartirlos. `--dry-run` muestra acciones previstas, pero no reemplaza la lectura del código.

## Datos que permanecen locales

No agregues credenciales ni estado del usuario al repo. Esto incluye `auth.json`, `.env`, tokens, claves privadas, OAuth, sesiones, historial, adjuntos, bases SQLite, backups, favoritos/modelos personales e identificadores o rutas de proyectos de confianza.

Los snapshots de Codex/OpenCode fusionan las claves gestionadas con la configuración ya presente. El restorer no copia archivos de autenticación. Reautentica Codex, OpenCode, Linear y conectores remotos en cada PC; vuelve a activar plugins/conectores por equipo. No se distribuyen cachés.

Los perfiles de pantalla también quedan locales. `config/niri/cfg/display.kdl` es una plantilla sin datos de monitores del equipo de origen.

## Dependencias externas

Las versiones MCP quedan fijadas en `config/mcp/`:

| Servidor | Fuente/version |
| --- | --- |
| JFLAP | Código local del repo, `jflap-mcp` `0.1.0`; las herramientas de archivos `.jff` funcionan sin JAR. Java/JAR solo se requieren para abrir la interfaz gráfica. |
| Packet Tracer | Paquete PyPI `packet-tracer-mcp` `0.9.0`; Cisco Packet Tracer se instala aparte. |
| Draw.io | `@drawio/mcp` `1.7.0` con integridad npm registrada. |

Linear usa OAuth remoto. La skill Draw.io empaquetada se conserva en `skills/drawio`; su servidor MCP se instala aparte del cliente. Los conectores remotos, plugins y credenciales requieren activación de nuevo por usuario.

T3 Code, Cisco Packet Tracer, el JAR de JFLAP, Docker, LaTeX y Android SDK/AVD no se incluyen en el repo. Instálalos desde sus fuentes y acepta sus licencias cuando corresponda. El módulo `desktop` añade un monitor local de chats terminados en T3: consulta `state.sqlite` con SQLite `-readonly`, y guarda solo los IDs ya notificados bajo `~/.local/state/t3code-notify/`. La unidad systemd se instala pero no se habilita automáticamente.

## Chequeos del repositorio

El proyecto incluye `scripts/check-secrets.sh`, que requiere Gitleaks y ejecuta también `scripts/check-security.py`. El workflow `.github/workflows/checks.yml` ejecuta las pruebas de regresión y escanea archivos e historial con Gitleaks en pushes y pull requests. Eso describe su configuración, no un resultado de CI. Los hooks `.githooks/pre-commit` y `.githooks/pre-push` están versionados, pero Git no los activa automáticamente. Configura el clon con:

```bash
git config core.hooksPath .githooks
```

Antes de crear o publicar cambios, ejecuta las comprobaciones disponibles en este clon:

```bash
git diff --check
bash tests/static-checks.sh
bash scripts/check-secrets.sh
```

Revisa el contenido staged y el historial cuando corresponda. Los hooks ayudan a detectar errores, pero no reemplazan la revisión manual. Haz `push` solo después de decidirlo explícitamente. CorvoSetup no sincroniza automáticamente archivos del HOME.
