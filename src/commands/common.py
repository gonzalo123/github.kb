from collections.abc import Sequence

import click

from lib.agent import create_agent
from lib.github import ensure_repository, parse_repository
from lib.repository import RepositoryExplorer
from lib.ui import get_console, print_repository_panel, print_result
from settings import get_settings


def join_parts(parts: Sequence[str]) -> str:
    return " ".join(part for part in parts if part).strip()


def run_prompt(
    repository: str,
    prompt: str,
    *,
    title: str,
    ref: str | None = None,
    refresh: bool = False,
) -> None:
    settings = get_settings()
    console = get_console()

    try:
        repo_reference = parse_repository(repository, ref=ref)
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    try:
        with console.status(f"Preparing {repo_reference.slug}...", spinner="dots"):
            repository_context = ensure_repository(
                repo_reference,
                settings=settings,
                refresh=refresh,
            )
            explorer = RepositoryExplorer(
                root_path=repository_context.local_path,
                settings=settings,
            )

        print_repository_panel(repository_context)

        with console.status("Thinking with Bedrock...", spinner="dots"):
            agent = create_agent(explorer, settings=settings)
            result = agent(prompt)
    except Exception as error:
        raise click.ClickException(str(error)) from error

    print_result(title, str(result))
