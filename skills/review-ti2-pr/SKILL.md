---
name: review-ti2-pr
description: Revisa Pull Requests existentes de TI2 como integrante de TI4 usando los criterios académicos, arquitectónicos, de privacidad, integración y trazabilidad del proyecto. Prepara un borrador primero y publica la revisión solo con confirmación explícita.
metadata:
  scope: local
  team: TI4
---

# Revisión de PR de TI2

Usa esta skill cuando una persona de TI4 deba revisar una Pull Request existente de TI2 en el proyecto correspondiente. Su objetivo es detectar problemas que puedan impedir la integración, explicar el criterio para que la persona autora gane autonomía y dejar una decisión sustentada en evidencia.

Esta skill complementa `code-review`, `file-pr` y `babysit-pr`. Usa `code-review` para una revisión genérica en dos ejes, `file-pr` para abrir una PR y `babysit-pr` para seguir una PR existente. Aquí el foco es el contexto académico y técnico del proyecto.

## Límites de actuación

- La primera fase es siempre de solo lectura sobre la PR ajena. Prepara el veredicto y los comentarios, pero no publiques, apruebes ni solicites cambios hasta que la persona usuaria confirme el borrador exacto.
- Después de una confirmación explícita, puedes publicar únicamente los comentarios inline aprobados y la decisión de revisión propuesta. No hagas merge ni modifiques etiquetas, revisores u otros metadatos de GitHub.
- La revisión no modifica código ajeno. Deriva los límites de ownership de las instrucciones y documentos vigentes del repositorio autorizado.
- Exige coordinación documentada cuando la PR cruce los límites de ownership establecidos por el proyecto. No inventes reglas de equipos si no están documentadas.
- La persona autora corrige su propia rama. Un comentario de revisión debe señalar el problema, explicar el criterio y orientar una solución razonable sin imponer una reescritura innecesaria.
- No conviertas una revisión en una auditoría general. Inspecciona el código atravesado por el cambio y las dependencias que puedan romperse, y registra oportunidades concretas de simplificación solo si afectan la PR.
- No solicites `@codex review` automáticamente. Una revisión automática se verifica contra el código igual que cualquier otro comentario.

## Contexto que debes cargar

Lee esta referencia antes de revisar una PR: [contexto de revisión TI2](references/contexto-ti2-cereti.md). Cuando el issue o la PR requieran más detalle, consulta las fuentes originales que la referencia enumera, en especial el issue de Linear y los documentos del repositorio.

La fuente de verdad para el alcance es el issue de Linear asociado, la descripción de la PR y el incremento o Sprint correspondiente. No exijas como faltante una funcionalidad que el plan haya diferido, y no aceptes como justificación que algo futuro sea necesario para el alcance actual.

## Flujo de revisión

### 1. Fijar el objeto de revisión

Resuelve la PR por URL, número, rama o el contexto entregado por la persona usuaria. Confirma repositorio, rama base, rama de origen, commit `head`, estado Draft o Ready, issue de Linear, aprobaciones, conversaciones pendientes y checks visibles.

Si no puedes identificar una PR inequívoca o no puedes fijar un commit, detente y pide ese dato. No revises un diff que pueda cambiar mientras lo analizas.

Determina el punto de comparación con el merge-base de la rama base y la rama de la PR. Usa el mismo punto durante la revisión:

```bash
git merge-base <base> <head>
git diff --check <merge-base>...<head>
git diff --stat <merge-base>...<head>
git diff <merge-base>...<head>
git log --oneline <merge-base>..<head>
```

Si solo tienes un checkout local, documenta qué ramas y commits representan la PR. Si la base, el `head` o el issue no están disponibles, informa la limitación en vez de inventar contexto.

### 2. Entender el alcance

Lee el issue, los criterios de aceptación, la descripción de la PR y los commits. Identifica qué comportamiento cambia, qué capas toca, qué contrato consume o modifica y qué trabajo queda expresamente fuera de alcance.

Comprueba la trazabilidad `Linear -> branch -> commits -> PR`. Una PR puede ser una parte de un issue, pero debe explicar su dependencia con otras PR cuando el issue tenga varios incrementos.

Clasifica los archivos modificados por ownership según la documentación del repositorio. Si una PR altera contratos consumidos por otro equipo, exige coordinación y evidencia del impacto conforme al alcance acordado.

### 3. Revisar con los cinco lentes

