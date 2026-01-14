# 🏛️ SYSTEM ARCHITECTURE - daten20 Platform

**Version:** 1.0.0
**Created:** 2026-01-14
**Status:** Architecture Design Document
**Scope:** Enterprise-wide Integration

---

## 🎯 ARCHITECTURAL OVERVIEW

The daten20 platform employs a **modular, microservices-inspired architecture** with three distinct but integrated variants sharing a common core. This design enables:

- **Flexibility:** Each variant can be deployed independently or together
- **Scalability:** Individual components scale based on demand
- **Maintainability:** Shared core reduces duplication
- **Evolution:** Easy to add new variants or features

---

## 🏗️ HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          daten20 PLATFORM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────── PRESENTATION TIER ─────────────────────────┐  │
│  │                                                                        │  │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │  │
│  │  │ VARIANT A    │   │ VARIANT B    │   │ VARIANT C    │            │  │
│  │  │              │   │              │   │              │            │  │
│  │  │ React SPA    │   │ Jinja2       │   │ Streamlit    │            │  │
│  │  │ (Port 3000)  │   │ Templates    │   │ (Port 8501)  │            │  │
│  │  │              │   │ (Port 8001)  │   │              │            │  │
│  │  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘            │  │
│  │         │                   │                   │                     │  │
│  └─────────┼───────────────────┼───────────────────┼─────────────────────┘  │
│            │                   │                   │                         │
│            └───────────────────┼───────────────────┘                         │
│                                │                                             │
│  ┌──────────────────────── API GATEWAY TIER ──────────────────────────┐    │
│  │                                                                      │    │
│  │  ┌────────────────────────────────────────────────────────────┐   │    │
│  │  │              UNIFIED API GATEWAY (Port 8080)               │   │    │
│  │  │                                                             │   │    │
│  │  │  • Route Management          • Rate Limiting               │   │    │
│  │  │  • Load Balancing            • Request Validation          │   │    │
│  │  │  • Authentication (JWT/OAuth) • API Documentation          │   │    │
│  │  │  • CORS Handling             • Monitoring & Logging        │   │    │
│  │  └─────────────────────┬──────────────────────────────────────┘   │    │
│  │                        │                                            │    │
│  └────────────────────────┼────────────────────────────────────────────┘   │
│                           │                                                 │
│  ┌────────────────────── APPLICATION TIER ─────────────────────────────┐  │
│  │                       │                                              │  │
│  │  ┌──────────┬─────────┴─────────┬──────────┐                       │  │
│  │  │          │                   │          │                        │  │
│  │  ▼          ▼                   ▼          ▼                        │  │
│  │                                                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐│  │
│  │  │  Variant A  │  │  Variant B  │  │  Variant C  │  │   Shared  ││  │
│  │  │   Service   │  │   Service   │  │   Service   │  │   Core    ││  │
│  │  │             │  │             │  │             │  │           ││  │
│  │  │ • BI API    │  │ • Service   │  │ • Dashboard │  │ • Auth    ││  │
│  │  │ • Predict   │  │   Mgmt API  │  │   Endpoints │  │ • DB      ││  │
│  │  │ • Warehouse │  │ • Finance   │  │ • Data      │  │ • Cache   ││  │
│  │  │ • OLAP      │  │   API       │  │   Connector │  │ • Logging ││  │
│  │  │ • Mining    │  │ • Parser    │  │             │  │ • Utils   ││  │
│  │  │             │  │   API       │  │             │  │           ││  │
│  │  │ Port 8000   │  │ Port 8001   │  │ Port 8501   │  │           ││  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘│  │
│  │         │                │                │               │       │  │
│  └─────────┼────────────────┼────────────────┼───────────────┼───────┘  │
│            │                │                │               │           │
│            └────────────────┴────────────────┴───────────────┘           │
│                             │                                             │
│  ┌──────────────────── MESSAGE QUEUE / EVENT BUS ─────────────────────┐  │
│  │                          │                                          │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │                   Redis Pub/Sub (Port 6379)                │   │  │
│  │  │                                                             │   │  │
│  │  │  • Inter-service Communication  • Event Broadcasting       │   │  │
│  │  │  • Cache Layer                  • Session Management       │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  │                                                                     │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │              Celery Task Queue (with Redis)                │   │  │
│  │  │                                                             │   │  │
│  │  │  • Asynchronous Tasks          • Report Generation         │   │  │
│  │  │  • Scheduled Jobs              • ETL Processing            │   │  │
│  │  │  • ML Model Training           • Email Notifications       │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                             │                                             │
│  ┌──────────────────────── DATA TIER ──────────────────────────────────┐ │
│  │                          │                                           │ │
│  │  ┌───────────────────────┴────────────────────────┐                │ │
│  │  │                                                 │                │ │
│  │  ▼                         ▼                       ▼                │ │
│  │                                                                      │ │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │ │
│  │  │  PostgreSQL  │   │    Redis     │   │  File Store  │           │ │
│  │  │   Primary    │   │    Cache     │   │   (S3/Local) │           │ │
│  │  │              │   │              │   │              │           │ │
│  │  │ • Relational │   │ • KV Store   │   │ • Reports    │           │ │
│  │  │   Data       │   │ • Sessions   │   │ • Templates  │           │ │
│  │  │ • ACID       │   │ • Locks      │   │ • Uploads    │           │ │
│  │  │              │   │              │   │              │           │ │
│  │  │ Port 5432    │   │ Port 6379    │   │              │           │ │
│  │  └──────────────┘   └──────────────┘   └──────────────┘           │ │
│  │                                                                      │ │
│  │  ┌──────────────┐   ┌──────────────┐                               │ │
│  │  │  SQLite      │   │  Time Series │                               │ │
│  │  │  (Variant C) │   │  DB (Option) │                               │ │
│  │  │              │   │              │                               │ │
│  │  │ • Embedded   │   │ • TimescaleDB│                               │ │
│  │  │ • Demo Data  │   │ • InfluxDB   │                               │ │
│  │  │              │   │              │                               │ │
│  │  └──────────────┘   └──────────────┘                               │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────── INFRASTRUCTURE / DEVOPS TIER ─────────────────────┐  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │   Nginx      │  │ Prometheus   │  │  ELK Stack   │             │  │
│  │  │ Reverse Proxy│  │  Monitoring  │  │   Logging    │             │  │
│  │  │ Load Balancer│  │   Metrics    │  │              │             │  │
│  │  │              │  │              │  │              │             │  │
│  │  │ Port 80/443  │  │ Port 9090    │  │ Port 9200    │             │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │   Docker     │  │  Kubernetes  │  │  CI/CD       │             │  │
│  │  │ Containers   │  │ Orchestration│  │ GitHub       │             │  │
│  │  │              │  │  (Optional)  │  │ Actions      │             │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 INTEGRATION PATTERNS

