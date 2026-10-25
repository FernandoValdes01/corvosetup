---
name: teachme
description: >-
  Construye e instala una guía web local por fases que reconstruye el encargo,
  enseña las decisiones sin asumir conocimientos previos y muestra qué produce
  el código o la infraestructura, con ejemplos, diagramas, progreso y
  panel de dudas. No responde en el chat con un resumen: el entregable
  es `tutorial.json` y el visor `./teach`. Úsala solo cuando el usuario invoque
  `$teachme` o pida explícitamente un teach o un recorrido guiado navegable
  ("enséñame de este proyecto", "hazme un teach"); no la uses para preguntas sueltas.
---

# Construir el visor teach de un proyecto

## Directiva primaria

Esta skill no responde preguntas: construye un artefacto. Si se activa, tu trabajo es dejar en el proyecto `tutorial.json`, `diagramas/` y `teach` funcionando. No es aceptable contestar con una explicación, un mapa de archivos, una tabla de resultados ni un "resumen del proyecto", aunque el usuario haya dicho "enséñame".

La lectura del repositorio es para obtener evidencia para `tutorial.json`, no para producir una respuesta en el chat.

## Contrato de invocación

Si el usuario invoca `$teachme` o pide un teach:

1. No respondas **en el chat** con el contenido del proyecto.
2. No empieces por el README para resumirlo en el chat. Úsalo, junto con el enunciado, los issues, los commits y las pruebas, para reconstruir qué se pidió y qué implica.
3. Ejecuta `install.py` y crea o actualiza `tutorial.json` antes de redactar una respuesta larga.
4. Si no puedes escribir en el proyecto, dilo y detente; no improvises la guía en el chat ni entregues un resumen como consuelo. No uses "no puedo escribir" como excusa si tienes herramientas de escritura: solo detente si un intento real de escritura falla y muestra el error.
5. El `tutorial.json` sí debe desarrollar el encargo: qué se solicitó, para quién, con qué restricciones y qué implica, antes de explicar el cómo y el resultado.
6. Tu respuesta final es solo el acuse de entrega del criterio de terminado.

El único mensaje permitido antes de terminar es un aviso de una línea, por ejemplo: "Voy a crear la guía; no voy a resumir el proyecto". No envíes "avances" con arquitectura, hallazgos, tablas de métricas ni mapas de archivos.

No confundas "no resumir en el chat" con "no explicar el problema en la guía". La guía empieza por el encargo; el chat no. Si te encuentras escribiendo "Aquí tienes un resumen", "El proyecto se compone de", "Mapa de archivos" o una explicación de arquitectura **en la respuesta**, estás fuera del contrato: detente y crea los archivos.

Activa esta skill solo cuando el usuario invoque `$teachme`, diga **"enséñame de este proyecto"**, "hazme un teach de esto", "quiero un recorrido guiado del proyecto" o "revísalo conmigo paso a paso". No la uses para un resumen corto ni para una pregunta puntual: para eso responde directamente sin activar la skill.

Pedir editar, analizar o corregir esta skill no activa la construcción de un teach. En ese caso modifica la skill y sus recursos según el encargo.

La skill instala en el proyecto el mismo visor que ya funciona en `evaluacionpractica02`: servidor local con token, fases navegables, código real con líneas, diagramas, progreso guardado, panel **Mis dudas**, copiar/descargar/limpiar y exportación para el agente. El resultado se abre con `./teach` desde la raíz del proyecto.

## Forma de enseñar

Escribe como alguien entusiasmado con su área que quiere que la otra persona entienda y conserve lo aprendido. Ese interés se nota al explicar el mecanismo, escoger un ejemplo útil y anticipar una duda, sin elogios vacíos ni tono infantil. No asumas que conoce siglas, bibliotecas, conceptos del dominio ni nombres creados para este proyecto.

