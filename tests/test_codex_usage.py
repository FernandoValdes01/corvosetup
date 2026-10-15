import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CodexUsageCacheTests(unittest.TestCase):
    def test_fresh_cache_returns_usage_without_starting_codex(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            cache = home / ".cache/noctalia-codex-usage.json"
            cache.parent.mkdir()
            now = int(time.time())
            cache.write_text(json.dumps({"dailyRemaining": 62, "dailyResetsAt": now + 3600, "weeklyRemaining": 87, "weeklyResetsAt": now + 90000, "fetchedAt": now}))
            bin_dir = home / ".local/bin"
            bin_dir.mkdir(parents=True)
            fake = bin_dir / "codex"
            fake.write_text('#!/bin/sh\ntouch "$HOME/codex-was-started"\nexit 1\n')
            fake.chmod(0o755)
            result = subprocess.run(
                ["bash", str(ROOT / "config/noctalia/scripts/codex-usage.sh")],
                env={**os.environ, "HOME": directory, "XDG_CACHE_HOME": str(cache.parent)},
                capture_output=True, text=True, check=True,
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["dailyRemaining"], 62)
            self.assertEqual(data["weeklyRemaining"], 87)
            self.assertFalse(data["stale"])
            self.assertFalse((home / "codex-was-started").exists())


if __name__ == "__main__":
    unittest.main()
