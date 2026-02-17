"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings."""

    app_env: str = "development"
    app_name: str = "SignalGrok Webhook Receiver"
    app_version: str = "0.1.0"
    signalgrok_webhook_key: str = ""
    log_level: str = "INFO"

    # Planned integrations
    finnhub_api_key: str = ""
    openai_api_key: str = ""
    discord_webhook_url: str = ""
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/signalgrok"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
