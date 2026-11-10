---
name: teachme
description: >-
  Construye una guía web local por fases: encargo, conceptos, decisiones, código y
  resultados, con ejemplos, diagramas, videos didácticos con Remotion cuando aporten,
  progreso y dudas. Entrega tutorial.json y
  ./teach, no un resumen en el chat. Úsala solo al invocar $teachme o pedir un teach
  o recorrido guiado navegable del proyecto; no para preguntas sueltas.
---

# Construir el visor teach de un proyecto

## Contrato y límites

- Activa la construcción solo ante `$teachme` o un pedido explícito como "enséñame de este proyecto", "hazme un teach", "quiero un recorrido guiado" o "revísalo conmigo paso a paso". Editar o analizar esta skill no construye una guía; una pregunta puntual o un resumen breve se responde directamente.
- El entregable vive en la raíz: `tutorial.json` contiene fases, archivos, fuentes y relato; `teach` es el lanzador ejecutable; `.teach/engine/` contiene el motor; `.teach/state/` guarda progreso y dudas; `diagramas/` contiene SVG/PNG cuando corresponda; `.gitignore` registra los artefactos locales.
- Instala el motor existente: servidor local con token, navegación por fases, código real con líneas, diagramas, progreso persistente, panel **Mis dudas** y copiar/descargar/limpiar/exportar. No sustituyas el visor por una explicación en el chat. Antes de terminar, limita el chat al aviso breve de construcción, sin arquitectura, métricas ni mapas de archivos; entrega el acuse final indicado abajo.
- Si no puedes escribir, detente con el error de un intento real; no alegues falta de permisos sin probar ni reemplaces los archivos con un resumen.
- No modifiques código del proyecto para prepararlo, instales dependencias, ejecutes el proyecto ni toques servicios o despliegues. El visor solo lee archivos públicos declarados; no incorpora botones de ejecución ni subcomandos operativos `teach lab`.
- Nunca inventes intención, historia, rutas, líneas, comandos, fuentes ni resultados. Excluye `.env`, `.git/`, `.state/`, llaves, discos, snapshots y exports de máquinas; no copies secretos ni datos personales a contenido, imágenes o estado. Español en contenido e interfaz salvo pedido explícito.

## Flujo obligatorio

### 0. Instalar antes de investigar

```bash
PROJECT=/ruta/al/proyecto
python3 "$HOME/.codex/skills/teachme/scripts/install.py" "$PROJECT"
```

Si existe `tutorial.json`, léelo y decide cómo actualizarlo; conserva `.teach/state/`. Construye sobre disco desde el inicio.

### 1. Reconstruir el encargo

Antes de explorar arquitectura, prepara un brief interno con pedido original y propósito, audiencia/contexto, problema previo, implicaciones/dependencias/riesgos/costos, restricciones, criterio de éxito, ambigüedades/supuestos y fuera de alcance. Usa la conversación, enunciado, `README`, `docs/`, `CONTRIBUTING`, issues, `git log --oneline -20`, `git status`, pruebas, esquemas, configuración y textos de interfaz. Distingue evidencia explícita de inferencias; si falta el enunciado, dilo y fundamenta la reconstrucción. Este brief será la primera fase, desarrollada y con evidencia, no una introducción ni un README resumido.

### 2. Reconocer la implementación y sus figuras

Lee puntos de entrada, configuración, esquemas/migraciones, pruebas/CI y los archivos que citarás con líneas exactas. Relaciona cada afirmación con archivo:línea o fuente oficial. Acota el flujo principal en `scope` si el proyecto es enorme; para uno mediano orientan README, entradas, configuración, pruebas y 10–15 archivos, sin inventario exhaustivo.

Busca y abre material gráfico antes de redactar: enlaces de documentación y carpetas de informes, resultados, notebooks, figuras, arquitectura e infraestructura; incluye SVG/PNG/JPEG/WebP, Mermaid, draw.io y figuras incrustadas en documentos. No te limites a `diagramas/`. Comprueba versión/ejecución y registra internamente origen → fase → uso o descarte justificado por alcance, decoración, duplicación o desactualización. Las figuras pertinentes y fiables deben mostrarse y explicarse en el lector, aunque el código o texto cuente lo mismo. Sigue la reutilización del paso 5.

### 3. Diseñar y enseñar

Lee [content-playbook.md](references/content-playbook.md) antes de redactar; contiene profundidad, ejemplos y elección de apoyos. Diseña 6–10 fases para un proyecto completo, cada una sobre un problema técnico concreto; el validador acepta 2–12 y avisa con fuerza si hay menos de 5. Orden: encargo y conceptos → decisiones/arquitectura/flujo/piezas críticas → alternativas y dificultades documentadas → resultado verificable. La arquitectura aparece después de comprender la necesidad.

