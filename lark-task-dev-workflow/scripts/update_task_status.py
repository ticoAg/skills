#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from task_status_common import (
    DEFAULT_STATES,
    TaskStatusError,
    ensure_status_field_context,
    resolve_status_option_guid,
    run_lark_cli_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="任务 guid、短任务号或完整 applink")
    parser.add_argument("--label", required=True, help="目标状态标签")
    parser.add_argument("--dry-run", action="store_true", help="只打印请求，不真正执行")
    args = parser.parse_args()

    label = args.label.strip()
    if label not in DEFAULT_STATES:
        raise TaskStatusError("invalid_label", f"不支持的研发状态：{label}")

    context = ensure_status_field_context(args.task_id)
    field_guid = str(context.field.get("guid", "")).strip()
    if not field_guid:
        raise TaskStatusError("field_guid_missing", "研发状态字段缺少 GUID。")

    option_guid = resolve_status_option_guid(context.field, label)
    payload = {
        "task": {
            "custom_fields": [
                {
                    "guid": field_guid,
                    "type": "single_select",
                    "single_select_value": option_guid,
                }
            ]
        },
        "update_fields": ["custom_fields"],
    }
    command = [
        "task",
        "tasks",
        "patch",
        "--params",
        json.dumps({"task_guid": context.task_guid}, ensure_ascii=False),
        "--data",
        json.dumps(payload, ensure_ascii=False),
        "--format",
        "json",
    ]
    if args.dry_run:
        command.append("--dry-run")

    result = run_lark_cli_json(command, allow_non_json_output=args.dry_run)
    output = {
        "ok": True,
        "task_guid": context.task_guid,
        "tasklist_guid": context.tasklist_guid,
        "field_guid": field_guid,
        "label": label,
        "option_guid": option_guid,
        "dry_run": args.dry_run,
        "response": result,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        payload = {"ok": False, "error": str(exc)}
        if hasattr(exc, "code"):
            payload["code"] = getattr(exc, "code")
        if hasattr(exc, "details") and getattr(exc, "details"):
            payload["details"] = getattr(exc, "details")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        raise SystemExit(1)
