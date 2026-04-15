#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shlex
from pathlib import Path

from task_status_common import (
    DEFAULT_FIELD_NAME,
    DEFAULT_FIELD_TYPE,
    DEFAULT_STATES,
    PermissionDeniedError,
    TaskStatusError,
    ensure_status_field_context,
)


def render_markdown_failure(error: TaskStatusError, task_id: str) -> str:
    lines = ["# 研发状态预检未通过", ""]
    retry_command = f"python3 {shlex.quote(str(Path(__file__).resolve()))} --task-id {shlex.quote(task_id)}"

    if error.code == "permission_denied":
        scopes = error.details.get("scopes") or []
        lines.append("当前环境无法读取或修复任务自定义字段，暂时不能自动初始化 `研发状态`。")
        lines.append("")
        lines.append("## 缺少的权限")
        lines.append("")
        for scope in scopes:
            lines.append(f"- `{scope}`")
        if not scopes:
            lines.append("- 请检查 `lark-cli` 当前身份的任务自定义字段权限")
        lines.append("")
        lines.append("## 修正方式")
        lines.append("")
        lines.append("- 先用 `lark-cli auth login` 重新授权，确保当前身份拥有任务自定义字段相关 scope")
        lines.append("- 至少需要能读取自定义字段；若要自动创建/补齐字段，还需要写权限")
        lines.append(f"- 权限修复后，重新运行 `{retry_command}`")
        return "\n".join(lines)

    lines.append(f"- 错误：{error}")
    lines.append("")
    if error.code == "wrong_field_type":
        lines.append("## 修正方式")
        lines.append("")
        lines.append(f"- 将现有 `{DEFAULT_FIELD_NAME}` 字段改为或替换成类型为 `{DEFAULT_FIELD_TYPE}` 的字段")
    elif error.code == "duplicate_fields":
        lines.append("## 修正方式")
        lines.append("")
        lines.append(f"- 清理清单中重复的 `{DEFAULT_FIELD_NAME}` 字段，只保留一个")
    elif error.code == "tasklist_missing":
        lines.append("## 修正方式")
        lines.append("")
        lines.append("- 先把任务加入一个飞书任务清单，再重新运行预检")
    elif error.code in {"task_not_found", "task_id_ambiguous"}:
        lines.append("## 修正方式")
        lines.append("")
        lines.append("- 传入真实任务 GUID、任务 applink，或能唯一命中的短任务编号")
    else:
        lines.append("## 修正方式")
        lines.append("")
        lines.append("- 先排查任务 ID、当前登录身份和清单字段配置是否正确")

    lines.append("")
    lines.append("## 目标状态")
    lines.append("")
    for label in DEFAULT_STATES:
        lines.append(f"- `{label}`")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="任务 guid、短任务号或完整 applink")
    args = parser.parse_args()

    try:
        context = ensure_status_field_context(args.task_id)
    except PermissionDeniedError as error:
        print(render_markdown_failure(error, args.task_id))
        return 2
    except TaskStatusError as error:
        print(render_markdown_failure(error, args.task_id))
        return 2

    _ = context
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("# 任务状态预检失败")
        print("")
        print(f"- 错误：{exc}")
        print("- 先排查 `lark-cli` 授权、任务 GUID 和相关 API 权限是否正确")
        raise SystemExit(1)
