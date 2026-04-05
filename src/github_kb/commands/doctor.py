import click
from rich.table import Table

from github_kb.commands.common import runtime_options
from github_kb.lib.doctor import run_diagnostics
from github_kb.lib.ui import get_console
from github_kb.settings import resolve_settings


@click.command(name="doctor")
@runtime_options
def doctor_command(
    aws_profile: str | None,
    region: str | None,
    model: str | None,
) -> None:
    """Validate the local runtime, AWS credentials and Bedrock access."""

    console = get_console()
    settings = resolve_settings(
        aws_profile=aws_profile,
        aws_region=region,
        bedrock_model_id=model,
    )
    results = run_diagnostics(settings)

    table = Table(title="github-kb doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    for result in results:
        status = "OK" if result.ok else "FAIL"
        table.add_row(result.name, status, result.message)

    console.print(table)

    if not all(result.ok for result in results):
        raise click.ClickException("One or more doctor checks failed.")
