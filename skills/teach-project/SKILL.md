---
name: teach-project
description: Convierte cualquier proyecto en una guía local por fases ("enséñame de este proyecto"), con narrativa de decisiones, código real, diagramas, progreso de lectura, panel de dudas y exportación para el agente. Úsala cuando el usuario pida enseñarle, explicarle o hacer un recorrido guiado de un proyecto o repositorio, o invoque teach-project.
---

# Enseñar un proyecto con teach

Activa esta skill cuando el usuario diga cosas como **"enséñame de este proyecto"**, "explícame este repo por fases", "hazme un teach de esto", "quiero un recorrido guiado del proyecto", "revísalo conmigo paso a paso" o invoque `$teach-project`. No la uses para un resumen corto ni para una pregunta puntual: para eso responde directamente.

La skill instala en el proyecto el mismo visor que ya funciona en `evaluacionpractica02`: servidor local con token, fases navegables, código real con líneas, diagramas, progreso guardado, panel **Mis dudas**, copiar/descargar/limpiar y exportación para el agente. El resultado se abre con `./teach` desde la raíz del proyecto.

## Resultado esperado

En la raíz del proyecto deben quedar:

```text
tutorial.json          # contenido: fases, archivos, fuentes y relato
teach                  # lanzador ejecutable
.teach/engine/         # motor copiado desde esta skill
.teach/state/          # progreso y dudas locales
diagramas/             # opcional: SVG/PNG propios citados por las fases
.gitignore             # bloque gestionado con todos los artefactos anteriores
```

Todo ese material es local: el instalador lo agrega a `.gitignore` dentro de un bloque gestionado. No lo dejes versionado en el proyecto.

No modifiques el código del proyecto para "prepararlo". El visor solo lee archivos públicos declarados en `tutorial.json`; no ejecuta el proyecto, no instala dependencias y no toca sus servicios. Esta skill reproduce el recorrido educativo de `teach`, no los subcomandos operativos `teach lab` que pertenecen a los laboratorios originales.

## Flujo obligatorio

### 1. Reconocer el proyecto antes de escribir

Lee, sin modificar:

- `README`, `docs/`, `CONTRIBUTING`, `Makefile`, manifiestos (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.).
- Puntos de entrada, configuración, esquemas, migraciones, pruebas y CI.
- `git log --oneline -20` y `git status` para entender el estado real y no inventar historia.
- Los archivos que piensas citar, con sus líneas exactas.

Construye una tabla mental de evidencia: afirmación → archivo:línea o fuente oficial. Si algo no está en el repositorio, no lo presentes como implementado.

### 2. Diseñar las fases

Aplica el arco narrativo del teach existente:

```text
qué se necesitaba → cómo se interpretó → qué se decidió → cómo lo hace el código
→ qué alternativas había → qué dificultades aparecieron → cómo adaptarlo
```

Reglas:

- Entre **6 y 10 fases** para un proyecto completo (el validador acepta 2–12; menos de 5 es un aviso fuerte).
- Cada fase resuelve **un problema técnico concreto**, no un capítulo genérico ("Introducción", "Instalación").
- La primera fase fija propósito, alcance y límites. La última cierra con adaptación, verificación y fuentes.
- Cada fase enlaza **1–4 archivos reales**. Si una fase no puede citar código, replantéala o conviértela en contexto breve.
- Distribuye: arquitectura, flujo de datos, decisiones, piezas críticas, errores/dificultades, operación/verificación y transferencia.
- Español por defecto; conserva el idioma del proyecto solo si el usuario lo pide.

Lee `references/content-playbook.md` para la plantilla de fase, los criterios de calidad y ejemplos.

### 3. Escribir `tutorial.json`

Usa el esquema completo de `references/schema.md`. Mínimo por fase:

- `id` estable en kebab-case, `title`, `flow` (3–5 pasos) y `sections` (2–4) para el modo texto.
- `story.request`, `interpretation`, `decision`, `transfer`.
- `story.alternatives` (al menos una con `name` y `tradeoff`).
- `story.walkthrough` (2–5 pasos con `file` y `lines` reales).
- `story.difficulties` (al menos una).
- `story.visual` solo si existe el diagrama; `file` es el nombre dentro de `diagramas/`.
- `files` con `path`, `purpose`, `used_when`, `explanation`, `parameters` y `lines`.
- `sources` con documentación oficial y `consulted` (fecha). No uses tutoriales secundarios.
- `scope` debe decir qué **no** cubre la guía y qué evidencia es histórica.

El contenido debe permitir modificar el proyecto, no memorizar comandos. Distingue siempre "el repositorio hace esto" de "esto se observó en una ejecución" y de "esto sería una alternativa".

### 4. Crear diagramas (opcional pero recomendado)

- Guarda SVG o PNG reales en `<proyecto>/diagramas/`.
- Cita solo el nombre del archivo en `story.visual.file`.
- Cada diagrama debe explicar una relación que el texto no muestra mejor: flujo, topología, capas, estados o dependencias.
- Si usas una herramienta de diagramas, verifica que el archivo abra y que no tenga etiquetas cortadas. Si no hay herramienta disponible, omite el diagrama y dilo; no inventes una imagen.
- Entre 2 y 6 diagramas para un recorrido completo; no decores.

### 5. Instalar el motor

```bash
PROJECT=/ruta/al/proyecto
python3 "$HOME/.codex/skills/teach-project/scripts/install.py" "$PROJECT"
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

No pidas confirmación para ignorar esos artefactos: es parte obligatoria del flujo. Verifica el bloque antes de entregar y no lo elimines ni lo reemplaces por reglas parciales.

### 6. Validar y probar de verdad

```bash
python3 "$HOME/.codex/skills/teach-project/scripts/validate_tutorial.py" "$PROJECT"
python3 "$HOME/.codex/skills/teach-project/scripts/smoke_test.py" "$PROJECT"
"$PROJECT/teach" fases
"$PROJECT/teach" archivos
```

Corrige **todos** los errores del validador. Los avisos son criterios de calidad: justifica los que decidas dejar. El smoke test comprueba bootstrap, archivos, duda, exportación, limpieza y cierre sin tocar el progreso real.

### 7. Verificar el visor y entregar

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

Al terminar, entrega:

1. Ruta de `tutorial.json`, número de fases y archivos citados.
2. Comando exacto para abrir: `./teach`.
3. Qué verificaste realmente y qué quedó pendiente.
4. Advertencia de no incluir credenciales, tokens, llaves ni artefactos de VM en el contenido.

## Reglas duras

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
