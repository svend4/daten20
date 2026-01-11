#!/bin/bash
# Test runner script for Document Management System
# Provides convenient commands for running tests with various options

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Create logs directory if it doesn't exist
mkdir -p tests/logs

# Parse command line arguments
COMMAND=${1:-all}

case "$COMMAND" in
    all)
        print_info "Running all tests with coverage..."
        pytest tests/ -v --cov=src --cov=. --cov-report=html --cov-report=term-missing
        print_success "All tests completed!"
        print_info "Coverage report: htmlcov/index.html"
        ;;

    unit)
        print_info "Running unit tests only..."
        pytest tests/unit/ -v
        print_success "Unit tests completed!"
        ;;

    integration)
        print_info "Running integration tests only..."
        pytest tests/integration/ -v
        print_success "Integration tests completed!"
        ;;

    apps)
        print_info "Running application tests only..."
        pytest tests/unit/apps/ -v
        print_success "Application tests completed!"
        ;;

    comparator)
        print_info "Running doc-comparator tests..."
        pytest tests/unit/apps/test_doc_comparator.py -v
        ;;

    anonymizer)
        print_info "Running doc-anonymizer tests..."
        pytest tests/unit/apps/test_doc_anonymizer.py -v
        ;;

    quality)
        print_info "Running doc-quality tests..."
        pytest tests/unit/apps/test_doc_quality.py -v
        ;;

    master)
        print_info "Running doc-master tests..."
        pytest tests/unit/apps/test_doc_master.py -v
        ;;

    coverage)
        print_info "Running tests and generating coverage report..."
        pytest tests/ --cov=src --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
        print_success "Coverage report generated!"
        print_info "HTML report: htmlcov/index.html"
        print_info "XML report: coverage.xml"
        ;;

    quick)
        print_info "Running quick smoke tests..."
        pytest tests/ -v -m smoke --tb=short
        print_success "Smoke tests completed!"
        ;;

    slow)
        print_info "Running slow tests..."
        pytest tests/ -v -m slow
        print_success "Slow tests completed!"
        ;;

    failed)
        print_info "Re-running previously failed tests..."
        pytest tests/ -v --lf
        ;;

    watch)
        print_info "Running tests in watch mode..."
        print_warning "This requires pytest-watch (pip install pytest-watch)"
        ptw tests/ -- -v
        ;;

    parallel)
        print_info "Running tests in parallel..."
        print_warning "This requires pytest-xdist (pip install pytest-xdist)"
        pytest tests/ -v -n auto
        ;;

    clean)
        print_info "Cleaning test artifacts..."
        rm -rf .pytest_cache
        rm -rf htmlcov
        rm -rf .coverage
        rm -rf coverage.xml
        rm -rf tests/logs/*.log
        rm -rf **/__pycache__
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        print_success "Test artifacts cleaned!"
        ;;

    install)
        print_info "Installing test dependencies..."
        pip install -r requirements-dev.txt
        print_success "Test dependencies installed!"
        ;;

    report)
        print_info "Opening coverage report in browser..."
        if [ -f "htmlcov/index.html" ]; then
            if command -v xdg-open > /dev/null; then
                xdg-open htmlcov/index.html
            elif command -v open > /dev/null; then
                open htmlcov/index.html
            else
                print_warning "Could not open browser. Open htmlcov/index.html manually."
            fi
        else
            print_error "Coverage report not found. Run './run_tests.sh coverage' first."
        fi
        ;;

    help)
        echo "Test runner for Document Management System"
        echo ""
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  all           - Run all tests with coverage (default)"
        echo "  unit          - Run unit tests only"
        echo "  integration   - Run integration tests only"
        echo "  apps          - Run application tests only"
        echo "  comparator    - Run doc-comparator tests"
        echo "  anonymizer    - Run doc-anonymizer tests"
        echo "  quality       - Run doc-quality tests"
        echo "  master        - Run doc-master tests"
        echo "  coverage      - Generate detailed coverage report"
        echo "  quick         - Run quick smoke tests"
        echo "  slow          - Run slow tests only"
        echo "  failed        - Re-run previously failed tests"
        echo "  watch         - Run tests in watch mode (requires pytest-watch)"
        echo "  parallel      - Run tests in parallel (requires pytest-xdist)"
        echo "  clean         - Clean test artifacts and cache"
        echo "  install       - Install test dependencies"
        echo "  report        - Open coverage report in browser"
        echo "  help          - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh all           # Run all tests"
        echo "  ./run_tests.sh apps          # Run application tests"
        echo "  ./run_tests.sh coverage      # Generate coverage report"
        echo "  ./run_tests.sh comparator    # Test doc-comparator only"
        ;;

    *)
        print_error "Unknown command: $COMMAND"
        print_info "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac
