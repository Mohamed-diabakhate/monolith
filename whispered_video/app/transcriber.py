"""
Core transcription engine for the Whispered Video Transcription App
"""

import os
import time
import sys
from typing import Tuple, Dict, Optional
from pathlib import Path

from faster_whisper import WhisperModel
from tqdm import tqdm

from config import (
    MODEL_CONFIGS, 
    DEVICE_CONFIGS, 
    TRANSCRIPTION_SETTINGS,
    CLOUD_RUN_RESOURCES,
    CLOUD_RUN_PRICING,
    ENV_VARS
)
from utils import (
    detect_best_device,
    get_system_metrics,
    calculate_cloud_run_cost,
    format_timestamp,
    create_output_paths,
    get_file_info
)


class Transcriber:
    """
    Main transcription engine using faster-whisper
    """
    
    def __init__(self, model_size: str = "medium", device: str = "auto"):
        """
        Initialize the transcriber
        
        Args:
            model_size: Model size to use
            device: Device to use (auto, mps, cpu)
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self.device_config = None
        
        # Validate model size
        if model_size not in MODEL_CONFIGS:
            raise ValueError(f"Invalid model size: {model_size}. Available: {list(MODEL_CONFIGS.keys())}")
        
        print(f"🧠 Initializing transcriber with model: {model_size}")
        print(f"📊 Model description: {MODEL_CONFIGS[model_size]['description']}")
        print(f"🎯 Recommended for: {MODEL_CONFIGS[model_size]['recommended_for']}")
    
    def _initialize_model(self) -> None:
        """Initialize the Whisper model"""
        if self.model is not None:
            return
        
        print("🔧 Initializing transcription pipeline...")
        
        # Detect best device configuration
        if self.device == "auto":
            device, compute_type = detect_best_device()
        elif self.device == "mps":
            device, compute_type = "mps", "float16"
        elif self.device == "cpu":
            device, compute_type = "cpu", "int8"
        else:
            raise ValueError(f"Invalid device: {self.device}")
        
        self.device_config = {
            "device": device,
            "compute_type": compute_type,
            "cpu_threads": ENV_VARS["CPU_THREADS"]
        }
        
        if device == "mps":
            print("🚀 Using GPU acceleration with Apple Metal Performance Shaders (MPS)")
        else:
            print("⚡ Using CPU with Apple Silicon optimizations")
        
        print("🔄 Initializing model...")
        print("   📦 Loading model weights...")
        print("   🔧 Configuring compute settings...")
        
        model_start_time = time.time()
        
        # Initialize model with optimized settings
        self.model = WhisperModel(
            self.model_size,
            device=device,
            compute_type=compute_type,
            cpu_threads=self.device_config["cpu_threads"],
            num_workers=1  # Single worker for better memory management
        )
        
        model_load_time = time.time() - model_start_time
        print(f"✅ Model loaded successfully in {model_load_time:.1f} seconds")
        print("   🎯 Model ready for transcription")
    
    def transcribe(
        self, 
        audio_file: str, 
        output_dir: str,
        total_service_runtime: Optional[float] = None
    ) -> Tuple[str, float]:
        """
        Transcribe audio file
        
        Args:
            audio_file: Path to audio file
            output_dir: Output directory for transcripts
            total_service_runtime: Total service runtime for cost calculation
            
        Returns:
            Tuple of (transcript_file_path, processing_duration)
        """
        # Validate input file
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Get file information
        file_info = get_file_info(audio_file)
        print(f"📄 Processing file: {file_info['name']} ({file_info['size_mb']} MB)")
        
        # Initialize model if not already done
        self._initialize_model()
        
        # Start timing
        start_time = time.time()
        
        # Get initial system metrics
        print("📊 Measuring system resources...")
        initial_cpu, initial_memory = get_system_metrics()
        print(f"   CPU Usage: {initial_cpu:.1f}%")
        print(f"   Memory Usage: {initial_memory:.2f} GB")
        
        # Transcribe audio
        print("🎵 Processing audio with faster-whisper...")
        print("   🔍 Analyzing audio characteristics...")
        print("   🎧 Extracting audio features...")
        
        transcription_start_time = time.time()
        
        segments, info = self.model.transcribe(
            audio_file,
            **TRANSCRIPTION_SETTINGS
        )
        
        transcription_time = time.time() - transcription_start_time
        
        # Get final system metrics
        final_cpu, final_memory = get_system_metrics()
        avg_cpu = (initial_cpu + final_cpu) / 2
        peak_memory = max(initial_memory, final_memory)
        
        print(f"✅ Audio processing completed in {transcription_time:.1f} seconds")
        print(f"📊 Final resource usage - CPU: {final_cpu:.1f}%, Memory: {final_memory:.2f} GB")
        print("   🎉 Audio analysis phase completed")
        
        # Calculate total processing time
        end_time = time.time()
        duration = end_time - start_time
        
        # Use total service runtime if provided, otherwise use internal duration
        service_runtime = total_service_runtime if total_service_runtime is not None else duration
        
        # Print timing breakdown
        self._print_timing_breakdown(start_time, transcription_start_time, transcription_time, duration, service_runtime)
        
        # Calculate costs
        cost_data = self._calculate_costs(service_runtime, info.duration)
        
        # Create output files
        transcript_file, summary_file = self._create_output_files(
            audio_file, output_dir, segments, info, duration, service_runtime, 
            avg_cpu, peak_memory, cost_data
        )
        
        # Print final summary
        self._print_final_summary(transcript_file, info, cost_data)
        
        return transcript_file, duration
    
    def _print_timing_breakdown(
        self, 
        start_time: float, 
        transcription_start_time: float, 
        transcription_time: float, 
        duration: float, 
        service_runtime: float
    ) -> None:
        """Print detailed timing breakdown"""
        model_load_time = transcription_start_time - start_time
        post_processing_time = duration - model_load_time - transcription_time
        
        print(f"📊 TIMING BREAKDOWN:")
        print(f"   ⏱️  Model loading: {model_load_time:.1f} seconds")
        print(f"   ⏱️  Transcription: {transcription_time:.1f} seconds")
        print(f"   ⏱️  Post-processing: {post_processing_time:.1f} seconds")
        print(f"   ⏱️  Python script runtime: {duration:.1f} seconds")
        if service_runtime != duration:
            print(f"   ⏱️  Total service runtime: {service_runtime:.1f} seconds")
        print("   📈 Performance metrics calculated")
    
    def _calculate_costs(self, service_runtime: float, audio_duration: float) -> Dict[str, float]:
        """Calculate Cloud Run costs"""
        print("💰 Calculating Cloud Run costs for total service runtime...")
        print("   🔢 Computing resource costs...")
        
        try:
            cost_data = calculate_cloud_run_cost(
                service_runtime,
                CLOUD_RUN_RESOURCES["cpu_cores"],
                CLOUD_RUN_RESOURCES["memory_gb"],
                audio_duration
            )
            print(f"   Audio duration: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
            print(f"   Total service runtime: {service_runtime:.1f} seconds")
            print(f"   Cloud Run configuration: {CLOUD_RUN_RESOURCES['cpu_cores']}vCPU, {CLOUD_RUN_RESOURCES['memory_gb']}GB RAM")
            print(f"   Cost calculation based on allocated resources for total service runtime")
            print("   💰 Cost analysis completed")
            return cost_data
        except Exception as e:
            print(f"Warning: Cost calculation failed: {e}")
            # Return fallback cost data
            return {
                'cpu_cost': 0.0,
                'memory_cost': 0.0,
                'request_cost': 0.0000004,
                'total_cost': 0.0000004,
                'cost_per_minute': 0.0,
                'cost_40min': 0.0,
                'processing_time_seconds': service_runtime,
                'audio_duration_seconds': audio_duration,
                'allocated_cpu_cores': CLOUD_RUN_RESOURCES["cpu_cores"],
                'allocated_memory_gb': CLOUD_RUN_RESOURCES["memory_gb"]
            }
    
    def _create_output_files(
        self,
        audio_file: str,
        output_dir: str,
        segments,
        info,
        duration: float,
        service_runtime: float,
        avg_cpu: float,
        peak_memory: float,
        cost_data: Dict[str, float]
    ) -> Tuple[str, str]:
        """Create transcript and summary output files"""
        print("📄 Writing clean transcript...")
        print("   📝 Creating transcript file...")
        
        # Create output paths
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        transcript_file, summary_file = create_output_paths(base_name, output_dir)
        
        # Write clean transcript
        self._write_transcript(transcript_file, audio_file, info, segments)
        
        # Write detailed summary
        print("📊 Writing detailed summary...")
        print("   📋 Creating summary file...")
        self._write_summary(
            summary_file, audio_file, info, segments, duration, service_runtime,
            avg_cpu, peak_memory, cost_data
        )
        
        return transcript_file, summary_file
    
    def _write_transcript(self, transcript_file: str, audio_file: str, info, segments) -> None:
        """Write clean transcript file in markdown format"""
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"# Transcript: {os.path.basename(audio_file)}\n\n")
            f.write(f"**Language:** {info.language} (confidence: {info.language_probability:.2f})\n\n")
            f.write(f"**Duration:** {info.duration:.2f} seconds\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Convert segments to list for progress tracking
            segments_list = list(segments)
            total_segments = len(segments_list)
            
            print(f"   📋 Writing {total_segments} segments to transcript...")
            print("   🔄 Processing segments...")
            
            for i, segment in enumerate(segments_list, 1):
                text = segment.text.strip()
                if text:
                    f.write(f"{text}\n\n")
                if i % 10 == 0 or i == total_segments:
                    progress = (i / total_segments) * 100
                    print(f"   📊 Progress: {i}/{total_segments} segments ({progress:.1f}%)")
            
            print("   ✅ Transcript file written successfully")
    
    def _write_summary(
        self,
        summary_file: str,
        audio_file: str,
        info,
        segments,
        duration: float,
        service_runtime: float,
        avg_cpu: float,
        peak_memory: float,
        cost_data: Dict[str, float]
    ) -> None:
        """Write detailed summary file in JSON format"""
        import json
        
        # Convert segments to list for processing
        segments_list = list(segments)
        segment_count = len(segments_list)
        total_words = 0
        
        # Process segments
        print("   📝 Processing detailed segment information...")
        processed_segments = []
        
        for i, segment in enumerate(segments_list, 1):
            start_time_str = format_timestamp(segment.start)
            end_time_str = format_timestamp(segment.end)
            segment_duration = segment.end - segment.start
            text = segment.text.strip()
            word_count = len(text.split())
            total_words += word_count
            
            segment_data = {
                "segment_number": i,
                "start_time": segment.start,
                "end_time": segment.end,
                "start_time_formatted": start_time_str,
                "end_time_formatted": end_time_str,
                "duration_seconds": segment_duration,
                "text": text,
                "word_count": word_count
            }
            
            # Add word-level timestamps if available
            if hasattr(segment, 'words') and segment.words:
                word_timestamps = []
                for word in segment.words:
                    word_timestamps.append({
                        "word": word.word,
                        "start_time": word.start,
                        "end_time": word.end,
                        "start_time_formatted": format_timestamp(word.start),
                        "end_time_formatted": format_timestamp(word.end)
                    })
                segment_data["word_timestamps"] = word_timestamps
            
            processed_segments.append(segment_data)
        
        print(f"   📊 Processed {segment_count} segments with {total_words} total words")
        
        # Create JSON structure
        summary_data = {
            "metadata": {
                "audio_file": os.path.basename(audio_file),
                "model_used": f"faster-whisper {self.model_size}",
                "device": f"Apple M2 Pro ({self.device_config['device'].upper()} with {self.device_config['compute_type']})",
                "compute_type": self.device_config['compute_type'],
                "cpu_threads": self.device_config['cpu_threads'],
                "language_detected": info.language,
                "language_confidence": info.language_probability,
                "audio_duration_seconds": info.duration,
                "generated_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "performance": {
                "total_segments": segment_count,
                "total_words": total_words,
                "average_words_per_segment": total_words / segment_count if segment_count > 0 else 0,
                "processing_speed_realtime": info.duration / duration if duration > 0 else 0,
                "python_script_runtime_seconds": duration,
                "total_service_runtime_seconds": service_runtime,
                "cloud_run_configuration": {
                    "cpu_cores": CLOUD_RUN_RESOURCES['cpu_cores'],
                    "memory_gb": CLOUD_RUN_RESOURCES['memory_gb']
                },
                "local_performance": {
                    "average_cpu_usage_percent": avg_cpu,
                    "peak_memory_usage_gb": peak_memory
                }
            },
            "cost_analysis": {
                "cpu_cost_usd": cost_data['cpu_cost'],
                "memory_cost_usd": cost_data['memory_cost'],
                "request_cost_usd": cost_data['request_cost'],
                "total_cost_usd": cost_data['total_cost'],
                "cost_per_minute_usd": cost_data['cost_per_minute'],
                "cost_40min_usd": cost_data['cost_40min'],
                "pricing_reference": {
                    "cpu_cost_per_vcpu_second": CLOUD_RUN_PRICING['cpu_cost_per_vcpu_second'],
                    "memory_cost_per_gib_second": CLOUD_RUN_PRICING['memory_cost_per_gib_second'],
                    "request_cost_per_million": CLOUD_RUN_PRICING['request_cost_per_million']
                }
            },
            "segments": processed_segments
        }
        
        # Write JSON file
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print("   ✅ Summary file written successfully in JSON format")
    

    
    def _print_final_summary(self, transcript_file: str, info, cost_data: Dict[str, float]) -> None:
        """Print final summary to console"""
        print("🎉 All processing completed!")
        print("✅ Transcription completed successfully!")
        print(f"📄 Clean transcript saved to: {transcript_file}")
        print(f"🌐 Detected language: {info.language} (confidence: {info.language_probability:.2f})")
        print(f"💰 Cloud Run cost estimate: ${cost_data['total_cost']:.6f}")
        print(f"📈 Cost per minute: ${cost_data['cost_per_minute']:.6f}") 