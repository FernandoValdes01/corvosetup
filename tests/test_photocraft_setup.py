import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import craft_install
import restore_agents


class PhotoCraftSetupTests(unittest.TestCase):
    def test_authorization_and_dry_run_write_nothing(self):
        with tempfile.TemporaryDirectory() as dest:
            env = {**os.environ, "HOME": dest, "CORVOSETUP_AUTHORIZED": "0"}
            command = [sys.executable, str(ROOT / "scripts/install_photocraft.py")]
            denied = subprocess.run(command, env=env, capture_output=True)
            self.assertNotEqual(denied.returncode, 0)
            allowed = subprocess.run(command, env={**env, "CORVOSETUP_AUTHORIZED": "1", "CORVOSETUP_DRY_RUN": "1"}, capture_output=True)
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertEqual(list(Path(dest).iterdir()), [])

    def test_install_wrapper_scope_and_idempotence_without_video_changes(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory(prefix="photo craft ") as dest:
            archive = Path(temp) / "photo.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for name, data in {
                    "release/bin/photocraft": b"#!/bin/sh\nexit 0\n",
                    "release/bin/photocraft-cli": b"#!/bin/sh\nprintf '%s\\n' \"$@\"\n",
                    "release/share/applications/ai.storyteller.photocraft.desktop": b"[Desktop Entry]\nType=Application\nName=PhotoCraft\nExec=photocraft %F\nTryExec=photocraft\n",
                }.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    tar.addfile(member, io.BytesIO(data))
            manifest = {"sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "archive_root": "release"}
            home = Path(dest)
            video = home / ".local/opt/filmcraft/bin/filmcraft-cli"
            video.parent.mkdir(parents=True)
            video.write_text("video unchanged")
            with patch.dict(os.environ, {"HOME": dest}):
                craft_install.install_archive(archive, manifest, "photocraft")
                craft_install.install_archive(archive, manifest, "photocraft")
            wrapper = home / ".local/bin/corvosetup-mcp-photocraft"
            env = {**os.environ, "HOME": dest, "PHOTOCRAFT_READ_ROOT": str(home / "read space"), "PHOTOCRAFT_WRITE_ROOT": str(home / "write space")}
            result = subprocess.check_output([str(wrapper)], env=env, text=True).splitlines()
            self.assertEqual(result, ["mcp", "--automation-read-root", env["PHOTOCRAFT_READ_ROOT"], "--automation-write-root", env["PHOTOCRAFT_WRITE_ROOT"]])
            self.assertEqual(video.read_text(), "video unchanged")
            self.assertFalse(list(home.rglob("*.corvosetup.bak*")))
            self.assertIn('photocraft/bin/photocraft" %F', (home / '.local/share/applications/ai.storyteller.photocraft.desktop').read_text())

    def test_both_editor_configs_render_and_remain_private(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"HOME": temp}):
            home = Path(temp)
            restore_agents.restore_agents(home)
            codex = tomllib.loads((home / ".codex/config.toml").read_text())
            opencode = json.loads((home / ".config/opencode/opencode.jsonc").read_text())
            for app in ("filmcraft", "photocraft"):
                expected = str(home / f".local/bin/corvosetup-mcp-{app}")
                self.assertEqual(codex['mcp_servers'][app]['command'], expected)
                self.assertEqual(opencode['mcp'][app]['command'], [expected])
            self.assertEqual((home / '.codex/config.toml').stat().st_mode & 0o777, 0o600)

    def test_unknown_editor_cannot_choose_arbitrary_manifest_or_destination(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            craft_install.install_archive(Path('unused'), {}, '../other')
