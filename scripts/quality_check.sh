#!/usr/bin/env bash
#
# Code Quality Check Script
# ==========================
# Runs all code quality checks for the Document Management System
#
# Usage:
#   ./scripts/quality_check.sh              # Run all checks
#   ./scripts/quality_check.sh --fast       # Skip slow checks
#   ./scripts/quality_check.sh --fix        # Auto-fix issues
#   ./scripts/quality_check.sh --check=<name>  # Run specific check
#
# Author: Document Management System
# Version: 1.0.0
# Date: 2026-01-11
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

FAST_MODE=false
FIX_MODE=false
SPECIFIC_CHECK=""
VERBOSE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --fast)
            FAST_MODE=true
            ;;
        --fix)
            FIX_MODE=true
            ;;
        --check=*)
            SPECIFIC_CHECK="${arg#*=}"
            ;;
        --verbose|-v)
            VERBOSE=true
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fast              Skip slow checks (mypy, bandit)"
            echo "  --fix               Auto-fix issues where possible"
            echo "  --check=<name>      Run specific check (black, flake8, mypy, etc.)"
            echo "  --verbose, -v       Verbose output"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Available checks:"
            echo "  black               Code formatting"
            echo "  isort               Import sorting"
            echo "  flake8              Style guide enforcement"
            echo "  mypy                Static type checking"
            echo "  bandit              Security linting"
            echo "  pytest              Run tests"
            echo "  coverage            Test coverage"
            echo "  all                 All checks (default)"
            exit 0
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BOLD}${CYAN}================================${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${BOLD}${CYAN}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

run_check() {
    local check_name=$1
    local check_command=$2

    if [ -n "$SPECIFIC_CHECK" ] && [ "$SPECIFIC_CHECK" != "$check_name" ] && [ "$SPECIFIC_CHECK" != "all" ]; then
        return 0
    fi

    print_header "$check_name"

    if eval "$check_command"; then
        print_success "$check_name passed"
        return 0
    else
        print_error "$check_name failed"
        return 1
    fi
}

# Main script
main() {
    local failed_checks=()
    local passed_checks=()

    echo -e "${BOLD}${BLUE}================================================${NC}"
    echo -e "${BOLD}${BLUE}   Code Quality Checks - DMS v4.1${NC}"
    echo -e "${BOLD}${BLUE}================================================${NC}"

    if [ "$FAST_MODE" = true ]; then
        print_info "Running in FAST mode (skipping slow checks)"
    fi

    if [ "$FIX_MODE" = true ]; then
        print_info "Running in FIX mode (auto-fixing issues)"
    fi

    # Check 1: Black (Code Formatting)
    if [ "$FIX_MODE" = true ]; then
        if run_check "Black (auto-fix)" "black src/ tests/ *.py --line-length 120"; then
            passed_checks+=("black")
        else
            failed_checks+=("black")
        fi
    else
        if run_check "Black (check)" "black src/ tests/ *.py --check --line-length 120"; then
            passed_checks+=("black")
        else
            failed_checks+=("black")
            print_warning "Run with --fix to auto-format"
        fi
    fi

    # Check 2: isort (Import Sorting)
    if [ "$FIX_MODE" = true ]; then
        if run_check "isort (auto-fix)" "isort src/ tests/ --profile black --line-length 120"; then
            passed_checks+=("isort")
        else
            failed_checks+=("isort")
        fi
    else
        if run_check "isort (check)" "isort src/ tests/ --check-only --profile black --line-length 120"; then
            passed_checks+=("isort")
        else
            failed_checks+=("isort")
            print_warning "Run with --fix to auto-sort imports"
        fi
    fi

    # Check 3: Flake8 (Style Guide)
    if run_check "Flake8 (style)" "flake8 src/ tests/ --config=.flake8"; then
        passed_checks+=("flake8")
    else
        failed_checks+=("flake8")
    fi

    # Check 4: MyPy (Type Checking) - Skip in fast mode
    if [ "$FAST_MODE" = false ]; then
        if run_check "MyPy (types)" "mypy src/ --config-file=mypy.ini --show-error-codes"; then
            passed_checks+=("mypy")
        else
            failed_checks+=("mypy")
            print_warning "Type checking failed (non-blocking)"
        fi
    else
        print_info "Skipping MyPy (fast mode)"
    fi

    # Check 5: Bandit (Security) - Skip in fast mode
    if [ "$FAST_MODE" = false ]; then
        if run_check "Bandit (security)" "bandit -c .bandit -r src/ -q"; then
            passed_checks+=("bandit")
        else
            failed_checks+=("bandit")
            print_warning "Security issues found (review manually)"
        fi
    else
        print_info "Skipping Bandit (fast mode)"
    fi

    # Check 6: Pytest (if requested)
    if [ "$SPECIFIC_CHECK" = "pytest" ] || [ "$SPECIFIC_CHECK" = "all" ]; then
        if run_check "Pytest (tests)" "pytest tests/ -v --tb=short"; then
            passed_checks+=("pytest")
        else
            failed_checks+=("pytest")
        fi
    fi

    # Check 7: Coverage (if requested)
    if [ "$SPECIFIC_CHECK" = "coverage" ] || [ "$SPECIFIC_CHECK" = "all" ]; then
        if run_check "Coverage (test)" "pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=70"; then
            passed_checks+=("coverage")
        else
            failed_checks+=("coverage")
            print_warning "Coverage below 70% (non-blocking)"
        fi
    fi

    # Summary
    print_header "Summary"

    echo -e "${BOLD}Passed checks (${#passed_checks[@]}):${NC}"
    for check in "${passed_checks[@]}"; do
        print_success "$check"
    done

    if [ ${#failed_checks[@]} -gt 0 ]; then
        echo -e "\n${BOLD}Failed checks (${#failed_checks[@]}):${NC}"
        for check in "${failed_checks[@]}"; do
            print_error "$check"
        done

        echo ""
        print_error "Quality checks FAILED"
        echo ""

        if [ "$FIX_MODE" = false ]; then
            print_info "Tip: Run with --fix to auto-fix formatting issues"
        fi

        echo -e "${YELLOW}Fix the issues above and try again.${NC}"
        exit 1
    else
        echo ""
        print_success "All quality checks PASSED! 🎉"
        echo ""
        exit 0
    fi
}

# Check if required tools are installed
check_dependencies() {
    local missing_tools=()

    for tool in black isort flake8 mypy bandit pytest; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        print_info "Install with: pip install black isort flake8 mypy bandit pytest pytest-cov"
        exit 1
    fi
}

# Run the main function
check_dependencies
main