### 1. Shared Core Architecture

All three variants leverage a common core that provides:

```python
shared/
├── database/
│   ├── connection.py      # Database connection pooling
│   ├── models.py          # Shared ORM models
│   └── migrations/        # Database schema versions
│
├── auth/
│   ├── jwt_handler.py     # JWT token management
│   ├── oauth.py           # OAuth2 providers
│   └── permissions.py     # RBAC implementation
│
├── cache/
│   ├── redis_client.py    # Redis connection
│   └── cache_manager.py   # Cache strategies
│
├── logging/
│   ├── config.py          # Logging configuration
│   └── formatters.py      # Log formatters
│
├── utils/
│   ├── validators.py      # Data validation
│   ├── formatters.py      # Data formatters
│   ├── encryption.py      # Encryption utilities
│   └── email.py           # Email sender
│
└── api/
    ├── gateway.py         # API gateway logic
    ├── middleware.py      # Middleware stack
    └── schemas.py         # Shared Pydantic models
```

#### Shared Database Models

```python
# shared/database/models.py
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Shared user model across all variants
    """
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class AuditLog(Base):
    """
    Audit trail for all variants
    """
    __tablename__ = 'audit_logs'

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    details = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    variant = Column(String(20))  # 'A', 'B', or 'C'
```

---

### 2. API Gateway Pattern

The unified API gateway routes requests to appropriate variant services:

