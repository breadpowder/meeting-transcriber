"""Custom exceptions for meeting transcriber."""


class MeetingTranscriberException(Exception):
    """Base exception for all meeting transcriber errors."""

    pass


class TranscriptionError(MeetingTranscriberException):
    """Errors during audio transcription."""

    pass


class SummarizationError(MeetingTranscriberException):
    """Errors during LLM summarization."""

    pass


class AudioFileError(MeetingTranscriberException):
    """Errors related to audio file handling."""

    pass


class ConfigurationError(MeetingTranscriberException):
    """Configuration-related errors."""

    pass
