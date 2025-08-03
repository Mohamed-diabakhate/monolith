# Solana NFT Downloader

A comprehensive tool for downloading and managing Solana NFTs with enhanced Firestore integration.

## Features

- **Dual Mode Operation**: Basic local download mode and enhanced Firestore integration mode
- **Helius API Integration**: Uses Helius DAS API for reliable NFT data retrieval
- **Firestore Storage**: Store NFT metadata and data in Google Cloud Firestore
- **Image Download**: Download NFT images to local storage
- **Compressed NFT Support**: Handle both regular and compressed NFTs
- **Search & Statistics**: Advanced search and statistics capabilities
- **Docker Support**: Containerized deployment options

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Helius API Key** - Get from [Helius.dev](https://www.helius.dev/)
3. **Google Cloud Project** (for enhanced mode)

### Basic Installation

```bash
git clone <repository-url>
cd NFT_Gallery
pip install -r requirements.txt
```

### Environment Setup

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# Required: Helius API Key
HELIUS_API_KEY=your-helius-api-key

# Optional: Output directory
OUTPUT_DIR=~/Pictures/SolanaNFTs

# Enhanced mode: Google Cloud configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
FIRESTORE_DATABASE=develop  # Use "develop" database to avoid App Engine issues
```

### Basic Usage

```bash
# Download NFTs to local storage
python main.py --wallet YOUR_WALLET_ADDRESS

# Enhanced mode with Firestore integration
python main_enhanced.py --wallet YOUR_WALLET_ADDRESS --firestore-only
```

## Firestore Database Configuration

### Using the "develop" Database

The application is configured to use the "develop" database by default to avoid issues with disabled App Engine databases. This is especially important for projects that have App Engine disabled.

**Configuration Options:**

1. **Environment Variable:**

   ```bash
   export FIRESTORE_DATABASE=develop
   ```

2. **Command Line:**

   ```bash
   python main_enhanced.py --wallet YOUR_WALLET --database develop
   ```

3. **Environment File (.env):**
   ```bash
   FIRESTORE_DATABASE=develop
   ```

### Why Use "develop" Database?

- **Avoids App Engine Issues**: The default Firestore database is often linked to App Engine, which may be disabled
- **Clean Separation**: Keeps development data separate from production
- **Better Permissions**: Avoids complex App Engine permission requirements

### Creating the "develop" Database

If the "develop" database doesn't exist, you can create it:

```bash
gcloud firestore databases create --project=your-project-id --database=develop
```

## Enhanced Mode Features

### Firestore Image Download System

The enhanced mode now includes a comprehensive image download system that reads from Firestore documents and tracks download status:

#### Download Status Tracking

Each NFT document in Firestore includes download status fields:

- `download_status`: "pending", "downloading", "completed", "failed"
- `download_attempts`: Number of download attempts
- `download_error`: Error message if download failed
- `local_file_path`: Path to downloaded file
- `file_size`: Size of downloaded file in bytes
- `download_completed_at`: Timestamp when download completed
- `last_download_attempt`: Timestamp of last download attempt

#### Download Commands

```bash
# Download all pending images from Firestore
python main_enhanced.py --wallet YOUR_WALLET --download-images

# Download only pending images
python main_enhanced.py --wallet YOUR_WALLET --download-pending

# Retry failed downloads
python main_enhanced.py --wallet YOUR_WALLET --retry-failed

# Show download statistics
python main_enhanced.py --wallet YOUR_WALLET --download-stats

# Download with custom settings
python main_enhanced.py --wallet YOUR_WALLET --download-images --max-concurrent 10 --batch-size 100

# Download by specific status
python main_enhanced.py --wallet YOUR_WALLET --download-images --download-status pending
```

#### Download Features

- **Concurrent Downloads**: Configurable concurrent download limits
- **Batch Processing**: Process documents in configurable batches
- **Retry Logic**: Automatic retry of failed downloads
- **Progress Tracking**: Real-time download progress and statistics
- **Status Management**: Comprehensive status tracking and updates
- **Error Handling**: Detailed error tracking and reporting

### Firestore Integration

Store NFT data in Google Cloud Firestore for:

- **Persistent Storage**: Keep NFT data across sessions
- **Advanced Queries**: Search and filter NFTs
- **Statistics**: Get detailed analytics
- **Multi-wallet Support**: Manage multiple wallets

### Usage Examples

```bash
# Sync NFTs to Firestore only
python main_enhanced.py --wallet YOUR_WALLET --firestore-only

# Full processing with image download
python main_enhanced.py --wallet YOUR_WALLET

# Search NFTs by collection
python main_enhanced.py --search-collection "Collection Name"

# Show Firestore statistics
python main_enhanced.py --firestore-stats

# Validate configuration only
python main_enhanced.py --wallet YOUR_WALLET --validate-only
```

## Docker Deployment

### Quick Docker Setup

```bash
# Build the image
docker build -t nft-downloader .

# Run with environment variables
docker run --rm \
  -e HELIUS_API_KEY=your-key \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  -e FIRESTORE_DATABASE=develop \
  nft-downloader --wallet YOUR_WALLET --firestore-only
```

### Docker Compose

```bash
# Copy environment file
cp env.example .env

# Edit .env with your configuration
# Make sure to set FIRESTORE_DATABASE=develop

# Run with docker-compose
docker-compose up
```

## Troubleshooting

### Common Issues

1. **Firestore Permission Errors**

   - Ensure you're using the "develop" database: `FIRESTORE_DATABASE=develop`
   - Check Google Cloud authentication: `gcloud auth application-default login`
   - Verify project permissions

2. **App Engine Database Disabled**

   - Use the "develop" database instead of default
   - This is the recommended solution for most cases

3. **Helius API Errors**
   - Verify your API key is valid
   - Check API quota and limits
   - Ensure DAS API access is enabled

### Environment Validation

```bash
# Validate your setup
python main_enhanced.py --wallet YOUR_WALLET --validate-only
```

## Configuration Reference

| Variable               | Description             | Default                 | Required            |
| ---------------------- | ----------------------- | ----------------------- | ------------------- |
| `HELIUS_API_KEY`       | Helius API key          | -                       | Yes                 |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | -                       | Yes (enhanced mode) |
| `FIRESTORE_DATABASE`   | Firestore database name | `develop`               | No                  |
| `OUTPUT_DIR`           | Local output directory  | `~/Pictures/SolanaNFTs` | No                  |
| `LOG_LEVEL`            | Logging level           | `INFO`                  | No                  |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
