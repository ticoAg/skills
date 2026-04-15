from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, urlparse

from common import CliContext, TaskV2CliError, run_task_command


UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


def parse_task_id_from_url(task_url: str) -> str:
    parsed = urlparse(task_url)
    query = parse_qs(parsed.query)
    return (query.get("suite_entity_num", [""])[0] or query.get("task_id", [""])[0]).strip()


def search_tasks(short_id: str, context: CliContext | None = None) -> list[dict]:
    payload = run_task_command(
        context or CliContext(),
        ["+search", "--query", short_id, "--format", "json"],
    )
    return payload.get("data", {}).get("items") or []


def fetch_task(task_guid: str, context: CliContext | None = None) -> dict:
    payload = run_task_command(
        context or CliContext(),
        [
            "tasks",
            "get",
            "--params",
            json.dumps({"task_guid": task_guid}, ensure_ascii=False),
            "--format",
            "json",
        ],
    )
    return payload.get("data", {}).get("task", {}) or payload.get("task", {})


def resolve_task_guid(task_id_or_url: str, context: CliContext | None = None) -> str:
    raw = task_id_or_url.strip()
    if not raw:
        raise TaskV2CliError("task_id_missing", "缺少任务 ID")

    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        guid = parse_qs(parsed.query).get("guid", [""])[0].strip()
        if guid:
            return guid
        short_id = parse_task_id_from_url(raw)
        if short_id:
            return resolve_task_guid(short_id, context)
        raise TaskV2CliError("task_guid_missing", "任务链接里没有 guid、suite_entity_num 或 task_id 参数")

    if UUID_RE.match(raw):
        return raw

    items = search_tasks(raw) if context is None else search_tasks(raw, context)
    if not items:
        raise TaskV2CliError("task_not_found", f"找不到任务：{raw}")
    if len(items) == 1:
        guid = str(items[0].get("guid", "")).strip()
        if guid:
            return guid

    for item in items:
        guid = str(item.get("guid", "")).strip()
        if not guid:
            continue
        task = fetch_task(guid) if context is None else fetch_task(guid, context)
        if str(task.get("task_id", "")).strip() == raw:
            return guid
        if parse_task_id_from_url(str(task.get("url", ""))) == raw:
            return guid

    raise TaskV2CliError("task_id_ambiguous", f"短任务编号 `{raw}` 命中多个任务，无法自动唯一定位。", details={"items": items})
