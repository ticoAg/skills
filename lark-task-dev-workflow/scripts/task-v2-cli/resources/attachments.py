from __future__ import annotations

from argparse import Namespace

from common import CliContext, TaskV2CliError, run_api_command
from resources._helpers import data_from_args, params_from_args, require_arg, task_guid_from_args


def _validate_upload_payload(args: Namespace) -> dict | None:
    file_arg = getattr(args, "file", None)
    if not file_arg:
        raise TaskV2CliError("invalid_attachment_payload", "`attachments upload` 需要 `--file`。")
    return data_from_args(args) or None


def _validate_delete_payload(args: Namespace) -> None:
    if data_from_args(args):
        raise TaskV2CliError("invalid_attachment_payload", "`attachments delete` 不接受 `--data-json` 请求体。")


def handle(context: CliContext, action: str, args: Namespace) -> dict:
    task_guid = task_guid_from_args(context, args, f"attachments {action}")
    base_path = f"/open-apis/task/v2/tasks/{task_guid}/attachments"
    if action == "list":
        return run_api_command(context, "GET", base_path, params=params_from_args(args), page_all=args.page_all, page_limit=args.page_limit, page_delay=args.page_delay, dry_run=args.dry_run)
    if action == "upload":
        return run_api_command(
            context,
            "POST",
            base_path,
            params=params_from_args(args),
            data=_validate_upload_payload(args),
            file_arg=getattr(args, "file", None),
            dry_run=args.dry_run,
        )

    attachment_guid = require_arg(getattr(args, "attachment_guid", None), "--attachment-guid", f"attachments {action}")
    path = f"{base_path}/{attachment_guid}"
    if action == "get":
        return run_api_command(context, "GET", path, params=params_from_args(args), dry_run=args.dry_run)
    if action == "delete":
        _validate_delete_payload(args)
        return run_api_command(context, "DELETE", path, params=params_from_args(args), dry_run=args.dry_run)
    raise TaskV2CliError("unsupported_action", f"`attachments {action}` 暂不支持")
