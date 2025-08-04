# EstFor Asset Collection System

A Docker-based system for collecting and storing EstFor Kingdom assets in Firestore.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Worker Service │    │  Firestore DB   │
│   (Port 8000)   │◄──►│   (Background)  │◄──►│   (Emulator)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │   ELK Stack     │
│   (Metrics)     │    │  (Dashboards)   │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Make (optional, for convenience commands)

### Local Deployment

1. **Clone and Setup**

   ```bash
   git clone <repository>
   cd estfor
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Build and Run**

   ```bash
   # Start all services
   docker-compose up -d

   # Or use make commands
   make start
   ```

3. **Verify Deployment**

   ```bash
   # Check all services are healthy
   make health-check

   # View logs
   make logs
   ```

4. **Access Services**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Kibana: http://localhost:5601

## 🧪 Testing

### Run All Tests

```bash
# Unit tests with coverage
make test

# Integration tests
make test-integration

# End-to-end tests
make test-e2e

# Security scan
make security-scan

# Performance tests
make performance-test
```

### Test Coverage

- **Unit Tests**: 90%+ coverage target
- **Integration Tests**: Service-to-service communication
- **E2E Tests**: Complete workflow validation

## 📊 Monitoring & Health Checks

### Health Endpoints

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Metrics

- Prometheus metrics at `/metrics`
- Custom business metrics for asset collection
- Resource utilization monitoring

### Logging

- Structured JSON logging
- Centralized log aggregation
- Error tracking and alerting

## 🔧 Configuration

### Environment Variables

```bash
# EstFor API Configuration
ESTFOR_API_URL=https://api.estfor.com
ESTFOR_API_KEY=your_api_key

# Firestore Configuration
FIRESTORE_PROJECT_ID=estfor
FIRESTORE_COLLECTION=all_assets
FIRESTORE_EMULATOR_HOST=firestore:8080

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Configuration Files

- `.env` - Environment variables
- `docker-compose.yml` - Service orchestration
- `docker-compose.override.yml` - Local development overrides
- `docker-compose.test.yml` - Testing environment

## 🔄 Deployment & Rollback

### Version Management

```bash
# Build with version tag
make build VERSION=v1.2.0

# Deploy specific version
make deploy VERSION=v1.2.0

# Rollback to previous version
make rollback VERSION=v1.1.0
```

### Canary Deployment

```bash
# Deploy canary version
make canary-deploy VERSION=v1.2.0

# Promote canary to production
make promote-canary

# Rollback canary
make rollback-canary
```

## 🛡️ Security

### Vulnerability Scanning

```bash
# Scan Docker images
make security-scan

# Scan dependencies
make dependency-scan

# Validate secrets
make secrets-validate
```

### Security Features

- Image vulnerability scanning with Trivy
- Secret management with Docker secrets
- Network isolation between services
- Input validation and sanitization

## 📈 Performance

### Load Testing

```bash
# Run performance tests
make performance-test

# Custom load scenarios
k6 run k6/load-test.js
```

### Performance Targets

- API response time: < 200ms (95th percentile)
- Asset collection throughput: 1000 assets/hour
- Database query performance: < 50ms

## 🗄️ Database

### Firestore Emulator

- Local development database
- Automatic schema validation
- Migration testing

### Data Management

```bash
# Backup data
make db-backup

# Restore data
make db-restore

# Run migrations
make db-migrate
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**

   ```bash
   # Check service status
   docker-compose ps

   # View service logs
   docker-compose logs <service-name>
   ```

2. **Database connection issues**

   ```bash
   # Check Firestore emulator
   docker-compose logs firestore

   # Test connection
   curl http://localhost:8080
   ```

3. **Performance issues**

   ```bash
   # Check resource usage
   docker stats

   # View metrics
   curl http://localhost:9090/metrics
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up

# Attach to running container
docker-compose exec app bash
```

## 📚 API Documentation

### EstFor Asset Collection

#### Endpoints

- `GET /assets` - List collected assets
- `POST /assets/collect` - Trigger asset collection
- `GET /assets/{asset_id}` - Get specific asset
- `GET /assets/stats` - Collection statistics

#### Authentication

- API key authentication
- Rate limiting
- Request validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Run tests locally
4. Submit pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run linting
make lint

# Format code
make format
```

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)

---

**Last Updated**: $(date)
**Version**: v1.0.0