- Abre con preguntas cercanas: "¿Qué se nos pidió?", "¿Qué decisiones tomamos y por qué?", "¿Cómo lo hace el código?" y "¿Qué produce al ejecutarse?". Desarrolla las respuestas; los títulos no reemplazan la explicación.
- Ante cada concepto nuevo explica qué es, qué papel cumple aquí y un ejemplo concreto antes de usarlo para justificar otra decisión. Incluye al principio un glosario breve de los conceptos necesarios en `story.glossary`, dentro de la fase del encargo, después de presentar el problema. Introduce los demás al necesitarlos; el glosario no sustituye la explicación contextual.
- Conecta necesidad → concepto → decisión → mecanismo → efecto. Si dos modelos o componentes reciben tratamientos distintos, explica qué diferencia de funcionamiento lo justifica y qué pasaría si aplicaras lo mismo a ambos.
- Usa ejemplos pequeños de entrada, transformación y salida. Marca los ejemplos didácticos como tales; no los presentes como mediciones del proyecto. Simplifica el lenguaje sin deformar la explicación técnica.
- El aprendizaje general surge del razonamiento, las alternativas y sus consecuencias. No agregues una sección de "transferencia", "cómo llevarlo a otro proyecto" ni consejos genéricos de adaptación. Cada fase cierra con `story.result`: qué produce o habilita el código o la infraestructura, con evidencia y límites.

Lee `references/content-playbook.md` antes de redactar: contiene el patrón de explicación, un ejemplo desarrollado y los criterios para elegir texto, ejemplos y diagramas.

## Reconstruir el encargo antes del código

La guía no empieza por la arquitectura ni por un README resumido. Empieza por el problema: qué se pidió, para quién, en qué contexto, con qué restricciones y qué implica resolverlo. Sin eso, el lector ve cómo funciona algo pero no entiende por qué existía la necesidad ni qué se estaba tratando de conseguir.

Antes de diseñar fases, armá un brief interno (no lo vuelques en el chat) que responda:

- **Pedido original**: qué se solicitó, con qué palabras y para qué.
- **Audiencia y contexto**: quién lo pidió, quién lo usa y en qué situación.
- **Problema**: qué fallaba, qué faltaba o qué había que cambiar.
- **Implicaciones**: qué piezas toca, de qué depende, qué riesgo o costo introduce.
- **Restricciones**: stack, datos, seguridad, compatibilidad, tiempo o decisiones ya tomadas.
- **Criterio de éxito**: cómo se reconoce que el pedido quedó resuelto.
- **Ambigüedades y supuestos**: qué no estaba claro y cómo se interpretó.
- **Fuera de alcance**: qué no se pidió o qué quedó explícitamente afuera.

Buscá evidencia en el enunciado de la tarea, `README`, `docs/`, issues, mensajes de commit, pruebas, esquemas, configuración y textos de interfaz. Distinguí siempre lo **explícito** de lo **inferido**. Si el pedido original no está en el repositorio, decilo: "El repositorio no conserva el enunciado; esto se infiere de...". No inventes intención ni historia.

Ese brief se convierte en la **primera fase** de la guía, no en una introducción de dos líneas. El pedido abre; las implicaciones, restricciones y criterios de éxito se desarrollan. El cómo y el resultado vienen después.

## Resultado esperado

En la raíz del proyecto deben quedar:

```text
tutorial.json          # contenido: fases, archivos, fuentes y relato
teach                  # lanzador ejecutable
.teach/engine/         # motor copiado desde esta skill
.teach/state/          # progreso y dudas locales
diagramas/             # SVG/PNG reutilizados o creados para las fases, cuando corresponda
.gitignore             # bloque gestionado con todos los artefactos anteriores
```

Los artefactos nuevos del teach son locales: el instalador los agrega a `.gitignore` dentro de un bloque gestionado. Conserva los recursos originales del proyecto, incluidos los gráficos o diagramas que ya estuvieran versionados; reutilizarlos no los convierte en artefactos desechables del teach.

No modifiques el código del proyecto para "prepararlo". El visor solo lee archivos públicos declarados en `tutorial.json`; no ejecuta el proyecto, no instala dependencias y no toca sus servicios. Esta skill reproduce el recorrido educativo de `teach`, no los subcomandos operativos `teach lab` que pertenecen a los laboratorios originales.

## Flujo obligatorio

### 0. Instalar el motor antes de investigar

Ejecuta primero el instalador para que el proyecto ya tenga `teach`, `.teach/engine/` y el bloque de `.gitignore`. No esperes a terminar la investigación para crear archivos: el teach se construye sobre el disco, no en el chat.

