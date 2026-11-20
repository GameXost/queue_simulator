from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://queue:queue@localhost:5432/queue"
    secret_key: str = "dev-secret-change-me"
    timezone: str = "Europe/Moscow"


settings = Settings()
TZ = ZoneInfo(settings.timezone)
