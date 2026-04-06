from github_kb.settings import (
    create_boto_session,
    default_bedrock_model_id,
    get_settings,
    resolve_settings,
)


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
    assert overridden.resolved_bedrock_model_id == "model-id"
    assert overridden.repo_cache_path == base_settings.repo_cache_path


def test_create_boto_session_includes_profile_and_region() -> None:
    settings = resolve_settings(
        aws_profile="sandbox",
        aws_region="eu-west-1",
    )

    session = create_boto_session(settings)

    assert session.profile_name == "sandbox"
    assert session.region_name == "eu-west-1"


def test_default_bedrock_model_id_uses_global_sonnet_4_6() -> None:
    assert default_bedrock_model_id("eu-central-1") == "global.anthropic.claude-sonnet-4-6"
    assert default_bedrock_model_id("ap-southeast-1") == "global.anthropic.claude-sonnet-4-6"
    assert default_bedrock_model_id("us-west-2") == "global.anthropic.claude-sonnet-4-6"
