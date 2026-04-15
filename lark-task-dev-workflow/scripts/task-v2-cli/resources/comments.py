from __future__ import annotations

from argparse import Namespace
from typing import Any

from common import CliContext, TaskV2CliError, parse_json_object, run_api_command
from resolve import resolve_task_guid


BASE_PATH = "/open-apis/task/v2/comments"


def _params_from_args(args: Namespace, *, task_guid: str | None = None) -> dict[str, Any]:
    params = parse_json_object(getattr(args, "params_json", None), "--params-json")
    if task_guid:
        params.setdefault("resource_type", "task")
        params.setdefault("resource_id", task_guid)
    page_size = int(getattr(args, "page_size", 0) or 0)
    page_token = getattr(args, "page_token", None)
    if page_size > 0:
        params["page_size"] = page_size
    if page_token:
        params["page_token"] = page_token
    return params


def _validate_create_payload(data: dict[str, Any], task_guid: str) -> dict[str, Any]:
    if "comment" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_comment_payload",
            "`comments create` 需要顶层 `content`，不要传 `comment`/`update_fields` 包装。",
        )
    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        raise TaskV2CliError("invalid_comment_payload", "`comments create` 需要非空字符串 `content`。")
    if "resource_type" in data and data["resource_type"] != "task":
        raise TaskV2CliError("invalid_comment_payload", "`comments create` 目前只支持 `resource_type=task`。")
    if "resource_id" in data and data["resource_id"] != task_guid:
        raise TaskV2CliError("invalid_comment_payload", "`comments create` 的 `resource_id` 必须与 `--task-id` 归一化结果一致。")
    normalized = dict(data)
    normalized["resource_type"] = "task"
    normalized["resource_id"] = task_guid
    normalized["content"] = content.strip()
    return normalized


def _validate_patch_payload(data: dict[str, Any]) -> dict[str, Any]:
    comment = data.get("comment")
    update_fields = data.get("update_fields")
    if not isinstance(comment, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_comment_payload",
            "`comments patch` 需要 `{ \"comment\": {...}, \"update_fields\": [...] }`。",
        )
    if "content" in update_fields:
        content = comment.get("content")
        if not isinstance(content, str) or not content.strip():
            raise TaskV2CliError("invalid_comment_payload", "`comments patch` 更新 `content` 时必须提供非空 `comment.content`。")
    normalized = dict(data)
    if "content" in update_fields:
        normalized_comment = dict(comment)
        normalized_comment["content"] = normalized_comment["content"].strip()
        normalized["comment"] = normalized_comment
    return normalized


def _validate_delete_payload(data: dict[str, Any]) -> None:
    if data:
        raise TaskV2CliError("invalid_comment_payload", "`comments delete` 不接受 `--data-json` 请求体。")


def handle(context: CliContext, action: str, args: Namespace) -> dict[str, Any]:
    task_id = getattr(args, "task_id", None)
    if not task_id:
        raise TaskV2CliError("task_id_missing", "`comments` 命令需要 `--task-id`")

    task_guid = resolve_task_guid(task_id, context)

    if action == "list":
        return run_api_command(
            context,
            "GET",
            BASE_PATH,
            params=_params_from_args(args, task_guid=task_guid),
            dry_run=bool(getattr(args, "dry_run", False)),
            page_all=bool(getattr(args, "page_all", False)),
            page_limit=getattr(args, "page_limit", None),
            page_delay=getattr(args, "page_delay", None),
        )

    comment_id = getattr(args, "comment_id", None)
    if action == "get":
        if not comment_id:
            raise TaskV2CliError("comment_id_missing", "`comments get` 需要 `--comment-id`")
        return run_api_command(context, "GET", f"{BASE_PATH}/{comment_id}", params=_params_from_args(args, task_guid=task_guid))

    data = parse_json_object(getattr(args, "data_json", None), "--data-json")
    if action == "create":
        return run_api_command(
            context,
            "POST",
            BASE_PATH,
            params=_params_from_args(args),
            data=_validate_create_payload(data, task_guid),
            dry_run=args.dry_run,
        )
    if action == "patch":
        if not comment_id:
            raise TaskV2CliError("comment_id_missing", "`comments patch` 需要 `--comment-id`")
        return run_api_command(
            context,
            "PATCH",
            f"{BASE_PATH}/{comment_id}",
            params=_params_from_args(args, task_guid=task_guid),
            data=_validate_patch_payload(data),
            dry_run=args.dry_run,
        )
    if action == "delete":
        if not comment_id:
            raise TaskV2CliError("comment_id_missing", "`comments delete` 需要 `--comment-id`")
        _validate_delete_payload(data)
        return run_api_command(
            context,
            "DELETE",
            f"{BASE_PATH}/{comment_id}",
            params=_params_from_args(args, task_guid=task_guid),
            dry_run=args.dry_run,
        )

    raise TaskV2CliError("unsupported_action", f"`comments {action}` 暂不支持")
