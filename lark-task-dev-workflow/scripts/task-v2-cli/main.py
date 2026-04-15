#!/usr/bin/env python3

from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Annotated, Any

try:
    import typer
except ModuleNotFoundError as exc:  # pragma: no cover - import-time guard
    raise SystemExit(
        "Missing dependency `typer`. Install with: python3 -m pip install --user --break-system-packages 'typer>=0.12,<1'"
    ) from exc

from common import CliContext, TaskV2CliError, print_payload, require_write_confirmation


app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False,
    help="Task v2 wrapper powered by lark-cli auth",
)

RESOURCES = {
    "tasks": "resources.tasks",
    "tasklists": "resources.tasklists",
    "comments": "resources.comments",
    "sections": "resources.sections",
    "custom-fields": "resources.custom_fields",
    "attachments": "resources.attachments",
    "subtasks": "resources.subtasks",
}

WRITE_ACTIONS = {
    "create",
    "patch",
    "delete",
    "upload",
    "add-members",
    "remove-members",
    "remove-tasklist",
    "create-option",
    "patch-option",
}

ACTIONS = [
    "get",
    "list",
    "create",
    "patch",
    "delete",
    "tasks",
    "tasklists",
    "add-members",
    "remove-members",
    "remove-tasklist",
    "list-options",
    "create-option",
    "patch-option",
    "upload",
]


def context_from_namespace(args: SimpleNamespace) -> CliContext:
    return CliContext(
        as_identity=args.as_identity,
        profile=args.profile,
        output_format=args.output_format,
        jq=args.jq,
    )


def dispatch(context: CliContext, resource: str, action: str, args: SimpleNamespace) -> dict[str, Any]:
    module_name = RESOURCES.get(resource)
    if not module_name:
        raise TaskV2CliError("unsupported_resource", f"不支持的资源：{resource}")
    module = importlib.import_module(module_name)
    return module.handle(context, action, args)


def _execute(resource: str, action: str, **kwargs: Any) -> None:
    args = SimpleNamespace(**kwargs)
    try:
        if action in WRITE_ACTIONS:
            require_write_confirmation(action, yes=args.yes, dry_run=args.dry_run)
        context = context_from_namespace(args)
        payload = dispatch(context, resource, action, args)
    except TaskV2CliError as error:
        print_payload(error.to_payload(), "json", None)
        raise typer.Exit(code=2) from error
    print_payload(payload, args.output_format, args.jq)


def _make_command(resource: str, action: str):
    def command(
        as_identity: Annotated[str, typer.Option("--as")] = "auto",
        profile: Annotated[str | None, typer.Option("--profile")] = None,
        output_format: Annotated[str, typer.Option("--format")] = "json",
        jq: Annotated[str | None, typer.Option("--jq")] = None,
        page_size: Annotated[int, typer.Option("--page-size")] = 0,
        page_token: Annotated[str | None, typer.Option("--page-token")] = None,
        page_all: Annotated[bool, typer.Option("--page-all")] = False,
        page_limit: Annotated[int, typer.Option("--page-limit")] = 10,
        page_delay: Annotated[int, typer.Option("--page-delay")] = 200,
        dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
        yes: Annotated[bool, typer.Option("--yes")] = False,
        params_json: Annotated[str | None, typer.Option("--params-json")] = None,
        data_json: Annotated[str | None, typer.Option("--data-json")] = None,
        task_id: Annotated[str | None, typer.Option("--task-id")] = None,
        tasklist_guid: Annotated[str | None, typer.Option("--tasklist-guid")] = None,
        comment_id: Annotated[str | None, typer.Option("--comment-id")] = None,
        section_guid: Annotated[str | None, typer.Option("--section-guid")] = None,
        custom_field_guid: Annotated[str | None, typer.Option("--custom-field-guid")] = None,
        option_guid: Annotated[str | None, typer.Option("--option-guid")] = None,
        attachment_guid: Annotated[str | None, typer.Option("--attachment-guid")] = None,
        file: Annotated[str | None, typer.Option("--file")] = None,
    ) -> None:
        _execute(
            resource,
            action,
            as_identity=as_identity,
            profile=profile,
            output_format=output_format,
            jq=jq,
            page_size=page_size,
            page_token=page_token,
            page_all=page_all,
            page_limit=page_limit,
            page_delay=page_delay,
            dry_run=dry_run,
            yes=yes,
            params_json=params_json,
            data_json=data_json,
            task_id=task_id,
            tasklist_guid=tasklist_guid,
            comment_id=comment_id,
            section_guid=section_guid,
            custom_field_guid=custom_field_guid,
            option_guid=option_guid,
            attachment_guid=attachment_guid,
            file=file,
        )

    command.__name__ = f"{resource.replace('-', '_')}_{action.replace('-', '_')}"
    return command


for resource in RESOURCES:
    resource_app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
    for action in ACTIONS:
        resource_app.command(name=action)(_make_command(resource, action))
    app.add_typer(resource_app, name=resource)


def main(argv: list[str] | None = None) -> None:
    app(args=argv, prog_name="task-v2-cli", standalone_mode=False)


if __name__ == "__main__":
    try:
        main()
    except typer.Exit as exc:
        raise SystemExit(exc.exit_code) from exc
