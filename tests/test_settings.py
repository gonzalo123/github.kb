from github_kb.settings import get_settings, resolve_settings


def test_resolve_settings_overrides_runtime_values() -> None:
    base_settings = get_settings()
    overridden = resolve_settings(
        aws_profile="sandbox",
        aws_region="eu-west-1",
        bedrock_model_id="model-id",
    )

    assert overridden.aws_profile == "sandbox"
    assert overridden.aws_region == "eu-west-1"
    assert overridden.bedrock_model_id == "model-id"
    assert overridden.repo_cache_path == base_settings.repo_cache_path