Enseña con interés, lenguaje simple y precisión, sin tono infantil ni elogios vacíos. Desarrolla las preguntas "¿Qué se pidió?", "¿Qué decidimos y por qué?", "¿Cómo lo hace el código?" y "¿Qué produce?". Antes de usar una sigla, biblioteca, concepto o nombre interno, explica qué es, su papel aquí y un ejemplo. Conecta necesidad → concepto → decisión → mecanismo → efecto. Compara mecanismos y consecuencias cuando dos modelos o componentes reciban tratamientos distintos, incluido qué pasaría al aplicarles lo mismo. Usa ejemplos pequeños de entrada, transformación y salida, identificando los didácticos. El glosario inicial no reemplaza la explicación contextual posterior. El aprendizaje general surge del razonamiento; no añadas una sección de transferencia ni consejos genéricos para otros proyectos.

### 4. Escribir `tutorial.json`

Lee [schema.md](references/schema.md) y respeta su esquema. El visor web prioriza `story`; `sections` debe conservar conceptos, ejemplos, razonamiento y resultados para el modo texto.

- Cada fase: `id` estable en kebab-case, título de problema concreto, `flow` de 3–5 pasos y `sections` de 2–4 bloques. La primera desarrolla pedido/audiencia/contexto, implicaciones, límites/supuestos y criterio de éxito en 3–4 bloques; no la titules "Introducción", "Resumen" ni "Contexto".
- `story.request`, `interpretation`, `decision`, `result`: pedido → implicaciones/conceptos → elección/mecanismo/porqué → entrada y salida o cambio de estado con evidencia/límites. En la primera fase, `request` abre, `interpretation` desarrolla el brief y `result` describe aceptación y comportamiento esperado sin afirmar que ya ocurrió. No concentres todo en la entradilla ni solo en `sections`.
- `story.glossary` obligatorio en la primera fase, después del problema: lista de `{term, explanation}` sin campos adicionales. Cubre todos los conceptos previos pertinentes, ordenados por prerrequisitos, sin máximo arbitrario, huecos ni relleno ajeno. Cada explicación incluye definición, mecanismo/idea, papel aquí y ejemplo. Repítelo en `sections`; las fases posteriores definen términos nuevos antes de apoyarse en ellos.
- `story.alternatives`: al menos una con `name` y `tradeoff`; en el encargo compara interpretaciones posibles. `story.walkthrough`: 2–5 pasos con `file` y `lines` reales; en el encargo puede citar enunciado, README o pruebas.
- `story.difficulties`: problemas y resoluciones con evidencia, o lista vacía; en el encargo, ambigüedades/requisitos en conflicto. Distingue riesgos de incidentes; las limitaciones de evidencia van en alcance/resultado.
- Enlaza 1–4 archivos de texto por fase cuando sostengan la explicación, sin forzar código para reemplazar figuras. El catálogo `files` incluye `path`, `purpose`, `used_when`, `explanation`, `parameters`, `lines`; las imágenes van en `story.visual`, según el paso 5.
- `sources`: documentación oficial con fecha real `consulted`, sin tutoriales secundarios. `scope`: exclusiones y evidencia histórica.

Distingue implementado, observado en una ejecución, esperado sin ejecutar y ejemplo didáctico. La última fase explica entradas, salidas/cambios de estado, cómo comprobarlos y límites. Sin evidencia de ejecución, indica resultado esperado, comprobación y qué no verificaste; no levantes servicios para completar el relato. Documentos entregados, casillas y progreso de estudio no prueban funcionamiento operativo. En guías nuevas usa `result`; `transfer` solo conserva compatibilidad antigua, nunca prueba ejecución. Al actualizarlo, redacta un resultado respaldado, no lo renombres sin revisar.

### 5. Reutilizar o crear apoyos legibles

