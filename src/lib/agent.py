from strands import Agent, tool
from strands.models import BedrockModel

from lib.prompts import SYSTEM_PROMPT
from lib.repository import RepositoryExplorer
from settings import Settings


def create_agent(explorer: RepositoryExplorer, *, settings: Settings) -> Agent:
    return Agent(
        model=BedrockModel(
            model_id=settings.bedrock_model_id,
            region_name=settings.aws_region,
        ),
        tools=create_tools(explorer),
        system_prompt=SYSTEM_PROMPT,
    )


def create_tools(explorer: RepositoryExplorer) -> list:
    @tool
    def get_directory_tree(path: str = ".", max_depth: int = 4) -> str:
        """Return a tree view for a directory inside the repository."""

        return explorer.get_directory_tree(path=path, max_depth=max_depth)

    @tool
    def list_directory(path: str = ".") -> str:
        """List the files and directories inside a repository path."""

        return explorer.list_directory(path=path)

    @tool
    def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> str:
        """Read a text file from the repository with line numbers."""

        return explorer.read_file(
            path=path,
            start_line=start_line,
            end_line=end_line,
        )

    @tool
    def search_code(
        query: str,
        glob_pattern: str | None = None,
        max_results: int = 20,
    ) -> str:
        """Search for text in repository files."""

        return explorer.search_code(
            query=query,
            glob_pattern=glob_pattern,
            max_results=max_results,
        )

    return [get_directory_tree, list_directory, read_file, search_code]
