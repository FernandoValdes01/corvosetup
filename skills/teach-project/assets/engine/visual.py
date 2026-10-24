"""Interfaz de estudio en terminal; nunca ejecuta comandos del proyecto."""

from __future__ import annotations

import curses
import os
from pathlib import Path
import textwrap

from teach import export, report, save_progress


def wrap(text: str, width: int) -> list[str]:
    lines = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, max(10, width), replace_whitespace=False,
                                   break_long_words=True, break_on_hyphens=False) or [""])
    return lines


def file_lines(lab_dir: Path, entry: dict, width: int, *, complete=False) -> list[str]:
    path = (lab_dir / entry["path"]).resolve()
    if not path.is_relative_to(lab_dir.resolve()) or any(part.startswith(".") for part in Path(entry["path"]).parts):
        raise ValueError("El visor solo abre archivos del proyecto fuera de directorios ocultos.")
    output = []
    for title, key in (("PARA QUÉ SIRVE", "purpose"), ("CUÁNDO SE USA", "used_when"),
                       ("CÓMO SE CONECTA", "explanation"), ("PARÁMETROS Y EFECTO", "parameters")):
        output.extend([title, *wrap(entry[key], width), ""])
    start, end = entry["lines"]
    source = path.read_text(encoding="utf-8").splitlines()
    if not 1 <= start <= end <= len(source):
        raise ValueError(f"El fragmento de {entry['path']} ya no coincide con el archivo. Revisa tutorial.json.")
    if complete:
        start, end = 1, len(source)
    output.extend([f"CÓDIGO REAL · {entry['path']} · líneas {start}-{end}", ""])
    for number in range(start, end + 1):
        output.extend(wrap(f"{number:>4} | {source[number - 1]}", width))
    return output


