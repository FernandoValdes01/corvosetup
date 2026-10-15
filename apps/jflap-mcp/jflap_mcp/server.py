"""Servidor MCP para JFLAP 7.1 (file-based, stdio por defecto como packet-tracer)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import __version__
from .jff import build_fa_jff, parse_fa_jff, simulate_fa, validate_fa
from .settings import SERVER_INSTRUCTIONS, SERVER_NAME

TRANSPORT_PORT = 39001

JFLAP_HOME = Path(os.environ.get("JFLAP_HOME", "~/Documentos/ramos/teoriacomputacion")).expanduser()
JFLAP_JAR = Path(os.environ.get("JFLAP_JAR", str(JFLAP_HOME / "JFLAP7.1-fixed.jar"))).expanduser()
JFLAP_LAUNCHER = Path(os.environ.get("JFLAP_LAUNCHER", str(JFLAP_HOME / "ejecutar-jflap.sh"))).expanduser()

mcp = FastMCP(
    SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
    host="127.0.0.1",
    port=TRANSPORT_PORT,
    stateless_http=True,
)

_lowlevel = getattr(mcp, "_mcp_server", None)
if _lowlevel is not None:
    _lowlevel.version = __version__


def _java_version() -> str:
    java = shutil.which("java")
    if not java:
        return "no encontrado"
    try:
        p = subprocess.run([java, "-version"], capture_output=True, text=True, timeout=5)
        return (p.stderr or p.stdout).strip().splitlines()[0] if (p.stderr or p.stdout) else "?"
    except Exception as exc:  # noqa: BLE001 - diagnostico, no falla el server
        return f"error: {exc}"


@mcp.tool()
def jflap_info() -> str:
    """Rutas reales del JFLAP instalado + java. Llamar primero antes de generar .jff."""
    return json.dumps(
        {
            "jar": str(JFLAP_JAR),
            "jar_exists": JFLAP_JAR.exists(),
            "launcher": str(JFLAP_LAUNCHER),
            "launcher_exists": JFLAP_LAUNCHER.exists(),
            "java": _java_version(),
            "open_hint": f"{JFLAP_LAUNCHER} /ruta/archivo.jff",
        },
        indent=2,
        ensure_ascii=False,
    )


@mcp.tool()
def jflap_create_fa(
    states: list[str],
    alphabet: list[str],
    initial: str,
    finals: list[str],
    transitions: list[dict],
    save_path: str = "",
) -> str:
    """Crea un automata finito .jff compatible con JFLAP 7.1.

    Parametros:
    - states: ["q0","q1",...]
    - alphabet: ["a","b"] (puede ser [] si solo lambda)
    - initial: "q0"
    - finals: ["q1"]
    - transitions: [{"from":"q0","read":"a","to":"q1"}]; read="" es lambda (AFN)
    - save_path: opcional, guarda el .jff en disco y devuelve la ruta
    """
    try:
        xml_text = build_fa_jff(states, alphabet, initial, finals, transitions)
    except ValueError as exc:
        return json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False)
    saved = ""
    if save_path:
        try:
            p = Path(save_path).expanduser()
            if not p.suffix:
                p = p.with_suffix(".jff")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(xml_text, encoding="utf-8")
            saved = str(p)
        except Exception as exc:  # noqa: BLE001 - reportar, no tirar el server
            return json.dumps({"ok": False, "error": f"no se pudo guardar: {exc}"}, indent=2, ensure_ascii=False)
    return json.dumps({"ok": True, "saved": saved, "jff": xml_text}, indent=2, ensure_ascii=False)


@mcp.tool()
def jflap_parse_jff(file_path: str = "", jff_xml: str = "") -> str:
    """Lee un .jff tipo fa desde disco (file_path) o XML directo (jff_xml)."""
    if not file_path and not jff_xml:
        return json.dumps({"ok": False, "error": "pasa file_path o jff_xml"}, indent=2, ensure_ascii=False)
    try:
        text = Path(file_path).expanduser().read_text(encoding="utf-8") if file_path else jff_xml
        data = parse_fa_jff(text)
        return json.dumps({"ok": True, **data}, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001 - error de usuario/archivo
        return json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False)


@mcp.tool()
def jflap_validate(
    states: list[str],
    alphabet: list[str],
    initial: str,
    finals: list[str],
    transitions: list[dict],
) -> str:
    """Valida AFD/AFN: determinismo, completitud, alcanzables, estados muertos."""
    try:
        result = validate_fa(states, alphabet, initial, finals, transitions)
        return json.dumps({"ok": True, **result}, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False)


@mcp.tool()
def jflap_simulate(
    states: list[str],
    initial: str,
    finals: list[str],
    transitions: list[dict],
    inputs: list[str],
) -> str:
    """Simula cadenas por BFS con cierre-lambda. Soporta AFN."""
    try:
        results = [simulate_fa(states, initial, finals, transitions, s) for s in inputs]
        return json.dumps({"ok": True, "results": results}, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False)


def main():
    """Arranca por stdio; usa --http para el endpoint local streamable-http."""
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
