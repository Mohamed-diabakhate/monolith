# Environment Variables Quick Reference

## 🚀 Quick Setup

### 1. Interactive Setup (Easiest)
```bash
python setup_env.py
```

### 2. Manual Setup
```bash
# Create .env file
cp env.example .env

# Edit with your values
nano .env
```

### 3. Shell Export
```bash
export HELIUS_API_KEY="your-api-key"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## 📋 Required Variables

| Variable | Required For | Example |
|----------|--------------|---------|
| `HELIUS_API_KEY` | All modes | `abc123def456...` |
| `GOOGLE_CLOUD_PROJECT` | Firestore mode | `my-nft-project` |

## 🔧 Optional Variables

| Variable | Default | Example |
|----------|---------|---------|
| `OUTPUT_DIR` | `~/Pictures/SolanaNFTs` | `~/Desktop/NFTs` |
| `LOG_LEVEL` | `INFO` | `DEBUG` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Auto-detected | `/path/to/key.json` |
| `MAX_CONCURRENT_DOWNLOADS` | `5` | `10` |
| `REQUEST_TIMEOUT` | `30` | `60` |

## 📝 Example .env File

```bash
# Required
HELIUS_API_KEY=your-helius-api-key-here
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# Optional
OUTPUT_DIR=~/Pictures/SolanaNFTs
LOG_LEVEL=INFO
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
MAX_CONCURRENT_DOWNLOADS=5
REQUEST_TIMEOUT=30
```

## 🧪 Testing

### Check Environment Variables
```bash
python setup_env.py check
```

### Test Configuration
```bash
# Standard mode
python main.py --wallet YOUR_WALLET --validate-only

# Enhanced mode
python main_enhanced.py --wallet YOUR_WALLET --validate-only
```

## 🔐 Security

### Set File Permissions
```bash
chmod 600 .env
chmod 600 /path/to/service-account.json
```

### Add to .gitignore
```bash
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "credentials/" >> .gitignore
```

## 🆘 Troubleshooting

### Common Issues
- **"API key not set"**: Check `HELIUS_API_KEY` is set
- **"Project not found"**: Verify `GOOGLE_CLOUD_PROJECT` is correct
- **"Permission denied"**: Set file permissions to 600

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python main.py --wallet YOUR_WALLET --verbose
```

## 📚 More Information

- **Full Guide**: [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **Firestore Setup**: [FIRESTORE_INTEGRATION.md](FIRESTORE_INTEGRATION.md)
- **Interactive Setup**: `python setup_env.py help` 