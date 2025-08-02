#!/usr/bin/env python3
"""
Main application entry point for Whispered Video Transcription
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from config import DEFAULT_MODELS, TRANSCRIPTS_DIR, ENV_VARS
from downloader import VideoDownloader
from transcriber import Transcriber
from utils import validate_audio_file, cleanup_temp_files


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        ("torch", "PyTorch"),
        ("psutil", "psutil"),
        ("faster_whisper", "faster-whisper"),
        ("tqdm", "tqdm"),
        ("yt_dlp", "yt-dlp")
    ]
    
    missing_deps = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name} available")
        except ImportError:
            print(f"   ❌ {name} not found")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True


def transcribe_url(
    url: str,
    model_size: Optional[str] = None,
    device: str = "auto",
    output_dir: Optional[str] = None,
    cleanup: bool = True
) -> str:
    """
    Download and transcribe a video from URL
    
    Args:
        url: Video URL
        model_size: Model size to use (auto-detected if None)
        device: Device to use (auto, mps, cpu)
        output_dir: Output directory for transcripts
        cleanup: Whether to cleanup temporary files
        
    Returns:
        Path to the transcript file
    """
    start_time = time.time()
    downloaded_files = []
    
    try:
        # Initialize components
        downloader = VideoDownloader()
        output_dir = output_dir or str(TRANSCRIPTS_DIR)
        
        # Detect platform and set default model
        platform = downloader.detect_platform(url)
        if model_size is None:
            model_size = DEFAULT_MODELS.get(platform, "medium")
        
        print(f"🎯 Platform: {platform}")
        print(f"🧠 Model: {model_size}")
        print(f"🔧 Device: {device}")
        
        # Download video
        print("\n" + "="*60)
        print("📥 DOWNLOAD PHASE")
        print("="*60)
        audio_file = downloader.download_video(url, platform)
        downloaded_files.append(audio_file)
        
        # Transcribe audio
        print("\n" + "="*60)
        print("🎵 TRANSCRIPTION PHASE")
        print("="*60)
        transcriber = Transcriber(model_size=model_size, device=device)
        transcript_file, duration = transcriber.transcribe(
            audio_file, 
            output_dir,
            total_service_runtime=time.time() - start_time
        )
        
        print("\n" + "="*60)
        print("✅ PROCESSING COMPLETED")
        print("="*60)
        print(f"📄 Transcript: {transcript_file}")
        print(f"📊 Summary: {transcript_file.replace('.md', '_summary.json')}")
        print(f"⏱️  Total time: {duration:.1f} seconds")
        
        return transcript_file
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise
    finally:
        # Cleanup temporary files
        if cleanup and downloaded_files:
            print("\n🗑️ Cleaning up temporary files...")
            cleanup_temp_files(downloaded_files)


def transcribe_file(
    audio_file: str,
    model_size: str = "medium",
    device: str = "auto",
    output_dir: Optional[str] = None
) -> str:
    """
    Transcribe an existing audio file
    
    Args:
        audio_file: Path to audio file
        model_size: Model size to use
        device: Device to use (auto, mps, cpu)
        output_dir: Output directory for transcripts
        
    Returns:
        Path to the transcript file
    """
    # Validate input file
    if not validate_audio_file(audio_file):
        raise ValueError(f"Invalid audio file: {audio_file}")
    
    output_dir = output_dir or str(TRANSCRIPTS_DIR)
    
    print(f"🎵 Transcribing audio file: {os.path.basename(audio_file)}")
    print(f"🧠 Model: {model_size}")
    print(f"🔧 Device: {device}")
    
    # Transcribe
    transcriber = Transcriber(model_size=model_size, device=device)
    transcript_file, duration = transcriber.transcribe(audio_file, output_dir)
    
    print(f"\n✅ Transcription completed!")
    print(f"📄 Transcript: {transcript_file}")
    print(f"📊 Summary: {transcript_file.replace('.md', '_summary.json')}")
    print(f"⏱️  Processing time: {duration:.1f} seconds")
    
    return transcript_file


def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description="Whispered Video Transcription - Download and transcribe videos from YouTube and Twitter/X",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe YouTube video
  python -m app.main "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Transcribe Twitter video with specific model
  python -m app.main "https://twitter.com/username/status/1234567890123456789" --model large
  
  # Transcribe local audio file
  python -m app.main --file audio.mp3 --model medium
  
  # Use CPU only
  python -m app.main "https://youtube.com/watch?v=..." --device cpu
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "url",
        nargs="?",
        help="Video URL (YouTube or Twitter/X)"
    )
    input_group.add_argument(
        "--file", "-f",
        help="Path to local audio file"
    )
    
    # Model options
    parser.add_argument(
        "--model", "-m",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        default="medium",
        help="Model size to use (default: medium)"
    )
    
    # Device options
    parser.add_argument(
        "--device", "-d",
        choices=["auto", "mps", "cpu"],
        default="auto",
        help="Device to use (default: auto)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output directory for transcripts (default: transcripts/)"
    )
    
    # Other options
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't cleanup temporary files"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        if check_dependencies():
            print("✅ All dependencies are available")
            sys.exit(0)
        else:
            print("❌ Some dependencies are missing")
            sys.exit(1)
    
    # If no input provided and not checking deps, show help
    if not args.url and not args.file and not args.check_deps:
        parser.print_help()
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        if args.file:
            # Transcribe local file
            transcript_file = transcribe_file(
                args.file,
                model_size=args.model,
                device=args.device,
                output_dir=args.output
            )
        else:
            # Download and transcribe URL
            transcript_file = transcribe_url(
                args.url,
                model_size=args.model,
                device=args.device,
                output_dir=args.output,
                cleanup=not args.no_cleanup
            )
        
        print(f"\n🎉 SUCCESS: {transcript_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 