from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, normalize_list_response, normalize_single_response, params_from_args, require_arg


BASE_PATH = "/open-apis/task/v2/sections"


def _validate_create_payload(data: dict) -> dict:
    if "section" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_section_payload",
            "`sections create` 需要 Task v2 顶层字段，例如 `name` / `resource_type`。",
        )
    missing = [field for field in ("name", "resource_type") if not data.get(field)]
    if missing:
        raise TaskV2CliError("invalid_section_payload", f"`sections create` 缺少必填字段：{', '.join(missing)}。")
    normalized = dict(data)
    if isinstance(normalized["name"], str):
        normalized["name"] = normalized["name"].strip()
    return normalized


def _validate_patch_payload(data: dict) -> dict:
    section = data.get("section")
    update_fields = data.get("update_fields")
    if not isinstance(section, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_section_payload",
            "`sections patch` 需要 `{ \"section\": {...}, \"update_fields\": [...] }`。",
        )
    if "name" in update_fields:
        name = section.get("name")
        if not isinstance(name, str) or not name.strip():
            raise TaskV2CliError("invalid_section_payload", "`sections patch` 更新 `name` 时必须提供非空 `section.name`。")
    normalized = dict(data)
    if "name" in update_fields and isinstance(section.get("name"), str):
        normalized_section = dict(section)
        normalized_section["name"] = normalized_section["name"].strip()
        normalized["section"] = normalized_section
    return normalized


def _validate_delete_payload(data: dict) -> None:
    if data:
        raise TaskV2CliError("invalid_section_payload", "`sections delete` 不接受 `--data-json` 请求体。")


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    if action == "list":
        raw = run_api_command(context, "GET", BASE_PATH, params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
        return normalize_list_response(raw, resource="sections", action="list")
    if action == "create":
        return run_api_command(context, "POST", BASE_PATH, params=params_from_args(args), data=_validate_create_payload(data_from_args(args)), dry_run=args.dry_run)

    section_guid = require_arg(getattr(args, "section_guid", None), "--section-guid", f"sections {action}")
    path = f"{BASE_PATH}/{section_guid}"
    if action == "get":
        raw = run_api_command(context, "GET", path, params=params_from_args(args), dry_run=args.dry_run)
        return normalize_single_response(raw, resource="sections", action="get", key="section")
    if action == "patch":
        return run_api_command(context, "PATCH", path, params=params_from_args(args), data=_validate_patch_payload(data_from_args(args)), dry_run=args.dry_run)
    if action == "delete":
        _validate_delete_payload(data_from_args(args))
        return run_api_command(context, "DELETE", path, params=params_from_args(args), dry_run=args.dry_run)
    if action == "tasks":
        raw = run_api_command(context, "GET", f"{path}/tasks", params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
        return normalize_list_response(raw, resource="sections", action="tasks")
    raise TaskV2CliError("unsupported_action", f"`sections {action}` 暂不支持")
