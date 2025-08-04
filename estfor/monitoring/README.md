# 📊 Monitoring Configuration Guide

This directory contains the configuration files for the EstFor monitoring stack.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  cAdvisor   │    │ Prometheus  │    │   Grafana   │
│ (Port 8080) │───►│ (Port 9090) │───►│ (Port 3000) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Elasticsearch│    │  Logstash   │    │   Kibana    │
│ (Port 9200) │◄───│ (Port 5044) │◄───│ (Port 5601) │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📁 File Structure

```
monitoring/
├── README.md                    # This file
├── prometheus.yml              # Prometheus configuration
├── grafana/
│   ├── dashboards/
│   │   ├── dashboard.yml       # Dashboard provisioning
│   │   └── docker-monitoring.json # Sample dashboard
│   └── datasources/
│       └── prometheus.yml      # Prometheus datasource
├── logstash/
│   └── pipeline/               # Logstash pipeline configs
└── filebeat/
    └── filebeat.yml           # Filebeat configuration
```

## 🚀 Quick Start

### 1. Start Monitoring Stack

```bash
# Start all monitoring services
./start-monitoring.sh

# Or manually
docker-compose up -d prometheus grafana cadvisor elasticsearch kibana
```

### 2. Access Monitoring Tools

| Service    | URL                   | Default Credentials |
| ---------- | --------------------- | ------------------- |
| Prometheus | http://localhost:9090 | None                |
| Grafana    | http://localhost:3000 | admin/admin         |
| cAdvisor   | http://localhost:8080 | None                |
| Kibana     | http://localhost:5601 | None                |

### 3. Configure Grafana

1. **Add Prometheus Data Source**

   - URL: `http://host.docker.internal:9090`
   - Access: Proxy
   - Set as default

2. **Import Dashboard**
   - Import the Docker Monitoring dashboard (ID: 893)
   - Or use the provided `docker-monitoring.json`

## ⚙️ Configuration Details

### Prometheus (`prometheus.yml`)

- **Scrape Interval**: 15 seconds
- **Targets**:
  - Prometheus self-monitoring
  - cAdvisor container metrics
  - EstFor application metrics
  - Firestore and Redis metrics

### Grafana

- **Admin Password**: admin
- **Auto-provisioning**: Enabled for dashboards and datasources
- **Sample Dashboard**: Docker container monitoring

### cAdvisor

- **Privileged Mode**: Required for container access
- **Metrics**: CPU, memory, disk, network usage
- **Access**: http://localhost:8080

### ELK Stack

- **Elasticsearch**: Single-node setup, security disabled
- **Kibana**: Connected to Elasticsearch
- **Logstash**: Log processing pipeline
- **Filebeat**: Docker log collection

## 🔧 Customization

### Adding Custom Metrics

1. **Application Metrics**

   ```python
   # In your FastAPI app
   from prometheus_client import Counter, Histogram

   request_count = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
   ```

2. **Custom Dashboards**
   - Create JSON dashboard files in `grafana/dashboards/`
   - Use Prometheus queries for custom metrics

### Alerting

1. **Prometheus Alerts**

   - Add alert rules to `prometheus.yml`
   - Configure alertmanager for notifications

2. **Grafana Alerts**
   - Create alerts in Grafana UI
   - Configure notification channels

## 🛠️ Troubleshooting

### Common Issues

1. **cAdvisor not accessible**

   ```bash
   # Check if running in privileged mode
   docker-compose ps cadvisor

   # Check logs
   docker-compose logs cadvisor
   ```

2. **Prometheus targets down**

   ```bash
   # Check target status
   curl http://localhost:9090/api/v1/targets

   # Verify network connectivity
   docker-compose exec prometheus wget -qO- http://cadvisor:8080/metrics
   ```

3. **Grafana datasource issues**
   - Verify Prometheus URL: `http://host.docker.internal:9090`
   - Check network connectivity between containers

### Performance Tuning

1. **Prometheus Storage**

   - Adjust retention time in `prometheus.yml`
   - Monitor disk usage for metrics storage

2. **Elasticsearch**
   - Adjust JVM heap size for your system
   - Monitor memory usage

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [cAdvisor GitHub](https://github.com/google/cadvisor)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
