# Learn Skill

## Qué es

`learn` es una skill para sesiones de aprendizaje profundo. Primero ubica lo que ya entiendes, concreta el resultado que quieres alcanzar, construye un mapa de dependencias y enseña cada concepto desde fundamentos conectados. Su criterio es `understanding > memorization`: poder reconstruir y aplicar una idea vale más que repetir una definición.

La skill queda separada de las respuestas normales. No se activa para una pregunta sencilla salvo que la invoques explícitamente.

## Cuándo usarla

Úsala cuando quieras estudiar un tema con continuidad y comprobar que los conceptos quedaron entendidos, por ejemplo:

- aprender OSPF y poder razonar sobre selección de rutas y adyacencias;
- estudiar arquitectura hexagonal y decidir dónde ubicar un adaptador en un proyecto real;
- entender concurrencia y predecir interleavings, carreras o bloqueos;
- construir la intuición de un concepto de cálculo a partir de sus fundamentos;
- leer un diagrama UML existente y reconstruir las relaciones que representa.

## Cuándo NO usarla

No la uses para definiciones rápidas, una explicación puntual, un resumen, una traducción, una solución directa o una duda casual. Por ejemplo, `¿qué es OSPF?` recibe una respuesta normal. `Usa learn para enseñarme OSPF desde mi nivel actual` inicia una sesión completa.

## Cómo activarla

Usa `$learn` si tu interfaz muestra las skills por nombre. También puedes copiar cualquiera de estos prompts:

`Usa la skill learn para enseñarme OSPF desde mi nivel actual.`

`Quiero aprender arquitectura hexagonal usando learn. Comprueba mis fundamentos antes de avanzar.`

`Enséñame concurrencia con la skill de aprendizaje y detente si no entiendo un prerrequisito.`

`Usa learn para enseñarme un concepto de cálculo con intuición, derivación y ejercicios.`

`Usa learn para ayudarme a entender este diagrama UML existente. Quiero que primero detectes qué sé y qué quiero poder hacer.`

Si `learn` no aparece como chip, escribe el prompt completo. La descripción de la skill exige una invocación explícita.

## Cómo funciona una sesión

La secuencia implementada es:

`probe → goal → plan → teach → verify`

1. `probe`: preguntas cortas y adaptativas localizan un piso conocido y un límite de comprensión en cada hilo relevante.
2. `goal`: una pregunta conversacional concreta qué quieres poder explicar, predecir, diseñar o diagnosticar.
3. `plan`: se investigan hechos que puedan haber cambiado o ser inciertos y se presenta el orden de conceptos. Se espera tu aprobación antes de enseñar.
4. `teach`: cada nodo pasa por motivar, establecer, conectar y comprobar. Si un fundamento falla, la sesión vuelve a ese punto.
5. `verify`: una tarea nueva comprueba transferencia. El resultado puede ser sólido, parcial o insuficiente, y cambia el siguiente paso.

## Visualizaciones

La skill dibuja solo cuando una imagen aporta algo que el texto no muestra bien.

- Relaciones, nodos, dependencias, flujos, secuencias, árboles, redes y estados usan Mermaid en la respuesta o en un archivo `.mmd`.
- Geometría, posiciones exactas, vectores, rectas numéricas y gráficos usan SVG u otro renderer disponible.
- Para un artefacto de diagrama independiente puede usar las skills instaladas `diagram-design` o `drawio`, si están disponibles. No son dependencias de `learn`.

La instalación actual no añade un renderer Mermaid ni extensiones Pi. El computador sí tiene `rsvg-convert` e ImageMagick para previsualizar SVG, y Codex dispone de inspección de imágenes. Cuando existe un renderer o una herramienta de inspección, la skill debe revisar el resultado antes de entregarlo. Si no existe, entrega la fuente Mermaid/SVG y declara que no fue renderizada, sin fingir una comprobación visual.

No se asume Obsidian, `viz/`, `md-log` ni una sintaxis especial de embed. Los archivos se guardan en el proyecto actual o en la ubicación que indiques.

## Investigación

Verifica antes de enseñar cuando la respuesta dependa de documentación actual, estándares, especificaciones, APIs, librerías, versiones, fechas, datos externos o un recuerdo incierto.

El orden de fuentes es documentación oficial, especificaciones y fuentes primarias, documentación técnica reconocida y otras fuentes solo cuando las anteriores no basten. Las afirmaciones verificadas llevan enlaces cercanos. La skill separa hechos de inferencias y reconoce cualquier dato que no pudo verificar.

