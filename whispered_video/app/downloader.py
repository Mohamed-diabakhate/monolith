"""
Video downloader module for YouTube and Twitter/X videos
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import yt_dlp

from config import YT_DLP_SETTINGS, DOWNLOADS_DIR, SUPPORTED_AUDIO_FORMATS
from utils import sanitize_filename, get_file_info


class VideoDownloader:
    """
    Download videos from YouTube and Twitter/X using yt-dlp
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the downloader
        
        Args:
            output_dir: Output directory for downloads (defaults to config)
        """
        self.output_dir = output_dir or str(DOWNLOADS_DIR)
        self.downloaded_files = []
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def detect_platform(self, url: str) -> str:
        """
        Detect the platform from the URL
        
        Args:
            url: Video URL
            
        Returns:
            Platform name (youtube, twitter, unknown)
        """
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ['youtube.com', 'youtu.be']):
            return 'youtube'
        elif any(domain in url_lower for domain in ['twitter.com', 'x.com', 'mobile.twitter.com']):
            return 'twitter'
        else:
            return 'unknown'
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is supported
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        platform = self.detect_platform(url)
        return platform in ['youtube', 'twitter']
    
    def download_video(self, url: str, platform: Optional[str] = None) -> str:
        """
        Download video and extract audio
        
        Args:
            url: Video URL
            platform: Platform (auto-detected if None)
            
        Returns:
            Path to the downloaded audio file
        """
        if not self.validate_url(url):
            raise ValueError(f"Unsupported URL: {url}")
        
        platform = platform or self.detect_platform(url)
        print(f"📥 Downloading from {platform.upper()}: {url}")
        
        # Configure yt-dlp options
        ydl_opts = self._get_ydl_options(platform)
        
        try:
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("🔍 Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                video_title = info.get('title', 'Unknown Title')
                print(f"📺 Video: {video_title}")
                
                # Download the video
                print("⬇️ Downloading and extracting audio...")
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = self._find_downloaded_file(video_title)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    file_info = get_file_info(downloaded_file)
                    print(f"✅ Download completed: {file_info['name']} ({file_info['size_mb']} MB)")
                    self.downloaded_files.append(downloaded_file)
                    return downloaded_file
                else:
                    raise FileNotFoundError("Downloaded file not found")
                    
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            raise
    
    def _get_ydl_options(self, platform: str) -> Dict[str, Any]:
        """
        Get yt-dlp options for the platform
        
        Args:
            platform: Platform name
            
        Returns:
            yt-dlp options dictionary
        """
        # Base options
        options = YT_DLP_SETTINGS.copy()
        
        # Platform-specific options
        if platform == 'youtube':
            options.update({
                'format': 'bestaudio/best',
                'extract_audio': True,
                'audio_format': 'mp3',
                'audio_quality': '192K',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif platform == 'twitter':
            options.update({
                'format': 'bestaudio/best',
                'extract_audio': True,
                'audio_format': 'mp3',
                'audio_quality': '192K',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # Twitter-specific options
                'cookiesfrombrowser': None,  # Use browser cookies if available
                'extractor_args': {
                    'twitter': {
                        'api': 'graphql',  # Use GraphQL API
                    }
                }
            })
        
        return options
    
    def _find_downloaded_file(self, video_title: str) -> Optional[str]:
        """
        Find the downloaded audio file
        
        Args:
            video_title: Original video title
            
        Returns:
            Path to the downloaded file or None
        """
        # Sanitize the title for filename matching
        sanitized_title = sanitize_filename(video_title)
        
        # Look for files in the output directory
        for file_path in Path(self.output_dir).glob("*.mp3"):
            if sanitized_title.lower() in file_path.stem.lower():
                return str(file_path)
        
        # If no exact match, return the most recent mp3 file
        mp3_files = list(Path(self.output_dir).glob("*.mp3"))
        if mp3_files:
            # Sort by modification time (newest first)
            mp3_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return str(mp3_files[0])
        
        return None
    
    def cleanup_downloads(self) -> None:
        """Clean up downloaded files"""
        for file_path in self.downloaded_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️ Failed to clean up {file_path}: {e}")
        
        self.downloaded_files.clear()


def download_and_extract_audio(url: str, output_dir: Optional[str] = None) -> str:
    """
    Convenience function to download and extract audio from a video URL
    
    Args:
        url: Video URL
        output_dir: Output directory (optional)
        
    Returns:
        Path to the extracted audio file
    """
    downloader = VideoDownloader(output_dir)
    return downloader.download_video(url)


def main():
    """Command line interface for the downloader"""
    if len(sys.argv) < 2:
        print("Usage: python downloader.py <video_url> [output_dir]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        downloader = VideoDownloader(output_dir)
        
        if not downloader.validate_url(url):
            print(f"❌ Unsupported URL: {url}")
            print("Supported platforms: YouTube, Twitter/X")
            sys.exit(1)
        
        platform = downloader.detect_platform(url)
        print(f"🎯 Detected platform: {platform}")
        
        audio_file = downloader.download_video(url, platform)
        print(f"✅ SUCCESS:{audio_file}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 