from collections.abc import Sequence
from functools import wraps

import click
from strands import Agent

from github_kb.lib.agent import create_agent
from github_kb.lib.github import ensure_repository, parse_repository
from github_kb.lib.models import RepositoryContext
from github_kb.lib.repository import RepositoryExplorer
from github_kb.lib.ui import get_console, print_repository_panel, print_result
from github_kb.settings import resolve_settings


def runtime_options(function):
    @click.option(
        "--aws-profile",
        default=None,
        help="AWS profile name to use. Falls back to AWS_PROFILE if unset.",
    )
    @click.option(
        "--region",
        default=None,
        help="AWS region for Bedrock. Falls back to AWS_REGION if unset.",
    )
    @click.option(
        "--model",
        default=None,
        help="Bedrock model id. Falls back to BEDROCK_MODEL_ID if unset.",
    )
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


def join_parts(parts: Sequence[str]) -> str:
    return " ".join(part for part in parts if part).strip()


def run_prompt(
    repository: str,
    prompt: str,
    *,
    title: str,
    ref: str | None = None,
    refresh: bool = False,
    aws_profile: str | None = None,
    region: str | None = None,
    model: str | None = None,
) -> None:
    repository_context, agent = prepare_agent(
        repository,
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
    print_repository_panel(repository_context)

    console = get_console()
    try:
        with console.status("Thinking with Bedrock...", spinner="dots"):
            result = agent(prompt)
    except Exception as error:
        raise click.ClickException(str(error)) from error

    print_result(title, str(result))


def prepare_agent(
    repository: str,
    *,
    ref: str | None = None,
    refresh: bool = False,
    aws_profile: str | None = None,
    region: str | None = None,
    model: str | None = None,
) -> tuple[RepositoryContext, Agent]:
    settings = resolve_settings(
        aws_profile=aws_profile,
        aws_region=region,
        bedrock_model_id=model,
    )
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
            agent = create_agent(explorer, settings=settings)
    except Exception as error:
        raise click.ClickException(str(error)) from error

    return repository_context, agent
