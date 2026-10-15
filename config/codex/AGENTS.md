# Autorización permanente para delegar subagentes GPT (T3 Code + Codex)

- El usuario autoriza de forma permanente al orquestador a crear subagentes GPT cuando aporten una ventaja técnica concreta dentro de la tarea solicitada. No pedir autorización adicional por cada delegación normal.
- Esta autorización no amplía el alcance pedido, no cede el control general de la tarea y no relaja los controles de aprobación para operaciones sensibles.
- La autorización para crear un agente no se transmite a ese agente. Un subagente solo crea agentes descendientes con autorización explícita para ese encargo.
- Nunca asignes a un agente un modelo de mayor capacidad que el tuyo. Por ejemplo, Luna no puede crear agentes Sol ni Astra, y Sol no puede crear agentes Astra.
- Límites permitidos para un agente Sol: puede crear agentes Luna con esfuerzo de razonamiento hasta `xhigh`, y agentes Terra hasta `medium`.
- Un agente Luna nunca puede crear agentes Terra, sin importar el esfuerzo de razonamiento. Este límite no tiene excepciones.
- Fuera de los límites indicados, no supongas que una combinación de modelo y esfuerzo está permitida. Trabaja sin delegar o pide instrucciones al usuario.

<!-- frontend-web-skills:start -->
## Skills para frontend y pruebas web

- Al desarrollar o modificar frontend, carga y aplica `design-taste-frontend` e `impeccable` automáticamente. Respeta el alcance pedido y el sistema de diseño existente. En dashboards, tablas y flujos de producto, usa Impeccable como guía principal y aplica solo las recomendaciones de Taste compatibles con ese contexto.
- Para verificar tareas web o cambios visibles en el navegador, carga `playwright-skill` automáticamente y ejecuta comprobaciones proporcionales al cambio. Comprueba los flujos afectados y el comportamiento responsive cuando corresponda. Reporta resultados reales y cualquier impedimento para ejecutar las pruebas.
<!-- frontend-web-skills:end -->

<!-- communication-coding-skills:start -->
## Skills automáticas para comunicación y programación

- Carga y aplica `i-have-adhd` automáticamente desde el inicio de cada sesión y al redactar respuestas. Empieza por la respuesta o acción concreta, divide pasos cuando corresponda y evita rodeos. Explica con detalle cuando se pida. Respeta la desactivación mediante "stop adhd mode" o "normal mode" durante esa sesión.
- Carga y aplica `ponytail` automáticamente en tareas de programación, correcciones, refactorizaciones, revisiones y decisiones de dependencias. Usa el nivel `full` por defecto y busca la solución mínima que complete todo lo pedido, preservando seguridad, validación, accesibilidad y manejo de errores. Respeta los cambios de nivel y la desactivación que indique el usuario.
<!-- communication-coding-skills:end -->

<!-- gpt-subagents-fase2:start (2026-10-14, optimización fase 2) -->
# Política de delegación GPT / Codex (T3 Code)

Solo modelos GPT. Orquestador: el modelo elegido en T3 Code. Subagentes: `gpt-6-luna` por defecto (`medium`); `gpt-6.1-sol` (`high`) solo para revisión de alto riesgo. Detalle ampliado en `~/.codex/models_gpt.md`: leerlo únicamente cuando la delegación sea extensa o compleja, no en cada tarea pequeña (Codex no lo carga automáticamente).

## Cuándo delegar

- Exploración amplia, investigación acotada o verificación independiente que ahorre tiempo real al hilo principal.
- Tareas separables en paralelo con archivos o ámbitos disjuntos.
- Cada encargo lleva objetivo verificable, alcance con rutas permitidas, contexto mínimo, validación concreta y criterio de parada.

## Cuándo no delegar

- Correcciones triviales o verificables en pocos pasos: trabajar directo e indicarlo.
- Para investigar exactamente lo mismo que otro subagente activo (evitar duplicados).
- Si el aporte no supera el coste de coordinar y verificar: no delegar para delegar.

## Roles y esfuerzo

- `luna_explorer` (Luna, `medium`): explora e investiga; no edita.
- `luna_worker` (Luna, `medium`): implementa lo encargado con pruebas puntuales; solo sus archivos asignados.
- `luna_verifier` (Luna, `medium`; `high` solo si la verificación es compleja y el cliente permite esfuerzo por ejecución): inspecciona diffs y pruebas; no edita.
- `sol_reviewer` (Sol 6.1, `high`): solo alto riesgo (auth, seguridad, migraciones, pagos, cambios estructurales delicados, revisión final de cambios extensos). Nada rutinario.
- Si los perfiles no son seleccionables en T3 Code, rigen los valores predeterminados (`gpt-6-luna`/`medium`); comprobar el modelo real y nunca fingirlo.
- Las restricciones de lectura/escritura son instrucciones de comportamiento, no un sandbox aislado.

## Paralelismo y archivos

- Máximo 2 subagentes simultáneos por sesión (configurado); ese límite es por sesión, no global: coordinar entre sesiones T3 Code que compartan repositorio.
- Un solo escritor a la vez por checkout compartido; el segundo agente en paralelo debe ser explorador o verificador sin conflictos.
- Dos escritores simultáneos solo con worktrees o separación de archivos comprobada.
- No sobrescribir cambios ajenos; no hacer reset, checkout destructivo ni limpiezas que borren trabajo existente.

## Verificación y cierre

- Todo subagente cierra con estado (terminado/parcial/bloqueado), archivos, evidencia de pruebas, riesgos y pendientes; sin inventar ejecuciones.
- El orquestador revisa el diff y el resultado real antes de aceptar; el informe no es evidencia.
- Una ronda de correcciones; si persisten defectos, nuevo diagnóstico y plan, no bucles ilimitados.

## Contexto y consumo

- Investigar solo rutas relevantes; búsquedas dirigidas antes que lecturas extensas; no repetir herramientas que ya respondieron.
- Dividir tareas grandes en entregables verificables; ante ciclo sin progreso, detener y reportar bloqueo; no relanzar agentes estancados ni reiniciar lo ya logrado: handoff con resumen.
- Una compactación aislada no es fallo; ante compactaciones repetidas sin avance, cerrar con handoff y reencargar en pequeño.
- Los contadores de T3 Code mezclan consumo acumulado (`totalProcessedTokens`), contexto activo (`usedTokens`) y ventana (`maxTokens`, ~475k medidos): no deducir coste ni contexto actual de una sola cifra. Sin umbrales 80k/100k de Claude.
<!-- gpt-subagents-fase2:end -->
