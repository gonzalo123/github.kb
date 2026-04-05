import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
ENV_FILE = BASE_DIR / "env" / ENVIRONMENT / ".env"

load_dotenv(dotenv_path=ENV_FILE)


class Settings(BaseSettings):
    aws_region: str = Field(
        default="us-west-2",
        validation_alias="AWS_REGION",
    )
    bedrock_model_id: str = Field(
        default="us.anthropic.claude-sonnet-4-20250514-v1:0",
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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
