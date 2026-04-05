from pathlib import Path

from pydantic import BaseModel, ConfigDict


class GitHubRepositoryReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    owner: str
    name: str
    clone_url: str
    html_url: str
    ref: str | None = None

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.name}"

    @property
    def cache_key(self) -> str:
        if not self.ref:
            return f"{self.owner}__{self.name}"

        sanitized_ref = self.ref.replace("/", "__")
        return f"{self.owner}__{self.name}__{sanitized_ref}"


class RepositoryContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    repository: GitHubRepositoryReference
    local_path: Path
