"""Detailed notes generation service using OpenAI GPT."""

import json
from typing import Optional

from openai import OpenAI

from ..core.config import Settings
from ..core.exceptions import SummarizationError
from ..core.logging_config import get_logger
from ..models.detailed_notes import DetailedMeetingNotes, NoteSection
from ..models.transcript import TranscriptResult


class DetailedNotesService:
    """
    Service for generating detailed meeting notes using OpenAI GPT.

    Unlike summarization which condenses information, this service paraphrases
    the entire oral meeting transcript into well-structured written notes,
    preserving all details discussed.
    """

    SYSTEM_PROMPT = """You are an expert meeting note-taker who transforms oral meeting transcripts into detailed, well-structured written notes.

Your task is to:
1. Paraphrase ALL oral content into clear, professional written prose
2. Preserve ALL details, discussions, and information from the meeting
3. Organize content chronologically with logical section breaks
4. Transform conversational speech into polished written language
5. Maintain the original language (English or Chinese) for each section
6. Include approximate timestamps for each major section/topic

DO NOT:
- Summarize or condense information
- Skip any discussed topics or details
- Remove context or explanations
- Create bullet points unless they were explicitly enumerated in the meeting

The goal is to create comprehensive meeting notes that someone who missed the meeting can read to understand EVERYTHING that was discussed, as if they were there.

Return a JSON object with this structure:
{
  "meeting_title": "Main topic or meeting purpose",
  "date_time": "Date/time if mentioned, otherwise empty string",
  "participants": ["name1", "name2"],
  "sections": [
    {
      "title": "Section topic",
      "timestamp": "MM:SS",
      "content": [
        "First paragraph of detailed content...",
        "Second paragraph continuing the discussion...",
        "Third paragraph with more details..."
      ]
    }
  ],
  "key_terminology": ["term1: explanation", "term2: explanation"]
}

Each section should contain multiple paragraphs that fully capture the discussion in that timeframe.
"""

    def __init__(self, settings: Settings):
        """
        Initialize detailed notes service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = get_logger(__name__)
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_detailed_notes(
        self,
        transcript: TranscriptResult,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
    ) -> DetailedMeetingNotes:
        """
        Generate detailed meeting notes from transcript.

        Args:
            transcript: Transcription result
            model: OpenAI model to use (gpt-4o, gpt-4o-mini)
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Detailed meeting notes

        Raises:
            SummarizationError: If generation fails
        """
        self.logger.info(f"Starting detailed notes generation with model: {model}")

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

            notes_data = json.loads(content)
            detailed_notes = self._parse_notes(notes_data)

            self.logger.info("Detailed notes generation completed successfully")
            return detailed_notes

        except json.JSONDecodeError as e:
            raise SummarizationError(f"Failed to parse JSON response: {e}") from e
        except Exception as e:
            raise SummarizationError(f"Detailed notes generation failed: {e}") from e

    def _prepare_transcript_prompt(self, transcript: TranscriptResult) -> str:
        """
        Prepare transcript text for LLM prompt.

        Args:
            transcript: Transcription result

        Returns:
            Formatted transcript text
        """
        lines = [
            "Meeting Transcript to Transform into Detailed Notes:",
            f"Duration: {self._format_duration(transcript.audio_duration)}",
            f"Languages: {', '.join(transcript.detected_languages)}",
            "",
            "Full Transcript:",
            "",
        ]

        # Include segment-level text with timestamps
        for segment in transcript.segments:
            timestamp = self._format_time(segment.start)
            lang_tag = f" [{segment.language}]" if segment.language else ""
            lines.append(f"[{timestamp}]{lang_tag} {segment.text}")

        lines.extend(
            [
                "",
                "Task: Transform this oral transcript into detailed, well-structured written meeting notes.",
                "Preserve ALL information and details. Organize chronologically with clear section breaks.",
            ]
        )

        return "\n".join(lines)

    def _parse_notes(self, data: dict) -> DetailedMeetingNotes:
        """
        Parse notes data from JSON to DetailedMeetingNotes model.

        Args:
            data: JSON data from LLM

        Returns:
            Parsed DetailedMeetingNotes
        """
        # Parse sections
        sections = [
            NoteSection(
                title=section.get("title", ""),
                timestamp=section.get("timestamp", "00:00"),
                content=section.get("content", []),
            )
            for section in data.get("sections", [])
        ]

        return DetailedMeetingNotes(
            meeting_title=data.get("meeting_title", "Meeting Notes"),
            date_time=data.get("date_time", ""),
            participants=data.get("participants", []),
            sections=sections,
            key_terminology=data.get("key_terminology", []),
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
