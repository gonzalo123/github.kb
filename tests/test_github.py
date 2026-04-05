import pytest

from lib.github import parse_repository


def test_parse_owner_and_repository() -> None:
    repository = parse_repository("openai/openai-python")

    assert repository.owner == "openai"
    assert repository.name == "openai-python"
    assert repository.clone_url == "https://github.com/openai/openai-python.git"
    assert repository.ref is None


def test_parse_github_tree_url_and_ref() -> None:
    repository = parse_repository("https://github.com/pallets/flask/tree/main")

    assert repository.owner == "pallets"
    assert repository.name == "flask"
    assert repository.ref == "main"


def test_reject_non_github_urls() -> None:
    with pytest.raises(ValueError):
        parse_repository("https://gitlab.com/example/project")
