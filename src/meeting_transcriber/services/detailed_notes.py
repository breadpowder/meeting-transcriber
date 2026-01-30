"""Detailed notes generation service using OpenAI GPT."""

import json
from typing import Optional

from openai import OpenAI

from ..core.config import Settings
from ..core.exceptions import SummarizationError
from ..core.logging_config import get_logger
from ..models.detailed_notes import BulletPoint, DetailedMeetingNotes, NoteSection
from ..models.transcript import TranscriptResult


class DetailedNotesService:
    """
    Service for generating detailed meeting notes using OpenAI GPT.

    Unlike summarization which condenses information, this service paraphrases
    the entire oral meeting transcript into well-structured written notes,
    preserving all details discussed.
    """

    SYSTEM_PROMPT = """You are an expert meeting note-taker who transforms oral transcripts into well-structured written notes using bullet points.

CRITICAL REQUIREMENTS:
1. The meeting_title MUST be descriptive (e.g., "Voice Pipeline Architecture and Deployment Strategy for Paytm"), NOT generic like "Meeting Notes"
2. ALL content MUST be bullet points - NO paragraphs allowed
3. Group content by TOPIC, not chronologically
4. Include timestamps [MM:SS] as sub-bullets for context
5. DO NOT include participants, terminology, or metadata sections

SECTION ORGANIZATION (follow this flow):
1. **Overview/Architecture Section** - Start with high-level understanding
2. **Configuration/Strategy Section** - How things work or are approached
3. **Implementation/Technical Details Section** - Current state and specifics
4. **Next Steps/Action Items Section** - ALWAYS include this as final section with:
   - Immediate priorities (short-term items)
   - Integration/approach strategy
   - Development/environment needs

BULLET POINT PATTERNS:
- Use category bullets that end with `:` when listing related items
- Use arrows (→) for process flows
- Main bullets = concepts/categories
- Sub-bullets = specific details, examples, timestamps

EXAMPLE STRUCTURE:
## Section Title
- Category or concept:
  - Specific detail
  - Another detail
  - [MM:SS] Timestamp context
- Process flow: Step 1 → Step 2 → Step 3
- Another main point
  - Supporting detail

PRESERVE ALL INFORMATION - transform speech into clear bullet points.

Return JSON:
{
  "meeting_title": "Specific descriptive title of the meeting topic",
  "sections": [
    {
      "title": "Overview/Architecture Section Title",
      "bullets": [
        {
          "text": "Category or concept:",
          "sub_bullets": ["Detail 1", "Detail 2", "[MM:SS] Timestamp"]
        }
      ]
    },
    {
      "title": "Next Steps and Action Items",
      "bullets": [
        {
          "text": "Immediate priorities:",
          "sub_bullets": ["Priority item 1", "Priority item 2"]
        },
        {
          "text": "Integration strategy:",
          "sub_bullets": ["Approach detail"]
        }
      ]
    }
  ]
}
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
                "Use bullet points with sub-bullets. Group by topic, not chronologically.",
                "Include timestamps as sub-bullets [MM:SS] for context.",
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
        # Parse sections with bullet structure
        sections = []
        for section in data.get("sections", []):
            bullets = []
            for bullet_data in section.get("bullets", []):
                bullet = BulletPoint(
                    text=bullet_data.get("text", ""),
                    sub_bullets=bullet_data.get("sub_bullets", []),
                )
                bullets.append(bullet)

            sections.append(
                NoteSection(
                    title=section.get("title", ""),
                    bullets=bullets,
                )
            )

        return DetailedMeetingNotes(
            meeting_title=data.get("meeting_title", "Meeting Notes"),
            sections=sections,
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
