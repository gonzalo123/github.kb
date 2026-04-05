from pathlib import Path

from github_kb.lib.repository import RepositoryExplorer
from github_kb.settings import Settings


def build_explorer(tmp_path: Path) -> RepositoryExplorer:
    return RepositoryExplorer(
        root_path=tmp_path,
        settings=Settings(
            repo_cache_path=tmp_path / ".cache",
            tree_max_entries=25,
            file_read_max_lines=10,
            search_max_results=10,
        ),
    )


def test_get_directory_tree_lists_nested_files(tmp_path: Path) -> None:
    src_path = tmp_path / "src"
    src_path.mkdir()
    (src_path / "api.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# demo\n", encoding="utf-8")

    explorer = build_explorer(tmp_path)
    tree = explorer.get_directory_tree()

    assert "src/" in tree
    assert "api.py" in tree
    assert "README.md" in tree


def test_read_file_returns_numbered_lines(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    file_path.write_text("line one\nline two\nline three\n", encoding="utf-8")

    explorer = build_explorer(tmp_path)
    content = explorer.read_file("app.py", start_line=2, end_line=3)

    assert "0002: line two" in content
    assert "0003: line three" in content


def test_search_code_finds_matches(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    file_path.write_text("router.get('/health')\n", encoding="utf-8")

    explorer = build_explorer(tmp_path)
    matches = explorer.search_code("health")

    assert "health" in matches
    assert "app.py" in matches
