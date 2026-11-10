import json
import os
import subprocess
import tempfile
import unittest
from importlib import reload
from pathlib import Path
from unittest.mock import patch

from jflap_mcp.jff import build_fa_jff, parse_fa_jff, simulate_fa, validate_fa


class JflapFileBasedTests(unittest.TestCase):
    def setUp(self):
        self.states = ["q0", "q1"]
        self.alphabet = ["a"]
        self.transitions = [{"from": "q0", "read": "a", "to": "q1"}]

    def test_create_parse_validate_and_simulate_without_jar(self):
        xml = build_fa_jff(self.states, self.alphabet, "q0", ["q1"], self.transitions)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "automata.jff"
            path.write_text(xml, encoding="utf-8")
            parsed = parse_fa_jff(path.read_text(encoding="utf-8"))
        self.assertEqual(parsed["states"], self.states)
        self.assertTrue(validate_fa(self.states, self.alphabet, "q0", ["q1"], self.transitions)["valid"])
        self.assertTrue(simulate_fa(self.states, "q0", ["q1"], self.transitions, "a")["accepted"])
        self.assertFalse(simulate_fa(self.states, "q0", ["q1"], self.transitions, "")["accepted"])

    def test_jflap_info_uses_environment_paths(self):
        from jflap_mcp import server

        with tempfile.TemporaryDirectory() as temp_dir:
            jar = Path(temp_dir) / "custom.jar"
            launcher = Path(temp_dir) / "custom-launcher"
            jar.touch()
            launcher.touch()
            with patch.dict(os.environ, {"JFLAP_JAR": str(jar), "JFLAP_LAUNCHER": str(launcher)}):
                reload(server)
                info = json.loads(server.jflap_info())
                self.assertTrue(info["jar_exists"])
                self.assertTrue(info["launcher_exists"])
                self.assertEqual(info["jar"], str(jar))
            reload(server)


class PortableWrapperTests(unittest.TestCase):
    def test_python_wrappers_resolve_home_at_runtime(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_home = Path(temp_dir)
            for server, command in (("jflap", "jflap-mcp"), ("packet-tracer", "pt-mcp")):
                target = fake_home / ".local/share/corvosetup/mcp" / server / "bin" / command
                target.parent.mkdir(parents=True)
                marker = fake_home / f"{server}-called"
                target.write_text(f"#!/bin/sh\nprintf '%s' \"$*\" > {marker}\n", encoding="utf-8")
                target.chmod(0o755)
                subprocess.run([str(root / "scripts" / f"mcp-{server}")], env={**os.environ, "HOME": str(fake_home)}, check=True)
                self.assertEqual(marker.read_text(encoding="utf-8"), "--stdio" if server == "packet-tracer" else "")

    def test_scrapling_and_firefox_wrappers_use_corvosetup_environments(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_home = Path(temp_dir)
            base = fake_home / ".local/share/corvosetup/mcp"
            for server, command in (("scrapling", "scrapling"), ("firefox-local", "python")):
                target = base / server / "bin" / command
                target.parent.mkdir(parents=True)
                target.write_text("#!/bin/sh\nprintf '%s ' \"$@\"\n", encoding="utf-8")
                target.chmod(0o755)
            env = {**os.environ, "HOME": str(fake_home)}
            scrapling = subprocess.check_output([str(root / "scripts/mcp-scrapling")], env=env, text=True)
            self.assertEqual(scrapling.split(), ["mcp"])
            firefox = subprocess.check_output([str(root / "scripts/mcp-firefox-local")], env=env, text=True)
            self.assertEqual(firefox.split(), [str(base / "firefox-local/server.py")])

    def test_youtube_wrapper_pins_package_and_keeps_key_out_of_configs(self):
        root = Path(__file__).resolve().parents[1]
        wrapper = (root / "scripts/mcp-youtube-research").read_text(encoding="utf-8")
        self.assertIn("@coyasong/youtube-mcp-server@2.0.0", wrapper)
        self.assertNotIn("@latest", wrapper)
        for config in ("config/codex/config.toml", "config/opencode/opencode.json", "config/claude/mcp.json"):
            self.assertNotIn("YOUTUBE_API_KEY=", (root / config).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
