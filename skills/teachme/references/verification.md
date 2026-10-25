# Verificación del visor teach

## Comandos

Al modificar la skill o el contrato de contenido, ejecuta también `python3 scripts/test_content_contract.py` desde la carpeta de la skill. Comprueba `result`, compatibilidad con `transfer`, validación del glosario y lectura de terminal sin imagen. No evalúa la calidad pedagógica; esa requiere revisar el relato y sus ejemplos.

```bash
PROJECT=/ruta/al/proyecto

python3 "$HOME/.codex/skills/teachme/scripts/install.py" "$PROJECT"
python3 "$HOME/.codex/skills/teachme/scripts/validate_tutorial.py" "$PROJECT"
python3 "$HOME/.codex/skills/teachme/scripts/smoke_test.py" "$PROJECT"

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

## Checklist de contenido

1. La primera fase desarrolla el encargo: qué se pidió, para quién, qué implica, qué límites había y cómo se reconoce el éxito. No es una introducción de dos líneas.
2. El cómo aparece después del encargo; cada cierre explica qué produce el código o la infraestructura. La fase final conecta entradas, salidas o cambios de estado, evidencia y límites.
3. El pedido original y lo inferido están distinguidos; no se inventa la intención.
4. Los conceptos y las siglas se explican antes de usarlos. El glosario inicial, si hace falta, define cada término con un ejemplo del proyecto y también aparece en el modo texto.
5. Las decisiones explican el mecanismo y sus consecuencias; las diferencias entre modelos o componentes tienen una razón comprensible. El aprendizaje general surge de ese razonamiento, sin un apartado de transferencia.
6. Los ejemplos didácticos, resultados esperados y ejecuciones observadas se distinguen. No se confunde un documento terminado o el progreso de lectura con el efecto operativo del proyecto.
7. Los flujos, relaciones o comparaciones difíciles de seguir tienen el apoyo visual apropiado y texto que enseña a leerlo. Las definiciones simples no llevan diagramas de relleno.
8. Las dificultades tienen evidencia; no se inventan incidentes. Las limitaciones de evidencia acompañan al resultado o al alcance.
9. Se buscaron y abrieron los recursos gráficos existentes en documentación, informes, resultados y notebooks relevantes. Las figuras pertinentes se muestran y explican en el lector con origen identificado; una ruta o enlace no basta. Cualquier omisión tiene una razón de alcance, vigencia, duplicación o un impedimento concreto.
10. Si faltaba material gráfico adecuado, se decidió qué crear según el tema, con preferencia por gráficos o dibujos para ejemplos matemáticos y diagramas para infraestructura, DevOps y diseño de sistemas. No se impone una cuota a todas las fases.
11. Si comprender el funcionamiento depende de las relaciones o ubicaciones entre carpetas, el flujo está representado y se explica quién consume cada ruta, cómo la resuelve y qué cambia al moverla. Se distingue requisito técnico de convención.
12. Los recursos gráficos originales permanecen intactos y conservan su seguimiento en Git. Las copias del teach no los sobrescriben, mueven ni retiran del índice.

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
14. El glosario se lee en la primera fase y los párrafos extensos se separan. En una guía nueva el cierre muestra el resultado; una guía antigua con `transfer` muestra "Cierre de la guía anterior", sin presentarlo como evidencia de ejecución.
15. Las figuras reutilizadas cargan en el lector y su pie identifica el origen. Los gráficos conservan ejes, leyendas y valores legibles; los diagramas de carpetas o despliegue permiten seguir las relaciones descritas en el texto.

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
| El diagrama da 404 | `file` no es un nombre dentro de `diagramas/` | Copiar la imagen a un nombre libre dentro de `diagramas/`, conservando la fuente, y actualizar `story.visual.file`. |
| La página no carga en el navegador | Se abrió sin token o desde otro host | Usar la URL completa que imprime `teach guia`. |
| El progreso no se guarda | `.teach/state` sin permisos | Revisar permisos y ejecutar de nuevo. |

## Entrega

Reporta:

- Ruta de `tutorial.json` y cantidad de fases/archivos/fuentes.
- Resultado real del validador y del smoke test.
- Si abriste el navegador y qué flujos comprobaste.
- Limitaciones: diagramas no renderizados, navegador no disponible, contenido no verificado, etc.
- Comando para abrir: `./teach`.
