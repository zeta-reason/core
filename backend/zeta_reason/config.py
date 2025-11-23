"""Configuration management for Zeta Reason."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS Settings
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        # For v0.1, we don't require API keys (can use dummy runner)
        pass


# Singleton config instance
config = Config()
