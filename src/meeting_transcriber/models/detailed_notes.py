"""Detailed meeting notes data models."""

from typing import List

from pydantic import BaseModel, Field


class BulletPoint(BaseModel):
    """A bullet point with optional sub-bullets."""

    text: str = Field(..., description="Main bullet point text")
    sub_bullets: List[str] = Field(
        default_factory=list,
        description="Nested sub-bullets for details, examples, or timestamps",
    )


class NoteSection(BaseModel):
    """A section of detailed meeting notes."""

    title: str = Field(..., description="Section title (topic-based, no timestamp)")
    bullets: List[BulletPoint] = Field(
        default_factory=list,
        description="Bullet points with nested sub-bullets",
    )


class DetailedMeetingNotes(BaseModel):
    """
    Detailed meeting notes with bullet-point structure.

    Notes are organized by topic (not chronologically) with bullet points
    and nested sub-bullets for clarity. Timestamps appear as sub-bullets
    for context.
    """

    meeting_title: str = Field(
        ..., description="Descriptive meeting title (not generic)"
    )
    sections: List[NoteSection] = Field(
        default_factory=list,
        description="Topic-based sections with bullet content",
    )

    def to_markdown(self) -> str:
        """Convert detailed notes to markdown format."""
        lines = [
            f"# {self.meeting_title}",
            "",
            "",
        ]

        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append("")

            for bullet in section.bullets:
                lines.append(f"- {bullet.text}")
                lines.append("")

                for sub_bullet in bullet.sub_bullets:
                    lines.append(f"  - {sub_bullet}")
                    lines.append("")

            lines.append("")

        return "\n".join(lines)
