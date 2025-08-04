# 📊 Monitoring Configuration Guide

This directory contains the configuration files for the EstFor monitoring stack with **alerting capabilities** for local deployment readiness.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  cAdvisor   │    │ Prometheus  │    │   Grafana   │
│ (Port 8082) │───►│ (Port 9090) │───►│ (Port 3000) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Elasticsearch│    │  Logstash   │    │   Kibana    │
│ (Port 9200) │◄───│ (Port 5044) │◄───│ (Port 5601) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ AlertManager│    │ Alert Rules │    │ Alert Sim.  │
│ (Port 9093) │◄───│ (alert_rules.yml)│◄───│ (alert-simulation.py)│
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📁 File Structure

```
monitoring/
├── README.md                    # This file
├── prometheus.yml              # Prometheus configuration
├── alert_rules.yml             # Alert rules for Prometheus
├── alertmanager.yml            # AlertManager configuration
├── alert-simulation.py         # Alert simulation script
├── grafana/
│   ├── dashboards/
│   │   ├── dashboard.yml       # Dashboard provisioning
│   │   ├── docker-monitoring.json # Sample dashboard
│   │   ├── estfor-dashboard.json  # Main EstFor dashboard
│   │   └── alert-dashboard.json   # Alert monitoring dashboard
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
# Start all monitoring services including AlertManager
./start-monitoring.sh

# Or manually
docker-compose up -d prometheus grafana cadvisor elasticsearch kibana alertmanager
```

### 2. Access Monitoring Tools

| Service      | URL                   | Default Credentials | Purpose                    |
| ------------ | --------------------- | ------------------- | -------------------------- |
| Prometheus   | http://localhost:9090 | None                | Metrics collection         |
| Grafana      | http://localhost:3000 | admin/admin         | Dashboards & visualization |
| AlertManager | http://localhost:9093 | None                | Alert management           |
| cAdvisor     | http://localhost:8082 | None                | Container metrics          |
| Kibana       | http://localhost:5601 | None                | Log visualization          |

### 3. Configure Grafana

1. **Add Prometheus Data Source**

   - URL: `http://prometheus:9090`
   - Access: Proxy
   - Set as default

2. **Import Dashboards**
   - **EstFor Dashboard**: Main system monitoring
   - **Alert Dashboard**: Monitor active alerts and their status
   - **Docker Monitoring**: Container-level metrics

## 🚨 Alerting System

### Alert Rules

The system includes comprehensive alert rules for:

- **High Error Rate**: > 0.1 errors/second for 2 minutes
- **Service Down**: Any service unavailable for 1 minute
- **High Response Time**: 95th percentile > 2 seconds for 3 minutes
- **High CPU Usage**: > 80% for 5 minutes
- **High Memory Usage**: > 85% for 5 minutes
- **MongoDB High Connections**: > 100 active connections
- **Redis High Memory**: > 80% memory usage
- **Disk Space Low**: < 10% available
- **Container Restarts**: Frequent restarts in 15 minutes

### Alert Simulation

Test the alerting system using the provided simulation script:

```bash
# Install required dependencies
pip install requests

# Run alert simulation
python monitoring/alert-simulation.py
```

**Simulation Options:**

1. **High Error Rate**: Generates 404 errors to trigger error rate alerts
2. **High Response Time**: Adds artificial delays to trigger response time alerts
3. **Service Unavailability**: Instructions for manually stopping services
4. **All Simulations**: Runs multiple simulations simultaneously

### Alert Management

- **AlertManager UI**: View and manage alerts at http://localhost:9093
- **Grafana Alert Dashboard**: Monitor alert status and trends
- **Alert Notifications**: Configured for webhook (localhost:5001) for local testing

## ⚙️ Configuration Details

### Prometheus (`prometheus.yml`)

- **Scrape Interval**: 15 seconds
- **Alert Rules**: Loaded from `alert_rules.yml`
- **AlertManager**: Integrated for alert routing
- **Targets**:
  - Prometheus self-monitoring
  - cAdvisor container metrics
  - EstFor application metrics
  - Firestore and Redis metrics

### AlertManager (`alertmanager.yml`)

- **Grouping**: Alerts grouped by alertname and service
- **Timing**: 10s group wait, 10s group interval, 1h repeat interval
- **Receivers**: Webhook configured for local testing
- **Inhibition**: Critical alerts suppress related warnings

### Grafana

- **Admin Password**: admin
- **Auto-provisioning**: Enabled for dashboards and datasources
- **Alert Dashboard**: Dedicated view for monitoring alert status
- **Thresholds**: Visual indicators for alert conditions

## 🔧 Customization

### Adding Custom Alerts

1. **Edit Alert Rules**

   ```yaml
   # In alert_rules.yml
   - alert: CustomAlert
     expr: your_metric > threshold
     for: 5m
     labels:
       severity: warning
     annotations:
       summary: "Custom alert description"
   ```

2. **Custom Metrics**

   ```python
   # In your FastAPI app
   from prometheus_client import Counter, Histogram

   request_count = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
   ```

### Alert Notifications

For production, add notification channels to `alertmanager.yml`:

```yaml
receivers:
  - name: "slack"
    slack_configs:
      - api_url: "YOUR_SLACK_WEBHOOK"
        channel: "#alerts"
  - name: "email"
    email_configs:
      - to: "admin@example.com"
        smarthost: "smtp.example.com:587"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Alerts not firing**

   ```bash
   # Check Prometheus alert rules
   curl http://localhost:9090/api/v1/rules

   # Check AlertManager status
   curl http://localhost:9093/api/v1/status
   ```

2. **AlertManager not receiving alerts**

   ```bash
   # Verify Prometheus-AlertManager connectivity
   docker-compose logs prometheus | grep alertmanager
   ```

3. **Simulation not working**

   ```bash
   # Check if app is running
   curl http://localhost:8000/health

   # Verify monitoring stack is up
   docker-compose ps
   ```

### Performance Tuning

1. **Alert Frequency**

   - Adjust `for` duration in alert rules
   - Modify `group_interval` in AlertManager

2. **Storage Retention**
   - Prometheus: 200h retention (configurable)
   - AlertManager: Persistent storage for alert history

## 📚 Additional Resources

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [cAdvisor GitHub](https://github.com/google/cadvisor)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)

## ✅ Local Deployment Checklist - Monitoring & Alerting

This monitoring setup satisfies the local deployment checklist requirements:

- ✅ **Basic**: TX/RX logs visible via `docker logs`
- ✅ **Good**: Local aggregated logging (ELK/Prometheus via containers)
- ✅ **Excellent**: Metrics collection and alert simulation (high error rate triggers warning)

**To validate:**

1. Start the monitoring stack
2. Run alert simulations
3. Check dashboards for alert visibility
4. Verify AlertManager receives and displays alerts
