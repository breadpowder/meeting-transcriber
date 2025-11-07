"""Summarization service using OpenAI GPT."""

import json
from typing import Optional

from openai import OpenAI

from ..core.config import Settings
from ..core.exceptions import SummarizationError
from ..core.logging_config import get_logger
from ..models.summary import ActionItem, Decision, DiscussionTopic, MeetingSummary
from ..models.transcript import TranscriptResult


class SummarizationService:
    """Service for summarizing meeting transcripts using OpenAI GPT."""

    SYSTEM_PROMPT = """You are an expert meeting assistant that creates structured meeting summaries.
Analyze the provided meeting transcript and extract:
1. Overview of the meeting
2. Participants mentioned (if any)
3. Key decisions made
4. Action items with assignees and deadlines (if mentioned)
5. Discussion topics with summaries
6. Next steps

Support both English and Chinese (Mandarin) content. Preserve the original language in summaries.

Return a JSON object with this structure:
{
  "overview": "Brief meeting overview",
  "participants": ["name1", "name2"],
  "key_decisions": [{"decision": "...", "context": "..."}],
  "action_items": [{"task": "...", "assignee": "...", "deadline": "..."}],
  "discussion_topics": [{"topic": "...", "summary": "...", "key_points": ["..."]}],
  "next_steps": ["step1", "step2"]
}
"""

    def __init__(self, settings: Settings):
        """
        Initialize summarization service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = get_logger(__name__)
        self.client = OpenAI(api_key=settings.openai_api_key)

    def summarize(
        self,
        transcript: TranscriptResult,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
    ) -> MeetingSummary:
        """
        Generate structured meeting summary from transcript.

        Args:
            transcript: Transcription result
            model: OpenAI model to use (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Structured meeting summary

        Raises:
            SummarizationError: If summarization fails
        """
        self.logger.info(f"Starting summarization with model: {model}")

        try:
            # Prepare the transcript text
            user_prompt = self._prepare_transcript_prompt(transcript)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise SummarizationError("Empty response from OpenAI API")

            summary_data = json.loads(content)
            summary = self._parse_summary(summary_data)

            self.logger.info("Summarization completed successfully")
            return summary

        except json.JSONDecodeError as e:
            raise SummarizationError(f"Failed to parse JSON response: {e}") from e
        except Exception as e:
            raise SummarizationError(f"Summarization failed: {e}") from e

    def _prepare_transcript_prompt(self, transcript: TranscriptResult) -> str:
        """
        Prepare transcript text for LLM prompt.

        Args:
            transcript: Transcription result

        Returns:
            Formatted transcript text
        """
        lines = [
            "Meeting Transcript:",
            f"Duration: {self._format_duration(transcript.audio_duration)}",
            f"Languages: {', '.join(transcript.detected_languages)}",
            "",
            "Transcript:",
            "",
        ]

        # Include segment-level text with timestamps
        for segment in transcript.segments:
            timestamp = self._format_time(segment.start)
            lang_tag = f" [{segment.language}]" if segment.language else ""
            lines.append(f"[{timestamp}]{lang_tag} {segment.text}")

        return "\n".join(lines)

    def _parse_summary(self, data: dict) -> MeetingSummary:
        """
        Parse summary data from JSON to MeetingSummary model.

        Args:
            data: JSON data from LLM

        Returns:
            Parsed MeetingSummary
        """
        # Parse key decisions
        key_decisions = [
            Decision(
                decision=d.get("decision", ""),
                context=d.get("context"),
            )
            for d in data.get("key_decisions", [])
        ]

        # Parse action items
        action_items = [
            ActionItem(
                task=item.get("task", ""),
                assignee=item.get("assignee"),
                deadline=item.get("deadline"),
            )
            for item in data.get("action_items", [])
        ]

        # Parse discussion topics
        discussion_topics = [
            DiscussionTopic(
                topic=topic.get("topic", ""),
                summary=topic.get("summary", ""),
                key_points=topic.get("key_points", []),
            )
            for topic in data.get("discussion_topics", [])
        ]

        return MeetingSummary(
            overview=data.get("overview", ""),
            participants=data.get("participants", []),
            key_decisions=key_decisions,
            action_items=action_items,
            discussion_topics=discussion_topics,
            next_steps=data.get("next_steps", []),
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration to human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
