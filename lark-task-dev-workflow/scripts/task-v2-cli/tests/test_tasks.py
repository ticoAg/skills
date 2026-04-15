import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class TasksResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.tasks = importlib.import_module("resources.tasks")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_create_requires_top_level_summary(self):
        args = Namespace(
            task_id=None,
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
            self.tasks.handle(self.context, "create", args)
        self.assertEqual(raised.exception.code, "invalid_task_payload")

    def test_patch_requires_task_and_update_fields(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            params_json=None,
            data_json='{"summary":"plain"}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasks.handle(self.context, "patch", args)
        self.assertEqual(raised.exception.code, "invalid_task_payload")

    def test_add_members_requires_members_array(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            tasklist_guid=None,
            params_json=None,
            data_json='{"members":{"id":"ou_x","role":"assignee"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasks.handle(self.context, "add-members", args)
        self.assertEqual(raised.exception.code, "invalid_task_payload")

    def test_remove_tasklist_requires_tasklist_guid(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            tasklist_guid=None,
            params_json=None,
            data_json="{}",
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasks.handle(self.context, "remove-tasklist", args)
        self.assertEqual(raised.exception.code, "invalid_task_payload")
