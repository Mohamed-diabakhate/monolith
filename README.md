# Puppy Monolith 🐶

A comprehensive cloud-native monorepo containing multiple specialized applications and services for data processing, blockchain operations, gaming assets, and AI-powered transcription.

## 🏗️ Repository Structure

This monorepo contains **5 main projects** with shared infrastructure and deployment patterns:

```
monolith/
├── estfor/                    # 🎮 Gaming asset collection system (FastAPI)
├── NFT_Gallery/              # 🖼️ Solana NFT downloader (Python)
├── rainbow-backend/          # 🌈 Full-stack backend application (Node.js)
├── whispered_video/          # 🎤 AI video transcription (Python)
├── bridge_satori/           # 🌉 Bridge service
└── monitoring_gcp/          # 📊 GCP monitoring tools
```

## 🚀 Projects Overview

### 🎮 EstFor Asset Collection System
**Location:** `estfor/`  
**Tech Stack:** FastAPI, MongoDB, Redis, Docker  
**Purpose:** Gaming asset collection and management with comprehensive monitoring

**Key Features:**
- 🔄 **Container Auto Start/Stop System** - Intelligent resource management
- 📊 **Full Observability Stack** - Prometheus, Grafana, ELK
- 🎯 **Game Integration** - EstFor Kingdom asset definitions
- ⚡ **High Performance** - Async operations with Redis caching
- 🔧 **CI/CD Pipeline** - GitHub Actions with comprehensive testing

**Quick Start:**
```bash
cd estfor/
make start                # Start all services
make test                 # Run comprehensive tests
```

### 🖼️ NFT Gallery (Solana Downloader)
**Location:** `NFT_Gallery/`  
**Tech Stack:** Python, Helius API, Google Firestore  
**Purpose:** Download and process Solana NFTs with metadata

**Key Features:**
- 🔗 **Helius API Integration** - Direct blockchain data access
- 🏪 **Firestore Storage** - Scalable NoSQL database
- 🖥️ **Enhanced Processing** - Comprehensive NFT metadata handling
- 📈 **Monitoring Dashboard** - Real-time processing statistics
- 🧪 **Full Test Coverage** - Unit, integration, and E2E tests

**Quick Start:**
```bash
cd NFT_Gallery/
python main_enhanced.py --wallet YOUR_WALLET_ADDRESS
```

### 🌈 Rainbow Backend
**Location:** `rainbow-backend/`  
**Tech Stack:** Node.js, MongoDB, Redis, Express  
**Purpose:** Full-featured backend with user management and data collection

**Key Features:**
- 👥 **User Management** - Authentication, roles, permissions
- 📋 **Data Collection** - Program and collect management
- 📊 **Reporting System** - Analytics and visualization
- 🔄 **Background Jobs** - Queue processing with Redis
- 🐳 **Containerized** - Docker deployment ready

**Quick Start:**
```bash
cd rainbow-backend/
npm install
npm start
```

### 🎤 Whispered Video Transcription
**Location:** `whispered_video/`  
**Tech Stack:** Python, Torch, Faster Whisper, Docker  
**Purpose:** AI-powered video transcription with Apple Silicon optimization

**Key Features:**
- 🧠 **AI Transcription** - State-of-the-art Whisper models
- 🍎 **Apple Silicon** - MPS acceleration for M1/M2 chips
- 📹 **Multi-Platform** - YouTube, local files, various formats
- ⚡ **High Performance** - Optimized for speed and accuracy
- 🐳 **Containerized** - Docker support for deployment

**Quick Start:**
```bash
cd whispered_video/app/
python main.py
```

### 🌉 Bridge Satori & 📊 Monitoring
**Additional Services:**
- **Bridge Satori** - Service bridge and integration layer
- **Monitoring GCP** - Google Cloud Platform monitoring tools

## 🛠️ Development Setup

### Prerequisites
- **Docker Desktop** - Container orchestration
- **Python 3.11+** - For Python projects
- **Node.js 18+** - For Node.js projects
- **Git** - Version control

### Global Setup
```bash
# Clone the repository
git clone <repository-url>
cd monolith

# Set up Git hooks (optional)
git config --local core.hooksPath .githooks/
```

### Project-Specific Setup

Each project has its own setup instructions:

```bash
# EstFor (Recommended starting point)
cd estfor/
cp .env.example .env
make setup-dev
make start

# NFT Gallery
cd NFT_Gallery/
pip install -r requirements.txt
python setup_env.py

# Rainbow Backend
cd rainbow-backend/
npm install
cp .env.example .env

# Whispered Video
cd whispered_video/app/
pip install -r requirements.txt
```

## 🚀 Quick Start Guide

### Option 1: EstFor (Full Stack Experience)
```bash
cd estfor/
make start                    # Starts 11+ services
open http://localhost:8000    # FastAPI application
open http://localhost:3000    # Grafana dashboards
open http://localhost:5601    # Kibana logs
```

### Option 2: Individual Projects
```bash
# Choose your adventure
cd NFT_Gallery/ && python main_enhanced.py --help
cd rainbow-backend/ && npm start
cd whispered_video/app/ && python main.py
```

## 🧪 Testing

Each project includes comprehensive testing:

```bash
# EstFor - Full test suite
cd estfor/
make test                 # All tests (90% coverage required)
make test-unit           # Unit tests only
make test-integration    # Integration tests
make test-e2e            # End-to-end tests

# NFT Gallery - Comprehensive testing
cd NFT_Gallery/
pytest tests/ -v --cov=src --cov-report=html

# Rainbow Backend - API testing
cd rainbow-backend/
npm test
```

## 📊 Monitoring & Observability

