# Delegación y modelos — GPT / Codex / T3 Code

> Adaptación del documento de referencia para un flujo exclusivamente GPT. Esta es una política de trabajo, no una opción de configuración que T3 Code cargue automáticamente. Para que Codex la aplique en un repositorio, usa el `AGENTS.md` incluido y la configuración de Codex.
>
> **Lectura bajo demanda (fase 2):** Codex carga automáticamente `AGENTS.md`, no este archivo. La política ejecutable y breve vive en `~/.codex/AGENTS.md`. Lee este documento completo solo cuando la delegación sea extensa o compleja, no en cada tarea pequeña: releerlo entero en encargos S desperdicia contexto.

## Principio rector

El modelo principal orquesta y **delega solo cuando el beneficio supera el coste** de iniciar, coordinar y verificar otro agente. El objetivo es terminar tareas correctas, no multiplicar agentes. Un subagente recibe trabajo acotado y devuelve evidencia verificable. Se evita reabrir la misma tarea indefinidamente o llenar el contexto con logs innecesarios.

## Roles GPT

| Rol | Modelo recomendado | Esfuerzo inicial | Responsabilidad |
|---|---|---|---|
| Orquestador | `gpt-6.1-sol` (si está disponible) u otro GPT principal escogido en T3 Code | `high` según dificultad | Planifica, define límites, integra diffs y decide el cierre |
| Explorador | `gpt-6-luna` | `medium` | Identifica archivos, dependencias y riesgos; no edita |
| Implementador | `gpt-6-luna` | `medium` | Cambios pequeños, acotados, con comprobación |
| Verificador | `gpt-6-luna` | `medium` (`high` solo si la verificación es compleja y el cliente permite esfuerzo por ejecución) | Compara cambios contra el encargo, ejecuta pruebas; no edita |
| Investigador | `gpt-6-luna` | `medium` | Consulta fuentes concretas y cita rutas, líneas o URLs; no edita |
| Revisor crítico | `gpt-6.1-sol`, si está disponible | `high` | Revisa autenticación, seguridad, migraciones, pagos, datos reales o cambios amplios |

**Disponibilidad:** usa únicamente los modelos que realmente aparezcan en Codex/T3 Code y los niveles de razonamiento admitidos por cada uno. `xhigh` no es el valor universal para todo subagente: úsalo únicamente cuando su complejidad lo justifique.

## ¿Cuándo delegar?

Delega para exploraciones amplias, comprobación independiente, tareas separables o cambios en archivos disjuntos que realmente puedan adelantarse en paralelo. Trabaja directamente en el hilo principal cuando la corrección es pequeña, clara y verificable en pocos pasos.

**Límite inicial:** hasta **2 subagentes simultáneos por sesión Codex**. Considera además el total de sesiones T3 Code abiertas: seis hilos principales con dos subagentes cada uno podrían lanzar doce trabajadores. Esta regla no crea un límite global entre hilos distintos.

No delegues para delegar. No encadenes subagentes ni permitas que los trabajadores lancen otros agentes, salvo autorización explícita del orquestador. Los agentes que escriban sobre archivos compartidos trabajan en serie o en worktrees aislados.

## Contrato de cada tarea

Todo encargo debe incluir:

1. **Objetivo verificable:** resultado esperado y criterios de aceptación.
2. **Alcance:** rutas o módulos permitidos; lo que queda fuera.
3. **Contexto mínimo:** decisiones actuales, arquitectura y restricciones, no el transcript completo.
4. **Modelo y rol:** usa el perfil explícito disponible o confirma que Codex aplicó el modelo predeterminado.
5. **Validación:** comando(s) concretos, tests y evidencia requerida.
6. **Criterio de parada:** terminar cuando se cumpla el objetivo; si excede el alcance, devolver hallazgos y solicitar nuevo encargo.

Formato de cierre exigido:

