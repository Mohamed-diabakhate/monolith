#!/bin/bash

# EstFor Asset Collection System - Grafana Dashboard Setup Script

echo "🚀 Setting up Grafana Dashboards for EstFor Asset Collection System"
echo "================================================================"

# Check if Grafana is running
echo "📊 Checking Grafana status..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is running at http://localhost:3000"
else
    echo "❌ Grafana is not running. Please start the services first:"
    echo "   docker-compose up -d"
    exit 1
fi

# Check if Prometheus is running
echo "📈 Checking Prometheus status..."
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "❌ Prometheus is not running. Please start the services first:"
    echo "   docker-compose up -d"
    exit 1
fi

echo ""
echo "🎯 Dashboard Setup Instructions:"
echo "================================="
echo ""
echo "1. Open Grafana in your browser:"
echo "   http://localhost:3000"
echo ""
echo "2. Login with default credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "3. Add Prometheus as a data source:"
echo "   - Go to Configuration > Data Sources"
echo "   - Click 'Add data source'"
echo "   - Select 'Prometheus'"
echo "   - Set URL to: http://prometheus:9090 (internal Docker hostname)"
echo "   - Click 'Save & Test'"
echo "   Note: Use 'prometheus' (not localhost) as Grafana runs inside Docker"
echo ""
echo "4. Access the EstFor Dashboard:"
echo "   - Go to Dashboards > Browse"
echo "   - Look for 'EstFor Asset Collection System'"
echo "   - Or import the dashboard manually from:"
echo "     monitoring/grafana/dashboards/estfor-dashboard.json"
echo ""
echo "5. Available Dashboards:"
echo "   - EstFor Asset Collection System (comprehensive monitoring)"
echo "   - Docker Monitoring (container metrics)"
echo ""
echo "📋 Dashboard Features:"
echo "====================="
echo "✅ System Health Overview"
echo "✅ Application Response Time"
echo "✅ Request Rate"
echo "✅ MongoDB Operations"
echo "✅ Redis Memory Usage"
echo "✅ Container CPU & Memory Usage"
echo "✅ Error Rate Monitoring"
echo "✅ Active Connections"
echo ""
echo "🔧 Manual Dashboard Import (if needed):"
echo "======================================="
echo "1. In Grafana, go to Dashboards > Import"
echo "2. Upload the JSON file: monitoring/grafana/dashboards/estfor-dashboard.json"
echo "3. Select Prometheus as the data source"
echo "4. Click 'Import'"
echo ""
echo "🎉 Setup Complete! Your EstFor monitoring dashboards are ready."
echo ""
echo "📊 Quick Access Links:"
echo "====================="
echo "Grafana: http://localhost:3000"
echo "Prometheus: http://localhost:9090"
echo "FastAPI App: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs" 