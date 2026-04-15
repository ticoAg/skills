from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, params_from_args, task_guid_from_args, validate_members_payload


BASE_PATH = "/open-apis/task/v2/tasks"


def _validate_create_payload(data: dict) -> dict:
    if "task" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_task_payload",
            "`tasks create` 需要 Task v2 顶层字段，例如 `summary`；不要传 `task`/`update_fields` 包装。",
        )
    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise TaskV2CliError("invalid_task_payload", "`tasks create` 需要非空字符串 `summary`。")
    normalized = dict(data)
    normalized["summary"] = summary.strip()
    return normalized


def _validate_patch_payload(data: dict) -> dict:
    task = data.get("task")
    update_fields = data.get("update_fields")
    if not isinstance(task, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_task_payload",
            "`tasks patch` 需要 `{ \"task\": {...}, \"update_fields\": [...] }`。",
        )
    if "summary" in update_fields:
        summary = task.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise TaskV2CliError("invalid_task_payload", "`tasks patch` 更新 `summary` 时必须提供非空 `task.summary`。")
    normalized = dict(data)
    if "summary" in update_fields and isinstance(task.get("summary"), str):
        normalized_task = dict(task)
        normalized_task["summary"] = normalized_task["summary"].strip()
        normalized["task"] = normalized_task
    return normalized


def _validate_add_members_payload(data: dict) -> dict:
    return validate_members_payload(
        data,
        error_code="invalid_task_payload",
        action_label="tasks add-members",
        allowed_roles={"assignee", "follower"},
        allowed_types={"user", "app"},
        role_mode="required",
    )


def _validate_remove_tasklist_payload(data: dict, *, tasklist_guid: str | None) -> dict:
    if "task" in data or "update_fields" in data:
        raise TaskV2CliError("invalid_task_payload", "`tasks remove-tasklist` 需要顶层 `tasklist_guid`。")
    resolved = tasklist_guid or data.get("tasklist_guid")
    if not isinstance(resolved, str) or not resolved.strip():
        raise TaskV2CliError("invalid_task_payload", "`tasks remove-tasklist` 需要 `--tasklist-guid` 或 `data_json.tasklist_guid`。")
    if data.get("tasklist_guid") and tasklist_guid and data.get("tasklist_guid") != tasklist_guid:
        raise TaskV2CliError("invalid_task_payload", "`tasks remove-tasklist` 的 `--tasklist-guid` 与 `data_json.tasklist_guid` 不一致。")
    return {"tasklist_guid": resolved.strip()}


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    if action == "list":
        return run_api_command(
            context,
            "GET",
            BASE_PATH,
            params=params_from_args(args),
            page_all=args.page_all,
            page_limit=args.page_limit,
            page_delay=args.page_delay,
            dry_run=args.dry_run,
        )
    if action == "create":
        return run_api_command(
            context,
            "POST",
            BASE_PATH,
            params=params_from_args(args),
            data=_validate_create_payload(data_from_args(args)),
            dry_run=args.dry_run,
        )

    task_guid = task_guid_from_args(context, args, f"tasks {action}")
    if action == "get":
        return run_api_command(context, "GET", f"{BASE_PATH}/{task_guid}", params=params_from_args(args), dry_run=args.dry_run)
    if action == "patch":
        return run_api_command(
            context,
            "PATCH",
            f"{BASE_PATH}/{task_guid}",
            params=params_from_args(args),
            data=_validate_patch_payload(data_from_args(args)),
            dry_run=args.dry_run,
        )
    if action == "delete":
        return run_api_command(context, "DELETE", f"{BASE_PATH}/{task_guid}", params=params_from_args(args), dry_run=args.dry_run)
    if action == "add-members":
        return run_api_command(
            context,
            "POST",
            f"{BASE_PATH}/{task_guid}/add_members",
            params=params_from_args(args),
            data=_validate_add_members_payload(data_from_args(args)),
            dry_run=args.dry_run,
        )
    if action == "remove-tasklist":
        return run_api_command(
            context,
            "POST",
            f"{BASE_PATH}/{task_guid}/remove_tasklist",
            params=params_from_args(args),
            data=_validate_remove_tasklist_payload(data_from_args(args), tasklist_guid=getattr(args, "tasklist_guid", None)),
            dry_run=args.dry_run,
        )
    if action == "tasklists":
        return run_api_command(context, "GET", f"{BASE_PATH}/{task_guid}/tasklists", params=params_from_args(args), dry_run=args.dry_run)

    raise TaskV2CliError("unsupported_action", f"`tasks {action}` 暂不支持")
