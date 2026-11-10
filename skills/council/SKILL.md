---
name: council
description: Reúne un consejo de modelos para debatir una pregunta, contrastar posturas y sintetizar una recomendación. Úsala cuando el usuario invoque council o pida un consejo o debate entre modelos.
metadata:
  origin: warpdotdev/common-skills
---

# Council multimodelo

Organiza una discusión sobre la pregunta del usuario, con respuestas independientes y una ronda de contraste. El orquestador decide la síntesis según la calidad de la evidencia, no por votación. No inventes respuestas ni ejecuciones.

## Integrantes y ejecución en T3 Code

Consulta `orchestrator_capabilities` una vez por hilo antes de la primera delegación y verifica los proveedores, modelos y opciones. Usa `delegate_task` para cada integrante y para cada nueva revisión; no uses `t3_thread_send`, CLI ni sustituciones silenciosas. Respeta sus instrucciones de continuación y no sondees tareas activas. Como máximo dos subagentes simultáneos por sesión; inicia los tres integrantes en tandas.

Consejo predeterminado, sujeto a disponibilidad y a las restricciones de delegación aplicables:

- Codex `gpt-6.1-sol`, opción `reasoningEffort: low`: solidez, síntesis y decisiones prácticas.
- OpenCode `opencode/deepseek-v4.1-flash-free`: alternativas y viabilidad.
- OpenCode `opencode/glm-5.3-flash-free`: crítica, supuestos y riesgos.

Usa los identificadores y opciones exactos que devuelva el catálogo. Si un integrante no está disponible o una restricción vigente impide lanzarlo, indícalo y sigue con los demás; no afirmes que participó ni lo reemplaces sin petición del usuario. Solo agrega otros modelos OpenCode que el catálogo identifique claramente como gratuitos cuando el usuario pida más integrantes; informa cuáles. No supongas que un modelo es gratuito por pertenecer a OpenCode. Los límites del servicio, cuotas y disponibilidad pueden cambiar.

Si no estás en T3 Code, usa las herramientas de delegación del entorno solo si permiten verificar proveedor, modelo y opciones; de lo contrario informa la limitación. No eludas restricciones de capacidad, autorización o concurrencia mediante otro mecanismo.

## Discusión

1. Delimita la pregunta, el contexto necesario y los criterios de decisión. Cada miembro recibe un ángulo distinto y produce su propia respuesta sin ver las otras. Pide evidencias, supuestos, recomendación, objeción principal e incertidumbre. Limita el contexto a lo necesario y excluye secretos.
2. Resume fielmente las respuestas y desacuerdos. Inicia una segunda ronda acotada con nuevas delegaciones para que al menos dos integrantes contrasten la postura rival y respondan a la objeción más fuerte. Si faltan integrantes o la ronda no puede ejecutarse, explica la limitación. No presentes respuestas independientes como una discusión que ocurrió.
3. Entrega la recomendación, sus razones, la mejor objeción, los desacuerdos que siguen abiertos y qué modelos participaron realmente. Menciona sustituciones solo si el usuario las pidió. No conviertas la discusión en autorización para modificar archivos o enviar mensajes.

Por defecto la investigación es de solo lectura: instruye a los integrantes a no editar, publicar, crear ramas ni hacer commits. Si el usuario solicita implementación, coordina el trabajo conforme a las instrucciones vigentes y evita escritores simultáneos en el mismo checkout.
