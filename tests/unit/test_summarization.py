"""Test summarization service."""

import json
from unittest.mock import MagicMock, patch

import pytest

from meeting_transcriber.core.config import Settings
from meeting_transcriber.core.exceptions import SummarizationError
from meeting_transcriber.models.transcript import TranscriptResult
from meeting_transcriber.services.summarization import SummarizationService


class TestSummarizationService:
    """Test SummarizationService."""

    def test_initialization(self, mock_settings: Settings) -> None:
        """Test service initialization."""
        service = SummarizationService(mock_settings)

        assert service.settings == mock_settings
        assert service.client is not None

    def test_prepare_transcript_prompt(
        self, mock_settings: Settings, sample_transcript: TranscriptResult
    ) -> None:
        """Test transcript prompt preparation."""
        service = SummarizationService(mock_settings)

        prompt = service._prepare_transcript_prompt(sample_transcript)

        assert "Meeting Transcript:" in prompt
        assert "Duration:" in prompt
        assert "Languages: en, zh" in prompt
        assert "Hello everyone" in prompt
        assert "大家好" in prompt

    def test_format_time(self, mock_settings: Settings) -> None:
        """Test time formatting."""
        service = SummarizationService(mock_settings)

        assert service._format_time(0) == "00:00"
        assert service._format_time(65) == "01:05"
        assert service._format_time(125) == "02:05"

    def test_format_duration(self, mock_settings: Settings) -> None:
        """Test duration formatting."""
        service = SummarizationService(mock_settings)

        assert service._format_duration(30) == "30s"
        assert service._format_duration(90) == "1m 30s"
        assert service._format_duration(3665) == "1h 1m 5s"

    def test_parse_summary(self, mock_settings: Settings) -> None:
        """Test summary parsing from JSON."""
        service = SummarizationService(mock_settings)

        data = {
            "overview": "Test meeting overview",
            "participants": ["Alice", "Bob"],
            "key_decisions": [{"decision": "Launch product", "context": "Ready"}],
            "action_items": [{"task": "Update docs", "assignee": "Alice", "deadline": "Friday"}],
            "discussion_topics": [
                {
                    "topic": "Planning",
                    "summary": "Discussed timeline",
                    "key_points": ["Point 1", "Point 2"],
                }
            ],
            "next_steps": ["Review", "Deploy"],
        }

        summary = service._parse_summary(data)

        assert summary.overview == "Test meeting overview"
        assert len(summary.participants) == 2
        assert len(summary.key_decisions) == 1
        assert summary.key_decisions[0].decision == "Launch product"
        assert len(summary.action_items) == 1
        assert summary.action_items[0].task == "Update docs"
        assert len(summary.discussion_topics) == 1
        assert len(summary.next_steps) == 2

    @patch("meeting_transcriber.services.summarization.OpenAI")
    def test_summarize_success(
        self,
        mock_openai_class: MagicMock,
        mock_settings: Settings,
        sample_transcript: TranscriptResult,
    ) -> None:
        """Test successful summarization."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "overview": "Meeting summary",
            "participants": ["Alice"],
            "key_decisions": [],
            "action_items": [],
            "discussion_topics": [],
            "next_steps": [],
        })
        mock_client.chat.completions.create.return_value = mock_response

        service = SummarizationService(mock_settings)
        summary = service.summarize(sample_transcript)

        assert summary.overview == "Meeting summary"
        assert len(summary.participants) == 1

    @patch("meeting_transcriber.services.summarization.OpenAI")
    def test_summarize_empty_response(
        self,
        mock_openai_class: MagicMock,
        mock_settings: Settings,
        sample_transcript: TranscriptResult,
    ) -> None:
        """Test summarization with empty response."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response

        service = SummarizationService(mock_settings)

        with pytest.raises(SummarizationError, match="Empty response"):
            service.summarize(sample_transcript)

    @patch("meeting_transcriber.services.summarization.OpenAI")
    def test_summarize_invalid_json(
        self,
        mock_openai_class: MagicMock,
        mock_settings: Settings,
        sample_transcript: TranscriptResult,
    ) -> None:
        """Test summarization with invalid JSON response."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "invalid json"
        mock_client.chat.completions.create.return_value = mock_response

        service = SummarizationService(mock_settings)

        with pytest.raises(SummarizationError, match="Failed to parse JSON"):
            service.summarize(sample_transcript)
