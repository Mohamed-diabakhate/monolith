"""
Configuration settings for the Whispered Video Transcription App
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
APP_DIR = BASE_DIR / "app"
DOWNLOADS_DIR = BASE_DIR / "downloads_cache"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

# Model configurations
MODEL_CONFIGS = {
    "tiny": {
        "size": "tiny",
        "description": "Fastest, least accurate",
        "recommended_for": "Quick tests, short videos"
    },
    "base": {
        "size": "base", 
        "description": "Fast, good for short content",
        "recommended_for": "Short videos, podcasts"
    },
    "small": {
        "size": "small",
        "description": "Good balance for Twitter/X",
        "recommended_for": "Twitter/X videos, short content"
    },
    "medium": {
        "size": "medium",
        "description": "Best balance for YouTube",
        "recommended_for": "YouTube videos, general use"
    },
    "large": {
        "size": "large",
        "description": "High accuracy, slower",
        "recommended_for": "Important content, high accuracy needed"
    },
    "large-v2": {
        "size": "large-v2",
        "description": "Improved large model",
        "recommended_for": "High accuracy requirements"
    },
    "large-v3": {
        "size": "large-v3",
        "description": "Latest large model",
        "recommended_for": "Best accuracy, longer processing time"
    }
}

# Default model sizes for different platforms
DEFAULT_MODELS = {
    "youtube": "medium",
    "twitter": "small",
    "general": "medium"
}

# Device and compute configurations
DEVICE_CONFIGS = {
    "mps": {
        "device": "mps",
        "compute_type": "float16",
        "description": "Apple Metal Performance Shaders (GPU)",
        "cpu_threads": 12
    },
    "cpu": {
        "device": "cpu", 
        "compute_type": "int8",
        "description": "CPU with Apple Silicon optimizations",
        "cpu_threads": 12
    }
}

# Transcription settings
TRANSCRIPTION_SETTINGS = {
    "beam_size": 5,
    "best_of": 5,
    "temperature": 0.0,
    "condition_on_previous_text": True,
    "initial_prompt": None,
    "word_timestamps": True,
    "vad_filter": True,
    "vad_parameters": {
        "min_silence_duration_ms": 500
    }
}

# Cloud Run cost calculation constants
CLOUD_RUN_PRICING = {
    "cpu_cost_per_vcpu_second": 0.00002400,
    "memory_cost_per_gib_second": 0.00000250,
    "request_cost_per_million": 0.40
}

# Default Cloud Run resource allocation
CLOUD_RUN_RESOURCES = {
    "cpu_cores": 2.0,
    "memory_gb": 4.0
}

# File extensions and formats
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".webm"]

# yt-dlp settings
YT_DLP_SETTINGS = {
    "format": "bestaudio/best",
    "extract_audio": True,
    "audio_format": "mp3",
    "audio_quality": "192K",
    "outtmpl": str(DOWNLOADS_DIR / "%(title)s.%(ext)s"),
    "quiet": False,
    "no_warnings": False,
    "ignoreerrors": False
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# Environment variables
ENV_VARS = {
    "MODEL_SIZE": os.getenv("MODEL_SIZE", "medium"),
    "DEVICE": os.getenv("DEVICE", "auto"),  # auto, mps, cpu
    "CPU_THREADS": int(os.getenv("CPU_THREADS", "12")),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "CLEANUP_TEMP_FILES": os.getenv("CLEANUP_TEMP_FILES", "true").lower() == "true"
} 