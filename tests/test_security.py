import importlib.util
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_security", ROOT / "scripts/check-security.py")
SECURITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SECURITY)


class SecurityConfigTests(unittest.TestCase):
    def test_environment_placeholders_are_public_references(self):
        for value in ("${SERVICE_TOKEN}", "$SERVICE_TOKEN", "{env:SERVICE_TOKEN}", "{file:~/.config/token}", "@ENV@SERVICE_TOKEN"):
            with self.subTest(value=value):
                self.assertTrue(SECURITY.public_reference(value))
        self.assertTrue(SECURITY.public_reference(""))

    def test_literal_credential_is_reported_without_value(self):
        credential = "synthetic" + "-credential" + "-not-real-38"
        issues = []
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            SECURITY.inspect_config(
                {"mcp": {"service": {"api_key": credential}}},
                "config/example.json",
                issues,
            )
        self.assertEqual(len(issues), 1)
        self.assertIn("credential literal", issues[0])
        self.assertIn("mcp.service.api_key", issues[0])
        self.assertNotIn(credential, issues[0])
        self.assertNotIn(credential, output.getvalue())

    def test_placeholders_are_allowed_for_credential_fields(self):
        issues = []
        SECURITY.inspect_config(
            {
                "api_key": "${SERVICE_API_KEY}",
                "access_token": "{env:ACCESS_TOKEN}",
                "client_secret": "@ENV@CLIENT_SECRET",
            },
            "config/example.json",
            issues,
        )
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
