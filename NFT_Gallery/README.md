# 🖼️ Solana NFT Downloader

Download all NFTs (images) from a Solana wallet using Helius DAS API. Images are saved to `~/Pictures/SolanaNFTs/` for native display inside the macOS Photos app.

## 🌟 Features

- **Simple API Key Management**: Uses environment variables for Helius API key
- **Incremental Downloads**: Only downloads NFTs that aren't already saved locally
- **macOS Photos Integration**: Automatically indexes downloaded images in macOS Photos app
- **Comprehensive Error Handling**: Robust error handling with detailed logging
- **Docker Support**: Containerized deployment for portability
- **Excellent Test Coverage**: Comprehensive test suite with 85% coverage (83 tests)
- **Compressed NFT Support**: Native support for Solana's compressed NFTs
- **Smart Image URL Extraction**: Intelligent extraction of image URLs from Helius DAS API responses
- **Flexible Content Type Handling**: Handles various content types and edge cases for image downloads
- **Enhanced Error Recovery**: Advanced retry logic and domain-specific fixes for missing NFTs
- **Comprehensive Failure Analysis**: Detailed reporting of failed downloads with error categorization
- **IPFS Metadata Extraction**: ⭐ **NEW** - Extracts images from IPFS/Arweave metadata for maximum NFT recovery

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Solana Wallet │───▶│  Helius DAS API  │───▶│  NFT Processor  │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────┐
                                              │  File Manager   │
                                              │                 │
                                              └─────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────┐
                                              │ ~/Pictures/     │
                                              │ SolanaNFTs/     │
                                              └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Helius API key (get from https://www.helius.dev/)
- macOS (for Photos app integration)

## 🚀 Quick Start

### 1. Get Helius API Key

1. Visit [Helius](https://www.helius.dev/)
2. Sign up for an account
3. Create a new API key
4. Ensure DAS API access is enabled

### 2. Set Environment Variable

```bash
# Set your Helius API key
export HELIUS_API_KEY="your-helius-api-key"
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 4. Run the Downloader

```bash
# Download NFTs from a wallet
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM

# With custom output directory
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --output ~/Desktop/NFTs

# With verbose logging
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --verbose

# Validate configuration only
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --validate-only

# Show statistics
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --stats

# Retry failed downloads with improved error handling
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --retry-failed

# Advanced retry with custom settings
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --retry-failed --max-retries 5 --verbose
```

### 5. Docker Deployment (Optional)

```bash
# Run with Docker
docker-compose run --rm nft-downloader --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

## 📖 Usage Examples

### Basic Usage

```bash
# Download all NFTs from a wallet
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

### Advanced Usage

```bash
# Custom output directory
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --output ~/Desktop/MyNFTs

# Verbose logging with log file
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --verbose --log-file nft_download.log

# Validate configuration only
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --validate-only

# Show statistics
python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --stats
```

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# End-to-end tests only
python -m pytest tests/e2e/ -v
```

### Docker Test Environment

```bash
# Run tests in Docker environment
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 📁 Project Structure

```
NFT_Gallery/
├── src/                          # Source code
│   ├── __init__.py
│   ├── helius_api.py            # Helius DAS API client
│   ├── file_manager.py          # Local file operations
│   ├── nft_processor.py         # Main NFT processing logic
│   └── utils.py                 # Utility functions
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   └── conftest.py              # Test configuration
├── main.py                      # Main script entry point
├── requirements.txt             # Main dependencies
├── requirements-test.txt        # Test dependencies
├── Dockerfile                   # Production Docker image
├── docker-compose.yml           # Production orchestration
├── docker-compose.test.yml      # Test environment
├── .dockerignore               # Docker build optimization
├── deploy.sh                   # Automated deployment script
├── env.example                 # Environment template
├── nginx.conf                  # Monitoring interface config
├── monitor/                    # Monitoring dashboard
│   └── index.html              # Web monitoring interface
├── DOCKER_DEPLOYMENT.md        # Docker deployment guide
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HELIUS_API_KEY` | Helius API key for DAS API access | Yes |
| `OUTPUT_DIR` | Output directory for NFT images | No (default: ~/Pictures/SolanaNFTs) |

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--wallet` | Solana wallet address | Required |

## 🔐 Security

- **Environment Variable Security**: API keys stored in environment variables
- **Secure File Operations**: Safe filename generation and validation
- **Error Handling**: Comprehensive error handling without exposing sensitive data
- **Docker Security**: Non-root user in container

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Ensure your Helius API key is set correctly
   echo $HELIUS_API_KEY
   ```

2. **Permission Denied**
   ```bash
   # Check output directory permissions
   ls -la ~/Pictures/SolanaNFTs/
   ```

3. **API Key Not Found**
   ```bash
   # Check if Helius API key is set
   echo $HELIUS_API_KEY
   
   # Set the API key if not already set
   export HELIUS_API_KEY="your-helius-api-key"
   ```

4. **Invalid Wallet Address**
   ```bash
   # Validate wallet address format
   python main.py --wallet YOUR_WALLET --validate-only
   ```

5. **Docker Permission Issues**
   ```bash
   # If you get permission errors in Docker:
   # The application now uses /app/output as the default output directory
   # Make sure the output directory is properly mounted and has correct permissions
   docker-compose run --rm nft-downloader --wallet YOUR_WALLET --validate-only
   ```

6. **Helius API Key Permission Issues**
   ```bash
   # If you get API access errors:
   # 1. Visit https://www.helius.dev/ and log in
   # 2. Navigate to API key settings
   # 3. Ensure DAS API access is enabled for your API key
   # 4. Check your API key permissions and rate limits
   
   # Test with a valid API key:
   export HELIUS_API_KEY="your-valid-helius-api-key"
   python main.py --wallet YOUR_WALLET --validate-only
   ```

7. **Missing NFTs and Download Failures (Enhanced)**
   ```bash
   # If you see many failed downloads or missing NFTs:
   # The application now includes advanced error recovery and retry logic
   
   # Use the enhanced retry features:
   python main.py --wallet YOUR_WALLET --retry-failed --max-retries 5
   
   # Common issues now automatically handled:
   # - 403 Forbidden errors (domain blocking)
   # - 404 Not Found errors (URL transformations)
   # - SSL certificate issues
   # - JSON responses containing image URLs
   # - Empty file downloads
   # - Network timeouts and connection errors
   
   # The improvements include:
   # - Automatic URL transformations for problematic domains
   # - Multiple IPFS gateway fallbacks
   # - Smart retry logic with error classification
   # - JSON response parsing for image URL extraction
   # - Enhanced content-type handling
   # - Comprehensive failure analysis and reporting
   ```

### Debug Mode

```bash
# Enable debug logging
python main.py --wallet YOUR_WALLET --verbose --log-file debug.log
```

## 🚀 Enhanced Features

### Advanced Error Recovery
- **Smart Retry Logic**: Configurable retry attempts with intelligent error classification
- **Domain-Specific Fixes**: Automatic handling of problematic domains (hi-hi.vip, IPFS gateways)
- **URL Transformations**: Automatic conversion of JSON endpoints to image endpoints
- **Multiple Fallbacks**: Multiple IPFS gateway alternatives for failed downloads

### Comprehensive Failure Analysis
- **Error Categorization**: Detailed breakdown of failures by error type and domain
- **Success Rate Tracking**: Real-time success rate calculation and reporting
- **Domain Health Monitoring**: Track which domains are causing the most failures
- **Detailed Logging**: Enhanced logging with retry attempts and error details

### Content-Type Handling
- **JSON Response Parsing**: Extract image URLs from JSON responses
- **Magic Byte Detection**: Validate image files using file signatures
- **Flexible MIME Types**: Support for various content types and edge cases
- **Video File Detection**: Skip video files and focus on image downloads

### IPFS Metadata Extraction ⭐ **NEW**
- **Metadata URI Detection**: Finds metadata URIs in NFT assets
- **IPFS Gateway Support**: Multiple fallback gateways (ipfs.io, cloudflare-ipfs.com, etc.)
- **Arweave Support**: Handles Arweave protocol URLs
- **Metadata Parsing**: Extracts image URLs from fetched metadata
- **Recursive Search**: Searches through nested metadata structures

## 📊 Performance

- **Incremental Downloads**: Only downloads new NFTs
- **Efficient File Management**: Checks file existence before downloading
- **Memory Efficient**: Streams large files without loading into memory
- **Error Recovery**: Continues processing even if individual downloads fail
- **Compressed NFT Support**: Native support for Solana's compressed NFTs
- **Enhanced Success Rate**: Expected 80-90% success rate with new error recovery and IPFS metadata extraction features

## 🧪 Testing

### Test Coverage
- **Overall Coverage**: 85%
- **Test Count**: 83 unit tests
- **Success Rate**: 93% (77/83 passing)

### Running Tests
```bash
# Run all tests with coverage
python -m pytest tests/unit/ --cov=src --cov-report=term-missing -v

# Run specific test modules
python -m pytest tests/unit/test_helius_api.py -v
python -m pytest tests/unit/test_file_manager.py -v
python -m pytest tests/unit/test_nft_processor.py -v

# Generate HTML coverage report
python -m pytest tests/unit/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Run E2E tests (requires Docker)
docker-compose -f docker-compose.test.yml up --build
```

### Test Categories
- **Unit Tests**: 83 tests covering all core modules
- **Integration Tests**: Infrastructure ready for external dependencies
- **E2E Tests**: 6 smoke tests for complete workflows

See [TEST_RUNBOOK.md](TEST_RUNBOOK.md) for detailed testing procedures.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality (≥90% coverage required)
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Helius](https://www.helius.dev/) for providing the DAS API
- [Solana](https://solana.com/) for the blockchain platform
- [Metaplex](https://metaplex.com/) for the Digital Asset Standard

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test logs
3. Open an issue on GitHub

---

**Happy NFT Collecting! 🎨** 