from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "BCBIST API"
    VERSION: str = "2.0.0"
    API_STR: str = "/api"

    # Yahoo Finance Settings
    YAHOO_TIMEOUT: int = 10

    # Cache Settings
    CACHE_DIR: str = "data/cache"
    CACHE_TIME: int = 1800  # 30 minutes

    # Execution Settings
    MAX_WORKERS: int = 40

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
