from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parent.parent / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://postgres:challenge@localhost:5432/test_postgres"
    secret_key: SecretStr = SecretStr("change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()
