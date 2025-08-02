# Whispered Video Transcription App

A high-performance video transcription system optimized for Apple M2 Pro, supporting both YouTube and Twitter/X videos using `faster-whisper` and `yt-dlp`. Now with Docker support for easy deployment and local execution.

## 🚀 Features

- **Multi-Platform Support**: YouTube and Twitter/X video transcription
- **Apple M2 Pro Optimized**: Leverages Metal Performance Shaders (MPS) for GPU acceleration
- **Fast Processing**: Uses `faster-whisper` with optimized settings
- **Cost Analysis**: Cloud Run deployment cost estimation
- **Markdown Transcripts**: Clean, readable transcript output in markdown format
- **JSON Summaries**: Structured, machine-readable summary data in JSON format
- **Docker Support**: Easy containerized deployment
- **Modular Architecture**: Clean, maintainable Python package structure
- **Automatic Cleanup**: Removes temporary files after processing

## 📋 Prerequisites

### For Local Development

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.9+
- Virtual environment (recommended)

### For Docker

- Docker Desktop
- Docker Compose (optional)

## 🛠️ Installation

### Option 1: Local Development

1. **Clone and setup environment:**

```bash
# Activate virtual environment
source activate_env.sh

# Or manually activate
source faster_whisper_env/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Check dependencies:**

```bash
python -m app.main --check-deps
```

### Option 2: Docker (Recommended)

1. **Build the Docker image:**

```bash
cd app
./docker-run.sh build
```

2. **Verify installation:**

```bash
./docker-run.sh run --help
```

## 🎯 Usage

### Local Development

#### Transcribe YouTube Videos

```bash
python -m app.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Transcribe Twitter/X Videos

```bash
python -m app.main "https://twitter.com/username/status/TWEET_ID"
```

#### Transcribe Local Audio Files

```bash
python -m app.main --file audio.mp3
```

#### Advanced Options

```bash
# Use specific model
python -m app.main "https://youtube.com/watch?v=..." --model large

# Use CPU only
python -m app.main "https://youtube.com/watch?v=..." --device cpu

# Custom output directory
python -m app.main "https://youtube.com/watch?v=..." --output /path/to/output

# Keep temporary files
python -m app.main "https://youtube.com/watch?v=..." --no-cleanup
```

### Docker Usage

#### Quick Start

```bash
cd app

# Build the image (first time only)
./docker-run.sh build

# Transcribe YouTube video
./docker-run.sh run "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Transcribe Twitter video
./docker-run.sh run "https://twitter.com/username/status/1234567890123456789"

# Transcribe local audio file
./docker-run.sh transcribe "/path/to/audio.mp3"
```

#### Advanced Docker Commands

```bash
# Use specific model
./docker-run.sh run "https://youtube.com/watch?v=..." --model large

# Use CPU only
./docker-run.sh run "https://youtube.com/watch?v=..." --device cpu

# Open shell in container
./docker-run.sh shell

# View logs
./docker-run.sh logs

# Clean up
./docker-run.sh clean
```

#### Docker Compose (Alternative)

```bash
cd app

# Start services
docker-compose up -d

# Run transcription
docker-compose exec whispered-video python -m app.main "https://youtube.com/watch?v=..."

# Stop services
docker-compose down
```

## 📊 Output

Both local and Docker execution generate:

1. **Clean Transcript** (`transcripts/filename.md`)

   - Markdown formatted transcription
   - Clean, readable format with proper markdown syntax
   - Ready for analysis and documentation
   - Includes metadata header with language, duration, and generation timestamp

2. **Detailed Summary** (`transcripts/filename_summary.json`)
   - Structured JSON data for programmatic access
   - Complete segment-by-segment breakdown with timestamps
   - Performance metrics and cost analysis
   - Machine-readable format for further processing
   - Includes word-level timestamps when available

### Output Format Examples

#### Markdown Transcript (`filename.md`)

```markdown
# Transcript: video_title.mp3

**Language:** en (confidence: 0.95)

**Duration:** 120.5 seconds

**Generated:** 2024-01-01 12:00:00

---

This is the first segment of the transcript.

This is the second segment with more content.
```

#### JSON Summary (`filename_summary.json`)

```json
{
  "metadata": {
    "audio_file": "video_title.mp3",
    "model_used": "faster-whisper medium",
    "device": "Apple M2 Pro (MPS with float16)",
    "language_detected": "en",
    "language_confidence": 0.95,
    "audio_duration_seconds": 120.5
  },
  "performance": {
    "total_segments": 15,
    "total_words": 250,
    "processing_speed_realtime": 2.5
  },
  "cost_analysis": {
    "total_cost_usd": 0.0000033,
    "cost_per_minute_usd": 0.0000016
  },
  "segments": [
    {
      "segment_number": 1,
      "start_time": 0.0,
      "end_time": 10.0,
      "text": "This is the first segment.",
      "word_count": 6
    }
  ]
}
```

