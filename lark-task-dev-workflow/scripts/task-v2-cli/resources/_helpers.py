from __future__ import annotations

from argparse import Namespace
from typing import Any

from common import TaskV2CliError, parse_json_object
from resolve import resolve_task_guid


def params_from_args(args: Namespace) -> dict[str, Any]:
    params = parse_json_object(getattr(args, "params_json", None), "--params-json")
    page_size = int(getattr(args, "page_size", 0) or 0)
    page_token = getattr(args, "page_token", None)
    if page_size > 0:
        params["page_size"] = page_size
    if page_token:
        params["page_token"] = page_token
    return params


def data_from_args(args: Namespace) -> dict[str, Any]:
    return parse_json_object(getattr(args, "data_json", None), "--data-json")


def require_arg(value: str | None, flag: str, action: str) -> str:
    if not value:
        raise TaskV2CliError("argument_missing", f"`{action}` 需要 `{flag}`")
    return value


def task_guid_from_args(context, args: Namespace, action: str) -> str:
    task_id = require_arg(getattr(args, "task_id", None), "--task-id", action)
    return resolve_task_guid(task_id, context)


def validate_members_payload(
    data: dict[str, Any],
    *,
    error_code: str,
    action_label: str,
    allowed_roles: set[str] | None,
    allowed_types: set[str],
    role_mode: str,
) -> dict[str, Any]:
    members = data.get("members")
    if not isinstance(members, list) or not members:
        raise TaskV2CliError(error_code, f"`{action_label}` 需要非空 `members` 数组。")

    normalized_members: list[dict[str, Any]] = []
    for index, member in enumerate(members):
        if not isinstance(member, dict):
            raise TaskV2CliError(error_code, f"`{action_label}` 的 `members[{index}]` 必须是对象。")
        member_id = member.get("id")
        if not isinstance(member_id, str) or not member_id.strip():
            raise TaskV2CliError(error_code, f"`{action_label}` 的 `members[{index}].id` 必须是非空字符串。")
        role = member.get("role")
        if role_mode == "required":
            if not isinstance(role, str) or role not in (allowed_roles or set()):
                allowed = ", ".join(sorted(allowed_roles or set()))
                raise TaskV2CliError(error_code, f"`{action_label}` 的 `members[{index}].role` 必须是：{allowed}。")
        elif role_mode == "forbidden":
            if role not in (None, ""):
                raise TaskV2CliError(error_code, f"`{action_label}` 的 `members[{index}]` 不应传 `role`。")
        member_type = member.get("type", "user")
        if not isinstance(member_type, str) or member_type not in allowed_types:
            allowed = ", ".join(sorted(allowed_types))
            raise TaskV2CliError(error_code, f"`{action_label}` 的 `members[{index}].type` 必须是：{allowed}。")
        normalized_member = dict(member)
        normalized_member["id"] = member_id.strip()
        normalized_member["type"] = member_type
        if role_mode == "required":
            normalized_member["role"] = role
        else:
            normalized_member.pop("role", None)
        normalized_members.append(normalized_member)

    normalized = dict(data)
    normalized["members"] = normalized_members
    return normalized


def normalize_list_response(raw: dict[str, Any], *, resource: str, action: str) -> dict[str, Any]:
    data = raw.get("data", {}) if isinstance(raw, dict) else {}
    return {
        "ok": True,
        "resource": resource,
        "action": action,
        "items": data.get("items") or [],
        "has_more": bool(data.get("has_more", False)),
        "page_token": data.get("page_token", ""),
        "response": raw,
    }


def normalize_single_response(raw: dict[str, Any], *, resource: str, action: str, key: str) -> dict[str, Any]:
    data = raw.get("data", {}) if isinstance(raw, dict) else {}
    return {
        "ok": True,
        "resource": resource,
        "action": action,
        key: data.get(key) or {},
        "response": raw,
    }
