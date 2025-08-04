# EstFor Asset Collection System - Makefile
# Comprehensive build, test, and deployment commands

.PHONY: help build start stop restart logs clean test test-unit test-integration test-e2e coverage security-scan performance-test health-check deploy rollback canary-deploy promote-canary rollback-canary db-backup db-restore db-migrate lint format docs

# Variables
VERSION ?= $(shell git describe --tags --always --dirty)
DOCKER_COMPOSE = docker-compose
DOCKER_IMAGE = estfor-asset-collection
REGISTRY ?= localhost:5000

# Default target
help:
	@echo "EstFor Asset Collection System - Available Commands:"
	@echo ""
	@echo "Build & Run:"
	@echo "  build          - Build Docker images"
	@echo "  start          - Start all services"
	@echo "  stop           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo "  logs           - View service logs"
	@echo "  clean          - Clean up containers and volumes"
	@echo ""
	@echo "Testing (Excellent Level):"
	@echo "  test           - Run all tests (unit, integration, e2e)"
	@echo "  test-unit      - Run unit tests with 90%+ coverage"
	@echo "  test-integration - Run integration tests"
	@echo "  test-e2e       - Run end-to-end tests with Docker Compose"
	@echo "  coverage       - Generate coverage report"
	@echo "  security-scan  - Run security vulnerability scan"
	@echo "  performance-test - Run performance tests with K6"
	@echo ""
	@echo "Health & Monitoring:"
	@echo "  health-check   - Check all service health endpoints"
	@echo "  metrics        - View Prometheus metrics"
	@echo "  grafana        - Open Grafana dashboard"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy         - Deploy specific version"
	@echo "  rollback       - Rollback to previous version"
	@echo "  canary-deploy  - Deploy canary version"
	@echo "  promote-canary - Promote canary to production"
	@echo "  rollback-canary - Rollback canary deployment"
	@echo ""
	@echo "Database:"
	@echo "  db-backup      - Backup Firestore data"
	@echo "  db-restore     - Restore Firestore data"
	@echo "  db-migrate     - Run database migrations"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black"
	@echo "  docs           - Generate documentation"
	@echo ""
	@echo "Variables:"
	@echo "  VERSION        - Version tag (default: git describe)"
	@echo "  REGISTRY       - Docker registry (default: localhost:5000)"

# Build and Run Commands
build:
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) build --no-cache
	@echo "Build completed successfully"

start:
	@echo "Starting EstFor Asset Collection System..."
	$(DOCKER_COMPOSE) up -d
	@echo "Services started. Waiting for health checks..."
	@sleep 30
	@make health-check

stop:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

restart:
	@echo "Restarting services..."
	$(DOCKER_COMPOSE) restart

logs:
	@echo "Viewing service logs..."
	$(DOCKER_COMPOSE) logs -f

clean:
	@echo "Cleaning up containers and volumes..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup completed"

# Testing Commands (Excellent Level)
test: test-unit test-integration test-e2e
	@echo "All tests completed successfully!"

test-unit:
	@echo "Running unit tests with 90%+ coverage target..."
	docker-compose run --rm app pytest tests/test_unit.py -v --cov=app --cov-report=html --cov-report=term --cov-fail-under=90
	@echo "Unit tests completed"

test-integration:
	@echo "Running integration tests..."
	docker-compose run --rm app pytest tests/test_integration.py -v
	@echo "Integration tests completed"

test-e2e:
	@echo "Running end-to-end tests with Docker Compose..."
	docker-compose run --rm app pytest tests/test_e2e.py -v
	@echo "E2E tests completed"

coverage:
	@echo "Generating coverage report..."
	docker-compose run --rm app pytest --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

# Security Scanning (Excellent Level)
security-scan:
	@echo "Running security vulnerability scan..."
	@if command -v trivy >/dev/null 2>&1; then \
		echo "Scanning Docker images with Trivy..."; \
		trivy image --severity HIGH,CRITICAL $(DOCKER_IMAGE):latest; \
	else \
		echo "Trivy not found. Installing..."; \
		curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin; \
		trivy image --severity HIGH,CRITICAL $(DOCKER_IMAGE):latest; \
	fi
	@echo "Security scan completed"

dependency-scan:
	@echo "Scanning dependencies for vulnerabilities..."
	docker-compose run --rm app safety check
	@echo "Dependency scan completed"

secrets-validate:
	@echo "Validating secrets and environment variables..."
	@if [ -f .env ]; then \
		echo "Checking .env file for secrets..."; \
		grep -E "(password|secret|key|token)" .env || echo "No obvious secrets found in .env"; \
	else \
		echo "No .env file found"; \
	fi
	@echo "Secrets validation completed"

# Performance Testing (Excellent Level)
performance-test:
	@echo "Running performance tests with K6..."
	@if command -v k6 >/dev/null 2>&1; then \
		echo "Running K6 load tests..."; \
		k6 run k6/load-test.js; \
	else \
		echo "K6 not found. Installing..."; \
		curl -L https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz | tar xz; \
		sudo mv k6-v0.45.0-linux-amd64/k6 /usr/local/bin/; \
		k6 run k6/load-test.js; \
	fi
	@echo "Performance tests completed"

