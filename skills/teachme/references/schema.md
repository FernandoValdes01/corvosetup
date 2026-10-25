# Esquema de `tutorial.json`

`tutorial.json` vive en la raíz del proyecto y es la única fuente de contenido del visor. Debe ser UTF-8 y un objeto JSON. El motor lo lee al iniciar y no modifica el proyecto.

## Nivel superior

```json
{
  "title": "Repaso guiado de Mi Proyecto",
  "objective": "Comprender el flujo principal y poder modificarlo con criterio.",
  "scope": "Qué cubre esta guía, qué no prueba y qué evidencia es histórica.",
  "files": [],
  "phases": [],
  "sources": []
}
```

| Campo | Obligatorio | Uso |
| --- | --- | --- |
| `title` | Sí | Título del proyecto en la barra lateral y en la exportación. |
| `objective` | Sí | Qué debe poder hacer o explicar quien termina el recorrido. |
| `scope` | Sí | Límites, exclusiones y advertencias de evidencia. |
| `files` | Recomendado | Catálogo de archivos citables. El visor solo sirve estos. |
| `phases` | Sí | Fases del recorrido, en orden. |
| `sources` | Recomendado | Documentación oficial consultada. |

## Archivo (`files[]`)

```json
{
  "path": "src/api/server.ts",
  "purpose": "Expone el endpoint de creación y valida la entrada.",
  "used_when": "Se usa en cada alta de recurso antes de tocar la base.",
  "explanation": "El handler normaliza el cuerpo, valida el esquema y delega la escritura.",
  "parameters": "`req.body.name` define el nombre; `req.user` aporta el propietario.",
  "lines": [18, 64]
}
```

Reglas:

- `path` relativo a la raíz, sin `..`, sin rutas absolutas y sin segmentos ocultos (`.git`, `.env`, `.teach`).
- El archivo debe existir, ser UTF-8 y pesar menos de 300 KB.
- `lines` debe caer dentro del archivo. Es el fragmento que se resalta al abrirlo.
- `purpose`, `used_when`, `explanation` y `parameters` son obligatorios para la lectura de código.
- Un archivo puede aparecer en varias fases, pero se declara una sola vez en `files`.

## Fase inicial: el encargo

La primera fase no es una introducción: reconstruye el pedido y su contexto. Se recomienda `id: "el-encargo"` y un título como **"El encargo: qué se pidió y qué implica"**. Evitá "Introducción", "Contexto" o "Resumen".

```json
{
  "id": "el-encargo",
  "title": "El encargo: qué se pidió y qué implica",
  "flow": ["Qué se pidió", "Qué implica", "Límites y supuestos", "Criterio de éxito"],
  "sections": [
    { "title": "El pedido original", "text": "Quién pidió qué, para qué y en qué contexto." },
    { "title": "Implicaciones y restricciones", "text": "Qué piezas toca, de qué depende, qué riesgo introduce y qué restricciones había." },
    { "title": "Criterio de éxito y fuera de alcance", "text": "Cómo se reconoce que quedó resuelto y qué no se pidió." },
    { "title": "Conceptos para empezar", "text": "Criterio de aceptación: una condición comprobable para decidir si cumplimos el pedido. Aquí sería que dos personas editen sin perder cambios y que quede registro de quién los hizo. Este bloque conserva en modo texto los conceptos de story.glossary." }
  ],
  "files": ["README.md"],
  "story": {
    "request": "El pedido original en 2–4 frases: quién, qué y para qué.",
    "interpretation": "Desarrollo del contexto: problema, implicaciones, restricciones, supuestos y criterio de éxito. No una frase.",
    "glossary": [
      { "term": "Criterio de aceptación", "explanation": "Una condición comprobable para decidir si cumplimos el pedido. Aquí sería que dos personas editen sin perder cambios y que quede registro de quién los hizo." }
    ],
    "decision": "Cómo se delimitó el alcance y por qué se priorizó eso.",
    "alternatives": [
      { "name": "Otra lectura del pedido", "tradeoff": "Qué se ganaba y qué se perdía con esa interpretación." }
    ],
    "walkthrough": [
      { "title": "Dónde está el pedido", "text": "El enunciado, README o prueba que sostiene esta reconstrucción.", "file": "README.md", "lines": [1, 20] }
    ],
    "difficulties": ["Qué parte del pedido era ambigua y cómo se resolvió."],
    "result": "Qué comportamiento debe producir el proyecto y qué observación permitiría aceptarlo. En esta fase se describe como esperado, sin afirmar que ya ocurrió."
  }
}
```