- Estado: terminado / parcial / bloqueado.
- Archivos cambiados y resumen de cada cambio.
- Evidencia: pruebas ejecutadas y resultados (sin inventar ejecuciones).
- Riesgos o dudas pendientes.
- Próxima acción específica, si hace falta.

El orquestador **lee el diff real** y verifica los resultados. El informe del trabajador no es prueba suficiente.

## Clasificación y presupuesto

- **S:** cambio puntual en uno o pocos archivos, fácil de validar.
- **M:** funcionalidad delimitada en varios archivos, con pruebas.
- **L:** trabajo transversal o que requiere iteración. Primero dividir en S/M o investigar el alcance.

No copies la tabla de porcentajes del documento original: sus números eran estimaciones particulares de otro entorno, **no tarifas ni consumos oficiales de GPT**. Tampoco asumas que `agent-budget` o `delegate_task` existen en tu instalación: son herramientas externas o integraciones que debes verificar antes de usarlas.

Antes de lanzar más agentes, revisa cuotas reales cuando estén disponibles, número de subagentes activos, riesgo de solapamiento y valor de paralelizar. Si la cuota o el contador no se puede consultar, decláralo y elige delegación conservadora.

## Contexto y compactación

**Importante:** los umbrales de 80.000 y 100.000 tokens del `models.md` original correspondían a **Haiku/Claude** y a su política de precios. **No son límites de GPT.**

- El orquestador mantiene el hilo principal breve; los agentes reciben únicamente contexto relevante, preferentemente rutas, símbolos y diffs acotados.
- Evita `cat`/logs masivos, búsquedas sin filtros y reiterar pruebas completas si basta un test dirigido.
- Cuando Codex informe ocupación de contexto, empieza a preparar un handoff alrededor del **60–70 %** de su ventana **como umbral operativo recomendado, no como límite del proveedor**.
- Si un agente ya compactó, reevalúa si conviene cerrarlo y continuar con un encargo limpio. Si se producen **compactaciones repetidas** sin progreso verificable, termina el encargo y abre otro con resumen.
- No configures una ventana ficticia ni un límite automático de compactación fijo sin conocer el tamaño de contexto compatible con el modelo y la versión instalada. Dejar las opciones de compactación de Codex en sus valores predeterminados es un buen punto de partida.
- El handoff conserva objetivo, rama, archivos modificados, decisiones, tests, resultados y pendientes; **no presume que un subagente nuevo vea automáticamente el chat anterior**.
- **Lectura de contadores T3 Code (medido 2026-10-14 en este equipo):** el evento `context-window.updated` publica `usedTokens` (contexto activo), `totalProcessedTokens` (acumulado histórico del hilo) y `maxTokens` (ventana, ~475.000 observados). El máximo acumulado visto fue ~135M frente a un máximo activo de ~351k, con compactaciones registradas de ~155k → ~14k. Conclusión operativa: una cifra de millones es consumo acumulado, nunca ventana activa; no la uses para decidir compactación ni coste de un subagente concreto.

## Flujo de ejecución

1. **Orquestador:** entiende el pedido y decide trabajo directo o delegación. Comunica la división si delega.
2. **Explorador Luna (opcional):** ubica los lugares exactos sin editar.
3. **Implementador(es) Luna:** hasta dos independientes por sesión y con propietarios de archivos no superpuestos.
4. **Verificador Luna:** ejecuta o inspecciona las pruebas pertinentes y solo reporta.
5. **Revisor Sol (condicional):** seguridad, auth, permisos, migraciones, datos reales, pagos, PR o cambios especialmente sensibles.
6. **Orquestador:** verifica el diff, resuelve problemas y entrega el resultado; no asume que `file change` significa éxito.

No hagas una revisión Sol para todos los cambios triviales. No hagas bucles ilimitados de implementación → revisión → corrección. En general, una ronda de correcciones; si hay defectos persistentes, replantea el plan.

## Integración con Codex y T3 Code

