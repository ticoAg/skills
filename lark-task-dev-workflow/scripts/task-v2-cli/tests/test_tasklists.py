import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class TasklistsResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.tasklists = importlib.import_module("resources.tasklists")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_create_requires_top_level_name(self):
        args = Namespace(
            tasklist_guid=None,
            params_json=None,
            data_json='{"tasklist":{"name":"nested"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasklists.handle(self.context, "create", args)
        self.assertEqual(raised.exception.code, "invalid_tasklist_payload")

    def test_patch_requires_tasklist_and_update_fields(self):
        args = Namespace(
            tasklist_guid="bf824a07-def8-4068-9fca-24530698ed1b",
            params_json=None,
            data_json='{"name":"plain"}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasklists.handle(self.context, "patch", args)
        self.assertEqual(raised.exception.code, "invalid_tasklist_payload")

    def test_add_members_requires_members_array(self):
        args = Namespace(
            tasklist_guid="bf824a07-def8-4068-9fca-24530698ed1b",
            params_json=None,
            data_json='{"members":{"id":"ou_x"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasklists.handle(self.context, "add-members", args)
        self.assertEqual(raised.exception.code, "invalid_tasklist_payload")

    def test_remove_members_rejects_owner_role(self):
        args = Namespace(
            tasklist_guid="bf824a07-def8-4068-9fca-24530698ed1b",
            params_json=None,
            data_json='{"members":[{"id":"ou_x","type":"user","role":"owner"}]}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.tasklists.handle(self.context, "remove-members", args)
        self.assertEqual(raised.exception.code, "invalid_tasklist_payload")
