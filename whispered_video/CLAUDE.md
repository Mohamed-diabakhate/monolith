# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Whispered Video is an AI-powered video transcription system that downloads and transcribes videos from YouTube and Twitter/X using faster-whisper and yt-dlp. It's optimized for Apple Silicon (M1/M2/M3) with Metal Performance Shaders acceleration and provides structured output in both Markdown and JSON formats.

## Development Commands

### Running the Application
```bash
# Transcribe YouTube video
python -m app.main "https://www.youtube.com/watch?v=VIDEO_ID"

# Transcribe Twitter/X video
python -m app.main "https://twitter.com/username/status/TWEET_ID"

# Transcribe local audio file
python -m app.main --file audio.mp3 --model medium

# Use specific model size (tiny, base, small, medium, large, large-v2, large-v3)
python -m app.main "URL" --model large

# Force CPU usage
python -m app.main "URL" --device cpu

# Check dependencies
python -m app.main --check-deps
```

### Docker Commands
```bash
# Build Docker image
cd app && ./docker-run.sh build

# Run with Docker
./docker-run.sh run "https://youtube.com/watch?v=..."

# Transcribe local file with Docker
./docker-run.sh transcribe "/path/to/audio.mp3"

# Open shell in container
./docker-run.sh shell

# Docker Compose alternative
docker-compose up -d
docker-compose exec whispered-video python -m app.main "URL"
```

### Testing
```bash
# Run basic tests
python app/test_app.py

# Test output format generation
python app/test_output_formats.py
```

## Architecture & Key Patterns

### Core Components
- **`app/main.py`**: Entry point with CLI interface and orchestration logic
- **`app/transcriber.py`**: Whisper model management and transcription engine
- **`app/downloader.py`**: Video downloading with yt-dlp, platform detection
- **`app/config.py`**: Centralized configuration, model settings, and paths
- **`app/utils.py`**: Helper functions for device detection, cost calculation, formatting

### Output Structure
The application generates two output formats for each transcription:
- **Markdown transcript** (`transcripts/filename.md`): Human-readable with metadata header
- **JSON summary** (`transcripts/filename_summary.json`): Machine-readable with segments, timestamps, performance metrics, and Cloud Run cost analysis

### Platform-Specific Model Selection
- **YouTube videos**: Default to `medium` model for balance of speed/accuracy
- **Twitter/X videos**: Default to `small` model for short content optimization
- Models auto-selected based on detected platform, overridable via `--model` flag

### Device Detection & Optimization
- Automatically detects Apple Silicon MPS availability
- Falls back to CPU with int8 quantization if MPS fails
- Configurable CPU threads (default: 12) for parallel processing

## Important Configuration

### Environment Variables
```bash
MODEL_SIZE=medium           # Default model size
DEVICE=auto                # auto, mps, or cpu
CPU_THREADS=12             # Number of CPU threads
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR
CLEANUP_TEMP_FILES=true   # Remove temporary downloads
```

### Directory Structure
- `downloads_cache/`: Temporary video downloads (auto-cleaned)
- `transcripts/`: Output directory for .md and .json files
- `input/`: Local audio files for processing (Docker volume)

### Docker Volume Mounts
- Host `../transcripts` → Container `/transcripts`
- Host `../downloads_cache` → Container `/downloads_cache`
- Host `../input` → Container `/app/input` (read-only)

## Dependencies & Requirements

### Core Dependencies
- `faster-whisper==0.10.0`: Optimized Whisper implementation
- `torch>=2.0.0`: PyTorch with MPS support for Apple Silicon
- `yt-dlp>=2025.7.21`: Video downloading from multiple platforms
- `psutil>=7.0.0`: System resource monitoring

### Platform Requirements
- Python 3.9+ required
- macOS with Apple Silicon for MPS acceleration
- 16GB RAM recommended for larger models
- Docker Desktop for containerized deployment