```bash
PROJECT=/ruta/al/proyecto
python3 "$HOME/.codex/skills/teachme/scripts/install.py" "$PROJECT"
```

Si ya existe `tutorial.json`, no lo sobrescribas a ciegas: léelo, decide si es una actualización y conserva `.teach/state/`.

### 1. Reconstruir el encargo

Antes de leer la arquitectura, reconstruí el problema con la evidencia disponible:

- Enunciado de la tarea, `README`, `docs/`, `CONTRIBUTING` e issues.
- `git log --oneline -20` y `git status` para ver qué se cambió y en qué orden.
- Pruebas, esquemas, configuración y textos de interfaz que revelen el comportamiento esperado.
- Lo que el usuario ya dijo en la conversación; no lo ignores ni lo reemplaces por tu interpretación.

Escribí el brief interno de la sección anterior: pedido, audiencia, problema, implicaciones, restricciones, criterio de éxito, ambigüedades y fuera de alcance. Marcá qué es explícito y qué es inferido.

La primera fase de `tutorial.json` sale de ese brief. No es un resumen del README ni una "Introducción" genérica: es la reconstrucción del encargo con evidencia. Si el pedido es ambiguo, decilo en la guía y explicá cómo lo interpretaste.

### 2. Reconocer el proyecto antes de escribir

Lee, sin modificar:

- Puntos de entrada, configuración, esquemas, migraciones, pruebas y CI.
- Los archivos que piensas citar, con sus líneas exactas.
- La relación entre el pedido reconstruido y las piezas que lo implementan.

**Busca material gráfico antes de redactar.** Revisa las imágenes enlazadas en README y documentación y los directorios de informes, resultados, notebooks, figuras, arquitectura e infraestructura que existan. Busca imágenes y fuentes como SVG/PNG/JPEG/WebP, Mermaid, draw.io y figuras incrustadas en notebooks o documentos. No te limites a los archivos de código ni a una carpeta llamada `diagramas/`. Abre los candidatos relevantes y comprueba qué explican y si corresponden a la versión o ejecución estudiada. Las figuras existentes que expliquen el flujo, las decisiones o los resultados del recorrido **deben mostrarse y explicarse en la guía**, no solo mencionarse o reemplazarse por citas de código. Descarta material ajeno al alcance, decorativo, duplicado o desactualizado con una razón concreta. Registra internamente origen → fase → uso o motivo de descarte. Aplica el procedimiento de reutilización del playbook.

Construye una tabla mental de evidencia: afirmación → archivo:línea o fuente oficial. Si algo no está en el repositorio, no lo presentes como implementado.

No hagas un inventario exhaustivo. Para un repositorio mediano bastan el README, los puntos de entrada, la configuración, las pruebas y entre 10 y 15 archivos. Si el repositorio es enorme, acota el flujo principal en `scope` y sigue; no leas todo antes de escribir.

### 3. Diseñar las fases

Aplica el arco narrativo del teach existente:

```text
qué se necesitaba → cómo se interpretó → qué se decidió → cómo lo hace el código
→ por qué se descartaron alternativas → qué dificultades hubo → qué produce al ejecutarse
```

Reglas:

- Entre **6 y 10 fases** para un proyecto completo (el validador acepta 2–12; menos de 5 es un aviso fuerte).
- Cada fase resuelve **un problema técnico concreto**, no un capítulo genérico ("Introducción", "Instalación").
- La **primera fase es el encargo**: reconstruye qué se pidió, para quién, con qué límites y qué implica. No es una introducción vacía ni un resumen del README; usa 3–4 bloques y cita la evidencia del encargo (enunciado, README, issues, pruebas).
- Las fases siguientes explican el **cómo**, introduciendo los conceptos al necesitarlos. La última muestra el **resultado verificable** del proyecto ejecutado: entradas, salidas o cambios de estado, cómo se comprueban y qué límites tienen. En la fase inicial, el resultado describe el comportamiento esperado y su criterio de aceptación, sin afirmar que ya ocurrió.
- Cada fase se apoya en evidencia real. Enlaza **1–4 archivos de texto** cuando sostengan la explicación: código, documentación, pruebas o configuración. Una fase de resultados también puede apoyarse en gráficos existentes con origen identificado; no fuerces fragmentos de código para reemplazar evidencia gráfica. Las imágenes van en `story.visual`, no en el catálogo `files` reservado a texto.
- Distribuye: encargo y conceptos necesarios, arquitectura, flujo de datos, decisiones, piezas críticas, dificultades documentadas y resultado/verificación. El aprendizaje reutilizable se desarrolla dentro de estas explicaciones.
- No empieces por la arquitectura: aparece cuando el encargo ya está claro. Español por defecto; conserva el idioma del proyecto solo si el usuario lo pide.

