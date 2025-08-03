#!/bin/bash

# Solana NFT Downloader Docker Deployment Script
set -e

echo "🚀 Solana NFT Downloader - Docker Deployment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        print_status "Created .env file from template. Please edit it with your configuration."
    else
        print_error "env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p output logs credentials monitor

# Set proper permissions
print_status "Setting directory permissions..."
chmod 755 output logs monitor
chmod 700 credentials

# Build the Docker image
print_status "Building Docker image..."
docker-compose build

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "Docker image built successfully!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Display usage instructions
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Google Cloud project ID"
echo "2. Place your service account key in credentials/service-account.json"
echo "3. Run the application:"
echo ""
echo "   # Download NFTs from a wallet"
echo "   docker-compose run --rm nft-downloader --wallet YOUR_WALLET_ADDRESS"
echo ""
echo "   # With custom output directory"
echo "   docker-compose run --rm nft-downloader --wallet YOUR_WALLET_ADDRESS --output /app/output/custom"
echo ""
echo "   # Validate configuration"
echo "   docker-compose run --rm nft-downloader --wallet YOUR_WALLET_ADDRESS --validate-only"
echo ""
echo "   # Show statistics"
echo "   docker-compose run --rm nft-downloader --wallet YOUR_WALLET_ADDRESS --stats"
echo ""
echo "🔧 Optional: Start monitoring interface"
echo "   docker-compose --profile monitor up -d"
echo ""
echo "📁 Output files will be saved to: ./output/"
echo "📝 Logs will be saved to: ./logs/"
echo "" 