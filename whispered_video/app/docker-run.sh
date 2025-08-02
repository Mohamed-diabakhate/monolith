#!/bin/bash

# Whispered Video Transcription - Docker Runner Script
# This script provides convenient commands for running the application in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    echo "Whispered Video Transcription - Docker Runner"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  build                    Build the Docker image"
    echo "  run <url>                Download and transcribe a video URL"
    echo "  transcribe <file>        Transcribe a local audio file"
    echo "  shell                    Open a shell in the container"
    echo "  logs                     Show container logs"
    echo "  stop                     Stop the container"
    echo "  clean                    Clean up containers and images"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  $0 transcribe '/path/to/audio.mp3'"
    echo "  $0 run 'https://twitter.com/username/status/1234567890123456789' --model large"
    echo ""
}

# Function to build the Docker image
build_image() {
    print_info "Building Docker image..."
    cd "$(dirname "$0")"
    docker build -t whispered-video:latest -f Dockerfile ..
    print_success "Docker image built successfully"
}

# Function to run transcription from URL
run_url() {
    local url="$1"
    shift
    
    if [[ -z "$url" ]]; then
        print_error "URL is required"
        show_usage
        exit 1
    fi
    
    print_info "Starting transcription for URL: $url"
    cd "$(dirname "$0")"
    
    # Create necessary directories
    mkdir -p ../transcripts ../downloads_cache ../input
    
    # Run the container
    docker run --rm \
        -v "$(pwd)/../transcripts:/transcripts" \
        -v "$(pwd)/../downloads_cache:/downloads_cache" \
        -v "$(pwd)/../input:/app/input:ro" \
        whispered-video:latest \
        python main.py "$url" "$@"
    
    print_success "Transcription completed"
}

# Function to transcribe local file
transcribe_file() {
    local file="$1"
    shift
    
    if [[ -z "$file" ]]; then
        print_error "File path is required"
        show_usage
        exit 1
    fi
    
    if [[ ! -f "$file" ]]; then
        print_error "File not found: $file"
        exit 1
    fi
    
    print_info "Starting transcription for file: $file"
    cd "$(dirname "$0")"
    
    # Create necessary directories
    mkdir -p ../transcripts ../downloads_cache ../input
    
    # Copy file to input directory
    cp "$file" ../input/
    local filename=$(basename "$file")
    
    # Run the container
    docker run --rm \
        -v "$(pwd)/../transcripts:/transcripts" \
        -v "$(pwd)/../downloads_cache:/downloads_cache" \
        -v "$(pwd)/../input:/app/input:ro" \
        whispered-video:latest \
        python main.py --file "/app/input/$filename" "$@"
    
    print_success "Transcription completed"
}

# Function to open shell in container
open_shell() {
    print_info "Opening shell in container..."
    cd "$(dirname "$0")"
    docker run --rm -it \
        -v "$(pwd)/../transcripts:/transcripts" \
        -v "$(pwd)/../downloads_cache:/downloads_cache" \
        -v "$(pwd)/../input:/app/input" \
        whispered-video:latest \
        /bin/bash
}

# Function to show logs
show_logs() {
    print_info "Showing container logs..."
    docker logs whispered-video-app 2>/dev/null || print_warning "Container not running"
}

# Function to stop container
stop_container() {
    print_info "Stopping container..."
    docker stop whispered-video-app 2>/dev/null || print_warning "Container not running"
    print_success "Container stopped"
}

# Function to clean up
clean_up() {
    print_info "Cleaning up containers and images..."
    docker stop whispered-video-app 2>/dev/null || true
    docker rm whispered-video-app 2>/dev/null || true
    docker rmi whispered-video:latest 2>/dev/null || true
    print_success "Cleanup completed"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_url "${@:2}"
        ;;
    transcribe)
        transcribe_file "${@:2}"
        ;;
    shell)
        open_shell
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_container
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 