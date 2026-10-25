# Convertir un proyecto en un recorrido que enseña

Cada fase debe dejar a la persona capaz de explicar una decisión, seguir el mecanismo en el código y anticipar su efecto. Si solo enumera bibliotecas, comandos o siglas, falta enseñanza.

## Tres actos: problema, cómo, resultado

El recorrido completo no empieza por la solución. Tiene tres actos:

1. **El problema**: qué se pidió, para quién, en qué contexto, con qué restricciones y qué implica. Es la primera fase y debe ser sustancial, no una introducción de dos líneas.
2. **El cómo**: las decisiones, el código, las alternativas y las dificultades que hicieron falta para resolverlo.
3. **El resultado**: qué produce el código al ejecutarse o qué cambia en la infraestructura, cómo se verifica y qué límites tiene. Distingue lo observado de lo esperado.

Si invertís el orden y empezás por la arquitectura, el lector ve piezas pero no entiende qué necesidad las justificaba.

## Arco de cada fase

1. **Pedido**: qué se nos pidió y qué necesidad concreta hay detrás. En la primera fase se expande; después se recuerda lo necesario para entender la fase.
2. **Interpretación y conceptos**: qué implica cumplirlo, qué necesitamos entender y por qué.
3. **Decisión**: qué elegimos, qué es esa pieza, cómo funciona y por qué sirve aquí.
4. **Alternativas**: qué otra forma existía y qué se gana/pierde con ella.
5. **Código**: dónde y cómo está implementado, con líneas reales.
6. **Dificultad**, si hay evidencia: qué falló o qué restricción técnica apareció y cómo se abordó. No inventes un incidente para llenar el apartado.
7. **Resultado**: con qué entrada opera, qué salida o estado produce y qué evidencia lo respalda.

La enseñanza general está dentro del porqué: qué propiedad del problema hizo conveniente una decisión y qué consecuencia tendría cambiarla. No termines con "Cómo llevarlo a otro proyecto", una sección de transferencia ni una receta genérica de adaptación.

## Enseñar sin dar por sabido

El tono es el de una persona que disfruta su área y quiere que otra la entienda. Muestra ese interés al detenerte en una diferencia que explica el comportamiento y al resolver la duda que surge de ella. Evita tanto el informe telegráfico como los discursos de motivación y el tono infantil.

Si falta historia del proyecto, indícalo una vez de forma breve y enseña lo que sí respalda la evidencia. Conserva las limitaciones relevantes en el alcance y junto al resultado; no interrumpas cada explicación con la misma salvedad.

Explica cada término en su primera aparición: qué es, para qué se usa aquí y un ejemplo. Una sigla desarrollada sigue necesitando explicación; "máquina de vectores de soporte" por sí solo no explica SVM. Los nombres internos como `select` o "red de provisión" también necesitan contexto. Usa comparaciones si ayudan y aclara dónde dejan de representar el mecanismo real.

En la fase del encargo, después de presentar el problema, incluye `story.glossary` con los conceptos que el lector necesitará al comenzar. Cada entrada tiene `term` y `explanation`, con una definición simple y un ejemplo del proyecto. Mantén ese glosario breve: las ideas especializadas se explican al llegar a su fase. Inclúyelo también en `sections` para el modo texto. No crees una fase vacía llamada "Conceptos básicos" ni supongas que leer el glosario basta para comprender después una decisión.

Para una decisión relevante, desarrolla necesidad → concepto → elección → mecanismo → efecto. Cuando dos piezas reciben tratamientos diferentes, compara cómo funcionan antes de enumerar sus configuraciones. Explica qué pasaría con una alternativa concreta, sin convertir ese razonamiento en una ley universal.

Usa párrafos con una idea por vez y preguntas como "¿Qué se nos pidió?", "¿Qué decisiones tomamos y por qué?" o "¿Por qué aquí es distinto?" cuando ordenen la explicación. No encadenes preguntas retóricas sin desarrollar sus respuestas. `story.decision` y `story.interpretation` admiten párrafos separados con una línea en blanco; el visor no interpreta Markdown dentro de ellos.

### Ejemplo de profundidad, no de contenido para copiar

Supón que el repositorio realmente contiene una pipeline de clasificación con escalado, muestreo y selección de variables. Lee primero el código; este ejemplo no fija el orden ni la configuración de todos los proyectos de ML.