```python
# shared/api/gateway.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict


class APIGateway:
    """
    Unified API Gateway for all variants

    Routes:
    - /api/v1/analytics/*  → Variant A (port 8000)
    - /api/v1/services/*   → Variant B (port 8001)
    - /api/v1/dashboard/*  → Variant C (port 8501)
    """

    def __init__(self):
        self.app = FastAPI(title="daten20 API Gateway")
        self._setup_cors()
        self._setup_routes()

        self.service_map = {
            'analytics': 'http://localhost:8000',
            'services': 'http://localhost:8001',
            'dashboard': 'http://localhost:8501'
        }

    def _setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    def _setup_routes(self):
        @self.app.api_route(
            "/api/v1/analytics/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE"]
        )
        async def route_analytics(path: str, request: Request):
            return await self._proxy_request('analytics', path, request)

        @self.app.api_route(
            "/api/v1/services/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE"]
        )
        async def route_services(path: str, request: Request):
            return await self._proxy_request('services', path, request)

        @self.app.api_route(
            "/api/v1/dashboard/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE"]
        )
        async def route_dashboard(path: str, request: Request):
            return await self._proxy_request('dashboard', path, request)

    async def _proxy_request(
        self,
        service: str,
        path: str,
        request: Request
    ):
        """Forward request to appropriate service"""
        target_url = f"{self.service_map[service]}/api/v1/{path}"

        async with httpx.AsyncClient() as client:
            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body()
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
```

---

### 3. Event-Driven Architecture

Services communicate via Redis Pub/Sub for loose coupling:

```python
# shared/events/event_bus.py
import redis
import json
from typing import Callable, Dict, Any


class EventBus:
    """
    Redis-based event bus for inter-service communication
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()
        self.handlers: Dict[str, Callable] = {}

    def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish event to all subscribers"""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }

        self.redis_client.publish(
            event_type,
            json.dumps(message)
        )

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self.handlers[event_type] = handler
        self.pubsub.subscribe(event_type)

    def listen(self):
        """Listen for events (blocking)"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                event_type = message['channel'].decode()
                data = json.loads(message['data'])

                if event_type in self.handlers:
                    self.handlers[event_type](data)


# Example usage across variants

# Variant A publishes event when forecast is generated
event_bus.publish('forecast.generated', {
    'forecast_id': 'FCST-001',
    'periods': 12,
    'accuracy': 0.87
})

# Variant B subscribes and creates service recommendations
def on_forecast_generated(data):
    # Create service recommendations based on forecast
    pass

event_bus.subscribe('forecast.generated', on_forecast_generated)
```

---

### 4. Shared Authentication & Authorization

```python
# shared/auth/jwt_handler.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional


class JWTHandler:
    """
    Centralized JWT authentication for all variants
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str
    ) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )

        to_encode = {
            'sub': user_id,
            'email': email,
            'role': role,
            'exp': expire,
            'iat': datetime.utcnow()
        }

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
```

---

### 5. Cross-Variant Data Sharing

```python
# shared/database/cross_variant_queries.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any


class CrossVariantDataAccess:
    """
    Provides data access methods that span multiple variants
    """

    def __init__(self, db: Session):
        self.db = db

    def get_service_with_forecast(
        self,
        service_id: str
    ) -> Dict[str, Any]:
        """
        Get service from Variant B with forecast from Variant A

        Combines:
        - Service details (Variant B)
        - Cost forecast (Variant A predictive analytics)
        """
        # Get service from Variant B
        service = self.db.query(Service).filter(
            Service.id == service_id
        ).first()

        if not service:
            return None

        # Get forecast from Variant A
        forecast = self.db.query(Forecast).filter(
            Forecast.service_id == service_id
        ).order_by(Forecast.created_at.desc()).first()

        return {
            'service': service,
            'forecast': forecast,
            'combined_view': {
                'service_name': service.name,
                'current_cost': service.base_hourly_rate,
                'forecasted_cost': forecast.predicted_value if forecast else None,
                'forecast_confidence': forecast.confidence if forecast else None
            }
        }

    def get_dashboard_data_for_services(
        self,
        category: str
    ) -> Dict[str, Any]:
        """
        Aggregate data from Variant B services for Variant A/C dashboard
        """
        services = self.db.query(Service).filter(
            Service.category == category
        ).all()

        return {
            'total_services': len(services),
            'total_monthly_cost': sum(s.base_hourly_rate * 160 for s in services),
            'services_by_status': {
                'active': len([s for s in services if s.status == 'active']),
                'inactive': len([s for s in services if s.status == 'inactive'])
            }
        }
```