Reglas de esta fase:

- `story.request` abre el tema; no es el brief completo. El visor lo muestra como entradilla.
- `story.interpretation` desarrolla qué implica el pedido: problema, dependencias, restricciones, supuestos y criterio de éxito.
- `story.glossary` introduce los conceptos necesarios después de presentar el problema. Cada término tiene una explicación simple y un ejemplo del proyecto. Repite esos conceptos en un bloque de `sections` para el modo texto, sin crear otra fase genérica.
- `sections` alimenta el modo texto y la exportación; usá al menos tres bloques distintos. No dejes el contexto solo ahí: el visor web prioriza `story`.
- `story.walkthrough` puede citar documentación, `README`, issues o pruebas; no necesita código.
- Si el pedido original no está en el repositorio, decilo en `story.difficulties` o `story.interpretation` y marcá qué es inferido.

## Fase (`phases[]`)

```json
{
  "id": "flujo-de-alta",
  "title": "Cómo se construye un recurso",
  "flow": ["Valida la entrada", "Resuelve permisos", "Persiste y responde"],
  "sections": [
    { "title": "El pedido", "text": "Qué necesita el usuario y qué recibe." },
    { "title": "La decisión", "text": "Por qué se resolvió de esta forma." }
  ],
  "files": ["src/api/server.ts", "src/db/repository.ts"],
  "story": {
    "request": "Pedido concreto que abre la fase.",
    "interpretation": "Qué implica el pedido y qué conceptos necesitamos entender para resolverlo.",
    "visual": {
      "file": "flujo-alta.svg",
      "alt": "Flujo de validación, permisos y persistencia.",
      "caption": "Cada capa recibe el recurso ya validado."
    },
    "decision": "Qué elegimos y por qué. Explica qué es esa pieza, cómo funciona aquí y qué efecto tendría una alternativa. Separa las ideas con párrafos si hace falta.",
    "alternatives": [
      { "name": "Escribir directo en el handler", "tradeoff": "Menos capas, pero mezcla validación y persistencia." }
    ],
    "walkthrough": [
      {
        "title": "Validar antes de escribir",
        "text": "El esquema rechaza campos desconocidos antes de llegar a la base.",
        "file": "src/api/server.ts",
        "lines": [24, 48]
      }
    ],
    "difficulties": [
      "La validación y la persistencia usaban criterios distintos; se unificaron en un esquema."
    ],
    "result": "Con una solicitud válida, el handler crea el registro y devuelve su identificador. Una entrada inválida se rechaza antes de escribir. Este es el comportamiento esperado según el código citado; la guía no ejecutó el servidor."
  }
}
```

| Campo | Obligatorio | Uso |
| --- | --- | --- |
| `id` | Sí | Kebab-case único; se guarda en el progreso. |
| `title` | Sí | Título visible de la fase. |
| `flow` | Recomendado | 3–5 pasos que resumen el recorrido. |
| `sections` | Sí | 2–4 secciones para el modo texto y la lectura lineal. En el encargo, al menos 3. |
| `files` | Recomendado | Rutas del catálogo que pertenecen a la fase. |
| `story` | Recomendado | Relato principal del visor web. Sin `story` se usa `sections`. |
| `story.request` | Sí si hay `story` | Pedido que abre la fase. En el encargo, 2–4 frases con quién, qué y para qué. |
| `story.interpretation` | Sí si hay `story` | Traducción del pedido a requisitos. En el encargo, desarrolla implicaciones, restricciones, supuestos y criterio de éxito. |
| `story.decision` | Sí si hay `story` | Qué se eligió, qué es, cómo funciona y por qué sirve aquí. Explica diferencias entre casos y sus consecuencias. En el encargo, cómo se delimitó el alcance. |
| `story.result` | Sí en guías nuevas con `story` | Qué produce o habilita el código o la infraestructura: entrada, salida o cambio de estado, evidencia y límites. En el encargo, comportamiento esperado y criterio de aceptación. |
| `story.glossary` | Cuando hay conceptos que introducir | Lista de `{term, explanation}`. En el encargo contiene los conceptos necesarios para comenzar; después introduce los nuevos al usarlos. |
| `story.visual` | Si hay material existente pertinente; si falta, según la decisión didáctica | `file` con nombre SVG/PNG real en `diagramas/`, `alt`, `caption`. Puede reutilizar un gráfico del proyecto o mostrar un apoyo nuevo. El pie identifica la fuente original si es reutilizado y explica qué observar. |
| `story.alternatives` | Recomendado | Lista de `{name, tradeoff}`. En el encargo, interpretaciones alternativas del pedido. |
| `story.walkthrough` | Recomendado | Pasos con `title`, `text`, `file`, `lines`. En el encargo puede citar documentación o pruebas. |
| `story.difficulties` | Si hay evidencia | Lista de problemas reales y su resolución; puede estar vacía. En el encargo, ambigüedades. No inventes incidentes ni rellenes con salvedades documentales. |

