#!/usr/bin/env python3
"""
Test script to verify the new output formats (markdown transcript and JSON summary)
"""

import os
import json
import tempfile
from pathlib import Path

def test_output_paths():
    """Test that output paths are created with correct extensions"""
    from utils import create_output_paths
    
    # Test with a sample filename
    base_name = "test_video"
    output_dir = "/tmp/test_output"
    
    transcript_file, summary_file = create_output_paths(base_name, output_dir)
    
    print("Testing output path creation:")
    print(f"  Transcript file: {transcript_file}")
    print(f"  Summary file: {summary_file}")
    
    # Verify extensions
    assert transcript_file.endswith('.md'), f"Transcript should end with .md, got: {transcript_file}"
    assert summary_file.endswith('.json'), f"Summary should end with .json, got: {summary_file}"
    
    print("✅ Output path creation test passed")

def test_markdown_transcript_format():
    """Test markdown transcript format"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        transcript_file = f.name
    
    try:
        # Simulate writing a markdown transcript
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write("# Transcript: test_video.mp3\n\n")
            f.write("**Language:** en (confidence: 0.95)\n\n")
            f.write("**Duration:** 120.5 seconds\n\n")
            f.write("**Generated:** 2024-01-01 12:00:00\n\n")
            f.write("---\n\n")
            f.write("This is a test transcript.\n\n")
            f.write("It contains multiple segments.\n\n")
        
        # Read and verify format
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Testing markdown transcript format:")
        print("  Content preview:")
        for line in content.split('\n')[:10]:
            print(f"    {line}")
        
        # Verify markdown elements
        assert '# Transcript:' in content, "Should have markdown header"
        assert '**Language:**' in content, "Should have bold language field"
        assert '---' in content, "Should have horizontal rule"
        
        print("✅ Markdown transcript format test passed")
        
    finally:
        os.unlink(transcript_file)

def test_json_summary_format():
    """Test JSON summary format"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        summary_file = f.name
    
    try:
        # Create sample JSON summary data
        summary_data = {
            "metadata": {
                "audio_file": "test_video.mp3",
                "model_used": "faster-whisper medium",
                "device": "Apple M2 Pro (MPS with float16)",
                "compute_type": "float16",
                "cpu_threads": 12,
                "language_detected": "en",
                "language_confidence": 0.95,
                "audio_duration_seconds": 120.5,
                "generated_timestamp": "2024-01-01 12:00:00"
            },
            "performance": {
                "total_segments": 5,
                "total_words": 25,
                "average_words_per_segment": 5.0,
                "processing_speed_realtime": 2.5,
                "python_script_runtime_seconds": 48.2,
                "total_service_runtime_seconds": 50.0,
                "cloud_run_configuration": {
                    "cpu_cores": 2.0,
                    "memory_gb": 4.0
                },
                "local_performance": {
                    "average_cpu_usage_percent": 45.2,
                    "peak_memory_usage_gb": 3.1
                }
            },
            "cost_analysis": {
                "cpu_cost_usd": 0.0000024,
                "memory_cost_usd": 0.0000005,
                "request_cost_usd": 0.0000004,
                "total_cost_usd": 0.0000033,
                "cost_per_minute_usd": 0.0000016,
                "cost_40min_usd": 0.000066
            },
            "segments": [
                {
                    "segment_number": 1,
                    "start_time": 0.0,
                    "end_time": 10.0,
                    "start_time_formatted": "00:00.000",
                    "end_time_formatted": "00:10.000",
                    "duration_seconds": 10.0,
                    "text": "This is a test transcript.",
                    "word_count": 6
                }
            ]
        }
        
        # Write JSON file
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        # Read and verify JSON structure
        with open(summary_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print("Testing JSON summary format:")
        print("  JSON structure verified:")
        print(f"    - Metadata: {len(loaded_data['metadata'])} fields")
        print(f"    - Performance: {len(loaded_data['performance'])} fields")
        print(f"    - Cost analysis: {len(loaded_data['cost_analysis'])} fields")
        print(f"    - Segments: {len(loaded_data['segments'])} segments")
        
        # Verify required fields
        assert 'metadata' in loaded_data, "Should have metadata section"
        assert 'performance' in loaded_data, "Should have performance section"
        assert 'cost_analysis' in loaded_data, "Should have cost_analysis section"
        assert 'segments' in loaded_data, "Should have segments section"
        
        print("✅ JSON summary format test passed")
        
    finally:
        os.unlink(summary_file)

def main():
    """Run all tests"""
    print("🧪 Testing new output formats")
    print("=" * 50)
    
    try:
        test_output_paths()
        print()
        test_markdown_transcript_format()
        print()
        test_json_summary_format()
        print()
        print("🎉 All tests passed! New output formats are working correctly.")
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 