- Codex descubre `AGENTS.md` (global o de proyecto). Un archivo llamado `models.md` **no se carga automáticamente**, salvo que otra instrucción o herramienta lo lea.
- `~/.codex/config.toml` o la configuración del proyecto puede definir `agents.default_subagent_model = "gpt-6-luna"`, el esfuerzo predeterminado y `agents.max_concurrent_threads_per_session`.
- Los perfiles TOML en `~/.codex/agents/` o `.codex/agents/` describen agentes especializados. Su selección **depende de la versión y de la interfaz de `spawn_agent` que exponga Codex**.
- **Limitación de esfuerzo por ejecución (fase 2):** cada perfil TOML fija un único `model_reasoning_effort` (p. ej. `luna_verifier` usa `medium`). Cambiarlo para un encargo concreto requiere un valor explícito de spawn (`agent_type`/`model`/`reasoning_effort` en la invocación), y eso solo funciona si el cliente (T3 Code) lo expone — en esta instalación está `NO VERIFICADO`. No existe un mecanismo por perfil para "medium normalmente, high a veces": por eso el default seguro es `medium` y `high` queda reservado a encargos donde se pida explícitamente y el cliente lo acepte.
- Si no se define ni modelo predeterminado ni modelo del agente, este puede heredar el del padre.
- La capa gráfica de T3 Code no es garantía de que un contador de tokens sea consumo adicional de ese subagente: contrasta con el transcript y las estadísticas de uso antes de sacar conclusiones.
- Para Orchestrator V2 revisa la versión de Codex exigida por T3 Code, actualiza cliente/servidor y prueba en un hilo nuevo. **No cambies flags de MultiAgent V2 a ciegas**: primero comprueba la interfaz de spawn expuesta.

## Semáforos para intervenir

- **Verde:** tarea completada, pruebas evidenciadas, cambios acotados, sin compactación repetida.
- **Amarillo:** progreso lento, múltiples ejecuciones, salida excesiva, números de tokens inexplicables o primera compactación; revisar transcript y tiempo antes de continuar.
- **Rojo:** compactaciones sucesivas sin avances, ciclos de correcciones, agente trabajando fuera de alcance o varios agentes cambiando los mismos archivos; detener, revisar diff, dividir tarea y relanzar con contexto limpio.

**No interpretar el color de un evento en la UI como diagnóstico de fallo sin abrir sus detalles.**

## Auditoría y medición

Para comprobar que mejora:

1. Mide una tarea S y una M **antes** y **después** (mismo repositorio, alcance y criterios).
2. Registra modelo real utilizado, nivel de razonamiento, agentes simultáneos, tiempo, compactaciones y resultado de tests.
3. Separa `contextTokens` (ocupación actual), `totalProcessedTokens` (si lo ofrece el proveedor) y consumo atribuible al subagente. Evita sumar contadores heredados del padre.
4. Cuenta retrabajos y colisiones de archivos. La velocidad sin pruebas válidas no es éxito.
5. Si la UI informa millones de tokens, contrasta datos de Codex y versión de T3 Code antes de atribuirlos a un prompt defectuoso.
6. Conserva una muestra del transcript/evento de `spawn_agent` para confirmar el `model` y `reasoning_effort` efectivos.

**Criterio de éxito:** menos agentes innecesarios, menos compactaciones repetidas, menos duplicación de trabajo, igual o mejor tasa de tests aprobados y menor tiempo/consumo **verificado**, no solo menor número visual en T3 Code.

## Fuentes técnicas consultadas (14-10-2026)

- Codex subagents: https://developers.openai.com/codex/subagents
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- T3 Code V2: https://github.com/pingdotgg/t3code/issues/14871
- T3 Code contadores Codex: https://github.com/pingdotgg/t3code/issues/5793
- T3 Code contadores Claude: https://github.com/pingdotgg/t3code/issues/14003
- Codex MultiAgent V2 / selección de perfiles: https://github.com/pingdotgg/t3code/issues/3875
