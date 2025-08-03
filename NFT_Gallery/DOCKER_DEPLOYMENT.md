# 🐳 Docker Deployment Guide

This guide will help you deploy the Solana NFT Downloader using Docker for production-ready, containerized deployment.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Google Cloud Project with Secret Manager enabled
- Ankr API key stored in Google Secret Manager

## 🚀 Quick Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd NFT_Gallery

# Run the automated deployment script
./deploy.sh
```

### 2. Configure Environment

```bash
# Edit the environment file
cp env.example .env
nano .env
```

Update the `.env` file with your configuration:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json

# Application Configuration
OUTPUT_DIR=/app/output
LOG_LEVEL=INFO
```

### 3. Add Google Cloud Credentials

```bash
# Create credentials directory
mkdir -p credentials

# Copy your service account key
cp /path/to/your/service-account.json credentials/service-account.json

# Set proper permissions
chmod 600 credentials/service-account.json
```

### 4. Deploy

```bash
# Build and start the application
docker-compose up -d

# Or run the deployment script
./deploy.sh
```

## 🔧 Manual Deployment

If you prefer manual deployment, follow these steps:

### 1. Build the Image

```bash
# Build the Docker image
docker-compose build

# Or build directly with Docker
docker build -t solana-nft-downloader .
```

### 2. Create Directories

```bash
# Create necessary directories
mkdir -p output logs credentials monitor

# Set permissions
chmod 755 output logs monitor
chmod 700 credentials
```

### 3. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit with your settings
nano .env
```

### 4. Add Credentials

```bash
# Copy your Google Cloud service account key
cp /path/to/service-account.json credentials/service-account.json
chmod 600 credentials/service-account.json
```

### 5. Run the Application

```bash
# Start the application
docker-compose up -d

# Check status
docker-compose ps
```

## 📖 Usage Examples

### Basic Usage

```bash
# Download NFTs from a wallet
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
```

### Advanced Usage

```bash
# Validate configuration
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --validate-only

# Show statistics
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --stats

# Verbose logging
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --verbose --log-file /app/logs/nft_download.log
```

### Custom Output Directory

```bash
# Use custom output directory
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --output /app/output/custom_folder
```

## 📊 Monitoring

### Enable Monitoring Interface

```bash
# Start with monitoring interface
docker-compose --profile monitor up -d

# Access monitoring at http://localhost:8080
```

### Health Checks

```bash
# Check container health
docker-compose ps

# View logs
docker-compose logs nft-downloader

# Follow logs in real-time
docker-compose logs -f nft-downloader
```

### Resource Monitoring

```bash
# Check resource usage
docker stats

# Inspect container
docker-compose exec nft-downloader ps aux
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | - | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | `/app/credentials/service-account.json` | Yes |
| `OUTPUT_DIR` | Output directory | `/app/output` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./output` | `/app/output` | Downloaded NFT images |
| `./logs` | `/app/logs` | Application logs |
| `./credentials` | `/app/credentials` | Google Cloud credentials |

### Ports

| Service | Port | Purpose |
|---------|------|---------|
| `nft-monitor` | 8080 | Monitoring interface |

## 🛠️ Troubleshooting

### Common Issues

#### 1. Permission Denied

```bash
# Fix directory permissions
chmod 755 output logs monitor
chmod 700 credentials
chmod 600 credentials/service-account.json
```

#### 2. Container Won't Start

```bash
# Check logs
docker-compose logs nft-downloader

# Check environment variables
docker-compose config

# Validate configuration
docker-compose run --rm nft-downloader --validate-only
```

#### 3. Google Cloud Authentication

```bash
# Verify service account key
docker-compose run --rm nft-downloader \
  --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM \
  --validate-only
```

#### 4. Network Issues

```bash
# Check network connectivity
docker-compose exec nft-downloader curl -I https://rpc.ankr.com

# Check DNS resolution
docker-compose exec nft-downloader nslookup rpc.ankr.com
```

### Debug Mode

```bash
# Run with debug logging
docker-compose run --rm nft-downloader \
  --wallet YOUR_WALLET \
  --verbose \
  --log-file /app/logs/debug.log

# Check debug logs
docker-compose logs nft-downloader
```

## 🔒 Security Considerations

### Container Security

- ✅ Non-root user in container
- ✅ Read-only credentials mount
- ✅ Minimal base image (python:3.11-slim)
- ✅ Multi-stage build for smaller image
- ✅ Health checks enabled

### Network Security

- ✅ Internal Docker network
- ✅ No exposed ports (except monitoring)
- ✅ Secure headers in nginx

### Data Security

- ✅ Credentials mounted as read-only
- ✅ Proper file permissions
- ✅ No secrets in environment variables

## 📈 Performance Optimization

### Resource Limits

```yaml
# Add to docker-compose.yml
services:
  nft-downloader:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### Volume Optimization

```bash
# Use named volumes for better performance
docker volume create nft-output
docker volume create nft-logs
```

### Build Optimization

```bash
# Use build cache
docker-compose build --no-cache

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t solana-nft-downloader .
```

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data

```bash
# Backup output directory
tar -czf nft-backup-$(date +%Y%m%d).tar.gz output/

# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### Cleanup

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager)
- [Ankr API Documentation](https://www.ankr.com/docs/)

## 🤝 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs: `docker-compose logs nft-downloader`
3. Validate configuration: `docker-compose run --rm nft-downloader --validate-only`
4. Open an issue on GitHub

---

**Happy Docker Deployment! 🐳** 