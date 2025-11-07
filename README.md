# Meeting Transcriber

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)

**AI-powered meeting transcription and summarization tool with GPU acceleration and multi-language support**

[Features](#features) • [Quick Start](#quick-start) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#development)

</div>

---

## About This Project

This is an enhanced fork of the [breadpowder/meeting-transcriber](https://github.com/breadpowder/meeting-transcriber) project, with improvements for audio recording, Docker configuration, and PulseAudio integration.

**What does it do?**

Convert your meeting recordings into professional transcripts and intelligent summaries with:
- 🎯 **GPU-accelerated transcription** using OpenAI's Whisper (large-v3 model)
- 🌏 **Bilingual support** for English and Mandarin Chinese with automatic language detection
- 🤖 **AI-powered outputs** with GPT-4o for summaries and detailed meeting notes
- 🐳 **One-command deployment** via Docker with NVIDIA GPU support
- 📝 **Multiple output formats** from quick summaries to comprehensive written notes

**Perfect for:**
- Technical teams needing accurate bilingual meeting records
- Project managers tracking decisions and action items
- Anyone wanting to preserve meeting details without manual note-taking

### Key Capabilities at a Glance

| Feature | Description |
|---------|-------------|
| 🎤 **Transcription** | GPU-accelerated Whisper (large-v3) ~10x realtime speed |
| 🌐 **Languages** | English & Mandarin Chinese with auto-detection |
| 📊 **Output Modes** | Raw transcript, AI summary, or detailed notes |
| 🚀 **Performance** | Process 30-min audio in ~3 minutes (16GB GPU) |
| 🐳 **Deployment** | One-command Docker setup with GPU support |
| 💾 **Audio Formats** | MP3, WAV, M4A, OGG, FLAC |

---

## Quick Demo

Here's what a typical workflow looks like:

```bash
# 1. Place your audio file
cp ~/Downloads/team-meeting.mp3 audio/

# 2. Run transcription (3 commands total)
./transcribe.sh audio/team-meeting.mp3

# 3. View results
ls output/
# team-meeting_transcript.txt
# team-meeting_summary.md
```

**That's it!** In ~3-5 minutes, you'll have:
- ✅ Complete transcript with timestamps and language tags
- ✅ AI-generated summary with action items and decisions
- ✅ Ready-to-share markdown files

---

## Features

- **High-Quality Transcription**: GPU-accelerated faster-whisper (large-v3 model)
- **Multi-Language Support**: Automatic phrase-level language detection for English and Chinese
- **AI-Powered Outputs**: Choose between two AI-powered output formats:
  - **Summary Mode**: Condensed meeting summary with key decisions, action items, and discussion topics
  - **Detailed Notes Mode**: Comprehensive written notes that preserve ALL meeting details (new!)
- **Simple Usage**: One-command transcription with Docker
- **Output Formats**:
  - Raw transcript (.txt) with timestamps and language tags
  - Structured summary (.md) - condensed highlights
  - Detailed notes (.md) - complete meeting notes preserving all information

## Quick Start

### Prerequisites

- Docker with NVIDIA Container Toolkit
- NVIDIA GPU (8GB+ VRAM recommended)
- OpenAI API key

### Setup (One-Time)

1. **Clone the repository:**
```bash
git clone https://github.com/breadpowder/meeting-transcriber.git
cd meeting-transcriber
```

2. **Create `.env` file:**
```bash
cat > .env << EOF
OPENAI_API_KEY=your_api_key_here
WHISPER_MODEL=large-v3
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
OUTPUT_DIR=./output
LOG_LEVEL=INFO
EOF
```

3. **Build Docker image:**
```bash
make docker-build
# Or: docker compose build
```

### Usage

**Simple way** (recommended):
```bash
./transcribe.sh meeting.mp3
```

**Direct Docker command:**
```bash
# Copy audio to audio/ directory first
mkdir -p audio
cp meeting.mp3 audio/

# Run transcription
docker compose run --rm meeting-transcriber transcribe /app/audio/meeting.mp3
```

**Using Makefile:**
```bash
make docker-run AUDIO=meeting.mp3
```

### Common Options

```bash
# Generate summary (default behavior)
./transcribe.sh meeting.mp3

# Generate detailed notes instead of summary (preserves ALL details)
./transcribe.sh meeting.mp3 --detailed-notes

# Transcription only (no AI processing)
./transcribe.sh meeting.mp3 --skip-summary

# Use GPT-4o for better quality
./transcribe.sh meeting.mp3 -m gpt-4o
./transcribe.sh meeting.mp3 --detailed-notes -m gpt-4o

# Force language (skip auto-detection)
./transcribe.sh meeting.mp3 -l en

# Verbose logging
./transcribe.sh meeting.mp3 -v

# Custom output directory
./transcribe.sh meeting.mp3 -o /app/output/custom
```

## Output Examples

### Transcript (output/meeting_transcript.txt)

```
================================================================================
MEETING TRANSCRIPT
================================================================================

[00:00:00 - 00:00:05] (en)
Hello everyone, welcome to today's meeting.

[00:00:05 - 00:00:10] (zh)
大家好，欢迎参加今天的会议。

[00:00:10 - 00:00:15] (en)
We need to discuss the project roadmap.
```

### Summary (output/meeting_summary.md)

```markdown
# Meeting Summary

## Overview
Team sync meeting to discuss Q1 project roadmap and deliverables.

## Key Decisions

### 1. Launch date set for March 15th
*Context: All teams confirmed readiness*

## Action Items

1. Update project documentation - **Assignee**: Alice - **Deadline**: Friday
2. Prepare deployment scripts - **Assignee**: Bob - **Deadline**: Next week

## Discussion Topics

### Project Timeline
Reviewed current progress and identified potential blockers...

**Key Points:**
- Backend development 80% complete
- UI design finalized
- Testing phase starts next week

## Next Steps
1. Schedule deployment dry run
2. Prepare release announcement
```

### Detailed Notes (output/meeting_detailed_notes.md)

**NEW!** When you need to preserve all meeting details instead of a condensed summary:

```markdown
# Detailed Meeting Notes

## Product Planning Session

**Date/Time**: January 2025

**Participants**:
- Product Team
- Engineering Lead
- Design Lead

**Key Topics**:
- Feature roadmap
- Technical architecture
- User experience design

---

## Meeting Content

### [00:00] Introduction and Agenda Overview

The team convened to discuss the upcoming product release and review the technical implementation strategy. The meeting focused on aligning cross-functional teams and establishing clear timelines for deliverables.

### [05:30] Technical Architecture Discussion

The engineering team presented the proposed system architecture, emphasizing scalability and maintainability. Key architectural decisions were reviewed, including database design, API structure, and frontend framework selection.

The discussion covered implementation details for core features, with particular attention to performance optimization and security considerations. The team agreed on adopting industry best practices and established coding standards.

### [18:45] User Experience and Design Review

The design team shared mockups and prototypes, highlighting user flows and interaction patterns. Feedback was collected regarding accessibility requirements and responsive design approaches.

Discussion points included navigation structure, visual design consistency, and user feedback integration strategies. The team emphasized the importance of user testing throughout the development process.

### [28:20] Timeline and Next Steps

Project milestones were established with clear deliverables and deadlines. The team identified dependencies and potential blockers, agreeing on mitigation strategies.

Action items were assigned to respective teams with follow-up meetings scheduled for progress reviews.

[Complete meeting notes continue with full context and details...]
```

**Key Difference:**
- **Summary**: Condenses 30 minutes → 2-3 pages of highlights
- **Detailed Notes**: Transforms 30 minutes → 10-15 pages of complete written notes

## Documentation

### Configuration

Edit `.env` to customize settings:

```bash
# OpenAI API
OPENAI_API_KEY=your_api_key_here

# Whisper Model (tiny, base, small, medium, large-v3)
WHISPER_MODEL=large-v3          # Best quality for 16GB GPU
WHISPER_DEVICE=cuda             # Use GPU
WHISPER_COMPUTE_TYPE=float16    # Balanced precision

# Application
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

**For different GPUs:**

| GPU VRAM | Model | Compute Type |
|----------|-------|--------------|
| 8GB | medium | int8 |
| 12GB | large-v3 | int8 |
| 16GB+ | large-v3 | float16 |

## Performance

With 16GB GPU and large-v3 model:
- **Transcription**: ~10x realtime (30-min audio in ~3 minutes)
- **Summarization**: ~10-30 seconds
- **Memory**: ~8-10GB VRAM

## Supported Audio Formats

MP3, WAV, M4A, OGG, FLAC

## FAQ

### Q: Do I need a GPU to use this tool?
**A:** Yes, this tool is optimized for NVIDIA GPUs. For CPU-only usage, you'll need to modify the configuration, but performance will be significantly slower (~1x realtime vs ~10x with GPU).

### Q: How much does it cost to use?
**A:** The OpenAI API usage is the main cost. Using gpt-4o-mini, a typical 30-minute meeting costs approximately $0.10-0.20 for summarization. Transcription is free (runs locally on your GPU).

### Q: Can I use other languages besides English and Chinese?
**A:** The Whisper model supports 100+ languages, but the current implementation is optimized for English/Mandarin. You can modify `src/meeting_transcriber/services/transcription.py` to support additional languages.

### Q: Can I run this without Docker?
**A:** Yes, see [Direct Python Usage](#direct-python-usage-without-docker) section. However, Docker is recommended as it includes all GPU libraries pre-configured.

### Q: How accurate is the transcription?
**A:** With the large-v3 model, expect 90-95% accuracy for clear audio. Accuracy depends on audio quality, accents, and technical terminology.

---

## Troubleshooting

### Docker Build Fails

```bash
# Clean and rebuild
docker system prune -a
docker compose build --no-cache
```

### GPU Not Detected

```bash
# Test NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi

# If this fails, reinstall NVIDIA Container Toolkit:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Out of GPU Memory

Edit `.env` to use smaller model:
```bash
WHISPER_MODEL=medium
WHISPER_COMPUTE_TYPE=int8
```

### OpenAI API Errors

- Check your API key is valid
- Verify you have API credits
- Use `gpt-4o-mini` instead of `gpt-4o` for lower costs
- Add `--skip-summary` to transcribe without OpenAI

## Project Structure

```
speech-to-text/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .env                         # Configuration
├── transcribe.sh                # Simple usage script
├── docker_test.sh               # Test script
├── Dockerfile                   # Docker build
├── docker-compose.yml           # Docker service
├── Makefile                     # Development commands
├── pyproject.toml               # Python dependencies
│
├── src/                         # Application code
│   └── meeting_transcriber/
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration
│       ├── models.py            # Data models
│       ├── core/                # Core utilities
│       └── services/            # Business logic
│           ├── transcription.py # Whisper transcription
│           └── summarization.py # OpenAI summarization
│
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── acceptance/              # End-to-end tests
│
├── audio/                       # Input: place audio files here
├── output/                      # Output: transcripts & summaries
├── models/                      # Cached Whisper models
└── venv/                        # Python virtual environment
```

## Development

### Setup Development Environment

```bash
# Install dependencies
make dev-install

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean
```

### Run Tests

```bash
# All tests with coverage
pytest --cov=meeting_transcriber --cov-report=html

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

### Docker Commands

```bash
# Build image
make docker-build

# Run transcription
make docker-run AUDIO=meeting.mp3

# Open shell in container
make docker-shell
```

## Advanced Usage

### Direct Python Usage (Without Docker)

If you prefer to run without Docker (requires local GPU setup):

```bash
# Install dependencies
pip install uv
uv pip install -e ".[dev]"

# Run transcription
meeting-transcriber transcribe meeting.mp3
```

**Note:** Docker is recommended as it includes all GPU libraries (CUDA, cuDNN) pre-configured.

### Batch Processing

```bash
# Process multiple files
for file in audio/*.mp3; do
    ./transcribe.sh "$file"
done
```

### Custom Docker Compose Commands

```bash
# Run with custom options
docker compose run --rm meeting-transcriber transcribe /app/audio/meeting.mp3 \
    --skip-summary \
    -o /app/output/custom \
    -v

# Check GPU availability
docker compose run --rm meeting-transcriber /bin/bash -c "nvidia-smi"
```

## Technology Stack

- **Speech-to-Text**: faster-whisper (optimized Whisper implementation)
- **AI Summarization**: OpenAI GPT-4o-mini / GPT-4o
- **Language Support**: English, Mandarin Chinese (auto-detected at phrase level)
- **GPU**: CUDA 12.3.2 with cuDNN 9
- **Container**: Docker with NVIDIA Container Toolkit
- **Python**: 3.11+

## License

MIT License - see LICENSE file for details

## Enhancements in This Fork

This enhanced version includes several improvements over the original project:

- **Audio Recording Integration**: Added support for live audio recording with PulseAudio
- **Docker Permission Fixes**: Resolved PulseAudio authentication and permission issues in Docker containers
- **Enhanced Installation**: Automated installation scripts for recorder setup (`install_recorder.sh`)
- **Recording Script**: Simple `record.sh` script for capturing audio directly
- **Improved Documentation**: Comprehensive installation guide and troubleshooting steps
- **Bug Fixes**: Fixed default audio source resolution and TTY handling in containerized environments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Reporting Issues

If you encounter any problems:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing [GitHub Issues](https://github.com/breadpowder/meeting-transcriber/issues)
3. Create a new issue with:
   - Your environment details (GPU, OS, Docker version)
   - Steps to reproduce the problem
   - Error messages and logs

## Support

- **Documentation**: See [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for detailed setup instructions
- **Issues**: [GitHub Issues](https://github.com/breadpowder/meeting-transcriber/issues)
- **Discussions**: Share your use cases and ask questions in GitHub Discussions

## Acknowledgments

This project builds upon excellent open-source technologies:

- **Original Project**: [breadpowder/meeting-transcriber](https://github.com/breadpowder/meeting-transcriber)
- **Speech Recognition**: [OpenAI Whisper](https://github.com/openai/whisper) for state-of-the-art speech-to-text
- **Optimized Inference**: [faster-whisper](https://github.com/guillaumekln/faster-whisper) for GPU-accelerated transcription
- **AI Summarization**: [OpenAI GPT](https://platform.openai.com/) for intelligent meeting summaries

Special thanks to the open-source community for making these powerful tools accessible.

---

## Show Your Support

If you find this project helpful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs and requesting features
- 🤝 Contributing improvements
- 📢 Sharing with others who might benefit

Made with ❤️ by the community
