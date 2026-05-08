from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Weather Ranker"
    app_version: str = "1.0.0"

    # Open-Meteo API base URL.
    # Stored in environment configuration to separate infrastructure settings
    # from application code and allow environment-specific overrides.
    open_meteo_base_url: str = "https://archive-api.open-meteo.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()