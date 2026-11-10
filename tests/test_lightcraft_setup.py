import hashlib
import io
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
import craft_install


class LightCraftSetupTests(unittest.TestCase):
    def test_authorization_and_dry_run_write_nothing(self):
        with tempfile.TemporaryDirectory() as dest:
            env = {**os.environ, "HOME": dest, "CORVOSETUP_AUTHORIZED": "0"}
            command = [sys.executable, str(ROOT / "scripts/install_lightcraft.py")]
            self.assertNotEqual(subprocess.run(command, env=env, capture_output=True).returncode, 0)
            allowed = subprocess.run(command, env={**env, "CORVOSETUP_AUTHORIZED": "1", "CORVOSETUP_DRY_RUN": "1"}, capture_output=True)
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertEqual(list(Path(dest).iterdir()), [])

    def test_install_publishes_headless_and_app_launchers(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory(prefix="light craft ") as dest:
            archive = Path(temp) / "light.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for name, data in {
                    "release/bin/lightcraft": b"#!/bin/sh\nexit 0\n",
                    "release/bin/lightcraft-cli": b"#!/bin/sh\nprintf '%s\\n' \"$@\"\n",
                    "release/share/applications/ai.storyteller.lightcraft.desktop": b"[Desktop Entry]\nType=Application\nExec=lightcraft %F\n",
                }.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    tar.addfile(member, io.BytesIO(data))
            manifest = {"sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "archive_root": "release"}
            home = Path(dest)
            with patch.dict(os.environ, {"HOME": dest}):
                craft_install.install_archive(archive, manifest, "lightcraft")
                craft_install.install_archive(archive, manifest, "lightcraft")
            env = {**os.environ, "HOME": dest}
            headless = subprocess.check_output([str(home / ".local/bin/corvosetup-mcp-lightcraft")], env=env, text=True)
            self.assertEqual(headless.splitlines(), ["mcp", "--compact"])
            app = subprocess.check_output([str(home / ".local/bin/corvosetup-mcp-lightcraft-app")], env=env, text=True)
            self.assertEqual(app.splitlines(), ["mcp", "--connect", "127.0.0.1:7980", "--compact"])
            self.assertFalse(list(home.rglob("*.corvosetup.bak*")))
            self.assertIn('lightcraft/bin/lightcraft" %F', (home / ".local/share/applications/ai.storyteller.lightcraft.desktop").read_text())

    def test_manifest_is_locked_to_official_release(self):
        import json
        manifest = json.loads((ROOT / "config/mcp/lightcraft.json").read_text())
        self.assertTrue(manifest["url"].startswith("https://github.com/storytold/lightcraft/releases/download/"))
        self.assertRegex(manifest["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
