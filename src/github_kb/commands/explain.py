import click

from github_kb.commands.common import run_prompt, runtime_options
from github_kb.lib.prompts import build_explain_prompt


@click.command(name="explain")
@click.argument("repository")
@click.option("--topic", default=None, help="Specific topic, module or flow to explain.")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
@runtime_options
def explain_command(
    repository: str,
    topic: str | None,
    ref: str | None,
    refresh: bool,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """Explain how the repository works."""

    run_prompt(
        repository,
        build_explain_prompt(topic=topic),
        title="Explanation",
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
