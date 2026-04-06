import os
from functools import lru_cache
from pathlib import Path

import boto3
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
ENV_FILE = BASE_DIR / "env" / ENVIRONMENT / ".env"

load_dotenv(dotenv_path=ENV_FILE)


class Settings(BaseSettings):
    aws_profile: str | None = Field(
        default=None,
        validation_alias="AWS_PROFILE",
    )
    aws_region: str = Field(
        default="us-west-2",
        validation_alias="AWS_REGION",
    )
    bedrock_model_id: str | None = Field(
        default=None,
        validation_alias="BEDROCK_MODEL_ID",
    )
    repo_cache_path: Path = Field(
        default=Path.home() / ".cache" / "github-kb" / "repos",
        validation_alias="REPO_CACHE_PATH",
    )
    tree_max_depth: int = Field(default=4, validation_alias="TREE_MAX_DEPTH")
    tree_max_entries: int = Field(default=250, validation_alias="TREE_MAX_ENTRIES")
    search_max_results: int = Field(default=25, validation_alias="SEARCH_MAX_RESULTS")
    file_read_max_lines: int = Field(default=250, validation_alias="FILE_READ_MAX_LINES")
    max_file_size_bytes: int = Field(default=200_000, validation_alias="MAX_FILE_SIZE_BYTES")
    git_binary: str = Field(default="git", validation_alias="GIT_BINARY")
    rg_binary: str = Field(default="rg", validation_alias="RG_BINARY")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def resolved_bedrock_model_id(self) -> str:
        if self.bedrock_model_id:
            return self.bedrock_model_id

        return default_bedrock_model_id(self.aws_region)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def resolve_settings(
    *,
    aws_profile: str | None = None,
    aws_region: str | None = None,
    bedrock_model_id: str | None = None,
) -> Settings:
    settings = get_settings()
    updates: dict[str, str | None] = {}

    if aws_profile:
        updates["aws_profile"] = aws_profile
    if aws_region:
        updates["aws_region"] = aws_region
    if bedrock_model_id:
        updates["bedrock_model_id"] = bedrock_model_id

    if not updates:
        return settings

    return settings.model_copy(update=updates)


def create_boto_session(settings: Settings) -> boto3.Session:
    kwargs: dict[str, str] = {}

    if settings.aws_profile:
        kwargs["profile_name"] = settings.aws_profile
    if settings.aws_region:
        kwargs["region_name"] = settings.aws_region

    return boto3.Session(**kwargs)


def default_bedrock_model_id(region: str) -> str:
    return "global.anthropic.claude-sonnet-4-6"
