import importlib
import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class CommentsResourceTests(unittest.TestCase):
    def setUp(self):
        self.common = importlib.import_module("common")
        self.comments = importlib.import_module("resources.comments")

    def context(self):
        return self.common.CliContext(as_identity="user", profile=None, output_format="json", jq=None)

    def test_list_comments_uses_task_v2_path(self):
        args = Namespace(
            task_id="t100169",
            comment_id=None,
            params_json=None,
            data_json=None,
            page_size=100,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )

        with patch.object(self.comments, "resolve_task_guid", return_value="task-guid"), patch.object(
            self.comments, "run_api_command", return_value={"ok": True}
        ) as run_api:
            result = self.comments.handle(self.context(), "list", args)

        self.assertEqual(result, {"ok": True})
        run_api.assert_called_once()
        call = run_api.call_args
        self.assertEqual(call.args[1], "GET")
        self.assertEqual(call.args[2], "/open-apis/task/v2/comments")
        self.assertEqual(
            call.kwargs["params"],
            {"resource_type": "task", "resource_id": "task-guid", "page_size": 100},
        )

    def test_get_comment_uses_task_v2_path(self):
        args = Namespace(
            task_id="task-guid",
            comment_id="comment-guid",
            params_json=None,
            data_json=None,
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )

        with patch.object(self.comments, "resolve_task_guid", return_value="task-guid"), patch.object(
            self.comments, "run_api_command", return_value={"ok": True}
        ) as run_api:
            result = self.comments.handle(self.context(), "get", args)

        self.assertEqual(result, {"ok": True})
        run_api.assert_called_once()
        self.assertEqual(call_args := run_api.call_args.args, (self.context(), "GET", "/open-apis/task/v2/comments/comment-guid"))

    def test_create_comment_requires_top_level_content(self):
        args = Namespace(
            task_id="task-guid",
            comment_id=None,
            params_json=None,
            data_json='{"comment":{"content":"nested"}}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )

        with patch.object(self.comments, "resolve_task_guid", return_value="task-guid"):
            with self.assertRaises(self.common.TaskV2CliError) as raised:
                self.comments.handle(self.context(), "create", args)

        self.assertEqual(raised.exception.code, "invalid_comment_payload")

    def test_patch_comment_requires_comment_and_update_fields(self):
        args = Namespace(
            task_id="task-guid",
            comment_id="comment-guid",
            params_json=None,
            data_json='{"content":"plain"}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )

        with patch.object(self.comments, "resolve_task_guid", return_value="task-guid"):
            with self.assertRaises(self.common.TaskV2CliError) as raised:
                self.comments.handle(self.context(), "patch", args)

        self.assertEqual(raised.exception.code, "invalid_comment_payload")

    def test_delete_comment_rejects_request_body(self):
        args = Namespace(
            task_id="task-guid",
            comment_id="comment-guid",
            params_json=None,
            data_json='{"unexpected":true}',
            page_size=0,
            page_token=None,
            page_all=False,
            page_limit=10,
            page_delay=200,
            dry_run=False,
        )

        with patch.object(self.comments, "resolve_task_guid", return_value="task-guid"):
            with self.assertRaises(self.common.TaskV2CliError) as raised:
                self.comments.handle(self.context(), "delete", args)

        self.assertEqual(raised.exception.code, "invalid_comment_payload")


if __name__ == "__main__":
    unittest.main()
