"""
Logging Examples for Daten20

Demonstrates various logging patterns and best practices.
"""

import logging
from src.core.logger import setup_logger, get_logger, log_performance, LogContext
from src.core.logging_config import LoggingConfig


def example_basic_logging():
    """Basic logging example"""
    print("\n=== Basic Logging Example ===")

    logger = get_logger('example.basic')

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


def example_custom_setup():
    """Custom logger setup example"""
    print("\n=== Custom Setup Example ===")

    # Setup with custom configuration
    logger = setup_logger(
        'example.custom',
        log_level=logging.DEBUG,
        enable_console=True,
        enable_file=True
    )

    logger.info("Logger configured with custom settings")


def example_json_logging():
    """JSON/structured logging example"""
    print("\n=== JSON Logging Example ===")

    # Setup JSON logger
    logger = LoggingConfig.setup(
        logger_name='example.json',
        enable_json=True,
        enable_console=False,
        enable_file=True
    )

    # Log with context
    LoggingConfig.log_with_context(
        logger,
        logging.INFO,
        "User action performed",
        user_id=123,
        action="create_service",
        service_name="Test Service"
    )

    print("JSON log written to logs/example.json.log")


def example_exception_logging():
    """Exception logging example"""
    print("\n=== Exception Logging Example ===")

    logger = get_logger('example.exception')

    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        # Log with full traceback
        logger.error(f"Operation failed: {e}", exc_info=True)


def example_context_logging():
    """Context-based logging example"""
    print("\n=== Context Logging Example ===")

    logger = get_logger('example.context')

    # Add context to log messages
    with LogContext(logger, request_id='REQ-12345', user='admin'):
        logger.info("Starting request processing")
        logger.info("Validating input")
        logger.info("Processing completed")


def example_performance_logging():
    """Performance logging example"""
    print("\n=== Performance Logging Example ===")

    logger = get_logger('example.performance')

    @log_performance(logger, 'data_processing')
    def process_data():
        """Simulate data processing"""
        import time
        time.sleep(0.5)  # Simulate work
        return "processed"

    result = process_data()
    logger.info(f"Result: {result}")


def example_structured_logging():
    """Structured logging with rich context"""
    print("\n=== Structured Logging Example ===")

    logger = get_logger('example.structured')

    # Log business event with context
    service_id = 42
    service_name = "Customer Service"
    operation_time = 1.234

    logger.info(
        f"Service created successfully: "
        f"ID={service_id}, "
        f"name='{service_name}', "
        f"time={operation_time:.3f}s"
    )


def example_multi_level_logging():
    """Multi-level logging example"""
    print("\n=== Multi-Level Logging Example ===")

    logger = get_logger('example.multilevel')

    def complex_operation():
        """Simulate complex operation with multiple log levels"""
        logger.info("Starting complex operation")

        # Debug details
        logger.debug("Loading configuration")
        logger.debug("Connecting to database")

        # Warning
        logger.warning("Cache miss, fetching from database")

        # Info
        logger.info("Processing 100 items")

        # Simulate potential error
        try:
            # ... some operation ...
            logger.debug("Operation step completed")
        except Exception as e:
            logger.error(f"Step failed: {e}")
            raise

        logger.info("Complex operation completed successfully")

    complex_operation()


def example_database_logging():
    """Database operations logging example"""
    print("\n=== Database Logging Example ===")

    logger = get_logger('example.database')

    def simulate_database_operations():
        """Simulate database CRUD operations with logging"""
        logger.info("Initializing database connection")
        logger.debug("Database schema verified")

        # Create
        logger.info("Creating new service: Test Service")
        service_id = 1
        logger.debug(f"Service created with ID: {service_id}")

        # Read
        logger.debug(f"Retrieving service with ID: {service_id}")
        logger.info(f"Service found: ID={service_id}")

        # Update
        logger.info(f"Updating service: ID={service_id}")
        version = 2
        logger.info(f"Service updated successfully: ID={service_id}, version={version}")

        # Delete
        logger.info(f"Deleting service: ID={service_id}")
        logger.info(f"Service deleted successfully: ID={service_id}")

    simulate_database_operations()


def example_log_levels_usage():
    """Demonstrate when to use each log level"""
    print("\n=== Log Levels Usage Example ===")

    logger = get_logger('example.levels')

    # DEBUG: Detailed diagnostic information
    logger.debug("SQL Query: SELECT * FROM services WHERE id = 1")
    logger.debug("Cache lookup: key='service:1', result=None")

    # INFO: Confirmation that things are working as expected
    logger.info("Application started successfully")
    logger.info("Service created: ID=1, name='Test'")
    logger.info("User logged in: user_id=123")

    # WARNING: Something unexpected happened, but the app continues
    logger.warning("Cache miss for key='config:settings'")
    logger.warning("API rate limit approaching: 95/100 requests")
    logger.warning("Deprecated function called: use new_function() instead")

    # ERROR: A serious problem occurred, operation failed
    logger.error("Failed to connect to database: connection timeout")
    logger.error("Invalid input data: missing required field 'name'")

    # CRITICAL: System is unusable, requires immediate attention
    logger.critical("Database corrupted, system shutting down")
    logger.critical("Out of memory, cannot continue")


def main():
    """Run all logging examples"""
    print("=" * 60)
    print("Daten20 Logging Examples")
    print("=" * 60)

    example_basic_logging()
    example_custom_setup()
    example_structured_logging()
    example_exception_logging()
    example_context_logging()
    example_performance_logging()
    example_multi_level_logging()
    example_database_logging()
    example_log_levels_usage()

    print("\n" + "=" * 60)
    print("Examples complete! Check logs/ directory for output files")
    print("=" * 60)


if __name__ == '__main__':
    main()
