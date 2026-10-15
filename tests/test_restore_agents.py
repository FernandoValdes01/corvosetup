import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / "scripts/restore_agents.py"


def run_restore(home, component="agents", *args):
    return subprocess.run(
        [sys.executable, str(RESTORE), component, *args],
        cwd=ROOT,
        env={**os.environ, "HOME": str(home)},
        check=True,
        capture_output=True,
        text=True,
    )


class RestoreAgentsTests(unittest.TestCase):
    def test_symlinked_parent_cannot_redirect_configuration_outside_home(self):
        with tempfile.TemporaryDirectory() as home_dir, tempfile.TemporaryDirectory() as outside_dir:
            home = Path(home_dir)
            (home / ".codex").symlink_to(outside_dir, target_is_directory=True)
            result = subprocess.run(
                [sys.executable, str(RESTORE), "agents"],
                env={**os.environ, "HOME": str(home)}, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(outside_dir).iterdir()), [])

    def test_symlinked_library_parent_cannot_redirect_skill_writes(self):
        with tempfile.TemporaryDirectory() as home_dir, tempfile.TemporaryDirectory() as outside_dir:
            home = Path(home_dir)
            library = home / ".local/share/corvosetup/skills"
            library.parent.mkdir(parents=True)
            library.symlink_to(outside_dir, target_is_directory=True)
            result = subprocess.run(
                [sys.executable, str(RESTORE), "skills"],
                env={**os.environ, "HOME": str(home)}, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(outside_dir).iterdir()), [])

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            result = run_restore(home, "agents", "--dry-run")
            self.assertIn("no writes", result.stdout)
            self.assertEqual(list(home.iterdir()), [])

    def test_merges_local_secrets_and_jsonc_without_emitting_them(self):
        secret = "synthetic" + "-local" + "-credential-47"
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            codex = home / ".codex/config.toml"
            codex.parent.mkdir(parents=True)
            codex.write_text(
                '[mcp_servers.private]\ncommand = "local-client"\n'
                f'env = {{ API_TOKEN = "{secret}" }}\n',
                encoding="utf-8",
            )
            opencode_dir = home / ".config/opencode"
            opencode_dir.mkdir(parents=True)
            (opencode_dir / "opencode.json").write_text(
                json.dumps({"mcp": {"private": {"type": "local", "env": {"API_TOKEN": secret}}}}),
                encoding="utf-8",
            )
            (opencode_dir / "opencode.jsonc").write_text(
                '''{
                  // comments, trailing commas, and URL text must survive parsing
                  "mcp": { "local-commented": { "url": "https://example.invalid/a//b,", }, },
                  /* a block comment */ "custom": [1, 2,],
                }''',
                encoding="utf-8",
            )

            result = run_restore(home)

            saved_codex = codex.read_text(encoding="utf-8")
            codex_data = tomllib.loads(saved_codex)
            self.assertEqual(codex_data["mcp_servers"]["private"]["env"]["API_TOKEN"], secret)
            saved_opencode = json.loads((opencode_dir / "opencode.jsonc").read_text(encoding="utf-8"))
            self.assertEqual(saved_opencode["mcp"]["private"]["env"]["API_TOKEN"], secret)
            self.assertEqual(saved_opencode["mcp"]["local-commented"]["url"], "https://example.invalid/a//b,")
            self.assertEqual(saved_opencode["custom"], [1, 2])
            self.assertNotIn(secret, result.stdout + result.stderr)

    def test_private_project_state_is_left_in_place(self):
        secret = "synthetic" + "-project" + "-state-83"
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            project_file = home / ".codex/projects/local-session/state.json"
            private_config = home / ".config/opencode/project-private.json"
            project_file.parent.mkdir(parents=True)
            private_config.parent.mkdir(parents=True)
            project_file.write_text(secret, encoding="utf-8")
            private_config.write_text(secret, encoding="utf-8")

            run_restore(home)

            self.assertEqual(project_file.read_text(encoding="utf-8"), secret)
            self.assertEqual(private_config.read_text(encoding="utf-8"), secret)
            self.assertFalse((ROOT / "config/codex/projects").exists())
            self.assertFalse((ROOT / "config/opencode/projects").exists())

    def test_idempotence_keeps_backups_stable_and_config_mode_private(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            codex = home / ".codex/config.toml"
            opencode = home / ".config/opencode/opencode.jsonc"
            codex.parent.mkdir(parents=True)
            opencode.parent.mkdir(parents=True)
            codex.write_text('model = "local-choice"\n', encoding="utf-8")
            opencode.write_text('{"custom": true}\n', encoding="utf-8")

            run_restore(home)
            backups = sorted(str(path.relative_to(home)) for path in home.rglob("*.corvosetup.bak*"))
            run_restore(home)

            self.assertEqual(
                sorted(str(path.relative_to(home)) for path in home.rglob("*.corvosetup.bak*")),
                backups,
            )
            self.assertEqual(codex.stat().st_mode & 0o777, 0o600)
            self.assertEqual(opencode.stat().st_mode & 0o777, 0o600)

    def test_invalid_opencode_fails_before_either_config_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            opencode_dir = home / ".config/opencode"
            opencode_dir.mkdir(parents=True)
            (opencode_dir / "opencode.jsonc").write_text('{ "broken": [ }', encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(RESTORE), "agents"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((home / ".codex/config.toml").exists())
            self.assertFalse((opencode_dir / "opencode.json").exists())
            self.assertFalse((opencode_dir / "opencode.jsonc.corvosetup.bak").exists())

    def test_skills_share_library_preserve_collision_and_do_not_follow_external_symlink(self):
        secret = "synthetic" + "-outside" + "-secret-92"
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as outside_dir:
            home = Path(temp_dir)
            library = home / ".local/share/corvosetup/skills"
            collision = home / ".codex/skills/impeccable"
            collision.mkdir(parents=True)
            (collision / "local.txt").write_text("keep this skill", encoding="utf-8")
            external = Path(outside_dir) / "private.txt"
            external.write_text(secret, encoding="utf-8")
            unsafe_link = home / ".agents/skills/jflap"
            unsafe_link.parent.mkdir(parents=True)
            unsafe_link.symlink_to(external)

            run_restore(home, "skills")

            codex_link = home / ".codex/skills/impeccable"
            agents_link = home / ".agents/skills/impeccable"
            opencode_link = home / ".config/opencode/skills/impeccable"
            for link in (codex_link, agents_link, opencode_link):
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), (library / "impeccable").resolve())
            self.assertEqual((collision.with_name("impeccable.corvosetup.bak") / "local.txt").read_text(), "keep this skill")
            preserved_link = unsafe_link.with_name("jflap.corvosetup.bak")
            self.assertTrue(preserved_link.is_symlink())
            self.assertEqual(preserved_link.resolve(), external)
            self.assertEqual(external.read_text(encoding="utf-8"), secret)
            self.assertEqual((library / "jflap/SKILL.md").is_file(), True)


if __name__ == "__main__":
    unittest.main()
