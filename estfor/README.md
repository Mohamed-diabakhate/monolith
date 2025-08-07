# EstFor Asset Collection System

A comprehensive Docker-based system for collecting, storing, and managing EstFor Kingdom assets with integrated game definitions and type-safe API endpoints.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Worker Service │    │   MongoDB DB    │
│   (Port 8000)   │◄──►│   (Background)  │◄──►│   (Port 27017)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │   ELK Stack     │
│   (Metrics)     │    │  (Dashboards)   │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🎮 EstFor Kingdom Integration

- **Type-Safe Game Constants**: Auto-generated Python enums from official TypeScript definitions
- **20+ Game Enums**: Skills, equipment positions, boost types, activity types, etc.
- **2,400+ Game Constants**: Item IDs, equipment stats, and game values
- **Pydantic Models**: Validated models for players, equipment, skills, and activities
- **Game Data APIs**: RESTful endpoints for items, skills, boosts, and equipment

### 🔄 Asset Collection System

- **Automated Collection**: Background workers for continuous asset gathering
- **MongoDB Storage**: Document-based storage with indexing and performance optimization
- **Real-time Processing**: Async processing with Celery and Redis

### 📊 Comprehensive Monitoring

- **Metrics Collection**: Prometheus with custom business metrics
- **Visualization**: Grafana dashboards for system and business metrics
- **Centralized Logging**: ELK stack for log aggregation and analysis
- **Performance Monitoring**: Response time, throughput, and error rate tracking

### 🛡️ Production-Ready

- **Multi-stage Docker Build**: Optimized images for development and production
- **Health Checks**: Readiness and liveness probes for Kubernetes deployment
- **Security Scanning**: Container and dependency vulnerability detection
- **CI/CD Pipeline**: Automated testing, building, and deployment

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
   - Game Assets API: http://localhost:8000/api/game/
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Kibana: http://localhost:5601
   - MongoDB: http://localhost:27017

### Production Deployment

For production deployment, see the comprehensive guides:

- [Production Deployment Guide](PRODUCTION.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Production Commands](Makefile.prod)

**Quick Production Setup:**

```bash
# Configure production environment
cp env.production.template .env.production
# Edit .env.production with your secure values

# Deploy to production
./deploy-production.sh

# Or use production Makefile
make -f Makefile.prod deploy-prod
```

## 🧪 Testing

### Current Status ✅

The system has been successfully tested and is fully operational:

- ✅ **Application Health**: All health endpoints responding correctly
- ✅ **Database Connectivity**: MongoDB connection established and working
- ✅ **Background Worker**: Celery worker running and connected to Redis
- ✅ **Monitoring Stack**: Prometheus, Grafana, and ELK stack operational
- ✅ **EstFor Integration**: Game constants and API endpoints fully tested
- ✅ **Performance**: Health endpoints responding in < 15ms average

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD pipeline that runs on pushes and pull requests to the main branch:

#### Build & Test Job

- **Code Quality Checks**: Black formatting, isort imports, flake8 linting, mypy type checking
- **Security Scanning**: Bandit for Python security issues, Trivy for container vulnerabilities
- **Testing**: Unit, integration, and E2E tests with coverage reporting
- **Docker Build**: Multi-stage Docker image build with caching
- **Container Testing**: Runs tests inside the built container

#### Deployment Jobs

- **Staging Deployment**: Automatic deployment to staging on main branch pushes (including merges)
- **Production Deployment**: Manual deployment to production on version tags

#### Quality Gates

- All tests must pass
- Code coverage requirements met
- No security vulnerabilities
- Code formatting standards maintained

### Local Development Setup

#### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

#### Code Quality Tools

The project uses several tools for maintaining code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **safety**: Dependency vulnerability scanning

#### Running Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m e2e       # End-to-end tests only

# Test EstFor integration
pytest tests/test_game_constants.py -v    # Game constants tests
pytest tests/test_game_assets_api.py -v   # Game API tests
pytest tests/test_enhanced_assets.py -v   # Enhanced asset tests

# Run tests in parallel
pytest -n auto
```

### Test Results

```bash
# Health endpoints test results
curl http://localhost:8000/health/
# Response: {"status": "healthy", "service": "EstFor Asset Collection System", "version": "1.0.0"}

curl http://localhost:8000/health/ready
# Response: {"status": "ready", "database": "connected", "service": "ready"}

curl http://localhost:8000/health/live
# Response: {"status": "alive", "service": "running"}
```

### Run Tests

```bash
# Check all services health
make health-check

