# 🚀 CI/CD Setup Guide

## Quick Setup

### 1. Repository Secrets

Add these secrets in your GitHub repository settings:

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

### 2. Branch Protection Rules

Set up branch protection for `main` and `develop`:

- Require status checks to pass
- Require branches to be up to date
- Include administrators

### 3. Environment Variables

Each project uses these environment variables:

| Project         | Variables                        | Purpose               |
| --------------- | -------------------------------- | --------------------- |
| EstFor          | `MONGODB_URI`, `DATABASE_NAME`   | Database connection   |
| NFT Gallery     | `GOOGLE_APPLICATION_CREDENTIALS` | Firestore access      |
| Whispered Video | None                             | Local processing only |

## Coverage Thresholds

| Project         | Feature Branch | Main Branch         |
| --------------- | -------------- | ------------------- |
| EstFor          | 60%            | 75%                 |
| NFT Gallery     | 60%            | 70%                 |
| Whispered Video | Basic tests    | Comprehensive tests |

## Security Settings

- **Trivy**: CRITICAL, HIGH severity only
- **Bandit**: Skip B101, B601
- **Safety**: CRITICAL issues only

## Performance Thresholds

- **Response Time**: 2000ms max
- **Memory Usage**: 512MB max
- **CPU Usage**: 80% max

## Workflow Triggers

### Automatic Triggers

- Push to `main`, `develop`, `feature/*`, `bugfix/*`
- Pull requests to `main`, `develop`
- Path-based filtering for project-specific changes

### Manual Triggers

- GitHub Actions tab → Select workflow → Run workflow

## Troubleshooting

### Common Issues

1. **Docker Build Failures**

   ```bash
   # Test locally first
   docker build -t test .
   docker run --rm test --help
   ```

2. **Test Failures**

   ```bash
   # Run tests locally
   cd project/
   pytest tests/ -v
   ```

3. **Security Scan Issues**
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   ```

### Debug Mode

Enable debug logging:

```bash
ACTIONS_STEP_DEBUG=true
```

## Next Steps

1. Configure your deployment environments
2. Set up monitoring and alerting
3. Customize notification channels
4. Add project-specific requirements

For detailed workflow documentation, see [README.md](./README.md).
