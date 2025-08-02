"""
Utility functions for the Whispered Video Transcription App
"""

import os
import time
import json
import psutil
import torch
from pathlib import Path
from typing import Dict, Tuple, Optional
from config import CLOUD_RUN_PRICING, CLOUD_RUN_RESOURCES


def detect_best_device() -> Tuple[str, str]:
    """
    Detect the best available device for faster-whisper
    
    Returns:
        Tuple[str, str]: (device, compute_type)
    """
    # Test MPS availability
    mps_available = torch.backends.mps.is_available() and torch.backends.mps.is_built()
    
    if mps_available:
        try:
            # Test if faster-whisper supports MPS
            from faster_whisper import WhisperModel
            test_model = WhisperModel("tiny", device="mps", compute_type="float16")
            print("✅ MPS backend is available and working")
            return "mps", "float16"
        except Exception as e:
            print(f"⚠️ MPS backend failed: {e}")
            print("🔄 Falling back to CPU with int8 optimization")
            return "cpu", "int8"
    else:
        print("⚠️ MPS backend not available")
        print("⚡ Using CPU with int8 optimization")
        return "cpu", "int8"


def get_system_metrics() -> Tuple[float, float]:
    """
    Get current system CPU and memory usage
    
    Returns:
        Tuple[float, float]: (cpu_percent, memory_gb)
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_gb = memory.used / (1024**3)  # Convert to GB
    return cpu_percent, memory_gb


def calculate_cloud_run_cost(
    processing_time_seconds: float,
    allocated_cpu_cores: float,
    allocated_memory_gb: float,
    audio_duration_seconds: float
) -> Dict[str, float]:
    """
    Calculate estimated Cloud Run costs for the entire service runtime
    
    Args:
        processing_time_seconds: Total processing time in seconds
        allocated_cpu_cores: Allocated vCPU cores
        allocated_memory_gb: Allocated memory in GB
        audio_duration_seconds: Audio duration in seconds
    
    Returns:
        Dict containing cost breakdown and estimates
    """
    # Ensure we don't have zero values that could cause division errors
    if processing_time_seconds <= 0:
        return {
            'cpu_cost': 0.0,
            'memory_cost': 0.0,
            'request_cost': CLOUD_RUN_PRICING['request_cost_per_million'] / 1000000,
            'total_cost': CLOUD_RUN_PRICING['request_cost_per_million'] / 1000000,
            'cost_per_minute': 0.0,
            'cost_40min': 0.0,
            'processing_time_seconds': processing_time_seconds,
            'audio_duration_seconds': audio_duration_seconds,
            'allocated_cpu_cores': allocated_cpu_cores,
            'allocated_memory_gb': allocated_memory_gb
        }
    
    try:
        # Calculate resource costs based on ALLOCATED RESOURCES for TOTAL SERVICE RUNTIME
        vcpu_seconds = processing_time_seconds * allocated_cpu_cores
        memory_seconds = processing_time_seconds * allocated_memory_gb
        
        cpu_cost = vcpu_seconds * CLOUD_RUN_PRICING['cpu_cost_per_vcpu_second']
        memory_cost = memory_seconds * CLOUD_RUN_PRICING['memory_cost_per_gib_second']
        request_cost = CLOUD_RUN_PRICING['request_cost_per_million'] / 1000000
        
        total_cost = cpu_cost + memory_cost + request_cost
        
        # Calculate cost per minute of audio (for comparison)
        audio_duration_minutes = max(audio_duration_seconds / 60, 0.1)
        cost_per_minute = total_cost / audio_duration_minutes
        
        # Calculate cost for 40-minute file (target use case)
        if audio_duration_seconds > 0:
            processing_time_ratio = processing_time_seconds / audio_duration_seconds
            estimated_40min_processing = 40 * 60 * processing_time_ratio
            estimated_40min_cost = (estimated_40min_processing * allocated_cpu_cores * 
                                  CLOUD_RUN_PRICING['cpu_cost_per_vcpu_second']) + \
                                 (estimated_40min_processing * allocated_memory_gb * 
                                  CLOUD_RUN_PRICING['memory_cost_per_gib_second']) + \
                                 request_cost
        else:
            estimated_40min_cost = 0.0
        
        return {
            'cpu_cost': cpu_cost,
            'memory_cost': memory_cost,
            'request_cost': request_cost,
            'total_cost': total_cost,
            'cost_per_minute': cost_per_minute,
            'cost_40min': estimated_40min_cost,
            'processing_time_seconds': processing_time_seconds,
            'audio_duration_seconds': audio_duration_seconds,
            'allocated_cpu_cores': allocated_cpu_cores,
            'allocated_memory_gb': allocated_memory_gb
        }
    except Exception as e:
        print(f"Error in cost calculation: {e}")
        # Return safe fallback values
        return {
            'cpu_cost': 0.0,
            'memory_cost': 0.0,
            'request_cost': CLOUD_RUN_PRICING['request_cost_per_million'] / 1000000,
            'total_cost': CLOUD_RUN_PRICING['request_cost_per_million'] / 1000000,
            'cost_per_minute': 0.0,
            'cost_40min': 0.0,
            'processing_time_seconds': processing_time_seconds,
            'audio_duration_seconds': audio_duration_seconds,
            'allocated_cpu_cores': allocated_cpu_cores,
            'allocated_memory_gb': allocated_memory_gb
        }


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp in MM:SS.mmm format
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def get_file_info(file_path: str) -> Dict[str, str]:
    """
    Get basic file information
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dict containing file information
    """
    path = Path(file_path)
    stat = path.stat()
    
    return {
        'name': path.name,
        'stem': path.stem,
        'suffix': path.suffix,
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created': time.ctime(stat.st_ctime),
        'modified': time.ctime(stat.st_mtime)
    }


def cleanup_temp_files(file_paths: list) -> None:
    """
    Clean up temporary files
    
    Args:
        file_paths: List of file paths to delete
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Cleaned up: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"⚠️ Failed to clean up {file_path}: {e}")


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that the file is a supported audio format
    
    Args:
        file_path: Path to the audio file
    
    Returns:
        True if valid, False otherwise
    """
    from config import SUPPORTED_AUDIO_FORMATS
    
    if not os.path.exists(file_path):
        return False
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in SUPPORTED_AUDIO_FORMATS


def create_output_paths(base_name: str, output_dir: str) -> Tuple[str, str]:
    """
    Create output file paths for transcript and summary
    
    Args:
        base_name: Base name for the files
        output_dir: Output directory
    
    Returns:
        Tuple of (transcript_path, summary_path)
    """
    sanitized_name = sanitize_filename(base_name)
    transcript_file = os.path.join(output_dir, f"{sanitized_name}.md")
    summary_file = os.path.join(output_dir, f"{sanitized_name}_summary.json")
    return transcript_file, summary_file 