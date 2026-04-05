from pathlib import Path
import shutil
import subprocess

from pydantic import BaseModel, ConfigDict

from settings import Settings

IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}


class RepositoryExplorer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    root_path: Path
    settings: Settings

    def get_directory_tree(self, path: str = ".", max_depth: int | None = None) -> str:
        directory = self._resolve_path(path)
        if not directory.is_dir():
            raise RuntimeError(f"{path} is not a directory.")

        remaining = self.settings.tree_max_entries
        depth_limit = max_depth if max_depth is not None else self.settings.tree_max_depth
        label = self._display_path(directory)
        lines = [f"{label}/"]

        def visit(current: Path, depth: int, prefix: str = "") -> None:
            nonlocal remaining
            if depth >= depth_limit or remaining <= 0:
                return

            entries = [entry for entry in self._iter_entries(current)]
            for index, entry in enumerate(entries):
                if remaining <= 0:
                    lines.append(f"{prefix}...")
                    return

                is_last = index == len(entries) - 1
                connector = "└──" if is_last else "├──"
                suffix = "/" if entry.is_dir() else ""
                lines.append(f"{prefix}{connector} {entry.name}{suffix}")
                remaining -= 1

                if entry.is_dir():
                    visit(entry, depth + 1, prefix + ("    " if is_last else "│   "))

        visit(directory, 0)
        return "\n".join(lines)

    def list_directory(self, path: str = ".") -> str:
        directory = self._resolve_path(path)
        if not directory.is_dir():
            raise RuntimeError(f"{path} is not a directory.")

        lines = [f"Directory: {self._display_path(directory)}"]
        for entry in self._iter_entries(directory):
            kind = "dir " if entry.is_dir() else "file"
            lines.append(f"- [{kind}] {entry.name}")
        return "\n".join(lines)

    def read_file(
        self,
        path: str,
        start_line: int = 1,
        end_line: int | None = None,
    ) -> str:
        file_path = self._resolve_path(path)
        if not file_path.is_file():
            raise RuntimeError(f"{path} is not a file.")

        raw_bytes = file_path.read_bytes()
        if len(raw_bytes) > self.settings.max_file_size_bytes:
            return (
                f"File {self._display_path(file_path)} is too large "
                f"({len(raw_bytes)} bytes). Narrow the request to a smaller file."
            )

        if b"\0" in raw_bytes:
            return f"File {self._display_path(file_path)} looks binary and cannot be rendered as text."

        content = raw_bytes.decode("utf-8", errors="replace").splitlines()
        start = max(start_line, 1)
        max_end = min(len(content), start + self.settings.file_read_max_lines - 1)
        end = min(end_line if end_line is not None else max_end, max_end)

        numbered_lines = [
            f"{line_number:04d}: {content[line_number - 1]}"
            for line_number in range(start, end + 1)
        ]
        header = f"File: {self._display_path(file_path)}"
        return "\n".join([header, *numbered_lines])

    def search_code(
        self,
        query: str,
        glob_pattern: str | None = None,
        max_results: int | None = None,
    ) -> str:
        effective_max_results = max_results or self.settings.search_max_results
        if shutil.which(self.settings.rg_binary):
            return self._search_with_rg(query, glob_pattern, effective_max_results)
        return self._search_with_python(query, glob_pattern, effective_max_results)

    def _search_with_rg(
        self,
        query: str,
        glob_pattern: str | None,
        max_results: int,
    ) -> str:
        command = [
            self.settings.rg_binary,
            "-F",
            "-n",
            "--hidden",
            "--glob",
            "!.git",
            "--glob",
            "!venv/**",
            "--glob",
            "!.venv/**",
        ]
        if glob_pattern:
            command.extend(["-g", glob_pattern])
        command.extend([query, "."])

        completed = subprocess.run(
            command,
            cwd=self.root_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode not in {0, 1}:
            message = completed.stderr.strip() or "Unable to search the repository."
            raise RuntimeError(message)

        matches = [line for line in completed.stdout.splitlines() if line][:max_results]
        if not matches:
            return f"No matches found for '{query}'."

        output = [f"Search query: {query}"]
        output.extend(f"- {match}" for match in matches)
        return "\n".join(output)

    def _search_with_python(
        self,
        query: str,
        glob_pattern: str | None,
        max_results: int,
    ) -> str:
        results: list[str] = []
        pattern = glob_pattern or "**/*"

        for file_path in sorted(self.root_path.glob(pattern)):
            if file_path.is_dir() or self._is_ignored(file_path):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue

            for line_number, line in enumerate(content, start=1):
                if query in line:
                    relative = file_path.relative_to(self.root_path)
                    results.append(f"- {relative}:{line_number}: {line.strip()}")
                    if len(results) >= max_results:
                        return "\n".join([f"Search query: {query}", *results])

        if not results:
            return f"No matches found for '{query}'."

        return "\n".join([f"Search query: {query}", *results])

    def _iter_entries(self, directory: Path) -> list[Path]:
        return sorted(
            (entry for entry in directory.iterdir() if not self._is_ignored(entry)),
            key=lambda entry: (not entry.is_dir(), entry.name.lower()),
        )

    def _is_ignored(self, path: Path) -> bool:
        return any(part in IGNORED_DIRECTORIES for part in path.parts)

    def _resolve_path(self, path: str) -> Path:
        candidate = (self.root_path / path).resolve()
        try:
            candidate.relative_to(self.root_path.resolve())
        except ValueError as error:
            raise RuntimeError(f"Path {path} points outside the repository.") from error
        return candidate

    def _display_path(self, path: Path) -> str:
        if path == self.root_path:
            return "."
        return str(path.relative_to(self.root_path))
