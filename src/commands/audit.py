import click

from commands.common import run_prompt
from lib.prompts import build_audit_prompt


@click.command(name="audit")
@click.argument("repository")
@click.option("--focus", default=None, help="Optional area to focus the audit on.")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
def audit_command(
    repository: str,
    focus: str | None,
    ref: str | None,
    refresh: bool,
) -> None:
    """Run a code audit against the repository."""

    run_prompt(
        repository,
        build_audit_prompt(focus=focus),
        title="Audit",
        ref=ref,
        refresh=refresh,
    )
