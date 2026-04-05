from pathlib import Path
import subprocess
from urllib.parse import urlparse

from github_kb.lib.models import GitHubRepositoryReference, RepositoryContext
from github_kb.settings import Settings

VALID_GITHUB_HOSTS = {"github.com", "www.github.com"}


def parse_repository(value: str, ref: str | None = None) -> GitHubRepositoryReference:
    raw_value = value.strip()
    if not raw_value:
        raise ValueError("Repository cannot be empty.")

    detected_ref: str | None = None

    if raw_value.startswith("http://") or raw_value.startswith("https://"):
        parsed = urlparse(raw_value)
        if parsed.netloc not in VALID_GITHUB_HOSTS:
            raise ValueError("Only github.com repositories are supported in this PoC.")

        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError("Repository must include owner and name.")

        owner = parts[0]
        name = parts[1].removesuffix(".git")

        if len(parts) >= 4 and parts[2] == "tree":
            detected_ref = parts[3]
    else:
        parts = [part for part in raw_value.split("/") if part]
        if len(parts) != 2:
            raise ValueError("Repository must look like owner/name or a GitHub URL.")

        owner = parts[0]
        name = parts[1].removesuffix(".git")

    return GitHubRepositoryReference(
        owner=owner,
        name=name,
        clone_url=f"https://github.com/{owner}/{name}.git",
        html_url=f"https://github.com/{owner}/{name}",
        ref=ref or detected_ref,
    )


def ensure_repository(
    repository: GitHubRepositoryReference,
    *,
    settings: Settings,
    refresh: bool = False,
) -> RepositoryContext:
    cache_path = settings.repo_cache_path / repository.cache_key
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if not cache_path.exists():
        _run_git(
            settings,
            ["clone", "--depth", "1", repository.clone_url, str(cache_path)],
        )
        _checkout_ref(cache_path, repository.ref, settings)
    elif refresh:
        _refresh_repository(cache_path, repository.ref, settings)

    return RepositoryContext(repository=repository, local_path=cache_path)


def _refresh_repository(path: Path, ref: str | None, settings: Settings) -> None:
    if ref:
        _run_git(settings, ["fetch", "--depth", "1", "origin", ref], cwd=path)
        _run_git(settings, ["checkout", "--detach", "FETCH_HEAD"], cwd=path)
        return

    current_branch = _run_git(
        settings,
        ["rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
    ).strip()
    if current_branch == "HEAD":
        current_branch = _run_git(
            settings,
            ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            cwd=path,
        ).removeprefix("origin/")
    _run_git(settings, ["checkout", current_branch], cwd=path)
    _run_git(settings, ["pull", "--ff-only", "origin", current_branch], cwd=path)


def _checkout_ref(path: Path, ref: str | None, settings: Settings) -> None:
    if not ref:
        return

    _run_git(settings, ["fetch", "--depth", "1", "origin", ref], cwd=path)
    _run_git(settings, ["checkout", "--detach", "FETCH_HEAD"], cwd=path)


def _run_git(settings: Settings, args: list[str], cwd: Path | None = None) -> str:
    command = [settings.git_binary, *args]
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Unknown git error"
        raise RuntimeError(message)
    return completed.stdout.strip()
