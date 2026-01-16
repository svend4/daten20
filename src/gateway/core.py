"""
API Gateway Core

Central gateway for routing, rate limiting, and request management.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class HTTPMethod(str, Enum):
    """HTTP methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class RouteStatus(str, Enum):
    """Route status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


@dataclass
class Route:
    """API route configuration"""

    path: str
    methods: List[HTTPMethod]
    backend_url: str
    timeout: int = 30
    retry_count: int = 0
    circuit_breaker_enabled: bool = True
    rate_limit: Optional[int] = None  # requests per minute
    auth_required: bool = True
    status: RouteStatus = RouteStatus.ACTIVE
    description: str = ""


@dataclass
class Request:
    """Incoming request"""

    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[str] = None
    client_ip: str = "0.0.0.0"
    user_id: Optional[int] = None
    api_key: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Response:
    """Outgoing response"""

    status_code: int
    headers: Dict[str, str]
    body: Optional[str] = None
    latency_ms: float = 0


@dataclass
class CircuitBreakerState:
    """Circuit breaker state"""

    failures: int = 0
    last_failure_time: Optional[datetime] = None
    is_open: bool = False
    last_success_time: Optional[datetime] = None


class APIGateway:
    """API Gateway for request routing and management"""

    def __init__(self):
        # Routes configuration
        self.routes: Dict[str, Route] = {}

        # Circuit breaker states per backend
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}

        # Request history (for analytics)
        self.request_history: List[Dict[str, Any]] = []

        # Rate limiting (simple in-memory)
        self.rate_limits: Dict[str, List[float]] = {}

        # Register default routes
        self._register_default_routes()

    def _register_default_routes(self):
        """Register default API routes"""
        routes = [
            Route(
                path="/api/v1/services",
                methods=[HTTPMethod.GET, HTTPMethod.POST],
                backend_url="http://localhost:5000/api/v1/services",
                description="Services CRUD operations",
            ),
            Route(
                path="/api/v1/services/<id>",
                methods=[HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE],
                backend_url="http://localhost:5000/api/v1/services/<id>",
                description="Single service operations",
            ),
            Route(
                path="/api/v1/calculate",
                methods=[HTTPMethod.POST],
                backend_url="http://localhost:5000/api/v1/calculate",
                rate_limit=100,  # 100 req/min
                description="Financial calculations",
            ),
            Route(
                path="/api/v1/statistics",
                methods=[HTTPMethod.GET],
                backend_url="http://localhost:5000/api/v1/statistics",
                rate_limit=60,
                description="System statistics",
            ),
            Route(
                path="/api/v1/auth/login",
                methods=[HTTPMethod.POST],
                backend_url="http://localhost:5000/api/v1/auth/login",
                auth_required=False,
                rate_limit=10,  # Stricter for auth
                description="User authentication",
            ),
        ]

        for route in routes:
            self.register_route(route)

    def register_route(self, route: Route):
        """Register a new route"""
        self.routes[route.path] = route

    def unregister_route(self, path: str) -> bool:
        """Unregister a route"""
        if path in self.routes:
            del self.routes[path]
            return True
        return False

    def find_route(self, path: str, method: HTTPMethod) -> Optional[Route]:
        """Find matching route for path and method"""
        # Exact match first
        if path in self.routes:
            route = self.routes[path]
            if method in route.methods:
                return route

        # Pattern matching (simplified)
        for route_path, route in self.routes.items():
            if "<" in route_path:
                # Convert route pattern to regex-like matching
                pattern_parts = route_path.split("/")
                path_parts = path.split("/")

                if len(pattern_parts) == len(path_parts):
                    match = True
                    for pp, pt in zip(pattern_parts, path_parts):
                        if pp.startswith("<") and pp.endswith(">"):
                            continue  # Variable part
                        elif pp != pt:
                            match = False
                            break

                    if match and method in route.methods:
                        return route

        return None

    def check_rate_limit(self, request: Request, route: Route) -> bool:
        """Check if request is within rate limit"""
        if route.rate_limit is None:
            return True

        # Generate key for rate limiting
        key = f"{request.client_ip}:{route.path}"

        now = time.time()
        window = 60  # 60 seconds window

        # Clean old timestamps
        if key in self.rate_limits:
            self.rate_limits[key] = [ts for ts in self.rate_limits[key] if now - ts < window]
        else:
            self.rate_limits[key] = []

        # Check limit
        if len(self.rate_limits[key]) >= route.rate_limit:
            return False

        # Add current timestamp
        self.rate_limits[key].append(now)
        return True

    def check_circuit_breaker(self, backend_url: str) -> bool:
        """Check if circuit breaker is open"""
        if backend_url not in self.circuit_breakers:
            self.circuit_breakers[backend_url] = CircuitBreakerState()

        state = self.circuit_breakers[backend_url]

        # If circuit is open, check if we should try again
        if state.is_open:
            if state.last_failure_time:
                # Try after 60 seconds
                elapsed = (datetime.now() - state.last_failure_time).total_seconds()
                if elapsed > 60:
                    state.is_open = False
                    state.failures = 0
                    return True
            return False

        return True

    def record_success(self, backend_url: str):
        """Record successful request"""
        if backend_url in self.circuit_breakers:
            state = self.circuit_breakers[backend_url]
            state.failures = 0
            state.last_success_time = datetime.now()
            state.is_open = False

    def record_failure(self, backend_url: str):
        """Record failed request"""
        if backend_url not in self.circuit_breakers:
            self.circuit_breakers[backend_url] = CircuitBreakerState()

        state = self.circuit_breakers[backend_url]
        state.failures += 1
        state.last_failure_time = datetime.now()

        # Open circuit after 5 failures
        if state.failures >= 5:
            state.is_open = True

    def transform_request(self, request: Request, route: Route) -> Dict[str, Any]:
        """Transform request before sending to backend"""
        # Build backend request
        backend_request = {
            "method": request.method.value,
            "url": route.backend_url,
            "headers": request.headers.copy(),
            "timeout": route.timeout,
        }

        # Add query parameters
        if request.query_params:
            backend_request["params"] = request.query_params

        # Add body
        if request.body:
            backend_request["data"] = request.body

        # Add authentication headers
        if route.auth_required and request.api_key:
            backend_request["headers"]["X-API-Key"] = request.api_key

        return backend_request

    def transform_response(self, backend_response: Dict[str, Any]) -> Response:
        """Transform backend response"""
        return Response(
            status_code=backend_response.get("status_code", 200),
            headers=backend_response.get("headers", {}),
            body=backend_response.get("body"),
            latency_ms=backend_response.get("latency_ms", 0),
        )

    def handle_request(self, request: Request) -> Response:
        """Handle incoming request"""
        start_time = time.time()

        # Find route
        route = self.find_route(request.path, request.method)
        if not route:
            return Response(
                status_code=404,
                headers={"Content-Type": "application/json"},
                body=json.dumps({"error": "Route not found"}),
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Check route status
        if route.status != RouteStatus.ACTIVE:
            return Response(
                status_code=503,
                headers={"Content-Type": "application/json"},
                body=json.dumps({"error": "Service unavailable"}),
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Check authentication
        if route.auth_required and not request.api_key:
            return Response(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body=json.dumps({"error": "Authentication required"}),
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Check rate limit
        if not self.check_rate_limit(request, route):
            return Response(
                status_code=429,
                headers={"Content-Type": "application/json"},
                body=json.dumps({"error": "Rate limit exceeded"}),
                latency_ms=(time.time() - start_time) * 1000,
            )

        # Check circuit breaker
        if route.circuit_breaker_enabled:
            if not self.check_circuit_breaker(route.backend_url):
                return Response(
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({"error": "Service temporarily unavailable"}),
                    latency_ms=(time.time() - start_time) * 1000,
                )

        # Transform request
        backend_request = self.transform_request(request, route)

        # Make backend request (simulated)
        try:
            # In real implementation, use requests library
            # import requests
            # backend_response = requests.request(**backend_request)

            # Simulated success
            backend_response = {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "success"}),
                "latency_ms": 50,
            }

            self.record_success(route.backend_url)

        except Exception as e:
            self.record_failure(route.backend_url)

            backend_response = {
                "status_code": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)}),
                "latency_ms": (time.time() - start_time) * 1000,
            }

        # Transform response
        response = self.transform_response(backend_response)
        response.latency_ms = (time.time() - start_time) * 1000

        # Log request
        self.log_request(request, route, response)

        return response

    def log_request(self, request: Request, route: Route, response: Response):
        """Log request for analytics"""
        log_entry = {
            "timestamp": request.timestamp.isoformat(),
            "method": request.method.value,
            "path": request.path,
            "route": route.path,
            "status_code": response.status_code,
            "latency_ms": response.latency_ms,
            "client_ip": request.client_ip,
            "user_id": request.user_id,
        }

        self.request_history.append(log_entry)

        # Keep only last 10000 requests
        if len(self.request_history) > 10000:
            self.request_history = self.request_history[-10000:]

    def get_analytics(self, minutes: int = 60) -> Dict[str, Any]:
        """Get gateway analytics"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)

        recent_requests = [
            r for r in self.request_history if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff_time
        ]

        if not recent_requests:
            return {
                "total_requests": 0,
                "requests_per_minute": 0,
                "avg_latency_ms": 0,
                "error_rate": 0,
                "status_codes": {},
            }

        total = len(recent_requests)
        errors = len([r for r in recent_requests if r["status_code"] >= 400])
        latencies = [r["latency_ms"] for r in recent_requests]

        # Status code distribution
        status_codes = {}
        for req in recent_requests:
            code = req["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

        return {
            "total_requests": total,
            "requests_per_minute": total / minutes,
            "avg_latency_ms": sum(latencies) / len(latencies),
            "error_rate": (errors / total * 100) if total > 0 else 0,
            "status_codes": status_codes,
        }


# Global instance
_gateway: Optional[APIGateway] = None


def get_gateway() -> APIGateway:
    """Get global API gateway instance"""
    global _gateway

    if _gateway is None:
        _gateway = APIGateway()

    return _gateway
