import click

from github_kb.commands.common import run_prompt, runtime_options
from github_kb.lib.prompts import build_audit_prompt


@click.command(name="audit")
@click.argument("repository")
@click.option("--focus", default=None, help="Optional area to focus the audit on.")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
@runtime_options
def audit_command(
    repository: str,
    focus: str | None,
    ref: str | None,
    refresh: bool,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """Run a code audit against the repository."""

    run_prompt(
        repository,
        build_audit_prompt(focus=focus),
        title="Audit",
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
