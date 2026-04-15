import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class SectionsResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.sections = importlib.import_module("resources.sections")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_create_requires_top_level_name_and_resource_type(self):
        args = Namespace(
            section_guid=None,
            params_json=None,
            data_json='{"section":{"name":"nested"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.sections.handle(self.context, "create", args)
        self.assertEqual(raised.exception.code, "invalid_section_payload")

    def test_patch_requires_section_and_update_fields(self):
        args = Namespace(
            section_guid="d57177c7-d964-c40f-b654-14bd5e619069",
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
            self.sections.handle(self.context, "patch", args)
        self.assertEqual(raised.exception.code, "invalid_section_payload")

    def test_delete_rejects_request_body(self):
        args = Namespace(
            section_guid="d57177c7-d964-c40f-b654-14bd5e619069",
            params_json=None,
            data_json='{"unexpected":true}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.sections.handle(self.context, "delete", args)
        self.assertEqual(raised.exception.code, "invalid_section_payload")

    def test_list_returns_normalized_items_shape(self):
        args = Namespace(
            section_guid=None,
            params_json=None,
            data_json=None,
            page_size=50,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        raw = {"code": 0, "data": {"items": [{"guid": "s1"}], "has_more": False, "page_token": ""}, "msg": "success"}
        with patch.object(self.sections, "run_api_command", return_value=raw):
            result = self.sections.handle(self.context, "list", args)
        self.assertEqual(
            result,
            {
                "ok": True,
                "resource": "sections",
                "action": "list",
                "items": [{"guid": "s1"}],
                "has_more": False,
                "page_token": "",
                "response": raw,
            },
        )

    def test_get_returns_normalized_section_shape(self):
        args = Namespace(
            section_guid="section-guid",
            params_json=None,
            data_json=None,
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        raw = {"code": 0, "data": {"section": {"guid": "section-guid"}}, "msg": "success"}
        with patch.object(self.sections, "run_api_command", return_value=raw):
            result = self.sections.handle(self.context, "get", args)
        self.assertEqual(
            result,
            {
                "ok": True,
                "resource": "sections",
                "action": "get",
                "section": {"guid": "section-guid"},
                "response": raw,
            },
        )

    def test_tasks_returns_normalized_items_shape(self):
        args = Namespace(
            section_guid="section-guid",
            params_json=None,
            data_json=None,
            page_size=50,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        raw = {"code": 0, "data": {"items": [{"guid": "t1"}], "has_more": True, "page_token": "next"}, "msg": "success"}
        with patch.object(self.sections, "run_api_command", return_value=raw):
            result = self.sections.handle(self.context, "tasks", args)
        self.assertEqual(
            result,
            {
                "ok": True,
                "resource": "sections",
                "action": "tasks",
                "items": [{"guid": "t1"}],
                "has_more": True,
                "page_token": "next",
                "response": raw,
            },
        )
