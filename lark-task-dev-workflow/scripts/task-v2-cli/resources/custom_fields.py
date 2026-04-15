from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, params_from_args, require_arg


BASE_PATH = "/open-apis/task/v2/custom_fields"


def _validate_create_payload(data: dict) -> dict:
    if "custom_field" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_custom_field_payload",
            "`custom-fields create` 需要 Task v2 顶层字段，例如 `resource_type` / `resource_id` / `name` / `type`。",
        )
    missing = [
        field
        for field in ("resource_type", "resource_id", "name", "type")
        if not data.get(field)
    ]
    if missing:
        raise TaskV2CliError("invalid_custom_field_payload", f"`custom-fields create` 缺少必填字段：{', '.join(missing)}。")
    normalized = dict(data)
    if isinstance(normalized["name"], str):
        normalized["name"] = normalized["name"].strip()
    return normalized


def _validate_patch_payload(data: dict) -> dict:
    custom_field = data.get("custom_field")
    update_fields = data.get("update_fields")
    if not isinstance(custom_field, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_custom_field_payload",
            "`custom-fields patch` 需要 `{ \"custom_field\": {...}, \"update_fields\": [...] }`。",
        )
    if "name" in update_fields:
        name = custom_field.get("name")
        if not isinstance(name, str) or not name.strip():
            raise TaskV2CliError("invalid_custom_field_payload", "`custom-fields patch` 更新 `name` 时必须提供非空 `custom_field.name`。")
    normalized = dict(data)
    if "name" in update_fields and isinstance(custom_field.get("name"), str):
        normalized_custom_field = dict(custom_field)
        normalized_custom_field["name"] = normalized_custom_field["name"].strip()
        normalized["custom_field"] = normalized_custom_field
    return normalized


def _validate_create_option_payload(data: dict) -> dict:
    if "option" in data or "update_fields" in data:
        raise TaskV2CliError(
            "invalid_custom_field_payload",
            "`custom-fields create-option` 需要顶层字段，例如 `name` / `color_index` / `is_hidden`。",
        )
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise TaskV2CliError("invalid_custom_field_payload", "`custom-fields create-option` 需要非空字符串 `name`。")
    normalized = dict(data)
    normalized["name"] = name.strip()
    return normalized


def _validate_patch_option_payload(data: dict) -> dict:
    option = data.get("option")
    update_fields = data.get("update_fields")
    if not isinstance(option, dict) or not isinstance(update_fields, list) or not update_fields:
        raise TaskV2CliError(
            "invalid_custom_field_payload",
            "`custom-fields patch-option` 需要 `{ \"option\": {...}, \"update_fields\": [...] }`。",
        )
    if "name" in update_fields:
        name = option.get("name")
        if not isinstance(name, str) or not name.strip():
            raise TaskV2CliError("invalid_custom_field_payload", "`custom-fields patch-option` 更新 `name` 时必须提供非空 `option.name`。")
    normalized = dict(data)
    if "name" in update_fields and isinstance(option.get("name"), str):
        normalized_option = dict(option)
        normalized_option["name"] = normalized_option["name"].strip()
        normalized["option"] = normalized_option
    return normalized


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    if action == "list":
        return run_api_command(context, "GET", BASE_PATH, params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
    if action == "create":
        return run_api_command(context, "POST", BASE_PATH, params=params_from_args(args), data=_validate_create_payload(data_from_args(args)), dry_run=args.dry_run)

    field_guid = require_arg(getattr(args, "custom_field_guid", None), "--custom-field-guid", f"custom-fields {action}")
    path = f"{BASE_PATH}/{field_guid}"
    if action == "get":
        return run_api_command(context, "GET", path, params=params_from_args(args), dry_run=args.dry_run)
    if action == "patch":
        return run_api_command(context, "PATCH", path, params=params_from_args(args), data=_validate_patch_payload(data_from_args(args)), dry_run=args.dry_run)
    if action == "list-options":
        return run_api_command(context, "GET", f"{path}/options", params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
    if action == "create-option":
        return run_api_command(context, "POST", f"{path}/options", params=params_from_args(args), data=_validate_create_option_payload(data_from_args(args)), dry_run=args.dry_run)
    if action == "patch-option":
        option_guid = require_arg(getattr(args, "option_guid", None), "--option-guid", "custom-fields patch-option")
        return run_api_command(context, "PATCH", f"{path}/options/{option_guid}", params=params_from_args(args), data=_validate_patch_option_payload(data_from_args(args)), dry_run=args.dry_run)
    raise TaskV2CliError("unsupported_action", f"`custom-fields {action}` 暂不支持")
