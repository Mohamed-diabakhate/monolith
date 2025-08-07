# EstFor Asset Collection System

> A powerful Docker-based API for collecting, enriching, and managing EstFor Kingdom gaming assets with comprehensive monitoring.

[![Build Status](https://github.com/your-repo/estfor/workflows/CI/badge.svg)](https://github.com/your-repo/estfor/actions)
[![Docker Image](https://img.shields.io/docker/image-size/estfor/api)](https://hub.docker.com/r/estfor/api)
[![API Documentation](https://img.shields.io/badge/API-Documentation-blue)](http://localhost:8000/docs)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 2GB RAM (minimum)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd estfor
cp .env.example .env
```

### 2. Start Services
```bash
# Start all services (API, database, monitoring)
make start

# Or using Docker Compose directly
docker-compose up -d
```

### 3. Access Your API
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Monitoring**: http://localhost:3000 (admin/admin)

### 4. Collect Assets
```bash
# Collect EstFor Kingdom assets (takes ~30 seconds)
curl -X POST http://localhost:8000/assets/collect

# View collected assets
curl http://localhost:8000/assets/
```

That's it! You now have a fully functional EstFor asset API with monitoring.

## ✨ What You Get

### 🎮 EstFor Kingdom Integration
- **Real-time Asset Collection**: Automatically fetch latest assets from EstFor Kingdom API
- **Enhanced Game Data**: Assets enriched with categories, rarity, skill requirements, and boost effects
- **Type-Safe Game Constants**: 2,400+ auto-generated constants from official game definitions

### 🔍 Powerful Asset API
- **Advanced Filtering**: Search by category, equipment position, skills, rarity, and more
- **Game Integration**: Equipment compatibility checking with player skill levels
- **Rich Metadata**: Combat stats, skill requirements, boost effects, and trading information

### 📊 Production Monitoring
- **Real-time Dashboards**: Grafana dashboards for system and business metrics
- **Centralized Logging**: ELK stack for comprehensive log analysis
- **Health Monitoring**: Automated health checks and alerting

## 🎯 Key Features

| Feature | Description | Example |
|---------|-------------|---------|
| **Asset Enrichment** | Transforms raw API data into rich game objects | `Bronze Helmet` → `{category: "helmet", position: "HEAD", defence_req: 1}` |
| **Smart Filtering** | 18+ filter parameters for precise asset queries | Get all helmets requiring Defence skill level 5+ |
| **Equipment Compatibility** | Check if players can equip specific items | Validate player meets skill requirements |
| **Live Collection** | Fetch latest assets from EstFor Kingdom API | 700+ assets collected and enriched automatically |
| **Performance Optimized** | Sub-200ms response times with MongoDB indexing | Handles 1000+ requests/second |

## 📚 API Usage Examples

### Basic Asset Retrieval
```bash
# Get all assets (paginated)
curl "http://localhost:8000/assets/?limit=10"

# Search assets by name
curl "http://localhost:8000/assets/search?q=helmet"
```

### Advanced Filtering
```bash
# Get all helmets for defence skill level 5+
curl "http://localhost:8000/assets/?category=helmet&min_skill_level=5&skill=DEFENCE"

# Get epic rarity weapons
curl "http://localhost:8000/assets/?category=weapon&rarity=EPIC"

# Get items with XP boosts
curl "http://localhost:8000/assets/?has_boosts=true&boost_type=XP"
```

### Equipment & Skills
```bash
# Get items for specific equipment slots
curl "http://localhost:8000/assets/equipment/HEAD"

# Get items requiring specific skills
curl "http://localhost:8000/assets/by-skill/MELEE"

# Check asset statistics
curl "http://localhost:8000/assets/stats/summary"
```

### Enhanced Asset Response
```json
{
  "id": "bronze_helmet_001",
  "name": "Bronze Helmet", 
  "category": "helmet",
  "equip_position": "HEAD",
  "rarity_tier": "COMMON",
  "skill_requirements": {"DEFENCE": 1},
  "combat_stats": {"defence": 5},
  "boost_effects": [
    {"boost_type": "COMBAT_XP", "value": 10, "duration": 3600}
  ],
  "tradeable": true
}
```

## 🛠️ Development

### Available Commands
```bash
make start          # Start all services
make stop           # Stop all services  
make restart        # Restart services
make logs           # View logs
make health-check   # Check all services
make test           # Run test suite
make lint           # Code quality checks
```

### Testing
```bash
# Run all tests
make test

# Specific test categories  
pytest tests/test_enhanced_assets.py -v    # Enhanced asset features
pytest tests/test_game_constants.py -v     # Game integration
pytest tests/test_unit.py -v               # Unit tests
```

## 📊 Monitoring & Health

### Service URLs
- **API Health**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3000 (admin/admin) 
- **Kibana Logs**: http://localhost:5601
- **Database**: http://localhost:27017

### Performance Metrics
- **Response Time**: < 200ms (95th percentile)
- **Asset Collection**: 700+ assets in ~30 seconds
- **Database Queries**: < 50ms average
- **Health Check**: < 15ms response time

## 🚨 Troubleshooting

### Common Issues

**Services won't start?**
```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs app
```

**Database connection failed?**
```bash
# Test MongoDB connection
docker-compose exec mongodb mongosh

# Check environment variables
cat .env
```

**API not responding?**
```bash
# Check health endpoint
curl http://localhost:8000/health

# View application logs
make logs-app
```

## 📖 Documentation

- **[Technical Documentation](TECHNICAL.md)** - Architecture, deployment, and advanced configuration
- **[API Reference](http://localhost:8000/docs)** - Interactive API documentation
- **[Game Integration Guide](GAME_INTEGRATION.md)** - EstFor Kingdom constants and models

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `make test`
4. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need Help?** 
- 📖 [Full Documentation](TECHNICAL.md)
- 🐛 [Report Issues](../../issues)
- 💬 [GitHub Discussions](../../discussions)

**Version**: v1.0.0 | **Last Updated**: $(date)