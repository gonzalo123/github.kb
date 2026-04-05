import click

from github_kb.commands.common import join_parts, run_prompt, runtime_options


@click.command(name="ask")
@click.argument("repository")
@click.argument("question", nargs=-1, required=True)
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
@runtime_options
def ask_command(
    repository: str,
    question: tuple[str, ...],
    ref: str | None,
    refresh: bool,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """Ask an open question about a GitHub repository."""

    run_prompt(
        repository,
        join_parts(question),
        title="Answer",
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