---

## 🔄 DATA FLOW EXAMPLES

### Example 1: User Creates Service Budget (Variant B) → Forecast (Variant A)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User creates service in Variant B Admin UI               │
│    POST /api/v1/services                                     │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Variant B Service Manager                                 │
│    - Validates service data                                  │
│    - Calculates financial parameters                         │
│    - Saves to database                                       │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Event Published: 'service.created'                        │
│    {service_id, category, base_cost}                         │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Variant A subscribes and receives event                   │
│    - Triggers forecast generation                            │
│    - Runs Monte Carlo simulation                             │
│    - Stores forecast results                                 │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Event Published: 'forecast.completed'                     │
│    {service_id, forecast_id, results}                        │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Variant B receives event                                  │
│    - Updates service with forecast link                      │
│    - Notifies user via email                                 │
└──────────────────────────────────────────────────────────────┘
```

### Example 2: Dashboard Displays Cross-Variant Data (Variant C)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User opens Variant C Dashboard                            │
│    http://localhost:8501                                     │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Streamlit app requests data                               │
│    GET /api/v1/dashboard/overview                            │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. API Gateway routes to Variant C service                   │
│    Variant C aggregates data from:                           │
│    - Variant A: KPIs, forecasts                              │
│    - Variant B: Services, budgets                            │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ├───► Query Variant A database
                 │     SELECT * FROM kpis, forecasts
                 │
                 └───► Query Variant B database
                       SELECT * FROM services, budgets
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Combine results                                            │
│    {                                                          │
│      analytics: {...},  // From Variant A                    │
│      services: {...}    // From Variant B                    │
│    }                                                          │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Render dashboard with integrated data                     │
│    - KPI cards from Variant A                                │
│    - Service metrics from Variant B                          │
│    - Combined visualizations                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛡️ SECURITY ARCHITECTURE

### 1. Authentication Flow

```
User Login Request
    │
    ▼
[API Gateway]
    │
    ├─► Validate credentials (shared/auth)
    │
    ├─► Generate JWT token
    │   - user_id, email, role
    │   - 15 minute expiration
    │
    ├─► Store session in Redis
    │
    └─► Return token to client
```

### 2. Authorization Check

```
API Request with JWT
    │
    ▼
[API Gateway Middleware]
    │
    ├─► Verify JWT signature
    │
    ├─► Check expiration
    │
    ├─► Load user permissions
    │
    ├─► Check resource access (RBAC)
    │   ├─ Admin: Full access all variants
    │   ├─ Analyst: Read Variant A/C, Limited Variant B
    │   └─ User: Read-only all
    │
    └─► Forward to service or reject (403)
```

### 3. Data Encryption

```python
# shared/utils/encryption.py
from cryptography.fernet import Fernet


class DataEncryption:
    """Encrypt sensitive data at rest"""

    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Usage: Encrypt sensitive fields in database
encrypted_tax_id = encryption.encrypt(provider.tax_id)
provider.encrypted_tax_id = encrypted_tax_id
```

---

## 📈 SCALABILITY PATTERNS

### 1. Horizontal Scaling

```
                 [Load Balancer]
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   [Variant A]   [Variant A]   [Variant A]
    Instance 1    Instance 2    Instance 3
        │             │             │
        └─────────────┼─────────────┘
                      │
                [Shared Database]
```

### 2. Caching Strategy

```
Request → Check Redis Cache
            │
            ├─► Cache Hit → Return cached data
            │
            └─► Cache Miss
                  │
                  ├─► Query Database
                  ├─► Store in Cache (TTL: 5 min)
                  └─► Return data
```

### 3. Database Sharding (Future)

```
Users A-M  → Shard 1
Users N-Z  → Shard 2
Services   → Shard 3
Analytics  → Shard 4
```

---

## 🧪 TESTING ARCHITECTURE

### 1. Unit Tests (Per Variant)

```python
# variant_a/tests/test_kpi_calculator.py
def test_calculate_mrr():
    calculator = KPICalculator(mock_db, mock_cache)
    result = calculator.calculate_mrr(date(2024, 1, 31))
    assert result > 0
