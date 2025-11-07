# Makefile for Meeting Transcriber

.PHONY: help install dev-install test lint format clean docker-build docker-run docker-shell

help:
	@echo "Meeting Transcriber - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  install        Install package in production mode"
	@echo "  dev-install    Install package in development mode"
	@echo "  test           Run tests with coverage"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black"
	@echo "  clean          Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run transcription in Docker"
	@echo "  docker-shell   Open shell in Docker container"
	@echo ""

install:
	uv pip install -e .

dev-install:
	uv pip install -e ".[dev]"

test:
	pytest --cov=meeting_transcriber --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker compose build

docker-run:
	@echo "Usage: make docker-run AUDIO=path/to/audio.mp3"
	@if [ -z "$(AUDIO)" ]; then \
		echo "Error: AUDIO parameter required"; \
		exit 1; \
	fi
	docker compose run --rm meeting-transcriber transcribe /app/audio/$(notdir $(AUDIO))

docker-shell:
	docker compose run --rm meeting-transcriber /bin/bash
