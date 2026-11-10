#!/usr/bin/env python3
"""Comprueba resultados, glosario y compatibilidad sin instalar ni abrir el visor."""

from pathlib import Path
import json
from contextlib import redirect_stdout
from io import StringIO
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "engine"))

from validate_tutorial import Validator
from visual import TutorApp
from reader import apply_action
from teach import guide, report, save_progress, load_progress


def phase(story):
    return {
        "id": "convertir-lecturas",
        "title": "Cómo comparamos temperaturas",
        "sections": [
            {"title": "Pedido", "text": "Comparar lecturas equivalentes."},
            {"title": "Resultado", "text": "Una decisión de alerta."},
        ],
        "files": [],
        "story": {"request": "Comparar lecturas.", "interpretation": "Unificar unidades.",
                  "decision": "Convertir a Celsius.", **story},
    }


class ContentContractTests(unittest.TestCase):
    def test_doubt_export_keeps_original_phase_after_navigation_and_reload(self):
        first = phase({"result": "Una alerta."})
        last = {**first, "id": "resultado-final", "title": "Resultados --> finales"}
        lesson = {"title": "Temperaturas", "phases": [first, last]}
        state = {"version": 1, "phase": last["id"], "section": 0, "completed": [], "doubts": []}
        state = apply_action(state, {"action": "doubt", "phase": last["id"], "text": "¿Cuántas filas?"}, lesson)
        state = apply_action(state, {"action": "visit", "phase": first["id"]}, lesson)
        state = apply_action(state, {"action": "doubt", "phase": first["id"], "text": "¿Qué es un pliegue?"}, lesson)
        path = self.project / "progress.json"
        save_progress(path, state)
        output = report(lesson, load_progress(path, lesson["phases"]))
        comments = [line for line in output.splitlines() if line.startswith("<!-- teachme-origin: ")]
        origins = [json.loads(line.removeprefix("<!-- teachme-origin: ").removesuffix(" -->")) for line in comments]
        self.assertEqual(origins[0], {"doubt": 1, "guide": "tutorial.json",
                                     "phase": {"number": 2, "id": last["id"], "title": last["title"]}})
        self.assertEqual(origins[1]["phase"]["id"], first["id"])
        self.assertEqual(origins[1]["doubt"], 2)
        self.assertNotIn("-->", comments[0][:-4])
        self.assertIn("Duda 1: ¿Cuántas filas?", output)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="teach-content-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)

    def validate_story(self, story):
        validator = Validator(self.project)
        validator.phase(phase(story), 1, set())
        return validator

    def test_result_and_glossary_are_accepted(self):
        validator = self.validate_story({
            "result": "86 Fahrenheit activa la alerta.",
            "glossary": [{"term": "Umbral", "explanation": "Valor que activa la alerta: 30 Celsius."}],
        })
        self.assertEqual(validator.errors, [])

    def test_result_is_required_and_must_be_nonempty_text(self):
        for story in ({}, {"result": " "}, {"result": 42},
                      {"result": "", "transfer": "Una nota antigua."}):
            with self.subTest(story=story):
                self.assertTrue(self.validate_story(story).errors)

    def test_legacy_transfer_is_accepted_with_migration_warning(self):
        validator = self.validate_story({"transfer": "Una nota antigua."})
        self.assertEqual(validator.errors, [])
        self.assertTrue(any("story.transfer" in warning for warning in validator.warnings))

    def test_malformed_glossary_is_rejected(self):
        for glossary in (None, {}, ["Umbral"], [{"term": "Umbral"}],
                         [{"term": " ", "explanation": "Un límite."}]):
            with self.subTest(glossary=glossary):
                self.assertTrue(self.validate_story({"result": "Una alerta.", "glossary": glossary}).errors)

    def test_new_first_phase_requires_a_theoretical_glossary(self):
        current = phase({"result": "Una alerta."})
        current["story"]["request"] = "Un encargo comprobable. " * 12
        current["story"]["interpretation"] = "Se comparan lecturas equivalentes en dos unidades. " * 12
        current["sections"].append({"title": "Límites", "text": "No controla sensores."})
        validator = Validator(self.project)
        validator.phase(current, 0, set())
        self.assertTrue(any("glossary" in error for error in validator.errors))
        current["story"]["glossary"] = [{"term": "Umbral", "explanation": "Límite de temperatura: 30 Celsius."}]
        validator = Validator(self.project)
        validator.phase(current, 0, set())
        self.assertEqual(validator.errors, [])

    def test_terminal_renders_new_and_legacy_content_without_visual(self):
        for story, expected, excluded in (
            ({"result": "Salida nueva.", "transfer": "Nota antigua."}, "Salida nueva.", "Nota antigua."),
            ({"transfer": "Nota antigua."}, "Nota antigua.", "Salida nueva."),
        ):
            with self.subTest(story=story):
                current = phase({**story, "glossary": [{"term": "Umbral", "explanation": "Límite de calor."}]})
                app = TutorApp.__new__(TutorApp)
                app.lesson = {"phases": [current], "files": []}
                app.state = {"phase": current["id"], "doubts": []}
                app.view, app.ask, app.lab_dir = "lesson", False, self.project
                output = "\n".join(app.body(120))
                self.assertIn(expected, output)
                self.assertNotIn(excluded, output)
                self.assertIn("Límite de calor.", output)

    def test_comprehension_is_reversible_idempotent_and_preserves_study_state(self):
        lesson = {"phases": [phase({"result": "Una alerta."})]}
        current = lesson["phases"][0]["id"]
        original = {"phase": current, "completed": [], "doubts": [{"phase": current, "text": "Una duda."}],
                    "reader": {"phase": current, "scroll": 120}}
        marked = apply_action(original, {"action": "complete", "phase": current}, lesson)
        self.assertEqual(original["completed"], [])
        self.assertEqual(marked["completed"], [current])
        self.assertEqual(apply_action(marked, {"action": "complete", "phase": current}, lesson), marked)
        unmarked = apply_action(marked, {"action": "uncomplete", "phase": current}, lesson)
        self.assertEqual(unmarked, original)
        self.assertEqual(apply_action(unmarked, {"action": "uncomplete", "phase": current}, lesson), original)
        with self.assertRaises(ValueError):
            apply_action(marked, {"action": "uncomplete", "phase": "no-existe"}, lesson)

    def test_text_mode_only_changes_comprehension_on_explicit_choice(self):
        current = phase({"result": "Una alerta."})
        lesson = {"title": "Temperaturas", "objective": "Comprender unidades.", "scope": "Ejemplo.", "phases": [current]}
        for answer, initially_marked, expected_marked in (("", False, False), ("s", False, True), ("n", True, False)):
            with self.subTest(answer=answer):
                state = {"version": 1, "phase": current["id"], "section": 0,
                         "completed": [current["id"]] if initially_marked else [], "doubts": []}
                with patch("teach.read", side_effect=["", "", "", answer]), redirect_stdout(StringIO()):
                    guide(lesson, state, self.project, self.project / "progress.json")
                self.assertEqual(current["id"] in state["completed"], expected_marked)


if __name__ == "__main__":
    unittest.main()
