"""
Unit tests for API gateway core module
"""

import json
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.gateway.core import (
    APIGateway,
    CircuitBreakerState,
    HTTPMethod,
    Request,
    Response,
    Route,
    RouteStatus,
    get_gateway,
)


# ============================================================================
# Enum Tests
# ============================================================================


class TestEnums:
    """Test enum types"""

    def test_http_methods(self):
        """Test HTTPMethod enum"""
        assert HTTPMethod.GET == "GET"
        assert HTTPMethod.POST == "POST"
        assert HTTPMethod.PUT == "PUT"
        assert HTTPMethod.PATCH == "PATCH"
        assert HTTPMethod.DELETE == "DELETE"
        assert HTTPMethod.OPTIONS == "OPTIONS"
        assert HTTPMethod.HEAD == "HEAD"

    def test_route_status(self):
        """Test RouteStatus enum"""
        assert RouteStatus.ACTIVE == "active"
        assert RouteStatus.INACTIVE == "inactive"
        assert RouteStatus.MAINTENANCE == "maintenance"


# ============================================================================
# Route Tests
# ============================================================================


class TestRoute:
    """Test Route dataclass"""

    def test_basic_route(self):
        """Test basic route configuration"""
        route = Route(
            path="/api/services", methods=[HTTPMethod.GET, HTTPMethod.POST], backend_url="http://localhost:5000/api/services"
        )

        assert route.path == "/api/services"
        assert HTTPMethod.GET in route.methods
        assert HTTPMethod.POST in route.methods
        assert route.backend_url == "http://localhost:5000/api/services"
        assert route.timeout == 30
        assert route.auth_required is True

    def test_route_with_rate_limit(self):
        """Test route with rate limiting"""
        route = Route(
            path="/api/calculate",
            methods=[HTTPMethod.POST],
            backend_url="http://localhost:5000/api/calculate",
            rate_limit=100,
        )

        assert route.rate_limit == 100

    def test_route_without_auth(self):
        """Test route without authentication"""
        route = Route(
            path="/api/public",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000/api/public",
            auth_required=False,
        )

        assert route.auth_required is False


# ============================================================================
# Request Tests
# ============================================================================


class TestRequest:
    """Test Request dataclass"""

    def test_basic_request(self):
        """Test basic request"""
        request = Request(
            method=HTTPMethod.GET,
            path="/api/services",
            headers={"Content-Type": "application/json"},
            query_params={"page": "1"},
        )

        assert request.method == HTTPMethod.GET
        assert request.path == "/api/services"
        assert request.headers["Content-Type"] == "application/json"
        assert request.query_params["page"] == "1"

    def test_request_with_body(self):
        """Test request with body"""
        request = Request(
            method=HTTPMethod.POST,
            path="/api/services",
            headers={"Content-Type": "application/json"},
            query_params={},
            body='{"name": "Test Service"}',
        )

        assert request.body == '{"name": "Test Service"}'

    def test_request_auto_timestamp(self):
        """Test request auto-generates timestamp"""
        request = Request(method=HTTPMethod.GET, path="/api/services", headers={}, query_params={})

        assert isinstance(request.timestamp, datetime)


# ============================================================================
# Response Tests
# ============================================================================


class TestResponse:
    """Test Response dataclass"""

    def test_basic_response(self):
        """Test basic response"""
        response = Response(status_code=200, headers={"Content-Type": "application/json"}, body='{"status": "ok"}')

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.body == '{"status": "ok"}'

    def test_response_with_latency(self):
        """Test response with latency"""
        response = Response(status_code=200, headers={}, latency_ms=45.5)

        assert response.latency_ms == 45.5


# ============================================================================
# CircuitBreakerState Tests
# ============================================================================


class TestCircuitBreakerState:
    """Test CircuitBreakerState dataclass"""

    def test_initial_state(self):
        """Test initial circuit breaker state"""
        state = CircuitBreakerState()

        assert state.failures == 0
        assert state.is_open is False
        assert state.last_failure_time is None
        assert state.last_success_time is None


