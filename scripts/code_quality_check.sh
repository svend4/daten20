#!/bin/bash
# Comprehensive code quality check script
# Usage: ./scripts/code_quality_check.sh

set -e

echo "================================"
echo "Code Quality Check"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

# Function to print section header
print_header() {
    echo ""
    echo "================================"
    echo "$1"
    echo "================================"
    echo ""
}

# Check if required tools are installed
check_tools() {
    local missing=0

    for tool in black isort flake8 mypy bandit; do
        if ! command -v $tool &> /dev/null; then
            echo -e "${YELLOW}Warning:${NC} $tool is not installed"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -gt 0 ]; then
        echo ""
        echo "Install missing tools with: pip install -r requirements-dev.txt"
        echo ""
    fi
}

# 1. Check code formatting with Black
print_header "1. Code Formatting (Black)"
if black --check src/ tests/ *.py 2>&1 | tail -20; then
    BLACK_STATUS=0
else
    BLACK_STATUS=1
fi
print_status $BLACK_STATUS "Black formatting"

# 2. Check import sorting with isort
print_header "2. Import Sorting (isort)"
if isort --check-only src/ tests/ *.py 2>&1 | tail -20; then
    ISORT_STATUS=0
else
    ISORT_STATUS=1
fi
print_status $ISORT_STATUS "Import sorting"

# 3. Linting with flake8
print_header "3. Linting (flake8)"
echo "Running flake8 checks..."

# Critical errors
if flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1 | tail -10; then
    FLAKE8_CRITICAL=0
else
    FLAKE8_CRITICAL=1
fi

# All issues
FLAKE8_COUNT=$(flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics 2>&1 | grep -E "^[0-9]+" | tail -1 || echo "0")
print_status $FLAKE8_CRITICAL "Flake8 linting (critical errors)"
echo "  Total issues: $FLAKE8_COUNT"

# 4. Type checking with mypy
print_header "4. Type Checking (mypy)"
if mypy src/ --ignore-missing-imports --no-strict-optional 2>&1 | tail -20; then
    MYPY_STATUS=0
else
    MYPY_STATUS=1
    echo -e "${YELLOW}Note: mypy errors are informational only${NC}"
fi
print_status 0 "Type checking (informational)"

# 5. Security check with bandit
print_header "5. Security Scanning (bandit)"
if bandit -r src/ -ll -f json -o bandit-report.json 2>&1 | tail -10; then
    BANDIT_STATUS=0
else
    BANDIT_STATUS=1
fi
print_status $BANDIT_STATUS "Security scan"

if [ -f bandit-report.json ]; then
    BANDIT_ISSUES=$(python3 -c "import json; data=json.load(open('bandit-report.json')); print(len(data.get('results', [])))" 2>/dev/null || echo "0")
    echo "  Security issues found: $BANDIT_ISSUES"
fi

# 6. Test coverage check
print_header "6. Test Coverage"
if command -v pytest &> /dev/null; then
    echo "Running pytest with coverage..."
    if python -m pytest tests/unit/apps/ --cov=src --cov-report=term-missing --cov-report=html -q 2>&1 | tail -30; then
        COVERAGE_STATUS=0
    else
        COVERAGE_STATUS=1
    fi
    print_status $COVERAGE_STATUS "Test coverage check"
else
    echo -e "${YELLOW}pytest not found, skipping coverage${NC}"
fi

# Summary
print_header "Summary"
TOTAL=$((BLACK_STATUS + ISORT_STATUS + FLAKE8_CRITICAL))

echo "Checks passed: $PASSED"
echo "Checks failed: $FAILED"
echo ""

if [ $TOTAL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review $FLAKE8_COUNT flake8 issues (if any)"
    echo "  2. Review bandit security report: bandit-report.json"
    echo "  3. Check test coverage report: htmlcov/index.html"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  black src/ tests/ *.py          # Auto-format code"
    echo "  isort src/ tests/ *.py          # Auto-sort imports"
    echo "  flake8 src/ tests/              # View linting errors"
    exit 1
fi
