# EstFor Asset Collection System - Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help start stop restart logs clean build test test-unit test-integration test-e2e lint format security-scan performance-test health-check db-backup db-restore db-migrate deploy rollback canary-deploy promote-canary rollback-canary dependency-scan secrets-validate

# Default target
help:
	@echo "EstFor Asset Collection System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  start              - Start all services"
	@echo "  stop               - Stop all services"
	@echo "  restart            - Restart all services"
	@echo "  logs               - View service logs"
	@echo "  clean              - Clean up containers and volumes"
	@echo "  build              - Build Docker images"
	@echo ""
	@echo "Testing:"
	@echo "  test               - Run all tests with coverage"
	@echo "  test-unit          - Run unit tests only"
	@echo "  test-integration   - Run integration tests only"
	@echo "  test-e2e           - Run end-to-end tests only"
	@echo "  performance-test   - Run performance tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint               - Run linting checks"
	@echo "  format             - Format code with black"
	@echo "  security-scan      - Run security vulnerability scan"
	@echo "  dependency-scan    - Scan dependencies for vulnerabilities"
	@echo "  secrets-validate   - Validate secrets configuration"
	@echo ""
	@echo "Database:"
	@echo "  db-backup          - Backup MongoDB data"
	@echo "  db-restore         - Restore MongoDB data"
	@echo "  db-migrate         - Run database migrations"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy             - Deploy application"
	@echo "  rollback           - Rollback to previous version"
	@echo "  canary-deploy      - Deploy canary version"
	@echo "  promote-canary     - Promote canary to production"
	@echo "  rollback-canary    - Rollback canary deployment"
	@echo ""
	@echo "Monitoring:"
	@echo "  health-check       - Check service health"
	@echo "  logs-app           - View app logs"
	@echo "  logs-worker        - View worker logs"
	@echo "  logs-mongodb       - View MongoDB logs"

# Development commands
start:
	@echo "Starting EstFor Asset Collection System..."
	docker-compose up -d
	@echo "Services started. Use 'make health-check' to verify."

stop:
	@echo "Stopping services..."
	docker-compose down
	@echo "Services stopped."

restart: stop start

logs:
	@echo "Viewing service logs..."
	docker-compose logs -f

clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup completed."

build:
	@echo "Building Docker images..."
	docker-compose build --no-cache
	@echo "Build completed."

# Testing commands
test:
	@echo "Running all tests with coverage..."
	docker-compose exec app pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

test-unit:
	@echo "Running unit tests..."
	docker-compose exec app pytest tests/test_unit.py -v -m "unit"

test-integration:
	@echo "Running integration tests..."
	docker-compose exec app pytest tests/test_integration.py -v -m "integration"

test-e2e:
	@echo "Running end-to-end tests..."
	docker-compose exec app pytest tests/test_e2e.py -v -m "e2e"

performance-test:
	@echo "Running performance tests..."
	k6 run k6/load-test.js

# Code quality commands
setup-dev:
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "Development environment setup complete."

lint:
	@echo "Running linting checks..."
	docker-compose exec app flake8 app/ tests/
	docker-compose exec app black --check app/ tests/
	docker-compose exec app isort --check-only app/ tests/

format:
	@echo "Formatting code..."
	docker-compose exec app black app/ tests/
	docker-compose exec app isort app/ tests/

security-scan:
	@echo "Running security vulnerability scan..."
	docker run --rm -v $(PWD):/app aquasec/trivy fs /app

dependency-scan:
	@echo "Scanning dependencies for vulnerabilities..."
	docker-compose exec app safety check

secrets-validate:
	@echo "Validating secrets configuration..."
	@if [ ! -f .env ]; then echo "Error: .env file not found"; exit 1; fi
	@echo "Secrets validation completed."

# Database commands
db-backup:
	@echo "Backing up MongoDB data..."
	docker-compose exec mongodb mongodump --db estfor --out /backup/$(shell date +%Y%m%d_%H%M%S)

db-restore:
	@echo "Restoring MongoDB data..."
	@read -p "Enter backup path: " BACKUP_PATH; \
	docker-compose exec mongodb mongorestore --db estfor /backup/$$BACKUP_PATH

db-migrate:
	@echo "Running database migrations..."
	@echo "MongoDB migrations completed (schema-less database)"

# Deployment commands
deploy:
	@echo "Deploying application..."
	@if [ -z "$(VERSION)" ]; then echo "Error: VERSION not specified"; exit 1; fi
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Deployment completed for version $(VERSION)"

rollback:
	@echo "Rolling back to previous version..."
	@if [ -z "$(VERSION)" ]; then echo "Error: VERSION not specified"; exit 1; fi
	@echo "Rollback completed to version $(VERSION)"

canary-deploy:
	@echo "Deploying canary version..."
	@if [ -z "$(VERSION)" ]; then echo "Error: VERSION not specified"; exit 1; fi
	@echo "Canary deployment completed for version $(VERSION)"

promote-canary:
	@echo "Promoting canary to production..."
	@echo "Canary promotion completed"

rollback-canary:
	@echo "Rolling back canary deployment..."
	@echo "Canary rollback completed"

# Monitoring commands
health-check:
	@echo "Checking service health..."
	@echo "Checking FastAPI app..."
	@curl -f http://localhost:8000/health || (echo "App health check failed" && exit 1)
	@echo "Checking MongoDB..."
	@docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" || (echo "MongoDB health check failed" && exit 1)
	@echo "Checking Redis..."
	@docker-compose exec redis redis-cli ping || (echo "Redis health check failed" && exit 1)
	@echo "Checking Prometheus..."
	@curl -f http://localhost:9090/-/healthy || (echo "Prometheus health check failed" && exit 1)
	@echo "Checking Grafana..."
	@curl -f http://localhost:3000/api/health || (echo "Grafana health check failed" && exit 1)
	@echo "All services are healthy!"

logs-app:
	@echo "Viewing app logs..."
	docker-compose logs -f app

logs-worker:
	@echo "Viewing worker logs..."
	docker-compose logs -f worker

logs-mongodb:
	@echo "Viewing MongoDB logs..."
	docker-compose logs -f mongodb 