# ============================================================================
# APIGateway Tests
# ============================================================================


class TestAPIGateway:
    """Test APIGateway class"""

    def test_init(self):
        """Test gateway initialization"""
        gateway = APIGateway()

        assert isinstance(gateway.routes, dict)
        assert isinstance(gateway.circuit_breakers, dict)
        assert isinstance(gateway.request_history, list)
        assert isinstance(gateway.rate_limits, dict)

    def test_default_routes_registered(self):
        """Test default routes are registered"""
        gateway = APIGateway()

        assert "/api/v1/services" in gateway.routes
        assert "/api/v1/calculate" in gateway.routes
        assert "/api/v1/statistics" in gateway.routes
        assert "/api/v1/auth/login" in gateway.routes

    def test_register_route(self):
        """Test registering a route"""
        gateway = APIGateway()
        route = Route(path="/api/custom", methods=[HTTPMethod.GET], backend_url="http://localhost:5000/api/custom")

        gateway.register_route(route)

        assert "/api/custom" in gateway.routes
        assert gateway.routes["/api/custom"].path == "/api/custom"

    def test_unregister_route(self):
        """Test unregistering a route"""
        gateway = APIGateway()
        route = Route(path="/api/custom", methods=[HTTPMethod.GET], backend_url="http://localhost:5000/api/custom")

        gateway.register_route(route)
        result = gateway.unregister_route("/api/custom")

        assert result is True
        assert "/api/custom" not in gateway.routes

    def test_unregister_nonexistent_route(self):
        """Test unregistering non-existent route"""
        gateway = APIGateway()

        result = gateway.unregister_route("/api/nonexistent")

        assert result is False

    def test_find_route_exact_match(self):
        """Test finding route with exact match"""
        gateway = APIGateway()

        route = gateway.find_route("/api/v1/services", HTTPMethod.GET)

        assert route is not None
        assert route.path == "/api/v1/services"

    def test_find_route_pattern_match(self):
        """Test finding route with pattern matching"""
        gateway = APIGateway()

        route = gateway.find_route("/api/v1/services/123", HTTPMethod.GET)

        assert route is not None
        assert route.path == "/api/v1/services/<id>"

    def test_find_route_no_match(self):
        """Test finding non-existent route"""
        gateway = APIGateway()

        route = gateway.find_route("/api/nonexistent", HTTPMethod.GET)

        assert route is None

    def test_find_route_wrong_method(self):
        """Test finding route with wrong HTTP method"""
        gateway = APIGateway()

        # /api/v1/statistics only supports GET
        route = gateway.find_route("/api/v1/statistics", HTTPMethod.POST)

        assert route is None

    def test_check_rate_limit_no_limit(self):
        """Test rate limiting when route has no limit"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000", rate_limit=None)
        request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.1")

        allowed = gateway.check_rate_limit(request, route)

        assert allowed is True

    def test_check_rate_limit_under_limit(self):
        """Test requests under rate limit"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000", rate_limit=10)
        request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.1")

        # Make 5 requests
        for _ in range(5):
            allowed = gateway.check_rate_limit(request, route)
            assert allowed is True

    def test_check_rate_limit_exceeds_limit(self):
        """Test requests exceeding rate limit"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000", rate_limit=3)
        request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.1")

        # Make 3 requests (should all pass)
        for _ in range(3):
            gateway.check_rate_limit(request, route)

        # 4th request should fail
        allowed = gateway.check_rate_limit(request, route)
        assert allowed is False

    def test_check_rate_limit_different_ips(self):
        """Test rate limiting is per IP"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000", rate_limit=2)

        request1 = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.1")
        request2 = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.2")

        # IP 1: make 2 requests
        gateway.check_rate_limit(request1, route)
        gateway.check_rate_limit(request1, route)

        # IP 2 should still be allowed
        allowed = gateway.check_rate_limit(request2, route)
        assert allowed is True

    def test_check_circuit_breaker_closed(self):
        """Test circuit breaker when closed"""
        gateway = APIGateway()

        allowed = gateway.check_circuit_breaker("http://localhost:5000")

        assert allowed is True

    def test_check_circuit_breaker_open(self):
        """Test circuit breaker when open"""
        gateway = APIGateway()
        backend_url = "http://localhost:5000"

        # Open circuit breaker
        state = CircuitBreakerState(failures=5, is_open=True, last_failure_time=datetime.now())
        gateway.circuit_breakers[backend_url] = state

        allowed = gateway.check_circuit_breaker(backend_url)

        assert allowed is False

    def test_check_circuit_breaker_half_open(self):
        """Test circuit breaker reopens after timeout"""
        gateway = APIGateway()
        backend_url = "http://localhost:5000"

        # Open circuit breaker with old failure time
        from datetime import timedelta

        old_time = datetime.now() - timedelta(seconds=70)
        state = CircuitBreakerState(failures=5, is_open=True, last_failure_time=old_time)
        gateway.circuit_breakers[backend_url] = state

        allowed = gateway.check_circuit_breaker(backend_url)

        # Should allow retry
        assert allowed is True
        assert gateway.circuit_breakers[backend_url].is_open is False

    def test_record_success(self):
        """Test recording successful request"""
        gateway = APIGateway()
        backend_url = "http://localhost:5000"

        # Set some failures
        gateway.circuit_breakers[backend_url] = CircuitBreakerState(failures=3)

        gateway.record_success(backend_url)

        assert gateway.circuit_breakers[backend_url].failures == 0
        assert gateway.circuit_breakers[backend_url].is_open is False

    def test_record_failure(self):
        """Test recording failed request"""
        gateway = APIGateway()
        backend_url = "http://localhost:5000"

        gateway.record_failure(backend_url)

        assert gateway.circuit_breakers[backend_url].failures == 1

    def test_record_failure_opens_circuit(self):
        """Test circuit opens after threshold"""
        gateway = APIGateway()
        backend_url = "http://localhost:5000"

        # Record 5 failures
        for _ in range(5):
            gateway.record_failure(backend_url)

        assert gateway.circuit_breakers[backend_url].is_open is True

    def test_transform_request(self):
        """Test request transformation"""
        gateway = APIGateway()
        route = Route(path="/api/services", methods=[HTTPMethod.POST], backend_url="http://localhost:5000/api/services")

        request = Request(
            method=HTTPMethod.POST,
            path="/api/services",
            headers={"Content-Type": "application/json"},
            query_params={"filter": "active"},
            body='{"name": "Test"}',
            api_key="test_key",
        )

        backend_request = gateway.transform_request(request, route)

        assert backend_request["method"] == "POST"
        assert backend_request["url"] == "http://localhost:5000/api/services"
        assert backend_request["params"]["filter"] == "active"
        assert backend_request["data"] == '{"name": "Test"}'
        assert backend_request["headers"]["X-API-Key"] == "test_key"

    def test_transform_response(self):
        """Test response transformation"""
        gateway = APIGateway()

        backend_response = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": '{"status": "ok"}',
            "latency_ms": 50,
        }

        response = gateway.transform_response(backend_response)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.body == '{"status": "ok"}'
        assert response.latency_ms == 50

    def test_handle_request_route_not_found(self):
        """Test handling request for non-existent route"""
        gateway = APIGateway()
        request = Request(method=HTTPMethod.GET, path="/api/nonexistent", headers={}, query_params={})

        response = gateway.handle_request(request)

        assert response.status_code == 404
        assert "not found" in response.body.lower()

    def test_handle_request_route_inactive(self):
        """Test handling request for inactive route"""
        gateway = APIGateway()
        route = Route(
            path="/api/maintenance",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000",
            status=RouteStatus.INACTIVE,
        )
        gateway.register_route(route)

        request = Request(method=HTTPMethod.GET, path="/api/maintenance", headers={}, query_params={})

        response = gateway.handle_request(request)

        assert response.status_code == 503

    def test_handle_request_missing_auth(self):
        """Test handling request without authentication"""
        gateway = APIGateway()
        route = Route(
            path="/api/protected",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000",
            auth_required=True,
        )
        gateway.register_route(route)

        request = Request(method=HTTPMethod.GET, path="/api/protected", headers={}, query_params={}, api_key=None)

        response = gateway.handle_request(request)

        assert response.status_code == 401

    def test_handle_request_rate_limited(self):
        """Test handling rate-limited request"""
        gateway = APIGateway()
        route = Route(
            path="/api/limited",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000",
            rate_limit=1,
            auth_required=False,
        )
        gateway.register_route(route)

        request = Request(
            method=HTTPMethod.GET, path="/api/limited", headers={}, query_params={}, client_ip="192.168.1.1"
        )

        # First request succeeds
        response1 = gateway.handle_request(request)
        assert response1.status_code == 200

        # Second request should be rate limited
        response2 = gateway.handle_request(request)
        assert response2.status_code == 429

    def test_handle_request_circuit_breaker_open(self):
        """Test handling request when circuit breaker is open"""
        gateway = APIGateway()
        route = Route(
            path="/api/test",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000",
            circuit_breaker_enabled=True,
        )
        gateway.register_route(route)

        # Open circuit breaker
        gateway.circuit_breakers[route.backend_url] = CircuitBreakerState(
            failures=5, is_open=True, last_failure_time=datetime.now()
        )

        request = Request(
            method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, api_key="test_key"
        )

        response = gateway.handle_request(request)

        assert response.status_code == 503

    def test_handle_request_success(self):
        """Test successful request handling"""
        gateway = APIGateway()
        route = Route(
            path="/api/test",
            methods=[HTTPMethod.GET],
            backend_url="http://localhost:5000",
            auth_required=False,
        )
        gateway.register_route(route)

        request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={})

        response = gateway.handle_request(request)

        assert response.status_code == 200

    def test_log_request(self):
        """Test request logging"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000")
        request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={}, client_ip="192.168.1.1")
        response = Response(status_code=200, headers={}, latency_ms=50)

        gateway.log_request(request, route, response)

        assert len(gateway.request_history) == 1
        assert gateway.request_history[0]["path"] == "/api/test"
        assert gateway.request_history[0]["status_code"] == 200

    def test_log_request_limits_history(self):
        """Test request logging limits history size"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000")

        # Log 11000 requests
        for i in range(11000):
            request = Request(method=HTTPMethod.GET, path=f"/api/test/{i}", headers={}, query_params={})
            response = Response(status_code=200, headers={}, latency_ms=50)
            gateway.log_request(request, route, response)

        # Should keep only last 10000
        assert len(gateway.request_history) == 10000

    def test_get_analytics_empty(self):
        """Test analytics with no requests"""
        gateway = APIGateway()

        analytics = gateway.get_analytics(minutes=60)

        assert analytics["total_requests"] == 0
        assert analytics["requests_per_minute"] == 0

    def test_get_analytics(self):
        """Test analytics with requests"""
        gateway = APIGateway()
        route = Route(path="/api/test", methods=[HTTPMethod.GET], backend_url="http://localhost:5000")

        # Log some requests
        for i in range(10):
            request = Request(method=HTTPMethod.GET, path="/api/test", headers={}, query_params={})
            response = Response(status_code=200 if i < 8 else 404, headers={}, latency_ms=50 + i)
            gateway.log_request(request, route, response)

        analytics = gateway.get_analytics(minutes=60)

        assert analytics["total_requests"] == 10
        assert analytics["avg_latency_ms"] > 0
        assert 200 in analytics["status_codes"]
        assert 404 in analytics["status_codes"]


# ============================================================================
# Global Instance Tests
# ============================================================================


class TestGlobalInstance:
    """Test global gateway instance"""

    def test_get_gateway(self):
        """Test get_gateway returns singleton"""
        gateway1 = get_gateway()
        gateway2 = get_gateway()

        assert gateway1 is gateway2
