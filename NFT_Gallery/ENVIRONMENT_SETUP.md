# Environment Variables Setup Guide

This guide explains how to set up environment variables for the Solana NFT Downloader application, including both standard mode and Firestore-enhanced mode.

## 📋 Quick Start

### 1. Create `.env` File

Copy the example file and create your own `.env` file:

```bash
# Copy the example file
cp env.example .env

# Edit the .env file with your values
nano .env
# or
code .env
```

### 2. Basic `.env` File Template

Create a `.env` file in the project root with the following content:

```bash
# =============================================================================
# REQUIRED: Helius API Configuration
# =============================================================================
# Get your API key from https://www.helius.dev/
HELIUS_API_KEY=your-helius-api-key-here

# =============================================================================
# REQUIRED FOR FIRESTORE: Google Cloud Configuration
# =============================================================================
# Your Google Cloud project ID (required for Firestore integration)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id-here

# =============================================================================
# OPTIONAL: Google Cloud Authentication
# =============================================================================
# Path to your Google Cloud service account key file
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# =============================================================================
# OPTIONAL: Application Configuration
# =============================================================================
# Output directory for NFT images
OUTPUT_DIR=~/Pictures/SolanaNFTs

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# =============================================================================
# OPTIONAL: Performance Tuning
# =============================================================================
# Maximum concurrent downloads
# MAX_CONCURRENT_DOWNLOADS=5

# Request timeout in seconds
# REQUEST_TIMEOUT=30
```

## 🔑 Required Environment Variables

### For Standard Mode (Basic NFT Downloading)

| Variable | Description | Example |
|----------|-------------|---------|
| `HELIUS_API_KEY` | Your Helius API key | `HELIUS_API_KEY=abc123def456...` |

### For Enhanced Mode (with Firestore)

| Variable | Description | Example |
|----------|-------------|---------|
| `HELIUS_API_KEY` | Your Helius API key | `HELIUS_API_KEY=abc123def456...` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | `GOOGLE_CLOUD_PROJECT=my-nft-project` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` |

## 🚀 Setting Up Environment Variables

### Method 1: Using `.env` File (Recommended)

1. **Create the `.env` file:**
   ```bash
   # In your project root directory
   touch .env
   ```

2. **Edit the `.env` file:**
   ```bash
   # Using nano
   nano .env
   
   # Using VS Code
   code .env
   
   # Using vim
   vim .env
   ```

3. **Add your environment variables:**
   ```bash
   HELIUS_API_KEY=your-actual-api-key-here
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   OUTPUT_DIR=~/Pictures/SolanaNFTs
   ```

### Method 2: Using Export Commands

```bash
# Set environment variables in your shell
export HELIUS_API_KEY="your-helius-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export OUTPUT_DIR="~/Pictures/SolanaNFTs"

# Verify they are set
echo $HELIUS_API_KEY
echo $GOOGLE_CLOUD_PROJECT
```

### Method 3: Using Shell Profile

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# Add to ~/.bashrc or ~/.zshrc
export HELIUS_API_KEY="your-helius-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export OUTPUT_DIR="~/Pictures/SolanaNFTs"

# Reload the profile
source ~/.bashrc  # or source ~/.zshrc
```

## 🔐 Getting Your API Keys

### Helius API Key

