# FilmCraft MCP y persistencia

FilmCraft es el editor de video enlazado desde PhotoCraft; no instalar PhotoCraft
para este trabajo. El setup reproducible de CorvoSetup está en
`config/mcp/filmcraft.json`, `scripts/install_filmcraft.py`, `scripts/mcp-filmcraft`
y `docs/filmcraft.md`. El servidor es el MCP oficial por stdio del editor.

En este equipo: `@HOME@/.local/opt/filmcraft/bin/filmcraft-cli mcp`.
En una restauración: `@HOME@/.local/bin/corvosetup-mcp-filmcraft`.
Codex y OpenCode usan el nombre `filmcraft`. En un hilo nuevo se cargan los MCP y
skills recién instalados. Si el cliente no expone las herramientas, comprueba su
configuración y la inicialización; no afirmes que el MCP está conectado solo por
existir el archivo. Mientras se resuelve la conexión, el CLI oficial permite operar
el mismo motor mediante `run` y comandos tipados; informa ese modo de uso.

## Descubrir antes de ejecutar

- `command_list` busca IDs, parámetros y disponibilidad. `command_run` ejecuta
  `{ "id": "...", "params": { ... } }`; `command_batch` agrupa pasos.
- `media_import` importa rutas absolutas. Usa los IDs devueltos y los de
  `project_inspect`/`sequence_inspect`, nunca IDs copiados de ejemplos.
- `render_preview`/`render_frame` devuelven imágenes MCP para que la IA vea el
  resultado. Renderiza antes y después de cada intervención visual significativa.
- `edit.undo` revierte una edición. Guardar es explícito y el proceso mantiene
  estado; llamadas aisladas al CLI no comparten proyecto sin guardar/reabrir.

Para explorar sin MCP: `filmcraft-cli commands --json`, `describe <id>`,
`probe /ruta/base.mp4`. Evita pegar todo el catálogo en contexto. Filtra por lo que
necesitas: `timeline`, `effects`, `audio`, `captions`, `graphics`, `export`.
Consulta los comandos habilitados después de seleccionar clips cuando corresponda.

Familias útiles comprobadas en 0.14.0: `file.newProject`, `file.newSequence`,
`file.newSequenceFromClip`, `timeline.place`, `timeline.razor`, `timeline.trim`,
`timeline.select`, `clip.audioGain`, `effects.list`, `effects.apply`,
`effects.setParam`, `graphics.newText`, `graphics.newFromFile`, `captions.*`,
`sequence.applyAudioTransition`, `file.saveAs`, `file.open`, `file.exportMedia`.
Descubre los parámetros de cada efecto con el motor, no inventes nombres o IDs.

## Tiempo y segmentos

FilmCraft usa 254016000000 ticks por segundo. Algunos comandos ofrecen `seconds`,
`frame` o timecode; otros como `sourceIn`, `duration` y ciertas operaciones de trim
usan ticks. Alinea a fotogramas y usa enteros/racionales para evitar deriva.
`track="V1"` identifica una pista de video; `track` en gráficos puede ser un índice
con otro significado. Consulta cada esquema antes de reutilizar el parámetro.

Ejemplo ilustrativo para conservar segundos 10..15 de un medio importado:

```json
{"id":"timeline.place","params":{"item":8,"track":"V1","seconds":0,"sourceIn":2540160000000,"duration":1270080000000}}
```

Sustituye `8` por el ID real. Los segmentos se pueden colocar sucesivamente con sus
rangos fuente y audio vinculado; no hace falta borrar nada del archivo original.

## Audio, exportación y entrega

Consulta `effects.list` con `kind="Audio"` y los parámetros reales de los efectos.
`clip.audioGain` permite ganancia y normalización de picos; no equivale a LUFS.
`file.exportMedia` admite `loudnessLufs`, pero mide el resultado y evita sumar otra
normalización sin necesidad. Si el formato del original falla, conserva el original
y crea un proxy/intermedio con FFmpeg, identificándolo en el registro de medios.
No cambies la duración ni la sincronía al preparar el intermedio.

Guarda una copia mediante `file.saveAs` y exporta a otro archivo mediante
`file.exportMedia` con `wait=true`, un formato compatible y audio cuando corresponda.
Examina `offlineMedia`: una lista no vacía significa que se exportaron placeholders.
Verifica fuera del editor con FFprobe y decodificación completa en FFmpeg.

Este servidor funciona sin ventana. Abre el `.fcproj` guardado en la aplicación
para revisión manual. No controla automáticamente una ventana abierta; bridge
requiere configurar aparte un canal local autenticado. El servidor tiene los permisos
del usuario y no confina rutas. El proyecto referencia archivos externos; guarda
los recursos de la entrega o un manifiesto de medios para evitar enlaces rotos.

Documentación oficial:
- https://github.com/storytold/filmcraft/blob/v0.14.0/docs/agents.md
- https://github.com/storytold/filmcraft/blob/v0.14.0/docs/control-protocol.md
