# Edición de video con FilmCraft

Este setup instala solo FilmCraft de la familia Craft. PhotoCraft es un editor de
fotografías y no se instala. Se utiliza el servidor MCP oficial `filmcraft-cli mcp`,
con la misma edición que el motor nativo, sin un servidor intermediario.

## Restaurar

El módulo `mcp` instala también los MCP ya existentes de Draw.io, JFLAP y Packet
Tracer. Para restaurar todo el entorno de agentes, revisa y ejecuta:

```sh
bash install.sh --only mcp --dry-run
bash install.sh --only mcp
bash install.sh --only skills
bash install.sh --only agents
```

Para instalar únicamente FilmCraft y su wrapper, sin los demás MCP:

```sh
CORVOSETUP_AUTHORIZED=1 CORVOSETUP_DRY_RUN=1 python3 scripts/install_filmcraft.py
CORVOSETUP_AUTHORIZED=1 python3 scripts/install_filmcraft.py
```

El segundo comando aplica una instalación de usuario autorizada explícitamente.
Requiere Linux x86_64, Python 3.11+ con soporte de filtro `tarfile` y acceso a GitHub.
Se fija FilmCraft 0.14.0 y su SHA256 oficial en `config/mcp/filmcraft.json`; el
instalador verifica la descarga antes de extraerla. `--archive /ruta/release.tar.gz`
permite reutilizar una descarga y exige el mismo checksum. La descarga no necesita
sudo. Para otra arquitectura hay que añadir un asset oficial y su checksum, no
reutilizar el binario x86_64.

Destinos:

- Binarios: `~/.local/opt/filmcraft/bin/filmcraft` y `filmcraft-cli`.
- Wrapper MCP: `~/.local/bin/corvosetup-mcp-filmcraft`.
- Entrada del menú FilmCraft, iconos y avisos de licencia en `~/.local/share/`.
- Biblioteca de skills: `~/.local/share/corvosetup/skills/video-editing` y enlaces de
  descubrimiento en Codex, Agents y OpenCode, creados por el módulo `skills`.
- Configuración del servidor en las plantillas Codex y OpenCode, restaurada por el
  módulo `agents`. Las rutas usan `@HOME@` y el restaurador conserva claves ajenas.

Los binarios no se guardan en Git. El instalador rechaza destinos con padres
simbólicos y hojas simbólicas, conserva respaldos al sustituir archivos y no
escribe ni descarga durante dry-run. La instalación de escritorio no se prueba
sobre el HOME real: las regresiones usan un HOME temporal.

FFmpeg y FFprobe deben estar instalados para medir audio, detectar pausas y validar
renders. No se instalan otros editores, motores de transcripción ni servicios de
IA. En Arch/CachyOS ambos vienen en el paquete `ffmpeg`. La skill usa lo disponible;
si falta transcripción o escucha real, lo declara y no inventa una revisión auditiva.

## Uso de la skill

Abre un hilo nuevo tras restaurar para que el cliente descubra el MCP y la skill.
La descripción de `video-editing` y `allow_implicit_invocation: true` permiten
selección automática al pedir edición de videos, limpieza de audio, cortes o montaje.
No depende de escribir un comando especial; también se puede invocar explícitamente
con `$video-editing`. La selección final depende del cliente y modelo que la carga.

Ejemplo: "Mejora la demo.mp4 de este repo para YouTube: limpia el ruido de voz,
recorta esperas innecesarias y añade imágenes del repo donde ayuden. Guarda una
copia y el proyecto editable".

La skill exige FilmCraft y reutiliza el contenido del repo del video: documentación,
logos, capturas, diagramas y resultados. Detecta silencios como candidatos y revisa
contexto antes de cortar. Retima subtítulos y conserva originales y medios del
proyecto. No autoriza subir a YouTube ni enviar grabaciones privadas a terceros.

## Validación

Pruebas aisladas, sin instalar sobre el escritorio:

```sh
python3 -m unittest discover -s tests -p 'test_filmcraft_setup.py' -v
python3 -m unittest discover -s tests -p 'test_video_analysis.py' -v
```

El análisis real de audio se prueba cuando están disponibles FFmpeg y FFprobe; de
lo contrario unittest registra esa parte como omitida. La prueba end-to-end opcional
requiere el CLI instalado, FFmpeg/FFprobe con libx264 y el SDK MCP de las dependencias
existentes del repo, o `uv` para resolver su versión fijada:

```sh
uv run scripts/verify_filmcraft_mcp.py
```

Genera medios sintéticos en una carpeta temporal nueva y deja allí informe JSON,
MP4, PNG y `.fcproj`. Comprueba importación, rangos fuente, montaje, corte, deshacer,
título, imagen MCP, guardado/reapertura, audio real y exportación de 72 fotogramas en
3 segundos sin errores de decodificación ni cambios en el original.

FilmCraft sigue en alpha. La prueba no certifica todos los comandos ni los formatos
de cámaras reales. El MCP tiene permisos de lectura/escritura del usuario. La sesión
headless mantiene el proyecto en memoria: guardar explícitamente `.fcproj` y sus
medios antes de cerrar. No controla automáticamente una ventana abierta.

Origen: [release oficial](https://github.com/storytold/filmcraft/releases/tag/v0.14.0)
y [protocolo para agentes](https://github.com/storytold/filmcraft/blob/v0.14.0/docs/agents.md).
