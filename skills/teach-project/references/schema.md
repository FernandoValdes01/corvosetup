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
    "interpretation": "Cómo se tradujo ese pedido en requisitos técnicos.",
    "visual": {
      "file": "flujo-alta.svg",
      "alt": "Flujo de validación, permisos y persistencia.",
      "caption": "Cada capa recibe el recurso ya validado."
    },
    "decision": "Decisión principal y su fundamento.",
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
    "transfer": "Para otro proyecto, separa primero el esquema de entrada del modelo de persistencia."
  }
}
```

| Campo | Obligatorio | Uso |
| --- | --- | --- |
| `id` | Sí | Kebab-case único; se guarda en el progreso. |
| `title` | Sí | Título visible de la fase. |
| `flow` | Recomendado | 3–5 pasos que resumen el recorrido. |
| `sections` | Sí | 2–4 secciones para el modo texto y la lectura lineal. |
| `files` | Recomendado | Rutas del catálogo que pertenecen a la fase. |
| `story` | Recomendado | Relato principal del visor web. Sin `story` se usa `sections`. |
| `story.request` | Sí si hay `story` | Pedido que abre la fase. |
| `story.interpretation` | Sí si hay `story` | Traducción del pedido a requisitos. |
| `story.decision` | Sí si hay `story` | Decisión técnica y por qué. |
| `story.transfer` | Sí si hay `story` | Cómo llevarlo a otro proyecto. |
| `story.visual` | Opcional | `file` (nombre en `diagramas/`), `alt`, `caption`. |
| `story.alternatives` | Recomendado | Lista de `{name, tradeoff}`. |
| `story.walkthrough` | Recomendado | Pasos con `title`, `text`, `file`, `lines`. |
| `story.difficulties` | Recomendado | Lista de problemas reales y su resolución. |

## Fuentes (`sources[]`)

```json
{
  "title": "Documentación oficial de la API",
  "url": "https://ejemplo.com/docs/api",
  "consulted": "2026-10-24"
}
```

Usa documentación oficial del creador o mantenedor. No sustituyas el manual por blogs o tutoriales secundarios. Registra la fecha de consulta.

## Ejemplo mínimo completo

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
        "transfer": "En otro proyecto, valida primero el puerto y falla con un mensaje claro."
      }
    }
  ]
}
```