## 🔧 Configuration

### Model Sizes

- **YouTube**: Uses `medium` model (good balance of speed/accuracy)
- **Twitter**: Uses `small` model (optimized for short videos)

Available models: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`

### Environment Variables

```bash
# Model configuration
MODEL_SIZE=medium          # Model size to use
DEVICE=auto               # Device: auto, mps, cpu
CPU_THREADS=12            # Number of CPU threads

# Logging
LOG_LEVEL=INFO            # Log level: DEBUG, INFO, WARNING, ERROR

# Cleanup
CLEANUP_TEMP_FILES=true   # Whether to cleanup temporary files
```

### Performance Optimization

- **Apple M2 Pro**: 12 CPU threads, MPS GPU acceleration
- **Memory**: Optimized for 16GB RAM
- **Compute Type**: `float16` for GPU, `int8` for CPU fallback

## 💰 Cost Analysis

The system calculates Cloud Run deployment costs:

- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

**Typical costs:**

- 2-minute Twitter video: ~$0.0001
- 10-minute YouTube video: ~$0.0005
- 40-minute YouTube video: ~$0.002

## 🏗️ Architecture

```
app/
├── __init__.py           # Package initialization
├── config.py             # Configuration settings
├── utils.py              # Utility functions
├── transcriber.py        # Core transcription engine
├── downloader.py         # Video downloader
├── main.py               # Main application entry point
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── docker-run.sh         # Docker convenience script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Key Components

- **Transcriber**: Handles audio transcription using faster-whisper
- **Downloader**: Downloads videos from YouTube and Twitter using yt-dlp
- **Config**: Centralized configuration management
- **Utils**: Helper functions for device detection, cost calculation, etc.

## 🐛 Troubleshooting

### Common Issues

#### Twitter/X Issues

1. **Private/Protected Accounts**: Only public videos can be downloaded
2. **URL Format**: Try mobile URL format if standard fails
3. **Video Availability**: Ensure the video hasn't been deleted
4. **yt-dlp Updates**: Keep yt-dlp updated: `pip install --upgrade yt-dlp`

#### Docker Issues

1. **Permission Errors**: Ensure Docker has access to mounted volumes
2. **Memory Issues**: Increase Docker memory allocation for large models
3. **Network Issues**: Check Docker network connectivity

#### Local Development Issues

```bash
# Update yt-dlp if download fails
pip install --upgrade yt-dlp

# Check virtual environment
source faster_whisper_env/bin/activate

# Verify dependencies
python -m app.main --check-deps

# Check GPU availability
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

### Error Messages

- **"MPS backend failed"**: Falling back to CPU processing
- **"Download failed"**: Check URL validity and network connectivity
- **"Model not found"**: Verify model size parameter

## 🚀 Cloud Deployment

The system is optimized for Google Cloud Run deployment:

- **CPU**: 2 vCPU cores
- **Memory**: 4GB RAM
- **Runtime**: Python 3.9+
- **Scaling**: 0-1 instances (serverless)

### Docker for Cloud Deployment

```bash
# Build for cloud
docker build -t gcr.io/PROJECT_ID/whispered-video .

# Push to Google Container Registry
docker push gcr.io/PROJECT_ID/whispered-video

# Deploy to Cloud Run
gcloud run deploy whispered-video \
  --image gcr.io/PROJECT_ID/whispered-video \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --allow-unauthenticated
```

## 📈 Performance

**Apple M2 Pro (16GB RAM):**

- YouTube (10min): ~30-60 seconds
- Twitter (2min): ~10-20 seconds
- Processing speed: 2-4x real-time

**Cloud Run (2vCPU, 4GB):**

- YouTube (10min): ~60-120 seconds
- Twitter (2min): ~20-40 seconds
- Processing speed: 1-2x real-time

**Docker (Local):**

- Similar to local development performance
- Slight overhead from containerization

## 🔄 Development

### Adding New Features

1. Create feature branch
2. Add tests in `tests/` directory
3. Update documentation
4. Submit pull request

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Test with Docker
./docker-run.sh shell
python -m pytest tests/
```

### Code Style

```bash
# Format code (when black is added)
black app/

# Lint code (when flake8 is added)
flake8 app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with both YouTube and Twitter videos
4. Update documentation
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader
- [OpenAI Whisper](https://github.com/openai/whisper) - Original transcription model

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information
