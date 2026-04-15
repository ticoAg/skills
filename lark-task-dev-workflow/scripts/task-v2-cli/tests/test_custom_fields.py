import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class CustomFieldsResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.custom_fields = importlib.import_module("resources.custom_fields")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_create_requires_top_level_resource_name_type(self):
        args = Namespace(
            custom_field_guid=None,
            option_guid=None,
            params_json=None,
            data_json='{"custom_field":{"name":"研发状态","type":"single_select"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.custom_fields.handle(self.context, "create", args)
        self.assertEqual(raised.exception.code, "invalid_custom_field_payload")

    def test_patch_requires_custom_field_and_update_fields(self):
        args = Namespace(
            custom_field_guid="edbb2b69-4e00-49ea-b42c-2faca1668342",
            option_guid=None,
            params_json=None,
            data_json='{"name":"研发状态2"}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.custom_fields.handle(self.context, "patch", args)
        self.assertEqual(raised.exception.code, "invalid_custom_field_payload")

    def test_create_option_requires_top_level_name(self):
        args = Namespace(
            custom_field_guid="edbb2b69-4e00-49ea-b42c-2faca1668342",
            option_guid=None,
            params_json=None,
            data_json='{"option":{"name":"todo"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.custom_fields.handle(self.context, "create-option", args)
        self.assertEqual(raised.exception.code, "invalid_custom_field_payload")

    def test_patch_option_requires_option_and_update_fields(self):
        args = Namespace(
            custom_field_guid="edbb2b69-4e00-49ea-b42c-2faca1668342",
            option_guid="option-guid",
            params_json=None,
            data_json='{"name":"todo"}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.custom_fields.handle(self.context, "patch-option", args)
        self.assertEqual(raised.exception.code, "invalid_custom_field_payload")
