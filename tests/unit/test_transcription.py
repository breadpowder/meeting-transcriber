"""Test transcription service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from meeting_transcriber.core.config import Settings
from meeting_transcriber.core.exceptions import AudioFileError, TranscriptionError
from meeting_transcriber.services.transcription import TranscriptionService


class TestTranscriptionService:
    """Test TranscriptionService."""

    def test_initialization(self, mock_settings: Settings) -> None:
        """Test service initialization."""
        service = TranscriptionService(mock_settings)

        assert service.settings == mock_settings
        assert service._model is None

    def test_detect_segment_language_english(self, mock_settings: Settings) -> None:
        """Test language detection for English text."""
        service = TranscriptionService(mock_settings)

        result = service._detect_segment_language("Hello world, this is a test.")
        assert result == "en"

    def test_detect_segment_language_chinese(self, mock_settings: Settings) -> None:
        """Test language detection for Chinese text."""
        service = TranscriptionService(mock_settings)

        result = service._detect_segment_language("你好世界，这是一个测试。")
        assert result == "zh"

    def test_detect_segment_language_mixed(self, mock_settings: Settings) -> None:
        """Test language detection for mixed text."""
        service = TranscriptionService(mock_settings)

        # More English than Chinese
        result = service._detect_segment_language("Hello 你好 world")
        assert result == "en"

        # More Chinese than English
        result = service._detect_segment_language("你好世界 hello")
        assert result == "zh"

    def test_transcribe_file_not_found(self, mock_settings: Settings) -> None:
        """Test transcription with non-existent file."""
        service = TranscriptionService(mock_settings)

        with pytest.raises(AudioFileError, match="Audio file not found"):
            service.transcribe(Path("/nonexistent/file.mp3"))

    def test_transcribe_unsupported_format(
        self, mock_settings: Settings, tmp_path: Path
    ) -> None:
        """Test transcription with unsupported file format."""
        service = TranscriptionService(mock_settings)

        # Create a file with unsupported extension
        bad_file = tmp_path / "test.txt"
        bad_file.write_text("not an audio file")

        with pytest.raises(AudioFileError, match="Unsupported audio format"):
            service.transcribe(bad_file)

    @patch("meeting_transcriber.services.transcription.WhisperModel")
    def test_load_model(self, mock_whisper_class: MagicMock, mock_settings: Settings) -> None:
        """Test model loading."""
        service = TranscriptionService(mock_settings)
        mock_model = MagicMock()
        mock_whisper_class.return_value = mock_model

        model = service._load_model()

        assert model == mock_model
        mock_whisper_class.assert_called_once_with(
            mock_settings.whisper_model,
            device=mock_settings.whisper_device,
            compute_type=mock_settings.whisper_compute_type,
        )

    @patch("meeting_transcriber.services.transcription.WhisperModel")
    def test_load_model_error(
        self, mock_whisper_class: MagicMock, mock_settings: Settings
    ) -> None:
        """Test model loading error."""
        service = TranscriptionService(mock_settings)
        mock_whisper_class.side_effect = Exception("Model load failed")

        with pytest.raises(TranscriptionError, match="Failed to load Whisper model"):
            service._load_model()
