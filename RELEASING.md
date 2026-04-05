# Releasing github-kb

## 1. Build and validate

```bash
poetry lock
poetry install
poetry run pytest -q
poetry build
pipx install --force dist/github_kb-0.1.0-py3-none-any.whl
github-kb --help
github-kb doctor --help
```

## 2. Configure the PyPI token

Create a token in PyPI and store it in Poetry:

```bash
poetry config pypi-token.pypi <your-token>
```

## 3. Publish

```bash
poetry publish --build
```

## 4. Verify the public install flow

```bash
pipx install github-kb
github-kb --help
```