`story.transfer` es un campo antiguo. El motor lo conserva como "Cierre de la guía anterior" si falta `result`, y el validador avisa que debe revisarse. Al actualizar contenido, escribe un `result` respaldado por evidencia y elimina `transfer`; no basta con renombrarlo. No presentes consejos antiguos de adaptación como resultados de ejecución. En guías nuevas no uses `transfer` ni un apartado de enseñanza general: desarrolla ese aprendizaje dentro de las decisiones y alternativas.

Los campos de texto son texto plano, sin interpretación de Markdown. En el visor web, separa párrafos con `\n\n` dentro de la cadena JSON. Un ejemplo didáctico debe identificarse como tal. `sections` conserva los conceptos, ejemplos y resultados para el modo texto; no los dejes solo en `story`.

Para una figura que estaba en `reports/figures/resultado.png`, copia sin alterar la fuente a un nombre libre en `diagramas/` y usa ese nombre en `story.visual.file`. El pie puede comenzar con `Origen: reports/figures/resultado.png` y desarrollar qué muestran los ejes o componentes y qué conclusión sostienen. Si ya estaba en `diagramas/`, referencia su nombre sin moverla. Las imágenes no se declaran en `files`, que solo admite texto UTF-8. El motor admite una figura por fase; reparte las figuras necesarias entre las fases correspondientes o compón una lámina legible sin perder sus fuentes.

## Fuentes (`sources[]`)

```json
{
  "title": "Documentación oficial de la API",
  "url": "https://ejemplo.com/docs/api",
  "consulted": "2026-10-24"
}
```

Usa documentación oficial del creador o mantenedor. No sustituyas el manual por blogs o tutoriales secundarios. Registra la fecha de consulta.

## Fragmento de una fase técnica

Este fragmento ilustra los campos; no es una guía completa validable. Necesita una fase inicial del encargo, más fases y archivos reales con los rangos indicados.

```json
{
  "title": "Repaso de ejemplo",
  "objective": "Entender el flujo mínimo.",
  "scope": "Guía de lectura; no ejecuta el proyecto.",
  "files": [
    {
      "path": "app.py",
      "purpose": "Punto de entrada.",
      "used_when": "Al iniciar la aplicación.",
      "explanation": "Lee la configuración y arranca el servidor.",
      "parameters": "`PORT` cambia el puerto.",
      "lines": [1, 12]
    }
  ],
  "sources": [],
  "phases": [
    {
      "id": "arranque",
      "title": "Cómo arranca",
      "flow": ["Lee configuración", "Crea servidor", "Escucha"],
      "sections": [
        { "title": "Entrada", "text": "El programa empieza en app.py." }
      ],
      "files": ["app.py"],
      "story": {
        "request": "Necesitamos un servidor local.",
        "interpretation": "Un solo proceso y un puerto configurable.",
        "decision": "Se usa la biblioteca estándar para evitar dependencias.",
        "alternatives": [
          { "name": "Framework externo", "tradeoff": "Más funciones, más dependencias." }
        ],
        "walkthrough": [
          { "title": "Arranque", "text": "Se crea y se pone a escuchar.", "file": "app.py", "lines": [5, 9] }
        ],
        "difficulties": ["El puerto fijo impedía dos instancias; se hizo configurable."],
        "result": "Al iniciar app.py se espera un proceso escuchando en el puerto elegido por PORT. Una conexión HTTP a ese puerto permite comprobarlo. No se ejecutó el proceso en esta guía."
      }
    }
  ]
}
```
