import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class SubtasksResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.subtasks = importlib.import_module("resources.subtasks")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_create_requires_top_level_summary(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            params_json=None,
            data_json='{"task":{"summary":"nested"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.subtasks.handle(self.context, "create", args)
        self.assertEqual(raised.exception.code, "invalid_subtask_payload")

    def test_list_returns_normalized_items_shape(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            params_json=None,
            data_json=None,
            page_size=50,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        raw = {"code": 0, "data": {"items": [{"guid": "sub1"}], "has_more": False, "page_token": ""}, "msg": "success"}
        with patch.object(self.subtasks, "run_api_command", return_value=raw):
            result = self.subtasks.handle(self.context, "list", args)
        self.assertEqual(
            result,
            {
                "ok": True,
                "resource": "subtasks",
                "action": "list",
                "items": [{"guid": "sub1"}],
                "has_more": False,
                "page_token": "",
                "response": raw,
            },
        )
