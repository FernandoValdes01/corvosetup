---
name: commit-workflow
description: Prepara commits profesionales en cualquier repositorio, incluidos proyectos TypeScript, cuando el usuario solicite hacer commits o guardar cambios. Usa un formato con tipo y área entre paréntesis, separa cambios independientes y no incluye IDs de tareas salvo instrucción explícita.
---

# Commits profesionales

Usa esta skill automáticamente cuando el usuario pida hacer, crear, preparar o guardar commits. También se aplica cuando el usuario autorice explícitamente la creación de commits como parte de otra tarea. La skill no autoriza por sí sola un commit: respeta la autorización de la solicitud actual.

## Formato obligatorio

Cada commit debe tener esta forma, con el área entre paréntesis siempre presente:

```text
tipo(área): descripción breve en imperativo
```

El `área` representa dónde se realizó el cambio: un módulo, directorio, capa o dominio. Debe ser concreta y útil para leer el historial, por ejemplo `api`, `frontend`, `auth`, `shared`, `types`, `tests`, `docs`, `latex` o `infra`. No debe ser un ID de tarea, una rama, el nombre del usuario ni un texto vacío.

El `tipo` debe describir la intención principal:

- `feat`: funcionalidad nueva.
- `fix`: corrección de un error.
- `docs`: documentación.
- `refactor`: reestructuración sin cambio funcional intencional.
- `test`: pruebas.
- `chore`: mantenimiento sin cambio funcional de producto.
- `build`: dependencias o configuración de compilación.
- `ci`: integración o despliegue continuo.
- `perf`: mejora de rendimiento.
- `style`: formato o estilo sin cambio de comportamiento.

Ejemplos válidos:

```text
feat(auth): agrega validación de sesión expirada
fix(api): evita respuestas duplicadas al reintentar
docs(latex): actualiza las instrucciones de compilación
test(frontend): cubre el estado vacío de la lista
build(types): ajusta la configuración de TypeScript
```

## Reglas de contenido

- Escribe una descripción clara, específica y profesional, preferiblemente en imperativo y sin punto final.
- Usa el idioma dominante del repositorio; si no hay una señal clara, usa español cuando la solicitud esté en español.
- No inventes nombres vagos como `cambios`, `updates`, `stuff`, `misc` o `mejoras varias`.
- No pongas IDs de tareas, issues o tickets en el título ni en el cuerpo. Por ejemplo, no uses `tarea001feat`, salvo que el usuario lo pida expresamente. Las referencias de tarea pertenecen normalmente a la pull request.
- No agregues referencias a una tarea solo porque aparezcan en el nombre de la rama, en el contexto de la conversación o en archivos del proyecto.
- No uses `feat` para documentación, pruebas, configuración o correcciones; el tipo debe coincidir con el cambio real.
- Añade un cuerpo únicamente si aporta contexto técnico relevante. No lo uses para compensar un título ambiguo ni para repetir la tarea.

## Separación de cambios

Antes de crear commits, inspecciona `git status`, el diff completo y, cuando ayude, el historial reciente. Identifica unidades coherentes de cambio y separa automáticamente los cambios independientes en commits distintos cuando puedan seleccionarse sin mezclar hunks.

Por ejemplo, una nueva funcionalidad y una corrección de documentación deben producir, si el diff lo permite:

```text
feat(frontend): agrega selector de perfiles
docs(docs): explica la configuración del selector
```

Un cambio coherente que atraviesa varios directorios puede permanecer en un solo commit; en ese caso usa como área el dominio principal, no una lista de rutas. Si dos cambios no pueden separarse con seguridad, explica la limitación antes de crear un commit combinado. Si el usuario pide explícitamente un único commit, respeta esa decisión.

Nunca uses `git add .` o `git commit -a` sin revisar qué cambios entrarían. Excluye modificaciones previas o archivos no relacionados que no formen parte de la solicitud. Verifica el staged diff antes de ejecutar cada commit.

## Verificación y límites

1. Revisa el estado, el diff y los archivos que se incluirán.
2. Clasifica cada unidad por tipo y área.
3. Ejecuta las comprobaciones relevantes y razonables para el cambio si el proyecto las tiene.
4. Crea los commits con el formato exacto `tipo(área): descripción`.
5. Comprueba `git status` y muestra los hashes y títulos resultantes.

No hagas `push`, `rebase`, `reset`, `clean`, `checkout`, `restore` ni `amend` salvo que el usuario lo solicite explícitamente. No reescribas commits existentes para corregir el formato sin autorización expresa.
