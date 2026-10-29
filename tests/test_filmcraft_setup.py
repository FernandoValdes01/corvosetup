import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("install_filmcraft", ROOT / "scripts/install_filmcraft.py")
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class FilmcraftSetupTests(unittest.TestCase):
    def bundle(self, directory, bad_link=False):
        archive = directory / "fixture.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for name, content in {
                "release/bin/filmcraft": b"#!/bin/sh\nexit 0\n",
                "release/bin/filmcraft-cli": b"#!/bin/sh\nprintf '%s\\n' \"$*\"\n",
                "release/share/applications/ai.storyteller.filmcraft.desktop": b"[Desktop Entry]\nType=Application\nName=FilmCraft\nExec=filmcraft %F\nTryExec=filmcraft\n",
                "release/share/doc/filmcraft/NOTICE": b"fixture license notice",
            }.items():
                entry = tarfile.TarInfo(name)
                entry.size = len(content)
                tar.addfile(entry, io.BytesIO(content))
            if bad_link:
                entry = tarfile.TarInfo("release/bin/escape")
                entry.type, entry.linkname = tarfile.SYMTYPE, "/tmp/outside"
                tar.addfile(entry)
        return archive, {"sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "archive_root": "release"}

    def test_authorization_and_dry_run_do_not_write_or_download(self):
        with tempfile.TemporaryDirectory() as temp:
            env = {**os.environ, "HOME": temp, "CORVOSETUP_AUTHORIZED": "0"}
            script = str(ROOT / "scripts/install_filmcraft.py")
            rejected = subprocess.run([sys.executable, script], env=env, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            accepted = subprocess.run([sys.executable, script], env={**env, "CORVOSETUP_AUTHORIZED": "1", "CORVOSETUP_DRY_RUN": "1"}, capture_output=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_isolated_install_wrapper_desktop_and_idempotence(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory(prefix="film craft ") as dest:
            archive, manifest = self.bundle(Path(temp))
            with patch.dict(os.environ, {"HOME": dest}):
                INSTALL.install_archive(archive, manifest)
                INSTALL.install_archive(archive, manifest)
            home = Path(dest)
            wrapper = home / ".local/bin/corvosetup-mcp-filmcraft"
            result = subprocess.check_output([str(wrapper), "--project", "project with spaces.fcproj"], env={**os.environ, "HOME": dest}, text=True)
            self.assertEqual(result.strip(), "mcp --project project with spaces.fcproj")
            self.assertIn(f'Exec="{dest}/.local/opt/filmcraft/bin/filmcraft" %F', (home / ".local/share/applications/ai.storyteller.filmcraft.desktop").read_text())
            self.assertFalse(list(home.rglob("*.corvosetup.bak*")))

    def test_invalid_checksum_and_archive_links_write_nothing(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as dest:
            archive, manifest = self.bundle(Path(temp))
            with patch.dict(os.environ, {"HOME": dest}):
                with self.assertRaisesRegex(ValueError, "checksum"):
                    INSTALL.install_archive(archive, {**manifest, "sha256": "invalid"})
                archive, manifest = self.bundle(Path(temp), bad_link=True)
                with self.assertRaisesRegex(ValueError, "links"):
                    INSTALL.install_archive(archive, manifest)
            self.assertEqual(list(Path(dest).iterdir()), [])

    def test_symlink_parents_and_leaf_cannot_redirect_install(self):
        for parent in (True, False):
            with self.subTest(parent=parent), tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as dest, tempfile.TemporaryDirectory() as outside:
                archive, manifest = self.bundle(Path(temp))
                home = Path(dest)
                if parent:
                    (home / ".local").symlink_to(outside, target_is_directory=True)
                else:
                    target = home / ".local/opt/filmcraft/bin/filmcraft"
                    target.parent.mkdir(parents=True)
                    target.symlink_to(Path(outside) / "untouched")
                with patch.dict(os.environ, {"HOME": dest}), self.assertRaises(ValueError):
                    INSTALL.install_archive(archive, manifest)
                self.assertEqual(list(Path(outside).iterdir()), [])

    def test_configs_render_filmcraft_in_both_clients(self):
        import tomllib
        import restore_agents
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"HOME": temp}):
            home = Path(temp)
            restore_agents.restore_agents(home)
            codex = tomllib.loads((home / ".codex/config.toml").read_text())
            opencode = json.loads((home / ".config/opencode/opencode.jsonc").read_text())
            expected = str(home / ".local/bin/corvosetup-mcp-filmcraft")
            self.assertEqual(codex["mcp_servers"]["filmcraft"]["command"], expected)
            self.assertEqual(opencode["mcp"]["filmcraft"]["command"], [expected])
            self.assertEqual((home / ".codex/config.toml").stat().st_mode & 0o777, 0o600)
