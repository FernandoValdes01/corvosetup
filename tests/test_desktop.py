import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DesktopRestoreTests(unittest.TestCase):
    def test_dry_run_leaves_home_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["bash", str(ROOT / "scripts/07-desktop.sh")],
                env={**os.environ, "HOME": directory, "CORVOSETUP_AUTHORIZED": "1", "CORVOSETUP_DRY_RUN": "1"},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_visual_preferences_preserve_private_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".t3/userdata/client-settings.json"
            target.parent.mkdir(parents=True)
            original = {"favorites": ["local-favorite"], "providerModelPreferences": {"custom": True}, "glassOpacity": 100}
            target.write_text(json.dumps(original))
            result = subprocess.run(
                ["bash", str(ROOT / "scripts/07-desktop.sh")],
                env={**os.environ, "HOME": directory, "CORVOSETUP_AUTHORIZED": "1"},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = json.loads(target.read_text())
            self.assertEqual(actual["favorites"], original["favorites"])
            self.assertEqual(actual["providerModelPreferences"], original["providerModelPreferences"])
            self.assertEqual(actual["glassOpacity"], 55)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(target.with_suffix(".json.corvosetup.bak").read_text()), original)


if __name__ == "__main__":
    unittest.main()