# Manual performance test (10 requests)
time (for i in {1..10}; do curl -s http://localhost:8000/health/ > /dev/null; done)
# Result: ~10ms average response time

# View service logs
make logs-app
make logs-worker
```

### Test Coverage

- **Health Checks**: ✅ All endpoints operational
- **Database Integration**: ✅ MongoDB connection working
- **Background Processing**: ✅ Celery worker operational
- **EstFor Game Integration**: ✅ 45+ tests passing (constants + API + enhanced assets)
- **Monitoring**: ✅ Prometheus, Grafana, ELK stack running
- **Performance**: ✅ Sub-15ms response times

## 📊 Monitoring & Health Checks

### Health Endpoints

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Monitoring Stack

The system includes a comprehensive monitoring stack with the following components:

| Component         | Purpose                          | Access URL            |
| ----------------- | -------------------------------- | --------------------- |
| **Prometheus**    | Time-series metrics collection   | http://localhost:9090 |
| **Grafana**       | Metrics visualization dashboards | http://localhost:3000 |
| **cAdvisor**      | Container-level metrics exporter | http://localhost:8080 |
| **Elasticsearch** | Log storage and indexing         | http://localhost:9200 |
| **Kibana**        | Log visualization and analysis   | http://localhost:5601 |

### Quick Monitoring Setup

```bash
# Start monitoring stack only
./start-monitoring.sh

# Or start specific monitoring services
docker-compose up -d prometheus grafana cadvisor elasticsearch kibana
```

### Metrics

- Prometheus metrics at `/metrics`
- Custom business metrics for asset collection
- Resource utilization monitoring
- Container performance metrics via cAdvisor

### Logging

- Structured JSON logging
- Centralized log aggregation via ELK stack
- Error tracking and alerting

## 🔧 Configuration

### Environment Variables

```bash
# EstFor API Configuration
ESTFOR_API_URL=https://api.estfor.com
# EstFor API doesn't require authentication
# ESTFOR_API_KEY=your_api_key

# MongoDB Configuration
MONGODB_URI=mongodb://admin:password@mongodb:27017/estfor?authSource=admin
MONGODB_DATABASE=estfor
MONGODB_COLLECTION=all_assets
MONGODB_MAX_POOL_SIZE=10

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

### MongoDB

- Document-based NoSQL database
- Automatic indexing for performance
- Connection pooling for scalability
- Built-in replication and sharding support

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
   # Check MongoDB
   docker-compose logs mongodb

   # Test connection
   mongosh mongodb://admin:password@localhost:27017/estfor?authSource=admin
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

### EstFor Asset Collection (Enhanced)

#### Core Endpoints

- `GET /assets` - List enhanced assets with comprehensive filtering
  - **Filters**: category, equip_position, rarity, skill requirements, boosts
  - **Pagination**: limit, offset, sorting options
  - **Response**: Rich asset metadata with game context
- `POST /assets/collect` - Collect and enrich assets from EstFor API
- `GET /assets/{asset_id}` - Get enhanced asset with game metadata
- `GET /assets/stats/summary` - Comprehensive collection statistics

#### Enhanced Asset Features

- **Game Integration**: Assets enriched with EstFor Kingdom constants
- **Skill Requirements**: Validate equipment against player skills
- **Equipment Positions**: Filter by HEAD, BODY, WEAPON, etc.
- **Boost Effects**: Track XP boosts, gathering bonuses, combat buffs
- **Asset Categories**: Classify items (helmet, weapon, consumable, material)
- **Rarity Tiers**: Common, Uncommon, Rare, Epic, Legendary

#### Specialized Endpoints

- `GET /assets/search?q={query}` - Search assets by name/description
- `GET /assets/equipment/{position}` - Get items by equipment slot
- `GET /assets/by-skill/{skill_name}` - Get items requiring specific skill
- `GET /assets/categories` - List all categories with counts
- `GET /assets/boosts` - Get items with boost effects
- `POST /assets/compatible` - Check player compatibility with asset
- `POST /assets/migrate` - Migrate legacy assets to enhanced format

#### Example Enhanced Asset Response

```json
{
  "id": "asset_123",
  "item_id": 1,
  "name": "Bronze Helmet",
  "category": "helmet",
  "equip_position": "HEAD",
  "rarity_tier": "COMMON",
  "skill_requirements": { "DEFENCE": 1 },
  "boost_effects": [
    {
      "boost_type": "COMBAT_XP",
      "value": 10,
      "duration": 3600
    }
  ],
  "combat_stats": { "defence": 5 },
  "compatible_skills": ["DEFENCE", "COMBAT"],
  "tradeable": true,
  "display_stats": {
    "name": "Bronze Helmet",
    "category": "helmet",
    "rarity": "COMMON",
    "equip_slot": "HEAD",
    "requirements": { "DEFENCE": 1 }
  }
}
```

### EstFor Game Assets API

The application includes a comprehensive integration with EstFor Kingdom game definitions, providing type-safe access to game constants, items, skills, and more.

#### Game Data Endpoints

- `GET /api/game/items/helmets` - List all helmet items with requirements
- `GET /api/game/items/{item_id}` - Get specific item details
- `POST /api/game/player/can-equip` - Check if player meets item requirements
- `GET /api/game/skills` - List all game skills
- `GET /api/game/skills?category=combat` - Filter skills by category (combat/gathering/crafting)
- `GET /api/game/boost-types` - List all boost types and effects
- `POST /api/game/boost/calculate-effect` - Calculate boost effect on specific skill
- `GET /api/game/equipment-slots` - List all equipment positions

#### EstFor Definitions Integration

The project includes auto-generated Python constants from EstFor Kingdom TypeScript definitions:

- **20+ Enums**: `Skill`, `EquipPosition`, `BoostType`, `ActivityType`, etc.
- **2,400+ Constants**: Item IDs, equipment constants, game values
- **Type-Safe Models**: Pydantic models for game assets with validation

Example usage:

```python
from app.game_constants import Skill, EquipPosition, BRONZE_HELMET

# Check skill requirements
if player.get_skill_level(Skill.DEFENCE) >= 10:
    player.equip_item(IRON_HELMET, EquipPosition.HEAD)
```

To regenerate constants from TypeScript:

```bash
python scripts/generate_estfor_constants.py
```

#### Authentication

- No authentication required (public API)
- Rate limiting
- Request validation with Pydantic models

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

# Test commit to trigger workflow
