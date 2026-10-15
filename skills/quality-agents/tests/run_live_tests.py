#!/usr/bin/env python3
"""Run the five controlled OpenCode acceptance scenarios without editing projects."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests/fixtures"
SPEC = importlib.util.spec_from_file_location("delegate", ROOT / "scripts/delegate.py")
assert SPEC and SPEC.loader
DELEGATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DELEGATE)

SCENARIOS = {
    "A": ("implementer", "trivial", "a-trivial.txt", ("TEST A: PASS",)),
    "B": ("implementer", "normal", "b-normal.txt", ("TEST B: PASS",)),
    "C": ("ui-engineer", "complex", "c-frontend.txt", ("TEST C: PASS", "VISUAL VERIFICATION: NOT AVAILABLE")),
    "D": ("debugger", "very-complex", "d-debugging.txt", ("TEST D: PASS", "CAUSE", "EVIDENCE", "MINIMAL FIX", "VERIFICATION")),
    "E": ("strict-reviewer", "review", "e-bad-review.txt", ("VERDICT: FAIL", "REQUIRED FIXES", "normalizeEmail")),
}


def run_scenario(name: str) -> dict[str, object]:
    role, difficulty, fixture, required = SCENARIOS[name]
    command = DELEGATE.build_command(role, difficulty, ROOT / "tests", "json")
    contract = (FIXTURES / fixture).read_text(encoding="utf-8")
    completed = subprocess.run(command + [contract], check=False, capture_output=True, text=True)
    texts: list[str] = []
    usage: dict[str, object] | None = None
    for line in completed.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "text":
            texts.append(event.get("part", {}).get("text", ""))
        elif event.get("type") == "step_finish":
            part = event.get("part", {})
            usage = {"tokens": part.get("tokens"), "cost": part.get("cost")}
    response = "\n".join(texts)
    passed = completed.returncode == 0 and "Falling back to default agent" not in completed.stderr
    passed = passed and all(fragment.lower() in response.lower() for fragment in required)
    if name == "E":
        lowered = response.lower()
        required_fixes = lowered.split("required fixes:", 1)[-1].split("optional improvements:", 1)[0]
        passed = passed and any(term in required_fixes for term in ("unnecessary", "overengineer"))
        passed = passed and any(term in required_fixes for term in ("duplicat", "reuse"))
        passed = passed and "malformed" in required_fixes and "test" in required_fixes
        passed = passed and (
            "verification" in required_fixes or ("run" in required_fixes and "command" in required_fixes)
        )
    route = DELEGATE.load_routes()[difficulty]
    return {
        "test": name,
        "passed": passed,
        "role": role,
        "model": route["model"],
        "variant": route["variant"],
        "response": response,
        "usage": usage,
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    with ThreadPoolExecutor(max_workers=4) as executor:
        first = list(executor.map(run_scenario, ("A", "B", "C", "D")))
    results = first + [run_scenario("E")]
    print(json.dumps(results, indent=2))
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
