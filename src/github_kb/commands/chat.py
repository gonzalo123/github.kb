import click

from github_kb.commands.common import prepare_agent, runtime_options
from github_kb.lib.ui import get_console, print_repository_panel, print_result

EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", ":q", "q"}


def is_exit_command(value: str) -> bool:
    return value.strip().lower() in EXIT_COMMANDS


@click.command(name="chat")
@click.argument("repository")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
@runtime_options
def chat_command(
    repository: str,
    ref: str | None,
    refresh: bool,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """Start a conversational session about a GitHub repository."""

    console = get_console()
    repository_context, agent = prepare_agent(
        repository,
        ref=ref,
        refresh=refresh,
        aws_profile=aws_profile,
        region=region,
        model=model,
    )
    print_repository_panel(repository_context)
    console.print("Interactive mode. Type your question or `/exit` to finish.\n")

    while True:
        try:
            question = console.input("[bold cyan]> [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nSession closed.")
            break

        if not question:
            continue

        if is_exit_command(question):
            console.print("Session closed.")
            break

        try:
            with console.status("Thinking with Bedrock...", spinner="dots"):
                result = agent(question)
        except Exception as error:
            raise click.ClickException(str(error)) from error

        print_result("Answer", str(result))
