"""Application configuration."""

from functools import lru_cache
from typing import Literal
from uuid import UUID

from fastapi import Request
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["dev", "prod"]


class Settings(BaseSettings):
    """Environment-backed settings with startup validation."""

    ENV: Environment
    LOG_LEVEL: str
    SIGNALGROK_WEBHOOK_KEY: SecretStr
    WEBHOOK_ENDPOINT_ID: UUID = UUID("00000000-0000-0000-0000-000000000001")
    DATABASE_URL: str
    OPENAI_API_KEY: SecretStr
    FINNHUB_API_KEY: SecretStr
    DISCORD_WEBHOOK_URL: SecretStr
    CORS_ALLOWED_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ENV")
    @classmethod
    def validate_env(cls, value: Environment) -> Environment:
        if value not in {"dev", "prod"}:
            raise ValueError("ENV must be either 'dev' or 'prod'")
        return value

    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"

    @property
    def debug(self) -> bool:
        return self.is_dev

    @property
    def cors_origins(self) -> list[str]:
        if self.is_dev:
            return ["*"]
        return self.CORS_ALLOWED_ORIGINS


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_settings_dependency(request: Request) -> Settings:
    return request.app.state.settings