Lee `references/content-playbook.md` para la plantilla de fase, los criterios de calidad y ejemplos.

### 4. Escribir `tutorial.json`

Usa el esquema completo de `references/schema.md`. Mínimo por fase:

- `id` estable en kebab-case, `title`, `flow` (3–5 pasos) y `sections` (2–4) para el modo texto.
- En la primera fase, `sections` debe tener al menos tres bloques: qué se pidió, qué implica y límites/criterio de éxito.
- `story.request`, `interpretation`, `decision`, `result`. En guías nuevas usa `result`; `transfer` solo se acepta por compatibilidad con guías anteriores y se muestra como un cierre antiguo, no como evidencia de ejecución.
- `story.glossary`, cuando haya conceptos que introducir: lista de `{term, explanation}`. En cada explicación define el término con lenguaje simple y vincúlalo con un ejemplo del proyecto. Replica esos conceptos en `sections` para el modo texto.
- En la fase del encargo, `story.request` abre con el pedido y `story.interpretation` desarrolla el contexto, las implicaciones y los criterios de éxito. No pongas todo en `request` ni dejes el contexto solo en `sections`: el visor web prioriza `story`.
- `story.alternatives` (al menos una con `name` y `tradeoff`). En el encargo, compará interpretaciones posibles del pedido.
- `story.walkthrough` (2–5 pasos con `file` y `lines` reales). En el encargo, puede recorrer el enunciado, el README o las pruebas que sostienen el pedido.
- `story.difficulties` con dificultades y resoluciones respaldadas por evidencia; puede estar vacío. Distingue un riesgo posible de un fallo ocurrido. En el encargo, registra ambigüedades o requisitos que chocaban si los hay. Las salvedades sobre la evidencia pertenecen al alcance o al resultado, no son dificultades técnicas por sí solas.
- `story.visual` cuando haya material gráfico existente relevante o se decida crear un apoyo nuevo; `file` es el nombre del SVG/PNG real dentro de `diagramas/`. Su pie identifica el origen si es reutilizado. El listado `flow` con flechas de texto no reemplaza una figura que deba mostrarse.
- `files` con `path`, `purpose`, `used_when`, `explanation`, `parameters` y `lines`.
- `sources` con documentación oficial y `consulted` (fecha). No uses tutoriales secundarios.
- `scope` debe decir qué **no** cubre la guía y qué evidencia es histórica.

El contenido debe permitir explicar las decisiones y anticipar sus efectos. `story.result` conecta una entrada concreta con la salida o el cambio de estado que produce el fragmento citado: predicciones en ML, respuestas y escrituras en una aplicación, o recursos y conectividad en infraestructura. Distingue "el repositorio implementa esto", "esto se observó en una ejecución", "esta salida es esperada y no se ejecutó" y "este ejemplo es didáctico". Un documento entregado, casillas marcadas o el progreso del teach no demuestran el resultado operativo. No ejecutes servicios ni despliegues para completar el relato; si falta evidencia de ejecución, indica el resultado esperado, cómo comprobarlo y qué no se verificó.

### 5. Reutilizar material gráfico y decidir qué crear

Primero incorpora el material existente que sea pertinente y fiable: su uso es obligatorio aunque la misma idea también se pueda describir en texto. Una ruta citada o un enlace a la imagen no equivale a mostrarla en el lector. Si no hay material adecuado, el modelo decide si crea diagramas o gráficos según el tema y el valor didáctico, sin una cuota universal. La preferencia es usar gráficos o dibujos en ejemplos matemáticos y diagramas en infraestructura, DevOps y diseño de sistemas. Para dependencias entre carpetas o módulos, representa el flujo cuando su relación sea necesaria para entender el funcionamiento. Una definición simple puede resolverse con texto y un ejemplo breve. Aplica los criterios y ejemplos del playbook.

