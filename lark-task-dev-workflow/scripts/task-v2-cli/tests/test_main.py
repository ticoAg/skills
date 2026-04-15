import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class MainCliTests(unittest.TestCase):
    def setUp(self):
        self.main = importlib.import_module("main")
        self.runner = CliRunner()

    def test_help_exits_successfully(self):
        result = self.runner.invoke(self.main.app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Task v2 wrapper powered by lark-cli auth", result.stdout)

    def test_write_operation_requires_yes_or_dry_run(self):
        result = self.runner.invoke(self.main.app, ["comments", "create", "--task-id", "t100169", "--data-json", "{}"])
        self.assertEqual(result.exit_code, 2)
        self.assertIn("write_confirmation_required", result.stdout)

    def test_read_operation_dispatches(self):
        with patch.object(self.main, "dispatch", return_value={"ok": True}) as dispatch, patch.object(
            self.main, "print_payload"
        ) as print_payload:
            result = self.runner.invoke(self.main.app, ["comments", "list", "--task-id", "t100169"])

        self.assertEqual(result.exit_code, 0)
        dispatch.assert_called_once()
        print_payload.assert_called_once_with({"ok": True}, "json", None)


if __name__ == "__main__":
    unittest.main()
