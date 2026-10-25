#!/usr/bin/env python3
"""Comprueba resultados, glosario y compatibilidad sin instalar ni abrir el visor."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets" / "engine"))

from validate_tutorial import Validator
from visual import TutorApp


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


if __name__ == "__main__":
    unittest.main()
