---
name: jflap
description: Disena, genera, valida y simula automatas finitos (AFD/AFN) y archivos .jff de JFLAP 7.1. Usa esta skill automaticamente cuando el usuario mencione JFLAP, .jff, automata, AFD, AFN, NFA, DFA, pila, PDA, Turing, gramatica, expresion regular, tabla o diagrama de transiciones, simular cadenas, teoria de la computacion, INFO1148, o pida abrir/generar/probar un automata. Siempre opera via el MCP jflap (file-based, sin GUI).
---

# JFLAP

Opera JFLAP 7.1 sin abrir la GUI: generas, lees, validas y simulas `.jff` via el MCP `jflap`.

## Auto-invocacion

Usa esta skill automaticamente cuando detectes cualquiera de:

- `JFLAP`, `jflap`, `.jff`, `.JFF`
- `automata`, `autómata`, `AFD`, `AFN`, `DFA`, `NFA`, `PDA`, `Turing`, `gramática`, `expresión regular`
- `tabla de transiciones`, `diagrama de transición`, `delta`, `simular cadena`, `probar cadena`
- `teoría de la computación`, `teoria computacion`, `INFO1148`, `sesion_TC`, `actividad TC`
- paths `Documentos/ramos/teoriacomputacion`, `JFLAP7.1`, `ejecutar-jflap.sh`

No pidas permiso para activarla: aplicala y menciona que lo hiciste en una linea.

## Herramientas MCP (nombres segun cliente)

Opencode: `jflap_info`, `jflap_create_fa`, `jflap_validate`, `jflap_simulate`, `jflap_parse_jff`.
Codex: mismo nombre con prefijo `mcp__jflap__` (ej. `mcp__jflap__jflap_info`).

Si las tools no existen en la sesion, dilo y trabaja en Python puro con el mismo formato, sin fingir una llamada MCP.

## Flujo obligatorio

1. `jflap_info` primero: confirma `JFLAP7.1-fixed.jar`, `ejecutar-jflap.sh` y `java`. Nunca inventes rutas del jar.
2. Definir el automata como datos, no como dibujo:
   - `states: ["q0","q1",...]`, `alphabet: ["0","1"]`, `initial: "q0"`, `finals: ["q1"]`
   - `transitions: [{from, read, to}]`, `read=""` es lambda (AFN). `read` de 1 simbolo maximo.
3. `jflap_validate` antes de entregar: revisa `is_dfa`, `has_lambda`, `missing_transitions`, `unreachable`, `dead_states`. Si el usuario pidio AFD y hay `has_lambda` o `nondet_pairs`, corrigelo.
4. `jflap_simulate` con las cadenas del enunciado + 1 aceptada y 1 rechazada de control.
5. `jflap_create_fa` con `save_path` absoluto terminado en `.jff` (ej. `@HOME@/Documentos/ramos/teoriacomputacion/actividades/actividad24-08/mi_afd.jff`). Verifica con `jflap_parse_jff file_path=<mismo>`.
6. Cierre: indica ruta `.jff`, resultado de `validate`, tabla aceptada/rechazada, y como abrirlo: `@HOME@/Documentos/ramos/teoriacomputacion/ejecutar-jflap.sh <ruta.jff>`.

## Formato .jff (FA, JFLAP 7.1 via FSATransducer)

```xml
<structure><type>fa</type><automaton>
<state id="0" name="q0"><x>..</x><y>..</y><initial/><final/></state>
<transition><from>0</from><to>1</to><read>a</read></transition>
</automaton></structure>
```

`<read/>` vacio = lambda. Los `id` los asigna el MCP en orden de `states`.

## Reutilizar codigo del ramo

Tus actividades ya modelan `TRANSICIONES[estado][simbolo]` (`actividad17-08/`, `actividad24-08/ejercicio1_afd.py`, `ejercicio2.py`). Convertirlas es mecanico:

```python
transitions=[{"from": s, "read": sym, "to": d}
             for s, mp in TRANSICIONES.items() for sym, d in mp.items()]
```

## Limites v0.1.0

- Solo `<type>fa</type>`. PDA/TM/gramaticas/regex: explica que el MCP las rechaza en vez de improvisar el XML.
- Simulacion BFS con cierre-lambda en Python, no es el simulador Java interno de JFLAP.
- No automatiza la ventana Swing. No uses `open_drawio_*` ni GUI para esto.
