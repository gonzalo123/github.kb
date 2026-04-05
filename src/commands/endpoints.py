import click

from commands.common import run_prompt
from lib.prompts import build_endpoints_prompt


@click.command(name="endpoints")
@click.argument("repository")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
def endpoints_command(
    repository: str,
    ref: str | None,
    refresh: bool,
) -> None:
    """List the API endpoints found in the repository."""

    run_prompt(
        repository,
        build_endpoints_prompt(),
        title="Endpoints",
        ref=ref,
        refresh=refresh,
    )