- Reutiliza SVG/PNG directamente si ya están en `<proyecto>/diagramas/`. Si están en otra ruta, copia a esa carpeta con un nombre libre; convierte o exporta otros formatos sin alterar el original. No ejecutes un notebook o pipeline para extraer figuras que ya contiene. Usa solo el nombre en `story.visual.file`, nunca una ruta arbitraria fuera de la carpeta.
- No sobrescribas, muevas ni retires del índice los recursos originales. Si `diagramas/` ya contiene material del proyecto, conserva sus archivos y usa nombres distintos para las copias o apoyos nuevos del teach.
- Presenta qué pregunta resuelve la imagen y explica cómo leerla y qué conclusión apoya. Incluye `alt` y un pie comprensible; el texto debe conservar el razonamiento en modo texto.
- Verifica que abra, que se lea en móvil y que no tenga etiquetas cortadas. No dependas solo del color. Nunca inventes una captura ni un gráfico de resultados.
- Si eliges crear un apoyo nuevo, hazlo con las herramientas disponibles. Si un impedimento real evita reutilizar o producir una figura necesaria, explica la relación en texto y reporta qué figura quedó pendiente y por qué. No entregues silenciosamente una guía de puro código tras encontrar material gráfico útil.

Cuando la ubicación de carpetas o archivos importe, explica **qué consume esa ruta, desde dónde se resuelve, qué se rompería al moverla y qué habría que cambiar para reubicarla**. Comprueba imports, configuración, scripts, contexto de build, volúmenes o reglas de descubrimiento según el proyecto. Distingue una ubicación exigida por el mecanismo de una convención organizativa; no afirmes que una carpeta "debe ir ahí" solo porque así está en el repositorio. Usa un esquema de dependencias o flujo si la ubicación se entiende por su relación con otras piezas.

### 6. Reinstalar y verificar el motor

Vuelve a ejecutar el instalador al terminar `tutorial.json` y los diagramas, para dejar el motor y el `.gitignore` actualizados.

```bash
PROJECT=/ruta/al/proyecto
python3 "$HOME/.codex/skills/teachme/scripts/install.py" "$PROJECT"
```

El instalador copia el motor a `.teach/engine/`, crea o actualiza `teach` y conserva `tutorial.json`, `diagramas/` y `.teach/state/`. Es idempotente: puedes reinstalar tras corregir la skill sin perder progreso.

El mismo instalador agrega o actualiza este bloque en `.gitignore`, sin borrar reglas existentes:

```gitignore
# teach-project: artefactos locales de la guía
/teach
/.teach/
/tutorial.json
/diagramas/
# fin teach-project
```

No pidas confirmación para ignorar los artefactos nuevos del teach: es parte obligatoria del flujo. Verifica el bloque antes de entregar. Si hay artefactos del teach ya versionados, retira del índice únicamente esos archivos identificados, sin borrarlos del disco. Nunca apliques `git rm --cached` a recursos originales reutilizados ni a todo un directorio `diagramas/` que ya pertenecía al proyecto.

### 7. Validar y probar de verdad

```bash
python3 "$HOME/.codex/skills/teachme/scripts/validate_tutorial.py" "$PROJECT"
python3 "$HOME/.codex/skills/teachme/scripts/smoke_test.py" "$PROJECT"
"$PROJECT/teach" fases
"$PROJECT/teach" archivos
```

Corrige **todos** los errores del validador. El validador rechaza una primera fase titulada "Introducción", "Resumen" o "Contexto", con menos de tres bloques, o con un pedido/interpretación demasiado breves. Los demás avisos son criterios de calidad: justifica los que decidas dejar. El smoke test comprueba bootstrap, archivos, duda, exportación, limpieza y cierre sin tocar el progreso real.

### 8. Verificar el visor y entregar

Si hay navegador automatizable, abre la URL que imprime:

```bash
"$PROJECT/teach" guia --no-abrir
```

Comprueba en proporción al cambio:

