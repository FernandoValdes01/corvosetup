"""Nucleo .jff para automatas finitos: build / parse / validate / simulate.

Reusa la convencion de tus actividades (ESTADOS/ALFABETO/TRANSICIONES dict),
pero serializa al XML que JFLAP 7.1 lee via file/xml/FSATransducer.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class Transition:
    frm: str
    read: str  # "" = lambda
    to: str


def _indent(elem: ET.Element, level: int = 0) -> None:
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def build_fa_jff(
    states: list[str],
    alphabet: list[str],
    initial: str,
    finals: list[str],
    transitions: list[dict],
) -> str:
    """Construye el XML .jff. Lanza ValueError si la definicion es inconsistente."""
    if not states:
        raise ValueError("states vacio")
    if len(set(states)) != len(states):
        raise ValueError("states duplicados")
    if initial not in states:
        raise ValueError(f"initial '{initial}' no esta en states")
    for f in finals:
        if f not in states:
            raise ValueError(f"final '{f}' no esta en states")
    sigma = set(alphabet)
    parsed: list[Transition] = []
    for t in transitions:
        frm, to, read = t.get("from"), t.get("to"), t.get("read", "")
        if frm not in states:
            raise ValueError(f"transicion from '{frm}' desconocido")
        if to not in states:
            raise ValueError(f"transicion to '{to}' desconocido")
        if read is None:
            read = ""
        read = str(read)
        if read != "" and read not in sigma and read not in ("",):
            raise ValueError(f"simbolo '{read}' fuera del alfabeto {alphabet}")
        if len(read) > 1:
            raise ValueError(f"read debe ser 1 simbolo o '' (lambda), llego '{read}'")
        parsed.append(Transition(frm, read, to))

    ids = {name: i for i, name in enumerate(states)}
    finals_set = set(finals)
    root = ET.Element("structure")
    ET.SubElement(root, "type").text = "fa"
    aut = ET.SubElement(root, "automaton")
    n = len(states)
    for i, name in enumerate(states):
        st = ET.SubElement(aut, "state", {"id": str(ids[name]), "name": name})
        ang = 2 * math.pi * i / max(n, 1)
        ET.SubElement(st, "x").text = f"{320.0 + 220.0 * math.cos(ang):.1f}"
        ET.SubElement(st, "y").text = f"{240.0 + 180.0 * math.sin(ang):.1f}"
        if name == initial:
            ET.SubElement(st, "initial")
        if name in finals_set:
            ET.SubElement(st, "final")
    for t in parsed:
        tr = ET.SubElement(aut, "transition")
        ET.SubElement(tr, "from").text = str(ids[t.frm])
        ET.SubElement(tr, "to").text = str(ids[t.to])
        ET.SubElement(tr, "read").text = t.read if t.read != "" else None
    _indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def parse_fa_jff(xml_text: str) -> dict:
    """Parsea un .jff tipo fa a dict {states, initial, finals, transitions, alphabet}."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"XML invalido: {exc}") from exc
    type_el = root.find("type")
    if type_el is None or (type_el.text or "").strip() != "fa":
        raise ValueError("solo se soporta <type>fa</type> en v0.1.0")
    aut = root.find("automaton")
    if aut is None:
        raise ValueError("falta <automaton>")
    id_to_name: dict[str, str] = {}
    states: list[str] = []
    initial: str | None = None
    finals: list[str] = []
    for st in aut.findall("state"):
        sid = st.get("id", "")
        name = st.get("name", sid)
        id_to_name[sid] = name
        states.append(name)
        if st.find("initial") is not None and initial is None:
            initial = name
        if st.find("final") is not None:
            finals.append(name)
    if initial is None:
        raise ValueError("el automata no declara <initial>")
    transitions: list[dict] = []
    alphabet: list[str] = []
    for tr in aut.findall("transition"):
        frm = (tr.findtext("from") or "").strip()
        to = (tr.findtext("to") or "").strip()
        read_el = tr.find("read")
        read = (read_el.text or "") if read_el is not None else ""
        read = read.strip()
        if frm not in id_to_name or to not in id_to_name:
            raise ValueError(f"transicion con id desconocido: {frm}->{to}")
        transitions.append({"from": id_to_name[frm], "to": id_to_name[to], "read": read})
        if read != "" and read not in alphabet:
            alphabet.append(read)
    return {
        "states": states,
        "alphabet": sorted(alphabet),
        "initial": initial,
        "finals": finals,
        "transitions": transitions,
    }


