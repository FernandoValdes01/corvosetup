#!/usr/bin/env python3
"""Install or update the bundled Quality Agents roles for OpenCode."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.home() / ".config/opencode/agents")
    parser.add_argument("--force", action="store_true", help="Replace installed quality-* agents")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent / "agents/opencode"
    args.target.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.glob("quality-*.md")):
        target = args.target / path.name
        if target.exists() and target.read_bytes() != path.read_bytes() and not args.force:
            raise SystemExit(f"refusing to overwrite modified agent: {target}")
        shutil.copy2(path, target)
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
