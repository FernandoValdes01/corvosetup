#!/usr/bin/env python3
"""Valida tutorial.json contra el esquema y las garantías del visor teach."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MAX_SOURCE_BYTES = 300_000


class Validator:
    def __init__(self, project: Path):
        self.project = project.resolve()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def text(self, value, where: str) -> str:
        if not isinstance(value, str) or not value.strip():
            self.error(f"{where}: se esperaba texto no vacío.")
            return ""
        return value.strip()

    def items(self, value, where: str) -> list:
        if not isinstance(value, list):
            self.error(f"{where}: se esperaba una lista.")
            return []
        return value

    def source_path(self, entry: dict, where: str) -> Path | None:
        relative = self.text(entry.get("path"), f"{where}.path")
        if not relative:
            return None
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or any(part.startswith(".") for part in path.parts):
            self.error(f"{where}.path: usa una ruta relativa pública, sin '..' ni carpetas ocultas.")
            return None
        resolved = (self.project / path).resolve()
        if not resolved.is_relative_to(self.project):
            self.error(f"{where}.path: la ruta sale del proyecto.")
            return None
        if not resolved.is_file():
            self.error(f"{where}.path: no existe {relative}.")
            return None
        if resolved.stat().st_size > MAX_SOURCE_BYTES:
            self.error(f"{where}.path: {relative} supera {MAX_SOURCE_BYTES} bytes.")
            return None
        try:
            resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.error(f"{where}.path: {relative} no es texto UTF-8.")
            return None
        return resolved

    def lines(self, value, where: str, path: Path | None) -> tuple[int, int] | None:
        if not isinstance(value, list) or len(value) != 2 or not all(type(item) is int for item in value):
            self.error(f"{where}: usa [línea_inicial, línea_final] con enteros.")
            return None
        start, end = value
        if not 1 <= start <= end:
            self.error(f"{where}: el rango debe empezar en 1 y terminar en una línea mayor o igual.")
            return None
        if path:
            total = len(path.read_text(encoding="utf-8").splitlines())
            if end > total:
                self.error(f"{where}: la línea final {end} supera las {total} líneas del archivo.")
                return None
        return start, end

    def visual(self, value, where: str) -> None:
        if not isinstance(value, dict):
            self.error(f"{where}: se esperaba un objeto con file, alt y caption.")
            return
        name = self.text(value.get("file"), f"{where}.file")
        self.text(value.get("alt"), f"{where}.alt")
        self.text(value.get("caption"), f"{where}.caption")
        if not name:
            return
        if Path(name).name != name or not name.endswith((".svg", ".png")):
            self.error(f"{where}.file: usa el nombre de un .svg o .png dentro de diagramas/.")
            return
        if not (self.project / "diagramas" / name).is_file():
            self.error(f"{where}.file: falta diagramas/{name}.")

    def file_entry(self, entry, where: str) -> str | None:
        if not isinstance(entry, dict):
            self.error(f"{where}: se esperaba un objeto de archivo.")
            return None
        path = self.source_path(entry, where)
        relative = self.text(entry.get("path"), f"{where}.path")
        for key in ("purpose", "used_when", "explanation", "parameters"):
            self.text(entry.get(key), f"{where}.{key}")
        line_range = entry.get("lines")
        if line_range is None:
            self.error(f"{where}.lines: indica el fragmento principal, por ejemplo [1, 20].")
        else:
            self.lines(line_range, f"{where}.lines", path)
        return relative or None

    def phase(self, phase, index: int, files: set[str]) -> None:
        where = f"phases[{index}]"
        if not isinstance(phase, dict):
            self.error(f"{where}: se esperaba un objeto.")
            return
        phase_id = self.text(phase.get("id"), f"{where}.id")
        if phase_id and not SLUG.match(phase_id):
            self.error(f"{where}.id: usa minúsculas, números y guiones, por ejemplo 'proposito-topologia'.")
        self.text(phase.get("title"), f"{where}.title")

        sections = self.items(phase.get("sections"), f"{where}.sections")
        if not sections:
            self.error(f"{where}.sections: agrega al menos una sección para el modo texto.")
        elif len(sections) < 2:
            self.warn(f"{where}.sections: se recomiendan 2 o más secciones para el modo texto.")
        for position, section in enumerate(sections):
            if not isinstance(section, dict):
                self.error(f"{where}.sections[{position}]: se esperaba un objeto.")
                continue
            self.text(section.get("title"), f"{where}.sections[{position}].title")
            self.text(section.get("text"), f"{where}.sections[{position}].text")

        phase_files = phase.get("files", [])
        if not isinstance(phase_files, list):
            self.error(f"{where}.files: se esperaba una lista de rutas.")
            phase_files = []
        for name in phase_files:
            if not isinstance(name, str) or name not in files:
                self.error(f"{where}.files: '{name}' no está declarado en files.")
        if not phase_files:
            self.warn(f"{where}.files: la fase no enlaza archivos reales.")

        flow = phase.get("flow", [])
        if not isinstance(flow, list):
            self.error(f"{where}.flow: se esperaba una lista de pasos.")
        else:
            for position, step in enumerate(flow):
                self.text(step, f"{where}.flow[{position}]")

        story = phase.get("story")
        if story is None:
            self.warn(f"{where}.story: falta el relato guiado; se usará el modo de reserva.")
            return
        if not isinstance(story, dict):
            self.error(f"{where}.story: se esperaba un objeto.")
            return
        for key in ("request", "interpretation", "decision", "transfer"):
            self.text(story.get(key), f"{where}.story.{key}")
        if story.get("visual") is not None:
            self.visual(story["visual"], f"{where}.story.visual")

        alternatives = self.items(story.get("alternatives", []), f"{where}.story.alternatives")
        if not alternatives:
            self.warn(f"{where}.story.alternatives: se recomienda comparar al menos una alternativa.")
        for position, item in enumerate(alternatives):
            if not isinstance(item, dict):
                self.error(f"{where}.story.alternatives[{position}]: se esperaba un objeto.")
                continue
            self.text(item.get("name"), f"{where}.story.alternatives[{position}].name")
            self.text(item.get("tradeoff"), f"{where}.story.alternatives[{position}].tradeoff")

        walkthrough = self.items(story.get("walkthrough", []), f"{where}.story.walkthrough")
        if not walkthrough:
            self.warn(f"{where}.story.walkthrough: se recomienda mostrar cómo lo hace el código.")
        for position, step in enumerate(walkthrough):
            label = f"{where}.story.walkthrough[{position}]"
            if not isinstance(step, dict):
                self.error(f"{label}: se esperaba un objeto.")
                continue
            self.text(step.get("title"), f"{label}.title")
            self.text(step.get("text"), f"{label}.text")
            name = self.text(step.get("file"), f"{label}.file")
            if name and name not in files:
                self.error(f"{label}.file: '{name}' no está declarado en files.")
            path = self.source_path({"path": name}, label) if name else None
            self.lines(step.get("lines"), f"{label}.lines", path)

        difficulties = self.items(story.get("difficulties", []), f"{where}.story.difficulties")
        for position, item in enumerate(difficulties):
            self.text(item, f"{where}.story.difficulties[{position}]")

    def sources(self, value) -> None:
        sources = self.items(value, "sources") if value is not None else []
        if not sources:
            self.warn("sources: se recomienda registrar documentación oficial con su fecha de consulta.")
        for position, source in enumerate(sources):
            label = f"sources[{position}]"
            if not isinstance(source, dict):
                self.error(f"{label}: se esperaba un objeto.")
                continue
            self.text(source.get("title"), f"{label}.title")
            url = self.text(source.get("url"), f"{label}.url")
            if url and not url.startswith(("https://", "http://")):
                self.error(f"{label}.url: debe ser una URL http(s).")
            self.text(source.get("consulted"), f"{label}.consulted")

    def run(self) -> int:
        manifest = self.project / "tutorial.json"
        if not manifest.is_file():
            print(f"ERROR: falta {manifest}", file=sys.stderr)
            return 1
        try:
            lesson = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"ERROR: no se pudo leer tutorial.json: {error}", file=sys.stderr)
            return 1
        if not isinstance(lesson, dict):
            print("ERROR: tutorial.json debe contener un objeto.", file=sys.stderr)
            return 1

        self.text(lesson.get("title"), "title")
        self.text(lesson.get("objective"), "objective")
        self.text(lesson.get("scope"), "scope")

        files: set[str] = set()
        for index, entry in enumerate(self.items(lesson.get("files", []), "files")):
            name = self.file_entry(entry, f"files[{index}]")
            if name:
                if name in files:
                    self.error(f"files[{index}].path: '{name}' está repetido.")
                files.add(name)
        if len(files) < 6:
            self.warn(f"files: solo hay {len(files)} archivos; se recomiendan 6 o más con código real.")

        phases = self.items(lesson.get("phases"), "phases")
        if not 2 <= len(phases) <= 12:
            self.error(f"phases: usa entre 2 y 12 fases; hay {len(phases)}.")
        if len(phases) < 5:
            self.warn(f"phases: solo hay {len(phases)}; para un proyecto completo se recomiendan 6 a 10.")
        ids = set()
        for index, phase in enumerate(phases):
            self.phase(phase, index, files)
            if isinstance(phase, dict):
                phase_id = phase.get("id")
                if isinstance(phase_id, str):
                    if phase_id in ids:
                        self.error(f"phases[{index}].id: '{phase_id}' está repetido.")
                    ids.add(phase_id)

        self.sources(lesson.get("sources"))
        diagrams_dir = self.project / "diagramas"
        diagrams = list(diagrams_dir.glob("*.svg")) + list(diagrams_dir.glob("*.png")) if diagrams_dir.is_dir() else []
        if not diagrams:
            self.warn("diagramas/: no hay imágenes; se recomienda al menos un diagrama propio por recorrido.")

        for warning in self.warnings:
            print(f"AVISO: {warning}")
        if self.errors:
            for error in self.errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"\n{len(self.errors)} error(es). Corrige tutorial.json antes de abrir la guía.", file=sys.stderr)
            return 1
        print(f"OK: {len(phases)} fases, {len(files)} archivos y {len(lesson.get('sources') or [])} fuentes.")
        if self.warnings:
            print(f"{len(self.warnings)} aviso(s) de calidad; no bloquean la guía.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida tutorial.json para el visor teach.")
    parser.add_argument("project", nargs="?", default=".", help="raíz del proyecto (por defecto: actual)")
    args = parser.parse_args()
    return Validator(Path(args.project)).run()


if __name__ == "__main__":
    raise SystemExit(main())