Una explicación insuficiente sería: "Pipeline con scale, sampler, select y model. k-NN y SVM usan StandardScaler". Nombra herramientas sin explicar la decisión.

Una explicación que desarrolla el razonamiento:

**¿Qué se nos pidió?** Queremos evaluar las predicciones con datos que el modelo no haya usado para aprender. Si elegimos las columnas mirando también las etiquetas de prueba, la evaluación recibe información que debía permanecer reservada. Esa filtración se llama data leakage y puede hacer que las métricas parezcan mejores de lo que serán ante datos nuevos.

**¿Qué decisiones tomamos?** Agrupamos el preprocesamiento y el modelo en una Pipeline de imbalanced-learn. Es una secuencia que ajusta sus pasos con los datos de entrenamiento; incluye muestreadores que cambian cuántos ejemplos de cada clase se usan al ajustar. Al predecir, aplica las transformaciones aprendidas sin remuestrear las entradas. Para evitar la filtración, la pipeline completa debe ajustarse dentro de cada partición de entrenamiento, también durante la validación cruzada.

**¿Por qué escalamos algunos modelos?** k-NN consulta los `k` ejemplos más cercanos; al clasificar, estos vecinos votan por la clase de la nueva entrada. En un ejemplo didáctico, una columna de montos puede variar por miles y otra de edades por decenas. Sin escalado, las unidades de los montos pueden dominar la distancia. StandardScaler resta la media de entrenamiento y divide por su desviación estándar para las columnas con varianza distinta de cero. Así las diferencias se expresan en una escala comparable. Una SVM busca una frontera entre clases con un margen de separación amplio. En sus formulaciones habituales, la escala afecta esa geometría y el equilibrio entre separar las clases y tolerar errores.

**¿Por qué el árbol recibe otro tratamiento?** Un árbol compara valores con umbrales en cada columna. Un cambio lineal de escala preserva su orden, por lo que normalmente no necesita ese escalado. Un bosque combina árboles y comparte esa propiedad. La elección depende de cómo usa los números cada modelo, no de que una biblioteca sea mejor en general.

El cierre de esta fase mostraría una entrada y la predicción que produce el código citado, o describiría esa salida como esperada si no se ejecutó. No inventaría una mejora de precisión. Si se menciona ANOVA, también habría que explicar qué compara, qué selecciona y por qué esa selección se ajusta solo con entrenamiento.