```

### 2. Integration Tests (Cross-Variant)

```python
# tests/integration/test_cross_variant.py
def test_service_to_forecast_flow():
    # Create service in Variant B
    service = variant_b_client.post('/api/v1/services', json={...})

    # Wait for event processing
    time.sleep(2)

    # Check forecast created in Variant A
    forecast = variant_a_client.get(
        f'/api/v1/forecasts/by-service/{service.id}'
    )

    assert forecast.status_code == 200
    assert forecast.json()['service_id'] == service.id
```

### 3. End-to-End Tests

```python
# tests/e2e/test_full_workflow.py
from playwright.sync_api import sync_playwright

def test_complete_user_journey():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Login
        page.goto('http://localhost:8080/login')
        page.fill('#email', 'test@example.com')
        page.fill('#password', 'password')
        page.click('#login-button')

        # Navigate to Variant B
        page.goto('http://localhost:8001/services')

        # Create service
        page.click('#create-service')
        page.fill('#service-name', 'Test Service')
        page.click('#submit')

        # Navigate to Variant A
        page.goto('http://localhost:3000/forecasts')

        # Verify forecast appears
        assert page.is_visible('text=Test Service')
```

---

## 📊 MONITORING & OBSERVABILITY

### 1. Metrics Collection (Prometheus)

```python
# shared/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'variant']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'variant']
)

# Business metrics
active_users = Gauge(
    'active_users_total',
    'Number of active users',
    ['variant']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'variant']
)
```

### 2. Logging (ELK Stack)

```python
# shared/logging/config.py
import logging
from pythonjsonlogger import jsonlogger


def setup_logging(variant: str):
    logger = logging.getLogger()
    handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(variant)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Add variant context to all logs
    logger = logging.LoggerAdapter(logger, {'variant': variant})

    return logger
```

### 3. Distributed Tracing

```python
# shared/tracing/opentelemetry_config.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter


def setup_tracing(service_name: str):
    trace.set_tracer_provider(TracerProvider())

    jaeger_exporter = JaegerExporter(
        agent_host_name='localhost',
        agent_port=6831
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    return trace.get_tracer(service_name)
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  # API Gateway
  gateway:
    build: ./shared/api
    ports:
      - "8080:8080"
    depends_on:
      - variant_a
      - variant_b
      - variant_c
      - postgres
      - redis

  # Variant A
  variant_a:
    build: ./variant_a
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/daten20
      - REDIS_URL=redis://redis:6379

  # Variant B
  variant_b:
    build: ./variant_b
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/daten20
      - REDIS_URL=redis://redis:6379

  # Variant C
  variant_c:
    build: ./variant_c
    ports:
      - "8501:8501"

  # Databases
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=daten20
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
```

### Kubernetes (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: variant-a
spec:
  replicas: 3
  selector:
    matchLabels:
      app: variant-a
  template:
    metadata:
      labels:
        app: variant-a
    spec:
      containers:
      - name: variant-a
        image: daten20/variant-a:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## ✅ ARCHITECTURE DECISION RECORDS (ADRs)

### ADR-001: Shared Core vs. Duplicated Code

**Decision:** Use shared core module for common functionality

**Rationale:**
- Reduces code duplication
- Ensures consistency (auth, logging, etc.)
- Easier maintenance

**Trade-offs:**
- Tight coupling between variants
- Shared bugs affect all variants

---

### ADR-002: Event-Driven vs. Direct API Calls

**Decision:** Use event-driven architecture for inter-service communication

**Rationale:**
- Loose coupling
- Async processing
- Easier to add new services

**Trade-offs:**
- Increased complexity
- Eventual consistency (not immediate)

---

### ADR-003: Monorepo vs. Separate Repositories

**Decision:** Use monorepo for all three variants

**Rationale:**
- Easier code sharing
- Atomic commits across variants
- Simplified CI/CD

**Trade-offs:**
- Larger repository size
- Potential merge conflicts

---

## 📚 NEXT STEPS

1. ✅ Review architecture design
2. ✅ Approve technical approach
3. ✅ Begin Phase 1 implementation
4. ✅ Set up shared core first
5. ✅ Implement variants sequentially

---

**Document Status:** ✅ Complete and Ready
**Next Document:** [API_REFERENCE.md](./API_REFERENCE.md)
