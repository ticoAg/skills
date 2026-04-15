import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


CLI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLI_DIR))


class ResolveTaskIdTests(unittest.TestCase):
    def setUp(self):
        self.resolve = importlib.import_module("resolve")

    def test_guid_passthrough(self):
        task_guid = "5b52c178-737e-42d9-9eea-b82f78e5ea61"

        self.assertEqual(self.resolve.resolve_task_guid(task_guid), task_guid)

    def test_applink_guid_extraction(self):
        task_guid = "5b52c178-737e-42d9-9eea-b82f78e5ea61"
        url = f"https://applink.feishu.cn/client/todo/detail?guid={task_guid}&suite_entity_num=t100169"

        self.assertEqual(self.resolve.resolve_task_guid(url), task_guid)

    def test_short_task_id_uses_search(self):
        with patch.object(self.resolve, "search_tasks", return_value=[{"guid": "guid-1"}]) as search:
            self.assertEqual(self.resolve.resolve_task_guid("t100169"), "guid-1")

        search.assert_called_once_with("t100169")

    def test_short_task_id_ambiguity_checks_task_detail(self):
        candidates = [{"guid": "guid-1"}, {"guid": "guid-2"}]
        details = {
            "guid-1": {"task_id": "t-other", "url": ""},
            "guid-2": {"task_id": "t100169", "url": ""},
        }

        with patch.object(self.resolve, "search_tasks", return_value=candidates), patch.object(
            self.resolve, "fetch_task", side_effect=lambda guid: details[guid]
        ):
            self.assertEqual(self.resolve.resolve_task_guid("t100169"), "guid-2")


if __name__ == "__main__":
    unittest.main()