Aplica los lentes en este orden. No marques un hallazgo solo porque el código podría escribirse de otra forma; exige una consecuencia observable, una regla del proyecto o un requisito del issue.

1. **Comportamiento y requisitos.** Verifica criterios de aceptación, estados válidos, errores, casos límite, idempotencia cuando corresponda y compatibilidad con el lenguaje del proyecto.
2. **Arquitectura y ownership.** Verifica dirección de dependencias, límites de capa, punto de entrada de la API y que cada equipo cambie solo las áreas que le corresponden.
3. **Seguridad y privacidad.** Verifica autenticación, autorización en Backend, minimización, datos ficticios, secretos y exposición de información sensible.
4. **Pruebas y operación.** Verifica pruebas proporcionales, typecheck, lint, build, CI, migraciones o índices cuando correspondan y evidencia reproducible.
5. **Integración y trazabilidad.** Verifica contrato compartido, impacto en Web y Mobile, Linear, documentación, dependencias, estado de la PR y Definition of Done.

### 4. Validar los hallazgos

Para cada posible hallazgo, lee el contexto suficiente fuera del hunk: tipos, callers, tests, funciones públicas, repositorios, esquema y contrato que lo consumen. Ejecuta solo validaciones de lectura o comandos de prueba que no modifiquen el repositorio, y registra exactamente lo que ejecutaste.

Prioriza así:

- **Bloqueante:** vulnerabilidad, pérdida o exposición de datos, incumplimiento de un requisito central, corrupción de estado, autorización evadible, contrato roto, incumplimiento de ownership que obligue a retirar cambios antes de integrar o fallo que impide integrar o usar el incremento.
- **Importante:** error funcional real, incumplimiento de una regla arquitectónica relevante, prueba ausente para un riesgo concreto o cambio de integración sin coordinación que puede romper otro componente.
- **Menor:** problema acotado que no bloquea la integración, pero conviene corregir ahora para evitar confusión, deuda o una regresión cercana.

No eleves una preferencia personal a hallazgo. Si una decisión es discutible pero válida, formula una pregunta o una sugerencia separada de los cambios solicitados.

### 5. Proponer la revisión

Entrega primero la decisión: `Cambios solicitados`, `Aprobable con observaciones menores` o `Aprobable`, según la autorización y el estado real de la revisión. Si la PR no tiene checks o evidencia necesarios, no la presentes como aprobable; indica qué falta verificar.

Cada hallazgo debe tener esta forma:

```md
### [Bloqueante] ruta/al/archivo.ts:42

El cambio permite [...].

Esto incumple [...]. La consecuencia es [...].

Corrige [...]. Comprueba [...].
```

Usa la línea más pequeña que explique el problema. Cita el requisito, regla, contrato o evidencia que sustenta el hallazgo. Si no hay hallazgos, dilo de forma explícita y enumera las limitaciones o validaciones pendientes.

Además del informe técnico dirigido a la persona usuaria, termina siempre con una sección separada titulada `## Comentarios inline listos para copiar en la PR`. Esta sección debe ser una lista de comentarios individuales, pareados con el archivo y la línea exacta de la modificación a la que corresponden, para que la persona usuaria pueda llevar cada uno a una conversación inline de GitHub:

- Cada entrada debe contener, en este orden, el archivo, la línea exacta del diff, la severidad y el texto completo del comentario que se publicaría en esa ubicación.
- Usa la línea modificada más pequeña que explique el problema. No apuntes a un archivo completo ni a una línea fuera del diff si existe un ancla adecuada dentro de la modificación.
- Crea una entrada separada por cada hallazgo que requiera una acción. No agrupes en un comentario problemas de archivos o causas distintas.
- El comentario debe resumir solo el problema que la persona autora debe atender, explicar el criterio y formular una acción concreta con la validación esperada. Empieza directamente con el hallazgo: no agregues saludos, felicitaciones, introducciones genéricas ni cierres de cortesía.
- Cuando haya cambios fuera del ownership documentado, nombra el límite, la fuente que lo establece y la acción necesaria.
- Mantén la firmeza sin descalificar: habla del cambio, su efecto y el criterio del proyecto, nunca de la capacidad o el desempeño de la persona.
- No copies el informe completo, no incluyas notas internas, limitaciones de herramientas, referencias a esta skill ni decisiones que solo correspondan a TI4.
- Si el hallazgo afecta a la PR completa y no tiene una línea modificada razonable, usa una entrada marcada como `Comentario general de la PR` y explica por qué no corresponde un anclaje inline.
- Si no hay cambios solicitados, indica `Sin comentarios inline` y agrega, cuando corresponda, un único `Comentario general de la PR` con la aprobación u observaciones menores y lo que queda pendiente.
- Usa esta estructura guiada:

  ```md
  ## Comentarios inline listos para copiar en la PR

  1. `ruta/al/archivo.ts:42` · **Importante**

     **Comentario para publicar en esa línea:**

     > Explica el problema, el criterio incumplido, la consecuencia y la acción concreta.

  2. `ruta/al/otro-archivo.md:18` · **Menor**

     **Comentario para publicar en esa línea:**

     > Corrige [...]. Comprueba [...].
  ```

