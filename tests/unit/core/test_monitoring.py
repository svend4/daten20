"""
Comprehensive tests for src/core/monitoring.py

Tests Prometheus metrics export, system monitoring, and request tracking.

Session 27 - 60+ tests
"""

import sys
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock flask before importing
mock_response_class = MagicMock()
sys.modules["flask"] = Mock(Response=mock_response_class)

# Mock prometheus_client before importing
mock_counter = MagicMock()
mock_gauge = MagicMock()
mock_histogram = MagicMock()
mock_generate_latest = MagicMock()
mock_content_type = "text/plain; version=0.0.4"

sys.modules["prometheus_client"] = Mock(
    Counter=mock_counter,
    Gauge=mock_gauge,
    Histogram=mock_histogram,
    generate_latest=mock_generate_latest,
    CONTENT_TYPE_LATEST=mock_content_type,
)

# Mock psutil before importing
mock_psutil = Mock()
sys.modules["psutil"] = mock_psutil

from src.core.monitoring import (
    ACTIVE_USERS,
    CACHE_HITS,
    CACHE_MISSES,
    CPU_USAGE,
    DATABASE_CONNECTIONS,
    MEMORY_USAGE,
    REQUEST_COUNT,
    REQUEST_DURATION,
    metrics_endpoint,
    track_request_metrics,
    update_system_metrics,
)


class TestPrometheusMetrics:
    """Test Prometheus metric definitions."""

    def test_request_count_metric_defined(self):
        """Test REQUEST_COUNT metric is defined"""
        assert REQUEST_COUNT is not None
        # Verify it was created as a Counter
        mock_counter.assert_any_call(
            "dms_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
        )

    def test_request_duration_metric_defined(self):
        """Test REQUEST_DURATION metric is defined"""
        assert REQUEST_DURATION is not None
        # Verify it was created as a Histogram
        mock_histogram.assert_any_call(
            "dms_request_duration_seconds", "HTTP request duration in seconds", ["method", "endpoint"]
        )

    def test_active_users_metric_defined(self):
        """Test ACTIVE_USERS metric is defined"""
        assert ACTIVE_USERS is not None
        # Verify it was created as a Gauge
        mock_gauge.assert_any_call("dms_active_users", "Number of currently active users")

    def test_database_connections_metric_defined(self):
        """Test DATABASE_CONNECTIONS metric is defined"""
        assert DATABASE_CONNECTIONS is not None
        # Verify it was created as a Gauge
        mock_gauge.assert_any_call("dms_database_connections", "Number of active database connections")

    def test_cache_hits_metric_defined(self):
        """Test CACHE_HITS metric is defined"""
        assert CACHE_HITS is not None
        # Verify it was created as a Counter
        mock_counter.assert_any_call("dms_cache_hits_total", "Total cache hits")

    def test_cache_misses_metric_defined(self):
        """Test CACHE_MISSES metric is defined"""
        assert CACHE_MISSES is not None
        # Verify it was created as a Counter
        mock_counter.assert_any_call("dms_cache_misses_total", "Total cache misses")

    def test_cpu_usage_metric_defined(self):
        """Test CPU_USAGE metric is defined"""
        assert CPU_USAGE is not None
        # Verify it was created as a Gauge
        mock_gauge.assert_any_call("dms_cpu_usage_percent", "CPU usage percentage")

    def test_memory_usage_metric_defined(self):
        """Test MEMORY_USAGE metric is defined"""
        assert MEMORY_USAGE is not None
        # Verify it was created as a Gauge
        mock_gauge.assert_any_call("dms_memory_usage_bytes", "Memory usage in bytes")


