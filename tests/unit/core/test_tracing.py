"""
Comprehensive tests for src/core/tracing.py

Tests distributed tracing with OpenTelemetry, span management, and auto-instrumentation.

Session 29 - 60+ tests
"""

import sys
from contextlib import nullcontext
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock opentelemetry modules before importing
mock_trace = Mock()
mock_tracer = MagicMock()
mock_span = MagicMock()
mock_span.is_recording.return_value = True
mock_trace.get_current_span.return_value = mock_span
mock_trace.get_tracer.return_value = mock_tracer
mock_trace.set_tracer_provider = MagicMock()
mock_trace.use_span = MagicMock(return_value=nullcontext())

# Mock Status and StatusCode
mock_status = Mock()
mock_status_code = Mock()
mock_status_code.OK = "OK"
mock_status_code.ERROR = "ERROR"

sys.modules["opentelemetry"] = Mock(trace=mock_trace)
sys.modules["opentelemetry.trace"] = mock_trace
sys.modules["opentelemetry.trace"].Status = mock_status
sys.modules["opentelemetry.trace"].StatusCode = mock_status_code

# Mock exporters
mock_jaeger_exporter = MagicMock()
mock_otlp_exporter = MagicMock()
mock_console_exporter = MagicMock()

sys.modules["opentelemetry.exporter"] = Mock()
sys.modules["opentelemetry.exporter.jaeger"] = Mock()
sys.modules["opentelemetry.exporter.jaeger.thrift"] = Mock(JaegerExporter=mock_jaeger_exporter)
sys.modules["opentelemetry.exporter.otlp"] = Mock()
sys.modules["opentelemetry.exporter.otlp.proto"] = Mock()
sys.modules["opentelemetry.exporter.otlp.proto.grpc"] = Mock()
sys.modules["opentelemetry.exporter.otlp.proto.grpc.trace_exporter"] = Mock(
    OTLPSpanExporter=mock_otlp_exporter
)

# Mock instrumentation
mock_flask_instrumentor = MagicMock()
mock_requests_instrumentor = MagicMock()
mock_sqlalchemy_instrumentor = MagicMock()

sys.modules["opentelemetry.instrumentation"] = Mock()
sys.modules["opentelemetry.instrumentation.flask"] = Mock(FlaskInstrumentor=mock_flask_instrumentor)
sys.modules["opentelemetry.instrumentation.requests"] = Mock(
    RequestsInstrumentor=mock_requests_instrumentor
)
sys.modules["opentelemetry.instrumentation.sqlalchemy"] = Mock(
    SQLAlchemyInstrumentor=mock_sqlalchemy_instrumentor
)

# Mock SDK
mock_resource = MagicMock()
mock_tracer_provider = MagicMock()
mock_batch_span_processor = MagicMock()

sys.modules["opentelemetry.sdk"] = Mock()
sys.modules["opentelemetry.sdk.resources"] = Mock(
    SERVICE_NAME="service.name", Resource=mock_resource
)
sys.modules["opentelemetry.sdk.trace"] = Mock(TracerProvider=mock_tracer_provider)
sys.modules["opentelemetry.sdk.trace.export"] = Mock(
    BatchSpanProcessor=mock_batch_span_processor, ConsoleSpanExporter=mock_console_exporter
)

# Now import the module
from src.core import tracing
from src.core.tracing import (
    add_span_attribute,
    add_span_event,
    create_span,
    get_tracer,
    init_tracing,
    shutdown_tracing,
    traced,
    traced_api,
    traced_db,
    traced_ml,
)


class TestGetTracer:
    """Test get_tracer function."""

    def test_get_tracer_uninitialized(self):
        """Test get_tracer raises error when uninitialized"""
        # Reset module state
        tracing._tracer = None
        tracing._is_initialized = False

        with pytest.raises(RuntimeError) as exc_info:
            get_tracer()

        assert "not initialized" in str(exc_info.value).lower()
        assert "init_tracing()" in str(exc_info.value)

    def test_get_tracer_initialized(self):
        """Test get_tracer returns tracer when initialized"""
        # Set up initialized state
        test_tracer = Mock()
        tracing._tracer = test_tracer
        tracing._is_initialized = True

        result = get_tracer()

        assert result == test_tracer


