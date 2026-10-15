#!/usr/bin/env python3
"""Restore public agent configuration without copying authentication or state."""

import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def check_parents(path):
    home = Path.home()
    relative = path.relative_to(home)
    ancestor = home
    for part in relative.parts[:-1]:
        ancestor = ancestor / part
        if ancestor.is_symlink():
            raise ValueError(f"Refusing a symlink in the destination's parents: {ancestor}")


def render(text, home):
    return text.replace("@HOME@", str(home))


def backup(path):
    if not path.exists() and not path.is_symlink():
        return
    candidate = path.with_name(path.name + ".corvosetup.bak")
    counter = 1
    while candidate.exists() or candidate.is_symlink():
        candidate = path.with_name(path.name + f".corvosetup.bak.{counter}")
        counter += 1
    if path.is_symlink():
        candidate.symlink_to(os.readlink(path))
    elif path.is_dir():
        shutil.copytree(path, candidate, symlinks=True)
    else:
        shutil.copy2(path, candidate)
        candidate.chmod(0o600)


def write(path, content, mode=0o644):
    check_parents(path)
    if path.is_file() and not path.is_symlink() and path.read_text() == content:
        path.chmod(mode)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    backup(path)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
            handle.flush()
            temporary.chmod(mode)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def link(source, target):
    check_parents(target)
    if target.is_symlink() and target.resolve() == source.resolve():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        # Move a collision instead of deleting an existing skill directory.
        candidate = target.with_name(target.name + ".corvosetup.bak")
        counter = 1
        while candidate.exists() or candidate.is_symlink():
            candidate = target.with_name(target.name + f".corvosetup.bak.{counter}")
            counter += 1
        target.rename(candidate)
    target.symlink_to(source, target_is_directory=source.is_dir())


def jsonc(text):
    """Remove JSONC comments and trailing commas only outside JSON strings."""
    result = []
    index = 0
    in_string = False
    while index < len(text):
        char = text[index]
        if in_string:
            result.append(char)
            if char == "\\" and index + 1 < len(text):
                index += 1
                result.append(text[index])
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            result.append(char)
        elif text[index:index + 2] == "//":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        elif text[index:index + 2] == "/*":
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unterminated JSONC comment")
            result.append(" ")
            index = end + 2
            continue
        else:
            result.append(char)
        index += 1
    clean = "".join(result)
    result, index, in_string = [], 0, False
    while index < len(clean):
        char = clean[index]
        if in_string and char == "\\" and index + 1 < len(clean):
            result.extend(clean[index:index + 2])
            index += 2
            continue
        if char == '"':
            in_string = not in_string
        if char == "," and not in_string:
            ahead = index + 1
            while ahead < len(clean) and clean[ahead].isspace():
                ahead += 1
            if ahead < len(clean) and clean[ahead] in "}]":
                index += 1
                continue
        result.append(char)
        index += 1
    return json.loads("".join(result))


def merge(existing, managed):
    for key, value in managed.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            merge(existing[key], value)
        else:
            existing[key] = value
    return existing


def toml_value(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value).lower()
    if isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{json.dumps(key)} = {toml_value(item)}" for key, item in value.items()) + " }"
    raise ValueError(f"Unsupported TOML value: {type(value).__name__}")


def dump_toml(data):
    lines = ["# Managed public defaults merged by corvosetup. Local credentials stay local."]

    def section(table, prefix=()):
        if prefix:
            lines.extend(["", "[" + ".".join(json.dumps(key) for key in prefix) + "]"])
        for key, value in table.items():
            if not isinstance(value, dict):
                lines.append(f"{json.dumps(key)} = {toml_value(value)}")
        for key, value in table.items():
            if isinstance(value, dict):
                section(value, prefix + (key,))

    section(data)
    result = "\n".join(lines) + "\n"
    assert tomllib.loads(result) == data
    return result


def restore_skills(home):
    library = home / ".local/share/corvosetup/skills"
    for directory in [library, home / ".agents/skills", home / ".codex/skills", home / ".config/opencode/skills"]:
        check_parents(directory / ".preflight")
    for source in sorted((ROOT / "skills").iterdir()):
        if not (source / "SKILL.md").is_file():
            continue
        target = library / source.name
        for path in sorted(source.rglob("*")):
            if path.is_file():
                write(target / path.relative_to(source), render(path.read_text(), home), path.stat().st_mode & 0o777)
        for client in [".agents/skills", ".codex/skills", ".config/opencode/skills"]:
            link(target, home / client / source.name)


def restore_agents(home):
    codex_path = home / ".codex/config.toml"
    check_parents(codex_path)
    check_parents(home / ".config/opencode/opencode.jsonc")
    managed = tomllib.loads(render((ROOT / "config/codex/config.toml").read_text(), home))
    existing = tomllib.loads(codex_path.read_text()) if codex_path.exists() else {}
    # Keep unrelated user skill overrides as well as private MCP credentials.
    previous = existing.get("skills", {}).get("config", [])
    overrides = managed.get("skills", {}).get("config", [])
    identities = {(item.get("name"), item.get("path")) for item in overrides}
    managed["skills"]["config"] = [item for item in previous if (item.get("name"), item.get("path")) not in identities] + overrides
    codex_content = dump_toml(merge(existing, managed))

    opencode_base = home / ".config/opencode"
    opencode_path = opencode_base / "opencode.jsonc"
    json_path = opencode_base / "opencode.json"
    # OpenCode loads .jsonc after .json. Preserve both layers when both exist.
    existing_json = jsonc(json_path.read_text()) if json_path.exists() else {}
    if opencode_path.exists():
        merge(existing_json, jsonc(opencode_path.read_text()))
    managed_json = json.loads(render((ROOT / "config/opencode/opencode.json").read_text(), home))
    paths = existing_json.get("skills", {}).get("paths", [])
    managed_json["skills"]["paths"] = list(dict.fromkeys(paths + managed_json["skills"]["paths"]))
    opencode_content = json.dumps(merge(existing_json, managed_json), ensure_ascii=False, indent=2) + "\n"

    # Validate all input configurations before writing either one.
    write(codex_path, codex_content, 0o600)
    write(opencode_path, opencode_content, 0o600)
    for client, directory in [("codex", home / ".codex"), ("opencode", opencode_base)]:
        source = ROOT / "config" / client
        for path in source.rglob("*"):
            if path.is_file() and path.name not in ["config.toml", "opencode.json"]:
                write(directory / path.relative_to(source), render(path.read_text(), home))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=["skills", "agents"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    home = Path.home()
    if args.dry_run:
        print(f"Would restore {args.component} under {home}; no writes.")
        return
    if args.component == "skills":
        restore_skills(home)
    else:
        restore_agents(home)


if __name__ == "__main__":
    main()
