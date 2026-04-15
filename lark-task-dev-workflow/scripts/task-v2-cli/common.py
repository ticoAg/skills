from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any


class TaskV2CliError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"ok": False, "code": self.code, "error": str(self)}
        if self.details:
            payload["details"] = self.details
        return payload


@dataclass(frozen=True)
class CliContext:
    as_identity: str = "auto"
    profile: str | None = None
    output_format: str = "json"
    jq: str | None = None


@dataclass(frozen=True)
class CommandResult:
    payload: dict[str, Any]
    command: list[str]


def parse_json_object(raw: str | None, label: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TaskV2CliError("invalid_json", f"{label} 不是合法 JSON：{exc}") from exc
    if not isinstance(payload, dict):
        raise TaskV2CliError("invalid_json", f"{label} 必须是 JSON object")
    return payload


def merge_json(*objects: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for item in objects:
        if item:
            merged.update(item)
    return merged


def build_base_command(context: CliContext) -> list[str]:
    command = ["lark-cli"]
    if context.profile:
        command.extend(["--profile", context.profile])
    return command


def run_json_command(command: list[str], *, allow_non_json_output: bool = False) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    raw_json = stdout or stderr

    if stdout.startswith("=== Dry Run ==="):
        raw_json = stdout.split("\n", 1)[1].strip() if "\n" in stdout else ""

    if not raw_json:
        if result.returncode != 0:
            raise TaskV2CliError("command_failed", stderr or "lark-cli 命令执行失败")
        return {}

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        if allow_non_json_output and result.returncode == 0:
            return {"raw_output": stdout or stderr}
        raise TaskV2CliError("non_json_output", stdout or stderr or str(exc)) from exc

    if result.returncode != 0:
        raise TaskV2CliError("command_failed", stderr or stdout or "lark-cli 命令执行失败", details={"payload": payload})

    if isinstance(payload, dict) and payload.get("ok") is False:
        error = payload.get("error") or {}
        raise TaskV2CliError(
            "lark_cli_error",
            error.get("message") if isinstance(error, dict) else str(error),
            details=payload,
        )

    if isinstance(payload, dict) and payload.get("code") not in (None, 0):
        raise TaskV2CliError(
            "task_api_error",
            str(payload.get("msg") or f"Task API error: {payload.get('code')}"),
            details=payload,
        )

    if not isinstance(payload, dict):
        return {"data": payload}
    return payload


def run_task_command(context: CliContext, args: list[str]) -> dict[str, Any]:
    command = build_base_command(context)
    command.extend(["task", *args])
    return run_json_command(command)


def run_api_command(
    context: CliContext,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    dry_run: bool = False,
    page_all: bool = False,
    page_limit: int | None = None,
    page_delay: int | None = None,
    output_format: str | None = None,
    jq: str | None = None,
    file_arg: str | None = None,
) -> dict[str, Any]:
    command = build_base_command(context)
    command.extend(["api", method.upper(), path, "--as", context.as_identity or "auto"])
    if params:
        command.extend(["--params", json.dumps(params, ensure_ascii=False)])
    if data is not None:
        command.extend(["--data", json.dumps(data, ensure_ascii=False)])
    if file_arg:
        command.extend(["--file", file_arg])
    if dry_run:
        command.append("--dry-run")
    if page_all:
        command.append("--page-all")
        if page_limit is not None:
            command.extend(["--page-limit", str(page_limit)])
        if page_delay is not None:
            command.extend(["--page-delay", str(page_delay)])
    if output_format:
        command.extend(["--format", output_format])
    if jq:
        command.extend(["--jq", jq])
    return run_json_command(command, allow_non_json_output=dry_run)


def require_write_confirmation(action: str, *, yes: bool, dry_run: bool) -> None:
    if yes or dry_run:
        return
    raise TaskV2CliError(
        "write_confirmation_required",
        f"`{action}` 是写操作；请显式传 `--yes` 执行，或传 `--dry-run` 预览。",
    )


def print_payload(payload: dict[str, Any], output_format: str, jq: str | None) -> None:
    if output_format != "json":
        print(json.dumps({"ok": True, "format": output_format, "data": payload}, ensure_ascii=False, indent=2))
        return
    if jq:
        print(json.dumps({"ok": True, "jq": jq, "data": payload}, ensure_ascii=False, indent=2))
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))