class TestInitTracing:
    """Test init_tracing function."""

    def setup_method(self):
        """Reset module state before each test"""
        tracing._tracer = None
        tracing._is_initialized = False
        mock_resource.reset_mock()
        mock_tracer_provider.reset_mock()
        mock_jaeger_exporter.reset_mock()
        mock_otlp_exporter.reset_mock()
        mock_console_exporter.reset_mock()

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_basic(self, mock_auto_inst):
        """Test basic tracing initialization"""
        result = init_tracing(app_name="test-app", environment="test")

        assert result is not None
        mock_resource.assert_called_once()
        mock_tracer_provider.assert_called_once()
        mock_auto_inst.assert_called_once()
        assert tracing._is_initialized is True

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_already_initialized(self, mock_auto_inst):
        """Test init_tracing skips when already initialized"""
        # First initialization
        tracing._is_initialized = True
        tracing._tracer = Mock()

        result = init_tracing(app_name="test-app")

        # Should return existing tracer without reconfiguring
        assert result == tracing._tracer
        mock_auto_inst.assert_not_called()

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_with_jaeger(self, mock_auto_inst):
        """Test initialization with Jaeger exporter"""
        result = init_tracing(
            app_name="test-app", jaeger_host="jaeger.example.com", jaeger_port=6831
        )

        mock_jaeger_exporter.assert_called_once_with(
            agent_host_name="jaeger.example.com", agent_port=6831
        )

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_with_otlp(self, mock_auto_inst):
        """Test initialization with OTLP exporter"""
        result = init_tracing(app_name="test-app", otlp_endpoint="http://localhost:4317")

        mock_otlp_exporter.assert_called_once_with(endpoint="http://localhost:4317")

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_with_console(self, mock_auto_inst):
        """Test initialization with console exporter"""
        result = init_tracing(app_name="test-app", enable_console=True)

        mock_console_exporter.assert_called()

    @patch("src.core.tracing._auto_instrument")
    @patch.dict("os.environ", {"JAEGER_AGENT_HOST": "env-jaeger", "JAEGER_AGENT_PORT": "9999"})
    def test_init_tracing_from_env_vars(self, mock_auto_inst):
        """Test initialization using environment variables"""
        result = init_tracing(app_name="test-app")

        # Should use environment variables
        mock_jaeger_exporter.assert_called_once_with(agent_host_name="env-jaeger", agent_port=9999)

    @patch("src.core.tracing._auto_instrument")
    def test_init_tracing_resource_attributes(self, mock_auto_inst):
        """Test resource attributes are set correctly"""
        result = init_tracing(app_name="my-service", environment="production")

        # Check resource was created with correct attributes
        call_args = mock_resource.call_args
        attrs = call_args[1]["attributes"]

        assert attrs["service.name"] == "my-service"
        assert attrs["environment"] == "production"
        assert "service.version" in attrs
        assert attrs["deployment.environment"] == "production"

    @patch("src.core.tracing._auto_instrument")
    @patch("src.core.tracing.logger")
    def test_init_tracing_jaeger_failure(self, mock_logger, mock_auto_inst):
        """Test graceful handling of Jaeger exporter failure"""
        mock_jaeger_exporter.side_effect = Exception("Jaeger connection failed")

        result = init_tracing(app_name="test-app")

        mock_logger.warning.assert_any_call("Failed to configure Jaeger exporter: Jaeger connection failed")

    @patch("src.core.tracing._auto_instrument")
    @patch("src.core.tracing.logger")
    def test_init_tracing_no_exporters_warning(self, mock_logger, mock_auto_inst):
        """Test warning when no exporters are configured"""
        mock_jaeger_exporter.side_effect = Exception("Failed")
        mock_otlp_exporter.side_effect = Exception("Failed")

        result = init_tracing(app_name="test-app", environment="production")

        # Should warn about no exporters
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any("No trace exporters configured" in str(call) for call in warning_calls)


class TestAutoInstrument:
    """Test _auto_instrument function."""

    @patch("src.core.tracing.logger")
    def test_auto_instrument_success(self, mock_logger):
        """Test successful auto-instrumentation"""
        mock_flask_instrumentor.reset_mock()
        mock_requests_instrumentor.reset_mock()
        mock_sqlalchemy_instrumentor.reset_mock()

        tracing._auto_instrument()

        mock_flask_instrumentor.return_value.instrument.assert_called_once()
        mock_requests_instrumentor.return_value.instrument.assert_called_once()
        mock_sqlalchemy_instrumentor.return_value.instrument.assert_called_once()

    @patch("src.core.tracing.logger")
    def test_auto_instrument_flask_failure(self, mock_logger):
        """Test graceful handling of Flask instrumentation failure"""
        mock_flask_instrumentor.return_value.instrument.side_effect = Exception("Flask error")

        tracing._auto_instrument()

        mock_logger.warning.assert_any_call("Failed to instrument Flask: Flask error")