La sencillez no permite decir "hay que limpiar todo antes de dividir". Las transformaciones que aprenden de los datos se ajustan solo con entrenamiento y luego se aplican a los datos reservados. Fuentes para comprobar estos mecanismos: [filtración de datos](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage), [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html), [efecto del escalado en modelos](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html) y [Pipeline de imbalanced-learn](https://imbalanced-learn.org/stable/references/generated/imblearn.pipeline.Pipeline.html). Verifica la versión que usa el proyecto al elaborar su guía.

## Reconstruir el encargo

Antes de escribir la primera fase, respondé estas preguntas con evidencia:

- ¿Quién pidió qué, con qué palabras y para qué?
- ¿Qué problema existía antes? ¿Qué fallaba, faltaba o había que cambiar?
- ¿Qué restricciones había: stack, datos, seguridad, compatibilidad, tiempo, decisiones ya tomadas?
- ¿Qué implica cumplir el pedido? ¿Qué piezas toca, de qué depende, qué riesgo introduce?
- ¿Cómo se reconoce que quedó resuelto?
- ¿Qué no se pidió o quedó explícitamente fuera de alcance?
- ¿Qué era explícito y qué tuviste que inferir? ¿Qué supuestos hiciste?

Fuentes útiles: enunciado de la tarea, `README`, `docs/`, issues, mensajes de commit, pruebas, esquemas, configuración y textos de interfaz. Si el enunciado original no está en el repositorio, decilo; no inventes la intención.

La primera fase se llama algo como **"El encargo: qué se pidió y qué implica"**, no "Introducción" ni "Contexto". Usa 3–4 bloques:

- **Qué se pidió**: el pedido original, la audiencia y el contexto.
- **Qué implica**: requisitos, dependencias, riesgos y cambios que arrastra.
- **Límites y supuestos**: restricciones, ambigüedades y lo que queda fuera.
- **Criterio de éxito**: cómo se comprueba que el pedido quedó resuelto.

No pongas todo en `story.request`: el visor lo muestra como entradilla. Desarrollá el contexto en `story.interpretation`, usá `sections` para el modo texto y `story.walkthrough` para citar el enunciado, el README o las pruebas que sostienen el encargo. El `story.request` abre; la interpretación explica.

### Ejemplo de apertura

Apertura floja, que no reconstruye nada:

> "La aplicación permite gestionar tareas."

Apertura que sí presenta el problema:

> "El equipo pedía reemplazar una planilla compartida que se pisaba entre áreas. Necesitaba una fuente única, permisos por rol y un historial de cambios. El éxito era que dos personas pudieran editar a la vez sin perder datos y que quedara registro de quién cambió qué. Quedaban fuera las notificaciones y la aplicación móvil."

La segunda no es más larga por relleno: nombra el pedido, el problema, las implicaciones, el criterio de éxito y el fuera de alcance.

## Selección de contenido

Empieza por el flujo que un nuevo colaborador necesita para no romper nada:

- Punto de entrada y arranque.
- Modelo de datos o estructura central.
- Flujo principal de punta a punta.
- Configuración y parámetros que cambian el comportamiento.
- Manejo de errores, reintentos, permisos o límites.
- Pruebas y verificación real.
- Operación, despliegue o migración.
- Salidas, recursos o cambios de estado que produce ese flujo.

Deja fuera lo accesorio. Si el proyecto tiene diez módulos, elige el camino que explica la arquitectura; menciona los demás en `scope` o en una alternativa.

## Plantilla de fase

```text
id: verbo-sustantivo
title: Problema concreto, no "Introducción"
flow: 3–5 pasos del recorrido
files: 1–4 archivos de texto que sostienen la fase, cuando corresponda
sections: 2–4 bloques para el modo texto
story:
  request: necesidad del usuario
  interpretation: qué implica el pedido, con los conceptos necesarios
  glossary: conceptos iniciales, con term y explanation, si hacen falta
  decision: qué es la pieza elegida, cómo funciona y por qué se eligió
  visual: figura existente relevante, o apoyo nuevo elegido según el tema
  alternatives: al menos una, con costo real
  walkthrough: 2–5 pasos con archivo y líneas
  difficulties: problemas documentados y resolución, o lista vacía
  result: entrada → salida o cambio de estado, con evidencia y límites
```

### Buenos títulos

- "Cómo se separan las redes de gestión y provisión"
- "Qué pasa desde el pedido hasta la escritura en disco"
- "Dónde se decide el reintento y qué evita duplicados"
- "Cómo se valida una entrada antes de tocar la base"

### Títulos que no sirven

- "Introducción"
- "Contexto"
- "Instalación"
- "Archivos importantes"
- "Resumen"
- "Conceptos básicos"

## Cómo escribir el relato

- Usa frases cortas y concretas. Explica el **porqué** antes del comando.
- Define los términos y acompaña las decisiones difíciles con un ejemplo pequeño. No reemplaces "por qué" por "porque es buena práctica".
- Nombra los parámetros y su efecto: "`timeout` en segundos; si se agota, el cliente reintenta una vez".
- Cita archivo y líneas reales. Si el código cambió, actualiza el rango y vuelve a validar.
- Distingue tres niveles de evidencia:
  - **Implementado**: está en el repositorio y se puede leer.
  - **Observado**: se ejecutó y se registró una salida o un estado.
  - **Alternativa**: no está implementado; se propone.
- No presentes una salida esperada como si fuera un resultado obtenido.
- Etiqueta los datos inventados para explicar como **ejemplo didáctico**. Nunca los uses para afirmar que el proyecto alcanzó una métrica.
- No inventes credenciales, direcciones, versiones ni fechas. Si no las sabes, omítelas o indica que no se verificaron.

## Buscar y reutilizar antes de crear

Antes de escribir las fases, busca material gráfico en las rutas reales del proyecto: enlaces del README y documentación, informes, resultados, notebooks, figuras, arquitectura y configuración de infraestructura. Empieza con búsquedas dirigidas con `rg --files` y revisa los enlaces a imágenes o diagramas en los documentos relevantes. No concluyas que no hay figuras porque no existe `diagramas/`: pueden estar en `reports/figures/`, salidas de notebooks, documentos PDF o fuentes Mermaid/draw.io. Si la documentación apunta a salidas ignoradas por Git, revisa esa ruta concreta también, sin recorrer dependencias ni cachés completas.

Abre cada candidato pertinente con un visor o renderizador disponible. Clasifica internamente origen, qué explica, a qué fase corresponde y si se usa o por qué se descarta. **Una figura que explica los resultados, la arquitectura o el flujo cubierto por la guía se debe usar.** No la omitas porque el texto o el código también cuentan esa parte, ni la sustituyas por un dibujo nuevo menos informativo. No es necesario incluir logos, capturas ajenas al alcance o duplicados. Si está desactualizada o contradice la implementación, explica la diferencia cuando enseñe algo útil, o descártala con esa razón; no la presentes como estado actual.

Para incorporarla al visor:

- Si ya es SVG/PNG en `diagramas/`, referencia su nombre en `story.visual.file`. Si está fuera, copia a `diagramas/` con un nombre sin colisiones. No muevas ni sobrescribas la fuente.
- Para JPEG/WebP, PDF, Mermaid, draw.io o imágenes embebidas, usa una conversión, exportación o extracción que conserve el contenido y produzca SVG/PNG. Extraer una salida guardada de un notebook no requiere ejecutarlo. No instales ni ejecutes el proyecto para regenerar resultados ya disponibles.
- Identifica la ruta original y, si se conoce, la celda, página o ejecución en el pie. Explica ejes, unidades, leyenda, flechas o elementos relevantes y qué conclusión permiten obtener. Un gráfico guardado prueba lo que registra esa ejecución, no una ejecución actual.
- `story.visual` muestra una figura por fase. Si hacen falta varias, distribúyelas en las fases que explican esas ideas o compón una lámina legible que conserve cada figura y su origen. No declares una lista `visuals` que el motor no soporta ni descartes una figura esencial por esa limitación.

Mencionar `reports/figures/resultados.png`, dejar un enlace o pegar más código no equivale a incorporar la figura. Debe aparecer en el lector y acompañarse de una explicación. Si una herramienta o formato impide mostrarla, registra ese impedimento específico y conserva la explicación textual; no la omitas sin decirlo. Las fuentes originales siguen siendo material del proyecto, aunque el teach ignore sus propias copias locales.

## Si falta material, decidir qué apoyo crear

Cuando no haya una figura existente adecuada, el modelo decide si crear un apoyo y de qué tipo según lo que la persona necesite entender. No hay una cuota universal ni un diagrama obligatorio para cada fase. La preferencia por tema es:

| Qué hay que explicar | Apoyo adecuado | Qué debe aclarar |
| --- | --- | --- |
| Definición, parámetro o decisión local | Texto y un ejemplo breve suelen bastar | Qué significa y qué cambia al usarlo. Esto no justifica omitir una figura existente relevante. |
| Ejemplo matemático, fórmula, cálculo o transformación de datos | Preferir texto más gráfico, dibujo geométrico, curva o antes/después; una tabla si aclara mejor el cálculo | Cómo cambian las cantidades y cómo una entrada se convierte en salida, con ejes, unidades y valores cuando correspondan. |
| Flujo con ramas, orden de pasos o intercambio entre componentes | Texto y diagrama de flujo o secuencia | Quién recibe qué, en qué orden y qué camino sigue un error. |
| Infraestructura, redes, despliegue DevOps, arquitectura o diseño de sistemas | Preferir texto y diagrama de topología, despliegue, capas o secuencia según el mecanismo | Qué se conecta, dónde corre cada pieza y qué datos, artefactos o configuración pasan entre ellas. |
| Flujo entre carpetas, módulos o archivos cuya relación o ubicación condiciona el funcionamiento | Texto y esquema de dependencias o flujo | Qué pieza consume a otra, cómo resuelve la ruta y por qué esa ubicación importa. Un árbol de directorios por sí solo no muestra esas relaciones. |
| Estados o pasos cuyo orden cambia el resultado | Texto y diagrama de estados o comparación de caminos | Qué habilita cada transición y qué ocurre si se cambia el orden. |
| Distribuciones, distancias, métricas o diferencias cuantitativas | Texto y gráfico o dibujo explicativo | Qué patrón explica la decisión. Indica origen de los datos, ejes, unidades y si son didácticos. |

En el ejemplo de ML, un flujo con entrenamiento y validación separados muestra dónde se ajustan las transformaciones; un antes/después con dos columnas explica por qué cambian las distancias al escalar. Cada visual responde una pregunta diferente. No exijas ilustraciones a todas las fases ni dejes una relación difícil solo en prosa por comodidad.

Si el repositorio ya contiene una matriz de confusión o curvas de evaluación pertinentes, intégralas y enseña a leerlas al explicar los resultados. Si la fase explica una distancia o una función y no hay figuras, considera un gráfico con un ejemplo didáctico. Si explica un despliegue, considera el recorrido commit → build → imagen → servicio, usando solo los pasos que el repositorio realmente implemente. No agregues componentes por parecer típicos de DevOps.

Presenta la pregunta que resuelve la imagen, explica cómo leerla y desarrolla la conclusión en texto. Cada flecha tiene un significado; etiqueta datos y pasos. Conserva esa explicación en `sections` para que el modo texto enseñe lo mismo. El glosario y los ejemplos numéricos breves pueden vivir en los párrafos; usa SVG/PNG en `story.visual` para el apoyo gráfico. No añadas claves de tabla o gráfico que el visor no renderiza.

Guarda el archivo real en `diagramas/`. Incluye `alt` útil y un pie que explique el mecanismo; verifica etiquetas, contraste y lectura móvil. No dependas solo del color. Usa herramientas de diagramas o dibujo disponibles y comprueba el resultado. Si un impedimento real evita crearlo, conserva la explicación textual y registra el apoyo pendiente. No declares verificada una imagen que no pudiste abrir ni inventes capturas o datos experimentales.

## Explicar la ubicación y el flujo entre carpetas

Evita "esta carpeta debe estar aquí" sin mostrar el mecanismo que lo exige. Cuando la disposición importe, sigue la dependencia hasta su consumidor:

- Qué archivo, proceso o herramienta usa esa ruta y para qué.
- Desde qué base la resuelve: directorio de trabajo, raíz del proyecto, paquete, contexto de build, volumen o regla de descubrimiento, según lo que indique la configuración.
- Qué fallo o cambio de comportamiento causaría moverla sin ajustar sus consumidores.
- Qué configuración o referencias habría que cambiar para moverla, o si la ubicación es solo una convención y podría variar.

Por ejemplo, si una instrucción de build copia una carpeta, revisa el contexto de build antes de afirmar por qué la encuentra; un volumen de despliegue puede sustituir esa ruta en ejecución. En un import entre módulos, sigue cómo se resuelve el paquete y no supongas que depende de una ruta relativa del sistema de archivos. Explica solo las condiciones comprobadas en ese repositorio.

Si esa relación es necesaria para entender el flujo, representa las carpetas o módulos como nodos y etiqueta las flechas con acciones como "importa", "genera", "copia", "monta" o "lee configuración". Conecta estructura → consumidor → efecto. No basta un árbol decorativo de carpetas ni una lista de archivos; el lector debe entender por qué las piezas están relacionadas.

## Qué significa el resultado

`story.result` responde qué hace posible la implementación de esta fase y cómo se reconoce su efecto. En el encargo describe el comportamiento esperado y el criterio de aceptación. En las fases técnicas sigue una entrada hasta una salida o un estado concreto. La fase final une el flujo completo.

- En ML: qué datos recibe el modelo, qué predice, qué significa la salida y con qué evidencia se evalúa.
- En una aplicación: qué acción o solicitud entra, qué respuesta recibe la persona y qué registros cambian.
- En infraestructura: qué configuración se aplica, qué recurso o conectividad queda disponible y qué observación lo comprueba.

Cita el código o configuración que produce el efecto y la prueba, salida o estado que lo comprueba, si existe. Si solo se leyó el código, explica el comportamiento esperado y cómo verificarlo, sin afirmar que se ejecutó. No levantes infraestructura ni servicios para completar la guía. Un checklist completado o un informe escrito no reemplaza el resultado operativo. Una salvedad sobre evidencia histórica debe acompañar la afirmación que limita, no rellenar "Dificultades".

## Archivos y fragmentos

- Para un recorrido completo suelen bastar entre 6 y 14 archivos de texto. No rellenes el catálogo ni reemplaces resultados gráficos con código para alcanzar un número; las figuras aportan su propia evidencia en `story.visual` y su pie.
- Elige el fragmento mínimo que muestra la decisión, no el archivo entero.
- `lines` debe apuntar al bloque real. El visor resalta ese rango y abre el archivo completo.
- `parameters` explica entradas, variables de entorno y valores por defecto.
- `used_when` responde cuándo se ejecuta o se lee ese archivo.
- `explanation` conecta el archivo con el flujo, no lo describe línea por línea.

## Fuentes

- Usa documentación oficial del creador o mantenedor.
- Registra `consulted` con la fecha real de consulta.
- No uses blogs o tutoriales secundarios como fuente principal.
- Si una afirmación no tiene fuente ni código, quítala o márcala como hipótesis.

## Errores frecuentes

| Error | Corrección |
| --- | --- |
| Copiar el README en `sections` | Convertir cada bloque en problema → decisión → evidencia. |
| Encargo en una línea | Desarrollar pedido, implicaciones, límites y criterio de éxito. |
| Empezar por la arquitectura | Primero el problema; la arquitectura es una respuesta. |
| Confundir README con el encargo | El README describe el proyecto; el encargo dice qué se pidió y qué implica. |
| Inventar el pedido | Marcarlo como inferido o decir que no está en el repositorio. |
| Citar archivos que no existen | Ejecutar el validador y corregir rutas. |
| Rangos de líneas desactualizados | Leer el archivo y ajustar `lines`; volver a validar. |
| Fases de una sola frase | Agregar interpretación, alternativa y walkthrough real. |
| Enumerar siglas o bibliotecas | Explicar qué son, su papel aquí y un ejemplo antes de usarlas. |
| Explicar diferencias solo con configuraciones | Comparar mecanismos y consecuencias de aplicar el mismo tratamiento. |
| Consejos genéricos para otro proyecto | Integrar el criterio en el porqué y cerrar con el efecto del código. |
| Confundir simplificación con precisión | Revisar el mecanismo; no enseñar que todo preprocesamiento debe hacerse antes de dividir datos. |
| Diagramas decorativos | Quitarlos o rehacerlos para que expliquen una relación. |
| Omitir gráficos del repositorio y citar solo código | Buscar, abrir e incorporar las figuras pertinentes con origen y explicación. |
| Usar solo un enlace o ruta de imagen | Mostrar el SVG/PNG real en `story.visual` y explicar qué se observa. |
| Crear otra figura sin revisar las existentes | Reutilizar la fuente adecuada antes de decidir qué falta crear. |
| Describir infraestructura solo con archivos de configuración | Considerar un diagrama de componentes y del flujo real entre ellos. |
| Afirmar que una carpeta debe ir en una ruta por costumbre | Identificar el consumidor, la resolución de la ruta y qué cambia al moverla. |
| Mezclar progreso de estudio con estado del proyecto | Mantenerlos separados; el visor solo guarda lectura y dudas. |
| Prometer que el proyecto "funciona" | Decir qué se leyó, qué se ejecutó y qué no se verificó. |

## Criterio de cierre

Antes de entregar, pregúntate:

- ¿Se entiende qué se pidió y qué implicaba antes de ver código?
- ¿La primera fase desarrolla el encargo o solo lo menciona en una frase?
- ¿Puede alguien explicar el flujo principal sin abrir el código?
- ¿Sabe dónde cambiar un parámetro y qué efecto tendrá?
- ¿Conoce al menos una alternativa y su costo?
- ¿Entiende cada término cuando aparece y puede explicar por qué dos casos reciben tratamientos distintos?
- ¿Los ejemplos y apoyos visuales resuelven una duda concreta en lugar de decorar?
- ¿Busqué y abrí las figuras existentes y mostré las relevantes, en vez de limitarme a citar código?
- Si faltaban figuras, ¿decidí los apoyos considerando gráficos para matemáticas y diagramas para infraestructura, DevOps y sistemas?
- ¿Representé las dependencias entre carpetas cuando eran necesarias y expliqué el motivo real de sus ubicaciones?
- ¿Distingue lo implementado de lo observado y de lo propuesto?
- ¿El resultado se puede verificar y no es solo un resumen?
- ¿Cada fase cita evidencia real y conecta la implementación con una salida o cambio de estado, sin una sección de transferencia?

Si alguna respuesta es no, falta contenido, no formato.
