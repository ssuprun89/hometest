from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "IP Geolocation Service"
    app_version: str = "1.0.0"
    debug: bool = False

    ip_api_base_url: str = "http://ip-api.com"
    ip_api_timeout: float = 10.0


settings = Settings()
