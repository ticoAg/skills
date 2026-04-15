import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class AttachmentsResourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.attachments = importlib.import_module("resources.attachments")
        self.context = self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_upload_requires_file(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            attachment_guid=None,
            params_json=None,
            data_json=None,
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
            file=None,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.attachments.handle(self.context, "upload", args)
        self.assertEqual(raised.exception.code, "invalid_attachment_payload")

    def test_delete_rejects_body(self):
        args = Namespace(
            task_id="5b52c178-737e-42d9-9eea-b82f78e5ea61",
            attachment_guid="attachment-guid",
            params_json=None,
            data_json='{"unexpected":true}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
            file=None,
        )
        with self.assertRaises(self.common.TaskV2CliError) as raised:
            self.attachments.handle(self.context, "delete", args)
        self.assertEqual(raised.exception.code, "invalid_attachment_payload")
