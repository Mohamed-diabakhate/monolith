#!/bin/bash

# Start the monitoring stack for EstFor
echo "🚀 Starting EstFor Monitoring Stack..."

# Start the monitoring services
docker-compose up -d prometheus grafana cadvisor elasticsearch kibana

echo "✅ Monitoring services started!"
echo ""
echo "📊 Access URLs:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo "  cAdvisor:   http://localhost:8080"
echo "  Kibana:     http://localhost:5601"
echo ""
echo "🔧 To start the full application stack:"
echo "  docker-compose up -d"
echo ""
echo "🛑 To stop monitoring services:"
echo "  docker-compose stop prometheus grafana cadvisor elasticsearch kibana" 