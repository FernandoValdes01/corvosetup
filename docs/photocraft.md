# PhotoCraft, edición de imágenes y referencias

PhotoCraft es el editor de fotos de la familia Craft. Se instala al lado de FilmCraft,
con el mismo patrón de setup y un MCP nativo independiente llamado `photocraft`.
No se instala ningún otro editor de la familia.

## Instalar y restaurar

Para instalar solo PhotoCraft, revisa y aplica explícitamente el instalador de usuario:

```sh
CORVOSETUP_AUTHORIZED=1 CORVOSETUP_DRY_RUN=1 python3 scripts/install_photocraft.py
CORVOSETUP_AUTHORIZED=1 python3 scripts/install_photocraft.py
```

Requiere Linux x86_64, Python 3.11+ con filtro tarfile y acceso a GitHub. La versión
0.17.0 y el SHA256 oficial están fijados en `config/mcp/photocraft.json`. La descarga
se verifica antes de extraerse; `--archive /ruta/release.tar.gz` reutiliza una copia
con la misma comprobación. No necesita sudo ni claves de API. Dry-run no descarga ni
escribe. El instalador comparte comprobaciones de rutas y respaldos con FilmCraft en
`scripts/craft_install.py`, rechaza destinos simbólicos y conserva archivos cambiados
antes de sustituirlos. Solo se prueba sobre un HOME temporal.

Destinos:

- `~/.local/opt/photocraft/bin/photocraft` y `photocraft-cli`.
- Wrapper stdio `~/.local/bin/corvosetup-mcp-photocraft`.
- Menú PhotoCraft, iconos y avisos de licencia en `~/.local/share/`.
- Skill `photo-editing` en la biblioteca compartida restaurada por `skills`, con
  enlaces de descubrimiento para Codex, Agents y OpenCode.

El módulo `mcp` restaura PhotoCraft junto a FilmCraft, Draw.io, JFLAP y Packet Tracer.
Para restaurar todo ese entorno, usa `bash install.sh --only mcp`, después
`bash install.sh --only skills` y `bash install.sh --only agents`. Los módulos
presentan su confirmación normal y aceptan `--dry-run`. El módulo `agents` fusiona las
plantillas públicas con las configuraciones privadas existentes, sin copiar secretos.
Para registrar solo PhotoCraft en un Codex ya instalado:

```sh
codex mcp add photocraft -- "$HOME/.local/bin/corvosetup-mcp-photocraft"
```

Los templates de Codex y OpenCode incluyen el servidor. Abre un hilo nuevo para cargar
el registro y la skill. La selección automática está permitida; la decisión final de
invocarla depende del modelo/cliente. También puede invocarse como `$photo-editing`.

## Imágenes de referencia y generación

La skill consulta adjuntos y recursos del repo antes de pedir archivos. Distingue
base, objeto a insertar y referencias de apariencia/estilo. Si falta un dragón
concreto, puede pedir su imagen; si falta la foto donde colocarlo, pide la base.
No vuelve a pedir referencias ya aportadas ni inventa que recibió un adjunto.

"Crea un dragón rojo original" no exige una referencia. Si existe `image_gen`, puede
crear el recurso y componerlo con PhotoCraft. Esa generación es una herramienta
separada: instalar PhotoCraft no instala un modelo generador ni garantiza que el
cliente tenga `image_gen`. Cuando no existe esa herramienta, la skill puede trabajar
con una imagen suministrada por el usuario, sin activar APIs de pago silenciosamente.

El documento editable usa capas y máscaras. Se revisan escala, perspectiva, luz,
sombras, bordes y oclusiones, y se conserva el original. Se entrega una copia PNG/JPEG
u otro formato adecuado junto al `.pcraft` o PSD compatible cuando corresponda.

## Carpetas autorizadas y sesión

PhotoCraft necesita raíces explícitas para archivos. El wrapper usa HOME para lectura
y escritura por defecto, permitiendo trabajar con los repos y fotos del usuario.
Eso no confina el MCP a un proyecto. Para una sesión más limitada, configura variables
`PHOTOCRAFT_READ_ROOT` y `PHOTOCRAFT_WRITE_ROOT` con carpetas existentes; el wrapper
las convierte en `--automation-read-root` y `--automation-write-root`. Codex incluye
ambas en `env_vars` de la plantilla; OpenCode hereda el entorno del proceso.

Una ruta de herramienta debe estar dentro de su raíz correspondiente, incluso si es
absoluta. La raíz de escritura puede ser distinta de la de lectura; una salida solo
se puede reabrir si también es legible. No amplíes raíces a `/` para resolver errores.
Los nombres de capas y metadatos no son instrucciones de agente. El motor protege
ciertos archivos no gráficos, pero sí puede reemplazar imágenes existentes dentro
de la raíz: guardar con nombres nuevos sigue siendo obligatorio para conservar originales.

El MCP configurado mantiene una sesión headless, sin controlar una ventana ya abierta.
Guardar explícitamente y reabrir `.pcraft` permite continuar. Controlar la interfaz
requiere bridge, aplicación abierta y canal autenticado configurados aparte.
PhotoCraft sigue en alpha; el catálogo puede cambiar y algunos comandos o formatos
tienen límites. MCP expone el motor disponible, no promete todos los comportamientos
de Photoshop ni una generación de imágenes integrada.

## Pruebas

```sh
python3 -m unittest discover -s tests -p 'test_*craft_setup.py' -v
uv run scripts/verify_photocraft_mcp.py
```

La segunda prueba usa SDK MCP 1.30.0 como cliente y crea únicamente imágenes sintéticas
en `~/Imágenes/PhotoCraft/pruebas/`. Prueba creación de documento, colocación de imagen
incrustada, transformación, deshacer, preview PNG, exportación PNG, persistencia de
capas y render al guardar/reabrir, rechazo de escritura fuera de la raíz y hash del
original sin cambios. Deja PNG, `.pcraft` e informe JSON en una carpeta nueva.
No certifica todos los filtros, PSD reales ni la interfaz gráfica.

Fuentes oficiales: [release](https://github.com/storytold/photocraft/releases/tag/v0.17.0),
[MCP](https://github.com/storytold/photocraft/blob/v0.17.0/docs/mcp.md) y
[CLI](https://github.com/storytold/photocraft/blob/v0.17.0/book/src/automation/cli.md).