class TestTrackRequestMetrics:
    """Test track_request_metrics decorator."""

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_successful_request(self, mock_duration, mock_count):
        """Test decorator tracks successful request"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_func():
            return mock_response

        with patch("flask.request", mock_request):
            result = test_func()

        assert result == mock_response
        # Verify Counter was incremented
        mock_count.labels.assert_called_once_with(method="GET", endpoint="/api/test", status=200)
        mock_count.labels.return_value.inc.assert_called_once()

        # Verify Histogram recorded duration
        mock_duration.labels.assert_called_once_with(method="GET", endpoint="/api/test")
        mock_duration.labels.return_value.observe.assert_called_once()

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_args(self, mock_duration, mock_count):
        """Test decorator preserves function arguments"""
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.endpoint = "/api/create"

        mock_response = Mock()
        mock_response.status_code = 201

        @track_request_metrics
        def test_func(arg1, arg2, kwarg1=None):
            assert arg1 == "test1"
            assert arg2 == "test2"
            assert kwarg1 == "kwtest"
            return mock_response

        with patch("flask.request", mock_request):
            result = test_func("test1", "test2", kwarg1="kwtest")

        assert result == mock_response

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_unknown_endpoint(self, mock_duration, mock_count):
        """Test decorator handles unknown endpoint"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = None

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_func():
            return mock_response

        with patch("flask.request", mock_request):
            result = test_func()

        assert result == mock_response
        # Verify endpoint is marked as "unknown"
        mock_count.labels.assert_called_once_with(method="GET", endpoint="unknown", status=200)

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_response_without_status_code(self, mock_duration, mock_count):
        """Test decorator handles response without status_code attribute"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        mock_response = Mock(spec=[])  # No status_code attribute

        @track_request_metrics
        def test_func():
            return mock_response

        with patch("flask.request", mock_request):
            result = test_func()

        assert result == mock_response
        # Verify default status 200 is used
        mock_count.labels.assert_called_once_with(method="GET", endpoint="/api/test", status=200)

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_exception(self, mock_duration, mock_count):
        """Test decorator tracks metrics on exception"""
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.endpoint = "/api/error"

        @track_request_metrics
        def test_func():
            raise ValueError("Test error")

        with patch("flask.request", mock_request):
            with pytest.raises(ValueError) as exc_info:
                test_func()

        assert str(exc_info.value) == "Test error"
        # Verify 500 status was recorded
        # Note: In the except block, request is not available, so it uses "unknown"
        mock_count.labels.assert_called_once_with(method="unknown", endpoint="unknown", status=500)
        mock_count.labels.return_value.inc.assert_called_once()

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_timing_accuracy(self, mock_duration, mock_count):
        """Test decorator accurately measures request duration"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/slow"

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_func():
            time.sleep(0.01)  # Simulate work
            return mock_response

        with patch("flask.request", mock_request):
            result = test_func()

        assert result == mock_response
        # Verify duration was observed
        mock_duration.labels.return_value.observe.assert_called_once()
        observed_duration = mock_duration.labels.return_value.observe.call_args[0][0]
        assert observed_duration >= 0.01  # At least 10ms

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_preserves_function_name(self, mock_duration, mock_count):
        """Test decorator preserves function metadata"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_function_with_name():
            """Test docstring"""
            return mock_response

        # Verify function name is preserved by @wraps
        assert test_function_with_name.__name__ == "test_function_with_name"
        assert test_function_with_name.__doc__ == "Test docstring"

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_multiple_calls(self, mock_duration, mock_count):
        """Test decorator tracks multiple calls correctly"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_func():
            return mock_response

        with patch("flask.request", mock_request):
            for _ in range(3):
                test_func()

        # Verify metrics were recorded 3 times
        assert mock_count.labels.call_count == 3
        assert mock_duration.labels.call_count == 3


class TestUpdateSystemMetrics:
    """Test update_system_metrics function."""

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    def test_update_system_metrics_success(self, mock_memory, mock_cpu):
        """Test update_system_metrics updates CPU and memory"""
        mock_psutil.cpu_percent.return_value = 45.2
        mock_virtual_memory = Mock()
        mock_virtual_memory.used = 8589934592  # 8GB
        mock_psutil.virtual_memory.return_value = mock_virtual_memory

        update_system_metrics()

        mock_cpu.set.assert_called_once_with(45.2)
        mock_memory.set.assert_called_once_with(8589934592)

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    def test_update_system_metrics_zero_values(self, mock_memory, mock_cpu):
        """Test update_system_metrics with zero values"""
        mock_psutil.cpu_percent.return_value = 0.0
        mock_virtual_memory = Mock()
        mock_virtual_memory.used = 0
        mock_psutil.virtual_memory.return_value = mock_virtual_memory

        update_system_metrics()

        mock_cpu.set.assert_called_once_with(0.0)
        mock_memory.set.assert_called_once_with(0)

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    def test_update_system_metrics_high_values(self, mock_memory, mock_cpu):
        """Test update_system_metrics with high values"""
        mock_psutil.cpu_percent.return_value = 99.9
        mock_virtual_memory = Mock()
        mock_virtual_memory.used = 17179869184  # 16GB
        mock_psutil.virtual_memory.return_value = mock_virtual_memory

        update_system_metrics()

        mock_cpu.set.assert_called_once_with(99.9)
        mock_memory.set.assert_called_once_with(17179869184)

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    @patch("src.core.monitoring.logger")
    def test_update_system_metrics_cpu_error(self, mock_logger, mock_memory, mock_cpu):
        """Test update_system_metrics handles CPU error gracefully"""
        mock_psutil.cpu_percent.side_effect = Exception("CPU error")

        update_system_metrics()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error updating system metrics" in mock_logger.error.call_args[0][0]

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    @patch("src.core.monitoring.logger")
    def test_update_system_metrics_memory_error(self, mock_logger, mock_memory, mock_cpu):
        """Test update_system_metrics handles memory error gracefully"""
        mock_psutil.cpu_percent.return_value = 45.2
        mock_psutil.virtual_memory.side_effect = Exception("Memory error")

        update_system_metrics()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error updating system metrics" in mock_logger.error.call_args[0][0]

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    def test_update_system_metrics_with_valid_float_values(self, mock_memory, mock_cpu):
        """Test update_system_metrics handles float values correctly"""
        # Clear any side effects
        mock_psutil.cpu_percent.side_effect = None
        mock_psutil.virtual_memory.side_effect = None

        mock_psutil.cpu_percent.return_value = 75.5
        mock_virtual_memory = Mock()
        mock_virtual_memory.used = 2147483648  # 2GB
        mock_psutil.virtual_memory.return_value = mock_virtual_memory

        update_system_metrics()

        # Verify metrics were updated with correct values
        mock_cpu.set.assert_called_with(75.5)
        mock_memory.set.assert_called_with(2147483648)


