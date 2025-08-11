# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

EstFor is a production-ready FastAPI application for collecting and managing EstFor Kingdom gaming assets. It features a comprehensive microservices architecture with MongoDB storage, Redis caching, Celery workers, and full observability stack (Prometheus, Grafana, ELK).

**Key Features:**
- Real-time asset collection from EstFor Kingdom API (700+ assets)
- Enhanced game data with categories, rarity, skill requirements, and boost effects
- Type-safe game constants (2,400+ auto-generated from official game definitions)
- Advanced filtering with 18+ parameters for precise asset queries
- Sub-200ms response times with MongoDB indexing

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

# Test specific categories
pytest tests/test_enhanced_assets.py -v    # Enhanced asset features
pytest tests/test_game_constants.py -v     # Game integration
pytest tests/test_asset_collector.py -v    # Asset collection logic
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

**Network Configuration:**
- Services use both `estfor-network` (internal) and `dev_net` (external shared network)
- MongoDB requires authentication with username/password
- Redis uses database 0 for caching, database 1 for Celery broker

### Application Structure
```
app/
├── main.py              # FastAPI application entry
├── config.py            # Pydantic settings management
├── database/            # MongoDB connection layer
│   ├── connection.py    # Async MongoDB client
│   └── collections.py   # Collection definitions
├── models/              # Pydantic models
│   ├── assets.py        # Asset data models
│   ├── game.py          # Game-specific models
│   └── responses.py     # API response models
├── routers/             # API endpoints
│   ├── health.py        # Health checks
│   ├── assets.py        # Asset CRUD operations
│   └── game_assets.py   # Game asset endpoints
├── services/            # Business logic
│   ├── asset_collector.py  # EstFor API integration
│   ├── asset_enricher.py   # Asset enhancement logic
│   └── game_service.py     # Game data processing
├── middleware/          # Container management
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
- `MONGODB_URI` - MongoDB connection string with authentication (default: mongodb://Mohamed:Mohamed@mongo:27017/estfor?authSource=estfor)
- `MONGODB_DATABASE` - Database name (default: estfor)
- `MONGODB_COLLECTION` - Collection name (default: all_assets)
- `REDIS_URL` - Redis connection (default: redis://redis:6379/0)
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

# Access MongoDB shell with authentication
docker-compose exec mongodb mongosh -u Mohamed -p Mohamed --authenticationDatabase estfor

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

## API Endpoints Overview

### Core Asset Endpoints
- `GET /assets/` - List all assets with pagination and filtering
- `GET /assets/search` - Search assets by name
- `GET /assets/{asset_id}` - Get specific asset details
- `POST /assets/collect` - Trigger asset collection from EstFor Kingdom API
- `GET /assets/stats/summary` - Asset statistics and counts

### Game Integration Endpoints
- `GET /assets/equipment/{position}` - Get items for equipment slots (HEAD, BODY, etc.)
- `GET /assets/by-skill/{skill}` - Get items requiring specific skills
- `GET /assets/categories` - List all available categories
- `GET /health` - Service health status with dependency checks

## Local Deployment Checklist

When preparing for deployment, follow the checklist in `.cursor/rules/local-deployement-checklist.mdc`:
1. Test coverage >= 90% for production, 75% for main branch
2. Security scanning with Trivy, Bandit, and Safety
3. Performance testing with k6 (sub-200ms response times)
4. Health checks on all services
5. Rollback strategy with versioned Docker tags
6. Monitoring setup (Prometheus, Grafana, ELK)
7. Documentation completeness
8. Configuration management with `.env` files
9. Database migration strategy
