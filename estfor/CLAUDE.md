# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

EstFor is a production-ready FastAPI application for collecting and managing EstFor Kingdom gaming assets. It features a comprehensive microservices architecture with MongoDB storage, Redis caching, Celery workers, and full observability stack (Prometheus, Grafana, ELK).

## Development Commands

### Quick Start
```bash
# Initial Setup
cp .env.example .env     # Configure environment variables
make setup-dev           # Install development dependencies
make start               # Start all services via docker-compose

# Core Development
make dev                 # Run with hot reload
make restart             # Restart services
make logs                # View service logs
make stop                # Stop all services
make clean               # Clean containers and volumes
```

### Testing Commands
```bash
# All tests (90% coverage required)
make test
pytest tests/ -v --cov=app --cov-report=html --cov-fail-under=90

# Specific test types
make test-unit           # Unit tests only
make test-integration    # Integration tests with MongoDB
make test-e2e            # End-to-end tests
make performance-test    # k6 load testing

# Run single test
pytest tests/test_unit.py::test_specific_function -v
```

### Code Quality
```bash
make lint                # Run flake8, black check, isort check
make format              # Auto-format with black and isort
make security-scan       # Trivy container scanning
make dependency-scan     # Safety dependency check
```

### Database Operations
```bash
make db-backup           # Backup MongoDB data
make db-restore          # Restore MongoDB data
make health-check        # Verify all services are healthy
```

## Architecture & Key Patterns

### Service Architecture
The application runs 11 interconnected Docker services orchestrated via docker-compose:

```
FastAPI (8000) ←→ MongoDB (27017) ←→ Redis (6379)
     ↓                    ↓               ↓
Celery Worker     Prometheus (9090)  Grafana (3000)
     ↓                    ↓               ↓
ELK Stack        AlertManager (9093)  cAdvisor (8082)
```

### Application Structure
```
app/
├── main.py              # FastAPI application entry
├── config.py            # Pydantic settings management
├── database.py          # MongoDB async client setup
├── models/              # Pydantic models
├── routers/             # API endpoints
│   ├── health.py        # Health checks
│   └── assets.py        # Asset operations
├── services/            # Business logic
└── utils/               # Shared utilities
```

### Testing Strategy
- **Unit Tests**: Mock external dependencies, test business logic in isolation
- **Integration Tests**: Test API endpoints with real MongoDB instance
- **E2E Tests**: Full user journey testing with all services running
- **Performance Tests**: k6 scenarios for load, stress, and spike testing
- **Coverage Requirement**: 90% minimum for production, 75% for main branch

### Key Configuration Files
- `docker-compose.yml` - Local development environment with all 11 services
- `docker-compose.prod.yml` - Production configuration
- `pytest.ini` - Test configuration with markers and asyncio setup
- `pyproject.toml` - Tool configuration (black, isort, mypy)
- `.env.example` - Environment variable template

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/estfor-ci-cd.yml`) with stages:
1. **Quick Test** (PR/develop): Linting, type checking, unit tests
2. **Comprehensive Test** (main): Full test suite with MongoDB
3. **Docker Build**: Multi-stage build with security scanning
4. **Performance Test**: k6 load testing
5. **Production Deploy**: Automated deployment with health checks

## Environment Variables

Required variables (set in `.env`):
- `MONGODB_URI` - MongoDB connection string (default: mongodb://mongodb:27017/)
- `DATABASE_NAME` - Database name (default: estfor_db)
- `REDIS_URL` - Redis connection (default: redis://redis:6379)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `WORKERS` - Number of API workers (default: 4)

## Monitoring & Observability

- **Metrics**: Prometheus at http://localhost:9090
- **Dashboards**: Grafana at http://localhost:3000 (admin/admin)
- **Logs**: Kibana at http://localhost:5601
- **Alerts**: 9 pre-configured alert rules in AlertManager
- **API Docs**: Interactive documentation at http://localhost:8000/docs

## Performance Targets

- Response time: <200ms (95th percentile)
- Error rate: <0.1 errors/second
- Availability: >99.9% uptime
- Resource usage: CPU <80%, Memory <85%

## Docker Development

The Dockerfile uses multi-stage builds:
- **base**: Python 3.11-slim with security hardening
- **development**: Hot reload enabled
- **production**: Optimized with 4 workers
- **worker**: Celery background processor

Build specific stages:
```bash
docker build --target development -t estfor:dev .
docker build --target production -t estfor:prod .
```

## Common Development Tasks

### Adding New API Endpoint
1. Create router in `app/routers/`
2. Add Pydantic models in `app/models/`
3. Implement service logic in `app/services/`
4. Write tests in `tests/`
5. Update OpenAPI documentation

### Running Database Migrations
```bash
# No built-in migration system - use MongoDB's schemaless design
# For schema changes, update Pydantic models and handle backward compatibility
```

### Debugging
```bash
# View specific service logs
docker-compose logs -f app
docker-compose logs -f worker

# Access MongoDB shell
docker-compose exec mongodb mongosh

# Access Redis CLI
docker-compose exec redis redis-cli
```

## EstFor Game Definitions

The `estfor-definitions/` directory contains TypeScript/AssemblyScript game definitions:
- Action definitions and requirements
- Skill configurations
- Item mappings
- Game mechanics

These are used for validating game assets and ensuring data consistency.