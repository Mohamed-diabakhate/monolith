# Repository Structure & CI/CD Configuration

## 📁 Repository Structure

The EstFor project is organized as a root-level repository with the following structure:

```
estfor/
├── .github/
│   └── workflows/
│       ├── build.yaml          # Main CI/CD pipeline
│       └── dependencies.yml    # Dependency management
├── app/                        # FastAPI application code
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── routers/               # API route handlers
│   ├── services/              # External service integrations
│   ├── tasks.py               # Celery background tasks
│   └── worker.py              # Celery worker
├── tests/                     # Test suite
│   ├── conftest.py
│   ├── test_unit.py
│   ├── test_integration.py
│   └── test_e2e.py
├── monitoring/                # Monitoring configuration
├── nginx/                     # Nginx configuration
├── mongo-init/               # MongoDB initialization
├── k6/                       # Performance testing
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
├── docker-compose.staging.yml # Staging environment
├── Dockerfile                # Multi-stage Docker build
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Code quality tool configuration
├── pytest.ini              # Test configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
└── README.md                # Project documentation
```

## 🔄 CI/CD Trigger Configuration

### Build & Test Pipeline (`.github/workflows/build.yaml`)

The main CI/CD pipeline triggers on:

**Events:**

- **Push to main**: Direct pushes to the main branch
- **Pull Request to main**: PRs targeting the main branch

**File Changes:**

- **Application Code**: `app/**`
- **Tests**: `tests/**`
- **Dependencies**: `requirements*.txt`
- **Docker Configuration**: `Dockerfile`, `docker-compose*.yml`
- **Code Quality**: `pyproject.toml`, `pytest.ini`
- **Workflow Files**: `.github/workflows/build.yaml`

### Dependency Management (`.github/workflows/dependencies.yml`)

The dependency management workflow triggers on:

**Events:**

- **Scheduled**: Weekly on Mondays at 9 AM UTC
- **Manual**: Via workflow dispatch
- **Push to main**: Direct pushes to the main branch
- **Pull Request to main**: PRs targeting the main branch

**File Changes:**

- **Dependency Changes**: `requirements*.txt`, `pyproject.toml`
- **Workflow Changes**: `.github/workflows/dependencies.yml`

## 🎯 Trigger Logic

### When CI/CD Runs

The pipeline will automatically trigger when:

**Events occur:**

1. **Push to main**: Direct commits pushed to the main branch
2. **Pull Request to main**: PRs created or updated targeting main branch
3. **Merge to main**: When PRs are merged into main branch

**AND relevant files change:**

1. **Code Changes**: Any modification to application code in `app/` directory
2. **Test Changes**: Updates to test files in `tests/` directory
3. **Dependency Updates**: Changes to `requirements.txt` or `requirements-dev.txt`
4. **Configuration Changes**: Updates to Docker files, Python configuration
5. **Workflow Changes**: Modifications to the CI/CD workflow files themselves

### When CI/CD Does NOT Run

The pipeline will NOT trigger for:

- Documentation changes (unless they affect configuration)
- README updates
- Comment-only changes
- Changes to non-essential files

## 🚀 Deployment Triggers

### Staging Deployment

- **Trigger**: Automatic on pushes to `main` branch (including merges)
- **Condition**: All tests pass and quality gates met
- **Environment**: Staging environment

### Production Deployment

- **Trigger**: Manual on version tags (e.g., `v1.0.0`, `v1.2.3`)
- **Condition**: All tests pass and quality gates met
- **Environment**: Production environment (configurable)

## 📊 Quality Gates

Before any deployment, the following must pass:

1. **Code Quality**: Black formatting, isort imports, flake8 linting
2. **Type Checking**: mypy validation
3. **Security**: Bandit and Trivy vulnerability scanning
4. **Testing**: All unit, integration, and E2E tests
5. **Coverage**: Minimum test coverage requirements
6. **Container Security**: No critical vulnerabilities in Docker images

## 🔧 Local Development

### Pre-commit Hooks

To ensure code quality locally:

```bash
# Install pre-commit hooks
make setup-dev

# Run quality checks
pre-commit run --all-files
```

### Testing Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit      # Unit tests
pytest -m integration  # Integration tests
pytest -m e2e       # End-to-end tests
```

## 📝 Best Practices

### For Developers

1. **Always run pre-commit hooks** before committing
2. **Update dependencies** through the dependency management workflow
3. **Test locally** before pushing changes
4. **Use meaningful commit messages** for better traceability

### For Operations

1. **Monitor CI/CD pipeline** for failures
2. **Review security scan results** regularly
3. **Validate deployments** in staging before production
4. **Keep dependencies updated** through automated workflows

## 🚨 Troubleshooting

### Common Issues

1. **Pipeline not triggering**: Check if changes are in monitored paths
2. **Quality gate failures**: Run pre-commit hooks locally first
3. **Test failures**: Ensure all dependencies are installed
4. **Security scan failures**: Review and address vulnerabilities

### Debug Commands

```bash
# Check what files would trigger CI/CD
git diff --name-only HEAD~1

# Run quality checks locally
make lint
make format
make security-scan

# Test Docker build locally
docker build -t estfor:test .
```

---

**Note**: This configuration ensures that CI/CD runs efficiently by only triggering on relevant changes while maintaining comprehensive quality checks and security scanning.
