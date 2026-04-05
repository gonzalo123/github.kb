import click

from commands.ask import ask_command
from commands.audit import audit_command
from commands.endpoints import endpoints_command
from commands.explain import explain_command


@click.group()
def cli() -> None:
    """Ask questions about a GitHub repository using Strands Agents and AWS Bedrock."""


cli.add_command(ask_command)
cli.add_command(audit_command)
cli.add_command(endpoints_command)
cli.add_command(explain_command)


if __name__ == "__main__":
    cli()
