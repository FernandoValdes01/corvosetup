#!/usr/bin/env python3
"""Check file selection and public configuration; never print secret values."""
import argparse
import fnmatch
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_PARTS = {"node_modules", ".venv", "__pycache__", "sessions", "secrets", "logs", "keys"}
FORBIDDEN_NAMES = {"auth.json", "credentials.json", "clerk-tokens.json", "fish_variables", "machine-id", "id_rsa", "id_ed25519"}
PRIVATE_KEYS = re.compile(r"^(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|authorization|bearer_token)$", re.I)


def public_reference(value):
    return isinstance(value, str) and (not value or value.startswith(("${", "$", "{env:", "{file:", "@ENV@")))


def inspect_config(data, path, issues, prefix=""):
    if isinstance(data, dict):
        for key, value in data.items():
            location = f"{prefix}.{key}" if prefix else key
            if PRIVATE_KEYS.match(key) and not public_reference(value):
                issues.append(f"{path}: credential literal at {location}")
            inspect_config(value, path, issues, location)
    elif isinstance(data, list):
        for item in data:
            inspect_config(item, path, issues, prefix)


def audit(staged=False):
    args = ["git", "ls-files", "-z"]
    if staged:
        args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    else:
        args += ["--cached", "--others", "--exclude-standard"]
    paths = set(subprocess.check_output(args, cwd=ROOT).decode().split("\0")) - {""}
    issues = []
    for name in sorted(paths):
        path = Path(name)
        if any(part in FORBIDDEN_PARTS or ".egg-info" in part for part in path.parts):
            issues.append(f"{name}: generated or private directory")
        if path.name in FORBIDDEN_NAMES or any(fnmatch.fnmatch(path.name, pattern) for pattern in ["*.sqlite*", "*.db", "*.key", "*.pem", "*.p12", "*.backup*", "*.before-*", "*.corvosetup.bak*", "*.pyc"]):
            issues.append(f"{name}: private or generated file")
        if path.name.startswith(".env") and path.name != ".env.example":
            issues.append(f"{name}: environment credential file")
        target = ROOT / path
        if not staged and not target.is_file():
            continue
        if staged:
            data = subprocess.check_output(["git", "show", ":" + name], cwd=ROOT)
        else:
            if target.is_symlink():
                issues.append(f"{name}: source symlinks must be materialized before publishing")
                continue
            data = target.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            if path.suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}:
                issues.append(f"{name}: unexpected binary file")
            continue
        if re.search(r"/home/[A-Za-z0-9_.-]+/", text):
            issues.append(f"{name}: machine-specific HOME path")
        if path.parts[0] == "config" and path.suffix in {".json", ".toml"}:
            try:
                parsed = json.loads(text) if path.suffix == ".json" else tomllib.loads(text)
                inspect_config(parsed, name, issues)
            except (ValueError, tomllib.TOMLDecodeError):
                issues.append(f"{name}: invalid structured configuration")
    for issue in issues:
        print(issue, file=sys.stderr)
    print(f"Public-file checks: {len(paths)} files, {len(issues)} findings.")
    return bool(issues)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    sys.exit(audit(parser.parse_args().staged))
