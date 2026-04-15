#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


DEFAULT_STATES = ["待开始", "开发中", "待测试", "修复中", "已完成"]
DEFAULT_FIELD_NAME = "研发状态"
DEFAULT_FIELD_TYPE = "single_select"
STATUS_OPTION_COLORS = {
    "待开始": 16,
    "开发中": 6,
    "待测试": 11,
    "修复中": 4,
    "已完成": 20,
}
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


class TaskStatusError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


class PermissionDeniedError(TaskStatusError):
    def __init__(self, message: str, *, scopes: list[str] | None = None, details: dict | None = None) -> None:
        merged = {"scopes": scopes or []}
        if details:
            merged.update(details)
        super().__init__("permission_denied", message, details=merged)


@dataclass
class StatusFieldContext:
    task_guid: str
    task: dict
    tasklist_guid: str
    field: dict


def run_json_command(args: list[str], *, allow_non_json_output: bool = False) -> dict:
    command = ["lark-cli", *args]
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    raw_json = stdout or stderr
    if stdout.startswith("=== Dry Run ==="):
        raw_json = stdout.split("\n", 1)[1].strip() if "\n" in stdout else ""
    if not raw_json:
        if result.returncode != 0:
            detail = stderr or "未知错误"
            raise RuntimeError(detail)
        return {}

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError:
        if allow_non_json_output and result.returncode == 0:
            return {"raw_output": stdout or stderr}
        if result.returncode != 0:
            detail = stderr or stdout or "未知错误"
            raise RuntimeError(detail)
        raise

    if isinstance(payload, dict) and payload.get("ok") is False:
        error = payload.get("error") or {}
        if error.get("type") == "permission":
            scopes: list[str] = []
            for violation in error.get("detail", {}).get("permission_violations", []):
                subject = str(violation.get("subject", "")).strip()
                if subject:
                    scopes.append(subject)
            raise PermissionDeniedError(
                error.get("message") or "权限不足",
                scopes=scopes,
                details=error.get("detail") or {},
            )
        raise RuntimeError(error.get("message") or "未知错误")
    if result.returncode != 0:
        detail = stderr or stdout or "未知错误"
        raise RuntimeError(detail)
    if isinstance(payload, dict) and payload.get("code") not in (None, 0):
        raise RuntimeError(payload.get("msg") or f"接口错误: {payload.get('code')}")
    return payload


def run_lark_cli_json(args: list[str], *, allow_non_json_output: bool = False) -> dict:
    return run_json_command(args, allow_non_json_output=allow_non_json_output)


def run_lark_api_json(method: str, path: str, *, params: dict | None = None, data: dict | None = None) -> dict:
    command = ["api", method.upper(), path]
    if params is not None:
        command.extend(["--params", json.dumps(params, ensure_ascii=False)])
    if data is not None:
        command.extend(["--data", json.dumps(data, ensure_ascii=False)])
    return run_json_command(command)


def search_tasks(query: str) -> list[dict]:
    payload = run_lark_cli_json(["task", "+search", "--query", query, "--format", "json"])
    return payload.get("data", {}).get("items") or []


def parse_task_id_from_url(task_url: str) -> str:
    parsed = urlparse(task_url)
    query = parse_qs(parsed.query)
    return (query.get("suite_entity_num", [""])[0] or query.get("task_id", [""])[0]).strip()


def resolve_task_guid_by_search(short_id: str) -> str:
    items = search_tasks(short_id)
    if not items:
        raise TaskStatusError("task_not_found", f"找不到任务：{short_id}")

    if len(items) == 1:
        return str(items[0].get("guid", "")).strip()

    for item in items:
        guid = str(item.get("guid", "")).strip()
        if not guid:
            continue
        task = fetch_task(guid)
        if str(task.get("task_id", "")).strip() == short_id:
            return guid
        if parse_task_id_from_url(str(task.get("url", ""))) == short_id:
            return guid

    raise TaskStatusError(
        "task_id_ambiguous",
        f"短任务编号 `{short_id}` 命中了多个任务，无法自动唯一定位。",
        details={"candidates": items},
    )


def extract_task_guid(task_id_or_url: str) -> str:
    raw = task_id_or_url.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        guid = parse_qs(parsed.query).get("guid", [""])[0].strip()
        if guid:
            return guid
        short_id = parse_task_id_from_url(raw)
        if short_id:
            return resolve_task_guid_by_search(short_id)
        raise ValueError("任务链接里没有 guid 参数")
    if UUID_RE.match(raw):
        return raw
    return resolve_task_guid_by_search(raw)


def fetch_task(task_guid: str) -> dict:
    payload = run_lark_cli_json(
        [
            "task",
            "tasks",
            "get",
            "--params",
            json.dumps({"task_guid": task_guid}, ensure_ascii=False),
            "--format",
            "json",
        ]
    )
    return payload.get("data", {}).get("task", {}) or payload.get("task", {})


def get_primary_tasklist_guid(task: dict) -> str:
    tasklists = task.get("tasklists") or []
    if not tasklists:
        raise TaskStatusError("tasklist_missing", "任务当前不在任何清单中，无法使用 `研发状态` 工作流。")
    tasklist_guid = str(tasklists[0].get("tasklist_guid", "")).strip()
    if not tasklist_guid:
        raise TaskStatusError("tasklist_missing", "任务所在清单缺少有效的 tasklist_guid。")
    return tasklist_guid


