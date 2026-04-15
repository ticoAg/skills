from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, normalize_list_response, params_from_args, task_guid_from_args


def _validate_create_payload(data: dict) -> dict:
    if "task" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_subtask_payload",
            "`subtasks create` 需要 Task v2 顶层字段，例如 `summary`；不要传 `task`/`update_fields` 包装。",
        )
    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise TaskV2CliError("invalid_subtask_payload", "`subtasks create` 需要非空字符串 `summary`。")
    normalized = dict(data)
    normalized["summary"] = summary.strip()
    return normalized


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    task_guid = task_guid_from_args(context, args, f"subtasks {action}")
    path = f"/open-apis/task/v2/tasks/{task_guid}/subtasks"
    if action == "list":
        raw = run_api_command(context, "GET", path, params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
        return normalize_list_response(raw, resource="subtasks", action="list")
    if action == "create":
        return run_api_command(context, "POST", path, params=params_from_args(args), data=_validate_create_payload(data_from_args(args)), dry_run=args.dry_run)
    raise TaskV2CliError("unsupported_action", f"`subtasks {action}` 暂不支持")
