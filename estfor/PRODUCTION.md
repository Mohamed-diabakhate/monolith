# EstFor Asset Collection System - Production Deployment Guide

## 🚀 Overview

This document provides comprehensive guidance for deploying and maintaining the EstFor Asset Collection System in production.

## 📋 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Security Requirements

- Firewall configured
- SSL/TLS certificates
- Secure secrets management
- Regular security updates

## 🔧 Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd estfor
```

### 2. Configure Production Environment

```bash
# Copy production template
cp env.production.template .env.production

# Edit production configuration
nano .env.production
```

### 3. Update Critical Configuration

**⚠️ IMPORTANT**: Update these values in `.env.production`:

```bash
# Security
SECRET_KEY=your-very-secure-secret-key-min-32-characters
REDIS_PASSWORD=your-secure-redis-password
GF_SECURITY_ADMIN_PASSWORD=your-secure-grafana-password

# API Configuration
# EstFor API doesn't require authentication
# ESTFOR_API_KEY=your-actual-estfor-api-key
ESTFOR_API_URL=https://api.estfor.com

# Domain Configuration
ALLOWED_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]
```

### 4. Generate Secure Secrets

```bash
# Generate secure secret key
openssl rand -hex 32

# Generate secure passwords
openssl rand -base64 32
```

## 🚀 Deployment

### Automated Deployment

```bash
# Run production deployment script
./deploy-production.sh
```

### Manual Deployment

```bash
# Build production images
make -f Makefile.prod build-prod

# Start production services
make -f Makefile.prod start-prod

# Verify deployment
make -f Makefile.prod health-check
```

## 📊 Monitoring & Observability

### Service URLs

- **API**: http://localhost:8000
- **API Health**: http://localhost:8000/health/
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **cAdvisor**: http://localhost:8082

### Health Checks

```bash
# Run comprehensive health checks
make -f Makefile.prod health-check

# Check service status
make -f Makefile.prod monitor
```

### Logs

```bash
# View all logs
make -f Makefile.prod logs-prod

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f app
docker-compose -f docker-compose.prod.yml logs -f worker
```

## 🔒 Security

### Security Scanning

```bash
# Install Trivy (recommended)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Run security scan
make -f Makefile.prod security-scan
```

### Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for all sensitive data
3. **Regular security updates** for base images
4. **Network segmentation** with Docker networks
5. **Resource limits** to prevent DoS attacks
6. **Log monitoring** for suspicious activity

## 💾 Backup & Recovery

### Database Backup

```bash
# Create backup
make -f Makefile.prod backup

# Restore from backup
make -f Makefile.prod restore BACKUP_DIR=backups/20231201_120000
```

### Backup Strategy

- **Daily automated backups** (recommended)
- **Weekly full backups**
- **Monthly archive backups**
- **Test restore procedures** regularly

### Backup Script Example

```bash
#!/bin/bash
# Add to crontab: 0 2 * * * /path/to/backup-script.sh

cd /path/to/estfor
make -f Makefile.prod backup

# Upload to cloud storage (example)
aws s3 sync ./backups s3://your-backup-bucket/estfor/
```

## 🔄 Maintenance

### Updates

```bash
# Update production deployment
make -f Makefile.prod update-prod

# Rollback if needed
make -f Makefile.prod rollback
```

### Scaling

```bash
# Scale worker instances
make -f Makefile.prod scale-worker COUNT=3
```

### Resource Management

```bash
# Clean up resources
make -f Makefile.prod clean-prod

# Monitor resource usage
docker stats
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs app

# Check resource usage
docker stats

# Verify configuration
docker-compose -f docker-compose.prod.yml config
```

#### Database Connection Issues

```bash
# Check MongoDB status
docker-compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check connection string
echo $MONGODB_URI
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
make -f Makefile.prod restart-prod

# Scale down if needed
make -f Makefile.prod scale-worker COUNT=1
```

### Emergency Procedures

#### Complete System Restart

```bash
# Stop all services
make -f Makefile.prod stop-prod

# Wait 30 seconds
sleep 30

# Start services
make -f Makefile.prod start-prod

# Verify health
make -f Makefile.prod health-check
```

#### Database Recovery

```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop app worker

# Restore database
make -f Makefile.prod restore BACKUP_DIR=backups/latest

# Start application
docker-compose -f docker-compose.prod.yml start app worker
```

## 📈 Performance Optimization

### Resource Limits

- **App**: 1GB RAM, 0.5 CPU
- **Worker**: 512MB RAM, 0.25 CPU
- **MongoDB**: 2GB RAM, 1.0 CPU
- **Redis**: 512MB RAM, 0.25 CPU

### Performance Monitoring

- **Prometheus metrics** for application performance
- **Grafana dashboards** for visualization
- **cAdvisor** for container metrics
- **Custom metrics** for business KPIs

### Optimization Tips

1. **Database indexing** for query performance
2. **Connection pooling** for database connections
3. **Caching strategies** with Redis
4. **Load balancing** for high availability
5. **CDN** for static assets

## 🔐 SSL/TLS Configuration

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📞 Support

### Monitoring Alerts

- Set up alerts for:
  - High CPU/Memory usage
  - Service health check failures
  - Database connection issues
  - High error rates

### Contact Information

- **System Administrator**: [admin@yourdomain.com]
- **Emergency Contact**: [emergency@yourdomain.com]
- **Documentation**: [docs.yourdomain.com]

## 📝 Change Log

### Version 1.0.0

- Initial production deployment
- Basic monitoring setup
- Security hardening
- Backup procedures

---

**⚠️ Important Notes:**

- Always test changes in staging environment first
- Keep backups before major updates
- Monitor system performance regularly
- Document all changes and procedures
- Train team members on emergency procedures
