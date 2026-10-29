#!/usr/bin/env python3
"""Install a locked official Craft editor release without sudo."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import urllib.request

from restore_agents import backup, check_parents

ROOT = Path(__file__).resolve().parents[1]


def check_destination(path):
    check_parents(path)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f"Refusing non-regular destination: {path}")


def publish(source, target, mode, content=None):
    check_destination(target)
    data = source.read_bytes() if content is None else content
    if target.is_file() and target.read_bytes() == data:
        target.chmod(mode)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    backup(target)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        pending = Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            pending.chmod(mode)
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)


def install_archive(archive, manifest, app="filmcraft"):
    if app not in {"filmcraft", "photocraft"}:
        raise ValueError("Unsupported Craft editor")
    title = "FilmCraft" if app == "filmcraft" else "PhotoCraft"
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError(f"{title} checksum mismatch; nothing installed")
    home = Path.home()
    prefix = home / ".local/opt" / app
    with tempfile.TemporaryDirectory(prefix=f"corvosetup-{app}-") as temporary:
        unpacked = Path(temporary)
        with tarfile.open(archive, "r:gz") as bundle:
            # The official bundle needs no links or special files.
            if any(not (m.isfile() or m.isdir()) for m in bundle.getmembers()):
                raise ValueError("Unexpected archive links or special files")
            bundle.extractall(unpacked, filter="data")
        source = unpacked / manifest["archive_root"]
        files = []
        for binary in (app, f"{app}-cli"):
            path = source / "bin" / binary
            if not path.is_file():
                raise ValueError(f"Missing release binary: {binary}")
            files.append((path, prefix / "bin" / binary, 0o755, None))
        for path in sorted((source / "share").rglob("*")):
            if path.is_file():
                relative = path.relative_to(source / "share")
                if relative.parts[0] not in {"applications", "doc", "icons", "metainfo", "mime"}:
                    continue
                data = None
                if relative == Path(f"applications/ai.storyteller.{app}.desktop"):
                    executable = str(prefix / "bin" / app)
                    escaped = executable.replace("\\", "\\\\").replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
                    escaped = escaped.replace("\\", "\\\\")
                    lines = path.read_text().splitlines()
                    data = ("\n".join(f'Exec="{escaped}" %F' if line.startswith("Exec=") else
                                      f"TryExec={executable}" if line.startswith("TryExec=") else
                                      line for line in lines) + "\n").encode()
                files.append((path, home / ".local/share" / relative, 0o644, data))
        files.append((ROOT / f"scripts/mcp-{app}", home / f".local/bin/corvosetup-mcp-{app}", 0o755, None))
        for _, destination, _, _ in files:
            check_destination(destination)
        for path, destination, mode, data in files:
            publish(path, destination, mode, data)


def main(app="filmcraft"):
    if app not in {"filmcraft", "photocraft"}:
        raise ValueError("Unsupported Craft editor")
    title = "FilmCraft" if app == "filmcraft" else "PhotoCraft"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Previously downloaded official archive; checksum still required")
    args = parser.parse_args()
    if os.environ.get("CORVOSETUP_AUTHORIZED") != "1":
        parser.error("Use the authorized CorvoSetup installer (CORVOSETUP_AUTHORIZED=1)")
    manifest = json.loads((ROOT / f"config/mcp/{app}.json").read_text())
    if os.environ.get("CORVOSETUP_DRY_RUN") == "1":
        print(f"Would install {title} {manifest['version']} and MCP under ~/.local; no downloads or writes")
        return
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        parser.error(f"The locked {title} release requires Linux x86_64")
    if any(c in str(Path.home()) for c in '\n\r\t%'):
        parser.error("HOME contains characters unsupported by desktop launchers")
    with tempfile.TemporaryDirectory(prefix=f"corvosetup-{app}-download-") as temporary:
        archive = args.archive
        if archive is None:
            archive = Path(temporary) / f"{app}.tar.gz"
            with urllib.request.urlopen(manifest["url"], timeout=60) as response, archive.open("wb") as output:
                shutil.copyfileobj(response, output)
        install_archive(archive, manifest, app)
    print(f"{title} {manifest['version']} and its native MCP installed; no other Craft apps")