- Reutiliza primero las figuras pertinentes. SVG/PNG ya en `diagramas/` se referencian directamente; desde otra ruta, copia con nombre libre. Convierte/exporta otros formatos sin alterar originales ni ejecutar notebooks/pipelines para extraer salidas guardadas. No sobrescribas, muevas ni retires del índice recursos originales.
- `story.visual.file` es solo el nombre del SVG/PNG real en `diagramas/`, con `alt` y pie comprensible que identifica origen si se reutiliza. Explica pregunta, lectura y conclusión; conserva el razonamiento en `sections`. Una ruta, enlace o `flow` textual no reemplaza mostrar la figura. El motor admite una por fase: distribuye varias entre fases o compón una lámina legible, sin perder contenido/orígenes.
- Si falta material adecuado, decide qué crear según valor didáctico, sin cuota: prefiere gráficos/dibujos para matemáticas y diagramas para infraestructura, DevOps y sistemas. Una definición simple puede bastar con texto y ejemplo. Representa dependencias entre carpetas/módulos cuando sean necesarias para comprender el funcionamiento.
- Si la ubicación importa, comprueba imports, configuración, scripts, build, volúmenes o descubrimiento. Explica consumidor, resolución de la ruta, qué falla al moverla y cambios para reubicarla; distingue requisito técnico de convención. Un árbol de carpetas no sustituye el flujo necesario.
- Abre y revisa figuras en escritorio y móvil: etiquetas/ejes/leyendas legibles y completos, buen contraste, sin depender solo del color. Nunca inventes capturas ni gráficos de resultados.
- Todo diagrama creado/adaptado se renderiza e inspecciona al tamaño del lector y a tamaño completo. Textos sin solaparse, salir de cajas ni quedar atravesados por líneas/flechas; separa etiquetas de conectores y nodos. Ante colisiones o letra pequeña, reorganiza nodos/rutas, acorta/divide etiquetas o reparte el contenido en varios diagramas respetando una figura por fase. No encojas tipografía para forzarlo. Renderiza y revisa otra vez tras corregir; abrir a tamaño completo no sustituye leerlo en la guía.
- Usa las herramientas disponibles. Si un impedimento real evita reutilizar/crear/verificar una figura necesaria, conserva la explicación textual y reporta figura y motivo pendientes; no omitas silenciosamente material útil ni declares una inspección que no hiciste.

#### Videos con Remotion junto con los diagramas

- Evalúa si el movimiento ayuda a enseñar una idea concreta: recorrido de datos, orden de mensajes, cambios de estado, evolución de un algoritmo o construcción progresiva de un diagrama. Cuando aporte claridad y Remotion esté disponible, crea un video breve que acompañe el diagrama y su explicación. No impongas una cuota ni generes videos decorativos o que solo desplacen texto.
- Descubre y usa la extensión/plugin de Remotion y carga sus skills pertinentes de creación y renderizado antes de producir el video. Si no están disponibles o el render falla, conserva los diagramas y el texto e informa el impedimento real; no declares un video terminado sin un archivo reproducible.
- Guarda composiciones, dependencias y videos dentro de `.teach/media/`, separado del código del proyecto. Como excepción al límite de dependencias del proyecto, puedes instalar allí las necesarias para Remotion y ejecutar únicamente la composición y el render didácticos. No ejecutes la aplicación, sus pipelines ni servicios para crear escenas.
- Parte de las mismas entidades, etiquetas y relaciones verificadas del diagrama. Identifica simulaciones y ejemplos didácticos; una animación explicativa no demuestra una ejecución real. Conserva la explicación completa y una figura estática para estudiar sin reproducir el video.
- Entrega el video renderizado y su fuente editable. Vincúlalo con la fase y el diagrama correspondientes mediante las opciones que el visor soporte. El contrato actual de `story.visual` solo admite SVG/PNG: no pongas un MP4 allí ni inventes campos JSON. Si el visor no permite video, entrega en `.teach/media/` una página HTML local con controles de reproducción y la relación con la fase, e indica su ruta en el contenido de esa fase sin afirmar que está incrustada.
- Toda narración de los videos usa explícitamente la voz chilena Catalina de Microsoft, `es-CL-CatalinaNeural`, nunca la voz predeterminada del sintetizador o del navegador. Selecciona ese identificador en el proveedor disponible, conserva el guion y el audio en `.teach/media/` e incorpora el audio al render con subtítulos sincronizados. Si Catalina no está disponible o falla la síntesis, informa el impedimento y no la sustituyas silenciosamente. Identificador confirmado en la [documentación oficial de Microsoft](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support), consultada el 2026-10-26.
- El video debe reconocerse como reproductor antes de pulsar reproducir: usa un contenedor con fondo claramente distinto al de la página, borde visible, separación exterior y rótulo "Video" con título y duración real. Añade una portada con botón de reproducción reconocible y controles accesibles; no dependas solo de una sombra tenue ni presentes el fotograma como otro bloque de texto. Mantén buen contraste también dentro del video. Revisa la separación en pausa, reproducción y final, en escritorio y móvil, incluida la página HTML alternativa.
- Evita reproducción automática; usa controles, texto legible y subtítulos si hay narración. Comprueba el archivo renderizado y revisa inicio, transiciones y final para detectar cortes, solapamientos o diferencias con el diagrama. Verifica la reproducción y legibilidad en escritorio y móvil cuando haya navegador; informa las comprobaciones pendientes.