class TutorApp:
    def __init__(self, screen, lesson: dict, state: dict, lab_dir: Path, progress_path: Path, state_dir: Path, motion: bool):
        self.screen, self.lesson, self.state = screen, lesson, state
        self.lab_dir, self.progress_path, self.state_dir, self.motion = lab_dir, progress_path, state_dir, motion
        self.view = "lesson" if state["phase"] else "summary"
        reader = state.get("terminal_reader", {})
        self.scroll = reader.get("scroll", 0) if reader.get("phase") == state["phase"] else 0
        self.document_scroll, self.file_index, self.index_cursor = self.scroll, 0, self.phase_index
        self.ask, self.draft, self.cursor = False, "", 0
        self.note = "←/→ cambia fase · ↑/↓ lee · Enter abre el código completo."
        self.flow_step = 0
        self.accent = curses.A_BOLD
        screen.keypad(True)
        if curses.has_colors() and "NO_COLOR" not in os.environ:
            try:
                curses.start_color()
                curses.use_default_colors()
                curses.init_pair(1, curses.COLOR_CYAN, -1)
                self.accent |= curses.color_pair(1)
            except curses.error:
                pass

    @property
    def phase_index(self):
        return next((i for i, phase in enumerate(self.lesson["phases"])
                     if phase["id"] == self.state["phase"]), len(self.lesson["phases"]) - 1)

    @property
    def phase(self):
        return self.lesson["phases"][self.phase_index]

    @property
    def asking(self):
        return self.view == "lesson" and self.ask

    @property
    def files(self):
        catalog = {entry["path"]: entry for entry in self.lesson.get("files", [])}
        return [catalog[path] for path in self.phase.get("files", []) if path in catalog]

    def save(self):
        save_progress(self.progress_path, self.state)

    def put(self, y: int, x: int, text: str, style=0):
        height, width = self.screen.getmaxyx()
        if 0 <= y < height and 0 <= x < width - 1:
            try:
                self.screen.addstr(y, x, text[:width - x - 1], style)
            except curses.error:
                # El terminal puede cambiar de tamaño mientras se dibuja.
                pass

    def body(self, width: int) -> list[str]:
        if self.view == "summary":
            return ["RECORRIDO TERMINADO", "", "Tus preguntas están guardadas y listas para copiar.",
                    "Q sale y muestra el bloque completo en la terminal.", "I permite volver a una fase.", "",
                    *wrap(report(self.lesson, self.state), width)]
        if self.view == "index":
            return ["ELIGE UNA FASE", "", "Usa las flechas y pulsa Enter para abrirla.",
                    "Volver a una fase conserva tus preguntas y las fases ya leídas.", "",
                    *[f"{'>' if i == self.index_cursor else ' '} {i + 1:>2}. {phase['title']}"
                      for i, phase in enumerate(self.lesson["phases"])]]
        if self.view == "files":
            if not self.files:
                return ["No hay archivos asociados a esta fase.", "Pulsa F para volver al tutorial."]
            self.file_index = min(self.file_index, len(self.files) - 1)
            entry = self.files[self.file_index]
            return [*wrap(entry["path"], width), "", *file_lines(self.lab_dir, entry, width, complete=True)]
        if self.asking:
            count = sum(item["phase"] == self.phase["id"] for item in self.state["doubts"])
            lines = ["¿DUDAS SOBRE ESTA FASE?", "", "Escribe una pregunta y pulsa Enter para guardarla.",
                     "Puedes registrar varias. Enter sin texto termina esta pausa.",
                     "Escribe /salir para guardar y cerrar el programa.", "",
                     f"Preguntas guardadas en esta fase: {count}", ""]
            for item in self.state["doubts"]:
                if item["phase"] == self.phase["id"]:
                    lines.extend([*wrap("• " + item["text"], width), ""])
            return lines
        story = self.phase.get("story")
        if not story:
            return [line for section in self.phase["sections"]
                    for line in [*wrap(section["title"], width), "", *wrap(section["text"], width), ""]]
        lines = []
        def paragraph(title, text):
            lines.extend([title, "", *wrap(text, width), ""])
        paragraph("QUÉ SE SOLICITÓ", story["request"])
        paragraph("CÓMO SE INTERPRETA", story["interpretation"])
        paragraph("REPRESENTACIÓN DEL PROCESO", " → ".join(self.phase.get("flow", [])))
        paragraph("QUÉ REPRESENTA LA IMAGEN", story["visual"]["caption"] + " Las imágenes reales están en teach guia.")
        paragraph("POR QUÉ SE HIZO ASÍ", story["decision"])
        for alternative in story["alternatives"]:
            paragraph("ALTERNATIVA · " + alternative["name"], alternative["tradeoff"])
        catalog = {entry["path"]: entry for entry in self.files}
        for index, step in enumerate(story["walkthrough"], 1):
            paragraph(f"PASO {index} · {step['title']}", step["text"])
            if step.get("file") in catalog:
                entry = dict(catalog[step["file"]])
                entry["lines"] = step.get("lines", entry["lines"])
                snippet = file_lines(self.lab_dir, entry, width)
                start = next(i for i, line in enumerate(snippet) if line.startswith("CÓDIGO REAL"))
                lines.extend([*snippet[start:], ""])
        for difficulty in story["difficulties"]:
            paragraph("DIFICULTAD Y CÓMO ABORDARLA", difficulty)
        paragraph("CÓMO ADAPTARLO A OTRO PROYECTO", story["transfer"])
        lines.extend(["Dudas opcionales: pulsa D para anotar una y seguir leyendo.",
                      "Enter abre el código completo. ←/→ cambia de fase."])
        return lines

    def render(self):
        height, width = self.screen.getmaxyx()
        self.screen.erase()
        if height < 22 or width < 76:
            self.put(1, 1, "Amplía la terminal a 76 columnas y 22 filas.", self.accent)
            self.put(3, 1, "Q guarda y sale. También puedes usar: teach tutorial --texto")
            self.screen.refresh()
            return
        side = 29 if width >= 108 else 0
        x, body_width = side + 2, width - side - 4
        self.body_height = height - 13
        completed, total = len(set(self.state["completed"])), len(self.lesson["phases"])
        self.put(0, 2, self.lesson["title"], self.accent)
        filled = round(24 * completed / total)
        detail = " · documento" if self.state["phase"] else ""
        self.put(2, 2, f"[{'=' * filled}{' ' * (24 - filled)}]  {completed}/{total} fases  ·  {len(self.state['doubts'])} dudas{detail}")
        self.put(3, 2, "Estudio guiado · el visor no ejecuta comandos del proyecto")
        self.put(4, 2, "─" * (width - 4))
        self.put(5, x, f"Fase {self.phase_index + 1}/{total} · {self.phase['title']}", curses.A_BOLD)
        flow = self.phase.get("flow", [])
        active = self.flow_step % len(flow) if flow else 0
        if flow:
            self.put(6, x, f"Secuencia didáctica [{active + 1}/{len(flow)}]  {flow[active]}", self.accent)
            self.put(7, x, "  >  ".join(flow))
        if side:
            self.put(5, 2, "ARCHIVOS" if self.view == "files" else "FASES", self.accent)
            labels = [entry["path"] for entry in self.files] if self.view == "files" else [phase["title"] for phase in self.lesson["phases"]]
            selected = self.file_index if self.view == "files" else self.index_cursor if self.view == "index" else self.phase_index
            start = max(0, selected - max(1, self.body_height // 2))
            for row, i in enumerate(range(start, min(len(labels), start + self.body_height + 2)), 7):
                prefix = ">" if i == selected else " "
                self.put(row, 2, f"{prefix} {i + 1:>2} {labels[i]}"[:side - 3], self.accent if i == selected else 0)
            for row in range(5, height - 4):
                self.put(row, side, "│")
        lines = self.body(body_width)
        max_scroll = max(0, len(lines) - self.body_height)
        self.scroll = max(0, min(self.scroll, max_scroll))
        for row, line in enumerate(lines[self.scroll:self.scroll + self.body_height], 9):
            style = self.accent if row == 9 and self.scroll == 0 else curses.A_NORMAL
            self.put(row, x, line, style)
        self.put(height - 4, 2, "─" * (width - 4))
        self.put(height - 3, 2, self.note)
        controls = "←→ fase · ↑↓ leer · Enter código · D duda · Q salir"
        if self.view == "files":
            controls = "←→ archivo · ↑↓ leer · Enter volver · D duda · Q salir"
        elif self.view == "index":
            controls = "↑↓ elegir fase · Enter abrir · Esc volver · Q salir"
        elif self.view == "summary":
            controls = "↑↓ leer dudas · I repasar una fase · Q salir y copiar"
        self.put(height - 2, 2, controls)
        arrows = "fase" if self.view == "index" else "texto"
        self.put(height - 1, 2, f"↑↓ {arrows} · Re/AvPág · Esc volver · A secuencia · M animación {'sí' if self.motion else 'no'}")
        try:
            curses.curs_set(1 if self.asking else 0)
        except curses.error:
            pass
        if self.asking:
            offset = max(0, self.cursor - width + 15)
            visible = self.draft[offset:offset + width - 13]
            self.put(height - 2, 2, " " * (width - 4))
            self.put(height - 2, 2, "Duda > " + visible)
            self.put(height - 1, 2, "Enter guarda · Enter vacío continúa · /salir pausa · no incluyas contraseñas")
            self.screen.move(height - 2, min(width - 2, 9 + self.cursor - offset))
        self.screen.refresh()

    def animate(self):
        if not self.motion or self.asking:
            return
        for step in range(len(self.phase.get("flow", []))):
            self.flow_step = step
            self.render()
            # Una secuencia acotada; no hay bucles de animación mientras se lee.
            self.screen.timeout(140)
            try:
                key = self.screen.get_wch()
            except curses.error:
                continue
            else:
                curses.unget_wch(key)
                break
            finally:
                self.screen.timeout(-1)

    def jump(self, index: int):
        if self.view == "lesson" and self.state["phase"]:
            self.state["terminal_reader"] = {"phase": self.state["phase"], "scroll": self.scroll}
        self.state["phase"] = self.lesson["phases"][index]["id"]
        self.state["section"] = 0
        self.view, self.scroll, self.ask = "lesson", 0, False
        self.file_index, self.flow_step = 0, 0
        self.state["terminal_reader"] = {"phase": self.state["phase"], "scroll": 0}
        self.save()
        self.animate()

    def submit(self) -> bool:
        text = self.draft.strip()
        if text.lower() == "/salir":
            return False
        if text:
            self.state["doubts"].append({"phase": self.phase["id"], "text": text})
            self.save()
            export(self.lesson, self.state, self.state_dir, show=False)
            self.note = f"Duda guardada. Total: {len(self.state['doubts'])}. Puedes escribir otra."
            self.draft, self.cursor = "", 0
            self.scroll = 0
        elif self.ask:
            self.ask = False
            self.scroll = 0
        else:
            index = self.phase_index
            if self.phase["id"] not in self.state["completed"]:
                self.state["completed"].append(self.phase["id"])
            self.state["section"] = 0
            if index + 1 == len(self.lesson["phases"]):
                self.state["phase"] = None
                self.view, self.scroll = "summary", 0
                self.save()
            else:
                self.jump(index + 1)
            self.note = "Fase leída. Avance y dudas guardados."
        return True

    def edit(self, key) -> bool:
        if key in ("\n", "\r", curses.KEY_ENTER):
            return self.submit()
        if key in (curses.KEY_BACKSPACE, "\x7f", "\b") and self.cursor:
            self.draft = self.draft[:self.cursor - 1] + self.draft[self.cursor:]
            self.cursor -= 1
        elif key == curses.KEY_DC:
            self.draft = self.draft[:self.cursor] + self.draft[self.cursor + 1:]
        elif key == curses.KEY_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif key == curses.KEY_RIGHT:
            self.cursor = min(len(self.draft), self.cursor + 1)
        elif key == curses.KEY_HOME:
            self.cursor = 0
        elif key == curses.KEY_END:
            self.cursor = len(self.draft)
        elif key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_NPAGE, curses.KEY_PPAGE):
            direction = -1 if key in (curses.KEY_UP, curses.KEY_PPAGE) else 1
            self.scroll += direction * (self.body_height if key in (curses.KEY_NPAGE, curses.KEY_PPAGE) else 1)
        elif key == "\x1b" and self.ask:
            self.ask, self.draft, self.cursor = False, "", 0
        elif isinstance(key, str) and key.isprintable():
            self.draft = self.draft[:self.cursor] + key + self.draft[self.cursor:]
            self.cursor += 1
        return True

    def run(self):
        self.save()
        self.animate()
        while True:
            self.render()
            key = self.screen.get_wch()
            if key == curses.KEY_RESIZE:
                continue
            height, width = self.screen.getmaxyx()
            if height < 22 or width < 76:
                if key in ("q", "Q"):
                    return
                continue
            if self.asking:
                if not self.edit(key):
                    return
                continue
            if key in ("q", "Q"):
                if self.view == "lesson" and self.state["phase"]:
                    self.state["terminal_reader"] = {"phase": self.state["phase"], "scroll": self.scroll}
                    self.save()
                return
            if key in (curses.KEY_NPAGE, curses.KEY_PPAGE):
                self.scroll += self.body_height if key == curses.KEY_NPAGE else -self.body_height
            elif key in (curses.KEY_UP, curses.KEY_DOWN):
                delta = 1 if key == curses.KEY_DOWN else -1
                if self.view == "index":
                    self.index_cursor = (self.index_cursor + delta) % len(self.lesson["phases"])
                else:
                    self.scroll += delta
            elif key in (curses.KEY_LEFT, curses.KEY_RIGHT):
                delta = 1 if key == curses.KEY_RIGHT else -1
                if self.view == "files" and self.files:
                    self.file_index = (self.file_index + delta) % len(self.files)
                    self.scroll = 0
                else:
                    index = self.phase_index + delta
                    if 0 <= index < len(self.lesson["phases"]):
                        self.jump(index)
            elif key in ("i", "I"):
                self.view, self.scroll, self.index_cursor = "index", 0, self.phase_index
            elif key in ("f", "F") and self.state["phase"] is not None:
                if self.view == "files":
                    self.view, self.scroll = "lesson", self.document_scroll
                else:
                    self.document_scroll = self.scroll
                    self.view, self.scroll = "files", 0
            elif key == "\x1b":
                self.view = "lesson" if self.state["phase"] else "summary"
                self.scroll = 0
            elif key in ("a", "A"):
                self.animate()
            elif key in ("m", "M"):
                self.motion = not self.motion
                self.note = "Animaciones activadas." if self.motion else "Animaciones desactivadas. El contenido permanece visible."
            elif key in ("d", "D") and self.state["phase"] is not None:
                self.view, self.ask, self.scroll = "lesson", True, 0
                self.draft, self.cursor = "", 0
            elif key in ("p", "P") and self.view == "lesson":
                self.state["section"] = max(0, self.state["section"] - 1)
                self.scroll = 0
                self.save()
            elif key in ("\n", "\r", curses.KEY_ENTER):
                if self.view == "index":
                    self.jump(self.index_cursor)
                elif self.view == "lesson":
                    self.document_scroll = self.scroll
                    self.view = "files"
                    self.scroll = 0
                elif self.view == "files":
                    self.view, self.scroll = "lesson", self.document_scroll


def run(lesson: dict, state: dict, lab_dir: Path, progress_path: Path, *, state_dir: Path | None = None, motion=True) -> None:
    state_dir = state_dir or progress_path.parent

    def session(screen):
        app = TutorApp(screen, lesson, state, lab_dir, progress_path, state_dir, motion)
        try:
            app.run()
        finally:
            if state["phase"]:
                position = app.document_scroll if app.view == "files" else app.scroll
                state["terminal_reader"] = {"phase": state["phase"], "scroll": position}
                save_progress(progress_path, state)
    try:
        curses.wrapper(session)
    except KeyboardInterrupt:
        pass
    print("Recorrido terminado." if state["phase"] is None else "Pausa guardada. Abre el mismo tutorial para continuar.")
    export(lesson, state, state_dir)
