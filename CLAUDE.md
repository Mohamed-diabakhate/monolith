# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python-based monorepo containing multiple independent projects with shared infrastructure:
- **nft_gallery/**: Solana NFT downloader using Helius API and Google Firestore
- **estfor/**: FastAPI gaming asset collection system with MongoDB and comprehensive monitoring
- **whispered_video/**: AI-powered video transcription using Torch and Faster Whisper
- **bridge/** and **monitoring/**: Supporting infrastructure services

## Development Commands

### EstFor (Primary Application)
```bash
# Environment Setup
cp .env.example .env     # Configure environment variables
make start               # Start all services via docker-compose
make stop                # Stop all services

# Development
make dev                 # Run in development mode with hot reload
make build               # Build Docker images
make migrate             # Run database migrations

# Testing & Quality
make test                # Run all tests (requires 90% coverage)
make test-unit           # Unit tests only
make test-integration    # Integration tests
make test-e2e            # End-to-end tests
make lint                # Run ruff, black, mypy
make format              # Auto-format code

# Monitoring
make health-check        # Verify all services are healthy
make logs                # View service logs
```

### NFT Gallery
```bash
# Setup & Run
pip install -r requirements.txt
python main_enhanced.py --wallet ADDRESS --firestore-only

# Testing
pytest tests/ -v --cov=src --cov-report=html
python -m pytest tests/test_integration.py -v  # Integration tests
```

### Whispered Video
```bash
# Setup
pip install -r requirements.txt

# Run transcription
python whisper_transcribe.py
```

## Architecture & Key Patterns

### EstFor Architecture
- **API Layer**: FastAPI application with comprehensive OpenAPI documentation
- **Database**: MongoDB for game asset storage with connection pooling
- **Caching**: Redis for session management and rate limiting
- **Background Jobs**: Celery workers for async processing
- **Monitoring Stack**: Prometheus metrics, Grafana dashboards, ELK logging
- **Service Mesh**: Docker networking with health checks and auto-restart

### NFT Gallery Architecture
- **Data Pipeline**: Helius API → Processing → Firestore storage
- **Error Handling**: Exponential backoff, comprehensive logging
- **Batch Processing**: Configurable batch sizes for API efficiency

### Testing Strategy
- **Unit Tests**: Mock external dependencies, test business logic
- **Integration Tests**: Test API endpoints and database interactions
- **E2E Tests**: Full user journey testing with Docker containers
- **Performance Tests**: Load testing with locust
- Minimum 90% code coverage requirement for EstFor

### CI/CD Pipeline (GitHub Actions)
- Automated testing on all pull requests
- Security scanning with Trivy and CodeQL
- Docker image building and registry push
- Deployment gates with manual approval for production

## Important Configuration

### Environment Variables (EstFor)
- `MONGODB_URI`: MongoDB connection string
- `REDIS_URL`: Redis connection for caching
- `API_KEY`: Required for authentication
- `LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARNING/ERROR)

### Docker Services
The docker-compose.yml orchestrates:
- API service (port 8000)
- MongoDB (port 27017)
- Redis (port 6379)  
- Prometheus (port 9090)
- Grafana (port 3000)
- Elasticsearch, Logstash, Kibana

## Code Conventions

- **Python Version**: 3.11+ required
- **Type Hints**: Comprehensive typing with mypy validation
- **Async/Await**: Preferred for I/O operations
- **Error Handling**: Custom exception classes with proper logging
- **API Responses**: Pydantic models for request/response validation
- **Database Models**: MongoDB documents with schema validation
- **Testing**: Pytest with fixtures, mocks, and comprehensive assertions