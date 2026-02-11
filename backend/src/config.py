"""Application configuration module.

Centralizes all environment variables and settings.
"""

import json
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Google Cloud
    google_cloud_project: str

    # Vertex AI Search
    vertex_ai_data_store_id: str
    vertex_ai_location: str = "global"

    # Gemini
    gemini_toc_model: str = "gemini-2.5-flash"
    gemini_report_model: str = "gemini-2.5-flash"
    gemini_location: str = "asia-northeast1"

    # CORS
    cors_origins: list[str] | str = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Support both JSON list and comma-separated string formats."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Fallback to comma or semicolon separated string (semicolon is safer for CLI)
            if ";" in v:
                return [origin.strip() for origin in v.split(";") if origin.strip()]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to avoid reading env vars on every call.
    """
    return Settings()