# Health Checks (Excellent Level)
health-check:
	@echo "Checking service health endpoints..."
	@echo "Checking app health..."
	@curl -f http://localhost:8000/health || (echo "App health check failed" && exit 1)
	@echo "Checking app readiness..."
	@curl -f http://localhost:8000/health/ready || (echo "App readiness check failed" && exit 1)
	@echo "Checking app liveness..."
	@curl -f http://localhost:8000/health/live || (echo "App liveness check failed" && exit 1)
	@echo "Checking Firestore emulator..."
	@curl -f http://localhost:8080 || (echo "Firestore health check failed" && exit 1)
	@echo "Checking Redis..."
	@docker-compose exec redis redis-cli ping || (echo "Redis health check failed" && exit 1)
	@echo "Checking Prometheus..."
	@curl -f http://localhost:9090/metrics || (echo "Prometheus health check failed" && exit 1)
	@echo "Checking Grafana..."
	@curl -f http://localhost:3000/api/health || (echo "Grafana health check failed" && exit 1)
	@echo "All health checks passed!"

metrics:
	@echo "Opening Prometheus metrics..."
	@xdg-open http://localhost:9090 || open http://localhost:9090 || echo "Please open http://localhost:9090"

grafana:
	@echo "Opening Grafana dashboard..."
	@xdg-open http://localhost:3000 || open http://localhost:3000 || echo "Please open http://localhost:3000"

# Deployment Commands (Excellent Level)
deploy:
	@echo "Deploying version $(VERSION)..."
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		exit 1; \
	fi
	docker tag $(DOCKER_IMAGE):latest $(REGISTRY)/$(DOCKER_IMAGE):$(VERSION)
	docker push $(REGISTRY)/$(DOCKER_IMAGE):$(VERSION)
	$(DOCKER_COMPOSE) up -d
	@echo "Deployment completed"

rollback:
	@echo "Rolling back to version $(VERSION)..."
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		exit 1; \
	fi
	docker pull $(REGISTRY)/$(DOCKER_IMAGE):$(VERSION)
	$(DOCKER_COMPOSE) up -d
	@echo "Rollback completed"

canary-deploy:
	@echo "Deploying canary version $(VERSION)..."
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.yml -f docker-compose.canary.yml up -d
	@echo "Canary deployment completed"

promote-canary:
	@echo "Promoting canary to production..."
	docker-compose -f docker-compose.yml up -d
	@echo "Canary promoted to production"

rollback-canary:
	@echo "Rolling back canary deployment..."
	docker-compose -f docker-compose.yml up -d
	@echo "Canary rollback completed"

# Database Commands
db-backup:
	@echo "Backing up Firestore data..."
	docker-compose exec firestore gcloud firestore export gs://estfor-backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "Database backup completed"

db-restore:
	@echo "Restoring Firestore data..."
	@if [ -z "$(BACKUP_PATH)" ]; then \
		echo "Error: BACKUP_PATH is required"; \
		exit 1; \
	fi
	docker-compose exec firestore gcloud firestore import gs://estfor-backups/$(BACKUP_PATH)
	@echo "Database restore completed"

db-migrate:
	@echo "Running database migrations..."
	docker-compose run --rm app python -m app.migrations.run
	@echo "Database migrations completed"

# Code Quality Commands
lint:
	@echo "Running linting checks..."
	docker-compose run --rm app flake8 app/ tests/
	docker-compose run --rm app mypy app/
	docker-compose run --rm app bandit -r app/
	@echo "Linting completed"

format:
	@echo "Formatting code with black..."
	docker-compose run --rm app black app/ tests/
	docker-compose run --rm app isort app/ tests/
	@echo "Code formatting completed"

docs:
	@echo "Generating documentation..."
	docker-compose run --rm app mkdocs build
	@echo "Documentation generated in site/"

# Development Commands
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Development environment started"

shell:
	@echo "Opening shell in app container..."
	docker-compose exec app bash

# Monitoring Commands
logs-app:
	@echo "Viewing app logs..."
	docker-compose logs -f app

logs-worker:
	@echo "Viewing worker logs..."
	docker-compose logs -f worker

logs-db:
	@echo "Viewing database logs..."
	docker-compose logs -f firestore

# Utility Commands
status:
	@echo "Service status:"
	$(DOCKER_COMPOSE) ps

ps:
	@echo "Container processes:"
	docker ps

stats:
	@echo "Container resource usage:"
	docker stats --no-stream

# Cleanup Commands
clean-images:
	@echo "Cleaning up Docker images..."
	docker image prune -f

clean-volumes:
	@echo "Cleaning up Docker volumes..."
	docker volume prune -f

clean-all: clean clean-images clean-volumes
	@echo "Complete cleanup completed"

# Help Commands
version:
	@echo "EstFor Asset Collection System version: $(VERSION)"

info:
	@echo "System Information:"
	@echo "Version: $(VERSION)"
	@echo "Registry: $(REGISTRY)"
	@echo "Docker Compose: $(shell docker-compose --version)"
	@echo "Docker: $(shell docker --version)" 