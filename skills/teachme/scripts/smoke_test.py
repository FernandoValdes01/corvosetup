#!/usr/bin/env python3
"""Comprueba el motor instalado sin modificar el progreso real del proyecto."""

from __future__ import annotations

import argparse
from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import tempfile
import threading
from urllib.parse import parse_qs, urlsplit


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba el visor teach instalado en un proyecto.")
    parser.add_argument("project", nargs="?", default=".", help="raíz del proyecto (por defecto: actual)")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    engine = project / ".teach" / "engine"
    if not (engine / "teach.py").is_file():
        print(f"ERROR: falta {engine}. Ejecuta install.py primero.", file=sys.stderr)
        return 1
    sys.path.insert(0, str(engine))
    try:
        from teach import load_progress
        from reader import create_server
    except ImportError as error:
        print(f"ERROR: no se pudo importar el motor: {error}", file=sys.stderr)
        return 1

    lesson = json.loads((project / "tutorial.json").read_text(encoding="utf-8"))
    phases = lesson["phases"]
    with tempfile.TemporaryDirectory(prefix="teach-smoke-") as temporary:
        state_dir = Path(temporary)
        state = load_progress(state_dir / "tutorial-progress.json", phases)
        server = create_server(project, lesson, state, state_dir=state_dir)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        token = parse_qs(urlsplit(server.url).query)["token"][0]

        def request(method: str, path: str, body=None):
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            headers = {"X-Teach-Token": token}
            payload = None
            if body is not None:
                headers["Content-Type"] = "application/json"
                payload = json.dumps(body)
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            content = response.read()
            connection.close()
            return response.status, content

        try:
            status, body = request("GET", "/api/bootstrap")
            assert status == 200, f"bootstrap respondió {status}"
            data = json.loads(body)
            assert set(data["files"]) == {entry["path"] for entry in lesson.get("files", [])}, "archivos incompletos"
            assert data["lesson"]["phases"], "sin fases"

            phase = phases[0]["id"]
            for action in (
                {"action": "visit", "phase": phase, "scroll": 120},
                {"action": "doubt", "phase": phase, "text": "¿Cómo se comprueba esta parte?"},
                {"action": "complete", "phase": phase},
            ):
                status, body = request("POST", "/api/action", action)
                assert status == 200, f"{action['action']} respondió {status}: {body[:200]}"

            status, body = request("GET", "/api/export")
            assert status == 200 and "¿Cómo se comprueba esta parte?" in body.decode(), "la exportación no incluye la duda"

            status, body = request("POST", "/api/action", {"action": "clear_doubts"})
            assert status == 200, f"clear_doubts respondió {status}"
            cleared = json.loads(body)["state"]
            assert cleared["doubts"] == [], "las dudas no se limpiaron"
            assert cleared["completed"] == [phase], "limpiar dudas borró el progreso"

            status, body = request("POST", "/api/action", {"action": "close"})
            assert status == 200, f"close respondió {status}"
            thread.join(timeout=3)
            assert not thread.is_alive(), "el servidor no se cerró"
            assert (state_dir / "dudas-tutorial.md").is_file(), "no se exportó dudas-tutorial.md"
        except AssertionError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            server.shutdown()
            server.server_close()
            return 1
        except Exception as error:
            print(f"ERROR inesperado: {error}", file=sys.stderr)
            server.shutdown()
            server.server_close()
            return 1

    print(f"OK: bootstrap, duda, exportación, limpieza y cierre funcionan ({len(phases)} fases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
