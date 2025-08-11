### System architecture

Describe the high-level system design, major components, and how they interact.

- Runtime: app services in `app/` (APIs in `routers/`, domain logic in `services/`, data access in `database/`, models in `models/`).
- Supporting infrastructure: MongoDB (see `mongo-init/`), monitoring stack in `monitoring/` (Prometheus, Grafana, ELK), reverse proxy in `nginx/`.
- Deployment: Docker Compose files (`docker-compose*.yml`), container image via `Dockerfile`.
- Entry points: API server in `app/main.py`, background worker in `app/worker.py`, periodic tasks in `app/tasks.py`.

Include an updated diagram when available.

### Key technical decisions

Document important choices and their rationale.

- Web framework: FastAPI-style layout under `app/` for async I/O and type hints.
- Database: MongoDB with initialization in `mongo-init/init.js`.
- Observability: Prometheus + Grafana dashboards under `monitoring/grafana/`; logs via Filebeat/Logstash.
- Containerization: Docker for local and production; environment templates in `env.production.template`.
- CI/CD: Separate workflows per project (see `CI_CD_IMPROVEMENTS.md`).

### Design patterns in use

Capture recurring patterns and conventions.

- Layered architecture: `routers/` (transport) → `services/` (application/domain) → `database/` (persistence).
- Dependency separation: configuration via `app/config.py`, shared constants in `app/game_constants.py`.
- Background processing: worker pattern in `app/worker.py`; scheduled tasks in `app/tasks.py`.
- Composition over inheritance for service helpers in `app/services/`.

### Component relationships

Explain how modules depend on and call each other.

- `routers/*.py` expose REST endpoints that call functions in `services/*.py`.
- `services/*.py` orchestrate domain logic and read/write via `database/*.py`.
- `models/*.py` define data shapes passed between layers.
- `middleware/container_middleware.py` adds cross-cutting behavior to requests.
- Monitoring components scrape application metrics and visualize dashboards in `monitoring/grafana/`.

Keep this section synchronized with actual code changes and dependency directions.
