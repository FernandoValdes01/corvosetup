# Verificación del visor teach

## Comandos

```bash
PROJECT=/ruta/al/proyecto

python3 "$HOME/.codex/skills/teach-project/scripts/install.py" "$PROJECT"
python3 "$HOME/.codex/skills/teach-project/scripts/validate_tutorial.py" "$PROJECT"
python3 "$HOME/.codex/skills/teach-project/scripts/smoke_test.py" "$PROJECT"

"$PROJECT/teach" fases
"$PROJECT/teach" archivos
"$PROJECT/teach" dudas
"$PROJECT/teach" guia --no-abrir
```

`install.py` es idempotente: actualiza el motor y el lanzador, conserva `tutorial.json`, `diagramas/` y `.teach/state/`, y agrega o actualiza el bloque gestionado de `teach-project` en `.gitignore`. Ese bloque debe ignorar `/teach`, `/.teach/`, `/tutorial.json` y `/diagramas/` sin tocar las demás reglas. `smoke_test.py` usa un directorio de estado temporal, así que no altera el progreso real.

## Qué comprueba el smoke test

- `GET /api/bootstrap` responde 200 y entrega exactamente los archivos declarados.
- Una visita guarda fase y scroll.
- Una duda se registra y aparece en `/api/export`.
- Marcar una fase como leída no borra dudas.
- `clear_doubts` borra solo dudas, no fases ni posición.
- `close` exporta `dudas-tutorial.md` y detiene el servidor.

## Checklist manual del navegador

1. La barra lateral muestra título, objetivo, progreso y todas las fases.
2. El lector muestra el relato de la fase, el diagrama si existe y los archivos de la fase.
3. ←/→ cambia de fase; ↑/↓ desplaza; Enter abre el primer archivo relacionado.
4. En el archivo completo, ←/→ cambia de archivo, ↑/↓ desplaza y Enter vuelve a la explicación.
5. **Marcar fase leída** actualiza el contador y persiste al recargar.
6. **Mis dudas** abre el panel; Enter envía y Shift+Enter agrega una línea.
7. **Limpiar** borra solo dudas; **Copiar** produce la instrucción para el agente; **Descargar .md** baja el archivo.
8. Recargar conserva fase, scroll, fases leídas y dudas.
9. **Pausar y salir** guarda y muestra el resumen exportable.
10. A ~390 px el panel de dudas se abre con el botón y se cierra con Escape.
11. Con `prefers-reduced-motion: reduce` no hay animaciones.
12. Los diagramas se ven, tienen pie y abren a tamaño completo.
13. `.gitignore` contiene el bloque gestionado con `/teach`, `/.teach/`, `/tutorial.json` y `/diagramas/`.

## Rutas y seguridad

- Servidor solo en `127.0.0.1`, puerto libre, token en la URL y cabecera `X-Teach-Token`.
- Verifica `Host` y `Origin`; no expongas el visor en la red.
- Solo sirve archivos declarados en `tutorial.json`; bloquea rutas ocultas, `..` y symlinks que salgan del proyecto.
- Límite de 300 KB por archivo y 4000 caracteres por duda.
- Estado en `.teach/state/tutorial-progress.json` con permisos privados.
- La exportación vive en `.teach/state/dudas-tutorial.md`.
- Nunca agregues credenciales, tokens, llaves privadas, discos, snapshots ni exports de máquinas.

## Fallos frecuentes

| Síntoma | Causa probable | Acción |
| --- | --- | --- |
| `No pude abrir o guardar el tutorial` | `tutorial.json` ausente o inválido | Ejecutar el validador y revisar el mensaje. |
| `El visor solo expone archivos...` | Ruta oculta, fuera del proyecto o symlink externo | Corregir `files[].path`. |
| `El archivo ... supera el tamaño permitido` | Archivo mayor de 300 KB | Citar un fragmento en un archivo menor o dividir el archivo. |
| `La fase no pertenece a esta guía` | Acción con `phase` inexistente | Revisar el estado guardado y reiniciar el progreso si es corrupto. |
| El código se ve desalineado | `lines` no coincide con el archivo actual | Corregir el rango y revalidar. |
| El diagrama da 404 | `file` no es un nombre dentro de `diagramas/` | Mover la imagen y actualizar `story.visual.file`. |
| La página no carga en el navegador | Se abrió sin token o desde otro host | Usar la URL completa que imprime `teach guia`. |
| El progreso no se guarda | `.teach/state` sin permisos | Revisar permisos y ejecutar de nuevo. |

## Entrega

Reporta:

- Ruta de `tutorial.json` y cantidad de fases/archivos/fuentes.
- Resultado real del validador y del smoke test.
- Si abriste el navegador y qué flujos comprobaste.
- Limitaciones: diagramas no renderizados, navegador no disponible, contenido no verificado, etc.
- Comando para abrir: `./teach`.
