from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = Field(default="dev", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    signalgrok_webhook_key: str = Field(..., alias="SIGNALGROK_WEBHOOK_KEY")
    database_url: str = Field(default="postgresql+psycopg://signalgrok:signalgrok@localhost:5432/signalgrok", alias="DATABASE_URL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    finnhub_api_key: str = Field(default="", alias="FINNHUB_API_KEY")
    discord_webhook_url: str = Field(default="", alias="DISCORD_WEBHOOK_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