def list_custom_fields(tasklist_guid: str) -> list[dict]:
    payload = run_lark_api_json(
        "GET",
        "/open-apis/task/v2/custom_fields",
        params={"resource_type": "tasklist", "resource_id": tasklist_guid},
    )
    return payload.get("data", {}).get("items") or []


def get_custom_field(custom_field_guid: str) -> dict:
    payload = run_lark_api_json("GET", f"/open-apis/task/v2/custom_fields/{custom_field_guid}")
    return payload.get("data", {}).get("custom_field") or {}


def find_named_fields(fields: list[dict], field_name: str) -> list[dict]:
    return [field for field in fields if field.get("name") == field_name]


def get_single_select_options(field: dict) -> list[dict]:
    return field.get("single_select_setting", {}).get("options") or []


def find_option_by_name(field: dict, label: str) -> dict | None:
    hidden_match: dict | None = None
    for option in get_single_select_options(field):
        if option.get("name") == label:
            if not option.get("is_hidden"):
                return option
            hidden_match = option
    return hidden_match


def create_status_field(tasklist_guid: str) -> dict:
    payload = run_lark_api_json(
        "POST",
        "/open-apis/task/v2/custom_fields",
        data={
            "resource_type": "tasklist",
            "resource_id": tasklist_guid,
            "name": DEFAULT_FIELD_NAME,
            "type": DEFAULT_FIELD_TYPE,
            "single_select_setting": {
                "options": [
                    {"name": label, "color_index": STATUS_OPTION_COLORS.get(label, 0)}
                    for label in DEFAULT_STATES
                ]
            },
        },
    )
    return payload.get("data", {}).get("custom_field") or {}


def create_status_option(field_guid: str, label: str) -> dict:
    payload = run_lark_api_json(
        "POST",
        f"/open-apis/task/v2/custom_fields/{field_guid}/options",
        data={"name": label, "color_index": STATUS_OPTION_COLORS.get(label, 0), "is_hidden": False},
    )
    return payload.get("data", {}).get("option") or {}


def unhide_status_option(field_guid: str, option_guid: str) -> dict:
    payload = run_lark_api_json(
        "PATCH",
        f"/open-apis/task/v2/custom_fields/{field_guid}/options/{option_guid}",
        data={"option": {"is_hidden": False}, "update_fields": ["is_hidden"]},
    )
    return payload.get("data", {}).get("option") or {}


def ensure_status_field(tasklist_guid: str) -> dict:
    fields = list_custom_fields(tasklist_guid)
    matches = find_named_fields(fields, DEFAULT_FIELD_NAME)
    if len(matches) > 1:
        raise TaskStatusError(
            "duplicate_fields",
            f"清单中存在多个同名字段 `{DEFAULT_FIELD_NAME}`，无法自动选择。",
        )

    if not matches:
        return create_status_field(tasklist_guid)

    field = matches[0]
    if field.get("type") != DEFAULT_FIELD_TYPE:
        raise TaskStatusError(
            "wrong_field_type",
            f"字段 `{DEFAULT_FIELD_NAME}` 已存在，但类型不是 `{DEFAULT_FIELD_TYPE}`。",
            details={"field_guid": field.get("guid", ""), "actual_type": field.get("type", "")},
        )

    field_guid = str(field.get("guid", "")).strip()
    if not field_guid:
        raise TaskStatusError("field_guid_missing", f"字段 `{DEFAULT_FIELD_NAME}` 缺少 GUID。")

    for label in DEFAULT_STATES:
        option = find_option_by_name(field, label)
        if not option:
            create_status_option(field_guid, label)
            continue
        if option.get("is_hidden"):
            option_guid = str(option.get("guid", "")).strip()
            if not option_guid:
                raise TaskStatusError(
                    "option_guid_missing",
                    f"字段 `{DEFAULT_FIELD_NAME}` 的选项 `{label}` 缺少 GUID。",
                )
            unhide_status_option(field_guid, option_guid)

    return get_custom_field(field_guid)


def ensure_status_field_context(task_id_or_url: str) -> StatusFieldContext:
    task_guid = extract_task_guid(task_id_or_url)
    task = fetch_task(task_guid)
    tasklist_guid = get_primary_tasklist_guid(task)
    field = ensure_status_field(tasklist_guid)
    return StatusFieldContext(task_guid=task_guid, task=task, tasklist_guid=tasklist_guid, field=field)


def resolve_status_option_guid(field: dict, label: str) -> str:
    option = find_option_by_name(field, label)
    if not option:
        raise TaskStatusError("option_missing", f"字段 `{DEFAULT_FIELD_NAME}` 中不存在状态 `{label}`。")
    if option.get("is_hidden"):
        raise TaskStatusError("option_hidden", f"字段 `{DEFAULT_FIELD_NAME}` 的状态 `{label}` 仍处于隐藏状态。")
    option_guid = str(option.get("guid", "")).strip()
    if not option_guid:
        raise TaskStatusError("option_guid_missing", f"状态 `{label}` 缺少 option GUID。")
    return option_guid
