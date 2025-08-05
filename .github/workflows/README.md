# 🚀 CI/CD Workflows for Solo Development

This directory contains GitHub Actions workflows designed for solo development with project-specific CI/CD pipelines that follow the local deployment checklist requirements.

## 📋 Workflow Overview

### **Project-Specific Workflows**

Each project has its own independent CI/CD pipeline:

1. **`estfor-ci-cd.yml`** - EstFor Asset Collection System
2. **`nft-gallery-ci-cd.yml`** - NFT Gallery Application
3. **`whispered-video-ci-cd.yml`** - Whispered Video Processing

### **Quick Development Workflow**

- **`quick-test.yml`** - Fast feedback for development branches

## 🎯 Workflow Strategy

### **Feature Branch (Development)**

- ✅ Quick tests and basic quality checks
- ✅ Docker build verification
- ✅ Fast feedback loop (2-5 minutes)

### **Main Branch (Production)**

- ✅ Comprehensive testing and quality checks
- ✅ Security scanning with Trivy
- ✅ Performance testing with k6
- ✅ Production deployment
- ✅ Coverage reporting

## 🔧 Workflow Features

### **1. Test Coverage & Quality**

- **Basic**: Unit tests with 60%+ coverage for feature branches
- **Good**: Integration tests with 75%+ coverage for main branch
- **Excellent**: End-to-end tests with Docker services

### **2. Security Scanning**

- **Trivy**: Docker image vulnerability scanning
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability checking
- **GitHub Security**: SARIF report integration

### **3. Performance Testing**

- **k6 Load Testing**: HTTP endpoint performance
- **Docker Resource Monitoring**: CPU/memory usage
- **Health Check Validation**: Service availability

### **4. Health Checks**

- **HTTP 200**: Service health endpoints
- **Docker Health**: Container readiness probes
- **Service Dependencies**: Database connectivity

### **5. Rollback Strategy**

- **Versioned Tags**: `app:latest`, `app:v1.2`
- **Docker Compose**: Environment-specific configs
- **Artifact Storage**: Docker image preservation

### **6. Monitoring & Alerting**

- **Log Aggregation**: Structured logging
- **Metrics Collection**: Performance data
- **Deployment Notifications**: Success/failure alerts

## 🚀 Usage

### **Automatic Triggers**

Workflows automatically trigger on:

```yaml
# Feature branches
push:
  branches: [develop, feature/*, bugfix/*]
  paths: ["project/**"]

# Pull requests
pull_request:
  branches: [main, develop]
  paths: ["project/**"]
```

### **Manual Triggers**

You can manually trigger workflows from GitHub Actions tab:

1. Go to **Actions** tab in your repository
2. Select the workflow you want to run
3. Click **Run workflow**
4. Choose branch and optional inputs

### **Environment Variables**

Set these secrets in your repository settings:

```bash
# For NFT Gallery (Firestore)
GOOGLE_APPLICATION_CREDENTIALS

# For EstFor (MongoDB)
MONGODB_URI
DATABASE_NAME

# For notifications (optional)
SLACK_WEBHOOK_URL
DISCORD_WEBHOOK_URL
```

## 📊 Coverage Requirements

| Project         | Feature Branch | Main Branch         |
| --------------- | -------------- | ------------------- |
| EstFor          | 60%            | 75%                 |
| NFT Gallery     | 60%            | 70%                 |
| Whispered Video | Basic tests    | Comprehensive tests |

## 🔒 Security Features

### **Vulnerability Scanning**

- **Trivy**: Scans Docker images for CVEs
- **Bandit**: Python security linting
- **Safety**: Checks Python dependencies
- **GitHub Security**: Integrated vulnerability reporting

### **Secrets Management**

- **Environment Variables**: Secure credential storage
- **Docker Secrets**: Production secret injection
- **GitHub Secrets**: Repository-level security

## 📈 Performance Monitoring

### **Load Testing**

```javascript
// k6/load-test.js example
import http from "k6/http";
import { check } from "k6";

export default function () {
  const response = http.get("http://localhost:8000/health");
  check(response, { "status is 200": (r) => r.status === 200 });
}
```

### **Resource Monitoring**

- **CPU Usage**: Container resource limits
- **Memory Usage**: Memory leak detection
- **Response Times**: API performance metrics

## 🛠️ Local Development

### **Pre-commit Checks**

```bash
# Run locally before pushing
cd estfor
black --check .
isort --check-only .
flake8 .
pytest tests/unit/ --cov=app --cov-report=term-missing
```

### **Docker Testing**

```bash
# Test Docker builds locally
docker build -t myapp:test .
docker run --rm myapp:test --help
```

## 📝 Customization

### **Adding New Projects**

1. Create new workflow file: `.github/workflows/new-project-ci-cd.yml`
2. Follow the template structure
3. Update path filters for your project
4. Add project-specific environment variables

### **Modifying Existing Workflows**

Each workflow is modular and can be customized:

```yaml
# Add custom steps
- name: Custom step
  run: |
    echo "Your custom logic here"

# Modify test commands
- name: Run custom tests
  run: |
    python -m pytest tests/custom/
```

### **Environment-Specific Configs**

```yaml
# Development
if: github.ref == 'refs/heads/develop'

# Production
if: github.ref == 'refs/heads/main'

# Feature branches
if: github.event_name == 'pull_request'
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Docker Build Failures**

   - Check Dockerfile syntax
   - Verify dependencies in requirements.txt
   - Ensure proper working directory

2. **Test Failures**

   - Run tests locally first
   - Check environment variables
   - Verify test data setup

3. **Security Scan Issues**
   - Update dependencies
   - Review vulnerability reports
   - Apply security patches

### **Debug Workflows**

```bash
# Enable debug logging
ACTIONS_STEP_DEBUG=true

# Check workflow logs
# Go to Actions tab → Select workflow → View logs
```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Local Deployment Checklist](../estfor/local_deploy.md)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Security Scanning with Trivy](https://aquasecurity.github.io/trivy/)

## 🤝 Contributing

When modifying workflows:

1. Test changes locally first
2. Use feature branches for workflow updates
3. Update this README with changes
4. Follow the existing patterns and structure

---

**Note**: These workflows are designed for solo development. For team environments, consider adding code review requirements and branch protection rules.