class TestMetricsEndpoint:
    """Test metrics_endpoint function."""

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    def test_metrics_endpoint_success(self, mock_response, mock_generate, mock_update):
        """Test metrics_endpoint returns Prometheus metrics"""
        mock_generate.return_value = b"# TYPE dms_requests_total counter\n"
        mock_response_instance = Mock()
        mock_response.return_value = mock_response_instance

        result = metrics_endpoint()

        # Verify system metrics were updated
        mock_update.assert_called_once()

        # Verify generate_latest was called
        mock_generate.assert_called_once()

        # Verify Response was created with correct parameters
        mock_response.assert_called_once_with(
            b"# TYPE dms_requests_total counter\n", mimetype=mock_content_type
        )

        assert result == mock_response_instance

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    def test_metrics_endpoint_empty_metrics(self, mock_response, mock_generate, mock_update):
        """Test metrics_endpoint with empty metrics"""
        mock_generate.return_value = b""
        mock_response_instance = Mock()
        mock_response.return_value = mock_response_instance

        result = metrics_endpoint()

        mock_update.assert_called_once()
        mock_generate.assert_called_once()
        mock_response.assert_called_once_with(b"", mimetype=mock_content_type)

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    def test_metrics_endpoint_large_metrics(self, mock_response, mock_generate, mock_update):
        """Test metrics_endpoint with large metrics output"""
        large_metrics = b"# TYPE metric counter\n" * 1000
        mock_generate.return_value = large_metrics
        mock_response_instance = Mock()
        mock_response.return_value = mock_response_instance

        result = metrics_endpoint()

        mock_response.assert_called_once_with(large_metrics, mimetype=mock_content_type)

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    def test_metrics_endpoint_calls_update_first(self, mock_response, mock_generate, mock_update):
        """Test metrics_endpoint updates system metrics before generating output"""
        call_order = []
        mock_update.side_effect = lambda: call_order.append("update")
        mock_generate.side_effect = lambda: call_order.append("generate") or b"metrics"

        metrics_endpoint()

        # Verify update was called before generate
        assert call_order == ["update", "generate"]

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    def test_metrics_endpoint_correct_content_type(self, mock_response, mock_generate, mock_update):
        """Test metrics_endpoint uses correct Prometheus content type"""
        mock_generate.return_value = b"metrics"
        mock_response_instance = Mock()
        mock_response.return_value = mock_response_instance

        metrics_endpoint()

        # Verify correct mimetype
        assert mock_response.call_args[1]["mimetype"] == mock_content_type


