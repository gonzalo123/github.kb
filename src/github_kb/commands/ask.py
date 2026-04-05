import click

from github_kb.commands.common import join_parts, run_prompt


@click.command(name="ask")
@click.argument("repository")
@click.argument("question", nargs=-1, required=True)
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
def ask_command(
    repository: str,
    question: tuple[str, ...],
    ref: str | None,
    refresh: bool,
) -> None:
    """Ask an open question about a GitHub repository."""

    run_prompt(
        repository,
        join_parts(question),
        title="Answer",
        ref=ref,
        refresh=refresh,
    )
