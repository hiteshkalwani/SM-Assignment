"""
Application configuration management.

This module handles loading and validating configuration settings from environment variables.
"""

import logging
from functools import lru_cache
from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    APP_NAME: str = "City Information Assistant"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = Field(
        default="change-this-in-production-using-.env-file",
        min_length=32,
        max_length=64,
    )

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "City Information Assistant API"
    SERVER_NAME: str = "city-info-api"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"  # type: ignore

    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:3000"]

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 1024

    # API Keys for external services
    OPENWEATHER_API_KEY: Optional[str] = Field(None, env="OPENWEATHER_API_KEY")
    GEODB_API_KEY: Optional[str] = Field(None, env="GEODB_API_KEY")

    # LangSmith settings (optional)
    LANGCHAIN_TRACING_V2: bool = Field(False, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_API_KEY: Optional[str] = Field(None, env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: Optional[str] = Field(None, env="LANGCHAIN_PROJECT")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(
        "https://api.smith.langchain.com",
        env="LANGCHAIN_ENDPOINT"
    )

    # GeoDB API settings
    GEODB_API_HOST: str = "wft-geo-db.p.rapidapi.com"

    # OpenWeatherMap API settings
    OPENWEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    # WorldTimeAPI settings
    WORLDTIME_API_URL: str = "http://worldtimeapi.org/api/timezone"

    # Database settings (for future use)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "city_assistant"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Model configuration
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse CORS origins from environment."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Any:
        """Assemble database connection string."""
        if isinstance(v, str):
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate LOG_LEVEL value."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {', '.join(valid_levels)}")
        return v.upper()


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    This function is cached to prevent reloading the .env file on every request.
    """
    return Settings()


# Create settings instance to be imported
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log the current environment
logger.info("Running in %s mode", settings.ENVIRONMENT)
logger.info("Using OpenAI model: %s", settings.OPENAI_MODEL)
