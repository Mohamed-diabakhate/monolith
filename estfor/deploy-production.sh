#!/bin/bash

# EstFor Asset Collection System - Production Deployment Script
set -e

echo "🚀 Starting Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it and try again."
    exit 1
fi

# Check if production environment file exists
if [ ! -f ".env.production" ]; then
    print_error "Production environment file (.env.production) not found!"
    print_warning "Please copy env.production.template to .env.production and configure it."
    exit 1
fi

# Validate production environment file
print_status "Validating production environment configuration..."

# Check for placeholder values
if grep -q "CHANGE_ME" .env.production; then
    print_error "Found placeholder values in .env.production. Please update all CHANGE_ME values."
    exit 1
fi

# Check for secure secret key
if grep -q "your-secret-key-change-in-production" .env.production; then
    print_error "Please update SECRET_KEY in .env.production to a secure value."
    exit 1
fi

print_status "Environment validation passed."

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Clean up old images (optional)
read -p "Do you want to clean up old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up old images..."
    docker system prune -f
fi

# Build production images
print_status "Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Security scan (if trivy is available)
if command -v trivy &> /dev/null; then
    print_status "Running security scan on images..."
    trivy image --severity HIGH,CRITICAL estfor-app:production || print_warning "Security scan found issues. Review and address them."
    trivy image --severity HIGH,CRITICAL estfor-worker:production || print_warning "Security scan found issues. Review and address them."
else
    print_warning "Trivy not found. Skipping security scan. Consider installing trivy for image vulnerability scanning."
fi

# Start production services
print_status "Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
timeout=300
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
        print_status "All services are healthy!"
        break
    fi
    sleep 10
    elapsed=$((elapsed + 10))
    print_status "Waiting for services... ($elapsed/$timeout seconds)"
done

if [ $elapsed -ge $timeout ]; then
    print_error "Timeout waiting for services to be healthy."
    docker-compose -f docker-compose.prod.yml ps
    exit 1
fi

# Run health checks
print_status "Running health checks..."

# Check API health
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    print_status "API health check passed"
else
    print_error "API health check failed"
    exit 1
fi

# Check MongoDB
if docker-compose -f docker-compose.prod.yml exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    print_status "MongoDB health check passed"
else
    print_error "MongoDB health check failed"
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "Redis health check passed"
else
    print_error "Redis health check failed"
    exit 1
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_status "Prometheus health check passed"
else
    print_error "Prometheus health check failed"
    exit 1
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    print_status "Grafana health check passed"
else
    print_error "Grafana health check failed"
    exit 1
fi

print_status "All health checks passed!"

# Show service status
print_status "Production deployment completed successfully!"
echo
echo "Service Status:"
docker-compose -f docker-compose.prod.yml ps
echo
echo "Service URLs:"
echo "  API: http://localhost:8000"
echo "  API Health: http://localhost:8000/health/"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000 (admin/CHANGE_ME_TO_SECURE_PASSWORD)"
echo "  cAdvisor: http://localhost:8082"
echo
echo "Next steps:"
echo "  1. Configure Grafana dashboards"
echo "  2. Set up monitoring alerts"
echo "  3. Configure backup strategies"
echo "  4. Set up SSL/TLS certificates"
echo "  5. Configure firewall rules"
echo
print_status "Deployment completed successfully! 🎉" 