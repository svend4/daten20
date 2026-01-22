#!/bin/bash
# Script for running tests by size category
# Based on Google Test Sizes standard

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TEST_SIZE]

Run tests by size category:
  small     - Fast unit tests (< 1 second, no I/O)
  medium    - Integration tests (< 5 minutes, local resources)
  large     - E2E tests (full integration, may be slow)
  all       - Run all tests
  quick     - Run small + medium (default for dev)
  ci        - Run tests suitable for CI/CD

Options:
  -v, --verbose         Verbose output
  -c, --coverage        Generate coverage report
  -p, --parallel        Run tests in parallel
  -f, --failfast        Stop on first failure
  -k EXPRESSION         Only run tests matching expression
  --durations N         Show N slowest tests
  -h, --help            Show this help message

Examples:
  $0 small              # Run only small tests
  $0 medium -c          # Run medium tests with coverage
  $0 quick -p           # Run small+medium tests in parallel
  $0 all --durations 20 # Run all tests, show 20 slowest

EOF
    exit 0
}

# Default values
TEST_SIZE=""
VERBOSE=""
COVERAGE=""
PARALLEL=""
FAILFAST=""
EXPRESSION=""
DURATIONS=""
EXTRA_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term-missing"
            shift
            ;;
        -p|--parallel)
            PARALLEL="-n auto"
            shift
            ;;
        -f|--failfast)
            FAILFAST="-x"
            shift
            ;;
        -k)
            EXPRESSION="-k $2"
            shift 2
            ;;
        --durations)
            DURATIONS="--durations=$2"
            shift 2
            ;;
        small|medium|large|all|quick|ci)
            TEST_SIZE="$1"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Default to quick if no size specified
if [ -z "$TEST_SIZE" ]; then
    TEST_SIZE="quick"
fi

# Build pytest command
PYTEST_CMD="python3 -m pytest"
PYTEST_CMD="$PYTEST_CMD $VERBOSE"
PYTEST_CMD="$PYTEST_CMD $COVERAGE"
PYTEST_CMD="$PYTEST_CMD $PARALLEL"
PYTEST_CMD="$PYTEST_CMD $FAILFAST"
PYTEST_CMD="$PYTEST_CMD $EXPRESSION"
PYTEST_CMD="$PYTEST_CMD $DURATIONS"
PYTEST_CMD="$PYTEST_CMD $EXTRA_ARGS"

# Run tests based on size
case $TEST_SIZE in
    small)
        print_header "Running SMALL tests (fast unit tests)"
        echo "Expected time: < 1 minute"
        echo ""
        $PYTEST_CMD -m small
        ;;

    medium)
        print_header "Running MEDIUM tests (integration tests)"
        echo "Expected time: < 5 minutes"
        echo ""
        $PYTEST_CMD -m medium
        ;;

    large)
        print_header "Running LARGE tests (E2E tests)"
        echo "Expected time: 5-30 minutes"
        echo ""
        $PYTEST_CMD -m large
        ;;

    all)
        print_header "Running ALL tests"
        echo "Expected time: 10-60 minutes"
        echo ""
        $PYTEST_CMD
        ;;

    quick)
        print_header "Running QUICK tests (small + medium)"
        echo "Expected time: < 10 minutes"
        echo ""
        print_warning "This is the recommended suite for pre-commit checks"
        echo ""
        $PYTEST_CMD -m "small or medium"
        ;;

    ci)
        print_header "Running CI tests (optimized for CI/CD)"
        echo "Expected time: < 15 minutes"
        echo ""
        # Run small and medium, but skip known slow tests
        $PYTEST_CMD -m "(small or medium) and not slow"
        ;;

    *)
        print_error "Unknown test size: $TEST_SIZE"
        echo ""
        usage
        ;;
esac

# Check exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed. Exit code: $EXIT_CODE"
fi

exit $EXIT_CODE