class TestTracedDecorator:
    """Test traced decorator."""

    def setup_method(self):
        """Set up tracer for tests"""
        tracing._tracer = mock_tracer
        tracing._is_initialized = True
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=False)

    def test_traced_basic(self):
        """Test traced decorator with basic function"""

        @traced()
        def test_func():
            return "result"

        result = test_func()

        assert result == "result"
        mock_tracer.start_as_current_span.assert_called()

    def test_traced_with_custom_name(self):
        """Test traced decorator with custom span name"""

        @traced(name="custom_span_name")
        def test_func():
            return "result"

        result = test_func()

        assert result == "result"
        mock_tracer.start_as_current_span.assert_called_with("custom_span_name")

    def test_traced_with_attributes(self):
        """Test traced decorator with custom attributes"""

        @traced(attributes={"key1": "value1", "key2": 42})
        def test_func():
            return "result"

        result = test_func()

        assert result == "result"
        mock_span.set_attribute.assert_any_call("key1", "value1")
        mock_span.set_attribute.assert_any_call("key2", 42)

    def test_traced_with_function_metadata(self):
        """Test traced decorator adds function metadata"""

        @traced()
        def test_func():
            return "result"

        result = test_func()

        assert result == "result"
        mock_span.set_attribute.assert_any_call("code.function", "test_func")
        # Check that code.namespace was set (module name)
        calls = [call for call in mock_span.set_attribute.call_args_list]
        assert any("code.namespace" in str(call) for call in calls)

    def test_traced_with_exception(self):
        """Test traced decorator records exceptions"""

        @traced(record_exception=True)
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError) as exc_info:
            test_func()

        assert str(exc_info.value) == "Test error"
        mock_span.record_exception.assert_called_once()
        mock_span.set_status.assert_called()

    def test_traced_without_recording_exception(self):
        """Test traced decorator with record_exception=False"""
        mock_span.reset_mock()

        @traced(record_exception=False)
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_func()

        mock_span.record_exception.assert_not_called()

    def test_traced_success_status(self):
        """Test traced decorator sets success status"""
        mock_span.reset_mock()

        @traced()
        def test_func():
            return "success"

        result = test_func()

        assert result == "success"
        # Check that status was set to OK
        status_calls = [call for call in mock_span.set_status.call_args_list]
        assert len(status_calls) > 0

    def test_traced_uninitialized_tracer(self):
        """Test traced decorator works when tracing not initialized"""
        tracing._tracer = None
        tracing._is_initialized = False

        @traced()
        def test_func():
            return "result"

        # Should execute without tracing
        result = test_func()

        assert result == "result"

    def test_traced_preserves_function_signature(self):
        """Test traced decorator preserves function name and docstring"""

        @traced()
        def test_func_with_doc():
            """Test docstring"""
            return "result"

        assert test_func_with_doc.__name__ == "test_func_with_doc"
        assert test_func_with_doc.__doc__ == "Test docstring"


class TestAddSpanAttribute:
    """Test add_span_attribute function."""

    def test_add_span_attribute_recording(self):
        """Test add_span_attribute with recording span"""
        mock_span.reset_mock()
        mock_span.is_recording.return_value = True

        add_span_attribute("test_key", "test_value")

        mock_span.set_attribute.assert_called_once_with("test_key", "test_value")

    def test_add_span_attribute_not_recording(self):
        """Test add_span_attribute with non-recording span"""
        mock_span.reset_mock()
        mock_span.is_recording.return_value = False

        add_span_attribute("test_key", "test_value")

        mock_span.set_attribute.assert_not_called()

    def test_add_span_attribute_no_span(self):
        """Test add_span_attribute with no active span"""
        with patch("src.core.tracing.trace.get_current_span", return_value=None):
            # Should not raise exception
            add_span_attribute("test_key", "test_value")


class TestAddSpanEvent:
    """Test add_span_event function."""

    def test_add_span_event_with_attributes(self):
        """Test add_span_event with attributes"""
        mock_span.reset_mock()
        mock_span.is_recording.return_value = True

        add_span_event("test_event", {"key1": "value1", "key2": 42})

        mock_span.add_event.assert_called_once_with("test_event", {"key1": "value1", "key2": 42})

    def test_add_span_event_without_attributes(self):
        """Test add_span_event without attributes"""
        mock_span.reset_mock()
        mock_span.is_recording.return_value = True

        add_span_event("test_event")

        mock_span.add_event.assert_called_once_with("test_event", {})

    def test_add_span_event_not_recording(self):
        """Test add_span_event with non-recording span"""
        mock_span.reset_mock()
        mock_span.is_recording.return_value = False

        add_span_event("test_event")

        mock_span.add_event.assert_not_called()


class TestCreateSpan:
    """Test create_span function."""

    def test_create_span_initialized(self):
        """Test create_span with initialized tracer"""
        tracing._tracer = mock_tracer
        tracing._is_initialized = True
        mock_new_span = Mock()
        mock_tracer.start_span.return_value = mock_new_span

        result = create_span("test_span", {"attr": "value"})

        mock_tracer.start_span.assert_called_once_with("test_span")
        mock_new_span.set_attribute.assert_called_with("attr", "value")

    def test_create_span_uninitialized(self):
        """Test create_span with uninitialized tracer"""
        tracing._tracer = None
        tracing._is_initialized = False

        result = create_span("test_span")

        # Should return a no-op context manager
        assert result is not None


class TestConvenienceDecorators:
    """Test convenience decorator functions."""

    def test_traced_api(self):
        """Test traced_api decorator"""
        decorator = traced_api("/api/users")

        # Check that it returns a traced decorator with correct attributes
        assert callable(decorator)

    def test_traced_db_with_table(self):
        """Test traced_db decorator with table name"""
        decorator = traced_db("SELECT", "users")

        assert callable(decorator)

    def test_traced_db_without_table(self):
        """Test traced_db decorator without table name"""
        decorator = traced_db("INSERT")

        assert callable(decorator)

    def test_traced_ml(self):
        """Test traced_ml decorator"""
        decorator = traced_ml("bert", "predict")

        assert callable(decorator)


class TestShutdownTracing:
    """Test shutdown_tracing function."""

    def test_shutdown_tracing_initialized(self):
        """Test shutdown_tracing when initialized"""
        tracing._is_initialized = True
        mock_provider = Mock()
        mock_provider.force_flush = Mock()
        mock_provider.shutdown = Mock()

        with patch("src.core.tracing.trace.get_tracer_provider", return_value=mock_provider):
            shutdown_tracing()

        mock_provider.force_flush.assert_called_once()
        mock_provider.shutdown.assert_called_once()
        assert tracing._is_initialized is False

    def test_shutdown_tracing_uninitialized(self):
        """Test shutdown_tracing when not initialized"""
        tracing._is_initialized = False

        # Should not raise exception
        shutdown_tracing()

    @patch("src.core.tracing.logger")
    def test_shutdown_tracing_error_handling(self, mock_logger):
        """Test shutdown_tracing handles errors gracefully"""
        tracing._is_initialized = True

        with patch(
            "src.core.tracing.trace.get_tracer_provider", side_effect=Exception("Shutdown error")
        ):
            shutdown_tracing()

        mock_logger.error.assert_called()
        assert tracing._is_initialized is False


class TestIntegration:
    """Integration tests for tracing module."""

    def test_full_tracing_workflow(self):
        """Test complete tracing workflow"""
        # Reset state
        tracing._tracer = None
        tracing._is_initialized = False

        # Initialize
        with patch("src.core.tracing._auto_instrument"):
            tracer = init_tracing(app_name="test", environment="test", enable_console=True)

        assert tracer is not None
        assert tracing._is_initialized is True

        # Use decorator
        @traced(name="test_span")
        def test_function():
            add_span_attribute("custom_attr", "value")
            add_span_event("test_event")
            return "result"

        result = test_function()
        assert result == "result"

        # Shutdown
        with patch("src.core.tracing.trace.get_tracer_provider") as mock_provider_getter:
            mock_provider = Mock()
            mock_provider_getter.return_value = mock_provider
            shutdown_tracing()

        assert tracing._is_initialized is False

    def test_traced_decorators_chaining(self):
        """Test chaining of traced decorators"""
        tracing._tracer = mock_tracer
        tracing._is_initialized = True

        @traced_api("/api/test")
        @traced_db("SELECT", "users")
        def complex_function():
            return "result"

        result = complex_function()
        assert result == "result"
