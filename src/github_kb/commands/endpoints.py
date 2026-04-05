import click

from github_kb.commands.common import run_prompt, runtime_options
from github_kb.lib.prompts import build_endpoints_prompt


@click.command(name="endpoints")
@click.argument("repository")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
@runtime_options
def endpoints_command(
    repository: str,
    ref: str | None,
    refresh: bool,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """List the API endpoints found in the repository."""

    run_prompt(
        repository,
        build_endpoints_prompt(),
        title="Endpoints",
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
