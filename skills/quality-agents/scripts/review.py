#!/usr/bin/env python3
"""Run the fixed Luna XHIGH strict quality gate."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delegate import main  # noqa: E402


if __name__ == "__main__":
    original = sys.argv[1:]
    forbidden = ("--role", "--difficulty")
    if any(arg in forbidden or arg.startswith(tuple(f"{flag}=" for flag in forbidden)) for arg in original):
        print("error: review role and difficulty are fixed to strict-reviewer/review", file=sys.stderr)
        raise SystemExit(2)
    sys.argv = [sys.argv[0], "--role", "strict-reviewer", "--difficulty", "review", *original]
    raise SystemExit(main())
