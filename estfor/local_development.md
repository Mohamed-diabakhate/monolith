# 🖥️ Local Monitoring Stack – Setup Summary

This document outlines the setup of a complete local monitoring stack using Docker on macOS. It includes **Prometheus**, **Grafana**, **cAdvisor**, and the **ELK Stack** (Elasticsearch, Kibana) to track metrics and logs for Docker containers and the host machine.

---

## ✅ Components Overview

| Tool              | Purpose                              | Access URL            |
| ----------------- | ------------------------------------ | --------------------- |
| **Prometheus**    | Collects time-series metrics         | http://localhost:9090 |
| **Grafana**       | Dashboards for metrics visualization | http://localhost:3000 |
| **cAdvisor**      | Container-level metrics exporter     | http://localhost:8080 |
| **Elasticsearch** | Stores logs and metrics (if needed)  | http://localhost:9200 |
| **Kibana**        | UI to explore and visualize logs     | http://localhost:5601 |

---

## ⚙️ Prometheus

- Installed via Docker.
- Configured with `prometheus.yml` to scrape:
  - Itself (Prometheus)
  - cAdvisor (for container metrics)
- Scrape Interval: `15s`

```yaml
scrape_configs:  - job_name: 'prometheus'    static_configs:      - targets: ['localhost:9090']  - job_name: 'cadvisor'    static_configs:      - targets: ['host.docker.internal:8080']
```

---

## 📊 Grafana

- Installed via Docker.
- Prometheus added as a data source:
  ```
  http://host.docker.internal:9090
  ```
- Dashboard imported from Grafana.com:
  - **Docker Monitoring** (Dashboard ID: `893`)

---

## 📦 cAdvisor

- Provides live container metrics: CPU, memory, disk, and network.
- Installed using Docker with the required volume mounts.
- Exposes Prometheus-compatible metrics at `/metrics`.
- Access: [http://localhost:8080](http://localhost:8080/)

---

## 🔍 ELK Stack

- Deployed via Docker Compose:
  - **Elasticsearch** for storing and indexing logs.
  - **Kibana** for log visualization.
- Security disabled (`xpack.security.enabled=false`) for local development.
- Persistent volume `esdata` used for Elasticsearch data.

### Run ELK Stack

```bash
docker-compose up -d
```

### `docker-compose.yml` (Simplified)

```yaml
version: '3.7'services:  elasticsearch:    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.2    environment:      - discovery.type=single-node      - xpack.security.enabled=false      - ES_JAVA_OPTS=-Xms1g -Xmx1g    ports:      - "9200:9200"    volumes:      - esdata:/usr/share/elasticsearch/data  kibana:    image: docker.elastic.co/kibana/kibana:8.12.2    environment:      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200    ports:      - "5601:5601"    depends_on:      - elasticsearchvolumes:  esdata:
```

---

## 🚧 Next Steps (Optional)

- 🔄 Add **Filebeat** to ingest Docker logs into Elasticsearch.
- 📈 Add **node-exporter** for host-level system metrics.
- 🔔 Configure **Grafana alerts** based on metric thresholds.
- 🔒 Harden security in ELK (enable auth, use TLS) for production setups.