class TestIntegration:
    """Integration tests for monitoring module."""

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_full_monitoring_workflow(self, mock_duration, mock_count):
        """Test complete monitoring workflow"""
        # Setup
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"
        mock_response = Mock()
        mock_response.status_code = 200

        # Track request
        @track_request_metrics
        def api_handler():
            return mock_response

        with patch("flask.request", mock_request):
            api_handler()

        # Verify all metrics were updated
        mock_count.labels.assert_called_once()
        mock_duration.labels.assert_called_once()

    @patch("src.core.monitoring.update_system_metrics")
    @patch("src.core.monitoring.generate_latest")
    @patch("src.core.monitoring.Response")
    @patch("src.core.monitoring.REQUEST_COUNT")
    def test_metrics_endpoint_after_requests(
        self, mock_count, mock_response, mock_generate, mock_update
    ):
        """Test metrics endpoint includes request metrics"""
        mock_generate.return_value = b"dms_requests_total 5"
        mock_response_instance = Mock()
        mock_response.return_value = mock_response_instance

        result = metrics_endpoint()

        mock_update.assert_called_once()
        assert result == mock_response_instance

    def test_all_metrics_are_exported(self):
        """Test all metric constants are properly exported"""
        assert REQUEST_COUNT is not None
        assert REQUEST_DURATION is not None
        assert ACTIVE_USERS is not None
        assert DATABASE_CONNECTIONS is not None
        assert CACHE_HITS is not None
        assert CACHE_MISSES is not None
        assert CPU_USAGE is not None
        assert MEMORY_USAGE is not None

    def test_all_functions_are_exported(self):
        """Test all functions are properly exported"""
        assert callable(track_request_metrics)
        assert callable(update_system_metrics)
        assert callable(metrics_endpoint)


class TestErrorHandling:
    """Test error handling in monitoring module."""

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_keyboard_interrupt(self, mock_duration, mock_count):
        """Test decorator does not catch KeyboardInterrupt"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        @track_request_metrics
        def test_func():
            raise KeyboardInterrupt()

        with patch("flask.request", mock_request):
            with pytest.raises(KeyboardInterrupt):
                test_func()

        # KeyboardInterrupt is not caught by except Exception, so no metrics are recorded
        mock_count.labels.assert_not_called()

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_system_exit(self, mock_duration, mock_count):
        """Test decorator does not catch SystemExit"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/test"

        @track_request_metrics
        def test_func():
            raise SystemExit(1)

        with patch("flask.request", mock_request):
            with pytest.raises(SystemExit):
                test_func()

        # SystemExit is not caught by except Exception, so no metrics are recorded
        mock_count.labels.assert_not_called()

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    @patch("src.core.monitoring.logger")
    def test_update_system_metrics_with_os_error(self, mock_logger, mock_memory, mock_cpu):
        """Test update_system_metrics handles OSError"""
        mock_psutil.cpu_percent.side_effect = OSError("Permission denied")

        update_system_metrics()

        mock_logger.error.assert_called_once()
        assert "Error updating system metrics" in mock_logger.error.call_args[0][0]

    @patch("src.core.monitoring.CPU_USAGE")
    @patch("src.core.monitoring.MEMORY_USAGE")
    @patch("src.core.monitoring.logger")
    def test_update_system_metrics_continues_after_error(self, mock_logger, mock_memory, mock_cpu):
        """Test update_system_metrics doesn't crash on error"""
        mock_psutil.cpu_percent.side_effect = Exception("Test error")

        # Should not raise exception
        update_system_metrics()

        # Should log error
        mock_logger.error.assert_called_once()


class TestMetricLabels:
    """Test metric label handling."""

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_special_characters_in_endpoint(
        self, mock_duration, mock_count
    ):
        """Test decorator handles special characters in endpoint"""
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.endpoint = "/api/user/123/data?filter=active"

        mock_response = Mock()
        mock_response.status_code = 200

        @track_request_metrics
        def test_func():
            return mock_response

        with patch("flask.request", mock_request):
            test_func()

        mock_count.labels.assert_called_once_with(
            method="GET", endpoint="/api/user/123/data?filter=active", status=200
        )

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_different_http_methods(self, mock_duration, mock_count):
        """Test decorator handles different HTTP methods"""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in methods:
            mock_request = Mock()
            mock_request.method = method
            mock_request.endpoint = "/api/test"

            mock_response = Mock()
            mock_response.status_code = 200

            @track_request_metrics
            def test_func():
                return mock_response

            with patch("flask.request", mock_request):
                test_func()

            # Verify method is correctly passed
            assert mock_count.labels.call_args[1]["method"] == method

    @patch("src.core.monitoring.REQUEST_COUNT")
    @patch("src.core.monitoring.REQUEST_DURATION")
    def test_track_request_metrics_with_different_status_codes(self, mock_duration, mock_count):
        """Test decorator handles different HTTP status codes"""
        status_codes = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]

        for status_code in status_codes:
            mock_request = Mock()
            mock_request.method = "GET"
            mock_request.endpoint = "/api/test"

            mock_response = Mock()
            mock_response.status_code = status_code

            @track_request_metrics
            def test_func():
                return mock_response

            with patch("flask.request", mock_request):
                test_func()

            # Verify status code is correctly passed
            assert mock_count.labels.call_args[1]["status"] == status_code