- Cierra el borrador con una pregunta de confirmación clara: "¿Te parece bien que publique esta revisión y estos comentarios en el commit `<head>`?". Espera una respuesta explícita antes de escribir en GitHub.

### 6. Publicar tras la confirmación

Después de que la persona usuaria confirme el borrador:

1. Vuelve a consultar la PR y verifica que el `head` sigue siendo el commit revisado. Si cambió, no publiques comentarios sobre un diff que puede haber quedado obsoleto: revisa los cambios nuevos y presenta un borrador actualizado.
2. Publica cada comentario inline aprobado en su archivo y línea. Conserva el texto acordado; no agregues observaciones nuevas durante la publicación.
3. Envía la decisión propuesta después de publicar los comentarios: solicitar cambios, aprobar o comentar, según el borrador confirmado.
4. Comprueba que GitHub registró la decisión y cada comentario. Informa las URLs o ubicaciones publicadas. Si una publicación falla, explica cuál falló y no dupliques los comentarios que ya se crearon.

Antes de cerrar la respuesta, aplica `unslop` tanto al informe como al comentario listo para copiar. Hazlo solo sobre la prosa: conserva exactamente comandos, rutas, identificadores, logs, citas textuales, bloques de código y datos técnicos.

El cierre debe incluir:

- PR, base, `head` y estado observado.
- Archivos o áreas revisadas.
- Hallazgos por severidad, sin esconder los bloqueantes entre sugerencias.
- Validaciones ejecutadas y resultado real.
- Checks, aprobaciones y conversaciones pendientes.
- Riesgos de integración con Web, Backend, Base de Datos o Mobile.
- Qué debe hacer la persona autora o qué decisión humana queda pendiente.
- Una sección `## Comentarios inline listos para copiar en la PR`, separada del informe técnico, con cada hallazgo pareado con `archivo:línea` y su comentario exacto.
- Si corresponde, un `Comentario general de la PR` separado para asuntos sin un anclaje razonable en una línea modificada.

## Regla de comunicación con TI2

Habla del cambio, no de la persona. Explica el porqué con el vocabulario del proyecto y ofrece una dirección concreta. En el informe dirigido a la persona usuaria puedes desarrollar el contexto; en el comentario para la PR usa una voz senior: directa, firme y respetuosa. La revisión debe ayudar a TI2 a resolver la tarea con más autonomía, no trasladar a TI4 la implementación ni convertir la aprobación en una inspección de estilo.

## Voz clara y cercana

Escribe como alguien que revisa el trabajo junto al equipo. Empieza por el efecto que verá una persona usuaria, un cliente o el siguiente equipo, y explica el detalle técnico solo cuando ayude a entenderlo.

- Prefiere frases cortas y palabras cotidianas. Por ejemplo, "Mobile no puede usar este tipo todavía" explica mejor el problema que "existe una incompatibilidad de contrato".
- En cada hallazgo, cuenta una historia breve: qué queda mal ahora, por qué importa y qué cambio permite cerrarlo. No recites todas las capas, reglas o herramientas si una sola evidencia basta.
- Reserva las rutas, tipos, commits, requisitos y comandos para respaldar una afirmación o indicar exactamente dónde actuar. No los uses como sustituto de la explicación.
- Los comentarios inline deben sonar como una conversación de revisión útil: describe el efecto, pide una acción concreta y termina con la comprobación esperada. Evita frases jurídicas o impersonales como "esto incumple" cuando "esto deja a Mobile sin un contrato utilizable" sea más claro.
- Mantén la firmeza cuando el cambio bloquea la integración. Ser cercano no significa suavizar un requisito ni convertir un cambio solicitado en una sugerencia.