#### Cuestionario final de selección múltiple

- Después del bloque de preguntas de repaso o preparación de defensa, cierra la guía con un cuestionario de selección múltiple. Si no existe ese bloque, colócalo después de explicar los resultados. Ajusta extensión y dificultad al alcance y a la audiencia; usa dificultad intermedia por defecto, con aplicación de conceptos, interpretación de ejemplos y consecuencias de decisiones, sin limitarte a memorizar cifras o definiciones.
- Cada pregunta tiene cuatro alternativas A–D, una sola correcta y distractores plausibles basados en errores de comprensión. Evalúa solo contenido enseñado y respaldado por la guía. Separa el solucionario de los enunciados para que se pueda responder antes de verlo; explica la respuesta correcta y el error de las alternativas, e indica qué fase repasar.
- Usa los campos existentes: añade preguntas y solucionario como bloques `sections` de la última fase y repítelos al final de `story.result` para que aparezcan en el lector web y en modo texto. Conserva primero el resultado verificable y respeta el límite de bloques de la fase, agrupando el contenido previo si hace falta. No inventes campos `quiz` ni afirmes que hay corrección interactiva, puntuación o persistencia de respuestas si el motor no las implementa.
- Antes de entregar, resuelve cada pregunta y comprueba que tiene una única respuesta defendible, que las explicaciones coinciden y que el cuestionario se ve al final sin revelar la solución junto a cada enunciado.

### 6. Reinstalar y conservar los originales

Repite el instalador del paso 0 al terminar contenido y figuras. Es idempotente: actualiza motor/lanzador y conserva `tutorial.json`, `diagramas/` y `.teach/state/`. Verifica este bloque gestionado en `.gitignore`, sin borrar otras reglas:

```gitignore
# teach-project: artefactos locales de la guía
/teach
/.teach/
/tutorial.json
/diagramas/
# fin teach-project
```

Ignorar artefactos nuevos es parte del flujo, sin confirmación adicional. Si alguno ya está versionado, retira del índice solo los artefactos identificados del teach, sin borrarlos del disco. Nunca uses `git rm --cached` sobre recursos originales reutilizados ni todo `diagramas/` si ya pertenecía al proyecto.

### 7. Validar

```bash
python3 "$HOME/.codex/skills/teachme/scripts/validate_tutorial.py" "$PROJECT"
python3 "$HOME/.codex/skills/teachme/scripts/smoke_test.py" "$PROJECT"
"$PROJECT/teach" fases
"$PROJECT/teach" archivos
```

Corrige todos los errores y justifica avisos restantes. El validador rechaza aperturas genéricas, menos de tres bloques iniciales o pedido/interpretación demasiado breves; el smoke test comprueba bootstrap, archivos, dudas, exportación, comprensión reversible, limpieza y cierre sin tocar progreso real.

### 8. Verificar el visor y entregar

Lee y ejecuta los checklists de contenido y navegador de [verification.md](references/verification.md), proporcionalmente al cambio. Abre la URL de `"$PROJECT/teach" guia --no-abrir` con navegador automatizable. Comprueba índice/lector/dudas, navegación y código con teclado, marcar/desmarcar `completed`, alta/copiar/descargar/limpiar dudas sin borrar comprensión, autosave y restauración de fase/scroll/dudas/progreso al recargar o cerrar/reabrir. Escritorio: índice con scroll de rueda/teclado; móvil: fases horizontales y panel de dudas con botón/Escape a ~390 px; respeta `prefers-reduced-motion`. Figuras con pie/enlace a tamaño completo y legibilidad según el paso 5. Sin navegador, valida API/HTML y declara la limitación.

Cada duda conserva internamente su fase original aunque se navegue. Copiar/exportar incluye junto a cada duda un comentario HTML `teachme-origin` con número de duda, guía y número/id/título de fase. No aparece en el panel ni se sustituye por la fase abierta al exportar; no infieras el origen de dudas antiguas por su texto.

Termina solo con contenido que cumpla los pasos 1–5, validador/smoke test aprobados, `teach` ejecutable listando fases y bloque de `.gitignore` verificado. Al modificar esta skill o su contrato, ejecuta además `python3 scripts/test_content_contract.py` desde su carpeta.

El acuse final contiene únicamente cuatro líneas:

1. Ruta de `tutorial.json`, número de fases y archivos citados.
2. Comando exacto para abrir: `./teach`.
3. Verificaciones reales y pendientes, incluidas limitaciones de inspección visual.
4. Advertencia de no incluir credenciales, tokens, llaves ni artefactos de VM.
