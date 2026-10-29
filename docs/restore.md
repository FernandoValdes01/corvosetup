# Restaurar en otro PC

CorvoSetup restaura archivos públicos de configuración mediante módulos separados. Ejecuta los que necesites desde una sesión de usuario normal. Cada aplicación de módulo pide confirmación; revisa el código y el modo de prueba antes de responder.

## Requisitos externos

- Arch/CachyOS con acceso a Internet y cuenta de usuario normal.
- T3 Code instalado aparte desde una fuente AUR. CorvoSetup respalda su configuración, no empaqueta la aplicación.
- Niri 26.04 con soporte de blur para el efecto glass de T3. La versión figura como referencia en `packages/current-versions.txt`; el repositorio rolling puede ofrecer otra versión.
- Para MCP, Python 3.11 o posterior y Node.js/npm. Packet Tracer requiere Cisco Packet Tracer instalado aparte. Las herramientas JFLAP que procesan archivos `.jff` funcionan sin JAR; Java y el JAR solo hacen falta para abrir la interfaz gráfica. Define `JFLAP_HOME`, `JFLAP_JAR` o `JFLAP_LAUNCHER` si sus rutas difieren de los valores predeterminados.
- Docker, LaTeX y Android SDK/AVD se instalan aparte si tus proyectos los necesitan. El repo no contiene estos binarios ni software propietario.

## Clonar y revisar

```bash
git clone https://github.com/FernandoValdes01/corvosetup.git
cd corvosetup
bash install.sh --help
```

El instalador prohíbe ejecutarse como root. Usa `--dry-run` para revisar cada módulo. Por ejemplo, este recorrido excluye `limine` y no aplica instalaciones:

```bash
for module in skills mcp agents desktop niri noctalia; do
  bash install.sh --only "$module" --dry-run
done
```

Para una restauración mínima que no toque arranque, aplica `skills`, `mcp` y `agents`; después aplica `desktop`, `niri` y `noctalia` según tu entorno. Cada ejecución sin `--dry-run` muestra sus acciones y pide escribir `APLICAR`. Revisa los scripts, el estado del equipo y las rutas antes de confirmar.

`limine` modifica configuración de arranque. Aplícalo solo si ese es el objetivo y después de revisar sus comprobaciones y plantillas. No es necesario para restaurar escritorio, MCP, agentes o skills.

## Pantallas y credenciales

La configuración incluida no fija nombres, modos ni coordenadas de monitor. Después de iniciar sesión en Niri:

```bash
niri msg outputs
```

Niri conserva un `~/.config/niri/cfg/display.kdl` ya existente e instala la plantilla portable solo si el archivo falta. Edita ese archivo localmente con los valores adecuados para el hardware.

Vuelve a autenticar las aplicaciones y servicios remotos en el nuevo PC:

```bash
codex login
opencode auth login
codex mcp login linear
```

T3 Code, sus plugins y conectores remotos también necesitan activación local. El módulo `desktop` instala `t3code-notify.service`, pero deja su activación manual. Con T3 Code ya instalado, habilítalo así:

```bash
systemctl --user daemon-reload
systemctl --user enable --now t3code-notify.service
```

El monitor lee la base SQLite local con acceso de solo lectura, no la copia ni migra el historial. No se migran sesiones, OAuth, cachés ni preferencias de modelos personales.

## Validación

Estos comandos están documentados como pasos de validación; la documentación no afirma que se hayan ejecutado en el PC destino.

```bash
bash tests/static-checks.sh
bash scripts/check-secrets.sh
bash scripts/verify.sh
```

`check-secrets.sh` requiere Gitleaks. El workflow `.github/workflows/checks.yml` ejecuta pruebas de regresión y escaneo Gitleaks sobre el directorio y el historial en pushes y pull requests; su existencia no significa que un run haya pasado. `scripts/verify.sh` comprueba servicios y archivos instalados; sus resultados dependen de los módulos que hayas aplicado. Se ejecutaron pruebas aisladas de restauración y MCP, pero no una restauración completa en otro PC.

## FilmCraft y edición de video

El módulo `mcp` incluye FilmCraft 0.14.0 para Linux x86_64, verificado por SHA256.
Los módulos `skills` y `agents` restauran la skill auto invocable y su conexión MCP.
Para instalar solo FilmCraft, requisitos de análisis y pruebas aisladas, consulta
[el setup de video](filmcraft.md). No se instalan los otros editores de la familia Craft.
