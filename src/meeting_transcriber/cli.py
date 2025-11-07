"""Command-line interface for meeting transcriber."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.config import get_settings
from .core.exceptions import MeetingTranscriberException
from .core.logging_config import get_logger
from .services.detailed_notes import DetailedNotesService
from .services.summarization import SummarizationService
from .services.transcription import TranscriptionService

app = typer.Typer(
    name="meeting-transcriber",
    help="AI-powered meeting transcription and summarization",
    add_completion=False,
)
console = Console()


@app.command()
def transcribe(
    audio_file: Path = typer.Argument(
        ..., help="Path to audio file (MP3, WAV, M4A, OGG, FLAC)", exists=True
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory (default: ./output)"
    ),
    language: Optional[str] = typer.Option(
        None, "--language", "-l", help="Language code (en, zh, etc.) or auto-detect if not specified"
    ),
    model: str = typer.Option(
        "gpt-4o-mini", "--model", "-m", help="OpenAI model for summarization/notes"
    ),
    skip_summary: bool = typer.Option(
        False, "--skip-summary", help="Skip LLM summarization, only transcribe"
    ),
    detailed_notes: bool = typer.Option(
        False,
        "--detailed-notes",
        help="Generate detailed notes instead of summary (preserves all details)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """
    Transcribe audio file and generate structured meeting summary or detailed notes.

    Examples:
        meeting-transcriber transcribe meeting.mp3
        meeting-transcriber transcribe meeting.wav -o ./results
        meeting-transcriber transcribe meeting.mp3 -l zh --skip-summary
        meeting-transcriber transcribe meeting.mp3 --detailed-notes
        meeting-transcriber transcribe meeting.mp3 --detailed-notes -m gpt-4o
    """
    logger = get_logger(__name__, level="DEBUG" if verbose else "INFO")

    try:
        # Load settings
        settings = get_settings()
        if output_dir:
            settings.output_dir = output_dir
            settings.output_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"\n[bold cyan]Meeting Transcriber[/bold cyan]")
        console.print(f"Audio file: [green]{audio_file}[/green]")
        console.print(f"Output directory: [green]{settings.output_dir}[/green]\n")

        # Initialize services
        transcription_service = TranscriptionService(settings)
        summarization_service = SummarizationService(settings) if not skip_summary else None
        detailed_notes_service = DetailedNotesService(settings) if detailed_notes else None

        # Transcription
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Transcribing audio with Whisper {settings.whisper_model}...",
                total=None,
            )

            transcript = transcription_service.transcribe(
                audio_path=audio_file, language=language
            )

            progress.update(task, completed=True)
            console.print(
                f"[green]✓[/green] Transcription completed: "
                f"{len(transcript.segments)} segments, "
                f"languages: {', '.join(transcript.detected_languages)}"
            )

        # Save transcript
        base_name = audio_file.stem
        transcript_path = settings.output_dir / f"{base_name}_transcript.txt"
        transcript_path.write_text(transcript.to_text(), encoding="utf-8")
        console.print(f"[green]✓[/green] Transcript saved: [blue]{transcript_path}[/blue]")

        # Detailed Notes Generation
        if detailed_notes and detailed_notes_service:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Generating detailed meeting notes with {model}...", total=None
                )

                notes = detailed_notes_service.generate_detailed_notes(
                    transcript, model=model
                )

                progress.update(task, completed=True)
                console.print("[green]✓[/green] Detailed notes generation completed")

            # Save detailed notes
            notes_path = settings.output_dir / f"{base_name}_detailed_notes.md"
            notes_path.write_text(notes.to_markdown(), encoding="utf-8")
            console.print(f"[green]✓[/green] Detailed notes saved: [blue]{notes_path}[/blue]")

        # Summarization (only if not using detailed notes)
        elif not skip_summary and summarization_service:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Generating structured summary with {model}...", total=None
                )

                summary = summarization_service.summarize(transcript, model=model)

                progress.update(task, completed=True)
                console.print("[green]✓[/green] Summarization completed")

            # Save summary
            summary_path = settings.output_dir / f"{base_name}_summary.md"
            summary_path.write_text(summary.to_markdown(), encoding="utf-8")
            console.print(f"[green]✓[/green] Summary saved: [blue]{summary_path}[/blue]")

        console.print(f"\n[bold green]✓ Processing complete![/bold green]\n")

    except MeetingTranscriberException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.error(f"Application error: {e}", exc_info=verbose)
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"meeting-transcriber version [cyan]{__version__}[/cyan]")


if __name__ == "__main__":
    app()
