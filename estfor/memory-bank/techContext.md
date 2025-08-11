## Runtime and Framework

- **Language/Runtime**: Python 3.11
- **Web Framework**: `FastAPI`
- **ASGI Server**: `uvicorn`
- **Data Validation/Settings**: `pydantic` v2, `pydantic-settings`
- **Serialization**: `orjson`
- **Structured Logging**: `structlog`

## API and Services

- **Primary API**: FastAPI app in `app/main.py` with routers under `app/routers/`
- **External Integration**: EstFor Kingdom API via `httpx` (`app/services/estfor_client.py`)
- **CORS**: FastAPI `CORSMiddleware`

## Data Storage

- **Database**: MongoDB (`mongo:7` in production compose)
  - Drivers: `motor` (async), `pymongo`
  - Default DB: `estfor`
  - Enhanced access layer: `app/database/base.py`, `app/database/enhanced.py`

## Caching, Queue, and State

- **Redis**: `redis:7` (used for container state and optional Celery broker/result)
  - Client: `redis.asyncio`
  - Note: Can be disabled in production; see compose files and `app/config.py`

## Background Processing

- **Task Runner**: `Celery` (optional in production)
  - Broker/Backend: Redis (configurable)
  - Tasks defined in `app/tasks.py`

## Container Automation

- **Docker SDK**: `docker` Python SDK for auto start/stop of containers
- **Idle Monitor**: `app/services/idle_monitor.py` manages idle timeouts
- **Middleware**: Auto-start and health-check middlewares in `app/middleware/`

## Observability and Monitoring

- **Metrics**: `prometheus-client` exposed at `/metrics`
- **Prometheus**: `prom/prometheus` with rules in `monitoring/prometheus.yml`
- **Grafana**: Dashboards provisioned from `monitoring/grafana/`
- **Alertmanager**: Config in `monitoring/alertmanager.yml`
- **Container Metrics**: `cAdvisor`

## Logging

- **ELK Stack (optional)**: Elasticsearch, Logstash, Kibana, Filebeat (dev/local stack via compose)

## Load/Performance Testing

- **k6**: Scripts in `k6/load-test.js`
- **Locust**: Included as a dev dependency

## Security and Rate Limiting

- **Security libs**: `cryptography`, `passlib[bcrypt]`
- **Rate limiting**: `slowapi`
- **Reverse Proxy (optional)**: `nginx` config under `nginx/nginx.conf` (TLS, headers, rate limits)

## Configuration

- **Env Management**: `.env` loaded via `pydantic-settings` / `python-dotenv`
- **Key Settings**: see `app/config.py` for `MONGODB_URI`, `REDIS_URL`, Celery, container automation, etc.

## Testing and Quality

- **Testing**: `pytest`, `pytest-asyncio`, `pytest-cov`
- **Type Checking**: `mypy`
- **Lint/Format**: `flake8`, `black`, `isort`, `bandit`, `safety`
- **Coverage**: configured in `pyproject.toml`

## Documentation and Tooling

- **Docs**: `mkdocs`, `mkdocs-material`
- **Build/Run**: Docker multi-stage `Dockerfile`, `docker-compose*.yml`, `Makefile`

## Environment Profiles

- **Development/Local**: Full stack via `docker-compose.yml` (API, Redis, Prometheus, Grafana, ELK, cAdvisor)
- **Production**: `docker-compose.prod.yml` (API, MongoDB, Prometheus, Grafana, cAdvisor; worker/Redis optional)

Notes:

- This project previously referenced Firestore; current implementation uses MongoDB. Update any remaining Firestore docs accordingly.
- This project uses Elephant-Mongo as a MongoDB server in a local container.
