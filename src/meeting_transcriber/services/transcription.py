"""Transcription service using faster-whisper."""

from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

from ..core.config import Settings
from ..core.exceptions import AudioFileError, TranscriptionError
from ..core.logging_config import get_logger
from ..models.transcript import Segment, TranscriptResult


class TranscriptionService:
    """Service for transcribing audio files using faster-whisper."""

    def __init__(self, settings: Settings):
        """
        Initialize transcription service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = get_logger(__name__)
        self._model: Optional[WhisperModel] = None

    def _load_model(self) -> WhisperModel:
        """
        Load Whisper model (lazy loading).

        Returns:
            Loaded WhisperModel instance
        """
        if self._model is None:
            self.logger.info(
                f"Loading Whisper model: {self.settings.whisper_model} "
                f"on {self.settings.whisper_device}"
            )
            try:
                self._model = WhisperModel(
                    self.settings.whisper_model,
                    device=self.settings.whisper_device,
                    compute_type=self.settings.whisper_compute_type,
                )
                self.logger.info("Whisper model loaded successfully")
            except Exception as e:
                raise TranscriptionError(f"Failed to load Whisper model: {e}") from e

        return self._model

    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> TranscriptResult:
        """
        Transcribe audio file with automatic language detection.

        Args:
            audio_path: Path to audio file (MP3 or WAV)
            language: Language code (None for auto-detection)
            task: 'transcribe' or 'translate'

        Returns:
            TranscriptResult with segments and full text

        Raises:
            AudioFileError: If audio file is invalid
            TranscriptionError: If transcription fails
        """
        if not audio_path.exists():
            raise AudioFileError(f"Audio file not found: {audio_path}")

        if audio_path.suffix.lower() not in [".mp3", ".wav", ".m4a", ".ogg", ".flac"]:
            raise AudioFileError(f"Unsupported audio format: {audio_path.suffix}")

        self.logger.info(f"Starting transcription for: {audio_path}")
        model = self._load_model()

        try:
            # Transcribe with language detection per segment
            segments_list, info = model.transcribe(
                str(audio_path),
                language=language,
                task=task,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                word_timestamps=False,
            )

            # Process segments
            transcript_segments = []
            full_text_parts = []
            detected_languages = set()

            for seg_id, segment in enumerate(segments_list):
                # Detect language for each segment if not specified
                seg_language = language or self._detect_segment_language(segment.text)
                detected_languages.add(seg_language)

                transcript_segment = Segment(
                    id=seg_id,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    language=seg_language,
                )
                transcript_segments.append(transcript_segment)
                full_text_parts.append(segment.text.strip())

            audio_duration = info.duration if hasattr(info, "duration") else 0.0

            result = TranscriptResult(
                segments=transcript_segments,
                full_text=" ".join(full_text_parts),
                detected_languages=sorted(list(detected_languages)),
                audio_duration=audio_duration,
            )

            self.logger.info(
                f"Transcription completed: {len(transcript_segments)} segments, "
                f"languages: {result.detected_languages}"
            )
            return result

        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {e}") from e

    def _detect_segment_language(self, text: str) -> str:
        """
        Simple heuristic to detect if segment is Chinese or English.

        Args:
            text: Text segment

        Returns:
            'zh' for Chinese, 'en' for English
        """
        # Count Chinese characters (Unicode range)
        chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        total_chars = len(text.replace(" ", ""))

        if total_chars == 0:
            return "en"

        # If more than 30% Chinese characters, consider it Chinese
        chinese_ratio = chinese_chars / total_chars
        return "zh" if chinese_ratio > 0.3 else "en"
