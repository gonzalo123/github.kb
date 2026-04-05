from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from github_kb.lib.models import RepositoryContext

console = Console()


def get_console() -> Console:
    return console


def print_repository_panel(repository_context: RepositoryContext) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("Repository", repository_context.repository.slug)
    table.add_row("Local path", str(repository_context.local_path))
    table.add_row("Ref", repository_context.repository.ref or "default branch")
    console.print(Panel(table, title="Repository", expand=False))


def print_result(title: str, result: str) -> None:
    console.print(Panel(Markdown(result), title=title))
