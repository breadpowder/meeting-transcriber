"""Detailed meeting notes data models."""

from typing import List

from pydantic import BaseModel, Field


class NoteSection(BaseModel):
    """A section of detailed meeting notes."""

    title: str = Field(..., description="Section title")
    content: List[str] = Field(
        default_factory=list,
        description="Detailed content paragraphs in chronological order",
    )
    timestamp: str = Field(..., description="Approximate timestamp (MM:SS format)")


class DetailedMeetingNotes(BaseModel):
    """
    Detailed meeting notes with full paraphrasing.

    Unlike a summary which condenses information, detailed notes preserve
    all discussed content by paraphrasing oral speech into well-structured
    written notes organized chronologically.
    """

    meeting_title: str = Field(..., description="Meeting title or main topic")
    date_time: str = Field(..., description="Meeting date/time if mentioned")
    participants: List[str] = Field(
        default_factory=list, description="Meeting participants if mentioned"
    )
    sections: List[NoteSection] = Field(
        default_factory=list,
        description="Chronological sections with detailed content",
    )
    key_terminology: List[str] = Field(
        default_factory=list,
        description="Important terms or acronyms mentioned",
    )

    def to_markdown(self) -> str:
        """Convert detailed notes to markdown format."""
        lines = [
            "# Detailed Meeting Notes",
            "",
            f"## {self.meeting_title}",
            "",
        ]

        if self.date_time:
            lines.extend([f"**Date/Time**: {self.date_time}", ""])

        if self.participants:
            lines.extend(["**Participants**:", ""])
            for participant in self.participants:
                lines.append(f"- {participant}")
            lines.append("")

        if self.key_terminology:
            lines.extend(["**Key Terminology**:", ""])
            for term in self.key_terminology:
                lines.append(f"- {term}")
            lines.append("")

        lines.extend(["---", "", "## Meeting Content", ""])

        # Add all sections chronologically
        for section in self.sections:
            lines.append(f"### [{section.timestamp}] {section.title}")
            lines.append("")

            for paragraph in section.content:
                lines.append(paragraph)
                lines.append("")

        return "\n".join(lines)