def validate_fa(states: list[str], alphabet: list[str], initial: str, finals: list[str], transitions: list[dict]) -> dict:
    """Chequea determinismo, completitud (solo AFD), alcanzables y estados muertos."""
    sigma = set(alphabet)
    by_pair: dict[tuple[str, str], list[str]] = {}
    has_lambda = False
    for t in transitions:
        frm, read, to = t.get("from"), t.get("read", ""), t.get("to")
        if read in (None, ""):
            has_lambda = True
            continue
        by_pair.setdefault((frm, read), []).append(to)
    nondet_pairs = sorted([f"{a} + '{b}' -> {v}" for (a, b), v in by_pair.items() if len(v) > 1])
    is_dfa = not has_lambda and not nondet_pairs
    missing: list[str] = []
    if is_dfa:
        for s in states:
            for sym in alphabet:
                if (s, sym) not in by_pair:
                    missing.append(f"delta({s},{sym}) indefinida")
    # Alcanzables (ignorando etiqueta, incluyendo lambda).
    adj: dict[str, set[str]] = {s: set() for s in states}
    for t in transitions:
        if t.get("from") in adj and t.get("to") in adj:
            adj[t["from"]].add(t["to"])
    seen = {initial} if initial in adj else set()
    stack = [initial] if initial in adj else []
    while stack:
        cur = stack.pop()
        for nxt in adj.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    unreachable = [s for s in states if s not in seen]
    # Productivos: llegan a algun final (grafo reverso).
    rev: dict[str, set[str]] = {s: set() for s in states}
    for t in transitions:
        if t.get("from") in rev and t.get("to") in rev:
            rev[t["to"]].add(t["from"])
    prod: set[str] = set(finals) & set(states)
    stack = list(prod)
    while stack:
        cur = stack.pop()
        for prev in rev.get(cur, ()):
            if prev not in prod:
                prod.add(prev)
                stack.append(prev)
    dead = sorted([s for s in seen if s not in prod])
    errors: list[str] = []
    if initial not in states:
        errors.append("initial fuera de states")
    for f in finals:
        if f not in states:
            errors.append(f"final '{f}' fuera de states")
    for t in transitions:
        if t.get("from") not in states or t.get("to") not in states:
            errors.append(f"transicion invalida {t}")
        r = t.get("read", "")
        if r not in (None, "") and r not in sigma:
            errors.append(f"simbolo '{r}' fuera del alfabeto")
    warnings: list[str] = []
    if has_lambda:
        warnings.append("tiene transiciones lambda: es AFN")
    if nondet_pairs:
        warnings.append(f"no-determinismo en: {'; '.join(nondet_pairs)}")
    if missing:
        warnings.append(f"AFD incompleto: {len(missing)} pares sin delta")
    if unreachable:
        warnings.append(f"inalcanzables: {', '.join(unreachable)}")
    if dead:
        warnings.append(f"sin camino a final: {', '.join(dead)}")
    return {
        "is_dfa": is_dfa,
        "has_lambda": has_lambda,
        "nondet_pairs": nondet_pairs,
        "missing_transitions": missing,
        "reachable": sorted(seen),
        "unreachable": unreachable,
        "dead_states": dead,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def _lambda_closure(state_set: set[str], lambda_adj: dict[str, set[str]]) -> set[str]:
    closure = set(state_set)
    stack = list(state_set)
    while stack:
        cur = stack.pop()
        for nxt in lambda_adj.get(cur, ()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure


def simulate_fa(
    states: list[str],
    initial: str,
    finals: list[str],
    transitions: list[dict],
    input_string: str,
) -> dict:
    """Simula por BFS con cierre-lambda. Devuelve accepted + trace de una rama testigo."""
    finals_set = set(finals)
    move: dict[tuple[str, str], set[str]] = {}
    lambda_adj: dict[str, set[str]] = {s: set() for s in states}
    for t in transitions:
        frm, to, read = t.get("from"), t.get("to"), t.get("read", "") or ""
        if read == "":
            if frm in lambda_adj and to in lambda_adj:
                lambda_adj[frm].add(to)
        else:
            move.setdefault((frm, read), set()).add(to)
    start = _lambda_closure({initial}, lambda_adj)
    # frontier: lista de (estado, camino_de_transiciones)
    frontier: list[tuple[str, list[dict]]] = [(s, []) for s in sorted(start)]
    for pos, sym in enumerate(input_string):
        nxt_frontier: list[tuple[str, list[dict]]] = []
        seen_states: set[str] = set()
        for st, path in frontier:
            for dst in sorted(move.get((st, sym), ())):
                for closed in sorted(_lambda_closure({dst}, lambda_adj)):
                    step = {"from": st, "read": sym, "to": closed, "pos": pos}
                    nxt_frontier.append((closed, path + [step]))
                    seen_states.add(closed)
        frontier = nxt_frontier
        if not frontier:
            return {"input": input_string, "accepted": False, "trace": [], "reason": f"se traba en pos {pos} simbolo '{sym}'"}
    for st, path in frontier:
        if st in finals_set:
            return {"input": input_string, "accepted": True, "trace": path, "final_state": st}
    return {"input": input_string, "accepted": False, "trace": frontier[0][1] if frontier else [], "reason": "consume todo pero no termina en final"}
