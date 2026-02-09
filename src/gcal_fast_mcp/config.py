"""Application settings via pydantic-settings."""

import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GCAL_")

    oauth_path: str = Field(
        default="~/.gcal-mcp/gcp-oauth.keys.json",
        description="Path to the OAuth client secrets JSON file.",
    )
    credentials_path: str = Field(
        default="~/.gcal-mcp/credentials.json",
        description="Path to the saved OAuth credentials/token file.",
    )
    default_calendar: str = Field(
        default="primary",
        description="Calendar ID to query by default.",
    )
    max_results: int = Field(
        default=50,
        description="Default maximum number of events to return.",
    )

    @model_validator(mode="after")
    def _expand_paths(self) -> "Config":
        object.__setattr__(self, "oauth_path", os.path.expanduser(self.oauth_path))
        object.__setattr__(self, "credentials_path", os.path.expanduser(self.credentials_path))
        return self
