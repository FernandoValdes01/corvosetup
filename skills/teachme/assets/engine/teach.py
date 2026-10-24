"""Guía educativa local por fases con progreso y dudas, sin ejecutar el proyecto."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import textwrap


COMMANDS = {"tutorial", "guia", "fases", "progreso", "dudas", "exportar", "archivos"}
STATE_DIR = Path(".teach") / "state"


def state_paths(lab_dir: Path) -> tuple[Path, Path]:
    state_dir = lab_dir / STATE_DIR
    return state_dir, state_dir / "tutorial-progress.json"


def write_private(path: Path, text: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.stem}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_progress(path: Path, phases: list[dict]) -> dict:
    if not path.exists():
        return {"version": 1, "phase": phases[0]["id"], "section": 0, "completed": [], "doubts": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {phase["id"]: phase for phase in phases}
    valid = (
        isinstance(data, dict)
        and data.get("version") == 1
        and "phase" in data
        and (data["phase"] is None or isinstance(data["phase"], str) and data["phase"] in by_id)
        and type(data.get("section")) is int
        and isinstance(data.get("completed"), list)
        and all(isinstance(item, str) and item in by_id for item in data["completed"])
        and isinstance(data.get("doubts"), list)
        and all(
            isinstance(item, dict)
            and isinstance(item.get("phase"), str)
            and item["phase"] in by_id
            and isinstance(item.get("text"), str)
            and item["text"].strip()
            for item in data["doubts"]
        )
    )
    if valid:
        current = by_id.get(data["phase"])
        valid = 0 <= data["section"] <= (len(current["sections"]) if current else 0)
        for key in ("reader", "terminal_reader"):
            if key in data:
                reader = data[key]
                valid = valid and isinstance(reader, dict) and isinstance(reader.get("phase"), str) and reader["phase"] in by_id
                valid = valid and type(reader.get("scroll")) is int and 0 <= reader["scroll"] <= 10_000_000
    if not valid:
        raise ValueError(f"El progreso de {path} tiene un formato incompatible. Se conservó sin sobrescribirlo.")
    return data


def save_progress(path: Path, state: dict) -> None:
    write_private(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def report(lesson: dict, state: dict) -> str:
    lines = [
        "Estoy leyendo las lecciones de este repositorio y hay partes que no entiendo bien. "
        "Explícame las siguientes dudas de manera simple, paso a paso y con ejemplos, para comprenderlas mejor.",
        "",
        f"Proyecto: {lesson['title']}.",
        "Guía: `tutorial.json`.",
        f"Progreso de estudio: {len(set(state['completed']))}/{len(lesson['phases'])} fases.",
        "Este progreso registra lectura y dudas; no verifica la ejecución ni el estado actual del proyecto.",
    ]
    for index, doubt in enumerate(state["doubts"], 1):
        lines.extend(["", f"Duda {index}: {doubt['text']}"])
    if not state["doubts"]:
        lines.extend(["", "Todavía no registré dudas."])
    lines.extend(["", "Responde según el contenido y la configuración del repositorio. Distingue evidencia histórica de resultados actuales.", ""])
    return "\n".join(lines)


def export(lesson: dict, state: dict, state_dir: Path, *, show: bool = True) -> None:
    content = report(lesson, state)
    path = state_dir / "dudas-tutorial.md"
    write_private(path, content)
    if show:
        print("\n----- INICIO PARA COPIAR -----\n" + content + "----- FIN PARA COPIAR -----")
        print(f"\nTambién guardado en {path}")


def read(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        raise KeyboardInterrupt from None


def show_text(text: str) -> None:
    for line in text.splitlines():
        if line.startswith(("$ ", "    ")):
            print(line)
        else:
            print(textwrap.fill(line, width=88, break_long_words=False, break_on_hyphens=False))


def guide(lesson: dict, state: dict, state_dir: Path, progress_path: Path) -> None:
    phases = lesson["phases"]
    print(f"\n{lesson['title']}\n{lesson['objective']}")
    print("Repaso de estudio. Los comandos se muestran para explicarlos; no se ejecutan.")
    print("Pulsa Enter para avanzar. Escribe q para pausar entre explicaciones.")
    print("Al final de cada fase escribe tus dudas, una por línea. Enter vacío cierra la fase.")
    print("Las dudas se guardan localmente. Escribe conceptos o errores sin contraseñas ni claves.")
    print(f"Alcance: {lesson['scope']}")
    save_progress(progress_path, state)
    try:
        while state["phase"] is not None:
            index = next(i for i, phase in enumerate(phases) if phase["id"] == state["phase"])
            phase = phases[index]
            completed = len(set(state["completed"]))
            print(f"\n{'=' * 64}\nFase {index + 1}/{len(phases)}: {phase['title']}")
            print(f"Progreso de estudio [{'#' * completed}{'.' * (len(phases) - completed)}] {completed}/{len(phases)}")
            while state["section"] < len(phase["sections"]):
                section = phase["sections"][state["section"]]
                print(f"\n{state['section'] + 1}/{len(phase['sections'])}. {section['title']}\n")
                show_text(section["text"])
                while True:
                    choice = read("\n[Enter] siguiente explicación · [q] guardar y salir: ").lower()
                    if choice == "q":
                        raise KeyboardInterrupt
                    if not choice:
                        break
                    print("Pulsa Enter o escribe q. Las dudas se registran al terminar la fase.")
                state["section"] += 1
                save_progress(progress_path, state)

            prompt = "\n¿Dudas? Escribe una duda, Enter para continuar o /salir para pausar: "
            while True:
                doubt = read(prompt)
                if doubt.lower() == "/salir":
                    raise KeyboardInterrupt
                if not doubt:
                    break
                state["doubts"].append({"phase": phase["id"], "text": doubt})
                save_progress(progress_path, state)
                export(lesson, state, state_dir, show=False)
                print(f"Duda guardada. Total: {len(state['doubts'])}.")
                prompt = "¿Otra duda? Escribe una, Enter para continuar o /salir para pausar: "
            if phase["id"] not in state["completed"]:
                state["completed"].append(phase["id"])
            state["phase"] = phases[index + 1]["id"] if index + 1 < len(phases) else None
            state["section"] = 0
            save_progress(progress_path, state)
    except KeyboardInterrupt:
        print("\nPausa guardada. Ejecuta el mismo comando para retomar esta explicación.")
    else:
        print("\nRecorrido terminado. Tus dudas están agrupadas por fase para pegarlas en el chat.")
        print("Puedes volver a estudiar desde una fase con: teach tutorial --fase NUMERO")
    export(lesson, state, state_dir)


def main(lab_dir: Path, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tutorial por fases con progreso y dudas para copiar al chat.")
    parser.add_argument("command", nargs="?", default="tutorial", choices=sorted(COMMANDS))
    parser.add_argument("--fase", type=int, help="repasar desde esta fase sin borrar dudas ni fases leídas")
    parser.add_argument("--texto", action="store_true", help="usar lectura lineal compatible con lectores de pantalla")
    parser.add_argument("--sin-animaciones", action="store_true", help="mostrar el programa visual sin movimiento")
    parser.add_argument("--terminal", action="store_true", help="usar la interfaz de terminal en vez del navegador")
    parser.add_argument("--no-abrir", action="store_true", help="imprimir la URL de la guía sin abrir el navegador")
    parser.add_argument("--puerto", type=int, default=0, help="puerto local de la guía; 0 elige uno libre")
    parser.epilog = "El progreso de estudio es independiente de la ejecución del proyecto."
    args = parser.parse_args(argv)
    if not 0 <= args.puerto <= 65535:
        parser.error("--puerto debe estar entre 0 y 65535")
    try:
        lesson = json.loads((lab_dir / "tutorial.json").read_text(encoding="utf-8"))
        phases = lesson["phases"]
        if args.fase is not None and (args.command not in {"tutorial", "guia"} or not 1 <= args.fase <= len(phases)):
            parser.error(f"--fase requiere tutorial y un número de 1 a {len(phases)}")
        state_dir, progress_path = state_paths(lab_dir)
        state = load_progress(progress_path, phases)
        if args.command in {"fases", "progreso"}:
            print(f"\n{lesson['title']} · {len(set(state['completed']))}/{len(phases)} fases leídas")
            for index, phase in enumerate(phases, 1):
                marker = "x" if phase["id"] in state["completed"] else " "
                cursor = " <- retomar aquí" if phase["id"] == state["phase"] else ""
                print(f"[{marker}] {index}. {phase['title']}{cursor}")
            print(f"Dudas guardadas: {len(state['doubts'])}. Verlas: teach dudas")
        elif args.command == "archivos":
            for entry in lesson.get("files", []):
                print(f"\n{entry['path']}\nPara qué: {entry['purpose']}\nCuándo: {entry['used_when']}")
                show_text(entry["explanation"])
                show_text(entry["parameters"])
        elif args.command in {"dudas", "exportar"}:
            export(lesson, state, state_dir)
        else:
            if args.fase is not None:
                state["phase"] = phases[args.fase - 1]["id"]
                state["section"] = 0
                state["reader"] = {"phase": state["phase"], "scroll": 0}
            browser = args.command == "guia" or (not args.texto and not args.terminal and sys.stdin.isatty() and sys.stdout.isatty())
            if browser:
                from reader import run as read_project
                read_project(lab_dir, lesson, state, port=args.puerto, open_browser=not args.no_abrir, motion=not args.sin_animaciones, state_dir=state_dir)
                return 0
            visual = not args.texto and sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM", "dumb") != "dumb"
            if visual:
                try:
                    import curses
                    from visual import run
                except ImportError:
                    print("Esta instalación de Python no incluye curses. Continúo en modo texto.")
                    guide(lesson, state, state_dir, progress_path)
                else:
                    try:
                        run(lesson, state, lab_dir, progress_path, state_dir=state_dir, motion=not args.sin_animaciones)
                    except curses.error as error:
                        print(f"El terminal no pudo abrir la interfaz visual: {error}. Continúo en modo texto.")
                        guide(lesson, state, state_dir, progress_path)
            else:
                guide(lesson, state, state_dir, progress_path)
        return 0
    except (OSError, ValueError) as error:
        print(f"No pude abrir o guardar el tutorial: {error}", file=sys.stderr)
        print("Los archivos existentes se conservaron. Revisa la ruta, formato y permisos indicados.", file=sys.stderr)
        return 1
