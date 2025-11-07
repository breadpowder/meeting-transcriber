"""Pytest configuration and fixtures."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from meeting_transcriber.core.config import Settings
from meeting_transcriber.models.transcript import Segment, TranscriptResult


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        openai_api_key="test-api-key",
        whisper_model="base",
        whisper_device="cpu",
        whisper_compute_type="int8",
        output_dir=Path("/tmp/test_output"),
        log_level="DEBUG",
    )


@pytest.fixture
def sample_transcript() -> TranscriptResult:
    """Create sample transcript for testing."""
    segments = [
        Segment(
            id=0,
            start=0.0,
            end=5.0,
            text="Hello everyone, welcome to today's meeting.",
            language="en",
        ),
        Segment(
            id=1,
            start=5.5,
            end=10.0,
            text="大家好，欢迎参加今天的会议。",
            language="zh",
        ),
        Segment(
            id=2,
            start=10.5,
            end=15.0,
            text="We need to discuss the project roadmap.",
            language="en",
        ),
    ]

    return TranscriptResult(
        segments=segments,
        full_text=" ".join([s.text for s in segments]),
        detected_languages=["en", "zh"],
        audio_duration=15.0,
    )


@pytest.fixture
def mock_audio_file(tmp_path: Path) -> Path:
    """Create a mock audio file for testing."""
    audio_file = tmp_path / "test_meeting.mp3"
    audio_file.write_bytes(b"fake audio content")
    return audio_file
