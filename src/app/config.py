import os
from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    DATABASE_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()