Si hay capacidad de investigación o un subagente de solo lectura, puede usarlo con una tarea acotada. Si no, usa la búsqueda web disponible en la sesión. No requiere ni instala Pi.

## Ejemplos de uso

### Redes: OSPF

`Usa learn para enseñarme OSPF. Sé que existen routers y tablas de rutas, pero no entiendo cómo se forma la adyacencia ni por qué cambia la ruta elegida.`

La sesión debe sondear redes IP, métricas y estado de vecinos, verificar el comportamiento contra la documentación o especificación relevante, y luego conectar esos fundamentos con el algoritmo de selección.

### Ingeniería de software: arquitectura hexagonal

`Quiero aprender arquitectura hexagonal usando learn. Usa un pequeño ejemplo y comprueba si puedo ubicar puertos y adaptadores.`

La sesión debe distinguir el problema de acoplamiento de la terminología y comprobar la decisión en un caso nuevo, no pedir una definición memorizada.

### Programación: concurrencia

`Enséñame concurrencia con learn desde mis fundamentos de procesos e hilos. Quiero poder detectar una carrera en un ejemplo nuevo.`

La sesión debe comprobar interleavings, estado compartido y sincronización antes de introducir patrones o APIs concretas.

### Matemática: cálculo

`Usa la skill learn para enseñarme la intuición de la derivada. Quiero entender de dónde sale y usarla para razonar sobre una función.`

La sesión debe construir la idea desde cambio, razón y límite según el nivel detectado, usando notación LaTeX cuando ayude y ejercicios de transferencia.

### Proyecto real: diagrama UML

`Usa learn para ayudarme a entender este diagrama UML existente. Primero dime qué necesitas que observe y después comprueba si puedo reconstruir sus relaciones.`

La sesión debe usar el archivo o imagen suministrada, distinguir observación de interpretación y no inventar relaciones que el diagrama no muestra.

## Archivos instalados

- `@HOME@/skills/learn/SKILL.md`: instrucciones operativas de la skill, con la filosofía de `teach`, el flujo completo y las degradaciones portables.
- `@HOME@/skills/learn/agents/openai.yaml`: nombre visible, prompt inicial y política de invocación explícita.
- `@HOME@/skills/learn/LEARN-SKILL-GUIDE.md`: esta guía de uso y mantenimiento.
- `@HOME@/.agents/skills/learn`: enlace de descubrimiento para OpenCode y el ecosistema de skills.
- `@HOME@/.codex/skills/learn`: enlace de descubrimiento para Codex.
- `@HOME@/.cache/learn-upstream`: copia de referencia del repositorio original, fijada al commit inspeccionado `7cfd894`. No se carga en tiempo de ejecución.

No se modificaron `~/.codex/config.toml`, `~/.config/opencode/opencode.jsonc`, las skills existentes ni archivos de proyecto.

## Limitaciones

El proyecto original es una configuración de Pi. No se trasladaron literalmente sus extensiones TypeScript, sus agentes Pi, el popup de `ask-user-question`, el feedback automático de `quiz`, el registro `md-log`, el subagente `researcher` obligatorio ni los makers que escriben y renderizan PNG mediante herramientas privadas.

Las alternativas son conversación normal para preguntas, quizzes Markdown con respuesta diferida, investigación web o de solo lectura cuando existe, Mermaid/SVG como fuente y las herramientas de diagramas ya instaladas. Los subagentes y renderers son opcionales. Si una capacidad no está disponible, la skill continúa con una salida textual o fuente verificable y declara la limitación.

La política `allow_implicit_invocation: false` evita que `learn` se inyecte como respuesta a explicaciones normales. La activación explícita sigue disponible mediante `$learn` o un prompt equivalente.

## Actualización

Para actualizar la adaptación, conserva `@HOME@/skills/learn` como instalación canónica y actualiza primero la copia de referencia:

```bash
git -C @HOME@/.cache/learn-upstream fetch --depth=1 origin
git -C @HOME@/.cache/learn-upstream log -1 --oneline
```

Compara los cambios de `skills/teach`, `skills/visualize`, `agents` y `extensions` con la adaptación actual. Integra ideas manualmente en `SKILL.md` y esta guía. No reemplaces la carpeta completa ni ejecutes una actualización sobre los enlaces, porque eso podría borrar las decisiones de compatibilidad. Después ejecuta la validación de frontmatter y comprueba `opencode debug skill` y la lista de skills de Codex.
