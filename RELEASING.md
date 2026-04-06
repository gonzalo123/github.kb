# Releasing github-kb

## 1. Bump the version

Update the version in:

- `pyproject.toml`
- `src/github_kb/__init__.py`

## 2. Build and validate

```bash
poetry lock
poetry install
poetry run pytest -q
poetry build
pipx install --force dist/github_kb-<version>-py3-none-any.whl
github-kb --help
github-kb doctor --help
```

If you want to test the local package without relying on entrypoint wrappers from another environment, this is also useful:

```bash
AWS_PROFILE=sandbox AWS_REGION=eu-central-1 poetry run python -m github_kb doctor
AWS_PROFILE=sandbox AWS_REGION=eu-central-1 poetry run python -m github_kb ask gonzalo123/autofix "What does this project do?"
```

By default the CLI now uses `global.anthropic.claude-sonnet-4-6` unless a different model is provided via `BEDROCK_MODEL_ID` or `--model`.

## 3. Configure the PyPI token

Create a token in PyPI and store it in Poetry:

```bash
poetry config pypi-token.pypi <your-token>
```

## 4. Commit, tag and publish

```bash
git add README.md RELEASING.md pyproject.toml poetry.lock src/github_kb/__init__.py src/github_kb/settings.py src/github_kb/lib/agent.py src/github_kb/lib/doctor.py tests/test_settings.py
git commit -m "Release v<version>"
git push
git tag v<version>
git push origin v<version>
```

Then publish to PyPI:

```bash
poetry publish --build
```

## 5. Verify the public install flow

```bash
pipx uninstall github-kb
pipx install github-kb
github-kb --help
github-kb doctor --help
```

For a real smoke test against Bedrock:

```bash
aws sso login --profile sandbox
AWS_PROFILE=sandbox AWS_REGION=eu-central-1 github-kb doctor
AWS_PROFILE=sandbox AWS_REGION=eu-central-1 github-kb ask gonzalo123/autofix "What does this project do?"
```
