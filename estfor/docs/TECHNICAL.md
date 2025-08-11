# EstFor Technical Documentation

This document provides comprehensive technical information for developers, DevOps engineers, and advanced users working with the EstFor Asset Collection System.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Service Components](#service-components)
- [Database Design](#database-design)
- [Game Integration](#game-integration)
- [Development Setup](#development-setup)
- [Testing Strategy](#testing-strategy)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Performance Optimization](#performance-optimization)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Architecture

The EstFor Asset Collection System follows a microservices architecture pattern with 11 interconnected Docker services:

```
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  EstFor Kingdom │    │   Player Data   │                │
│  │      API        │    │   (External)    │                │
│  └─────────┬───────┘    └─────────────────┘                │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   FastAPI App   │◄──►│  Celery Worker  │                │
│  │   (Port 8000)   │    │  (Background)   │                │
│  └─────────┬───────┘    └─────────┬───────┘                │
└───────────┼─────────────────────┼─────────────────────────────┘
            │                     │
┌───────────▼─────────────────────▼─────────────────────────────┐
│                    Data Layer                                 │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │    MongoDB      │    │     Redis       │                │
│  │  (Port 27017)   │    │  (Port 6379)    │                │
│  └─────────────────┘    └─────────────────┘                │
└───────────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────────┐
│                  Observability Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐   │
│  │ Prometheus  │ │   Grafana   │ │       ELK Stack         │   │
│  │(Port 9090)  │ │(Port 3000)  │ │ (Elasticsearch/Kibana)  │   │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI 0.104+ | High-performance async API with automatic documentation |
| **Database** | MongoDB 7.0 | Document-based storage with flexible schema |
| **Cache** | Redis 7 | Session management, rate limiting, task queuing |
| **Background Jobs** | Celery 5.3+ | Asynchronous task processing |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Logging** | ELK Stack | Centralized log aggregation and analysis |
| **Container Runtime** | Docker + Docker Compose | Service orchestration |
| **Load Testing** | k6 | Performance testing and validation |

## Service Components

### 1. FastAPI Application (`app`)

**Purpose**: Main HTTP API server handling client requests

**Key Features**:
- Async/await throughout for high concurrency
- Automatic OpenAPI documentation generation
- Pydantic models for request/response validation
- Custom middleware for logging and error handling
- Health check endpoints for monitoring

**Configuration**:
```yaml
# docker-compose.yml
app:
  build:
    target: production
  ports:
    - "8000:8000"
  environment:
    - WORKERS=4
    - LOG_LEVEL=INFO
  resources:
    limits:
      memory: 512M
      cpus: "0.5"
```

### 2. Background Worker (`worker`)

**Purpose**: Processes async tasks like asset collection and enrichment

**Key Features**:
- Celery-based task queue processing
- Asset collection from EstFor Kingdom API
- Asset enrichment with game metadata
- Error handling and retry logic
- Progress tracking and status updates

**Task Types**:
- `collect_assets_task`: Fetch assets from external API
- `enrich_assets_task`: Add game metadata to raw assets
- `cleanup_old_assets_task`: Remove stale data

### 3. MongoDB Database (`mongodb`)

**Purpose**: Primary data storage for assets and system data

**Configuration**:
```yaml
mongodb:
  image: mongo:7.0
  environment:
    - MONGO_INITDB_ROOT_USERNAME=Mongo
    - MONGO_INITDB_ROOT_PASSWORD=Mongo123456
    - MONGO_INITDB_DATABASE=estfor
  volumes:
    - mongodb_data:/data/db
```

**Collections**:
- `all_assets`: Enhanced asset data with game metadata
- `raw_assets`: Original unprocessed asset data
- `collection_stats`: Collection metrics and timestamps

### 4. Redis Cache (`redis`)

**Purpose**: High-speed caching and session storage

**Use Cases**:
- API response caching (30-second TTL)
- Rate limiting counters
- Celery task queue and results backend
- Session storage for future authentication

### 5. Monitoring Stack

#### Prometheus (`prometheus`)
- **Purpose**: Time-series metrics collection
- **Metrics**: Custom application metrics, container metrics via cAdvisor
- **Configuration**: `monitoring/prometheus.yml`
- **Retention**: 15 days of metrics data

#### Grafana (`grafana`)
- **Purpose**: Metrics visualization and dashboards
- **Dashboards**: System metrics, business metrics, asset collection stats
- **Access**: http://localhost:3000 (admin/admin)
- **Data Sources**: Prometheus, Elasticsearch

#### ELK Stack
- **Elasticsearch**: Log storage and indexing
- **Kibana**: Log visualization and analysis
- **Filebeat**: Log shipping from containers
- **Logstash**: Log processing and transformation

## Database Design

### MongoDB Schema

#### Enhanced Asset Document
```javascript
{
  _id: ObjectId,
  asset_id: String,           // Unique identifier from source
  item_id: Number,            // EstFor game item ID
  name: String,
  description: String,
  category: String,           // helmet, weapon, consumable, etc.
  equip_position: String,     // HEAD, BODY, WEAPON, etc.
  rarity_tier: String,        // COMMON, RARE, EPIC, LEGENDARY
  skill_requirements: {       // Required skills to use item
    "DEFENCE": Number,
    "MELEE": Number,
    // ... other skills
  },
  boost_effects: [{           // XP/bonus effects
    boost_type: String,
    value: Number,
    duration: Number
  }],
  combat_stats: {             // Combat-related stats
    defence: Number,
    melee: Number,
    magic: Number,
    // ... other stats
  },
  compatible_skills: [String], // Skills this item works with
  required_level: Number,      // Minimum level to use
  tradeable: Boolean,
  display_stats: Object,       // Pre-computed display data
  created_at: DateTime,
  updated_at: DateTime,
  source: String,             // api.estfor.com
  enhancement: String         // estfor_game_constants
}
```

### Indexes

```javascript
// Performance indexes
db.all_assets.createIndex({"category": 1})
db.all_assets.createIndex({"equip_position": 1})
db.all_assets.createIndex({"rarity_tier": 1})
db.all_assets.createIndex({"skill_requirements.DEFENCE": 1})
db.all_assets.createIndex({"skill_requirements.MELEE": 1})
db.all_assets.createIndex({"name": "text", "description": "text"})

// Compound indexes for common queries
db.all_assets.createIndex({"category": 1, "rarity_tier": 1})
db.all_assets.createIndex({"equip_position": 1, "required_level": 1})
```

## Game Integration

### EstFor Kingdom Constants

The system includes auto-generated Python constants from EstFor Kingdom TypeScript definitions:

#### Generation Process
1. **Source**: TypeScript/AssemblyScript files in `estfor-definitions/`
2. **Parser**: `scripts/generate_estfor_constants.py`
3. **Output**: `app/game_constants.py` (2,400+ constants)
4. **Validation**: Comprehensive test suite ensuring accuracy

#### Key Enums Generated
```python
class Skill(IntEnum):
    NONE = 0
    COMBAT = 1
    MELEE = 2
    RANGED = 3
    MAGIC = 4
    DEFENCE = 5
    HEALTH = 6
    SMITHING = 7
    MINING = 8
    # ... 15 more skills

class EquipPosition(IntEnum):
    NONE = 0
    HEAD = 1
    NECK = 2
    BODY = 3
    ARMS = 4
    LEGS = 5
    FEET = 6
    RING = 7
    RESERVED_COMBAT = 8
    # ... more positions

class BoostType(IntEnum):
    NONE = 0
    COMBAT_XP = 1
    NON_COMBAT_XP = 2
    MELEE_XP = 3
    RANGED_XP = 4
    # ... 20+ boost types
```

#### Asset Enrichment Process
```python
# app/services/asset_enrichment.py
class AssetEnrichmentService:
    def enrich_asset(self, raw_asset: Dict) -> EstForAsset:
        # 1. Determine category from name patterns
        category = self._determine_category(raw_asset['name'])
        
        # 2. Map to equipment position if applicable  
        equip_position = self._get_equipment_position(category)
        
        # 3. Extract skill requirements from description
        skills = self._extract_skill_requirements(raw_asset)
        
        # 4. Determine rarity tier
        rarity = self._determine_rarity(raw_asset)
        
        # 5. Extract boost effects
        boosts = self._extract_boost_effects(raw_asset)
        
        return EstForAsset(...)
```

## Development Setup

### Local Environment

#### Prerequisites
```bash
# Required software
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- Make (GNU Make)
- Git

# Recommended tools
- VS Code with Python extension
- MongoDB Compass (GUI client)
- Postman (API testing)
```

#### Environment Configuration
```bash
# .env file structure
# Database
MONGODB_URI=mongodb://Mongo:Mongo123456@mongodb:27017/estfor?authSource=admin
DATABASE_NAME=estfor
COLLECTION_NAME=all_assets

# Redis
REDIS_URL=redis://redis:6379/0

# Application
LOG_LEVEL=DEBUG
ENVIRONMENT=development
API_VERSION=v1
WORKERS=1  # Single worker for development

# EstFor API
ESTFOR_API_URL=https://api.estfor.com
ESTFOR_API_TIMEOUT=30

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ELK_ENABLED=true
```

#### Development Workflow
```bash
# 1. Initial setup
git clone <repository>
cd estfor
cp .env.example .env

# 2. Start development environment
make dev  # Starts with hot reload enabled

# 3. Code quality checks
make lint     # Runs all linting tools
make format   # Auto-formats code
make test     # Runs test suite

# 4. Database operations
make db-reset     # Reset database to clean state
make db-seed      # Load test data
make db-migrate   # Run migrations
```

### IDE Configuration

#### VS Code Settings
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".coverage": true
  }
}
```

### Code Quality Tools

#### Configuration Files
```python
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=app --cov-report=html"
```

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- **Location**: `tests/test_unit.py`
- **Purpose**: Test individual functions and classes in isolation
- **Coverage**: Business logic, utility functions, data validation
- **Mocking**: All external dependencies (database, API calls)

#### 2. Integration Tests
- **Location**: `tests/test_enhanced_assets.py`
- **Purpose**: Test component interactions with real dependencies
- **Coverage**: API endpoints, database operations, asset enrichment
- **Environment**: Uses test database and Redis instance

#### 3. End-to-End Tests
- **Location**: `tests/test_e2e.py`
- **Purpose**: Test complete user workflows
- **Coverage**: Asset collection, API queries, monitoring endpoints
- **Environment**: Full Docker stack

#### 4. Game Integration Tests
- **Location**: `tests/test_game_constants.py`
- **Purpose**: Validate EstFor Kingdom integration
- **Coverage**: Constant generation, asset enrichment, game logic
- **Validation**: Type safety, enum values, constant accuracy

### Test Execution

```bash
# Run all tests with coverage
make test
# Output: 90%+ coverage required

# Run specific test categories
pytest tests/test_unit.py -v
pytest tests/test_enhanced_assets.py -v
pytest tests/test_game_constants.py -v

# Run tests with specific markers
pytest -m "unit" -v          # Unit tests only
pytest -m "integration" -v   # Integration tests only
pytest -m "e2e" -v          # End-to-end tests only

# Performance testing
pytest tests/test_performance.py -v

# Run tests in parallel (faster execution)
pytest -n auto -v
```

### Test Database

```bash
# Setup test database
docker-compose -f docker-compose.test.yml up -d mongodb-test

# Run integration tests against test DB
MONGODB_URI=mongodb://localhost:27018/estfor_test pytest tests/test_enhanced_assets.py
```

## Deployment

### Docker Multi-stage Build

#### Dockerfile Structure
```dockerfile
# Base stage - Common dependencies
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage - Hot reload enabled
FROM base AS development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage - Optimized for performance
FROM base AS production
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Worker stage - Background task processing
FROM base AS worker
COPY app/ ./app/
CMD ["python", "-m", "app.worker"]
```

### Environment-specific Configurations

#### Development (`docker-compose.yml`)
```yaml
services:
  app:
    build:
      target: development
    volumes:
      - ./app:/app/app  # Hot reload
    environment:
      - LOG_LEVEL=DEBUG
      - WORKERS=1
```

#### Production (`docker-compose.prod.yml`)
```yaml
services:
  app:
    build:
      target: production
    environment:
      - LOG_LEVEL=INFO
      - WORKERS=4
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
        reservations:
          memory: 512M
          cpus: "0.5"
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/estfor-ci-cd.yml
name: EstFor CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        black --check app/
        isort --check app/
        flake8 app/
        mypy app/
    
    - name: Run tests
      run: pytest --cov=app --cov-fail-under=90
    
    - name: Build Docker image
      run: docker build -t estfor:${{ github.sha }} .
    
    - name: Security scan
      run: |
        docker run --rm -v $(pwd):/workspace \
          aquasec/trivy filesystem --exit-code 1 /workspace
```

### Production Deployment

#### Using Docker Swarm
```yaml
# docker-stack.yml
version: '3.8'
services:
  app:
    image: estfor/api:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    ports:
      - "8000:8000"
    networks:
      - estfor-network
```

#### Using Kubernetes
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: estfor-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: estfor-api
  template:
    spec:
      containers:
      - name: estfor-api
        image: estfor/api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## Monitoring & Observability

### Metrics Collection

#### Custom Application Metrics
```python
# app/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
REQUEST_ERRORS = Counter('http_errors_total', 'HTTP errors', ['status_code'])

# Business metrics
ASSETS_COLLECTED = Counter('assets_collected_total', 'Total assets collected')
ASSETS_ENRICHED = Counter('assets_enriched_total', 'Total assets enriched')
COLLECTION_DURATION = Histogram('collection_duration_seconds', 'Asset collection duration')

# Database metrics
DB_CONNECTIONS = Gauge('db_connections_active', 'Active database connections')
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration')
```

#### Alert Rules
```yaml
# monitoring/alerts.yml
groups:
  - name: estfor_alerts
    rules:
    - alert: HighErrorRate
      expr: rate(http_errors_total[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: High error rate detected
        description: Error rate is {{ $value }} errors/sec
    
    - alert: SlowResponseTime
      expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: Slow response time
        description: 95th percentile response time is {{ $value }}s
```

### Logging Strategy

#### Structured Logging
```python
# app/utils/logging.py
import structlog

logger = structlog.get_logger()

# Usage in application
logger.info(
    "Asset collection completed",
    collection_id="abc123",
    assets_count=500,
    duration_seconds=30.5,
    source="api.estfor.com"
)
```

#### Log Aggregation
```yaml
# filebeat/filebeat.yml
filebeat.inputs:
- type: docker
  containers.ids:
    - "*"
  processors:
  - add_docker_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  template.settings:
    index.number_of_shards: 1
    index.number_of_replicas: 0
```

## Performance Optimization

### Database Optimization

#### Connection Pooling
```python
# app/database/connection.py
from motor.motor_asyncio import AsyncIOMotorClient

class DatabaseManager:
    def __init__(self):
        self.client = AsyncIOMotorClient(
            MONGODB_URI,
            maxPoolSize=20,
            minPoolSize=5,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000
        )
```

#### Query Optimization
```python
# Efficient asset queries
async def get_assets_optimized(filters: AssetFilter):
    pipeline = [
        {"$match": build_filter_query(filters)},
        {"$sort": {"created_at": -1}},
        {"$skip": filters.offset},
        {"$limit": filters.limit},
        {
            "$project": {
                "_id": 0,
                "asset_id": 1,
                "name": 1,
                "category": 1,
                "rarity_tier": 1,
                "display_stats": 1
            }
        }
    ]
    return await collection.aggregate(pipeline).to_list(length=None)
```

### Caching Strategy

#### Redis Caching
```python
# app/utils/cache.py
import redis.asyncio as redis

class CacheManager:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)
    
    async def get_cached_assets(self, cache_key: str):
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_assets(self, cache_key: str, data: list, ttl: int = 300):
        await self.redis.setex(
            cache_key, 
            ttl, 
            json.dumps(data, default=str)
        )
```

### Load Testing

#### k6 Performance Tests
```javascript
// k6/load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up
    { duration: '1m', target: 100 },   // Stay at 100 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],   // 95% under 200ms
    http_req_failed: ['rate<0.01'],     // Error rate under 1%
  },
};

export default function() {
  let response = http.get('http://localhost:8000/assets/?limit=20');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

## Security

### Container Security

#### Security Scanning
```bash
# Dockerfile security best practices
FROM python:3.11-slim AS base

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Use non-root user
USER appuser
WORKDIR /app

# Copy with proper ownership
COPY --chown=appuser:appuser . .
```

#### Vulnerability Scanning
```yaml
# Security scanning in CI
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'estfor:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy scan results to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

### Application Security

#### Input Validation
```python
# app/models/validators.py
from pydantic import BaseModel, validator

class AssetFilter(BaseModel):
    category: Optional[str] = None
    limit: int = 50
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v and v not in VALID_CATEGORIES:
            raise ValueError(f'Invalid category: {v}')
        return v
```

#### Rate Limiting
```python
# app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/assets/")
@limiter.limit("100/minute")
async def get_assets(request: Request):
    # Asset retrieval logic
    pass
```

## Troubleshooting

### Common Issues and Solutions

#### 1. High Memory Usage
```bash
# Symptoms
- Container OOM kills
- Slow response times
- High swap usage

# Diagnosis
docker stats
docker-compose logs app | grep -i memory

# Solutions
- Increase container memory limits
- Optimize database queries
- Implement connection pooling
- Add pagination to large responses
```

#### 2. Database Connection Issues
```bash
# Symptoms
- "Connection refused" errors
- Timeout errors
- Authentication failures

# Diagnosis
docker-compose logs mongodb
mongosh mongodb://Mongo:Mongo123456@localhost:27017/estfor?authSource=admin

# Solutions
- Check MongoDB container status
- Verify connection string
- Check network connectivity
- Review authentication credentials
```

#### 3. Performance Degradation
```bash
# Symptoms
- Slow API responses
- High CPU usage
- Database query timeouts

# Diagnosis
curl -o /dev/null -s -w "%{time_total}\n" http://localhost:8000/assets/
docker-compose exec mongodb mongosh --eval "db.all_assets.explain().find({})"

# Solutions
- Add database indexes
- Implement caching
- Optimize asset enrichment
- Scale horizontally
```

### Debug Mode

#### Enable Verbose Logging
```bash
# Set environment variables
export LOG_LEVEL=DEBUG
export MONGODB_DEBUG=true

# Restart services with debug logging
docker-compose down
docker-compose up -d

# View debug logs
docker-compose logs -f app
```

#### Database Debugging
```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh -u Mongo -p Mongo123456 --authenticationDatabase admin estfor

# Check collection stats
db.all_assets.stats()

# Analyze slow queries
db.setProfilingLevel(2)
db.system.profile.find().limit(5).sort({ts:-1}).pretty()

# Check indexes
db.all_assets.getIndexes()
```

### Performance Monitoring

#### Real-time Metrics
```bash
# System resource usage
docker stats --no-stream

# Database performance
docker-compose exec mongodb mongosh --eval "db.serverStatus().connections"

# API response times
curl -o /dev/null -s -w "Connect: %{time_connect}\nTTFB: %{time_starttransfer}\nTotal: %{time_total}\n" \
  http://localhost:8000/assets/
```

#### Health Check Endpoints
```bash
# Application health
curl http://localhost:8000/health | jq

# Database connectivity
curl http://localhost:8000/health/ready | jq

# Service liveness
curl http://localhost:8000/health/live | jq
```

---

This technical documentation provides comprehensive information for working with the EstFor Asset Collection System at an advanced level. For basic usage, refer to the main [README.md](README.md).