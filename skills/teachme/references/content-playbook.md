# Convertir un proyecto en un recorrido que enseña

El visor no es un índice de archivos ni una documentación autogenerada. Cada fase debe dejar a la persona capaz de **explicar una decisión y modificarla**. Si una fase solo enumera comandos o reproduce el README, no sirve.

## Arco de cada fase

1. **Pedido**: una necesidad concreta, en una frase.
2. **Interpretación**: qué requisitos se derivan de ese pedido y cuáles se descartan.
3. **Decisión**: la pieza que resuelve el problema y por qué se eligió.
4. **Alternativas**: qué otra forma existía y qué se gana/pierde con ella.
5. **Código**: dónde y cómo está implementado, con líneas reales.
6. **Dificultad**: qué falló, qué restricción apareció o qué se aprendió.
7. **Transferencia**: qué cambiaría en otro proyecto y cómo verificarlo.

Este orden es el que ya usan los tutoriales de MAAS y Foreman de `evaluacionpractica02`; consérvalo para que el resultado se sienta igual.

## Selección de contenido

Empieza por el flujo que un nuevo colaborador necesita para no romper nada:

- Punto de entrada y arranque.
- Modelo de datos o estructura central.
- Flujo principal de punta a punta.
- Configuración y parámetros que cambian el comportamiento.
- Manejo de errores, reintentos, permisos o límites.
- Pruebas y verificación real.
- Operación, despliegue o migración.
- Adaptación a otro entorno.

Deja fuera lo accesorio. Si el proyecto tiene diez módulos, elige el camino que explica la arquitectura; menciona los demás en `scope` o en una alternativa.

## Plantilla de fase

```text
id: verbo-sustantivo
title: Problema concreto, no "Introducción"
flow: 3–5 pasos del recorrido
files: 1–4 archivos que realmente se leen
sections: 2–4 bloques para el modo texto
story:
  request: necesidad del usuario
  interpretation: requisitos y exclusiones
  decision: pieza elegida y fundamento
  visual: diagrama solo si aclara una relación
  alternatives: al menos una, con costo real
  walkthrough: 2–5 pasos con archivo y líneas
  difficulties: al menos un problema real
  transfer: adaptación verificable
```

### Buenos títulos

- "Cómo se separan las redes de gestión y provisión"
- "Qué pasa desde el pedido hasta la escritura en disco"
- "Dónde se decide el reintento y qué evita duplicados"
- "Cómo se valida una entrada antes de tocar la base"

### Títulos que no sirven

- "Introducción"
- "Instalación"
- "Archivos importantes"
- "Resumen"
- "Conceptos básicos"

## Cómo escribir el relato

- Usa frases cortas y concretas. Explica el **porqué** antes del comando.
- Nombra los parámetros y su efecto: "`timeout` en segundos; si se agota, el cliente reintenta una vez".
- Cita archivo y líneas reales. Si el código cambió, actualiza el rango y vuelve a validar.
- Distingue tres niveles de evidencia:
  - **Implementado**: está en el repositorio y se puede leer.
  - **Observado**: se ejecutó y se registró una salida o un estado.
  - **Alternativa**: no está implementado; se propone.
- No presentes una salida esperada como si fuera un resultado obtenido.
- No inventes credenciales, direcciones, versiones ni fechas. Si no las sabes, omítelas o indica que no se verificaron.

## Diagramas

Un diagrama vale la pena cuando muestra:

- una topología o separación de redes;
- un flujo entre componentes;
- capas y responsabilidades;
- estados y transiciones;
- una comparación de caminos.

No lo uses para repetir una lista. Cada flecha debe tener un significado que el pie de figura explique. Prefiere SVG editable y verifica que el texto no quede cortado. Si no puedes renderizarlo, no lo declares verificado.

## Archivos y fragmentos

- Declara entre 6 y 14 archivos; menos de 6 suele dejar el recorrido sin evidencia.
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
| Citar archivos que no existen | Ejecutar el validador y corregir rutas. |
| Rangos de líneas desactualizados | Leer el archivo y ajustar `lines`; volver a validar. |
| Fases de una sola frase | Agregar interpretación, alternativa y walkthrough real. |
| Diagramas decorativos | Quitarlos o rehacerlos para que expliquen una relación. |
| Mezclar progreso de estudio con estado del proyecto | Mantenerlos separados; el visor solo guarda lectura y dudas. |
| Prometer que el proyecto "funciona" | Decir qué se leyó, qué se ejecutó y qué no se verificó. |

## Criterio de cierre

Antes de entregar, pregúntate:

- ¿Puede alguien explicar el flujo principal sin abrir el código?
- ¿Sabe dónde cambiar un parámetro y qué efecto tendrá?
- ¿Conoce al menos una alternativa y su costo?
- ¿Distingue lo implementado de lo observado y de lo propuesto?
- ¿Cada fase cita código real y tiene una transferencia accionable?

Si alguna respuesta es no, falta contenido, no formato.
