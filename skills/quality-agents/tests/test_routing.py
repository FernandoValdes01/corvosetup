#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("delegate", ROOT / "scripts/delegate.py")
assert SPEC and SPEC.loader
DELEGATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DELEGATE)


class RoutingTests(unittest.TestCase):
    def test_expected_routes(self) -> None:
        routes = DELEGATE.load_routes()
        self.assertEqual(routes["trivial"], {
            "model": "opencode/muse-spark-1.2-contributor-free", "variant": "xhigh"
        })
        self.assertEqual(routes["normal"], {"model": "openai/gpt-5.6-luna", "variant": "medium"})
        self.assertEqual(routes["complex"], {"model": "openai/gpt-5.6-luna", "variant": "high"})
        self.assertEqual(routes["very-complex"], {"model": "openai/gpt-5.6-luna", "variant": "xhigh"})
        self.assertEqual(routes["review"], {"model": "openai/gpt-5.6-luna", "variant": "xhigh"})

    def test_reviewer_cannot_be_downgraded(self) -> None:
        with self.assertRaisesRegex(ValueError, "must use review"):
            DELEGATE.build_command("strict-reviewer", "trivial", ROOT, "default")

    def test_workers_cannot_take_review_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "reserved"):
            DELEGATE.build_command("implementer", "review", ROOT, "default")

    def test_review_wrapper_rejects_route_override(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/review.py"),
                "--dir",
                str(ROOT),
                "--contract",
                str(ROOT / "tests/fixtures/e-bad-review.txt"),
                "--dry-run",
                "--role",
                "implementer",
                "--difficulty",
                "trivial",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("fixed to strict-reviewer/review", completed.stderr)
        self.assertNotIn("muse-spark", completed.stdout)

    def test_review_wrapper_emits_fixed_runtime_route(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/review.py"),
                "--dir",
                str(ROOT),
                "--contract",
                str(ROOT / "tests/fixtures/e-bad-review.txt"),
                "--dry-run",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        route = json.loads(completed.stdout)
        self.assertEqual(route["role"], "strict-reviewer")
        self.assertEqual(route["model"], "openai/gpt-5.6-luna")
        self.assertEqual(route["variant"], "xhigh")

    def test_leaf_process_cannot_launch_bridge(self) -> None:
        environment = os.environ.copy()
        environment["QUALITY_AGENTS_LEAF"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/delegate.py"), "--help"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("cannot launch nested workers", completed.stderr)

    def test_all_agents_deny_nested_tasks(self) -> None:
        for path in (ROOT / "agents/opencode").glob("quality-*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("mode: primary", text, path.name)
            self.assertIn("task: deny", text, path.name)
            self.assertIn("skill: deny", text, path.name)
            if "explorer" not in path.name and "strict-reviewer" not in path.name:
                self.assertIn('"*opencode*": deny', text, path.name)


if __name__ == "__main__":
    unittest.main()