- Las tres zonas: índice de fases, lector y panel **Mis dudas**.
- Navegación con ←/→, Enter para abrir código, ↑/↓ para desplazar y Enter para volver.
- Alta de una duda, **Limpiar**, **Copiar** y **Descargar .md**; que limpiar no borre fases leídas.
- Recarga: se conservan fase, scroll y dudas.
- Vista móvil (~390 px): el panel de dudas se abre con el botón y se cierra con Escape.
- `prefers-reduced-motion`: el visor respeta la preferencia.
- Diagramas visibles, con pie y enlace a tamaño completo.

Si no puedes usar navegador, valida la API y el HTML, y reporta la limitación sin afirmar que viste la interfaz.

## Criterio de terminado

No cierres la tarea hasta comprobar:

- `tutorial.json` existe y pasa el validador.
- `teach` existe, es ejecutable y `./teach fases` lista las fases.
- `.gitignore` contiene el bloque gestionado con `/teach`, `/.teach/`, `/tutorial.json` y `/diagramas/`.
- La primera fase explica el encargo con detalle: qué se pidió, para quién, qué implica, qué límites había y cómo se reconoce el éxito. No es una frase ni un resumen del README.
- Los conceptos necesarios están definidos antes de usarlos; hay un glosario inicial si hace falta. Las decisiones explican el mecanismo y sus consecuencias con ejemplos.
- El cómo aparece después del encargo; el cierre muestra qué produce el código o la infraestructura y distingue resultados observados, esperados y didácticos. No hay una sección explícita de transferencia.
- Se buscó y abrió el material gráfico relevante del repositorio; las figuras útiles están incorporadas y explicadas en el lector con su origen, o hay un impedimento concreto reportado. No basta con citar código o enlazar la imagen.
- Si faltaba material, se decidió qué crear según el tema: preferencia por gráficos en matemáticas y diagramas en infraestructura, DevOps y diseño de sistemas. Los flujos entre carpetas necesarios para comprender la implementación están representados y las restricciones de ubicación tienen una causa comprobada.
- El smoke test pasa.
- La respuesta al usuario es un acuse de entrega de cuatro líneas, no un resumen del proyecto ni el contenido de las fases.

El acuse final contiene solo:

1. Ruta de `tutorial.json`, número de fases y archivos citados.
2. Comando exacto para abrir: `./teach`.
3. Qué verificaste realmente y qué quedó pendiente.
4. Advertencia de no incluir credenciales, tokens, llaves ni artefactos de VM en el contenido.

El contenido completo vive en `tutorial.json` y en el visor. No lo vuelques en el chat.

## Reglas duras

- **No confundas teach con un resumen.** Un mapa de archivos, un flujo en bloques o una lista de métricas en el chat no reemplaza `tutorial.json` ni el visor. Si el usuario invocó `$teachme`, no hay explicación que valga: construye la guía.
- **La skill no es una respuesta.** Si el usuario solo quería una explicación breve, no la actives. Si ya se activó, el entregable sigue siendo los archivos y el visor, no un mensaje.
- **El problema primero.** La guía empieza por el encargo, no por la arquitectura. Explicá qué se pidió, qué implica y cómo se mide el éxito antes de mostrar código.
- **No resumas el encargo en una línea.** Si el pedido original es ambiguo o no está documentado, decilo y mostrá la evidencia; no inventes la intención ni la historia.
- **Nunca inventes** rutas, líneas, comandos, resultados de ejecución ni fuentes.
- Solo archivos públicos dentro del proyecto: nada de `.env`, `.git/`, `.state/`, llaves, discos, snapshots ni exports.
- No copies secretos ni datos personales al `tutorial.json`, a los diagramas ni al estado.
- El visor es de solo lectura: no agrega botones que ejecuten el proyecto.
- El progreso de estudio es independiente del estado operativo del proyecto. No mezcles ambos.
- Conserva el español en la interfaz y en el contenido salvo pedido explícito.
- Si el proyecto es enorme, acota el recorrido en `scope` y elige el flujo principal; no prometas cubrir todo.

## Referencias

- `references/schema.md`: esquema campo por campo y ejemplo mínimo.
- `references/content-playbook.md`: cómo convertir el código en fases que enseñan.
- `references/verification.md`: checklist de pruebas y fallos frecuentes.
