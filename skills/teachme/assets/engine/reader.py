"""Visor educativo local: sirve contenido explícito del proyecto y guarda lectura."""

from __future__ import annotations

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
from urllib.parse import parse_qs, urlsplit
import webbrowser

from teach import export, report, save_progress, state_paths


def sources(lab_dir: Path, lesson: dict) -> dict[str, str]:
    result = {}
    for entry in lesson.get("files", []):
        relative = Path(entry["path"])
        path = (lab_dir / relative).resolve()
        if any(part.startswith(".") for part in relative.parts) or not path.is_relative_to(lab_dir.resolve()):
            raise ValueError("El visor solo expone archivos de código declarados dentro del proyecto.")
        if path.stat().st_size > 300_000:
            raise ValueError(f"El archivo {relative} supera el tamaño permitido para esta guía.")
        result[entry["path"]] = path.read_text(encoding="utf-8")
    return result


def apply_action(state: dict, action: dict, lesson: dict) -> dict:
    if not isinstance(action, dict):
        raise ValueError("La acción debe ser un objeto JSON.")
    kind = action.get("action")
    if not isinstance(kind, str) or kind not in {"visit", "complete", "doubt", "clear_doubts"}:
        raise ValueError("Acción desconocida.")
    if kind == "clear_doubts":
        updated = copy.deepcopy(state)
        updated["doubts"] = []
        return updated
    phase = action.get("phase")
    if not isinstance(phase, str) or phase not in {item["id"] for item in lesson["phases"]}:
        raise ValueError("La fase no pertenece a esta guía.")
    updated = copy.deepcopy(state)
    if kind == "visit":
        scroll = action.get("scroll", 0)
        if type(scroll) is not int or not 0 <= scroll <= 10_000_000:
            raise ValueError("La posición de lectura debe ser un entero válido.")
        updated["reader"] = {"phase": phase, "scroll": scroll}
        if updated["phase"] != phase:
            updated["section"] = 0
        updated["phase"] = phase
    elif kind == "complete":
        if phase not in updated["completed"]:
            updated["completed"].append(phase)
    else:
        text = action.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > 4000:
            raise ValueError("Escribe una duda de entre 1 y 4000 caracteres.")
        updated["doubts"].append({"phase": phase, "text": text.strip()})
    return updated


def create_server(lab_dir: Path, lesson: dict, state: dict, *, port=0, motion=True, state_dir=None):
    web_dir = Path(__file__).resolve().parent / "web"
    diagrams = lab_dir / "diagramas"
    state_dir = state_dir or state_paths(lab_dir)[0]
    code = sources(lab_dir, lesson)
    images = {phase.get("story", {}).get("visual", {}).get("file") for phase in lesson["phases"]} - {None}
    token = secrets.token_urlsafe(24)
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, content, mime="application/json; charset=utf-8"):
            data = content.encode("utf-8") if isinstance(content, str) else content
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(data)

        def json(self, status, value):
            self.send(status, json.dumps(value, ensure_ascii=False))

        def authorized(self, *, page=False):
            if self.headers.get("Host") != self.server.authority:
                self.json(403, {"error": "Acceso permitido solo desde la dirección local de esta sesión."})
                return False
            supplied = parse_qs(urlsplit(self.path).query).get("token", [""])[0] if page else self.headers.get("X-Teach-Token", "")
            origin = self.headers.get("Origin")
            if not secrets.compare_digest(supplied.encode(), token.encode()) or origin and origin != self.server.origin:
                self.json(403, {"error": "La sesión no es válida. Vuelve a abrir la URL que imprime teach."})
                return False
            return True

        def do_GET(self):
            path = urlsplit(self.path).path
            if path in {"/api/bootstrap", "/api/export"}:
                if not self.authorized():
                    return
                with lock:
                    if path == "/api/bootstrap":
                        self.json(200, {"lesson": lesson, "state": self.server.progress, "files": code,
                                        "report": report(lesson, self.server.progress), "motion": motion})
                    else:
                        self.send(200, report(lesson, self.server.progress), "text/markdown; charset=utf-8")
                return
            if path == "/":
                if not self.authorized(page=True):
                    return
                self.send(200, (web_dir / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif path in {"/app.js", "/style.css"}:
                mime = "text/javascript" if path.endswith(".js") else "text/css"
                self.send(200, (web_dir / path[1:]).read_bytes(), mime + "; charset=utf-8")
            elif path.startswith("/diagramas/") and path.removeprefix("/diagramas/") in images:
                name = path.removeprefix("/diagramas/")
                if Path(name).name != name or not name.endswith((".svg", ".png")):
                    self.json(404, {"error": "Imagen no disponible."})
                    return
                try:
                    self.send(200, (diagrams / name).read_bytes(), "image/svg+xml" if name.endswith(".svg") else "image/png")
                except FileNotFoundError:
                    self.json(404, {"error": "No se encontró la imagen de esta fase."})
            else:
                self.json(404, {"error": "Recurso no disponible en la guía."})

        def do_POST(self):
            if urlsplit(self.path).path != "/api/action":
                self.json(404, {"error": "Acción no disponible."})
                return
            if not self.authorized():
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 20000:
                    raise ValueError("La petición no tiene un tamaño válido.")
                action = json.loads(self.rfile.read(size).decode("utf-8"))
                if isinstance(action, dict) and action.get("action") == "close":
                    with lock:
                        export(lesson, self.server.progress, state_dir, show=False)
                        self.json(200, {"state": self.server.progress, "report": report(lesson, self.server.progress)})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                    return
                with lock:
                    updated = apply_action(self.server.progress, action, lesson)
                    save_progress(state_dir / "tutorial-progress.json", updated)
                    self.server.progress = updated
                    state.clear()
                    state.update(copy.deepcopy(updated))
                    export(lesson, updated, state_dir, show=False)
                    self.json(200, {"state": updated, "report": report(lesson, updated)})
            except (ValueError, UnicodeError) as error:
                self.json(400, {"error": str(error)})
            except OSError as error:
                self.json(500, {"error": f"No se pudo guardar el avance: {error}. Conserva tu texto y reintenta."})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.progress = copy.deepcopy(state)
    server.authority = f"127.0.0.1:{server.server_port}"
    server.origin = f"http://{server.authority}"
    server.url = f"{server.origin}/?token={token}"
    return server


def run(lab_dir: Path, lesson: dict, state: dict, *, port=0, open_browser=True, motion=True, state_dir=None):
    state_dir = state_dir or state_paths(lab_dir)[0]
    with create_server(lab_dir, lesson, state, port=port, motion=motion, state_dir=state_dir) as server:
        print(f"\nGuía educativa local: {server.url}", flush=True)
        print("←/→ fases · ↑/↓ leer · Enter abre el código completo. Ctrl+C cierra el visor local.", flush=True)
        if open_browser:
            def open_tab():
                try:
                    if not webbrowser.open(server.url, new=2):
                        print("Abre la URL anterior en tu navegador para comenzar.", flush=True)
                except (webbrowser.Error, OSError):
                    print("No se pudo abrir el navegador automáticamente. Usa la URL anterior.", flush=True)
            threading.Thread(target=open_tab, daemon=True).start()
        try:
            server.serve_forever(poll_interval=.2)
        except KeyboardInterrupt:
            pass
        export(lesson, server.progress, state_dir)