1. Visit [Helius](https://www.helius.dev/)
2. Sign up for an account
3. Create a new API key
4. Ensure DAS API access is enabled
5. Copy the API key to your `.env` file

### Google Cloud Project ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Firestore API
4. Copy the project ID to your `.env` file

### Google Cloud Service Account (Optional)

1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Create a new service account
3. Download the JSON key file
4. Set the path in `GOOGLE_APPLICATION_CREDENTIALS`

## 🧪 Testing Your Environment Setup

### Test Standard Mode

```bash
# Test with validation only
python main.py --wallet YOUR_WALLET_ADDRESS --validate-only
```

### Test Enhanced Mode

```bash
# Test with validation only
python main_enhanced.py --wallet YOUR_WALLET_ADDRESS --validate-only
```

### Test Environment Variables

```bash
# Check if variables are loaded
python -c "
import os
print('HELIUS_API_KEY:', 'SET' if os.getenv('HELIUS_API_KEY') else 'NOT SET')
print('GOOGLE_CLOUD_PROJECT:', 'SET' if os.getenv('GOOGLE_CLOUD_PROJECT') else 'NOT SET')
print('OUTPUT_DIR:', os.getenv('OUTPUT_DIR', 'NOT SET'))
"
```

## 🔧 Environment Variable Reference

### Required Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `HELIUS_API_KEY` | All modes | Helius API key for DAS API access |
| `GOOGLE_CLOUD_PROJECT` | Enhanced mode | Google Cloud project ID |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTPUT_DIR` | `~/Pictures/SolanaNFTs` | Output directory for NFT images |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Auto-detected | Path to Google Cloud service account key |
| `MAX_CONCURRENT_DOWNLOADS` | `5` | Maximum concurrent downloads |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `FIRESTORE_COLLECTION` | `nfts` | Firestore collection name |
| `FIRESTORE_DATABASE_MODE` | `native` | Firestore database mode |

## 🐳 Docker Environment Variables

When using Docker, you can pass environment variables:

```bash
# Using docker-compose
docker-compose run --rm -e HELIUS_API_KEY=your-key nft-downloader --wallet YOUR_WALLET

# Using docker run
docker run --rm -e HELIUS_API_KEY=your-key -e GOOGLE_CLOUD_PROJECT=your-project nft-downloader --wallet YOUR_WALLET
```

## 🔒 Security Best Practices

### 1. Never Commit `.env` Files

```bash
# Add to .gitignore (if not already there)
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "credentials/" >> .gitignore
```

### 2. Use Strong API Keys

- Generate unique API keys for each environment
- Rotate keys regularly
- Use minimal required permissions

### 3. Secure File Permissions

```bash
# Set restrictive permissions on .env file
chmod 600 .env

# Set restrictive permissions on service account key
chmod 600 /path/to/service-account-key.json
```

### 4. Environment-Specific Files

```bash
# Create environment-specific files
cp .env .env.local
cp .env .env.production
cp .env .env.development
```

## 🚨 Troubleshooting

### Common Issues

1. **"HELIUS_API_KEY not set"**
   ```bash
   # Check if variable is set
   echo $HELIUS_API_KEY
   
   # Re-source your .env file
   source .env
   ```

2. **"Google Cloud project not found"**
   ```bash
   # Verify project ID
   echo $GOOGLE_CLOUD_PROJECT
   
   # Check Google Cloud authentication
   gcloud auth list
   ```

3. **"Permission denied"**
   ```bash
   # Check file permissions
   ls -la .env
   
   # Fix permissions
   chmod 600 .env
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py --wallet YOUR_WALLET --verbose
```

## 📝 Example Configurations

### Minimal Configuration (Standard Mode)

```bash
# .env
HELIUS_API_KEY=your-helius-api-key
OUTPUT_DIR=~/Pictures/SolanaNFTs
```

### Full Configuration (Enhanced Mode)

```bash
# .env
HELIUS_API_KEY=your-helius-api-key
GOOGLE_CLOUD_PROJECT=my-nft-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
OUTPUT_DIR=~/Pictures/SolanaNFTs
LOG_LEVEL=INFO
MAX_CONCURRENT_DOWNLOADS=10
REQUEST_TIMEOUT=60
```

### Development Configuration

```bash
# .env.development
HELIUS_API_KEY=your-dev-api-key
GOOGLE_CLOUD_PROJECT=my-nft-dev-project
OUTPUT_DIR=~/Desktop/NFTs/dev
LOG_LEVEL=DEBUG
MAX_CONCURRENT_DOWNLOADS=3
```

## ✅ Verification Checklist

- [ ] `.env` file created in project root
- [ ] `HELIUS_API_KEY` set with valid API key
- [ ] `GOOGLE_CLOUD_PROJECT` set (for enhanced mode)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` set (optional)
- [ ] `.env` file added to `.gitignore`
- [ ] File permissions set correctly (600)
- [ ] Environment variables loaded successfully
- [ ] Validation test passes

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your API keys are valid
3. Ensure all required variables are set
4. Check file permissions
5. Review the application logs
6. Open an issue on GitHub with details 