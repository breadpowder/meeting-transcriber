"""Application configuration management."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for GPT summarization")

    # Whisper Model Configuration
    whisper_model: str = Field(
        default="large-v3", description="Whisper model size (tiny, base, small, medium, large-v3)"
    )
    whisper_device: Literal["cuda", "cpu"] = Field(
        default="cuda", description="Device to run Whisper on"
    )
    whisper_compute_type: str = Field(
        default="float16", description="Compute type (float16, int8, float32)"
    )

    # Application Configuration
    output_dir: Path = Field(default=Path("./output"), description="Output directory for results")
    log_level: str = Field(default="INFO", description="Logging level")

    def __init__(self, **kwargs):  # type: ignore
        super().__init__(**kwargs)
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
