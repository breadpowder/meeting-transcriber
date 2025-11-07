"""Test data models."""

from meeting_transcriber.models.summary import ActionItem, Decision, DiscussionTopic, MeetingSummary
from meeting_transcriber.models.transcript import Segment, TranscriptResult


class TestSegment:
    """Test Segment model."""

    def test_segment_creation(self) -> None:
        """Test creating a segment."""
        segment = Segment(
            id=0, start=0.0, end=5.0, text="Hello world", language="en"
        )

        assert segment.id == 0
        assert segment.start == 0.0
        assert segment.end == 5.0
        assert segment.text == "Hello world"
        assert segment.language == "en"


class TestTranscriptResult:
    """Test TranscriptResult model."""

    def test_transcript_result_creation(self, sample_transcript: TranscriptResult) -> None:
        """Test creating a transcript result."""
        assert len(sample_transcript.segments) == 3
        assert sample_transcript.audio_duration == 15.0
        assert "en" in sample_transcript.detected_languages
        assert "zh" in sample_transcript.detected_languages

    def test_to_text_format(self, sample_transcript: TranscriptResult) -> None:
        """Test transcript to text conversion."""
        text = sample_transcript.to_text()

        assert "MEETING TRANSCRIPT" in text
        assert "[00:00:00 - 00:00:05] (en)" in text
        assert "Hello everyone" in text
        assert "大家好" in text

    def test_format_time(self, sample_transcript: TranscriptResult) -> None:
        """Test time formatting."""
        assert sample_transcript._format_time(0) == "00:00:00"
        assert sample_transcript._format_time(65) == "00:01:05"
        assert sample_transcript._format_time(3665) == "01:01:05"


class TestMeetingSummary:
    """Test MeetingSummary model."""

    def test_summary_creation(self) -> None:
        """Test creating a meeting summary."""
        summary = MeetingSummary(
            overview="Team sync meeting",
            participants=["Alice", "Bob"],
            key_decisions=[Decision(decision="Launch next week", context="Ready for release")],
            action_items=[ActionItem(task="Update docs", assignee="Alice", deadline="Friday")],
            discussion_topics=[
                DiscussionTopic(
                    topic="Release Planning",
                    summary="Discussed release timeline",
                    key_points=["Testing complete", "Documentation needed"],
                )
            ],
            next_steps=["Prepare release notes", "Schedule announcement"],
        )

        assert summary.overview == "Team sync meeting"
        assert len(summary.participants) == 2
        assert len(summary.key_decisions) == 1
        assert len(summary.action_items) == 1

    def test_to_markdown(self) -> None:
        """Test summary to markdown conversion."""
        summary = MeetingSummary(
            overview="Test meeting",
            participants=["Alice"],
            key_decisions=[Decision(decision="Approved", context="All agreed")],
            action_items=[ActionItem(task="Follow up", assignee="Bob")],
            discussion_topics=[],
            next_steps=["Review"],
        )

        markdown = summary.to_markdown()

        assert "# Meeting Summary" in markdown
        assert "## Overview" in markdown
        assert "## Participants" in markdown
        assert "## Key Decisions" in markdown
        assert "## Action Items" in markdown
