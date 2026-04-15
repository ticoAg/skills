from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, params_from_args, require_arg, validate_members_payload


BASE_PATH = "/open-apis/task/v2/tasklists"


def _validate_create_payload(data: dict) -> dict:
    if "tasklist" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_tasklist_payload",
            "`tasklists create` 需要 Task v2 顶层字段，例如 `name`；不要传 `tasklist`/`update_fields` 包装。",
        )
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise TaskV2CliError("invalid_tasklist_payload", "`tasklists create` 需要非空字符串 `name`。")
    normalized = dict(data)
    normalized["name"] = name.strip()
    return normalized


def _validate_patch_payload(data: dict) -> dict:
    tasklist = data.get("tasklist")
    update_fields = data.get("update_fields")
    if not isinstance(tasklist, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_tasklist_payload",
            "`tasklists patch` 需要 `{ \"tasklist\": {...}, \"update_fields\": [...] }`。",
        )
    if "name" in update_fields:
        name = tasklist.get("name")
        if not isinstance(name, str) or not name.strip():
            raise TaskV2CliError("invalid_tasklist_payload", "`tasklists patch` 更新 `name` 时必须提供非空 `tasklist.name`。")
    normalized = dict(data)
    if "name" in update_fields and isinstance(tasklist.get("name"), str):
        normalized_tasklist = dict(tasklist)
        normalized_tasklist["name"] = normalized_tasklist["name"].strip()
        normalized["tasklist"] = normalized_tasklist
    return normalized


def _validate_add_members_payload(data: dict) -> dict:
    return validate_members_payload(
        data,
        error_code="invalid_tasklist_payload",
        action_label="tasklists add-members",
        allowed_roles={"editor", "viewer"},
        allowed_types={"user", "chat", "app"},
        role_mode="required",
    )


def _validate_remove_members_payload(data: dict) -> dict:
    return validate_members_payload(
        data,
        error_code="invalid_tasklist_payload",
        action_label="tasklists remove-members",
        allowed_roles=None,
        allowed_types={"user", "chat", "app"},
        role_mode="forbidden",
    )


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    if action == "list":
        return run_api_command(context, "GET", BASE_PATH, params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
    if action == "create":
        return run_api_command(context, "POST", BASE_PATH, params=params_from_args(args), data=_validate_create_payload(data_from_args(args)), dry_run=args.dry_run)

    tasklist_guid = require_arg(getattr(args, "tasklist_guid", None), "--tasklist-guid", f"tasklists {action}")
    path = f"{BASE_PATH}/{tasklist_guid}"
    if action == "get":
        return run_api_command(context, "GET", path, params=params_from_args(args), dry_run=args.dry_run)
    if action == "patch":
        return run_api_command(context, "PATCH", path, params=params_from_args(args), data=_validate_patch_payload(data_from_args(args)), dry_run=args.dry_run)
    if action == "delete":
        return run_api_command(context, "DELETE", path, params=params_from_args(args), dry_run=args.dry_run)
    if action == "tasks":
        return run_api_command(context, "GET", f"{path}/tasks", params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
    if action == "add-members":
        return run_api_command(context, "POST", f"{path}/add_members", params=params_from_args(args), data=_validate_add_members_payload(data_from_args(args)), dry_run=args.dry_run)
    if action == "remove-members":
        return run_api_command(context, "POST", f"{path}/remove_members", params=params_from_args(args), data=_validate_remove_members_payload(data_from_args(args)), dry_run=args.dry_run)

    raise TaskV2CliError("unsupported_action", f"`tasklists {action}` 暂不支持")
