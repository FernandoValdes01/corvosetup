#!/usr/bin/env python3
"""Run one non-recursive OpenCode worker with an explicit model and variant."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROLES = {"explorer", "implementer", "debugger", "ui-engineer", "verifier", "strict-reviewer"}
DIFFICULTIES = {"trivial", "normal", "complex", "very-complex", "review"}


def load_routes() -> dict[str, dict[str, str]]:
    path = Path(__file__).resolve().parent.parent / "routing.json"
    return json.loads(path.read_text(encoding="utf-8"))["routes"]


def build_command(role: str, difficulty: str, directory: Path, output_format: str) -> list[str]:
    if role not in ROLES:
        raise ValueError(f"unknown role: {role}")
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"unknown difficulty: {difficulty}")
    if role == "strict-reviewer" and difficulty != "review":
        raise ValueError("strict-reviewer must use review routing")
    if difficulty == "review" and role != "strict-reviewer":
        raise ValueError("review routing is reserved for strict-reviewer")
    route = load_routes()[difficulty]
    return [
        "opencode",
        "run",
        "--dir",
        str(directory),
        "--agent",
        f"quality-{role}",
        "--model",
        route["model"],
        "--variant",
        route["variant"],
        "--format",
        output_format,
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, choices=sorted(ROLES))
    parser.add_argument("--difficulty", required=True, choices=sorted(DIFFICULTIES))
    parser.add_argument("--dir", required=True, type=Path)
    parser.add_argument("--contract", type=Path, help="Read the task contract from a file instead of stdin")
    parser.add_argument("--format", choices=("default", "json"), default="default")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    if os.environ.get("QUALITY_AGENTS_LEAF") == "1":
        print("error: Quality Agents workers cannot launch nested workers", file=sys.stderr)
        return 2
    args = parse_args()
    directory = args.dir.resolve()
    if not directory.is_dir():
        print(f"error: project directory does not exist: {directory}", file=sys.stderr)
        return 2
    if shutil.which("opencode") is None:
        print("error: opencode is not on PATH", file=sys.stderr)
        return 2
    try:
        command = build_command(args.role, args.difficulty, directory, args.format)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    contract = args.contract.read_text(encoding="utf-8") if args.contract else sys.stdin.read()
    if not contract.strip():
        print("error: task contract is empty", file=sys.stderr)
        return 2
    route = load_routes()[args.difficulty]
    if args.dry_run:
        print(json.dumps({
            "role": args.role,
            "difficulty": args.difficulty,
            "model": route["model"],
            "variant": route["variant"],
            "agent": f"quality-{args.role}",
            "directory": str(directory),
            "contract_chars": len(contract),
            "command": command,
        }, indent=2))
        return 0
    environment = os.environ.copy()
    environment["QUALITY_AGENTS_LEAF"] = "1"
    completed = subprocess.run(command + [contract], check=False, env=environment)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
