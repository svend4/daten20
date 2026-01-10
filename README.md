# 📋 Document Management System

**Enterprise-Ready Document Management for Social Services Planning**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-326CE5.svg)](https://kubernetes.io/)

Professional system for managing personal budget service planning documents for social services in Germany.

**Current Version:** 2.2.0 | **Status:** Production-Ready ✅

---

## 🎯 Features Overview

### Core System (v1.0)
- ✅ **Template Analyzer** - Parse and analyze document templates
- ✅ **Financial Calculator** - Calculate service costs with German regulations
- ✅ **Document Generator** - Generate filled documents (TXT, HTML, PDF, Markdown)
- ✅ **Interactive Editor** - Step-by-step service creation wizard
- ✅ **Service Manager** - SQLite database with CRUD operations
- ✅ **CLI Tools** - Command-line utilities for all operations

### Web & API (v2.0)
- ✅ **Flask Web Application** - Full-featured web interface with Bootstrap 5
- ✅ **REST API** - RESTful API with 8+ endpoints
- ✅ **Excel/CSV Export/Import** - Data exchange capabilities
- ✅ **Email Notifications** - SMTP-based notification system
- ✅ **Analytics Engine** - Comprehensive data analysis and reporting
- ✅ **Unit Tests** - pytest-based test suite

### Enterprise Features (v2.1)
- ✅ **Docker Containerization** - Production-ready Docker images
- ✅ **Authentication & Authorization** - Multi-user system with sessions and JWT
- ✅ **Role-Based Access Control** - 5 roles with granular permissions
- ✅ **Webhooks** - Event-based integrations with retry logic
- ✅ **Advanced Visualization** - Matplotlib and Plotly charts
- ✅ **PDF Export with Branding** - Professional PDF generation
- ✅ **API Versioning** - Versioned REST API (v1)
- ✅ **Comprehensive Logging** - Multi-file logging with rotation
- ✅ **Caching System** - Redis and in-memory caching

### Security & DevOps (v2.2)
- ✅ **Two-Factor Authentication** - TOTP-based 2FA with QR codes
- ✅ **Comprehensive Audit Logging** - Track all system activities
- ✅ **API Rate Limiting** - Token bucket algorithm with per-user limits
- ✅ **CORS Configuration** - Secure cross-origin requests
- ✅ **CI/CD Pipeline** - GitHub Actions with automated testing
- ✅ **Kubernetes Deployment** - Production-ready K8s manifests
- ✅ **Prometheus Monitoring** - 8+ metrics for system monitoring
- ✅ **Automated Backups** - Scheduled backups with retention policy
- ✅ **Real-time Notifications** - WebSocket-based live updates
- ✅ **GraphQL API** - Flexible data querying with GraphiQL

---

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd daten20

# Run setup script
python setup.py

# Start application
python src/web_app.py
```

### Method 2: Docker
```bash
# Start with Docker Compose
docker-compose up -d

# Access application
open http://localhost:5000
```

### Method 3: Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit configuration

# Initialize and run
python -c "from src.core.database import Database; Database()"
python src/web_app.py
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.**

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide (600+ lines) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and design |
| [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) | Complete deployment checklist |
| [CHANGELOG_v2.0.md](CHANGELOG_v2.0.md) | v2.0 features documentation |
| [CHANGELOG_v2.1.md](CHANGELOG_v2.1.md) | v2.1 features documentation |
| [CHANGELOG_v2.2.md](CHANGELOG_v2.2.md) | v2.2 features documentation |

---

## 💻 Usage

### Web Interface
```bash
# Start application
python src/web_app.py

# Access interfaces
# Main UI:     http://localhost:5000
# API Docs:    http://localhost:5000/apidocs
# GraphQL:     http://localhost:5000/graphql
# Metrics:     http://localhost:5000/metrics
```

### CLI Tools
```bash
# Admin utilities
python dms-admin.py --help

# Create user
python dms-admin.py users create

# Create backup
python dms-admin.py backup create

# View audit log
python dms-admin.py audit view

# System status
python dms-admin.py system status
```

### REST API
```bash
# List services
curl http://localhost:5000/api/v1/services

# Create service
curl -X POST http://localhost:5000/api/v1/services \
  -H "Content-Type: application/json" \
  -d '{"service_name": "Shopping Assistance", "region": "Bavaria"}'

# Get statistics
curl http://localhost:5000/api/v1/statistics
```

### GraphQL
```graphql
query {
  services(region: "Bavaria", limit: 10) {
    id
    serviceName
    bruttoRate
  }
}

mutation {
  createService(
    serviceName: "New Service"
    region: "Berlin"
    bruttoRate: 45.50
  ) {
    service { id }
    success
  }
}
```

### WebSockets
```javascript
const socket = io('http://localhost:5000');

socket.emit('authenticate', {
    user_id: 123,
    token: 'jwt-token'
});

socket.on('service_created', (data) => {
    console.log('New service:', data);
});
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Interface                          │
│            (Bootstrap 5, JavaScript, Chart.js)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ REST API │ GraphQL  │WebSockets│  Auth    │  Admin   │  │
│  │   (v1)   │          │          │  (RBAC)  │  Panel   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Core Services                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │Template  │Financial │Document  │  Email   │Analytics │  │
│  │Analyzer  │Calculator│Generator │Notifier  │ Engine   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Audit   │   2FA    │Webhooks  │  Cache   │ Backup   │  │
│  │  Logger  │          │          │          │  Manager │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │SQLite/   │  Redis   │  Files   │  Audit   │  Backup  │  │
│  │PostgreSQL│  Cache   │  Storage │   DB     │  Storage │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Features

- **Two-Factor Authentication** - TOTP with Google Authenticator
- **Audit Logging** - Comprehensive activity tracking (20+ event types)
- **API Rate Limiting** - Protection against abuse
- **RBAC** - 5 roles with 13+ granular permissions
- **JWT Tokens** - Secure API authentication
- **Password Hashing** - Bcrypt-based secure storage
- **Session Management** - Secure cookie-based sessions
- **CORS Configuration** - Cross-origin request control
- **API Key Management** - Scoped API keys with expiration

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| **Total Lines of Code** | 30,000+ |
| **Python Modules** | 45 |
| **Web Templates** | 13 |
| **Documentation Files** | 8 |
| **API Endpoints** | 20+ |
| **GraphQL Operations** | 10+ |
| **Prometheus Metrics** | 8 |
| **Audit Events** | 20+ |
| **User Roles** | 5 |
| **Permissions** | 13+ |
| **Supported Languages** | German, Russian |

---

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core language
- **Flask 3.0** - Web framework
- **SQLite/PostgreSQL** - Database
- **Redis** - Caching
- **Gunicorn** - WSGI server

### Frontend
- **Bootstrap 5** - UI framework
- **JavaScript** - Client-side logic
- **Chart.js** - Data visualization
- **Socket.IO** - Real-time updates

### Security
- **Flask-Login** - Session management
- **Flask-Bcrypt** - Password hashing
- **PyJWT** - JSON Web Tokens
- **PyOTP** - Two-factor authentication

### DevOps
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **GitHub Actions** - CI/CD
- **Prometheus** - Monitoring
- **Nginx** - Reverse proxy

### APIs
- **Flasgger** - Swagger/OpenAPI
- **Graphene** - GraphQL
- **Flask-SocketIO** - WebSockets
- **Flask-CORS** - CORS handling

---

## 🚢 Deployment Options

### 1. Docker (Recommended)
```bash
docker-compose up -d
```

### 2. Kubernetes
```bash
kubectl apply -f k8s/base/
```

### 3. Traditional Server
See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Integration tests
pytest tests/test_api_integration.py -v

# Specific test
pytest tests/test_financial_calculator.py::test_calculate_rate -v
```

---

## 📈 Monitoring

### Prometheus Metrics
```bash
# Access metrics endpoint
curl http://localhost:5000/metrics
```

Available metrics:
- `dms_requests_total` - HTTP request count
- `dms_request_duration_seconds` - Request latency
- `dms_active_users` - Active user count
- `dms_cache_hits_total` / `dms_cache_misses_total` - Cache performance
- `dms_cpu_usage_percent` - CPU usage
- `dms_memory_usage_bytes` - Memory usage

### Health Check
```bash
curl http://localhost:5000/api/v1/health
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built for social services planning in Germany
- Supports German social insurance regulations
- Compatible with Persönlicher Budget services
- Follows German data protection standards

---

## 📞 Support

- **Documentation:** See `/docs` directory
- **CLI Help:** `python dms-admin.py --help`
- **System Status:** `python dms-admin.py system status`
- **Issues:** GitHub Issues

---

## 🗺️ Roadmap

### v2.3 (Planned)
- [ ] Multi-language support (i18n)
- [ ] Advanced analytics with ML
- [ ] Mobile app (React Native)
- [ ] SSO integration (OAuth2, SAML)
- [ ] Advanced reporting templates

### v3.0 (Future)
- [ ] Microservices architecture
- [ ] Event sourcing
- [ ] CQRS pattern
- [ ] Advanced collaboration features

---

**Production-Ready Enterprise System** 🚀

Built with ❤️ for social services professionals.

**Version:** 2.2.0 | **Last Updated:** January 2026