### EstFor Monitoring Stack
- **Prometheus** - http://localhost:9090 - Metrics collection
- **Grafana** - http://localhost:3000 - Dashboards (admin/admin)
- **Kibana** - http://localhost:5601 - Log visualization
- **AlertManager** - http://localhost:9093 - Alert management

### Health Checks
```bash
# EstFor health checks
curl http://localhost:8000/health              # Basic health
curl http://localhost:8000/health/containers   # Container status
curl http://localhost:8000/health/automation   # Auto-management

# NFT Gallery monitoring
open NFT_Gallery/monitor/index.html

# Rainbow Backend status
curl http://localhost:3000/health
```

## 🔧 Container Management (EstFor)

The EstFor project includes an advanced **Container Auto Start/Stop System**:

### Features
- 🚀 **Auto-Start** - Containers start when endpoints are accessed
- 🛑 **Auto-Stop** - Idle containers stop after configurable timeouts
- 📊 **Smart Monitoring** - Priority-based resource management
- 🎛️ **Manual Control** - API endpoints for manual operations

### Configuration
```bash
# Environment variables
CONTAINER_AUTO_START=true              # Enable auto-start
CONTAINER_AUTO_STOP=true               # Enable auto-stop
CONTAINER_IDLE_TIMEOUT=30              # Normal timeout (minutes)
CONTAINER_HIGH_IDLE_TIMEOUT=120        # High priority timeout
CONTAINER_LOW_IDLE_TIMEOUT=10          # Low priority timeout
```

### Usage
```bash
# View container status
curl http://localhost:8000/health/containers

# Manual control
curl -X POST http://localhost:8000/health/containers/grafana/start
curl -X POST http://localhost:8000/health/containers/kibana/stop
```

## 🚢 Deployment

### Local Development
```bash
# EstFor - Full stack
cd estfor/ && make start

# Individual services
docker-compose up -d                    # Each project root
```

### Production Deployment
```bash
# EstFor production
cd estfor/
docker-compose -f docker-compose.prod.yml up -d

# NFT Gallery with Docker
cd NFT_Gallery/
docker-compose up -d

# Rainbow Backend
cd rainbow-backend/
npm run deploy
```

### CI/CD Pipelines

- **GitHub Actions** - Automated testing and deployment
- **Security Scanning** - Trivy, Bandit, Safety checks
- **Performance Testing** - k6 load testing
- **Multi-environment** - Development, staging, production

## 📋 Common Commands

### EstFor Commands
```bash
cd estfor/
make help                # Show all available commands
make start               # Start all services
make test                # Run all tests
make lint                # Code quality checks
make logs                # View service logs
make health-check        # Verify all services
```

### Development Utilities
```bash
# Docker management
docker-compose ps                       # Service status
docker-compose logs -f [service]        # Follow logs
docker system prune                     # Cleanup resources

# Testing across projects
find . -name "test_*.py" -exec python -m pytest {} \;
find . -name "package.json" -exec npm test {} \;
```

## 🛡️ Security & Best Practices

### Security Features
- 🔐 **Secret Management** - Google Secret Manager integration
- 🔑 **Authentication** - JWT tokens, API keys
- 🛡️ **Input Validation** - Pydantic models, sanitization
- 🔒 **Container Security** - Non-root users, resource limits
- 📊 **Audit Logging** - Comprehensive request/response logging

### Development Best Practices
- **Code Quality** - Black, isort, flake8, mypy
- **Testing** - 90% coverage requirement for production code
- **Documentation** - Comprehensive README and API docs
- **Monitoring** - Health checks, metrics, alerting
- **Error Handling** - Structured logging, graceful degradation

## 🤝 Contributing

### Development Workflow
1. **Branch Strategy** - Feature branches from `main`
2. **Code Quality** - Automated linting and formatting
3. **Testing** - All tests must pass with coverage requirements
4. **Review Process** - Pull request reviews required
5. **Documentation** - Update relevant README and docs

### Getting Help
- 📚 **Project Documentation** - Each project has detailed CLAUDE.md
- 🐛 **Issues** - Use GitHub Issues for bug reports
- 💬 **Discussions** - GitHub Discussions for questions
- 📖 **API Docs** - Interactive docs at `/docs` endpoints

## 📈 Performance & Scaling

### Resource Requirements
- **Development** - 16GB RAM, 4+ CPU cores recommended
- **Production** - Varies by project, see individual requirements
- **Container Limits** - Defined in docker-compose files

### Scaling Options
- **Horizontal Scaling** - Multiple container instances
- **Load Balancing** - Nginx reverse proxy configurations
- **Database Scaling** - MongoDB sharding, Redis clustering
- **Caching** - Multi-layer caching strategies

## 📄 License & Support

- **License** - See individual project licenses
- **Support** - Community-driven development
- **Updates** - Regular maintenance and feature updates

---

## 🔗 Quick Links

| Project | Local URL | Documentation | Status |
|---------|-----------|---------------|---------|
| EstFor API | http://localhost:8000 | [CLAUDE.md](estfor/CLAUDE.md) | ✅ Production Ready |
| EstFor Docs | http://localhost:8000/docs | [Container Guide](estfor/CONTAINER_AUTO_MANAGEMENT.md) | 📊 Interactive API |
| Grafana | http://localhost:3000 | Built-in Help | 📈 Monitoring |
| NFT Gallery | - | [README.md](NFT_Gallery/README.md) | ✅ Production Ready |
| Rainbow Backend | http://localhost:3000 | [README.md](rainbow-backend/README.md) | ✅ Production Ready |
| Whispered Video | - | [CLAUDE.md](whispered_video/CLAUDE.md) | ✅ Production Ready |

**Get Started:** `cd estfor/ && make start` 🚀