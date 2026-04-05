import click

from github_kb.commands.common import prepare_agent
from github_kb.lib.ui import get_console, print_repository_panel, print_result

EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", ":q", "q"}


def is_exit_command(value: str) -> bool:
    return value.strip().lower() in EXIT_COMMANDS


@click.command(name="chat")
@click.argument("repository")
@click.option("--ref", default=None, help="Git branch, tag or commit to inspect.")
@click.option("--refresh", is_flag=True, help="Refresh the cached local checkout.")
def chat_command(
    repository: str,
    ref: str | None,
    refresh: bool,
) -> None:
    """Start a conversational session about a GitHub repository."""

    console = get_console()
    repository_context, agent = prepare_agent(
        repository,
        ref=ref,
        refresh=refresh,
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
