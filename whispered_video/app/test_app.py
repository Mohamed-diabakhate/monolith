#!/usr/bin/env python3
"""
Simple test script to verify the refactored application components
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from app import config, utils, transcriber, downloader, main
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.config import MODEL_CONFIGS, DEFAULT_MODELS, TRANSCRIPTS_DIR
        
        # Test model configs
        assert "medium" in MODEL_CONFIGS
        assert "youtube" in DEFAULT_MODELS
        assert "twitter" in DEFAULT_MODELS
        
        # Test directory creation
        assert TRANSCRIPTS_DIR.exists() or TRANSCRIPTS_DIR.parent.exists()
        
        print("✅ Configuration loaded successfully")
        print(f"   Available models: {list(MODEL_CONFIGS.keys())}")
        print(f"   Default models: {DEFAULT_MODELS}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\n🛠️ Testing utility functions...")
    
    try:
        from app.utils import sanitize_filename, format_timestamp
        
        # Test filename sanitization
        test_filename = "test<>:\"/\\|?*.txt"
        sanitized = sanitize_filename(test_filename)
        assert "<>" not in sanitized
        assert ":" not in sanitized
        print("✅ Filename sanitization works")
        
        # Test timestamp formatting
        timestamp = format_timestamp(125.5)
        assert timestamp == "02:05.500"
        print("✅ Timestamp formatting works")
        
        return True
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False

def test_downloader():
    """Test downloader initialization"""
    print("\n📥 Testing downloader...")
    
    try:
        from app.downloader import VideoDownloader
        
        downloader = VideoDownloader()
        
        # Test platform detection
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        twitter_url = "https://twitter.com/username/status/1234567890123456789"
        
        assert downloader.detect_platform(youtube_url) == "youtube"
        assert downloader.detect_platform(twitter_url) == "twitter"
        print("✅ Platform detection works")
        
        # Test URL validation
        assert downloader.validate_url(youtube_url)
        assert downloader.validate_url(twitter_url)
        assert not downloader.validate_url("https://example.com")
        print("✅ URL validation works")
        
        return True
    except Exception as e:
        print(f"❌ Downloader test failed: {e}")
        return False

def test_transcriber():
    """Test transcriber initialization"""
    print("\n🎵 Testing transcriber...")
    
    try:
        from app.transcriber import Transcriber
        
        # Test transcriber initialization
        transcriber = Transcriber(model_size="tiny", device="cpu")
        assert transcriber.model_size == "tiny"
        assert transcriber.device == "cpu"
        print("✅ Transcriber initialization works")
        
        # Test invalid model size
        try:
            Transcriber(model_size="invalid")
            print("❌ Should have raised ValueError for invalid model")
            return False
        except ValueError:
            print("✅ Invalid model size properly rejected")
        
        return True
    except Exception as e:
        print(f"❌ Transcriber test failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        ("torch", "PyTorch"),
        ("faster_whisper", "faster-whisper"),
        ("yt_dlp", "yt-dlp"),
        ("psutil", "psutil"),
        ("tqdm", "tqdm")
    ]
    
    missing = []
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            missing.append(name)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    else:
        print("✅ All dependencies available")
        return True

def main():
    """Run all tests"""
    print("🧪 Testing Whispered Video Transcription App")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_utils,
        test_downloader,
        test_transcriber,
        test_dependencies
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 